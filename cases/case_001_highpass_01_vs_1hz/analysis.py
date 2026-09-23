"""Run the two Case 001 preprocessing variants and write the results."""

from __future__ import annotations

import json
import platform
import re
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
import yaml

from eeg_forensics.metrics import mean_window_amplitude
from eeg_forensics.provenance import (
    classify_source_verification,
    configuration_hash,
    file_sha256,
    git_commit,
    software_versions,
)
from eeg_forensics.validation import validate_manifest

CASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = CASE_DIR / "config.yaml"


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Case configuration must be a mapping.")
    return config


def _load_raw(subject: int, raw_path: Path | None):
    if raw_path is not None:
        if not raw_path.exists():
            raise FileNotFoundError(raw_path)
        return mne.io.read_raw_fif(raw_path, preload=True, verbose=False), file_sha256(raw_path), "local_file", raw_path
    data_dir = Path(mne.datasets.erp_core.data_path(verbose=False))
    path = data_dir / f"ERP-CORE_Subject-{subject:03d}_Task-Flankers_eeg.fif"
    if not path.is_file():
        raise FileNotFoundError(f"Expected ERP CORE recording was not found: {path}")
    return mne.io.read_raw_fif(path, preload=True, verbose=False), file_sha256(path), "mne_erp_core_fetcher", path


def _incorrect_response_events(raw: mne.io.BaseRaw, cfg: dict) -> np.ndarray:
    epoch_cfg = cfg["epoching"]
    response_pattern = re.compile(epoch_cfg["event_description_regex"])
    if epoch_cfg["response_condition"] != "incorrect":
        raise ValueError(f"Unsupported response_condition: {epoch_cfg['response_condition']!r}")
    events, event_id = mne.events_from_annotations(raw, verbose=False)
    descriptions = {code: name for name, code in event_id.items()}
    stimulus, responses = [], []
    for sample, _, code in events:
        name = descriptions[code]
        if name.startswith("stimulus/") and "/target_" in name:
            stimulus.append((sample, name))
        elif response_pattern.fullmatch(name):
            responses.append((sample, name.rsplit("/", 1)[-1]))
    if not stimulus or not responses:
        raise RuntimeError("Expected ERP CORE stimulus and response annotations were not found.")
    max_latency_samples = int(round(float(epoch_cfg["max_response_latency_s"]) * raw.info["sfreq"]))
    stimulus.sort()
    incorrect = []
    for sample, response_side in responses:
        previous = [item for item in stimulus if item[0] <= sample]
        if not previous:
            continue
        stim_sample, stim_name = previous[-1]
        if sample - stim_sample > max_latency_samples:
            continue
        if response_side != stim_name.rsplit("_", 1)[-1]:
            incorrect.append([sample, 0, 1])
    if not incorrect:
        raise RuntimeError("No incorrect responses could be derived from the annotation stream.")
    return np.asarray(incorrect, dtype=int)


def _preprocess(raw: mne.io.BaseRaw, highpass_hz: float, cfg: dict) -> mne.Epochs:
    lowpass_hz = float(cfg["filter"]["lowpass_hz"])
    if not 0 <= highpass_hz < lowpass_hz:
        raise ValueError("High-pass cutoff must be >= 0 and lower than the low-pass cutoff.")
    work = raw.copy()
    work.filter(l_freq=highpass_hz, h_freq=lowpass_hz, method="fir", phase="zero", verbose=False)
    work.set_eeg_reference(cfg["reference"], projection=False, verbose=False)
    epoch_cfg = cfg["epoching"]
    return mne.Epochs(
        work,
        _incorrect_response_events(work, cfg),
        event_id={"incorrect_response": 1},
        tmin=epoch_cfg["tmin_s"],
        tmax=epoch_cfg["tmax_s"],
        baseline=tuple(cfg["baseline_s"]),
        picks="eeg",
        preload=True,
        reject={"eeg": cfg["rejection_uV"]["eeg"] * 1e-6},
        reject_by_annotation=True,
        verbose=False,
    )


def _subject_result(subject: int, raw_path: Path | None, cfg: dict):
    raw, raw_sha256, source_kind, source_path = _load_raw(subject, raw_path)
    rows, evokeds = [], {}
    for variant, cutoff in [("A", cfg["variant_a"]["highpass_hz"]), ("B", cfg["variant_b"]["highpass_hz"])]:
        epochs = _preprocess(raw, cutoff, cfg)
        channel = cfg["metric"]["channel"]
        if channel not in epochs.ch_names:
            raise RuntimeError(f"Metric channel {channel!r} not found.")
        evoked = epochs.average()
        evokeds[variant] = evoked
        rows.append({"subject": subject, "variant": variant, "highpass_hz": cutoff,
                     "primary_metric_uv": mean_window_amplitude(evoked, channel, cfg["metric"]["tmin_s"], cfg["metric"]["tmax_s"]) * 1e6,
                     "n_epochs": len(epochs)})
    return pd.DataFrame(rows), evokeds, raw_sha256, source_kind, source_path


def _plot_waveforms(evokeds, output: Path, channel: str) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for label, evoked in evokeds.items():
        ax.plot(evoked.times, evoked.data[evoked.ch_names.index(channel)] * 1e6, label=label)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.axhline(0, linewidth=0.8)
    ax.set(xlabel="Time relative to response (s)", ylabel="Amplitude (µV)", title=f"ERP CORE Flankers — {channel}: A vs B")
    ax.legend(title="Variant")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _plot_difference(evokeds, output: Path, channel: str) -> None:
    a, b = evokeds["A"], evokeds["B"]
    idx = a.ch_names.index(channel)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.plot(a.times, (a.data[idx] - b.data[idx]) * 1e6)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.axhline(0, linewidth=0.8)
    ax.set(xlabel="Time relative to response (s)", ylabel="A − B (µV)", title=f"Difference waveform — {channel}")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _plot_subjects(summary: pd.DataFrame, output: Path) -> None:
    pivot = summary.pivot(index="subject", columns="variant", values="primary_metric_uv")
    difference = pivot["A"] - pivot["B"]
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.axhline(0, linewidth=0.8)
    ax.scatter(np.arange(len(difference)), difference.values)
    ax.set(
        xticks=np.arange(len(difference)),
        xticklabels=difference.index,
        xlabel="Subject",
        ylabel="A − B (µV)",
        title="Subject-level primary metric difference",
    )
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def run_case(*, subjects: Iterable[int], raw_path: Path | None, case_dir: Path) -> None:
    cfg = load_config()
    subjects = [int(s) for s in subjects]
    if not subjects or len(set(subjects)) != len(subjects) or any(s < 1 for s in subjects):
        raise ValueError("subjects must be a non-empty collection of unique positive integers.")
    result_dir = case_dir / "results"
    figure_dir = case_dir / "figures"
    result_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    raw_hashes, source_kinds, source_paths, source_verification = {}, {}, {}, {}
    evoked_by_variant = {"A": [], "B": []}
    for subject in subjects:
        if raw_path is not None and len(subjects) > 1:
            raise ValueError("--raw-path supplies one recording; use exactly one subject with a local file.")
        df, evokeds, raw_sha256, source_kind, source_path = _subject_result(subject, raw_path, cfg)
        raw_hashes[subject] = raw_sha256
        source_kinds[subject] = source_kind
        source_paths[subject] = source_path.name
        expected = cfg.get("provenance", {}).get("expected_raw_sha256_by_subject", {}).get(str(subject))
        source_verification[subject] = classify_source_verification(source_kind=source_kind, raw_sha256=raw_sha256, expected_sha256=expected)
        all_rows.append(df)
        for variant, evoked in evokeds.items():
            evoked_by_variant[variant].append(evoked)
    summary = pd.concat(all_rows, ignore_index=True)
    summary.to_csv(result_dir / "summary_long.csv", index=False)
    pivot = summary.pivot(index="subject", columns="variant", values="primary_metric_uv")
    diff = pivot["A"] - pivot["B"]
    verified_source = all(v in {"sha256_match", "official_mne_fetcher"} for v in source_verification.values())
    git_sha = git_commit(CASE_DIR.parents[1])
    manifest = {
        "manifest_schema_version": 1, "case_id": cfg["case_id"], "dataset": "ERP CORE",
        "dataset_version": cfg.get("dataset_version", "v1.1.1"), "raw_file_sha256_by_subject": raw_hashes,
        "raw_source_kind_by_subject": source_kinds, "raw_source_path_by_subject": source_paths,
        "raw_source_verification_by_subject": source_verification, "subjects": sorted(summary["subject"].unique().tolist()),
        "pipeline_a": cfg["variant_a"], "pipeline_b": cfg["variant_b"],
        "primary_metric": "mean FCz amplitude 0–100 ms post-response (uV)",
        "metric_A_mean_uv": float(pivot["A"].mean()), "metric_B_mean_uv": float(pivot["B"].mean()),
        "difference_mean_uv": float(diff.mean()), "difference_sd_uv": float(diff.std(ddof=1)) if len(diff) > 1 else None,
        "n_subjects": int(len(diff)), "n_epochs_by_subject_and_variant": summary[["subject", "variant", "n_epochs"]].to_dict(orient="records"),
        "software_versions": software_versions(), "python_version": sys.version, "platform": platform.platform(),
        "git_commit": git_sha, "configuration_hash": configuration_hash(cfg), "configuration_file_sha256": file_sha256(CONFIG_PATH),
        "random_seed": cfg.get("random_seed"), "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_status": "empirical_executed" if verified_source else "unverified_source",
        "claims": {"observed": verified_source, "generalization": False, "provenance_complete": git_sha is not None},
        "paired_cohens_dz": None,
    }
    validate_manifest(manifest)
    with (result_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    pd.DataFrame({"Aspect": ["High-pass cutoff","Subjects","Mean primary metric (A, µV)","Mean primary metric (B, µV)","Mean A−B (µV)","Paired Cohen dz"],
                  "Variant A": [cfg["variant_a"]["highpass_hz"],"same",manifest["metric_A_mean_uv"],"—",manifest["difference_mean_uv"],None],
                  "Variant B": [cfg["variant_b"]["highpass_hz"],"same","—",manifest["metric_B_mean_uv"],"—","—"]}).to_csv(result_dir / "comparison_table.csv", index=False)
    grand = {v: mne.combine_evoked(es, weights="equal") for v, es in evoked_by_variant.items() if es}
    if grand:
        _plot_waveforms(grand, figure_dir / "erp_variant_a_vs_b.png", cfg["metric"]["channel"])
        _plot_difference(grand, figure_dir / "erp_difference.png", cfg["metric"]["channel"])
        _plot_subjects(summary, figure_dir / "subject_level_difference.png")
    print(summary.to_string(index=False))
    print(f"Wrote results to {result_dir}")
