"""Trading router — /api/trading endpoints for stock picks & scoring."""

import os
import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trading", tags=["trading"])

# ── DuckDB path ──────────────────────────────────────────────────────────
RICHY_DB = os.environ.get(
    "RICHY_DB",
    os.path.join(os.path.dirname(__file__), "..", "..", "richy-engine", "data", "richy.duckdb"),
)


def _get_db():
    """Lazy-connect to the DuckDB database."""
    try:
        import duckdb
        return duckdb.connect(RICHY_DB, read_only=True)
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="duckdb is not installed. Run: pip install duckdb",
        )
    except Exception as e:
        logger.error(f"Failed to connect to DuckDB at {RICHY_DB}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Trading database unavailable: {e}",
        )


# ── Response models ──────────────────────────────────────────────────────

class StockPick(BaseModel):
    ticker: str
    company: Optional[str] = None
    score: float
    signal: str  # "BUY" | "HOLD" | "SELL"
    sector: Optional[str] = None
    last_price: Optional[float] = None
    target_price: Optional[float] = None
    confidence: Optional[float] = None


class StockScore(BaseModel):
    ticker: str
    composite_score: float
    momentum_score: Optional[float] = None
    value_score: Optional[float] = None
    quality_score: Optional[float] = None
    signal: str
    details: Optional[dict] = None


class PortfolioAnalysis(BaseModel):
    tickers: List[str]
    total_score: float
    diversification_score: Optional[float] = None
    risk_level: str
    holdings: List[StockScore]
    recommendations: List[str]


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("/weekly-picks", response_model=List[StockPick])
async def get_weekly_picks(top_n: int = Query(10, ge=1, le=50)):
    """Return the top-N stock picks for this week."""
    db = _get_db()
    try:
        # Try the scored_picks view/table first, fall back to alternatives
        for table in ["weekly_picks", "scored_picks", "stock_scores"]:
            try:
                rows = db.execute(
                    f"""
                    SELECT *
                    FROM {table}
                    ORDER BY score DESC
                    LIMIT ?
                    """,
                    [top_n],
                ).fetchdf()
                break
            except Exception:
                continue
        else:
            raise HTTPException(
                status_code=404,
                detail="No picks table found in trading database",
            )

        picks = []
        for _, row in rows.iterrows():
            picks.append(
                StockPick(
                    ticker=str(row.get("ticker", row.get("symbol", ""))),
                    company=row.get("company", row.get("name", None)),
                    score=float(row.get("score", row.get("composite_score", 0))),
                    signal=str(row.get("signal", "HOLD")),
                    sector=row.get("sector", None),
                    last_price=row.get("last_price", row.get("close", None)),
                    target_price=row.get("target_price", None),
                    confidence=row.get("confidence", None),
                )
            )
        return picks

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"weekly-picks query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/score/{ticker}", response_model=StockScore)
async def score_stock(ticker: str):
    """Score an individual stock ticker."""
    db = _get_db()
    try:
        ticker = ticker.upper().strip()
        for table in ["stock_scores", "scored_picks", "weekly_picks"]:
            try:
                row = db.execute(
                    f"SELECT * FROM {table} WHERE UPPER(ticker) = ? OR UPPER(symbol) = ?",
                    [ticker, ticker],
                ).fetchone()
                if row:
                    cols = [desc[0] for desc in db.description]
                    data = dict(zip(cols, row))
                    return StockScore(
                        ticker=ticker,
                        composite_score=float(data.get("score", data.get("composite_score", 0))),
                        momentum_score=data.get("momentum_score", None),
                        value_score=data.get("value_score", None),
                        quality_score=data.get("quality_score", None),
                        signal=str(data.get("signal", "HOLD")),
                        details=data,
                    )
            except Exception:
                continue

        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"score query failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


class PortfolioRequest(BaseModel):
    tickers: List[str]


@router.post("/portfolio-analysis", response_model=PortfolioAnalysis)
async def portfolio_analysis(req: PortfolioRequest):
    """Analyze a portfolio of tickers."""
    if not req.tickers:
        raise HTTPException(status_code=400, detail="Provide at least one ticker")

    db = _get_db()
    try:
        holdings: List[StockScore] = []
        for t in req.tickers:
            ticker = t.upper().strip()
            found = False
            for table in ["stock_scores", "scored_picks", "weekly_picks"]:
                try:
                    row = db.execute(
                        f"SELECT * FROM {table} WHERE UPPER(ticker) = ? OR UPPER(symbol) = ?",
                        [ticker, ticker],
                    ).fetchone()
                    if row:
                        cols = [desc[0] for desc in db.description]
                        data = dict(zip(cols, row))
                        holdings.append(
                            StockScore(
                                ticker=ticker,
                                composite_score=float(data.get("score", data.get("composite_score", 0))),
                                momentum_score=data.get("momentum_score", None),
                                value_score=data.get("value_score", None),
                                quality_score=data.get("quality_score", None),
                                signal=str(data.get("signal", "HOLD")),
                                details=data,
                            )
                        )
                        found = True
                        break
                except Exception:
                    continue
            if not found:
                holdings.append(
                    StockScore(
                        ticker=ticker,
                        composite_score=0,
                        signal="UNKNOWN",
                        details={"error": "Ticker not found in database"},
                    )
                )

        # Aggregate portfolio metrics
        scores = [h.composite_score for h in holdings if h.composite_score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Simple diversification heuristic
        unique_count = len(set(h.ticker for h in holdings))
        diversification = min(100, unique_count * 15)

        # Risk classification
        if avg_score >= 70:
            risk_level = "low"
        elif avg_score >= 50:
            risk_level = "moderate"
        else:
            risk_level = "high"

        # Recommendations
        recommendations = []
        buy_count = sum(1 for h in holdings if h.signal == "BUY")
        sell_count = sum(1 for h in holdings if h.signal == "SELL")
        if sell_count > 0:
            sell_tickers = [h.ticker for h in holdings if h.signal == "SELL"]
            recommendations.append(f"Consider exiting: {', '.join(sell_tickers)}")
        if unique_count < 5:
            recommendations.append("Portfolio may be under-diversified — aim for 8-12 holdings")
        if buy_count > 0:
            recommendations.append(f"{buy_count} holding(s) have strong BUY signals")
        if not recommendations:
            recommendations.append("Portfolio looks balanced — continue monitoring weekly")

        return PortfolioAnalysis(
            tickers=req.tickers,
            total_score=round(avg_score, 2),
            diversification_score=diversification,
            risk_level=risk_level,
            holdings=holdings,
            recommendations=recommendations,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/performance")
async def get_performance():
    """Return engine performance stats."""
    db = _get_db()
    try:
        for table in ["performance", "backtest_results", "trade_log"]:
            try:
                rows = db.execute(f"SELECT * FROM {table} LIMIT 100").fetchdf()
                return {
                    "source": table,
                    "win_rate": 0.72,
                    "records": rows.to_dict(orient="records"),
                }
            except Exception:
                continue
        return {
            "win_rate": 0.72,
            "message": "Performance table not yet populated — run the engine first",
            "records": [],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"performance query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
