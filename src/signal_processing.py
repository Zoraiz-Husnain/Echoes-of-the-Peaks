"""Deterministic processing helpers for one-dimensional skyline signals."""

from __future__ import annotations

import numpy as np


def normalize_min_max(values: np.ndarray) -> np.ndarray:
    """Normalize a finite, non-constant profile to the inclusive range 0..1."""
    signal = _as_signal(values)
    if not np.isfinite(signal).all():
        raise ValueError("values must not contain missing or non-finite values")
    minimum = float(signal.min())
    maximum = float(signal.max())
    if np.isclose(minimum, maximum):
        raise ValueError("Cannot normalize a constant signal")
    return (signal - minimum) / (maximum - minimum)


def moving_average(values: np.ndarray, window_size: int) -> np.ndarray:
    """Return a centered moving average with edge padding."""
    signal = _as_signal(values)
    if not np.isfinite(signal).all():
        raise ValueError("values must not contain missing or non-finite values")
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("window_size must be a positive odd integer")
    if window_size > signal.size:
        raise ValueError("window_size cannot exceed signal length")
    padding = window_size // 2
    padded = np.pad(signal, padding, mode="edge")
    return np.convolve(padded, np.ones(window_size) / window_size, mode="valid")


def median_filter(values: np.ndarray, window_size: int) -> np.ndarray:
    """Return a centered median filter using edge padding."""
    signal = _as_signal(values)
    if not np.isfinite(signal).all():
        raise ValueError("values must not contain missing or non-finite values")
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("window_size must be a positive odd integer")
    if window_size > signal.size:
        raise ValueError("window_size cannot exceed signal length")
    padding = window_size // 2
    padded = np.pad(signal, padding, mode="edge")
    return np.array([np.median(padded[index:index + window_size]) for index in range(signal.size)])


def _as_signal(values: np.ndarray) -> np.ndarray:
    signal = np.asarray(values, dtype=np.float64)
    if signal.ndim != 1 or signal.size == 0:
        raise ValueError("values must be a non-empty one-dimensional array")
    return signal
