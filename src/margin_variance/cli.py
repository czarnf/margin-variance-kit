"""Command-line interface: analyze a CSV of batch data and print the variances.

    margin-variance analyze path/to/batches.csv
    margin-variance analyze path/to/batches.csv --currency EUR
"""

from __future__ import annotations

import argparse
import sys

from margin_variance.loader import CsvFormatError, load_batches
from margin_variance.report import format_report
from margin_variance.variance import analyze


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="margin-variance",
        description="CIMA standard-cost variance analysis for manufacturing batch data.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    an = sub.add_parser("analyze", help="Analyze a CSV of batch data.")
    an.add_argument("csv", help="Path to the batch CSV export.")
    an.add_argument(
        "--currency", default="GBP", help="Currency label for the report (default: GBP)."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        try:
            batches = load_batches(args.csv)
        except FileNotFoundError:
            print(f"error: file not found: {args.csv}", file=sys.stderr)
            return 2
        except CsvFormatError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if not batches:
            print("No batches found in the CSV.", file=sys.stderr)
            return 1
        print(format_report(analyze(batches), currency=args.currency))
        return 0
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
