from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_case_001_changes_one_declared_parameter():
    config = yaml.safe_load((ROOT / "cases/case_001_highpass_01_vs_1hz/config.yaml").read_text())
    assert config["variant_a"]["highpass_hz"] == 0.1
    assert config["variant_b"]["highpass_hz"] == 1.0
    assert config["filter"]["lowpass_hz"] == 40.0
    assert config["reference"] == "average"
