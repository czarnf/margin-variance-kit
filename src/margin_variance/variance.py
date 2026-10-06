"""Standard-cost variance formulas (CIMA definitions).

These are the published CIMA standard-costing variances for direct materials,
expressed here as small, exact functions. The sign convention throughout is:

    positive variance  = favourable  (actual is better than standard)
    negative variance  = adverse     (actual is worse than standard)

References: CIMA Official Terminology; standard-cost variance analysis as taught
in CIMA P1 / management accounting. The formulas are public accounting standards.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from margin_variance.model import Batch, MaterialLine


def price_variance(line: MaterialLine) -> Decimal:
    """Material price variance.

    (standard price - actual price) x actual quantity

    Favourable when the actual unit price paid is below standard.
    """
    return (line.standard_price - line.actual_price) * line.actual_qty


def usage_variance(line: MaterialLine) -> Decimal:
    """Material usage (quantity) variance.

    (standard quantity for actual output - actual quantity) x standard price

    Favourable when less material is used than the flexed standard allows.
    """
    return (line.standard_qty - line.actual_qty) * line.standard_price


def yield_variance(batch: Batch) -> Decimal:
    """Material yield variance for a batch, valued in money.

    (actual output - standard output expected from the actual input)
        x standard cost per unit of output

    The standard output expected from the actual input is:

        total actual input x standard yield ratio

    Favourable when the batch produced more good output than the standard yield
    implies for the quantity of input actually consumed.
    """
    expected_output = batch.total_actual_input * batch.standard_yield_ratio
    return (batch.actual_output - expected_output) * batch.standard_cost_per_output


@dataclass(frozen=True)
class MaterialVariance:
    """Per-material price and usage variance."""

    material: str
    price_variance: Decimal
    usage_variance: Decimal

    @property
    def total(self) -> Decimal:
        return self.price_variance + self.usage_variance


@dataclass(frozen=True)
class BatchVariance:
    """The full variance breakdown for one batch."""

    batch_id: str
    product: str
    materials: list[MaterialVariance]
    yield_variance: Decimal

    @property
    def total_price_variance(self) -> Decimal:
        return sum((m.price_variance for m in self.materials), Decimal("0"))

    @property
    def total_usage_variance(self) -> Decimal:
        return sum((m.usage_variance for m in self.materials), Decimal("0"))

    @property
    def total_variance(self) -> Decimal:
        """Price + usage + yield: the total standard-cost variance for the batch."""
        return (
            self.total_price_variance
            + self.total_usage_variance
            + self.yield_variance
        )


def analyze_batch(batch: Batch) -> BatchVariance:
    """Compute price, usage and yield variances for a single batch."""
    materials = [
        MaterialVariance(
            material=line.material,
            price_variance=price_variance(line),
            usage_variance=usage_variance(line),
        )
        for line in batch.materials
    ]
    return BatchVariance(
        batch_id=batch.batch_id,
        product=batch.product,
        materials=materials,
        yield_variance=yield_variance(batch),
    )


def analyze(batches: list[Batch]) -> list[BatchVariance]:
    """Compute variances for several batches."""
    return [analyze_batch(b) for b in batches]
