import pytest

from eeg_forensics.validation import validate_manifest


def _manifest(**overrides):
    manifest = {
        "case_id": "case_001",
        "dataset": "synthetic",
        "pipeline_a": {"highpass_hz": 0.1},
        "pipeline_b": {"highpass_hz": 1.0},
        "primary_metric": "mean amplitude",
        "n_subjects": 1,
        "subjects": [1],
        "software_versions": {"python": "3"},
        "configuration_hash": "0" * 64,
        "execution_status": "smoke_test",
        "timestamp_utc": "2026-09-05T00:00:00+00:00",
        "claims": {"observed": True},
        "metric_A_mean_uv": 2.5,
        "metric_B_mean_uv": 1.5,
        "difference_mean_uv": 1.0,
        "difference_sd_uv": None,
        "paired_cohens_dz": None,
        "n_epochs_by_subject_and_variant": [
            {"subject": 1, "variant": "A", "n_epochs": 10},
            {"subject": 1, "variant": "B", "n_epochs": 11},
        ],
    }
    manifest.update(overrides)
    return manifest


def test_manifest_validation():
    validate_manifest(_manifest())


def test_unverified_source_cannot_claim_observed():
    with pytest.raises(ValueError, match="unverified_source"):
        validate_manifest(_manifest(execution_status="unverified_source", claims={"observed": True}))


def test_local_file_source_is_unverified_without_matching_hash():
    from eeg_forensics.provenance import classify_source_verification

    assert classify_source_verification(
        source_kind="local_file", raw_sha256="abc", expected_sha256=None
    ) == "unverified_local_file"
    assert classify_source_verification(
        source_kind="local_file", raw_sha256="ABC", expected_sha256="abc"
    ) == "sha256_match"


def test_mne_fetcher_is_explicitly_verified_source():
    from eeg_forensics.provenance import classify_source_verification

    assert classify_source_verification(
        source_kind="mne_erp_core_fetcher", raw_sha256="abc", expected_sha256=None
    ) == "official_mne_fetcher"


def test_manifest_rejects_inconsistent_difference():
    with pytest.raises(ValueError, match="difference_mean_uv"):
        validate_manifest(_manifest(difference_mean_uv=0.5))


def test_manifest_requires_complete_provenance_when_declared():
    with pytest.raises(ValueError, match="git_commit"):
        validate_manifest(
            _manifest(
                claims={"observed": True, "provenance_complete": True},
                git_commit=None,
                configuration_file_sha256="0" * 64,
            )
        )
