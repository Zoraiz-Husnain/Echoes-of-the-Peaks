import cv2
import numpy as np
import pytest

from src.segmentation import HSVThresholds, segment_rgb


def test_segment_rgb_returns_aligned_boolean_foreground_mask() -> None:
    image = np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]], dtype=np.uint8)
    mask = segment_rgb(image, HSVThresholds(hue_min=55, hue_max=65, saturation_min=200))
    assert mask.shape == image.shape[:2]
    assert mask.dtype == np.bool_
    assert mask.tolist() == [[False, True], [False, False]]


def test_segment_rgb_uses_rgb_to_hsv_boundary() -> None:
    image = np.array([[[255, 0, 0]]], dtype=np.uint8)
    red_hue = int(cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[0, 0, 0])
    assert segment_rgb(image, HSVThresholds(red_hue, red_hue, 200, 255, 200, 255)).item()


def test_thresholds_reject_invalid_bounds() -> None:
    with pytest.raises(ValueError, match="Hue bounds"):
        HSVThresholds(hue_min=180)


def test_segment_rgb_rejects_wrong_dtype_and_shape() -> None:
    with pytest.raises(ValueError, match="dtype uint8"):
        segment_rgb(np.zeros((2, 2, 3), dtype=np.float32), HSVThresholds())
    with pytest.raises(ValueError, match="Expected RGB shape"):
        segment_rgb(np.zeros((2, 2), dtype=np.uint8), HSVThresholds())
