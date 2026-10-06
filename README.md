# margin-variance-kit

A clean, tested reference implementation of **CIMA standard-cost variance analysis** (price, usage, and yield variances) for manufacturing batch data.

[![CI](https://github.com/czarnf/margin-variance-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/czarnf/margin-variance-kit/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

It takes a CSV of batch production data (standard versus actual price and quantity per material, plus batch yield) and returns the variance broken down by material and by batch, valued in money, with a favourable/adverse label. Calculations use `Decimal` throughout, so results are exact and reproducible rather than subject to floating-point drift.

The kit is deliberately small and has **no runtime dependencies**. It is the standalone arithmetic core: the published accounting formulas, implemented cleanly and covered by tests.

## The variances

The sign convention is consistent everywhere: **positive is favourable** (actual better than standard), **negative is adverse**.

| Variance | Formula | Favourable when |
| --- | --- | --- |
| Material price | `(standard price − actual price) × actual quantity` | the unit price paid is below standard |
| Material usage | `(standard quantity for actual output − actual quantity) × standard price` | less material is used than the flexed standard allows |
| Material yield | `(actual output − standard output from actual input) × standard cost per output unit` | the batch yields more good output than standard implies |

where *standard output from actual input* = `total actual input × standard yield ratio`.

These are the published CIMA standard-costing variances; the kit is an implementation of them, not a new method.

## Install

```bash
pip install -e ".[dev]"   # from a clone; installs pytest + ruff for development
```

Requires Python 3.10 or newer.

## Use it: CLI

```bash
margin-variance analyze sample_data/batches.csv
```

Output (from the shipped synthetic sample):

```
Batch B-001 - Oat Granola 500g  (GBP)
  material                       price         usage         total
  Rolled Oats                   -10.50         -8.00        -18.50
  Honey                          +4.20         -7.00         -2.80
  --------------------------------------------------------------
  price variance                 -6.30   (adverse)
  usage variance                -15.00   (adverse)
  yield variance                 -2.21   (adverse)
  TOTAL                         -23.51   (adverse)
```

A `--currency` flag sets the report label (default `GBP`).

## Use it: library

```python
from margin_variance import Batch, MaterialLine, analyze_batch

batch = Batch(
    batch_id="B-001",
    product="Oat Granola 500g",
    materials=[
        MaterialLine("Rolled Oats", standard_price="0.80", actual_price="0.85",
                     standard_qty="200", actual_qty="210"),
        MaterialLine("Honey", standard_price="3.50", actual_price="3.40",
                     standard_qty="40", actual_qty="42"),
    ],
    standard_yield_ratio="0.92",
    standard_cost_per_output="1.20",
    actual_output="230",
)

result = analyze_batch(batch)
print(result.total_price_variance)  # -6.30
print(result.yield_variance)        # -2.208
print(result.total_variance)        # -23.508
```

## Input format

One row per material line; batch-level fields repeat on each row of the same batch:

```
batch_id, product, material,
standard_price, actual_price, standard_qty, actual_qty,
standard_yield_ratio, standard_cost_per_output, actual_output
```

A worked example lives in [`sample_data/batches.csv`](sample_data/batches.csv). The data shipped with the kit is synthetic.

## Tests

```bash
pytest          # unit tests for the formulas, the CSV loader, and the CLI
ruff check src/ tests/
```

CI runs the suite and the linter on Python 3.10, 3.11, and 3.12 (badge above).

## Scope

This is a focused reference for the variance arithmetic on well-formed batch data. It does not read ERP exports, reconcile documents, or manage data pipelines; it computes the standard-cost variances and nothing more. That narrow scope is the point: it keeps the maths auditable and the code easy to read.

## About

Built by Emmanuel Chiefson as part of the engineering behind [Talos Intelligent Systems](https://talosintelligentsystems.com), a data and software venture building margin-intelligence tooling for batch and process manufacturers.

## License

MIT. See [LICENSE](LICENSE).
