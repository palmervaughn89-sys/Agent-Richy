"""Shared economic-indicator data layer for all Richy tools.

Provides ``get_latest_indicator`` and ``get_indicator_trend`` that
every tool spec references.  Data flows through three tiers:

1. **DuckDB cache** — local ``data/indicators.duckdb`` written by the
   FRED/BLS fetcher.  Fastest; authoritative when fresh.
2. **FRED / BLS API** — live pull when cache is stale (> ``MAX_AGE``).
   Requires ``FRED_API_KEY`` env-var for FRED series.
3. **Static fallback** — hand-curated reference values from
   ``economic-reference.json`` so tools *always* return something
   even without API keys or network.

Other tools do::

    from tools.data_layer import get_latest_indicator, get_indicator_trend
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Optional DuckDB import ────────────────────────────────────────────────
try:
    import duckdb

    _HAS_DUCKDB = True
except ImportError:
    _HAS_DUCKDB = False

# ── Optional requests ────────────────────────────────────────────────────
try:
    import requests

    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# ── Paths ─────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent
_DB_PATH = _ROOT / "data" / "indicators.duckdb"
_REF_PATH = (
    _ROOT
    / "agent-richy-v2"
    / "frontend"
    / "src"
    / "data"
    / "economic-reference.json"
)

# ── Cache TTL ─────────────────────────────────────────────────────────────
MAX_AGE_HOURS: int = 24  # Refetch from API after this many hours

# ── API keys ──────────────────────────────────────────────────────────────
FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")


# ═══════════════════════════════════════════════════════════════════════════
# STATIC FALLBACK REFERENCE
# ═══════════════════════════════════════════════════════════════════════════

# Values used when DuckDB and FRED are both unavailable.
# Keyed by FRED series ID → (value, unit, as_of_date).
_STATIC_FALLBACK: dict[str, tuple[float, str, str]] = {
    # ── Inflation ────────────────────────────────────────────────────────
    "CPIAUCSL":            (312.1,   "index",   "2026-01-01"),
    "CPILFESL":            (319.8,   "index",   "2026-01-01"),
    "CUSR0000SAF11":       (328.0,   "index",   "2026-01-01"),   # Food at home
    "CUSR0000SEFV":        (352.4,   "index",   "2026-01-01"),   # Food away
    "CUSR0000SEHF01":      (290.5,   "index",   "2026-01-01"),   # Electricity
    "CUSR0000SETB01":      (215.3,   "index",   "2026-01-01"),   # Gasoline
    "CUSR0000SEHG":        (235.1,   "index",   "2026-01-01"),   # Water/sewer
    "CUSR0000SEED":        (251.2,   "index",   "2026-01-01"),   # Phone
    "CUSR0000SEEE03":      (118.6,   "index",   "2026-01-01"),   # Internet
    "PCEPI":               (124.3,   "index",   "2026-01-01"),
    "PCEPILFE":            (126.1,   "index",   "2026-01-01"),
    "T5YIE":               (2.35,    "pct",     "2026-02-01"),

    # ── Jobs ─────────────────────────────────────────────────────────────
    "UNRATE":              (4.1,     "pct",     "2026-01-01"),
    "U6RATE":              (7.5,     "pct",     "2026-01-01"),
    "PAYEMS":              (157_800, "thous",   "2026-01-01"),
    "ICSA":                (218_000, "units",   "2026-02-15"),
    "JTSJOL":              (8_900,   "thous",   "2026-01-01"),
    "CES0500000003":       (35.12,   "$/hr",    "2026-01-01"),
    "MEHOINUSA646N":       (80_610,  "$/yr",    "2025-01-01"),

    # ── Rates & Money ────────────────────────────────────────────────────
    "FEDFUNDS":            (4.50,    "pct",     "2026-02-01"),
    "DFF":                 (4.50,    "pct",     "2026-02-27"),
    "DPRIME":              (7.50,    "pct",     "2026-02-27"),
    "DGS1MO":              (4.30,    "pct",     "2026-02-27"),
    "DGS3MO":              (4.35,    "pct",     "2026-02-27"),
    "DGS6MO":              (4.28,    "pct",     "2026-02-27"),
    "DGS1":                (4.20,    "pct",     "2026-02-27"),
    "DGS2":                (4.10,    "pct",     "2026-02-27"),
    "DGS5":                (4.05,    "pct",     "2026-02-27"),
    "DGS10":               (4.25,    "pct",     "2026-02-27"),
    "DGS30":               (4.45,    "pct",     "2026-02-27"),
    "T10Y2Y":              (0.15,    "pct",     "2026-02-27"),
    "T10Y3M":              (-0.10,   "pct",     "2026-02-27"),
    "MORTGAGE30US":        (6.85,    "pct",     "2026-02-20"),
    "MORTGAGE15US":        (6.10,    "pct",     "2026-02-20"),
    "MORTGAGE5US":         (6.30,    "pct",     "2026-02-20"),
    "NFCI":                (-0.25,   "index",   "2026-02-21"),
    "TERMCBCCALLNS":       (21.5,    "pct",     "2025-Q4"),
    "TERMCBAUTO48NS":      (8.40,    "pct",     "2025-Q4"),
    "RIFLPBCIANM60NM":     (8.65,    "pct",     "2025-Q4"),
    "TERMCBPER24NS":       (12.35,   "pct",     "2025-Q4"),

    # ── Consumer ─────────────────────────────────────────────────────────
    "PSAVERT":             (4.6,     "pct",     "2026-01-01"),
    "TDSP":                (11.3,    "pct",     "2026-01-01"),
    "RSXFS":               (542_100, "mil$",    "2026-01-01"),
    "UMCSENT":             (67.8,    "index",   "2026-02-01"),

    # ── Housing ──────────────────────────────────────────────────────────
    "MSPUS":               (420_400, "$",       "2025-Q4"),
    "HOUST":               (1_460,   "thous",   "2026-01-01"),
    "FIXHAI":              (98.5,    "index",   "2025-Q4"),
    "CSUSHPINSA":          (328.0,   "index",   "2025-12-01"),   # Case-Shiller national HPI
    "CUSR0000SAH1":        (380.5,   "index",   "2026-01-01"),   # CPI Shelter

    # ── Markets ──────────────────────────────────────────────────────────
    "SP500":               (5_980,   "index",   "2026-02-27"),
    "VIXCLS":              (16.2,    "index",   "2026-02-27"),
    "GOLDAMGBD228NLBM":    (2_920,   "$/oz",    "2026-02-27"),
    "DCOILWTICO":          (72.5,    "$/bbl",   "2026-02-27"),

    # ── GDP / Recession ──────────────────────────────────────────────────
    "GDPC1":               (23_100,  "bil$",    "2025-Q4"),
    "A191RL1Q225SBEA":     (2.3,     "pct",     "2025-Q4"),
    "RECPROUSM156N":       (5.2,     "pct",     "2025-12-01"),
    "SAHMREALTIME":        (0.23,    "ppt",     "2026-01-01"),
    "INDPRO":              (104.2,   "index",   "2026-01-01"),

    # ── Real yields & inflation expectations ─────────────────────────────
    "T10YIE":              (2.30,    "pct",     "2026-02-27"),   # 10Y breakeven
    "DFII5":               (1.70,    "pct",     "2026-02-27"),   # 5Y real yield
    "DFII10":              (1.95,    "pct",     "2026-02-27"),   # 10Y real yield

    # ── Credit spreads ───────────────────────────────────────────────────
    "BAMLH0A0HYM2":        (3.45,    "pct",     "2026-02-27"),   # HY OAS spread
}


# ═══════════════════════════════════════════════════════════════════════════
# DUCKDB CACHE
# ═══════════════════════════════════════════════════════════════════════════

_conn: Optional["duckdb.DuckDBPyConnection"] = None


def _get_db() -> Optional["duckdb.DuckDBPyConnection"]:
    """Return a module-level DuckDB connection (lazy-init)."""
    global _conn
    if _conn is not None:
        return _conn
    if not _HAS_DUCKDB:
        return None
    try:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = duckdb.connect(str(_DB_PATH))
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                series_id   VARCHAR NOT NULL,
                obs_date    DATE    NOT NULL,
                value       DOUBLE  NOT NULL,
                unit        VARCHAR DEFAULT '',
                fetched_at  TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (series_id, obs_date)
            )
        """)
        return _conn
    except Exception as exc:
        logger.warning("DuckDB init failed: %s", exc)
        return None


def _cache_get(series_id: str) -> Optional[tuple[float, str, str]]:
    """Read latest value for *series_id* from DuckDB cache."""
    db = _get_db()
    if db is None:
        return None
    try:
        row = db.execute(
            """
            SELECT value, unit, obs_date, fetched_at
              FROM indicators
             WHERE series_id = ?
             ORDER BY obs_date DESC
             LIMIT 1
            """,
            [series_id],
        ).fetchone()
        if row is None:
            return None
        value, unit, obs_date, fetched_at = row
        # Check freshness
        if fetched_at and (
            datetime.now() - fetched_at > timedelta(hours=MAX_AGE_HOURS)
        ):
            return None  # stale — trigger API refetch
        return (value, unit, str(obs_date))
    except Exception:
        return None


def _cache_put(series_id: str, value: float, unit: str, obs_date: str) -> None:
    """Upsert a value into the DuckDB cache."""
    db = _get_db()
    if db is None:
        return
    try:
        db.execute(
            """
            INSERT INTO indicators (series_id, obs_date, value, unit, fetched_at)
            VALUES (?, ?, ?, ?, current_timestamp)
            ON CONFLICT (series_id, obs_date)
            DO UPDATE SET value = excluded.value,
                          unit  = excluded.unit,
                          fetched_at = current_timestamp
            """,
            [series_id, obs_date, value, unit],
        )
    except Exception as exc:
        logger.warning("DuckDB cache_put failed for %s: %s", series_id, exc)


def _cache_get_trend(
    series_id: str, months: int = 3
) -> Optional[list[tuple[str, float]]]:
    """Return last *months* of data points for trend analysis."""
    db = _get_db()
    if db is None:
        return None
    try:
        rows = db.execute(
            """
            SELECT obs_date, value
              FROM indicators
             WHERE series_id = ?
               AND obs_date >= current_date - INTERVAL ? MONTH
             ORDER BY obs_date ASC
            """,
            [series_id, months],
        ).fetchall()
        if not rows:
            return None
        return [(str(r[0]), r[1]) for r in rows]
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# FRED API
# ═══════════════════════════════════════════════════════════════════════════

_FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def _fetch_fred(
    series_id: str,
    limit: int = 12,
) -> Optional[list[dict]]:
    """Fetch recent observations from FRED API.

    Returns list of {date, value} dicts, newest first.
    """
    if not _HAS_REQUESTS or not FRED_API_KEY:
        return None
    try:
        resp = requests.get(
            _FRED_BASE,
            params={
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit,
            },
            timeout=10,
        )
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
        result = []
        for obs in observations:
            try:
                result.append(
                    {"date": obs["date"], "value": float(obs["value"])}
                )
            except (ValueError, KeyError):
                continue
        return result if result else None
    except Exception as exc:
        logger.warning("FRED fetch failed for %s: %s", series_id, exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API (used by all tools via self.get_latest_indicator etc.)
# ═══════════════════════════════════════════════════════════════════════════


def get_latest_indicator(series_id: str) -> dict:
    """Return the most recent value for an economic indicator.

    Resolution order: DuckDB cache → FRED API (+ cache write) → static fallback.

    Returns::

        {
            "series_id": "UNRATE",
            "value": 4.1,
            "unit": "pct",
            "as_of": "2026-01-01",
            "source": "duckdb" | "fred" | "fallback",
        }
    """
    # 1. DuckDB cache
    cached = _cache_get(series_id)
    if cached:
        val, unit, as_of = cached
        return {
            "series_id": series_id,
            "value": val,
            "unit": unit,
            "as_of": as_of,
            "source": "duckdb",
        }

    # 2. FRED API
    fred_data = _fetch_fred(series_id, limit=1)
    if fred_data:
        latest = fred_data[0]
        fallback_unit = _STATIC_FALLBACK.get(series_id, (0, "", ""))[1]
        _cache_put(series_id, latest["value"], fallback_unit, latest["date"])
        return {
            "series_id": series_id,
            "value": latest["value"],
            "unit": fallback_unit,
            "as_of": latest["date"],
            "source": "fred",
        }

    # 3. Static fallback
    if series_id in _STATIC_FALLBACK:
        val, unit, as_of = _STATIC_FALLBACK[series_id]
        return {
            "series_id": series_id,
            "value": val,
            "unit": unit,
            "as_of": as_of,
            "source": "fallback",
        }

    # Unknown series
    return {
        "series_id": series_id,
        "value": 0.0,
        "unit": "",
        "as_of": "",
        "source": "none",
    }


def get_indicator_trend(
    series_id: str, months: int = 3
) -> dict:
    """Return trend data for an indicator over the last *months*.

    Returns::

        {
            "series_id": "UNRATE",
            "data_points": [("2025-11-01", 3.8), ("2025-12-01", 3.9), ...],
            "direction": "rising" | "falling" | "flat",
            "change": 0.3,          # first → last absolute diff
            "change_pct": 7.89,     # percentage change
            "source": "duckdb" | "fred" | "fallback",
        }
    """
    # 1. Try DuckDB
    trend = _cache_get_trend(series_id, months)
    if trend and len(trend) >= 2:
        return _build_trend_result(series_id, trend, "duckdb")

    # 2. Try FRED API (pull 12 obs for a decent history)
    fred_data = _fetch_fred(series_id, limit=12)
    if fred_data and len(fred_data) >= 2:
        # fred_data is newest-first; reverse for chronological
        pairs = [(d["date"], d["value"]) for d in reversed(fred_data)]
        # cache all of them
        fallback_unit = _STATIC_FALLBACK.get(series_id, (0, "", ""))[1]
        for date_str, val in pairs:
            _cache_put(series_id, val, fallback_unit, date_str)
        return _build_trend_result(series_id, pairs, "fred")

    # 3. Fallback — synthesise a flat trend from static value
    if series_id in _STATIC_FALLBACK:
        val, _, as_of = _STATIC_FALLBACK[series_id]
        fake_points = [(as_of, val)]
        return {
            "series_id": series_id,
            "data_points": fake_points,
            "direction": "flat",
            "change": 0.0,
            "change_pct": 0.0,
            "source": "fallback",
        }

    return {
        "series_id": series_id,
        "data_points": [],
        "direction": "unknown",
        "change": 0.0,
        "change_pct": 0.0,
        "source": "none",
    }


def _build_trend_result(
    series_id: str,
    points: list[tuple[str, float]],
    source: str,
) -> dict:
    first_val = points[0][1]
    last_val = points[-1][1]
    change = last_val - first_val
    change_pct = (change / first_val * 100) if first_val else 0.0

    if abs(change_pct) < 1.0:
        direction = "flat"
    elif change > 0:
        direction = "rising"
    else:
        direction = "falling"

    return {
        "series_id": series_id,
        "data_points": points,
        "direction": direction,
        "change": round(change, 4),
        "change_pct": round(change_pct, 2),
        "source": source,
    }
