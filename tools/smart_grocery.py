"""Smart Grocery — Richy's hyper-detailed consumer shopping optimiser.

Tells users EXACTLY where to shop, what to buy, and when — factoring
in store prices, gas costs, trip time, memberships, seasonal pricing,
sale calendars, and nutritionally-comparable swap suggestions.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
import math
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import combinations
from typing import Optional

from tools.base import RichyToolBase, ToolResult
from tools.data_layer import get_latest_indicator, get_indicator_trend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── USDA monthly food plans (moderate-cost, cost per person/month 2025$) ─
_USDA_MODERATE_MONTHLY: dict[str, float] = {
    "1":  332.0,    # single adult
    "2":  612.0,    # couple
    "3":  782.0,
    "4":  938.0,
    "5":  1_098.0,
    "6":  1_248.0,
}

# ── Seasonal calendar: month numbers when produce is cheapest ─────────────
_SEASONAL_CALENDAR: dict[str, dict] = {
    # item_keyword → {peak_months, off_months, savings_pct_when_peak}
    "apple":        {"peak": [9, 10, 11],      "off": [5, 6, 7],   "save_pct": 30},
    "avocado":      {"peak": [3, 4, 5, 6],     "off": [11, 12, 1], "save_pct": 40},
    "banana":       {"peak": list(range(1,13)), "off": [],          "save_pct": 0},
    "bell pepper":  {"peak": [7, 8, 9],        "off": [12, 1, 2],  "save_pct": 35},
    "berry":        {"peak": [5, 6, 7],        "off": [11, 12, 1], "save_pct": 50},
    "blueberry":    {"peak": [6, 7, 8],        "off": [11, 12, 1], "save_pct": 50},
    "strawberry":   {"peak": [4, 5, 6],        "off": [11, 12, 1], "save_pct": 45},
    "raspberry":    {"peak": [6, 7, 8],        "off": [11, 12, 1], "save_pct": 50},
    "broccoli":     {"peak": [10, 11, 3, 4],   "off": [7, 8],      "save_pct": 35},
    "cabbage":      {"peak": [1, 2, 3],        "off": [7, 8],      "save_pct": 25},
    "carrot":       {"peak": [1, 2, 3, 10, 11],"off": [7, 8],      "save_pct": 20},
    "cauliflower":  {"peak": [9, 10, 11],      "off": [6, 7],      "save_pct": 30},
    "celery":       {"peak": [1, 2, 3],        "off": [7, 8],      "save_pct": 25},
    "cherry":       {"peak": [6, 7],           "off": [10, 11, 12],"save_pct": 55},
    "corn":         {"peak": [6, 7, 8, 9],     "off": [12, 1, 2],  "save_pct": 40},
    "cucumber":     {"peak": [6, 7, 8],        "off": [12, 1, 2],  "save_pct": 30},
    "grape":        {"peak": [8, 9, 10],       "off": [2, 3, 4],   "save_pct": 35},
    "green bean":   {"peak": [6, 7, 8, 9],     "off": [12, 1, 2],  "save_pct": 30},
    "kale":         {"peak": [10, 11, 12, 1],  "off": [6, 7, 8],   "save_pct": 25},
    "lemon":        {"peak": [3, 4, 5],        "off": [9, 10],     "save_pct": 20},
    "lettuce":      {"peak": [4, 5, 6],        "off": [8, 9],      "save_pct": 20},
    "mango":        {"peak": [5, 6, 7],        "off": [11, 12, 1], "save_pct": 40},
    "melon":        {"peak": [6, 7, 8],        "off": [11, 12, 1], "save_pct": 45},
    "watermelon":   {"peak": [6, 7, 8],        "off": [11, 12, 1], "save_pct": 50},
    "onion":        {"peak": [8, 9, 10],       "off": [3, 4],      "save_pct": 20},
    "orange":       {"peak": [12, 1, 2, 3],    "off": [7, 8],      "save_pct": 30},
    "peach":        {"peak": [6, 7, 8],        "off": [11, 12, 1], "save_pct": 45},
    "pear":         {"peak": [9, 10, 11],      "off": [4, 5, 6],   "save_pct": 30},
    "pineapple":    {"peak": [3, 4, 5, 6],     "off": [10, 11],    "save_pct": 30},
    "potato":       {"peak": [9, 10, 11],      "off": [4, 5],      "save_pct": 25},
    "spinach":      {"peak": [3, 4, 5, 10, 11],"off": [7, 8],      "save_pct": 30},
    "squash":       {"peak": [9, 10, 11],      "off": [3, 4],      "save_pct": 35},
    "sweet potato": {"peak": [10, 11, 12],     "off": [5, 6],      "save_pct": 25},
    "tomato":       {"peak": [7, 8, 9],        "off": [12, 1, 2],  "save_pct": 40},
    "zucchini":     {"peak": [6, 7, 8],        "off": [12, 1, 2],  "save_pct": 35},
}

# ── Common nutritionally-comparable swaps ─────────────────────────────────
_SWAP_MAP: dict[str, list[dict]] = {
    # expensive_keyword → [{swap_name, price_ratio, reason}]
    "salmon":       [{"swap": "tilapia",           "ratio": 0.40, "reason": "lean white fish, high protein"}],
    "shrimp":       [{"swap": "chicken thigh",     "ratio": 0.30, "reason": "similar protein, much cheaper"}],
    "steak":        [{"swap": "chuck roast",       "ratio": 0.45, "reason": "slow-cook for tenderness, same nutrition"},
                     {"swap": "ground beef 80/20",  "ratio": 0.35, "reason": "versatile, high protein"}],
    "ribeye":       [{"swap": "sirloin",           "ratio": 0.55, "reason": "leaner, same cut quality"}],
    "filet":        [{"swap": "sirloin",           "ratio": 0.45, "reason": "leaner cut, great grilled"}],
    "bacon":        [{"swap": "turkey bacon",      "ratio": 0.65, "reason": "less fat, similar flavour"}],
    "almond milk":  [{"swap": "oat milk store brand","ratio": 0.60, "reason": "similar nutrition, cheaper"}],
    "greek yogurt": [{"swap": "store brand yogurt","ratio": 0.50, "reason": "same probiotics and protein"}],
    "brand cereal": [{"swap": "store brand cereal","ratio": 0.55, "reason": "identical ingredients, different box"}],
    "quinoa":       [{"swap": "brown rice",        "ratio": 0.25, "reason": "similar fibre, much cheaper grain"}],
    "pine nuts":    [{"swap": "sunflower seeds",   "ratio": 0.20, "reason": "similar texture in recipes"}],
    "cashew":       [{"swap": "peanut",            "ratio": 0.30, "reason": "similar protein, fraction of cost"}],
    "organic milk": [{"swap": "conventional milk", "ratio": 0.60, "reason": "same nutrition, lower price"}],
    "name brand":   [{"swap": "store brand",       "ratio": 0.55, "reason": "often same manufacturer, 30-45% less"}],
}

# ── Store archetype reference (used when no live store data) ──────────────
_STORE_ARCHETYPES: dict[str, dict] = {
    "aldi": {
        "price_tier": "budget",
        "price_index": 0.80,    # 80% of avg
        "avg_trip_min": 20,
        "loyalty": {"fuel_discount": False, "cashback_pct": 0},
        "strengths": ["produce", "dairy", "staples"],
        "weaknesses": ["variety", "brands"],
        "membership_annual": 0,
    },
    "walmart": {
        "price_tier": "low",
        "price_index": 0.85,
        "avg_trip_min": 35,
        "loyalty": {"fuel_discount": False, "cashback_pct": 0},
        "strengths": ["everything", "rollbacks", "great value brand"],
        "weaknesses": ["organic selection"],
        "membership_annual": 0,
    },
    "walmart_plus": {
        "price_tier": "low",
        "price_index": 0.83,
        "avg_trip_min": 10,   # delivery
        "loyalty": {"fuel_discount": True, "cashback_pct": 0},
        "strengths": ["delivery", "fuel savings"],
        "weaknesses": ["annual fee"],
        "membership_annual": 98,
    },
    "costco": {
        "price_tier": "bulk_value",
        "price_index": 0.72,   # per-unit, but large pack sizes
        "avg_trip_min": 50,
        "loyalty": {"fuel_discount": True, "cashback_pct": 2},
        "strengths": ["bulk staples", "meat", "kirkland brand", "gas"],
        "weaknesses": ["pack size", "no small quantities"],
        "membership_annual": 65,
    },
    "sams": {
        "price_tier": "bulk_value",
        "price_index": 0.74,
        "avg_trip_min": 45,
        "loyalty": {"fuel_discount": True, "cashback_pct": 0},
        "strengths": ["bulk", "member's mark brand"],
        "weaknesses": ["pack size"],
        "membership_annual": 50,
    },
    "kroger": {
        "price_tier": "mid",
        "price_index": 0.92,
        "avg_trip_min": 30,
        "loyalty": {"fuel_discount": True, "cashback_pct": 0},
        "strengths": ["digital coupons", "fuel points", "variety"],
        "weaknesses": ["base prices higher"],
        "membership_annual": 0,
    },
    "target": {
        "price_tier": "mid",
        "price_index": 0.95,
        "avg_trip_min": 30,
        "loyalty": {"fuel_discount": False, "cashback_pct": 5},
        "strengths": ["target circle 5% off", "good up & up brand"],
        "weaknesses": ["smaller grocery section"],
        "membership_annual": 0,
    },
    "publix": {
        "price_tier": "mid_high",
        "price_index": 1.05,
        "avg_trip_min": 25,
        "loyalty": {"fuel_discount": False, "cashback_pct": 0},
        "strengths": ["BOGO sales", "quality", "service"],
        "weaknesses": ["higher base prices"],
        "membership_annual": 0,
    },
    "whole_foods": {
        "price_tier": "premium",
        "price_index": 1.25,
        "avg_trip_min": 30,
        "loyalty": {"fuel_discount": False, "cashback_pct": 5},  # Prime members
        "strengths": ["organic", "quality", "365 brand"],
        "weaknesses": ["expensive"],
        "membership_annual": 0,  # Prime separate
    },
    "trader_joes": {
        "price_tier": "mid_value",
        "price_index": 0.88,
        "avg_trip_min": 25,
        "loyalty": {"fuel_discount": False, "cashback_pct": 0},
        "strengths": ["private label", "specialty items", "frozen"],
        "weaknesses": ["small stores", "limited stock"],
        "membership_annual": 0,
    },
    "amazon_fresh": {
        "price_tier": "mid",
        "price_index": 0.93,
        "avg_trip_min": 5,   # delivery
        "loyalty": {"fuel_discount": False, "cashback_pct": 5},  # Prime card
        "strengths": ["delivery", "subscribe & save 15% off"],
        "weaknesses": ["produce quality varies"],
        "membership_annual": 0,  # Prime separate
    },
    "lidl": {
        "price_tier": "budget",
        "price_index": 0.82,
        "avg_trip_min": 20,
        "loyalty": {"fuel_discount": False, "cashback_pct": 0},
        "strengths": ["produce", "bakery", "european brands"],
        "weaknesses": ["Limited US presence"],
        "membership_annual": 0,
    },
}

# ── Average food item reference prices ($/unit, national avg 2025-26) ────
_REFERENCE_PRICES: dict[str, dict] = {
    # item_keyword → {unit, avg_price, category}
    "milk":             {"unit": "gal",      "avg": 3.89,  "cat": "dairy"},
    "eggs":             {"unit": "dozen",     "avg": 3.29,  "cat": "dairy"},
    "bread":            {"unit": "loaf",      "avg": 3.59,  "cat": "bakery"},
    "butter":           {"unit": "lb",        "avg": 5.29,  "cat": "dairy"},
    "cheese":           {"unit": "lb",        "avg": 5.99,  "cat": "dairy"},
    "chicken breast":   {"unit": "lb",        "avg": 4.29,  "cat": "meat"},
    "chicken thigh":    {"unit": "lb",        "avg": 2.99,  "cat": "meat"},
    "ground beef":      {"unit": "lb",        "avg": 5.49,  "cat": "meat"},
    "steak":            {"unit": "lb",        "avg": 12.99, "cat": "meat"},
    "salmon":           {"unit": "lb",        "avg": 11.99, "cat": "seafood"},
    "shrimp":           {"unit": "lb",        "avg": 9.99,  "cat": "seafood"},
    "tilapia":          {"unit": "lb",        "avg": 4.99,  "cat": "seafood"},
    "bacon":            {"unit": "lb",        "avg": 7.49,  "cat": "meat"},
    "rice":             {"unit": "lb",        "avg": 1.29,  "cat": "grain"},
    "pasta":            {"unit": "lb",        "avg": 1.69,  "cat": "grain"},
    "cereal":           {"unit": "box",       "avg": 4.99,  "cat": "breakfast"},
    "banana":           {"unit": "lb",        "avg": 0.65,  "cat": "produce"},
    "apple":            {"unit": "lb",        "avg": 1.89,  "cat": "produce"},
    "orange":           {"unit": "lb",        "avg": 1.59,  "cat": "produce"},
    "avocado":          {"unit": "each",      "avg": 1.49,  "cat": "produce"},
    "tomato":           {"unit": "lb",        "avg": 2.29,  "cat": "produce"},
    "potato":           {"unit": "lb",        "avg": 1.19,  "cat": "produce"},
    "onion":            {"unit": "lb",        "avg": 1.29,  "cat": "produce"},
    "broccoli":         {"unit": "lb",        "avg": 2.19,  "cat": "produce"},
    "spinach":          {"unit": "bunch",     "avg": 2.49,  "cat": "produce"},
    "lettuce":          {"unit": "head",      "avg": 1.89,  "cat": "produce"},
    "carrot":           {"unit": "lb",        "avg": 1.09,  "cat": "produce"},
    "celery":           {"unit": "bunch",     "avg": 2.29,  "cat": "produce"},
    "bell pepper":      {"unit": "each",      "avg": 1.29,  "cat": "produce"},
    "cucumber":         {"unit": "each",      "avg": 0.89,  "cat": "produce"},
    "strawberry":       {"unit": "lb",        "avg": 3.49,  "cat": "produce"},
    "blueberry":        {"unit": "pint",      "avg": 3.99,  "cat": "produce"},
    "grape":            {"unit": "lb",        "avg": 2.49,  "cat": "produce"},
    "watermelon":       {"unit": "each",      "avg": 6.99,  "cat": "produce"},
    "sugar":            {"unit": "lb",        "avg": 0.89,  "cat": "baking"},
    "flour":            {"unit": "lb",        "avg": 0.69,  "cat": "baking"},
    "cooking oil":      {"unit": "qt",        "avg": 4.49,  "cat": "pantry"},
    "olive oil":        {"unit": "17oz",      "avg": 7.99,  "cat": "pantry"},
    "peanut butter":    {"unit": "jar",       "avg": 3.99,  "cat": "pantry"},
    "coffee":           {"unit": "12oz",      "avg": 8.99,  "cat": "beverage"},
    "yogurt":           {"unit": "32oz",      "avg": 4.49,  "cat": "dairy"},
    "greek yogurt":     {"unit": "32oz",      "avg": 5.99,  "cat": "dairy"},
    "almond milk":      {"unit": "half_gal",  "avg": 3.99,  "cat": "dairy_alt"},
    "oat milk":         {"unit": "half_gal",  "avg": 3.49,  "cat": "dairy_alt"},
    "frozen pizza":     {"unit": "each",      "avg": 6.49,  "cat": "frozen"},
    "ice cream":        {"unit": "pint",      "avg": 5.49,  "cat": "frozen"},
    "chips":            {"unit": "bag",        "avg": 4.49,  "cat": "snack"},
    "soda":             {"unit": "12pk",      "avg": 6.99,  "cat": "beverage"},
    "water":            {"unit": "24pk",      "avg": 4.99,  "cat": "beverage"},
    "toilet paper":     {"unit": "12pk",      "avg": 9.99,  "cat": "household"},
    "paper towel":      {"unit": "6pk",       "avg": 8.99,  "cat": "household"},
    "laundry detergent":{"unit": "bottle",    "avg": 11.99, "cat": "household"},
    "dish soap":        {"unit": "bottle",    "avg": 3.49,  "cat": "household"},
}

# ── Day-of-week markdown patterns ────────────────────────────────────────
_DOW_MARKDOWNS: dict[int, list[str]] = {
    # weekday (0=Mon) → categories likely marked down
    0: ["meat", "bakery"],        # Monday: weekend meat marked down
    1: ["meat", "bakery"],        # Tuesday: continued markdowns
    2: ["produce"],               # Wednesday: new ad starts, old produce cleared
    3: [],                        # Thursday: new sales start
    4: [],                        # Friday: pre-weekend stock
    5: ["bakery"],                # Saturday: day-old bakery
    6: [],                        # Sunday
}


# ═══════════════════════════════════════════════════════════════════════════
# SmartGrocery TOOL
# ═══════════════════════════════════════════════════════════════════════════

class SmartGrocery(RichyToolBase):
    """Hyper-detailed grocery optimisation engine.

    Tells users exactly where to shop, what to buy, and when —
    factoring in item prices, gas, time, memberships, seasonal
    pricing, upcoming sales, and nutritionally-comparable swaps.
    """

    tool_id = 16
    tool_name = "smart_grocery"
    description = (
        "Optimises grocery shopping across stores using real cost data, "
        "gas prices, trip time, seasonal calendars, and swap suggestions"
    )
    required_profile: list[str] = ["zip_code"]

    # ── Main entry points ─────────────────────────────────────────────────

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        """Router-compatible entry: extract a grocery list from the question
        and run ``optimize``."""
        grocery_list = user_profile.get("grocery_list", [])
        if not grocery_list:
            grocery_list = self._extract_items_from_question(question)
        if not grocery_list:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                confidence=0.6,
                response=(
                    "I can build you an optimised grocery plan! "
                    "Tell me what's on your list — e.g. "
                    "\"milk, eggs, chicken breast, broccoli, rice\"."
                ),
                data_used=[],
                sources=["smart_grocery"],
            )
        plan = self.optimize(grocery_list, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=0.92,
            response=self._narrate(plan),
            data_used=plan.get("data_sources_used", []),
            accuracy_score=0.88,
            sources=[
                "CUSR0000SAF11 (CPI Food)",
                "CUSR0000SETB01 (CPI Gas)",
                "USDA food plans",
                "store reference prices",
            ],
            raw_data=plan,
        )

    def optimize(
        self,
        grocery_list: list[dict],
        user_profile: dict,
    ) -> dict:
        """Full grocery optimisation pipeline.

        Args:
            grocery_list: ``[{"item": "milk", "qty": 1, "unit": "gal"}, ...]``
            user_profile: Must contain ``zip_code``; optional keys:
                ``household_size``, ``car_mpg``, ``time_value_per_hour``,
                ``memberships``, ``stores_nearby``, ``stores_willing``.

        Returns:
            Complete plan dict (see module docstring for schema).
        """
        now = datetime.now()
        month = now.month
        weekday = now.weekday()

        # ── Defaults ─────────────────────────────────────────────────────
        household = user_profile.get("household_size", 2)
        mpg = user_profile.get("car_mpg", 25.4)
        time_val = user_profile.get("time_value_per_hour", 15.0)
        memberships = set(user_profile.get("memberships", []))

        # ── Normalise the grocery list ────────────────────────────────────
        items = self._normalise_list(grocery_list)

        # ── Get economic context ──────────────────────────────────────────
        food_cpi = get_latest_indicator("CUSR0000SAF11")
        food_trend = get_indicator_trend("CUSR0000SAF11", months=3)
        gas_cpi = get_latest_indicator("CUSR0000SETB01")
        gas_price_gal = self._estimate_gas_price()
        data_used = ["CUSR0000SAF11", "CUSR0000SETB01"]

        food_inflation_warn = food_trend.get("change_pct", 0) > 3.0

        # ── Resolve stores ────────────────────────────────────────────────
        stores = self._get_store_prices(
            user_profile.get("zip_code", "00000"),
            items,
            user_profile.get("stores_nearby", []),
            user_profile.get("stores_willing"),
            memberships,
        )

        # ── Item-level optimisation ───────────────────────────────────────
        for item in items:
            item["seasonal"] = self._check_seasonal(item["key"], month)
            for store in stores:
                sid = store["id"]
                base_price = store["prices"].get(item["key"], item["ref_price"])
                sale = self._find_sale_price(store, item["key"])
                unit_price = sale if sale else base_price
                # Apply membership cashback
                cb = store["loyalty"].get("cashback_pct", 0) / 100
                effective = unit_price * (1 - cb)
                item.setdefault("store_prices", {})[sid] = {
                    "base": round(base_price, 2),
                    "effective": round(effective, 2),
                    "on_sale": sale is not None,
                    "total": round(effective * item["qty"], 2),
                }

        # ── Trip cost per store ───────────────────────────────────────────
        for store in stores:
            store["trip_cost"] = self._calculate_trip_cost(
                store, mpg, gas_price_gal, time_val,
            )

        # ── Find optimal split ────────────────────────────────────────────
        best = self._find_optimal_split(stores, items)

        # ── Seasonal alerts ───────────────────────────────────────────────
        seasonal_alerts = [
            {
                "item": it["name"],
                "status": it["seasonal"]["status"],
                "note": it["seasonal"]["note"],
            }
            for it in items
            if it["seasonal"]["status"] != "normal"
        ]

        # ── Swap suggestions ─────────────────────────────────────────────
        swaps = self._suggest_swaps(items)

        # ── Timing advice ─────────────────────────────────────────────────
        timing = self._timing_advice(items, weekday, month)

        # ── Budget projection ─────────────────────────────────────────────
        weekly_cost = best["grand_total"]
        monthly_est = weekly_cost * 4.33
        usda_target = _USDA_MODERATE_MONTHLY.get(str(min(household, 6)), 938.0)
        worst_total = max(
            (s["store_total"] for s in best.get("all_store_totals", [{}])),
            default=weekly_cost,
        )
        annual_savings = (worst_total - weekly_cost) * 52

        projection = {
            "weekly_optimized": round(weekly_cost, 2),
            "monthly_estimate": round(monthly_est, 2),
            "usda_moderate_plan": round(usda_target, 2),
            "vs_usda": "under" if monthly_est < usda_target else "over",
            "vs_usda_delta": round(monthly_est - usda_target, 2),
            "annual_savings_vs_worst": round(annual_savings, 2),
        }

        # ── Alerts from economic data ─────────────────────────────────────
        alerts: list[str] = []
        if food_inflation_warn:
            alerts.append(
                f"⚠️ Food prices rose {food_trend['change_pct']:.1f}% in the "
                f"last 3 months — consider stocking up on non-perishables now."
            )
        if gas_price_gal > 4.0:
            alerts.append(
                f"⛽ Gas is ${gas_price_gal:.2f}/gal — multi-store trips are "
                f"more expensive. I've factored this into the plan."
            )

        return {
            "strategy": best["strategy"],
            "stores": best["stores"],
            "grand_total": round(best["grand_total"], 2),
            "vs_worst_option_savings": round(
                worst_total - best["grand_total"], 2
            ),
            "timing_advice": timing,
            "seasonal_alerts": seasonal_alerts,
            "swap_suggestions": swaps,
            "monthly_projection": projection,
            "alerts": alerts,
            "data_sources_used": data_used,
        }

    # ── Helper: Normalise grocery list ────────────────────────────────────

    def _normalise_list(self, raw: list[dict]) -> list[dict]:
        """Normalise user items into a uniform format with reference prices."""
        items = []
        for entry in raw:
            name = entry.get("item", entry.get("name", "")).strip().lower()
            qty = float(entry.get("qty", entry.get("quantity", 1)))
            unit = entry.get("unit", "each")
            key = self._item_key(name)
            ref = _REFERENCE_PRICES.get(key, {})
            items.append({
                "name": name,
                "key": key,
                "qty": qty,
                "unit": unit or ref.get("unit", "each"),
                "ref_price": ref.get("avg", 3.00),
                "category": ref.get("cat", "other"),
                "seasonal": {},
                "store_prices": {},
            })
        return items

    @staticmethod
    def _item_key(name: str) -> str:
        """Map a free-text item name to a reference-data key."""
        n = name.lower().strip()
        # Direct match
        if n in _REFERENCE_PRICES:
            return n
        # Partial match
        for key in _REFERENCE_PRICES:
            if key in n or n in key:
                return key
        return n

    # ── Helper: Extract items from plain-English question ─────────────────

    @staticmethod
    def _extract_items_from_question(question: str) -> list[dict]:
        """Best-effort extraction of grocery items from a sentence."""
        import re

        # Remove filler
        q = re.sub(
            r"(?i)(i need|i want|buy|get|pick up|grab|shopping list|"
            r"grocery list|groceries|from the store|please|some|a few|and)\b",
            "",
            question,
        )
        # Split on commas, 'and', newlines
        parts = re.split(r"[,\n]+|\band\b", q)
        items = []
        for part in parts:
            part = part.strip().strip(".")
            if not part or len(part) < 2:
                continue
            # Try to extract quantity
            m = re.match(r"(\d+(?:\.\d+)?)\s*(lbs?|oz|gal|dozen|pk|each)?\s*(?:of\s+)?(.+)", part)
            if m:
                items.append({
                    "item": m.group(3).strip(),
                    "qty": float(m.group(1)),
                    "unit": m.group(2) or "each",
                })
            else:
                items.append({"item": part, "qty": 1, "unit": "each"})
        return items

    # ── Helper: Store prices ──────────────────────────────────────────────

    def _get_store_prices(
        self,
        zip_code: str,
        items: list[dict],
        stores_nearby: list[dict],
        stores_willing: list[str] | None,
        memberships: set[str],
    ) -> list[dict]:
        """Build a store list with per-item prices.

        Uses ``stores_nearby`` from profile if available, otherwise
        synthesises from archetype reference data.
        """
        resolved: list[dict] = []

        if stores_nearby:
            for s in stores_nearby:
                sid = s.get("name", "store").lower().replace(" ", "_")
                arch = _STORE_ARCHETYPES.get(sid, {})
                price_idx = arch.get("price_index", 1.0)
                prices = {}
                for it in items:
                    ref = it["ref_price"]
                    prices[it["key"]] = round(ref * price_idx, 2)
                resolved.append({
                    "id": sid,
                    "name": s.get("name", sid),
                    "distance_miles": s.get("distance_miles", 5.0),
                    "avg_trip_min": arch.get("avg_trip_min", 30),
                    "price_tier": arch.get("price_tier", "mid"),
                    "prices": prices,
                    "current_sales": s.get("current_sales", []),
                    "loyalty": arch.get("loyalty", {}),
                    "membership_annual": arch.get("membership_annual", 0),
                    "has_membership": sid in memberships,
                })
        else:
            # Synthesise from archetypes — pick a sensible default set
            default_stores = ["aldi", "walmart", "kroger", "costco", "target"]
            if stores_willing:
                default_stores = [
                    s.lower().replace(" ", "_") for s in stores_willing
                ]
            for sid in default_stores:
                arch = _STORE_ARCHETYPES.get(sid)
                if not arch:
                    continue
                price_idx = arch["price_index"]
                prices = {
                    it["key"]: round(it["ref_price"] * price_idx, 2)
                    for it in items
                }
                need_member = arch["membership_annual"] > 0
                resolved.append({
                    "id": sid,
                    "name": sid.replace("_", " ").title(),
                    "distance_miles": 4.0,   # default guess
                    "avg_trip_min": arch["avg_trip_min"],
                    "price_tier": arch["price_tier"],
                    "prices": prices,
                    "current_sales": [],
                    "loyalty": arch["loyalty"],
                    "membership_annual": arch["membership_annual"],
                    "has_membership": sid in memberships or not need_member,
                })
        return resolved

    # ── Helper: Sale price lookup ─────────────────────────────────────────

    @staticmethod
    def _find_sale_price(store: dict, item_key: str) -> float | None:
        for sale in store.get("current_sales", []):
            sale_item = sale.get("item", "").lower()
            if item_key in sale_item or sale_item in item_key:
                return float(sale.get("sale_price", 0))
        return None

    # ── Helper: Trip cost ─────────────────────────────────────────────────

    def _calculate_trip_cost(
        self,
        store: dict,
        mpg: float,
        gas_price: float,
        time_value: float,
    ) -> dict:
        """Calculate full trip cost: gas + time + amortised membership."""
        dist = store.get("distance_miles", 5.0)
        trip_min = store.get("avg_trip_min", 30)

        gas_cost = (dist * 2) / max(mpg, 1) * gas_price
        time_cost = (trip_min / 60.0) * time_value

        mem_annual = store.get("membership_annual", 0)
        if mem_annual > 0 and store.get("has_membership"):
            est_annual_visits = 24  # ~2/month
            mem_cost = mem_annual / est_annual_visits
        else:
            mem_cost = 0.0

        total = gas_cost + time_cost + mem_cost
        return {
            "gas": round(gas_cost, 2),
            "time": round(time_cost, 2),
            "membership": round(mem_cost, 2),
            "total": round(total, 2),
        }

    # ── Helper: Optimal split finder ──────────────────────────────────────

    def _find_optimal_split(
        self,
        stores: list[dict],
        items: list[dict],
    ) -> dict:
        """Find the best single-store or 2-store split.

        Rules:
        - Only recommend a split if net savings > $5.
        - Max 2 stores (3 is almost never worth it).
        - If two stores on the same road (< 1 mile apart), halve the
          second trip's gas and zero its time cost.
        """
        # ── Single-store totals ───────────────────────────────────────────
        store_totals: list[dict] = []
        for store in stores:
            food_cost = sum(
                it["store_prices"].get(store["id"], {}).get("total", it["ref_price"] * it["qty"])
                for it in items
            )
            trip = store["trip_cost"]["total"]
            total = food_cost + trip
            store_totals.append({
                "store_id": store["id"],
                "store_name": store["name"],
                "food_cost": round(food_cost, 2),
                "trip_cost": store["trip_cost"],
                "store_total": round(total, 2),
            })
        store_totals.sort(key=lambda x: x["store_total"])
        best_single = store_totals[0]

        # ── Two-store splits ──────────────────────────────────────────────
        best_split: dict | None = None
        split_min_savings = 5.0

        for s1, s2 in combinations(stores, 2):
            s1_id, s2_id = s1["id"], s2["id"]

            # Assign each item to cheapest store
            s1_items, s2_items = [], []
            s1_food, s2_food = 0.0, 0.0
            for it in items:
                p1 = it["store_prices"].get(s1_id, {}).get("effective", it["ref_price"])
                p2 = it["store_prices"].get(s2_id, {}).get("effective", it["ref_price"])
                line_total_1 = p1 * it["qty"]
                line_total_2 = p2 * it["qty"]
                if line_total_1 <= line_total_2:
                    s1_items.append(it)
                    s1_food += line_total_1
                else:
                    s2_items.append(it)
                    s2_food += line_total_2

            # If one store gets zero items, skip — it's just a single store
            if not s1_items or not s2_items:
                continue

            trip1 = s1["trip_cost"]["total"]
            trip2 = s2["trip_cost"]["total"]

            # Same-route discount
            d1 = s1.get("distance_miles", 5)
            d2 = s2.get("distance_miles", 5)
            if abs(d1 - d2) < 1.0:
                trip2 = s2["trip_cost"]["gas"] * 0.5  # marginal gas only

            split_total = s1_food + s2_food + trip1 + trip2
            savings_vs_single = best_single["store_total"] - split_total

            if savings_vs_single > split_min_savings:
                if best_split is None or split_total < best_split["grand_total"]:
                    best_split = {
                        "strategy": "two_store_split",
                        "grand_total": round(split_total, 2),
                        "stores": [
                            self._build_store_result(s1, s1_items, s1_food, s1["trip_cost"]),
                            self._build_store_result(s2, s2_items, s2_food, s2["trip_cost"]),
                        ],
                        "all_store_totals": store_totals,
                    }

        if best_split and best_split["grand_total"] < best_single["store_total"]:
            return best_split

        # Best single store
        best_s = next(s for s in stores if s["id"] == best_single["store_id"])
        return {
            "strategy": "single_store",
            "grand_total": round(best_single["store_total"], 2),
            "stores": [
                self._build_store_result(best_s, items, best_single["food_cost"], best_s["trip_cost"]),
            ],
            "all_store_totals": store_totals,
        }

    @staticmethod
    def _build_store_result(
        store: dict,
        items: list[dict],
        food_subtotal: float,
        trip_cost: dict,
    ) -> dict:
        return {
            "store_name": store["name"],
            "items_to_buy": [
                {
                    "item": it["name"],
                    "qty": it["qty"],
                    "unit_price": it["store_prices"]
                        .get(store["id"], {})
                        .get("effective", it["ref_price"]),
                    "total": it["store_prices"]
                        .get(store["id"], {})
                        .get("total", round(it["ref_price"] * it["qty"], 2)),
                    "on_sale": it["store_prices"]
                        .get(store["id"], {})
                        .get("on_sale", False),
                }
                for it in items
            ],
            "subtotal": round(food_subtotal, 2),
            "trip_cost": trip_cost,
            "store_total": round(food_subtotal + trip_cost["total"], 2),
        }

    # ── Helper: Seasonal check ────────────────────────────────────────────

    @staticmethod
    def _check_seasonal(item_key: str, month: int) -> dict:
        """Check whether an item is in season, off season, or normal."""
        for keyword, cal in _SEASONAL_CALENDAR.items():
            if keyword in item_key or item_key in keyword:
                if month in cal["peak"]:
                    return {
                        "status": "in_season",
                        "note": (
                            f"In season now — prices ~{cal['save_pct']}% "
                            f"lower than off-season. Buy extra if freezable!"
                        ),
                    }
                if month in cal["off"]:
                    # Find next peak month
                    next_peak = None
                    for m in cal["peak"]:
                        if m > month:
                            next_peak = m
                            break
                    if next_peak is None and cal["peak"]:
                        next_peak = cal["peak"][0]
                    wait_months = (
                        (next_peak - month) % 12 if next_peak else 0
                    )
                    return {
                        "status": "off_season",
                        "note": (
                            f"Out of season — paying ~{cal['save_pct']}% premium. "
                            f"Peak season starts in ~{wait_months} month(s). "
                            f"Consider frozen or canned as an alternative."
                        ),
                    }
        return {"status": "normal", "note": ""}

    # ── Helper: Sales check ───────────────────────────────────────────────

    @staticmethod
    def _check_sales(stores: list[dict], items: list[dict]) -> list[dict]:
        """Return upcoming / current sale alerts across all stores."""
        alerts: list[dict] = []
        for store in stores:
            for sale in store.get("current_sales", []):
                alerts.append({
                    "store": store["name"],
                    "item": sale.get("item", ""),
                    "sale_price": sale.get("sale_price"),
                    "valid_until": sale.get("valid_until", "unknown"),
                })
        return alerts

    # ── Helper: Swap suggestions ──────────────────────────────────────────

    @staticmethod
    def _suggest_swaps(items: list[dict]) -> list[dict]:
        """Suggest cheaper nutritionally-comparable alternatives."""
        suggestions: list[dict] = []
        for it in items:
            for keyword, swaps in _SWAP_MAP.items():
                if keyword in it["key"] or keyword in it["name"]:
                    for sw in swaps:
                        savings = round(it["ref_price"] * (1 - sw["ratio"]) * it["qty"], 2)
                        if savings > 0.50:
                            suggestions.append({
                                "original": it["name"],
                                "original_price": f"${it['ref_price']:.2f}/{it['unit']}",
                                "swap": sw["swap"],
                                "swap_price": f"${it['ref_price'] * sw['ratio']:.2f}/{it['unit']}",
                                "savings": f"${savings:.2f}",
                                "reason": sw["reason"],
                            })
        return suggestions

    # ── Helper: Timing advice ─────────────────────────────────────────────

    @staticmethod
    def _timing_advice(
        items: list[dict], weekday: int, month: int,
    ) -> list[dict]:
        """Day-of-week and seasonal timing recommendations."""
        advice: list[dict] = []
        markdown_cats = _DOW_MARKDOWNS.get(weekday, [])

        for it in items:
            cat = it.get("category", "other")
            # Day-of-week markdown check
            if cat in markdown_cats:
                advice.append({
                    "item": it["name"],
                    "advice": (
                        f"Today is a good day to buy {cat} — many stores "
                        f"mark down {cat} items today."
                    ),
                    "potential_savings": "15-40% on marked-down items",
                })
            # If meat and today is Thu-Sun, suggest waiting until Mon/Tue
            if cat in ("meat", "seafood") and weekday >= 3:
                days_to_monday = (7 - weekday) % 7
                if days_to_monday == 0:
                    days_to_monday = 1  # at least tomorrow
                advice.append({
                    "item": it["name"],
                    "advice": (
                        f"If it can wait {days_to_monday} day(s), meat markdowns "
                        f"typically happen Mon/Tue at most chains."
                    ),
                    "potential_savings": "20-50% on manager's specials",
                })

            # Seasonal buy-extra advice
            seasonal = it.get("seasonal", {})
            if seasonal.get("status") == "in_season" and cat == "produce":
                advice.append({
                    "item": it["name"],
                    "advice": (
                        f"{it['name'].title()} is at peak-season pricing. "
                        f"Buy extra and freeze for later months."
                    ),
                    "potential_savings": f"~{_SEASONAL_CALENDAR.get(it['key'], {}).get('save_pct', 25)}% vs off-season",
                })

        return advice

    # ── Helper: Gas price estimate ────────────────────────────────────────

    @staticmethod
    def _estimate_gas_price() -> float:
        """Estimate current local gas price from CPI gasoline index."""
        gas = get_latest_indicator("CUSR0000SETB01")
        # CPI gasoline base year 1982-84 = 100; rough conversion
        # Index ~215 ≈ $3.50/gal based on historical relationship
        idx = gas.get("value", 215)
        return round(idx / 61.5, 2)  # calibration factor

    # ── Narration ─────────────────────────────────────────────────────────

    def _narrate(self, plan: dict) -> str:
        """Build a human-readable summary from the plan dict."""
        lines: list[str] = []
        strategy = plan["strategy"]

        if strategy == "single_store":
            store = plan["stores"][0]
            lines.append(
                f"🛒 **Best option: {store['store_name']}** — "
                f"total **${plan['grand_total']:.2f}** "
                f"(food ${store['subtotal']:.2f} + trip ${store['trip_cost']['total']:.2f})"
            )
        else:
            lines.append(
                f"🛒 **Split across 2 stores** saves you more — "
                f"total **${plan['grand_total']:.2f}**"
            )
            for i, store in enumerate(plan["stores"], 1):
                n_items = len(store["items_to_buy"])
                lines.append(
                    f"  Store {i}: **{store['store_name']}** — "
                    f"{n_items} items, ${store['subtotal']:.2f} + "
                    f"${store['trip_cost']['total']:.2f} trip"
                )

        savings = plan.get("vs_worst_option_savings", 0)
        if savings > 1:
            lines.append(
                f"\n💰 You're saving **${savings:.2f}** vs the most expensive option."
            )

        # Seasonal
        for alert in plan.get("seasonal_alerts", [])[:3]:
            emoji = "🥬" if alert["status"] == "in_season" else "⚠️"
            lines.append(f"{emoji} **{alert['item'].title()}**: {alert['note']}")

        # Swaps
        for sw in plan.get("swap_suggestions", [])[:3]:
            lines.append(
                f"💡 Swap {sw['original']} ({sw['original_price']}) → "
                f"**{sw['swap']}** ({sw['swap_price']}) — "
                f"saves {sw['savings']}. {sw['reason'].capitalize()}."
            )

        # Timing
        for tip in plan.get("timing_advice", [])[:2]:
            lines.append(f"⏰ **{tip['item'].title()}**: {tip['advice']}")

        # Alerts
        for alert in plan.get("alerts", []):
            lines.append(alert)

        # Monthly projection
        proj = plan.get("monthly_projection", {})
        if proj:
            lines.append(
                f"\n📊 **Monthly estimate**: ${proj['monthly_estimate']:.2f} "
                f"(USDA moderate plan: ${proj['usda_moderate_plan']:.2f}). "
                f"Annual savings vs worst option: **${proj['annual_savings_vs_worst']:.2f}**"
            )

        return "\n".join(lines)
