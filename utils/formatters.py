"""Number and currency formatting utilities for Agent Richy."""

import locale
from typing import Union


def format_currency(amount: Union[int, float], decimals: int = 0) -> str:
    """Format number as USD currency string.

    Args:
        amount: Dollar amount.
        decimals: Decimal places (default 0 for clean display).

    Returns:
        Formatted string like '$4,500' or '$4,500.00'.
    """
    if decimals == 0:
        return f"${amount:,.0f}"
    return f"${amount:,.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Format number as percentage string.

    Args:
        value: Percentage value (e.g., 15.3).
        decimals: Decimal places.

    Returns:
        Formatted string like '15.3%'.
    """
    return f"{value:.{decimals}f}%"


def format_months(months: int) -> str:
    """Convert months to a human-readable years+months string.

    Args:
        months: Total months.

    Returns:
        String like '2yr 3mo' or '8mo'.
    """
    if months <= 0:
        return "0mo"
    years = months // 12
    remaining = months % 12
    if years == 0:
        return f"{remaining}mo"
    if remaining == 0:
        return f"{years}yr"
    return f"{years}yr {remaining}mo"


def format_compact(amount: float) -> str:
    """Format large numbers compactly (e.g., $1.2M, $450K).

    Args:
        amount: Dollar amount.

    Returns:
        Compact string like '$1.2M' or '$450K'.
    """
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amt >= 1_000_000:
        return f"{sign}${abs_amt / 1_000_000:.1f}M"
    if abs_amt >= 1_000:
        return f"{sign}${abs_amt / 1_000:.0f}K"
    return f"{sign}${abs_amt:,.0f}"


def ordinal(n: int) -> str:
    """Return ordinal string (1st, 2nd, 3rd, etc.).

    Args:
        n: Integer.

    Returns:
        Ordinal string.
    """
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 * (n % 100 not in (11, 12, 13)), "th")
    return f"{n}{suffix}"
