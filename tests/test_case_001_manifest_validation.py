import json
from pathlib import Path

from eeg_forensics.validation import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_published_manifest_passes_structural_validation():
    path = ROOT / "cases/case_001_highpass_01_vs_1hz/results/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
