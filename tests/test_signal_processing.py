import numpy as np
import pytest

from src.signal_processing import median_filter, moving_average, normalize_min_max


def test_normalize_min_max_maps_signal_to_zero_one() -> None:
    result = normalize_min_max(np.array([2.0, 4.0, 6.0]))
    assert np.allclose(result, [0.0, 0.5, 1.0])


def test_normalize_min_max_rejects_constant_signal() -> None:
    with pytest.raises(ValueError, match="constant"):
        normalize_min_max(np.array([4.0, 4.0]))


def test_moving_average_uses_edge_padding() -> None:
    result = moving_average(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), 3)
    assert np.allclose(result, [4 / 3, 2.0, 3.0, 4.0, 14 / 3])


def test_moving_average_validates_window() -> None:
    with pytest.raises(ValueError, match="odd"):
        moving_average(np.arange(5, dtype=float), 2)


def test_median_filter_removes_isolated_spike_without_mutating_input() -> None:
    signal = np.array([1.0, 1.0, 9.0, 1.0, 1.0])
    result = median_filter(signal, 3)
    assert np.array_equal(result, np.ones(5))
    assert np.array_equal(signal, [1.0, 1.0, 9.0, 1.0, 1.0])
