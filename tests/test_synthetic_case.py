import mne
import numpy as np

from eeg_forensics.metrics import mean_window_amplitude


def test_highpass_smoke_changes_known_slow_component():
    sfreq = 100.0
    times = np.arange(0, 40, 1 / sfreq)
    rng = np.random.default_rng(7)
    signal = 8e-6 * np.sin(2 * np.pi * 0.25 * times)
    signal += 5e-6 * np.exp(-0.5 * ((times - 1.2) / 0.08) ** 2)
    signal += rng.normal(0, 0.5e-6, size=times.size)
    info = mne.create_info(["FCz"], sfreq=sfreq, ch_types=["eeg"])
    raw = mne.io.RawArray(signal[np.newaxis, :], info)
    a = raw.copy().filter(0.1, 40, method="fir", phase="zero", verbose=False)
    b = raw.copy().filter(1.0, 40, method="fir", phase="zero", verbose=False)
    ev_a = mne.EvokedArray(a.get_data(), info, tmin=0.0)
    ev_b = mne.EvokedArray(b.get_data(), info, tmin=0.0)
    assert np.isfinite(mean_window_amplitude(ev_a, "FCz", 1.0, 1.5))
    assert np.isfinite(mean_window_amplitude(ev_b, "FCz", 1.0, 1.5))
    assert not np.allclose(a.get_data(), b.get_data())
