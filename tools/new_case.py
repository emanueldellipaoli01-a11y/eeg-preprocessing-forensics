from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

README = """# {title}

## Question

## Data

## Pipelines

## Analysis

## Results

## Limitations

## Reproduction

## References
"""

CONFIG = """case_id: {case_id}\ntitle: {title}\nstatus: planned\nvariant_a: {{}}\nvariant_b: {{}}\n"

RUN = '''if __name__ == "__main__":
    raise SystemExit("Implement the case before execution.")
'''

ANALYSIS = '"""Case-specific analysis."""\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    case_dir = ROOT / "cases" / f"{args.id}_{args.title.lower().replace(' ', '_').replace('/', '_')}"
    case_dir.mkdir(parents=True, exist_ok=False)
    (case_dir / "figures").mkdir()
    (case_dir / "results").mkdir()
    (case_dir / "README.md").write_text(README.format(title=args.title), encoding="utf-8")
    (case_dir / "config.yaml").write_text(CONFIG.format(case_id=args.id, title=args.title), encoding="utf-8")
    (case_dir / "run.py").write_text(RUN, encoding="utf-8")
    (case_dir / "analysis.py").write_text(ANALYSIS, encoding="utf-8")
    (case_dir / "references.md").write_text("# References\n", encoding="utf-8")
    print(case_dir)


if __name__ == "__main__":
    main()
