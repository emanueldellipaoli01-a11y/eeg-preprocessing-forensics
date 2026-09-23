from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from typing import Any


def configuration_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def software_versions() -> dict[str, str]:
    versions = {"python": sys.version.split()[0]}
    for name in ["mne", "numpy", "scipy", "pandas", "matplotlib", "yaml"]:
        try:
            module = importlib.import_module(name)
            versions[name] = getattr(module, "__version__", "unknown")
        except ImportError:
            versions[name] = "not-installed"
    return versions


def classify_source_verification(*, source_kind: str, raw_sha256: str, expected_sha256: str | None) -> str:
    if expected_sha256 and expected_sha256.lower() == raw_sha256.lower():
        return "sha256_match"
    if source_kind == "mne_erp_core_fetcher":
        return "official_mne_fetcher"
    return "unverified_local_file"
