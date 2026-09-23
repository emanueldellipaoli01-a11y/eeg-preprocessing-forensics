from __future__ import annotations

import numpy as np
from mne.evoked import Evoked


def mean_window_amplitude(evoked: Evoked, channel: str, tmin_s: float, tmax_s: float) -> float:
    """Return mean channel amplitude in the inclusive time window, in SI volts."""
    if not np.isfinite([tmin_s, tmax_s]).all():
        raise ValueError("Metric window bounds must be finite.")
    if tmin_s > tmax_s:
        raise ValueError("Metric window start must be <= metric window end.")
    if channel not in evoked.ch_names:
        raise ValueError(f"Metric channel {channel!r} not found in evoked data.")
    mask = (evoked.times >= tmin_s) & (evoked.times <= tmax_s)
    if not np.any(mask):
        raise ValueError("Requested metric window contains no samples.")
    value = float(np.mean(evoked.data[evoked.ch_names.index(channel), mask]))
    if not np.isfinite(value):
        raise ValueError("Metric result is not finite.")
    return value
