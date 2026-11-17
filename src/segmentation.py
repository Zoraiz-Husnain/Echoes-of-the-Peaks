"""Day 2 HSV threshold segmentation utilities."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.image_io import load_image


@dataclass(frozen=True)
class HSVThresholds:
    """Inclusive OpenCV HSV bounds for pixels considered foreground."""

    lower: tuple[int, int, int] = (0, 0, 0)
    upper: tuple[int, int, int] = (179, 255, 255)

    def __post_init__(self) -> None:
        if len(self.lower) != 3 or len(self.upper) != 3:
            raise ValueError("HSV bounds must contain exactly three values")
        if any(value < 0 for value in self.lower) or any(value < 0 for value in self.upper):
            raise ValueError("HSV bounds cannot contain negative values")
        if any(lower > upper for lower, upper in zip(self.lower, self.upper)):
            raise ValueError("Each lower HSV bound must be <= its upper bound")
        if self.upper[0] > 179 or self.upper[1] > 255 or self.upper[2] > 255:
            raise ValueError("OpenCV HSV bounds are H<=179 and S/V<=255")


def rgb_to_hsv(image: np.ndarray) -> np.ndarray:
    """Convert an RGB image shaped (height, width, 3) to OpenCV HSV."""
    if not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected an RGB image with shape (height, width, 3)")
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)


def segment_foreground(image: np.ndarray, thresholds: HSVThresholds) -> np.ndarray:
    """Return a boolean foreground mask aligned to the input image.

    True means the pixel's HSV values are inside the configured inclusive bounds.
    No morphology or semantic interpretation is applied.
    """
    hsv_image = rgb_to_hsv(image)
    lower = np.asarray(thresholds.lower, dtype=np.uint8)
    upper = np.asarray(thresholds.upper, dtype=np.uint8)
    return cv2.inRange(hsv_image, lower, upper).astype(bool)


def save_mask(mask: np.ndarray, path: str | Path) -> None:
    """Save a boolean mask as a black/white PNG (True foreground = white)."""
    if mask.ndim != 2 or mask.dtype != np.bool_:
        raise ValueError("mask must be a two-dimensional boolean array")
    if not cv2.imwrite(str(path), mask.astype(np.uint8) * 255):
        raise OSError(f"Could not save mask: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an HSV threshold foreground mask.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs") / "mask.png")
    parser.add_argument("--lower", nargs=3, type=int, default=(0, 0, 0), metavar=("H", "S", "V"))
    parser.add_argument("--upper", nargs=3, type=int, default=(179, 255, 255), metavar=("H", "S", "V"))
    args = parser.parse_args()
    mask = segment_foreground(load_image(args.image), HSVThresholds(tuple(args.lower), tuple(args.upper)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_mask(mask, args.output)
    print(f"mask_shape: {mask.shape}")
    print(f"foreground_pixels: {int(mask.sum())}")
    print(f"output: {args.output}")


if __name__ == "__main__":
    main()
