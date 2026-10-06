"""Load batches from a CSV export.

The expected CSV has one row per material line. Batch-level fields repeat on
each row of the same batch; the first row of each batch group supplies them.

Columns (header names, case-insensitive):

    batch_id, product, material,
    standard_price, actual_price, standard_qty, actual_qty,
    standard_yield_ratio, standard_cost_per_output, actual_output
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from margin_variance.model import Batch, MaterialLine

REQUIRED_COLUMNS = {
    "batch_id",
    "product",
    "material",
    "standard_price",
    "actual_price",
    "standard_qty",
    "actual_qty",
    "standard_yield_ratio",
    "standard_cost_per_output",
    "actual_output",
}


class CsvFormatError(ValueError):
    """Raised when the CSV is missing required columns."""


def load_batches(path: str | Path) -> list[Batch]:
    """Read a CSV file and return the batches it describes, in first-seen order."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = {h.strip().lower() for h in (reader.fieldnames or [])}
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise CsvFormatError(
                f"CSV is missing required columns: {', '.join(sorted(missing))}"
            )
        rows = [{k.strip().lower(): (v or "").strip() for k, v in row.items()} for row in reader]

    grouped: dict[str, list[dict]] = {}
    order: list[str] = []
    for row in rows:
        bid = row["batch_id"]
        if not bid:
            continue
        if bid not in grouped:
            grouped[bid] = []
            order.append(bid)
        grouped[bid].append(row)

    batches: list[Batch] = []
    for bid in order:
        group = grouped[bid]
        head = group[0]
        materials = [
            MaterialLine(
                material=r["material"],
                standard_price=Decimal(r["standard_price"]),
                actual_price=Decimal(r["actual_price"]),
                standard_qty=Decimal(r["standard_qty"]),
                actual_qty=Decimal(r["actual_qty"]),
            )
            for r in group
            if r["material"]
        ]
        batches.append(
            Batch(
                batch_id=bid,
                product=head["product"],
                materials=materials,
                standard_yield_ratio=Decimal(head["standard_yield_ratio"]),
                standard_cost_per_output=Decimal(head["standard_cost_per_output"]),
                actual_output=Decimal(head["actual_output"]),
            )
        )
    return batches
