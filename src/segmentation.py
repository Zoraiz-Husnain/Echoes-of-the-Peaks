"""Configurable HSV threshold segmentation for RGB images."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class HSVThresholds:
    """Inclusive OpenCV HSV bounds for foreground pixels."""

    hue_min: int = 0
    hue_max: int = 179
    saturation_min: int = 0
    saturation_max: int = 255
    value_min: int = 0
    value_max: int = 255

    def __post_init__(self) -> None:
        bounds = (self.hue_min, self.hue_max, self.saturation_min, self.saturation_max, self.value_min, self.value_max)
        if not all(isinstance(value, (int, np.integer)) for value in bounds):
            raise TypeError("HSV thresholds must be integers")
        if not 0 <= self.hue_min <= self.hue_max <= 179:
            raise ValueError("Hue bounds must satisfy 0 <= hue_min <= hue_max <= 179")
        if not 0 <= self.saturation_min <= self.saturation_max <= 255:
            raise ValueError("Saturation bounds must be between 0 and 255")
        if not 0 <= self.value_min <= self.value_max <= 255:
            raise ValueError("Value bounds must be between 0 and 255")

    @property
    def lower(self) -> np.ndarray:
        return np.array([self.hue_min, self.saturation_min, self.value_min], dtype=np.uint8)

    @property
    def upper(self) -> np.ndarray:
        return np.array([self.hue_max, self.saturation_max, self.value_max], dtype=np.uint8)


def segment_rgb(image: np.ndarray, thresholds: HSVThresholds) -> np.ndarray:
    """Return a same-height/width boolean mask; True means foreground."""
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a NumPy array")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected RGB shape (height, width, 3), got {image.shape}")
    if image.dtype != np.uint8:
        raise ValueError("image must have dtype uint8")
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    return cv2.inRange(hsv, thresholds.lower, thresholds.upper).astype(bool)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and inspect an HSV foreground mask.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, help="Optional path for a PNG mask (foreground=255).")
    parser.add_argument("--hue", nargs=2, type=int, metavar=("MIN", "MAX"), default=(0, 179))
    parser.add_argument("--saturation", nargs=2, type=int, metavar=("MIN", "MAX"), default=(0, 255))
    parser.add_argument("--value", nargs=2, type=int, metavar=("MIN", "MAX"), default=(0, 255))
    args = parser.parse_args()
    from src.image_io import load_image

    thresholds = HSVThresholds(args.hue[0], args.hue[1], args.saturation[0], args.saturation[1], args.value[0], args.value[1])
    mask = segment_rgb(load_image(args.image), thresholds)
    print(f"shape: {mask.shape}")
    print(f"foreground_pixels: {int(mask.sum())}")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(args.output), mask.astype(np.uint8) * 255):
            raise OSError(f"Could not save mask: {args.output}")


if __name__ == "__main__":
    main()
