import ast
from pathlib import Path

import pytest
import yaml

from tools.new_case import create_case


def test_new_case_scaffold_is_valid(tmp_path: Path):
    case_dir = create_case("case_002", "Reference / Interpolation", tmp_path)
    assert case_dir == tmp_path / "cases" / "case_002_reference_interpolation"
    assert (case_dir / "figures").is_dir()
    assert (case_dir / "results").is_dir()
    config = yaml.safe_load((case_dir / "config.yaml").read_text(encoding="utf-8"))
    assert config["case_id"] == "case_002"
    assert config["title"] == "Reference / Interpolation"
    ast.parse((case_dir / "run.py").read_text(encoding="utf-8"))
    ast.parse((case_dir / "analysis.py").read_text(encoding="utf-8"))


def test_new_case_rejects_unsafe_case_id(tmp_path: Path):
    with pytest.raises(ValueError, match="case_id"):
        create_case("../escape", "A case", tmp_path)
