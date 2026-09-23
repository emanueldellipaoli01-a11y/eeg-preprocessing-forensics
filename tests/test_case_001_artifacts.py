import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "cases" / "case_001_highpass_01_vs_1hz"
RESULTS = CASE_DIR / "results"
FIGURES = CASE_DIR / "figures"


def test_case_001_published_artifacts_exist():
    assert (RESULTS / "manifest.json").is_file()
    assert (RESULTS / "comparison_table.csv").is_file()
    assert (RESULTS / "summary_long.csv").is_file()

    for name in (
        "erp_difference.png",
        "erp_variant_a_vs_b.png",
        "subject_level_difference.png",
    ):
        path = FIGURES / name
        assert path.is_file()
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_case_001_manifest_is_empirical_and_redacted():
    manifest = json.loads(
        (RESULTS / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["case_id"] == "case_001"
    assert manifest["dataset"] == "ERP CORE"
    assert manifest["dataset_version"] == "v1.1.1"
    assert manifest["subjects"] == [1]
    assert manifest["execution_status"] == "empirical_executed"
    assert manifest["claims"]["observed"] is True
    assert manifest["claims"]["generalization"] is False

    assert (
        manifest["raw_source_path_by_subject"]["1"]
        == "local_path_redacted"
    )


def test_case_001_csv_results_match_manifest():
    manifest = json.loads(
        (RESULTS / "manifest.json").read_text(encoding="utf-8")
    )

    with (RESULTS / "summary_long.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2

    row_a = next(row for row in rows if row["variant"] == "A")
    row_b = next(row for row in rows if row["variant"] == "B")

    assert int(row_a["subject"]) == 1
    assert int(row_b["subject"]) == 1

    assert float(row_a["highpass_hz"]) == 0.1
    assert float(row_b["highpass_hz"]) == 1.0

    assert float(row_a["primary_metric_uv"]) == manifest["metric_A_mean_uv"]
    assert float(row_b["primary_metric_uv"]) == manifest["metric_B_mean_uv"]

    assert int(row_a["n_epochs"]) == 34
    assert int(row_b["n_epochs"]) == 37

    with (RESULTS / "comparison_table.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        table = list(csv.DictReader(handle))

    values = {row["Aspect"]: row for row in table}

    assert float(values["High-pass cutoff"]["Variant A"]) == 0.1
    assert float(values["High-pass cutoff"]["Variant B"]) == 1.0

    assert float(
        values["Mean primary metric (A, µV)"]["Variant A"]
    ) == manifest["metric_A_mean_uv"]

    assert float(
        values["Mean primary metric (B, µV)"]["Variant B"]
    ) == manifest["metric_B_mean_uv"]

    assert float(
        values["Mean A−B (µV)"]["Variant A"]
    ) == manifest["difference_mean_uv"]
