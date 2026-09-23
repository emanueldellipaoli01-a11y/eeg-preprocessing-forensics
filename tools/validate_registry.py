from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "case_id",
    "title",
    "preprocessing_decision",
    "variant_A",
    "variant_B",
    "dataset",
    "task",
    "downstream_measure",
    "primary_metric",
    "code_status",
    "validation_status",
    "evidence_quality",
    "date_added",
}


def main() -> None:
    path = ROOT / "metadata" / "case_registry.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit("Case registry has no header.")
        rows = list(reader)

    if not rows:
        raise SystemExit("Case registry is empty.")

    missing = REQUIRED - set(reader.fieldnames)
    if missing:
        raise SystemExit(f"Case registry missing columns: {sorted(missing)}")

    if any(field is None for field in reader.fieldnames):
        raise SystemExit("Case registry header contains an unexpected empty column name.")

    case_ids = set()
    for row in rows:
        if None in row:
            raise SystemExit(f"Unexpected extra fields in case {row.get('case_id')!r}.")
        for key in REQUIRED:
            if not row[key].strip():
                raise SystemExit(f"Blank required field {key!r} in {row['case_id']!r}.")
        if row["case_id"] in case_ids:
            raise SystemExit(f"Duplicate case_id {row['case_id']!r}.")
        case_ids.add(row["case_id"])
        if row["variant_A"].strip() == row["variant_B"].strip():
            raise SystemExit(f"Variants are identical for {row['case_id']}.")
        try:
            datetime.strptime(row["date_added"].strip(), "%Y-%m-%d")
        except ValueError as exc:
            raise SystemExit(
                f"Invalid date_added for {row['case_id']!r}: {row['date_added']!r}"
            ) from exc

    print(f"Validated {len(rows)} case registry record(s).")


if __name__ == "__main__":
    main()
