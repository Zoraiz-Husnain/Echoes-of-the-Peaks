import cv2
import numpy as np
import pytest

from src.segmentation import HSVThresholds, rgb_to_hsv, segment_foreground


def test_segment_foreground_returns_aligned_boolean_mask() -> None:
    image = np.array([[[20, 20, 20], [240, 240, 240]]], dtype=np.uint8)
    mask = segment_foreground(image, HSVThresholds((0, 0, 0), (179, 255, 100)))
    assert mask.shape == image.shape[:2]
    assert mask.dtype == np.bool_
    assert mask.tolist() == [[True, False]]


def test_rgb_to_hsv_uses_rgb_boundary() -> None:
    image = np.array([[[255, 0, 0]]], dtype=np.uint8)
    assert rgb_to_hsv(image).tolist() == [[[0, 255, 255]]]


def test_thresholds_reject_invalid_opencv_bounds() -> None:
    with pytest.raises(ValueError, match="H<=179"):
        HSVThresholds((0, 0, 0), (180, 255, 255))