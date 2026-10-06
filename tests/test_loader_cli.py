"""Tests for the CSV loader, CLI, and the shipped sample data."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from margin_variance.cli import main
from margin_variance.loader import CsvFormatError, load_batches
from margin_variance.variance import analyze

SAMPLE = Path(__file__).resolve().parents[1] / "sample_data" / "batches.csv"


def test_sample_data_exists():
    assert SAMPLE.is_file()


def test_load_groups_rows_into_batches():
    batches = load_batches(SAMPLE)
    assert [b.batch_id for b in batches] == ["B-001", "B-002"]
    assert len(batches[0].materials) == 2
    assert batches[0].materials[0].material == "Rolled Oats"


def test_sample_totals_match_hand_calculation():
    results = analyze(load_batches(SAMPLE))
    by_id = {r.batch_id: r for r in results}
    assert by_id["B-001"].total_variance == Decimal("-23.508")
    assert by_id["B-002"].total_variance == Decimal("-31.995")
    portfolio = sum((r.total_variance for r in results), Decimal("0"))
    assert portfolio == Decimal("-55.503")


def test_loader_rejects_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("batch_id,product\nB-1,Thing\n", encoding="utf-8")
    with pytest.raises(CsvFormatError):
        load_batches(bad)


def test_cli_analyze_sample_returns_zero(capsys):
    rc = main(["analyze", str(SAMPLE)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "B-001" in out
    assert "Portfolio total variance" in out


def test_cli_missing_file_returns_error():
    assert main(["analyze", "does_not_exist.csv"]) == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
