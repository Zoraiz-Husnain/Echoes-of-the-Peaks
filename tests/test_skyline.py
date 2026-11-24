import numpy as np
import pytest

from src.skyline import extract_skyline, interpolate_missing, skyline_height


def test_extract_skyline_returns_topmost_row_and_nan_for_empty_column() -> None:
    mask = np.array([[False, False, False], [True, False, False], [True, False, True]], dtype=bool)
    rows = extract_skyline(mask)
    assert np.array_equal(rows[[0, 2]], [1.0, 2.0])
    assert np.isnan(rows[1])


def test_extract_skyline_filters_short_vertical_runs() -> None:
    mask = np.zeros((8, 3), dtype=bool)
    mask[1, 0] = True
    mask[2:6, 1] = True
    mask[0:2, 2] = True
    rows = extract_skyline(mask, min_run_length=3)
    assert np.isnan(rows[0])
    assert rows[1] == 2
    assert np.isnan(rows[2])


def test_extract_skyline_rejects_invalid_run_length() -> None:
    with pytest.raises(ValueError, match="min_run_length"):
        extract_skyline(np.ones((3, 2), dtype=bool), min_run_length=0)


def test_extract_skyline_rejects_all_empty_mask() -> None:
    with pytest.raises(ValueError, match="no foreground"):
        extract_skyline(np.zeros((3, 2), dtype=bool))


def test_skyline_height_is_upward_positive() -> None:
    rows = np.array([0.0, 2.0, np.nan])
    heights = skyline_height(rows, image_height=4)
    assert np.array_equal(heights[:2], [3.0, 1.0])
    assert np.isnan(heights[2])


@pytest.mark.parametrize("invalid_row", [np.inf, -np.inf])
def test_skyline_height_rejects_infinite_rows(invalid_row: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        skyline_height(np.array([1.0, invalid_row]), image_height=4)


def test_interpolate_missing_does_not_mutate_and_handles_edges() -> None:
    profile = np.array([np.nan, 2.0, np.nan, 6.0, np.nan])
    result = interpolate_missing(profile)
    assert np.array_equal(result, [2.0, 2.0, 4.0, 6.0, 6.0])
    assert np.isnan(profile[0])
