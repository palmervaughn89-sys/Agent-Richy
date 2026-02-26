"""Coupons router — /api/coupons for coupon search, daily deals, and savings tracking.

Integrates with CouponAPI.org, LinkMyDeals, or falls back to mock data.
"""

import os
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/coupons", tags=["coupons"])

COUPON_API_KEY = os.getenv("COUPON_API_KEY", "")
COUPON_API_URL = os.getenv("COUPON_API_URL", "https://api.couponapi.org/v1")


# ── Models ─────────────────────────────────────────────

class CouponRequest(BaseModel):
    stores: list[str]
    categories: list[str] = []
    zip_code: Optional[str] = None


class CouponResult(BaseModel):
    store: str
    title: str
    code: Optional[str] = None
    discount: str
    url: str
    expiry: Optional[str] = None


class ShoppingProfile(BaseModel):
    user_id: str
    grocery_stores: list[str] = []
    online_retailers: list[str] = []
    restaurants: list[str] = []
    gas_stations: list[str] = []
    categories: list[str] = []
    zip_code: str = ""


# ── In-memory stores (replace with DB in production) ───

_shopping_profiles: dict[str, ShoppingProfile] = {}
_savings_tracker: dict[str, float] = {}  # user_id → total savings


# ── Coupon Search ──────────────────────────────────────

@router.post("/search")
async def search_coupons(req: CouponRequest):
    """Search for coupons based on user's stores and preferences."""

    if not COUPON_API_KEY:
        return {
            "coupons": _get_mock_coupons(req.stores),
            "total_potential_savings": _estimate_savings_from_mocks(req.stores),
            "count": len(_get_mock_coupons(req.stores)),
            "source": "mock_data",
        }

    async with httpx.AsyncClient() as http:
        all_coupons: list[CouponResult] = []

        for store in req.stores:
            try:
                response = await http.get(
                    f"{COUPON_API_URL}/coupons",
                    params={
                        "store": store,
                        "api_key": COUPON_API_KEY,
                        "format": "json",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    coupons = data.get("coupons", data.get("offers", []))

                    for coupon in coupons[:5]:
                        all_coupons.append(CouponResult(
                            store=store,
                            title=coupon.get("title", coupon.get("offer", "")),
                            code=coupon.get("code", coupon.get("coupon_code")),
                            discount=coupon.get("discount", coupon.get("offer_value", "Deal")),
                            url=coupon.get("url", coupon.get("affiliate_link", "")),
                            expiry=coupon.get("expiry", coupon.get("end_date")),
                        ))
            except Exception as e:
                logger.warning(f"Error fetching coupons for {store}: {e}")
                continue

        total = _estimate_savings(all_coupons)

        return {
            "coupons": [c.model_dump() for c in all_coupons],
            "total_potential_savings": f"${total:.2f}",
            "count": len(all_coupons),
        }


# ── Daily Personalized Coupons ─────────────────────────

@router.post("/daily")
async def daily_coupons(user_id: str):
    """Get personalized daily coupons based on user's shopping profile."""
    profile = _shopping_profiles.get(user_id)
    if not profile:
        return {"error": "No shopping profile found. Set one up first.", "coupons": []}

    all_stores = (
        profile.grocery_stores
        + profile.online_retailers
        + profile.restaurants
        + profile.gas_stations
    )

    req = CouponRequest(
        stores=all_stores,
        categories=profile.categories,
        zip_code=profile.zip_code,
    )
    return await search_coupons(req)


# ── Shopping Profile ───────────────────────────────────

@router.post("/profile")
async def save_shopping_profile(profile: ShoppingProfile):
    """Save user's shopping preferences for personalized coupons."""
    _shopping_profiles[profile.user_id] = profile
    store_count = len(
        profile.grocery_stores
        + profile.online_retailers
        + profile.restaurants
        + profile.gas_stations
    )
    return {"status": "saved", "stores_tracked": store_count}


@router.get("/profile/{user_id}")
async def get_shopping_profile(user_id: str):
    """Get user's shopping profile."""
    profile = _shopping_profiles.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# ── Savings Tracker ────────────────────────────────────

@router.get("/savings/{user_id}")
async def get_savings(user_id: str):
    """Get user's total coupon savings."""
    total = _savings_tracker.get(user_id, 0.0)
    return {
        "user_id": user_id,
        "total_savings": f"${total:.2f}",
        "message": f"Richy has saved you ${total:.2f} so far! 🎯",
    }


@router.post("/savings/{user_id}/add")
async def add_savings(user_id: str, amount: float):
    """Track when a user redeems a coupon."""
    _savings_tracker[user_id] = _savings_tracker.get(user_id, 0.0) + amount
    new_total = _savings_tracker[user_id]
    return {"new_total": f"${new_total:.2f}"}


# ── Helpers ────────────────────────────────────────────

def _estimate_savings(coupons: list[CouponResult]) -> float:
    """Rough estimate of potential savings from coupon list."""
    total = 0.0
    for c in coupons:
        discount = c.discount.lower()
        try:
            if "%" in discount:
                pct = float(discount.replace("%", "").replace("off", "").strip())
                total += pct * 0.5  # assume ~$50 avg purchase
            elif "$" in discount:
                total += float(discount.replace("$", "").replace("off", "").strip())
            else:
                total += 2.50
        except (ValueError, AttributeError):
            total += 2.50
    return total


def _estimate_savings_from_mocks(stores: list[str]) -> str:
    mocks = _get_mock_coupons(stores)
    total = 0.0
    for c in mocks:
        d = c.get("discount", "").lower()
        try:
            if "%" in d:
                pct = float(d.replace("%", "").replace("off", "").strip())
                total += pct * 0.5
            elif "$" in d:
                total += float(d.replace("$", "").replace("off", "").strip())
            else:
                total += 2.50
        except (ValueError, AttributeError):
            total += 2.50
    return f"${total:.2f}"


def _get_mock_coupons(stores: list[str]) -> list[dict]:
    """Return mock coupons for dev/testing."""
    mock_db = {
        "walmart": [
            {"store": "Walmart", "title": "$5 off $50 grocery order", "code": "SAVE5NOW", "discount": "$5 off", "url": "https://walmart.com", "expiry": "2026-03-15"},
            {"store": "Walmart", "title": "15% off home essentials", "code": None, "discount": "15% off", "url": "https://walmart.com/deals", "expiry": "2026-03-10"},
        ],
        "target": [
            {"store": "Target", "title": "Target Circle: 20% off one item", "code": "CIRCLE20", "discount": "20% off", "url": "https://target.com", "expiry": "2026-03-20"},
        ],
        "amazon": [
            {"store": "Amazon", "title": "$10 off $50 with Prime", "code": "PRIME10", "discount": "$10 off", "url": "https://amazon.com", "expiry": "2026-03-12"},
            {"store": "Amazon", "title": "Subscribe & Save extra 15%", "code": None, "discount": "15% off", "url": "https://amazon.com/subscribe-save", "expiry": None},
        ],
        "kroger": [
            {"store": "Kroger", "title": "Free item Friday - check app", "code": None, "discount": "Free item", "url": "https://kroger.com", "expiry": "2026-03-07"},
        ],
        "chipotle": [
            {"store": "Chipotle", "title": "BOGO free entree", "code": "BOGO2026", "discount": "Buy 1 Get 1", "url": "https://chipotle.com", "expiry": "2026-03-08"},
        ],
        "starbucks": [
            {"store": "Starbucks", "title": "50% off handcrafted drinks after 3pm", "code": None, "discount": "50% off", "url": "https://starbucks.com", "expiry": "2026-03-14"},
        ],
    }

    results = []
    for store in stores:
        key = store.lower().strip()
        if key in mock_db:
            results.extend(mock_db[key])
    return results
