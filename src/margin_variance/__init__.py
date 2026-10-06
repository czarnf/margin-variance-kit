"""margin-variance-kit: CIMA standard-cost variance analysis for batch data.

A small, exact, tested reference implementation of the published CIMA material
variances (price, usage, yield) for manufacturing batch data.
"""

from margin_variance.loader import load_batches
from margin_variance.model import Batch, MaterialLine
from margin_variance.report import format_batch, format_report
from margin_variance.variance import (
    BatchVariance,
    MaterialVariance,
    analyze,
    analyze_batch,
    price_variance,
    usage_variance,
    yield_variance,
)

__version__ = "0.1.0"

__all__ = [
    "Batch",
    "MaterialLine",
    "MaterialVariance",
    "BatchVariance",
    "price_variance",
    "usage_variance",
    "yield_variance",
    "analyze_batch",
    "analyze",
    "load_batches",
    "format_batch",
    "format_report",
    "__version__",
]
