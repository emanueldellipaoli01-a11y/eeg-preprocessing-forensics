VALID_EXECUTION_STATUSES = {
    "empirical_executed",
    "unverified_source",
    "not_executed",
    "smoke_test",
}


def validate_manifest(manifest: dict) -> None:
    required = {
        "case_id",
        "dataset",
        "pipeline_a",
        "pipeline_b",
        "primary_metric",
        "n_subjects",
        "software_versions",
        "configuration_hash",
        "execution_status",
        "claims",
        "timestamp_utc",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError(f"Manifest is missing required fields: {missing}")
    if manifest["n_subjects"] < 1:
        raise ValueError("Manifest must report at least one subject.")
    if manifest["execution_status"] not in VALID_EXECUTION_STATUSES:
        raise ValueError("Unknown execution status.")
    if not isinstance(manifest["claims"], dict):
        raise ValueError("claims must be a mapping.")
    observed = bool(manifest["claims"].get("observed", False))
    if manifest["execution_status"] == "empirical_executed" and not observed:
        raise ValueError("empirical_executed requires claims.observed=true.")
    if manifest["execution_status"] == "unverified_source" and observed:
        raise ValueError("unverified_source requires claims.observed=false.")
