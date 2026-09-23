import mne
import numpy as np
import pytest
import yaml

from cases.case_001_highpass_01_vs_1hz.analysis import _incorrect_response_events, _preprocess


@pytest.fixture
def case_config():
    with open("cases/case_001_highpass_01_vs_1hz/config.yaml", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _annotated_raw():
    sfreq = 100.0
    times = np.arange(0.0, 8.0, 1.0 / sfreq)
    data = np.zeros((2, times.size))
    data[0] = 2e-6 * np.sin(2 * np.pi * 0.5 * times)
    info = mne.create_info(["FCz", "Cz"], sfreq=sfreq, ch_types=["eeg", "eeg"])
    raw = mne.io.RawArray(data, info, verbose=False)
    raw.set_annotations(
        mne.Annotations(
            onset=[1.0, 1.5, 3.0, 3.6, 6.0, 6.5],
            duration=[0.0] * 6,
            description=[
                "stimulus/block/target_left",
                "response/right",
                "stimulus/block/target_right",
                "response/right",
                "stimulus/block/target_left",
                "response/right",
            ],
        )
    )
    return raw


def test_incorrect_response_events_are_config_driven(case_config):
    events = _incorrect_response_events(_annotated_raw(), case_config)
    assert events[:, 0].tolist() == [150, 650]
    assert events[:, 2].tolist() == [1, 1]


def test_response_condition_is_not_ignored(case_config):
    cfg = dict(case_config)
    cfg["epoching"] = dict(case_config["epoching"])
    cfg["epoching"]["response_condition"] = "correct"
    with pytest.raises(ValueError, match="response_condition"):
        _incorrect_response_events(_annotated_raw(), cfg)


def test_case_preprocess_uses_events_and_rejects_bad_cutoff(case_config):
    raw = _annotated_raw()
    cfg = dict(case_config)
    cfg["filter"] = {"lowpass_hz": 20.0, "method": "fir_zero_phase"}
    epochs = _preprocess(raw, 2.0, cfg)
    assert len(epochs) == 2
    assert set(epochs.events[:, 0]) == {150, 650}
    with pytest.raises(ValueError, match="High-pass cutoff"):
        _preprocess(raw, 25.0, cfg)
