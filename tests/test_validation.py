from eeg_forensics.validation import validate_manifest


def test_manifest_validation():
    manifest = {
        "case_id": "case_001",
        "dataset": "synthetic",
        "pipeline_a": {"highpass_hz": 0.1},
        "pipeline_b": {"highpass_hz": 1.0},
        "primary_metric": "mean amplitude",
        "n_subjects": 1,
        "software_versions": {"python": "3"},
        "configuration_hash": "abc",
        "execution_status": "smoke_test",
        "timestamp_utc": "2026-09-05T00:00:00+00:00",
        "claims": {"observed": True},
    }
    validate_manifest(manifest)


def test_unverified_source_cannot_claim_observed():
    manifest = {
        "case_id": "case_001",
        "dataset": "ERP CORE",
        "pipeline_a": {"highpass_hz": 0.1},
        "pipeline_b": {"highpass_hz": 1.0},
        "primary_metric": "mean amplitude",
        "n_subjects": 1,
        "software_versions": {"python": "3"},
        "configuration_hash": "abc",
        "execution_status": "unverified_source",
        "timestamp_utc": "2026-09-05T00:00:00+00:00",
        "claims": {"observed": True},
    }
    import pytest

    with pytest.raises(ValueError, match="unverified_source"):
        validate_manifest(manifest)


def test_local_file_source_cannot_be_empirical():
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
