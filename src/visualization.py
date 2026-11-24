"""Optional Matplotlib plots for inspecting each pipeline stage."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise ImportError("plotting requires matplotlib; install requirements.txt") from error
    return plt


def plot_skyline_overlay(image: np.ndarray, skyline_rows: np.ndarray):
    """Return a figure showing skyline rows over an RGB image."""
    plt = _pyplot()
    image_array = np.asarray(image)
    rows = np.asarray(skyline_rows, dtype=float)
    if image_array.ndim != 3 or image_array.shape[2] != 3:
        raise ValueError("image must have shape (height, width, 3)")
    if rows.ndim != 1 or rows.size != image_array.shape[1]:
        raise ValueError("skyline_rows must have one value per image column")
    figure, axis = plt.subplots()
    axis.imshow(image_array)
    axis.plot(np.arange(rows.size), rows, color="red", linewidth=1)
    axis.set(xlabel="image column", ylabel="image row", title="Extracted skyline")
    figure.tight_layout()
    return figure


def plot_profiles(profiles: Iterable[tuple[str, np.ndarray]]):
    """Return a figure comparing named spatial profiles."""
    plt = _pyplot()
    figure, axis = plt.subplots()
    for name, values in profiles:
        signal = np.asarray(values, dtype=float)
        if signal.ndim != 1 or signal.size == 0:
            raise ValueError("profiles must contain non-empty one-dimensional arrays")
        axis.plot(signal, label=name)
    axis.set(xlabel="image column", ylabel="profile value", title="Skyline spatial profiles")
    axis.legend()
    figure.tight_layout()
    return figure
