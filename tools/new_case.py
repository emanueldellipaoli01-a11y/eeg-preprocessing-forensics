from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")

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

CONFIG = """case_id: {case_id}\ntitle: {title}\nstatus: planned\nvariant_a: {{}}\nvariant_b: {{}}\n"""

RUN = '''if __name__ == "__main__":
    raise SystemExit("Implement the case before execution.")
'''

ANALYSIS = '"""Case-specific analysis."""\n'


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    if not slug:
        raise ValueError("title must contain at least one alphanumeric character")
    return slug


def create_case(case_id: str, title: str, root: Path = ROOT) -> Path:
    if not CASE_ID_RE.fullmatch(case_id):
        raise ValueError("case_id must contain only letters, numbers, underscores, and hyphens")
    if not title.strip():
        raise ValueError("title must not be blank")
    case_dir = root / "cases" / f"{case_id}_{_slugify(title)}"
    case_dir.mkdir(parents=True, exist_ok=False)
    (case_dir / "figures").mkdir()
    (case_dir / "results").mkdir()
    (case_dir / "README.md").write_text(README.format(title=title), encoding="utf-8")
    (case_dir / "config.yaml").write_text(CONFIG.format(case_id=case_id, title=title), encoding="utf-8")
    (case_dir / "run.py").write_text(RUN, encoding="utf-8")
    (case_dir / "analysis.py").write_text(ANALYSIS, encoding="utf-8")
    (case_dir / "references.md").write_text("# References\n", encoding="utf-8")
    return case_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    print(create_case(args.id, args.title))


if __name__ == "__main__":
    main()
