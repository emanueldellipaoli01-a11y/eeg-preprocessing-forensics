"""Execute Case 001: high-pass 0.1 Hz vs 1 Hz."""

from __future__ import annotations

import argparse
from pathlib import Path

from cases.case_001_highpass_01_vs_1hz.analysis import load_config, run_case

CASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", nargs="+", type=int, default=None)
    parser.add_argument("--raw-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=CASE_DIR)
    args = parser.parse_args()
    cfg = load_config()
    subjects = args.subjects if args.subjects is not None else cfg["subjects"]
    run_case(subjects=subjects, raw_path=args.raw_path, case_dir=args.output_dir)


if __name__ == "__main__":
    main()
