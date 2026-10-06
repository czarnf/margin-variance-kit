"""Domain model for standard-cost variance analysis.

All monetary and quantity values use :class:`decimal.Decimal` so that results are
exact and reproducible rather than subject to binary floating-point drift.

The model is deliberately small: a batch is a product run made up of material
lines, each carrying its standard and actual price and quantity, plus the
batch-level figures needed for a yield variance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


def _d(value: object) -> Decimal:
    """Coerce a value to Decimal without passing through float."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@dataclass(frozen=True)
class MaterialLine:
    """One material consumed by a batch, with its standard and actual figures.

    Attributes:
        material: Material name or code.
        standard_price: Standard cost per unit of input (e.g. GBP per kg).
        actual_price: Actual cost per unit of input.
        standard_qty: Standard input quantity allowed for the actual output
            (the "flexed" standard, not the original plan).
        actual_qty: Actual input quantity used.
    """

    material: str
    standard_price: Decimal
    actual_price: Decimal
    standard_qty: Decimal
    actual_qty: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "standard_price", _d(self.standard_price))
        object.__setattr__(self, "actual_price", _d(self.actual_price))
        object.__setattr__(self, "standard_qty", _d(self.standard_qty))
        object.__setattr__(self, "actual_qty", _d(self.actual_qty))


@dataclass(frozen=True)
class Batch:
    """A single production run.

    Attributes:
        batch_id: Identifier for the run.
        product: Product name.
        materials: The material lines consumed.
        standard_yield_ratio: Standard output units expected per unit of total
            input (0 < ratio). A ratio of 0.9 means 100 units of input should
            yield 90 units of output under standard conditions.
        standard_cost_per_output: Standard cost of one unit of good output,
            used to value the yield variance in money terms.
        actual_output: Actual good output units produced.
    """

    batch_id: str
    product: str
    materials: list[MaterialLine]
    standard_yield_ratio: Decimal
    standard_cost_per_output: Decimal
    actual_output: Decimal
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "standard_yield_ratio", _d(self.standard_yield_ratio))
        object.__setattr__(
            self, "standard_cost_per_output", _d(self.standard_cost_per_output)
        )
        object.__setattr__(self, "actual_output", _d(self.actual_output))

    @property
    def total_actual_input(self) -> Decimal:
        return sum((m.actual_qty for m in self.materials), Decimal("0"))
