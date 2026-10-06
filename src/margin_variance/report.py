"""Render variance results as a plain-text table.

No external dependencies: the table is formatted with the standard library so the
package stays light and easy to audit.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from margin_variance.variance import BatchVariance

_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> str:
    q = value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)
    return f"{q:+,.2f}"


def _label(value: Decimal) -> str:
    if value > 0:
        return "favourable"
    if value < 0:
        return "adverse"
    return "nil"


def format_batch(bv: BatchVariance, currency: str = "GBP") -> str:
    """Return a readable per-material and summary block for one batch."""
    lines = [f"Batch {bv.batch_id} - {bv.product}  ({currency})"]
    lines.append(f"  {'material':<22}{'price':>14}{'usage':>14}{'total':>14}")
    for m in bv.materials:
        lines.append(
            f"  {m.material:<22}{_money(m.price_variance):>14}"
            f"{_money(m.usage_variance):>14}{_money(m.total):>14}"
        )
    lines.append(f"  {'-' * 62}")
    lines.append(
        f"  {'price variance':<22}{_money(bv.total_price_variance):>14}"
        f"   ({_label(bv.total_price_variance)})"
    )
    lines.append(
        f"  {'usage variance':<22}{_money(bv.total_usage_variance):>14}"
        f"   ({_label(bv.total_usage_variance)})"
    )
    lines.append(
        f"  {'yield variance':<22}{_money(bv.yield_variance):>14}"
        f"   ({_label(bv.yield_variance)})"
    )
    lines.append(
        f"  {'TOTAL':<22}{_money(bv.total_variance):>14}"
        f"   ({_label(bv.total_variance)})"
    )
    return "\n".join(lines)


def format_report(results: list[BatchVariance], currency: str = "GBP") -> str:
    """Return a full report for several batches, with a portfolio total."""
    blocks = [format_batch(bv, currency) for bv in results]
    portfolio = sum((bv.total_variance for bv in results), Decimal("0"))
    blocks.append(
        f"\nPortfolio total variance: {_money(portfolio)} ({_label(portfolio)})"
    )
    return "\n\n".join(blocks)
