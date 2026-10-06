"""Unit tests for the variance formulas and sign convention."""

from __future__ import annotations

from decimal import Decimal

import pytest

from margin_variance.model import Batch, MaterialLine
from margin_variance.variance import (
    analyze_batch,
    price_variance,
    usage_variance,
    yield_variance,
)


def line(**kw) -> MaterialLine:
    base = dict(
        material="X",
        standard_price="1.00",
        actual_price="1.00",
        standard_qty="100",
        actual_qty="100",
    )
    base.update(kw)
    return MaterialLine(**base)


def test_price_variance_favourable_when_cheaper():
    # paid 0.85 vs standard 0.80 -> adverse; here cheaper -> favourable
    assert price_variance(line(standard_price="0.90", actual_price="0.80", actual_qty="210")) == Decimal("21.00")


def test_price_variance_adverse_when_dearer():
    assert price_variance(line(standard_price="0.80", actual_price="0.85", actual_qty="210")) == Decimal("-10.50")


def test_usage_variance_favourable_when_less_used():
    assert usage_variance(line(standard_qty="100", actual_qty="95", standard_price="2.00")) == Decimal("10.00")


def test_usage_variance_adverse_when_more_used():
    assert usage_variance(line(standard_qty="200", actual_qty="210", standard_price="0.80")) == Decimal("-8.00")


def test_yield_variance_adverse_when_output_below_expected():
    batch = Batch(
        batch_id="T",
        product="P",
        materials=[line(actual_qty="252")],
        standard_yield_ratio="0.92",
        standard_cost_per_output="1.20",
        actual_output="230",
    )
    # expected = 252 * 0.92 = 231.84 ; (230 - 231.84) * 1.20 = -2.208
    assert yield_variance(batch) == Decimal("-2.208")


def test_yield_variance_favourable_when_output_above_expected():
    batch = Batch(
        batch_id="T",
        product="P",
        materials=[line(actual_qty="100")],
        standard_yield_ratio="0.90",
        standard_cost_per_output="2.00",
        actual_output="95",
    )
    # expected = 90 ; (95 - 90) * 2 = 10
    assert yield_variance(batch) == Decimal("10.00")


def test_analyze_batch_totals():
    batch = Batch(
        batch_id="B-001",
        product="Oat Granola 500g",
        materials=[
            MaterialLine("Rolled Oats", "0.80", "0.85", "200", "210"),
            MaterialLine("Honey", "3.50", "3.40", "40", "42"),
        ],
        standard_yield_ratio="0.92",
        standard_cost_per_output="1.20",
        actual_output="230",
    )
    bv = analyze_batch(batch)
    assert bv.total_price_variance == Decimal("-6.30")
    assert bv.total_usage_variance == Decimal("-15.00")
    assert bv.yield_variance == Decimal("-2.208")
    assert bv.total_variance == Decimal("-23.508")


def test_decimal_exactness_no_float_drift():
    # 0.1 + 0.2 style traps must not appear
    v = price_variance(line(standard_price="0.30", actual_price="0.20", actual_qty="3"))
    assert v == Decimal("0.30")
    assert str(v) == "0.30"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
