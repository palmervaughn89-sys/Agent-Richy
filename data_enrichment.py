#!/usr/bin/env python3
"""data_enrichment.py — Daily intelligence layer for the Richy engine.

Reads raw DuckDB databases (indicators, tickers, fundamentals, discounts,
heartbeat patterns) and computes context tables + signals that give the AI
agent pattern-recognition superpowers.

Run daily:
    python data_enrichment.py

Databases (paths pulled from config constants at top):
  • data/richy.duckdb          — indicators (monthly) + tickers (daily)
  • data/fundamentals.duckdb   — quarterly financials
  • data/discount_intel.duckdb — discount calendar + consumer indicators
  • correlations/richy_algorithms.json — compiled heartbeat rules

Output:
  New tables in richy.duckdb   — indicator_context, ticker_context,
      fundamental_signals, regime_signals, divergence_signals,
      consumer_insights, active_predictions, summary_snapshot
  data/daily_briefing.json     — single file the AI agent loads
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURATION — all paths in one place
# ══════════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

# Database paths (read from env or defaults)
RICHY_DB       = Path(os.getenv("RICHY_DB",       str(DATA_DIR / "richy.duckdb")))
FUNDAMENTALS_DB = Path(os.getenv("FUNDAMENTALS_DB", str(DATA_DIR / "fundamentals.duckdb")))
DISCOUNT_DB    = Path(os.getenv("DISCOUNT_DB",    str(DATA_DIR / "discount_intel.duckdb")))
ALGORITHMS_JSON = Path(os.getenv("ALGORITHMS_JSON", str(ROOT / "correlations" / "richy_algorithms.json")))

BRIEFING_OUT   = DATA_DIR / "daily_briefing.json"

# ══════════════════════════════════════════════════════════════════════════
# LOGGING + CONSOLE
# ══════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("data_enrichment")

console = Console()

# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════

_TODAY = date.today()
_NOW_ISO = datetime.utcnow().isoformat(timespec="seconds")


def _safe_float(v: Any) -> float | None:
    """Convert to float or return None."""
    try:
        f = float(v)
        return f if np.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _pct_change(old: float, new: float) -> float | None:
    if old == 0:
        return None
    return ((new - old) / abs(old)) * 100.0


def _direction(recent_avg: float, prior_avg: float, tol: float = 0.005) -> str:
    if prior_avg == 0:
        return "FLAT"
    change = (recent_avg - prior_avg) / abs(prior_avg)
    if change > tol:
        return "RISING"
    if change < -tol:
        return "FALLING"
    return "FLAT"


def _momentum(recent_roc: float | None, prior_roc: float | None) -> str:
    if recent_roc is None or prior_roc is None:
        return "STABLE"
    if abs(recent_roc) > abs(prior_roc) * 1.1:
        return "ACCELERATING"
    if abs(recent_roc) < abs(prior_roc) * 0.9:
        return "DECELERATING"
    return "STABLE"


def _z_score(value: float, mean: float, std: float) -> float | None:
    if std == 0:
        return 0.0
    return (value - mean) / std


def _percentile_rank(value: float, series: np.ndarray) -> float:
    """Where value sits vs the full history array (0-100)."""
    if len(series) == 0:
        return 50.0
    return float(np.searchsorted(np.sort(series), value) / len(series) * 100.0)


def _connect(path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Open or create a DuckDB database."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path), read_only=read_only)


def _table_exists(con: duckdb.DuckDBPyConnection, name: str) -> bool:
    r = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = ?",
        [name],
    ).fetchone()
    return r is not None and r[0] > 0


def _row_count(con: duckdb.DuckDBPyConnection, name: str) -> int:
    if not _table_exists(con, name):
        return 0
    return con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]


def _progress() -> Progress:
    return Progress(
        SpinnerColumn("dots"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


# ══════════════════════════════════════════════════════════════════════════
# DATABASE SCHEMA BOOTSTRAP
# ══════════════════════════════════════════════════════════════════════════

_SOURCE_SCHEMAS = {
    # richy.duckdb expected source tables
    "indicators": """
        CREATE TABLE IF NOT EXISTS indicators (
            series_id   VARCHAR NOT NULL,
            obs_date    DATE    NOT NULL,
            value       DOUBLE  NOT NULL,
            unit        VARCHAR DEFAULT '',
            fetched_at  TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (series_id, obs_date)
        )
    """,
    "tickers": """
        CREATE TABLE IF NOT EXISTS tickers (
            ticker      VARCHAR NOT NULL,
            price_date  DATE    NOT NULL,
            close_price DOUBLE  NOT NULL,
            volume      BIGINT  DEFAULT 0,
            fetched_at  TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (ticker, price_date)
        )
    """,
    "heartbeat_patterns": """
        CREATE TABLE IF NOT EXISTS heartbeat_patterns (
            indicator       VARCHAR NOT NULL,
            ticker          VARCHAR NOT NULL,
            correlation     DOUBLE,
            lag_months      INTEGER DEFAULT 0,
            pattern_type    VARCHAR DEFAULT '',
            strength        INTEGER DEFAULT 0,
            description     VARCHAR DEFAULT '',
            created_at      TIMESTAMP DEFAULT current_timestamp
        )
    """,
    "iron_laws": """
        CREATE TABLE IF NOT EXISTS iron_laws (
            indicator       VARCHAR NOT NULL,
            ticker          VARCHAR NOT NULL,
            rule_text       VARCHAR,
            correlation     DOUBLE,
            lag_months      INTEGER DEFAULT 0,
            confidence      DOUBLE DEFAULT 0,
            created_at      TIMESTAMP DEFAULT current_timestamp
        )
    """,
}

_FUND_SCHEMAS = {
    "fundamentals": """
        CREATE TABLE IF NOT EXISTS fundamentals (
            ticker          VARCHAR NOT NULL,
            report_date     DATE    NOT NULL,
            metric          VARCHAR NOT NULL,
            value           DOUBLE,
            PRIMARY KEY (ticker, report_date, metric)
        )
    """,
}

_DISCOUNT_SCHEMAS = {
    "discount_calendar": """
        CREATE TABLE IF NOT EXISTS discount_calendar (
            event_name      VARCHAR NOT NULL,
            start_date      DATE,
            end_date        DATE,
            category        VARCHAR DEFAULT '',
            avg_discount_pct DOUBLE DEFAULT 0,
            description     VARCHAR DEFAULT ''
        )
    """,
    "monthly_discount_index": """
        CREATE TABLE IF NOT EXISTS monthly_discount_index (
            month_date      DATE NOT NULL,
            category        VARCHAR NOT NULL,
            discount_index  DOUBLE DEFAULT 0,
            PRIMARY KEY (month_date, category)
        )
    """,
    "consumer_indicators": """
        CREATE TABLE IF NOT EXISTS consumer_indicators (
            indicator_name  VARCHAR NOT NULL,
            obs_date        DATE    NOT NULL,
            value           DOUBLE,
            PRIMARY KEY (indicator_name, obs_date)
        )
    """,
}

# Enrichment output tables (all in richy.duckdb)
_OUTPUT_SCHEMAS = {
    "indicator_context": """
        CREATE OR REPLACE TABLE indicator_context (
            series_id           VARCHAR PRIMARY KEY,
            latest_value        DOUBLE,
            latest_date         DATE,
            direction           VARCHAR,
            momentum            VARCHAR,
            historical_percentile DOUBLE,
            pct_from_ath        DOUBLE,
            pct_from_atl        DOUBLE,
            change_3m           DOUBLE,
            change_6m           DOUBLE,
            change_12m          DOUBLE,
            z_score             DOUBLE,
            computed_at         TIMESTAMP DEFAULT current_timestamp
        )
    """,
    "ticker_context": """
        CREATE OR REPLACE TABLE ticker_context (
            ticker              VARCHAR PRIMARY KEY,
            latest_price        DOUBLE,
            latest_date         DATE,
            direction           VARCHAR,
            momentum            VARCHAR,
            historical_percentile DOUBLE,
            pct_from_52w_high   DOUBLE,
            pct_from_52w_low    DOUBLE,
            return_1m           DOUBLE,
            return_3m           DOUBLE,
            return_6m           DOUBLE,
            return_12m          DOUBLE,
            volatility_30d      DOUBLE,
            drawdown_from_peak  DOUBLE,
            near_52w_low        BOOLEAN DEFAULT FALSE,
            near_52w_high       BOOLEAN DEFAULT FALSE,
            computed_at         TIMESTAMP DEFAULT current_timestamp
        )
    """,
    "fundamental_signals": """
        CREATE OR REPLACE TABLE fundamental_signals (
            ticker          VARCHAR NOT NULL,
            signal_type     VARCHAR NOT NULL,
            description     VARCHAR,
            strength        INTEGER DEFAULT 1,
            detected_date   DATE DEFAULT current_date
        )
    """,
    "regime_signals": """
        CREATE OR REPLACE TABLE regime_signals (
            signal_type     VARCHAR NOT NULL,
            indicator_name  VARCHAR NOT NULL,
            description     VARCHAR,
            detected_date   DATE DEFAULT current_date,
            severity        INTEGER DEFAULT 1
        )
    """,
    "divergence_signals": """
        CREATE OR REPLACE TABLE divergence_signals (
            indicator       VARCHAR NOT NULL,
            ticker          VARCHAR NOT NULL,
            historical_r    DOUBLE,
            current_r_3m    DOUBLE,
            divergence_magnitude DOUBLE,
            description     VARCHAR
        )
    """,
    "consumer_insights": """
        CREATE OR REPLACE TABLE consumer_insights (
            insight_type    VARCHAR NOT NULL,
            category        VARCHAR,
            description     VARCHAR,
            data_date       DATE DEFAULT current_date
        )
    """,
    "active_predictions": """
        CREATE OR REPLACE TABLE active_predictions (
            indicator               VARCHAR NOT NULL,
            target_asset            VARCHAR NOT NULL,
            current_indicator_value DOUBLE,
            indicator_direction     VARCHAR,
            predicted_direction     VARCHAR,
            predicted_arrival_date  DATE,
            confidence              DOUBLE DEFAULT 0,
            last_3_outcomes_summary VARCHAR
        )
    """,
    "summary_snapshot": """
        CREATE OR REPLACE TABLE summary_snapshot (
            generated_at    TIMESTAMP,
            payload         VARCHAR
        )
    """,
}


# ══════════════════════════════════════════════════════════════════════════
# STEP 0 — BOOTSTRAP DATABASES
# ══════════════════════════════════════════════════════════════════════════

def step0_bootstrap() -> dict[str, duckdb.DuckDBPyConnection]:
    """Ensure all databases and tables exist. Return connection dict."""
    console.rule("[bold gold1]STEP 0 · Bootstrap Databases")

    conns: dict[str, duckdb.DuckDBPyConnection] = {}

    # richy.duckdb — source + output tables
    con_r = _connect(RICHY_DB)
    for name, ddl in _SOURCE_SCHEMAS.items():
        con_r.execute(ddl)
    for name, ddl in _OUTPUT_SCHEMAS.items():
        con_r.execute(ddl)
    conns["richy"] = con_r

    counts_r = {t: _row_count(con_r, t) for t in list(_SOURCE_SCHEMAS) + list(_OUTPUT_SCHEMAS)}
    console.print(f"  [cyan]richy.duckdb[/] → {RICHY_DB}")
    for t, c in counts_r.items():
        tag = "[green]✓[/]" if c > 0 else "[dim]empty[/]"
        console.print(f"    {t}: {c:,} rows {tag}")

    # fundamentals.duckdb
    con_f = _connect(FUNDAMENTALS_DB)
    for name, ddl in _FUND_SCHEMAS.items():
        con_f.execute(ddl)
    conns["fundamentals"] = con_f
    fc = _row_count(con_f, "fundamentals")
    console.print(f"  [cyan]fundamentals.duckdb[/] → {FUNDAMENTALS_DB}")
    console.print(f"    fundamentals: {fc:,} rows {'[green]✓[/]' if fc else '[dim]empty[/]'}")

    # discount_intel.duckdb
    con_d = _connect(DISCOUNT_DB)
    for name, ddl in _DISCOUNT_SCHEMAS.items():
        con_d.execute(ddl)
    conns["discount"] = con_d
    console.print(f"  [cyan]discount_intel.duckdb[/] → {DISCOUNT_DB}")
    for t in _DISCOUNT_SCHEMAS:
        c = _row_count(con_d, t)
        tag = "[green]✓[/]" if c > 0 else "[dim]empty[/]"
        console.print(f"    {t}: {c:,} rows {tag}")

    console.print()
    return conns


# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — INDICATOR TREND CONTEXT
# ══════════════════════════════════════════════════════════════════════════

def step1_indicator_context(con: duckdb.DuckDBPyConnection) -> int:
    """Compute indicator_context for each series_id in indicators table."""
    console.rule("[bold gold1]STEP 1 · Indicator Trend Context")

    series_ids = con.execute(
        "SELECT DISTINCT series_id FROM indicators ORDER BY series_id"
    ).fetchall()
    n = len(series_ids)
    if n == 0:
        console.print("  [dim]No indicators found — skipping.[/]")
        return 0

    rows: list[tuple] = []
    errors = 0

    with _progress() as prog:
        task = prog.add_task("Indicators", total=n)
        for (sid,) in series_ids:
            try:
                df = con.execute(
                    "SELECT obs_date, value FROM indicators "
                    "WHERE series_id = ? ORDER BY obs_date",
                    [sid],
                ).fetchdf()
                if len(df) < 3:
                    prog.advance(task)
                    continue

                vals = df["value"].values.astype(float)
                dates = pd.to_datetime(df["obs_date"])

                latest_val = float(vals[-1])
                latest_dt = dates.iloc[-1].date()

                # 3-month averages for direction
                recent_3 = vals[-3:].mean() if len(vals) >= 3 else latest_val
                prior_3 = vals[-6:-3].mean() if len(vals) >= 6 else vals[:-3].mean() if len(vals) > 3 else latest_val
                d = _direction(recent_3, prior_3)

                # Momentum: rate of change of rate of change
                roc_recent = _pct_change(prior_3, recent_3)
                prior_6 = vals[-9:-6].mean() if len(vals) >= 9 else None
                roc_prior = _pct_change(prior_6, prior_3) if prior_6 is not None else None
                mom = _momentum(roc_recent, roc_prior)

                # Percentile
                hist_pctile = _percentile_rank(latest_val, vals)

                # ATH / ATL
                ath = float(np.nanmax(vals))
                atl = float(np.nanmin(vals))
                pct_ath = _pct_change(ath, latest_val) if ath != 0 else 0.0
                pct_atl = _pct_change(atl, latest_val) if atl != 0 else 0.0

                # Period changes
                ch3 = _pct_change(float(vals[-4]), latest_val) if len(vals) >= 4 else None
                ch6 = _pct_change(float(vals[-7]), latest_val) if len(vals) >= 7 else None
                ch12 = _pct_change(float(vals[-13]), latest_val) if len(vals) >= 13 else None

                # Z-score
                z = _z_score(latest_val, float(np.nanmean(vals)), float(np.nanstd(vals)))

                rows.append((
                    sid, latest_val, latest_dt, d, mom,
                    round(hist_pctile, 2),
                    round(pct_ath, 2) if pct_ath is not None else None,
                    round(pct_atl, 2) if pct_atl is not None else None,
                    round(ch3, 2) if ch3 is not None else None,
                    round(ch6, 2) if ch6 is not None else None,
                    round(ch12, 2) if ch12 is not None else None,
                    round(z, 4) if z is not None else None,
                ))
            except Exception:
                errors += 1
                logger.debug("indicator_context error for %s: %s", sid, traceback.format_exc())
            prog.advance(task)

    # Write
    con.execute("DELETE FROM indicator_context")
    if rows:
        con.executemany(
            "INSERT INTO indicator_context VALUES (?,?,?,?,?,?,?,?,?,?,?,?,current_timestamp)",
            rows,
        )
    console.print(f"  [green]✓[/] {len(rows):,} indicators enriched ({errors} errors)")
    return len(rows)


# ══════════════════════════════════════════════════════════════════════════
# STEP 2 — TICKER TREND CONTEXT
# ══════════════════════════════════════════════════════════════════════════

def step2_ticker_context(con: duckdb.DuckDBPyConnection) -> int:
    """Compute ticker_context for each ticker in tickers table."""
    console.rule("[bold gold1]STEP 2 · Ticker Trend Context")

    ticker_list = con.execute(
        "SELECT DISTINCT ticker FROM tickers ORDER BY ticker"
    ).fetchall()
    n = len(ticker_list)
    if n == 0:
        console.print("  [dim]No tickers found — skipping.[/]")
        return 0

    rows: list[tuple] = []
    errors = 0
    cutoff_52w = _TODAY - timedelta(days=365)

    with _progress() as prog:
        task = prog.add_task("Tickers", total=n)
        for (tkr,) in ticker_list:
            try:
                df = con.execute(
                    "SELECT price_date, close_price FROM tickers "
                    "WHERE ticker = ? ORDER BY price_date",
                    [tkr],
                ).fetchdf()
                if len(df) < 5:
                    prog.advance(task)
                    continue

                prices = df["close_price"].values.astype(float)
                dates = pd.to_datetime(df["price_date"])

                latest_price = float(prices[-1])
                latest_dt = dates.iloc[-1].date()

                # Direction / momentum (use ~21 trading days ≈ 1 month)
                n_pts = len(prices)
                m1 = 21;  m3 = 63;  m6 = 126;  m12 = 252

                avg_recent = prices[-m1:].mean() if n_pts >= m1 else latest_price
                avg_prior = prices[-m3:-m1].mean() if n_pts >= m3 else prices[:-m1].mean() if n_pts > m1 else latest_price
                d = _direction(avg_recent, avg_prior, tol=0.01)

                roc_recent = _pct_change(avg_prior, avg_recent)
                avg_pp = prices[-m6:-m3].mean() if n_pts >= m6 else None
                roc_prior = _pct_change(avg_pp, avg_prior) if avg_pp is not None else None
                mom = _momentum(roc_recent, roc_prior)

                # Historical percentile
                hist_pctile = _percentile_rank(latest_price, prices)

                # 52-week high/low
                mask_52w = dates >= pd.Timestamp(cutoff_52w)
                prices_52w = prices[mask_52w.values] if mask_52w.any() else prices[-m12:]
                if len(prices_52w) == 0:
                    prices_52w = prices
                high_52w = float(np.nanmax(prices_52w))
                low_52w = float(np.nanmin(prices_52w))
                pct_h = _pct_change(high_52w, latest_price)
                pct_l = _pct_change(low_52w, latest_price)

                # Returns
                r1 = _pct_change(float(prices[-m1 - 1]), latest_price) if n_pts > m1 else None
                r3 = _pct_change(float(prices[-m3 - 1]), latest_price) if n_pts > m3 else None
                r6 = _pct_change(float(prices[-m6 - 1]), latest_price) if n_pts > m6 else None
                r12 = _pct_change(float(prices[-m12 - 1]), latest_price) if n_pts > m12 else None

                # Volatility 30d
                if n_pts >= 31:
                    daily_ret = np.diff(prices[-31:]) / prices[-31:-1]
                    vol_30 = float(np.nanstd(daily_ret)) * np.sqrt(252) * 100
                else:
                    vol_30 = None

                # Max drawdown last 12 months
                window = prices_52w
                if len(window) > 1:
                    cummax = np.maximum.accumulate(window)
                    dd = (window - cummax) / cummax * 100
                    max_dd = float(np.nanmin(dd))
                else:
                    max_dd = 0.0

                near_low = bool(pct_l is not None and pct_l <= 10.0)
                near_high = bool(pct_h is not None and abs(pct_h) <= 5.0)

                rows.append((
                    tkr, latest_price, latest_dt, d, mom,
                    round(hist_pctile, 2),
                    round(pct_h, 2) if pct_h is not None else None,
                    round(pct_l, 2) if pct_l is not None else None,
                    round(r1, 2) if r1 is not None else None,
                    round(r3, 2) if r3 is not None else None,
                    round(r6, 2) if r6 is not None else None,
                    round(r12, 2) if r12 is not None else None,
                    round(vol_30, 2) if vol_30 is not None else None,
                    round(max_dd, 2),
                    near_low, near_high,
                ))
            except Exception:
                errors += 1
                logger.debug("ticker_context error for %s: %s", tkr, traceback.format_exc())
            prog.advance(task)

    con.execute("DELETE FROM ticker_context")
    if rows:
        con.executemany(
            "INSERT INTO ticker_context VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,current_timestamp)",
            rows,
        )
    console.print(f"  [green]✓[/] {len(rows):,} tickers enriched ({errors} errors)")
    return len(rows)


# ══════════════════════════════════════════════════════════════════════════
# STEP 3 — FUNDAMENTAL SIGNALS
# ══════════════════════════════════════════════════════════════════════════

def step3_fundamental_signals(
    con_r: duckdb.DuckDBPyConnection,
    con_f: duckdb.DuckDBPyConnection,
) -> int:
    """Detect fundamental value/caution signals for stocks with fundamentals."""
    console.rule("[bold gold1]STEP 3 · Fundamental Signals")

    if not _table_exists(con_f, "fundamentals") or _row_count(con_f, "fundamentals") == 0:
        console.print("  [dim]No fundamentals data — skipping.[/]")
        return 0

    # Get tickers that exist in BOTH databases
    fund_tickers = {r[0] for r in con_f.execute(
        "SELECT DISTINCT ticker FROM fundamentals"
    ).fetchall()}
    price_tickers = set()
    if _table_exists(con_r, "tickers") and _row_count(con_r, "tickers") > 0:
        price_tickers = {r[0] for r in con_r.execute(
            "SELECT DISTINCT ticker FROM tickers"
        ).fetchall()}

    common = sorted(fund_tickers & price_tickers) if price_tickers else sorted(fund_tickers)
    if not common:
        console.print("  [dim]No overlapping tickers between fundamentals and price data.[/]")
        return 0

    signals: list[tuple] = []
    errors = 0

    # Pull all fundamentals into a DataFrame for vectorised access
    fund_df = con_f.execute(
        "SELECT ticker, report_date, metric, value FROM fundamentals ORDER BY ticker, report_date"
    ).fetchdf()

    with _progress() as prog:
        task = prog.add_task("Fundamentals", total=len(common))
        for tkr in common:
            try:
                tf = fund_df[fund_df["ticker"] == tkr].copy()
                if tf.empty:
                    prog.advance(task)
                    continue

                # Pivot so each metric is a column, date is the index
                piv = tf.pivot_table(index="report_date", columns="metric", values="value", aggfunc="last")
                piv = piv.sort_index()
                if len(piv) < 2:
                    prog.advance(task)
                    continue

                # ── P/E trend ──
                if "pe_ratio" in piv.columns and piv["pe_ratio"].notna().sum() >= 4:
                    pe = piv["pe_ratio"].dropna().tail(4)
                    if len(pe) >= 2:
                        if pe.iloc[-1] > pe.iloc[0] * 1.1:
                            signals.append((tkr, "PE_EXPANDING",
                                f"{tkr}: P/E expanding from {pe.iloc[0]:.1f} to {pe.iloc[-1]:.1f} over last {len(pe)} quarters",
                                2, _TODAY))
                        elif pe.iloc[-1] < pe.iloc[0] * 0.9:
                            signals.append((tkr, "PE_CONTRACTING",
                                f"{tkr}: P/E contracting from {pe.iloc[0]:.1f} to {pe.iloc[-1]:.1f} — getting cheaper",
                                3, _TODAY))

                # ── Revenue growth vs price ──
                if "revenue" in piv.columns and piv["revenue"].notna().sum() >= 4:
                    rev = piv["revenue"].dropna().tail(4)
                    rev_growth = _pct_change(float(rev.iloc[0]), float(rev.iloc[-1]))
                    # Get price change over same period
                    if tkr in price_tickers:
                        try:
                            price_row = con_r.execute(
                                "SELECT close_price FROM tickers WHERE ticker = ? "
                                "ORDER BY price_date DESC LIMIT 1", [tkr]
                            ).fetchone()
                            price_row_old = con_r.execute(
                                "SELECT close_price FROM tickers WHERE ticker = ? "
                                "AND price_date <= ? ORDER BY price_date DESC LIMIT 1",
                                [tkr, str(piv.index[0])[:10]]
                            ).fetchone()
                            if price_row and price_row_old:
                                price_chg = _pct_change(price_row_old[0], price_row[0])
                                if rev_growth is not None and price_chg is not None:
                                    if rev_growth > 10 and price_chg < -5:
                                        signals.append((tkr, "REVENUE_PRICE_DIVERGE",
                                            f"{tkr}: revenue +{rev_growth:.0f}% YoY but stock {price_chg:+.0f}% — potential value",
                                            4, _TODAY))
                        except Exception:
                            pass

                # ── Margin trend ──
                for margin_col in ["gross_margin", "operating_margin", "net_margin", "profit_margin"]:
                    if margin_col in piv.columns and piv[margin_col].notna().sum() >= 4:
                        mg = piv[margin_col].dropna().tail(4)
                        if len(mg) >= 3:
                            declining = all(mg.iloc[i] > mg.iloc[i + 1] for i in range(len(mg) - 1))
                            improving = all(mg.iloc[i] < mg.iloc[i + 1] for i in range(len(mg) - 1))
                            if declining:
                                signals.append((tkr, "MARGIN_DECLINING",
                                    f"{tkr}: {margin_col} declining {len(mg)} consecutive quarters ({mg.iloc[0]:.1f}% → {mg.iloc[-1]:.1f}%)",
                                    3, _TODAY))
                            elif improving:
                                signals.append((tkr, "MARGIN_IMPROVING",
                                    f"{tkr}: {margin_col} improving {len(mg)} consecutive quarters ({mg.iloc[0]:.1f}% → {mg.iloc[-1]:.1f}%)",
                                    3, _TODAY))
                        break  # Only use first available margin metric

                # ── Debt-to-equity ──
                if "debt_to_equity" in piv.columns and piv["debt_to_equity"].notna().sum() >= 4:
                    dte = piv["debt_to_equity"].dropna().tail(4)
                    if len(dte) >= 2 and dte.iloc[-1] > dte.iloc[0] * 1.15:
                        signals.append((tkr, "DEBT_RISING",
                            f"{tkr}: debt/equity rising from {dte.iloc[0]:.2f} to {dte.iloc[-1]:.2f} — caution",
                            3, _TODAY))

                # ── Free cash flow yield ──
                if "free_cash_flow" in piv.columns and piv["free_cash_flow"].notna().sum() >= 1:
                    fcf = piv["free_cash_flow"].dropna().iloc[-1]
                    if tkr in price_tickers:
                        try:
                            p = con_r.execute(
                                "SELECT close_price FROM tickers WHERE ticker = ? ORDER BY price_date DESC LIMIT 1",
                                [tkr],
                            ).fetchone()
                            if p and p[0] > 0:
                                # Rough FCF yield (annualised quarterly FCF / price as proxy)
                                fcf_yield = (fcf * 4) / p[0]
                                if fcf_yield > 0.08:
                                    signals.append((tkr, "HIGH_FCF_YIELD",
                                        f"{tkr}: estimated FCF yield ~{fcf_yield:.0%} — strong cash generation",
                                        4, _TODAY))
                        except Exception:
                            pass

            except Exception:
                errors += 1
                logger.debug("fundamental_signals error for %s: %s", tkr, traceback.format_exc())
            prog.advance(task)

    con_r.execute("DELETE FROM fundamental_signals")
    if signals:
        con_r.executemany(
            "INSERT INTO fundamental_signals VALUES (?,?,?,?,?)",
            signals,
        )
    console.print(f"  [green]✓[/] {len(signals):,} signals from {len(common):,} stocks ({errors} errors)")
    return len(signals)


# ══════════════════════════════════════════════════════════════════════════
# STEP 4 — REGIME CHANGE DETECTION
# ══════════════════════════════════════════════════════════════════════════

def step4_regime_signals(con: duckdb.DuckDBPyConnection) -> int:
    """Detect unusual moves across all indicators."""
    console.rule("[bold gold1]STEP 4 · Regime Change Detection")

    if not _table_exists(con, "indicators") or _row_count(con, "indicators") == 0:
        console.print("  [dim]No indicators — skipping.[/]")
        return 0

    series_ids = con.execute(
        "SELECT DISTINCT series_id FROM indicators ORDER BY series_id"
    ).fetchall()

    signals: list[tuple] = []
    errors = 0

    with _progress() as prog:
        task = prog.add_task("Regime scan", total=len(series_ids))
        for (sid,) in series_ids:
            try:
                df = con.execute(
                    "SELECT obs_date, value FROM indicators WHERE series_id = ? ORDER BY obs_date",
                    [sid],
                ).fetchdf()
                if len(df) < 6:
                    prog.advance(task)
                    continue

                vals = df["value"].values.astype(float)
                dates = pd.to_datetime(df["obs_date"])

                # Direction reversal in last 2 months
                if len(vals) >= 8:
                    old_dir = _direction(vals[-6:-3].mean(), vals[-9:-6].mean() if len(vals) >= 9 else vals[:-6].mean())
                    new_dir = _direction(vals[-3:].mean(), vals[-6:-3].mean())
                    if old_dir != new_dir and old_dir != "FLAT" and new_dir != "FLAT":
                        signals.append(("DIRECTION_REVERSAL", sid,
                            f"{sid}: flipped from {old_dir} to {new_dir} in last 2 months",
                            _TODAY, 4))

                # New 5-year high or low
                cutoff_5y = _TODAY - timedelta(days=5 * 365)
                mask_5y = dates >= pd.Timestamp(cutoff_5y)
                vals_5y = vals[mask_5y.values] if mask_5y.any() else vals
                if len(vals_5y) >= 12:
                    if vals[-1] >= np.nanmax(vals_5y):
                        signals.append(("NEW_5Y_HIGH", sid,
                            f"{sid}: hit new 5-year high at {vals[-1]:.4g}",
                            _TODAY, 3))
                    elif vals[-1] <= np.nanmin(vals_5y):
                        signals.append(("NEW_5Y_LOW", sid,
                            f"{sid}: hit new 5-year low at {vals[-1]:.4g}",
                            _TODAY, 3))

                # 3-month RoC in top/bottom 10%
                if len(vals) >= 7:
                    rocs = []
                    for i in range(3, len(vals)):
                        r = _pct_change(float(vals[i - 3]), float(vals[i]))
                        if r is not None:
                            rocs.append(r)
                    if rocs:
                        current_roc = rocs[-1]
                        p10 = np.percentile(rocs, 10)
                        p90 = np.percentile(rocs, 90)
                        if current_roc >= p90:
                            signals.append(("EXTREME_RISE", sid,
                                f"{sid}: 3-month change ({current_roc:+.1f}%) in top 10% historically",
                                _TODAY, 4))
                        elif current_roc <= p10:
                            signals.append(("EXTREME_FALL", sid,
                                f"{sid}: 3-month change ({current_roc:+.1f}%) in bottom 10% historically",
                                _TODAY, 4))

            except Exception:
                errors += 1
                logger.debug("regime error for %s: %s", sid, traceback.format_exc())
            prog.advance(task)

    # ── Yield curve inversion check ──
    try:
        t10 = con.execute(
            "SELECT value FROM indicators WHERE series_id IN ('DGS10','GS10','10Y_TREASURY') "
            "ORDER BY obs_date DESC LIMIT 1"
        ).fetchone()
        t2 = con.execute(
            "SELECT value FROM indicators WHERE series_id IN ('DGS2','GS2','2Y_TREASURY') "
            "ORDER BY obs_date DESC LIMIT 1"
        ).fetchone()
        if t10 and t2:
            spread = t10[0] - t2[0]
            if spread < 0:
                signals.append(("YIELD_CURVE_INVERTED", "10Y-2Y Spread",
                    f"Yield curve INVERTED: 10Y ({t10[0]:.2f}%) - 2Y ({t2[0]:.2f}%) = {spread:+.2f}% — recession signal",
                    _TODAY, 5))
            elif spread < 0.25:
                signals.append(("YIELD_CURVE_FLAT", "10Y-2Y Spread",
                    f"Yield curve nearly flat: spread {spread:+.2f}% — watch closely",
                    _TODAY, 3))
    except Exception:
        pass

    con.execute("DELETE FROM regime_signals")
    if signals:
        con.executemany("INSERT INTO regime_signals VALUES (?,?,?,?,?)", signals)
    console.print(f"  [green]✓[/] {len(signals):,} regime signals detected ({errors} errors)")
    return len(signals)


# ══════════════════════════════════════════════════════════════════════════
# STEP 5 — CROSS-ASSET DIVERGENCE DETECTION
# ══════════════════════════════════════════════════════════════════════════

def step5_divergence_signals(con: duckdb.DuckDBPyConnection) -> int:
    """Compare current vs historical correlations from heartbeat patterns."""
    console.rule("[bold gold1]STEP 5 · Cross-Asset Divergence")

    # Try heartbeat_patterns table first, fall back to iron_laws
    source_table = None
    for t in ("heartbeat_patterns", "iron_laws"):
        if _table_exists(con, t) and _row_count(con, t) > 0:
            source_table = t
            break

    if source_table is None:
        # Try loading from algorithms JSON
        if ALGORITHMS_JSON.exists():
            console.print(f"  [dim]Loading from {ALGORITHMS_JSON.name}...[/]")
            try:
                algo_data = json.loads(ALGORITHMS_JSON.read_text())
                # We'll work with whatever structure is in the JSON
                rules = algo_data if isinstance(algo_data, list) else algo_data.get("rules", [])
                if not rules:
                    console.print("  [dim]No heartbeat data available — skipping.[/]")
                    return 0
                # Convert to pairs
                pairs = []
                for rule in rules:
                    ind = rule.get("indicator", rule.get("series_id", ""))
                    tkr = rule.get("ticker", rule.get("target", ""))
                    corr = rule.get("correlation", rule.get("r", 0))
                    if ind and tkr and abs(corr) >= 0.80:
                        pairs.append((ind, tkr, corr))
            except Exception:
                console.print("  [dim]Failed to parse algorithms JSON — skipping.[/]")
                return 0
        else:
            console.print("  [dim]No heartbeat/iron_laws data — skipping.[/]")
            return 0
    else:
        corr_col = "correlation"
        pairs_raw = con.execute(
            f"SELECT indicator, ticker, {corr_col} FROM {source_table} "
            f"WHERE abs({corr_col}) >= 0.80"
        ).fetchall()
        pairs = [(r[0], r[1], r[2]) for r in pairs_raw]

    if not pairs:
        console.print("  [dim]No high-correlation pairs (|r| ≥ 0.80) — skipping.[/]")
        return 0

    signals: list[tuple] = []
    errors = 0

    with _progress() as prog:
        task = prog.add_task("Divergences", total=len(pairs))
        for ind, tkr, hist_r in pairs:
            try:
                # Get 3-month indicator data
                ind_df = con.execute(
                    "SELECT obs_date, value FROM indicators WHERE series_id = ? "
                    "ORDER BY obs_date DESC LIMIT 90", [ind]
                ).fetchdf()
                tkr_df = con.execute(
                    "SELECT price_date AS obs_date, close_price AS value FROM tickers "
                    "WHERE ticker = ? ORDER BY price_date DESC LIMIT 90", [tkr]
                ).fetchdf()

                if len(ind_df) < 3 or len(tkr_df) < 3:
                    prog.advance(task)
                    continue

                # Resample both to monthly for correlation
                ind_df["obs_date"] = pd.to_datetime(ind_df["obs_date"])
                tkr_df["obs_date"] = pd.to_datetime(tkr_df["obs_date"])
                ind_m = ind_df.set_index("obs_date").resample("MS").last().dropna()
                tkr_m = tkr_df.set_index("obs_date").resample("MS").last().dropna()

                merged = ind_m.join(tkr_m, lsuffix="_ind", rsuffix="_tkr", how="inner")
                if len(merged) < 3:
                    prog.advance(task)
                    continue

                current_r = float(merged["value_ind"].corr(merged["value_tkr"]))
                div_mag = abs(hist_r - current_r)

                if div_mag > 0.30:
                    desc = (
                        f"{ind} ↔ {tkr}: historical r={hist_r:.2f}, "
                        f"current 3m r={current_r:.2f} — divergence {div_mag:.2f}"
                    )
                    signals.append((ind, tkr, round(hist_r, 4), round(current_r, 4),
                                    round(div_mag, 4), desc))

            except Exception:
                errors += 1
            prog.advance(task)

    con.execute("DELETE FROM divergence_signals")
    if signals:
        con.executemany("INSERT INTO divergence_signals VALUES (?,?,?,?,?,?)", signals)
    console.print(f"  [green]✓[/] {len(signals):,} divergences from {len(pairs):,} pairs ({errors} errors)")
    return len(signals)


# ══════════════════════════════════════════════════════════════════════════
# STEP 6 — CONSUMER PRICE TRACKING
# ══════════════════════════════════════════════════════════════════════════

def step6_consumer_insights(
    con_r: duckdb.DuckDBPyConnection,
    con_d: duckdb.DuckDBPyConnection,
) -> int:
    """Cross-reference CPI subcategories, discount calendar, and retail tickers."""
    console.rule("[bold gold1]STEP 6 · Consumer Price Tracking")

    insights: list[tuple] = []

    # ── CPI subcategory changes ──
    cpi_keywords = ["CPI", "CPIAUCSL", "cpi_food", "cpi_energy", "cpi_medical",
                     "cpi_housing", "cpi_transport", "cpi_apparel", "cpi_education",
                     "CPIFABSL", "CPIENGSL", "CPIMEDSL", "CPIHOSSL"]
    try:
        all_series = con_r.execute(
            "SELECT DISTINCT series_id FROM indicators"
        ).fetchall()
        all_ids = [r[0] for r in all_series]
        cpi_ids = [s for s in all_ids if any(kw.lower() in s.lower() for kw in cpi_keywords)]

        for sid in cpi_ids:
            try:
                rows = con_r.execute(
                    "SELECT obs_date, value FROM indicators WHERE series_id = ? ORDER BY obs_date DESC LIMIT 13",
                    [sid],
                ).fetchall()
                if len(rows) >= 2:
                    current = rows[0][1]
                    year_ago = rows[-1][1] if len(rows) >= 12 else rows[-1][1]
                    change = _pct_change(year_ago, current)
                    if change is not None:
                        direction = "MORE EXPENSIVE" if change > 0 else "CHEAPER"
                        insights.append((
                            "CPI_CHANGE", sid,
                            f"{sid}: {change:+.1f}% YoY — getting {direction}",
                            _TODAY,
                        ))
            except Exception:
                continue
    except Exception:
        pass

    # ── Upcoming discount events (next 90 days) ──
    try:
        if _table_exists(con_d, "discount_calendar") and _row_count(con_d, "discount_calendar") > 0:
            cutoff_90 = _TODAY + timedelta(days=90)
            events = con_d.execute(
                "SELECT event_name, start_date, category, avg_discount_pct "
                "FROM discount_calendar WHERE start_date >= ? AND start_date <= ? "
                "ORDER BY start_date",
                [str(_TODAY), str(cutoff_90)],
            ).fetchall()
            for ev_name, start, cat, disc_pct in events:
                insights.append((
                    "UPCOMING_DISCOUNT", cat or "general",
                    f"{ev_name} ({start}): avg {disc_pct:.0f}% off — plan purchases",
                    _TODAY,
                ))
    except Exception:
        pass

    # ── Retail tickers near 52-week lows ──
    retail_keywords = ["WMT", "TGT", "COST", "AMZN", "DG", "DLTR", "KR", "HD",
                       "LOW", "BBBY", "M", "JWN", "KSS", "GPS", "ANF", "AEO",
                       "ROST", "TJX", "BURL", "FIVE", "OLLI"]
    try:
        if _table_exists(con_r, "ticker_context") and _row_count(con_r, "ticker_context") > 0:
            for tkr in retail_keywords:
                row = con_r.execute(
                    "SELECT ticker, latest_price, pct_from_52w_low, near_52w_low "
                    "FROM ticker_context WHERE ticker = ?", [tkr]
                ).fetchone()
                if row and row[3]:  # near_52w_low is True
                    insights.append((
                        "RETAILER_NEAR_LOW", tkr,
                        f"{tkr} near 52-week low (${row[1]:.2f}, {row[2]:+.1f}% from low) — struggling retailer = potential bigger consumer discounts",
                        _TODAY,
                    ))
    except Exception:
        pass

    con_r.execute("DELETE FROM consumer_insights")
    if insights:
        con_r.executemany("INSERT INTO consumer_insights VALUES (?,?,?,?)", insights)
    console.print(f"  [green]✓[/] {len(insights):,} consumer insights generated")
    return len(insights)


# ══════════════════════════════════════════════════════════════════════════
# STEP 7 — ACTIVE PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════

def step7_active_predictions(con: duckdb.DuckDBPyConnection) -> int:
    """For each predictive heartbeat pattern (lag > 0), generate prediction."""
    console.rule("[bold gold1]STEP 7 · Active Predictions")

    # Find source of lagged patterns
    source_table = None
    for t in ("heartbeat_patterns", "iron_laws"):
        if _table_exists(con, t) and _row_count(con, t) > 0:
            source_table = t
            break

    if source_table is None:
        console.print("  [dim]No heartbeat/iron_laws data — skipping.[/]")
        return 0

    try:
        lagged = con.execute(
            f"SELECT indicator, ticker, correlation, lag_months, confidence "
            f"FROM {source_table} WHERE lag_months > 0 AND abs(correlation) >= 0.60 "
            f"ORDER BY abs(correlation) DESC"
        ).fetchall()
    except Exception:
        # Table might lack confidence column
        try:
            lagged = con.execute(
                f"SELECT indicator, ticker, correlation, lag_months, 0.0 AS confidence "
                f"FROM {source_table} WHERE lag_months > 0 AND abs(correlation) >= 0.60"
            ).fetchall()
        except Exception:
            console.print("  [dim]Could not query lagged patterns — skipping.[/]")
            return 0

    if not lagged:
        console.print("  [dim]No predictive (lagged) patterns found — skipping.[/]")
        return 0

    predictions: list[tuple] = []
    errors = 0

    with _progress() as prog:
        task = prog.add_task("Predictions", total=len(lagged))
        for ind, tkr, corr, lag, conf in lagged:
            try:
                # Get current indicator value + direction
                ctx = con.execute(
                    "SELECT latest_value, direction FROM indicator_context WHERE series_id = ?",
                    [ind],
                ).fetchone()
                if not ctx:
                    prog.advance(task)
                    continue

                ind_val, ind_dir = ctx

                # Predicted direction based on correlation sign + indicator direction
                if corr > 0:
                    pred_dir = ind_dir  # same direction
                else:
                    pred_dir = {"RISING": "FALLING", "FALLING": "RISING", "FLAT": "FLAT"}.get(ind_dir, "FLAT")

                arrival = _TODAY + timedelta(days=lag * 30)

                # Last 3 times indicator was at similar level & direction
                summary = _last_3_outcomes(con, ind, tkr, ind_val, ind_dir)

                predictions.append((
                    ind, tkr,
                    round(ind_val, 4) if ind_val else None,
                    ind_dir, pred_dir,
                    arrival,
                    round(abs(corr) * (conf if conf > 0 else 0.75), 4),
                    summary,
                ))
            except Exception:
                errors += 1
            prog.advance(task)

    con.execute("DELETE FROM active_predictions")
    if predictions:
        con.executemany(
            "INSERT INTO active_predictions VALUES (?,?,?,?,?,?,?,?)",
            predictions,
        )
    console.print(f"  [green]✓[/] {len(predictions):,} active predictions ({errors} errors)")
    return len(predictions)


def _last_3_outcomes(
    con: duckdb.DuckDBPyConnection,
    indicator: str,
    ticker: str,
    current_val: float,
    current_dir: str,
) -> str:
    """Look up last 3 similar indicator states and what happened to the ticker."""
    try:
        ind_df = con.execute(
            "SELECT obs_date, value FROM indicators WHERE series_id = ? ORDER BY obs_date",
            [indicator],
        ).fetchdf()
        tkr_df = con.execute(
            "SELECT price_date, close_price FROM tickers WHERE ticker = ? ORDER BY price_date",
            [ticker],
        ).fetchdf()
        if ind_df.empty or tkr_df.empty:
            return "Insufficient historical data"

        vals = ind_df["value"].values.astype(float)
        if current_val is None or len(vals) < 6:
            return "Insufficient data"

        # Find dates when indicator was within 10% of current value
        tolerance = abs(current_val) * 0.10 if current_val != 0 else 1.0
        mask = np.abs(vals - current_val) <= tolerance
        similar_indices = np.where(mask)[0]

        if len(similar_indices) == 0:
            return "No similar historical observations"

        # Take last 3 (excluding the current)
        similar_indices = similar_indices[similar_indices < len(vals) - 1][-3:]
        outcomes = []
        tkr_df["price_date"] = pd.to_datetime(tkr_df["price_date"])

        for idx in similar_indices:
            obs_date = pd.to_datetime(ind_df.iloc[idx]["obs_date"])
            # What happened to ticker 3 months after
            future = obs_date + timedelta(days=90)
            price_at = tkr_df[tkr_df["price_date"] >= obs_date].head(1)
            price_after = tkr_df[tkr_df["price_date"] >= future].head(1)
            if not price_at.empty and not price_after.empty:
                chg = _pct_change(
                    float(price_at.iloc[0]["close_price"]),
                    float(price_after.iloc[0]["close_price"]),
                )
                if chg is not None:
                    outcomes.append(f"{obs_date.strftime('%Y-%m')}: {ticker} {chg:+.1f}%")

        return " | ".join(outcomes) if outcomes else "No matching price data"
    except Exception:
        return "Lookup error"


# ══════════════════════════════════════════════════════════════════════════
# STEP 8 — SUMMARY SNAPSHOT + DAILY BRIEFING
# ══════════════════════════════════════════════════════════════════════════

def step8_summary_and_briefing(con: duckdb.DuckDBPyConnection) -> dict:
    """Build summary_snapshot table and export daily_briefing.json."""
    console.rule("[bold gold1]STEP 8 · Summary Snapshot & Daily Briefing")

    briefing: dict[str, Any] = {
        "generated_at": _NOW_ISO,
        "market_mood": "MIXED",
        "indicator_summary": {"rising": 0, "falling": 0, "flat": 0, "total": 0},
        "ticker_summary": {"near_52w_high": 0, "near_52w_low": 0, "total": 0},
        "regime_signals": [],
        "divergences": [],
        "predictions": [],
        "consumer_outlook": {},
        "opportunities": [],
        "cautions": [],
        "fundamental_signal_count": 0,
    }

    # ── Indicator summary ──
    try:
        for d in ("RISING", "FALLING", "FLAT"):
            c = con.execute(
                "SELECT count(*) FROM indicator_context WHERE direction = ?", [d]
            ).fetchone()[0]
            briefing["indicator_summary"][d.lower()] = c
        briefing["indicator_summary"]["total"] = sum(briefing["indicator_summary"].values())
    except Exception:
        pass

    # ── Ticker summary ──
    try:
        total_t = _row_count(con, "ticker_context")
        near_h = con.execute("SELECT count(*) FROM ticker_context WHERE near_52w_high = true").fetchone()[0]
        near_l = con.execute("SELECT count(*) FROM ticker_context WHERE near_52w_low = true").fetchone()[0]
        briefing["ticker_summary"] = {"near_52w_high": near_h, "near_52w_low": near_l, "total": total_t}
    except Exception:
        pass

    # ── Market mood ──
    ind = briefing["indicator_summary"]
    tkr = briefing["ticker_summary"]
    rising_pct = ind["rising"] / max(ind["total"], 1)
    low_heavy = tkr["near_52w_low"] > tkr["near_52w_high"] * 2
    if rising_pct > 0.55 and not low_heavy:
        briefing["market_mood"] = "RISK ON"
    elif rising_pct < 0.40 or low_heavy:
        briefing["market_mood"] = "RISK OFF"
    else:
        briefing["market_mood"] = "MIXED"

    # ── Regime signals (top 10) ──
    try:
        rows = con.execute(
            "SELECT signal_type, indicator_name, description, severity "
            "FROM regime_signals ORDER BY severity DESC, indicator_name LIMIT 10"
        ).fetchall()
        briefing["regime_signals"] = [
            {"type": r[0], "indicator": r[1], "description": r[2], "severity": r[3]}
            for r in rows
        ]
    except Exception:
        pass

    # ── Divergences (top 10) ──
    try:
        rows = con.execute(
            "SELECT indicator, ticker, historical_r, current_r_3m, divergence_magnitude, description "
            "FROM divergence_signals ORDER BY divergence_magnitude DESC LIMIT 10"
        ).fetchall()
        briefing["divergences"] = [
            {"indicator": r[0], "ticker": r[1], "hist_r": r[2], "current_r": r[3],
             "magnitude": r[4], "description": r[5]}
            for r in rows
        ]
    except Exception:
        pass

    # ── Predictions (top 20) ──
    try:
        rows = con.execute(
            "SELECT indicator, target_asset, current_indicator_value, indicator_direction, "
            "predicted_direction, predicted_arrival_date, confidence, last_3_outcomes_summary "
            "FROM active_predictions ORDER BY confidence DESC LIMIT 20"
        ).fetchall()
        briefing["predictions"] = [
            {"indicator": r[0], "target": r[1], "current_value": r[2],
             "direction": r[3], "predicted": r[4],
             "arrival": str(r[5]) if r[5] else None, "confidence": r[6],
             "history": r[7]}
            for r in rows
        ]
    except Exception:
        pass

    # ── Consumer outlook ──
    try:
        cpi_rows = con.execute(
            "SELECT category, description FROM consumer_insights WHERE insight_type = 'CPI_CHANGE'"
        ).fetchall()
        disc_rows = con.execute(
            "SELECT category, description FROM consumer_insights WHERE insight_type = 'UPCOMING_DISCOUNT'"
        ).fetchall()
        retail_rows = con.execute(
            "SELECT category, description FROM consumer_insights WHERE insight_type = 'RETAILER_NEAR_LOW'"
        ).fetchall()
        briefing["consumer_outlook"] = {
            "price_changes": [{"category": r[0], "description": r[1]} for r in cpi_rows],
            "upcoming_discounts": [{"category": r[0], "description": r[1]} for r in disc_rows],
            "struggling_retailers": [{"ticker": r[0], "description": r[1]} for r in retail_rows],
        }
    except Exception:
        briefing["consumer_outlook"] = {}

    # ── Opportunities (near 52w low + improving fundamentals) ──
    try:
        rows = con.execute("""
            SELECT tc.ticker, tc.latest_price, tc.pct_from_52w_low, fs.description
            FROM ticker_context tc
            JOIN fundamental_signals fs ON tc.ticker = fs.ticker
            WHERE tc.near_52w_low = true
              AND fs.signal_type IN ('MARGIN_IMPROVING','PE_CONTRACTING','REVENUE_PRICE_DIVERGE','HIGH_FCF_YIELD')
            ORDER BY tc.pct_from_52w_low ASC
            LIMIT 20
        """).fetchall()
        briefing["opportunities"] = [
            {"ticker": r[0], "price": r[1], "pct_from_low": r[2], "signal": r[3]}
            for r in rows
        ]
    except Exception:
        pass

    # ── Cautions (deteriorating fundamentals) ──
    try:
        rows = con.execute("""
            SELECT ticker, signal_type, description, strength
            FROM fundamental_signals
            WHERE signal_type IN ('MARGIN_DECLINING','DEBT_RISING','PE_EXPANDING')
            ORDER BY strength DESC
            LIMIT 20
        """).fetchall()
        briefing["cautions"] = [
            {"ticker": r[0], "type": r[1], "description": r[2], "strength": r[3]}
            for r in rows
        ]
    except Exception:
        pass

    # ── Fundamental signal count ──
    try:
        briefing["fundamental_signal_count"] = _row_count(con, "fundamental_signals")
    except Exception:
        pass

    # Save to DB
    con.execute("DELETE FROM summary_snapshot")
    con.execute(
        "INSERT INTO summary_snapshot VALUES (?, ?)",
        [_NOW_ISO, json.dumps(briefing, default=str)],
    )

    # Export JSON
    BRIEFING_OUT.parent.mkdir(parents=True, exist_ok=True)
    BRIEFING_OUT.write_text(json.dumps(briefing, indent=2, default=str))
    console.print(f"  [green]✓[/] Briefing saved → {BRIEFING_OUT}")
    return briefing


# ══════════════════════════════════════════════════════════════════════════
# DAILY INTELLIGENCE BRIEFING — formatted output
# ══════════════════════════════════════════════════════════════════════════

def print_briefing(briefing: dict) -> None:
    """Rich-formatted intelligence briefing to the console."""
    console.print()

    # ── Header Panel ──
    mood = briefing.get("market_mood", "UNKNOWN")
    mood_color = {"RISK ON": "green", "RISK OFF": "red", "MIXED": "yellow"}.get(mood, "white")
    ind = briefing.get("indicator_summary", {})
    tkr = briefing.get("ticker_summary", {})

    header_text = Text.assemble(
        ("DAILY INTELLIGENCE BRIEFING\n", "bold white"),
        (f"Generated: {briefing['generated_at']}\n\n", "dim"),
        ("Market Mood: ", "bold"),
        (f" {mood} ", f"bold {mood_color} on {mood_color}"),
        ("\n\n", ""),
        (f"Indicators: {ind.get('total', 0):,} tracked  ", ""),
        (f"↑ {ind.get('rising', 0)} RISING  ", "green"),
        (f"↓ {ind.get('falling', 0)} FALLING  ", "red"),
        (f"→ {ind.get('flat', 0)} FLAT\n", "yellow"),
        (f"Tickers:    {tkr.get('total', 0):,} tracked  ", ""),
        (f"📈 {tkr.get('near_52w_high', 0)} near 52w high  ", "green"),
        (f"📉 {tkr.get('near_52w_low', 0)} near 52w low", "red"),
    )
    console.print(Panel(header_text, title="[bold gold1]🧠 RICHY INTELLIGENCE ENGINE",
                        border_style="gold1", padding=(1, 2)))

    # ── Regime Signals Table ──
    regime = briefing.get("regime_signals", [])
    if regime:
        t = Table(title="🔴 Regime Signals (Top 10)", border_style="red", show_lines=True)
        t.add_column("Severity", style="bold red", width=8)
        t.add_column("Type", style="cyan", width=22)
        t.add_column("Description", style="white")
        for s in regime:
            sev = "🔴" * min(s.get("severity", 1), 5)
            t.add_row(sev, s.get("type", ""), s.get("description", ""))
        console.print(t)
        console.print()

    # ── Divergences Table ──
    divs = briefing.get("divergences", [])
    if divs:
        t = Table(title="⚡ Divergence Signals (Top 10)", border_style="yellow", show_lines=True)
        t.add_column("Indicator", style="cyan", width=18)
        t.add_column("Ticker", style="bold", width=8)
        t.add_column("Hist r", width=8)
        t.add_column("Now r", width=8)
        t.add_column("Gap", style="bold yellow", width=8)
        for d in divs:
            t.add_row(d["indicator"], d["ticker"],
                      f'{d.get("hist_r", 0):.2f}',
                      f'{d.get("current_r", 0):.2f}',
                      f'{d.get("magnitude", 0):.2f}')
        console.print(t)
        console.print()

    # ── Predictions Table ──
    preds = briefing.get("predictions", [])
    if preds:
        t = Table(title="🔮 Active Predictions (Top 20)", border_style="magenta", show_lines=True)
        t.add_column("Indicator", style="cyan", width=18)
        t.add_column("Target", style="bold", width=8)
        t.add_column("Predicted", width=10)
        t.add_column("Arrives", width=12)
        t.add_column("Conf", width=6)
        t.add_column("History", style="dim", width=40)
        for p in preds[:20]:
            t.add_row(
                p.get("indicator", ""),
                p.get("target", ""),
                p.get("predicted", ""),
                str(p.get("arrival", "")),
                f'{p.get("confidence", 0):.2f}',
                (p.get("history", "") or "")[:40],
            )
        console.print(t)
        console.print()

    # ── Opportunities ──
    opps = briefing.get("opportunities", [])
    if opps:
        t = Table(title="💎 Opportunities (Near 52w Low + Improving Fundamentals)",
                  border_style="green", show_lines=True)
        t.add_column("Ticker", style="bold green", width=8)
        t.add_column("Price", width=10)
        t.add_column("From Low", width=10)
        t.add_column("Signal", style="white")
        for o in opps[:10]:
            t.add_row(o["ticker"], f'${o["price"]:.2f}',
                      f'{o.get("pct_from_low", 0):+.1f}%',
                      o.get("signal", ""))
        console.print(t)
        console.print()

    # ── Cautions ──
    cauts = briefing.get("cautions", [])
    if cauts:
        t = Table(title="⚠️ Cautions (Deteriorating Fundamentals)",
                  border_style="red", show_lines=True)
        t.add_column("Ticker", style="bold red", width=8)
        t.add_column("Type", style="cyan", width=22)
        t.add_column("Description", style="white")
        for c in cauts[:10]:
            t.add_row(c["ticker"], c["type"], c.get("description", ""))
        console.print(t)
        console.print()

    # ── Consumer Outlook ──
    consumer = briefing.get("consumer_outlook", {})
    price_chgs = consumer.get("price_changes", [])
    discounts = consumer.get("upcoming_discounts", [])
    if price_chgs or discounts:
        t = Table(title="🛒 Consumer Outlook", border_style="blue", show_lines=True)
        t.add_column("Type", style="cyan", width=20)
        t.add_column("Detail", style="white")
        for p in price_chgs[:5]:
            t.add_row("Price Change", p.get("description", ""))
        for d in discounts[:5]:
            t.add_row("Upcoming Discount", d.get("description", ""))
        console.print(t)
        console.print()

    # ── Final stats ──
    console.print(Panel(
        f"[bold]Fundamental signals:[/] {briefing.get('fundamental_signal_count', 0):,}\n"
        f"[bold]Regime signals:[/]      {len(regime)}\n"
        f"[bold]Divergences:[/]         {len(divs)}\n"
        f"[bold]Active predictions:[/]  {len(preds)}\n"
        f"[bold]Opportunities:[/]       {len(opps)}\n"
        f"[bold]Cautions:[/]            {len(cauts)}",
        title="[bold gold1]📊 Signal Counts",
        border_style="gold1",
    ))


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main() -> None:
    t0 = time.perf_counter()

    console.print()
    console.print(Panel(
        "[bold white]Richy Data Enrichment Engine[/]\n"
        "[dim]Adding intelligence layers to raw financial data[/]\n\n"
        f"[cyan]richy.duckdb:[/]        {RICHY_DB}\n"
        f"[cyan]fundamentals.duckdb:[/] {FUNDAMENTALS_DB}\n"
        f"[cyan]discount_intel.duckdb:[/] {DISCOUNT_DB}\n"
        f"[cyan]algorithms JSON:[/]     {ALGORITHMS_JSON}\n"
        f"[cyan]briefing output:[/]     {BRIEFING_OUT}",
        title="[bold gold1]🧠 DATA ENRICHMENT",
        border_style="gold1",
        padding=(1, 2),
    ))
    console.print()

    # Step 0: Bootstrap
    conns = step0_bootstrap()
    con_r = conns["richy"]
    con_f = conns["fundamentals"]
    con_d = conns["discount"]

    # Step 1: Indicator context
    n_indicators = step1_indicator_context(con_r)

    # Step 2: Ticker context
    n_tickers = step2_ticker_context(con_r)

    # Step 3: Fundamental signals
    n_fund_signals = step3_fundamental_signals(con_r, con_f)

    # Step 4: Regime signals
    n_regime = step4_regime_signals(con_r)

    # Step 5: Divergence signals
    n_diverge = step5_divergence_signals(con_r)

    # Step 6: Consumer insights
    n_consumer = step6_consumer_insights(con_r, con_d)

    # Step 7: Active predictions
    n_predictions = step7_active_predictions(con_r)

    # Step 8: Summary + briefing
    briefing = step8_summary_and_briefing(con_r)

    # Close connections
    for c in conns.values():
        try:
            c.close()
        except Exception:
            pass

    elapsed = time.perf_counter() - t0

    # Print briefing
    print_briefing(briefing)

    console.print()
    console.rule("[bold gold1]ENRICHMENT COMPLETE")
    console.print(
        f"  [bold]Runtime:[/]       {elapsed:.1f}s\n"
        f"  [bold]Indicators:[/]    {n_indicators:,} enriched\n"
        f"  [bold]Tickers:[/]       {n_tickers:,} enriched\n"
        f"  [bold]Fund signals:[/]  {n_fund_signals:,}\n"
        f"  [bold]Regime:[/]        {n_regime:,}\n"
        f"  [bold]Divergences:[/]   {n_diverge:,}\n"
        f"  [bold]Consumer:[/]      {n_consumer:,}\n"
        f"  [bold]Predictions:[/]   {n_predictions:,}\n"
        f"  [bold]Output:[/]        {BRIEFING_OUT}\n"
    )


if __name__ == "__main__":
    main()
