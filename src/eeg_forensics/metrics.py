from __future__ import annotations

import numpy as np
from mne.evoked import Evoked


def mean_window_amplitude(
    evoked: Evoked,
    channel: str,
    tmin_s: float,
    tmax_s: float,
) -> float:
    """Return mean channel amplitude in the inclusive time window, in SI volts."""
    idx = evoked.ch_names.index(channel)
    mask = (evoked.times >= tmin_s) & (evoked.times <= tmax_s)
    if not np.any(mask):
        raise ValueError("Requested metric window contains no samples.")
    return float(np.mean(evoked.data[idx, mask]))
