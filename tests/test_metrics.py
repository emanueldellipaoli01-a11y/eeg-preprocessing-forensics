import mne
import numpy as np

from eeg_forensics.metrics import mean_window_amplitude


def test_mean_window_amplitude():
    info = mne.create_info(["FCz"], sfreq=10.0, ch_types=["eeg"])
    data = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]])
    evoked = mne.EvokedArray(data, info, tmin=-0.2)
    expected = np.mean(evoked.data[0, (evoked.times >= 0.0) & (evoked.times <= 0.2)])
    assert np.isclose(mean_window_amplitude(evoked, "FCz", 0.0, 0.2), expected)
