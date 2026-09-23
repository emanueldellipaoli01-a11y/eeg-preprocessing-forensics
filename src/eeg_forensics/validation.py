from __future__ import annotations

import re
from datetime import datetime
from math import isfinite

VALID_EXECUTION_STATUSES = {"empirical_executed", "unverified_source", "not_executed", "smoke_test"}
VALID_SOURCE_VERIFICATIONS = {"sha256_match", "official_mne_fetcher", "unverified_local_file"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _number(value: object, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError(f"{field} must be a finite number.")
    return float(value)


def validate_manifest(manifest: dict) -> None:
    required = {
        "case_id", "dataset", "pipeline_a", "pipeline_b", "primary_metric",
        "n_subjects", "software_versions", "configuration_hash",
        "execution_status", "claims", "timestamp_utc",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError(f"Manifest is missing required fields: {missing}")
    if not isinstance(manifest["n_subjects"], int) or isinstance(manifest["n_subjects"], bool):
        raise ValueError("n_subjects must be an integer.")
    if manifest["n_subjects"] < 1:
        raise ValueError("Manifest must report at least one subject.")
    if not isinstance(manifest["pipeline_a"], dict) or not isinstance(manifest["pipeline_b"], dict):
        raise ValueError("pipeline_a and pipeline_b must be mappings.")
    if manifest["pipeline_a"] == manifest["pipeline_b"]:
        raise ValueError("pipeline_a and pipeline_b must differ.")
    if not isinstance(manifest["software_versions"], dict) or not manifest["software_versions"]:
        raise ValueError("software_versions must be a non-empty mapping.")
    if not isinstance(manifest["configuration_hash"], str) or not _SHA256_RE.fullmatch(
        manifest["configuration_hash"].lower()
    ):
        raise ValueError("configuration_hash must be a 64-character SHA-256 hex digest.")
    if manifest["execution_status"] not in VALID_EXECUTION_STATUSES:
        raise ValueError("Unknown execution status.")
    if not isinstance(manifest["claims"], dict):
        raise ValueError("claims must be a mapping.")
    if not isinstance(manifest["claims"].get("observed"), bool):
        raise ValueError("claims.observed must be a boolean.")
    observed = manifest["claims"]["observed"]
    if manifest["execution_status"] == "empirical_executed" and not observed:
        raise ValueError("empirical_executed requires claims.observed=true.")
    if manifest["execution_status"] == "unverified_source" and observed:
        raise ValueError("unverified_source requires claims.observed=false.")
    try:
        datetime.fromisoformat(manifest["timestamp_utc"])
    except (TypeError, ValueError) as exc:
        raise ValueError("timestamp_utc must be a valid ISO-8601 timestamp.") from exc

    subjects = manifest.get("subjects")
    if subjects is not None:
        if not isinstance(subjects, list) or len(subjects) != manifest["n_subjects"]:
            raise ValueError("subjects must contain exactly n_subjects entries.")
        if any(not isinstance(s, int) or isinstance(s, bool) or s < 1 for s in subjects):
            raise ValueError("subjects must contain positive integer subject identifiers.")
        if len(set(subjects)) != len(subjects):
            raise ValueError("subjects must be unique.")

    for field in (
        "raw_file_sha256_by_subject", "raw_source_kind_by_subject",
        "raw_source_path_by_subject", "raw_source_verification_by_subject",
    ):
        mapping = manifest.get(field)
        if mapping is not None:
            if not isinstance(mapping, dict):
                raise ValueError(f"{field} must be a mapping.")
            if subjects is not None and set(mapping) != {str(s) for s in subjects}:
                raise ValueError(f"{field} keys must match subjects.")

    source_verification = manifest.get("raw_source_verification_by_subject")
    if source_verification is not None:
        if any(v not in VALID_SOURCE_VERIFICATIONS for v in source_verification.values()):
            raise ValueError("Unknown raw source verification value.")
        if manifest["execution_status"] == "empirical_executed" and any(
            v == "unverified_local_file" for v in source_verification.values()
        ):
            raise ValueError("empirical_executed cannot contain unverified local sources.")

    records = manifest.get("n_epochs_by_subject_and_variant")
    if records is not None:
        if not isinstance(records, list):
            raise ValueError("n_epochs_by_subject_and_variant must be a list.")
        expected = {(int(s), v) for s in subjects or [] for v in ("A", "B")}
        actual = set()
        for record in records:
            if not isinstance(record, dict) or {"subject", "variant", "n_epochs"} - set(record):
                raise ValueError("Each epoch record must contain subject, variant, and n_epochs.")
            s, v, n = record["subject"], record["variant"], record["n_epochs"]
            if not isinstance(s, int) or isinstance(s, bool) or s < 1:
                raise ValueError("Epoch records must use positive integer subject identifiers.")
            if v not in {"A", "B"}:
                raise ValueError("Epoch records must use variant A or B.")
            if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                raise ValueError("n_epochs must be a non-negative integer.")
            pair = (s, v)
            if pair in actual:
                raise ValueError("Duplicate subject/variant epoch record.")
            actual.add(pair)
        if subjects is not None and actual != expected:
            raise ValueError("Epoch records must contain exactly one A and B record per subject.")

    metric_fields = {"metric_A_mean_uv", "metric_B_mean_uv", "difference_mean_uv"}
    if metric_fields <= manifest.keys():
        a = _number(manifest["metric_A_mean_uv"], "metric_A_mean_uv")
        b = _number(manifest["metric_B_mean_uv"], "metric_B_mean_uv")
        d = _number(manifest["difference_mean_uv"], "difference_mean_uv")
        if abs((a - b) - d) > 1e-9:
            raise ValueError("difference_mean_uv must equal metric_A_mean_uv - metric_B_mean_uv.")

    if manifest.get("difference_sd_uv") is not None:
        if _number(manifest["difference_sd_uv"], "difference_sd_uv") < 0:
            raise ValueError("difference_sd_uv cannot be negative.")

    if manifest.get("paired_cohens_dz") is not None:
        dz = _number(manifest["paired_cohens_dz"], "paired_cohens_dz")
        sd = manifest.get("difference_sd_uv")
        if sd in (None, 0):
            raise ValueError("paired_cohens_dz requires a positive difference_sd_uv.")
        expected_dz = float(manifest["difference_mean_uv"]) / float(sd)
        if abs(dz - expected_dz) > 1e-9:
            raise ValueError("paired_cohens_dz is inconsistent with the reported mean and SD.")

    complete = manifest["claims"].get("provenance_complete")
    if complete is not None and not isinstance(complete, bool):
        raise ValueError("claims.provenance_complete must be a boolean when present.")
    if complete:
        commit = manifest.get("git_commit")
        config_sha = manifest.get("configuration_file_sha256")
        if not isinstance(commit, str) or not _GIT_SHA_RE.fullmatch(commit.lower()):
            raise ValueError("Complete provenance requires a 40-character git_commit.")
        if not isinstance(config_sha, str) or not _SHA256_RE.fullmatch(config_sha.lower()):
            raise ValueError("Complete provenance requires configuration_file_sha256.")
