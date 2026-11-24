"""Extract a visible skyline from a boolean foreground mask."""

from __future__ import annotations

import numpy as np


def extract_skyline(mask: np.ndarray, *, min_run_length: int = 1) -> np.ndarray:
    """Return the topmost foreground row per column, using NaN for empty columns.

    A foreground pixel is accepted only when it belongs to a vertical run of at
    least ``min_run_length`` pixels. This filters isolated sky/cloud noise while
    preserving continuous building silhouettes.
    """
    _validate_mask(mask)
    if not isinstance(min_run_length, (int, np.integer)) or min_run_length < 1:
        raise ValueError("min_run_length must be a positive integer")
    height, width = mask.shape
    rows = np.full(width, np.nan, dtype=np.float64)
    for column in range(width):
        foreground_rows = np.flatnonzero(mask[:, column])
        if foreground_rows.size:
            starts = np.r_[0, np.flatnonzero(np.diff(foreground_rows) > 1) + 1]
            ends = np.r_[starts[1:] - 1, foreground_rows.size - 1]
            run_lengths = foreground_rows[ends] - foreground_rows[starts] + 1
            valid_runs = np.flatnonzero(run_lengths >= min_run_length)
            if valid_runs.size:
                rows[column] = float(foreground_rows[starts[valid_runs[0]]])
    if np.isnan(rows).all():
        raise ValueError("Mask contains no foreground pixels")
    return rows


def skyline_height(skyline_rows: np.ndarray, image_height: int) -> np.ndarray:
    """Convert image rows to upward-positive heights, preserving NaN values."""
    if image_height <= 0:
        raise ValueError("image_height must be positive")
    rows = np.asarray(skyline_rows, dtype=np.float64)
    if rows.ndim != 1:
        raise ValueError("skyline_rows must be one-dimensional")
    invalid = np.isinf(rows) | (rows < 0) | (rows >= image_height)
    if np.any(invalid):
        raise ValueError("skyline rows must be finite or NaN and within the image height")
    return (image_height - 1) - rows


def interpolate_missing(values: np.ndarray) -> np.ndarray:
    """Linearly interpolate interior and edge NaNs without mutating input."""
    profile = np.asarray(values, dtype=np.float64)
    if profile.ndim != 1 or profile.size == 0:
        raise ValueError("values must be a non-empty one-dimensional array")
    valid = np.flatnonzero(np.isfinite(profile))
    if valid.size == 0:
        raise ValueError("Cannot interpolate an all-missing profile")
    result = profile.copy()
    missing = ~np.isfinite(result)
    result[missing] = np.interp(np.flatnonzero(missing), valid, result[valid])
    return result


def _validate_mask(mask: np.ndarray) -> None:
    if not isinstance(mask, np.ndarray) or mask.ndim != 2 or mask.dtype != np.bool_:
        raise ValueError("mask must be a two-dimensional boolean array")
    if mask.shape[0] == 0 or mask.shape[1] == 0:
        raise ValueError("mask dimensions must be positive")
