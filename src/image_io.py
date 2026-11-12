"""Day 1 image loading and validation utilities."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def load_image(path: str | Path) -> np.ndarray:
    """Load a supported image as RGB with shape (height, width, 3)."""
    image_path = Path(path)
    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported image extension '{image_path.suffix}'. Use: {supported}")
    if not image_path.is_file():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    bgr_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if bgr_image is None or bgr_image.size == 0:
        raise ValueError(f"Could not decode a non-empty image: {image_path}")
    if bgr_image.ndim != 3 or bgr_image.shape[2] != 3:
        raise ValueError(f"Expected a colour image with shape (height, width, 3), got {bgr_image.shape}")

    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)


def describe_image(image: np.ndarray) -> dict[str, object]:
    """Return validated metadata for an RGB image array."""
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a NumPy array")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected RGB shape (height, width, 3), got {image.shape}")
    height, width, channels = image.shape
    if height <= 0 or width <= 0:
        raise ValueError("Image dimensions must be positive")
    return {
        "shape": image.shape,
        "height": height,
        "width": width,
        "channels": channels,
        "dtype": str(image.dtype),
        "colour_convention": "RGB",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and describe an input image.")
    parser.add_argument("image", type=Path, help="Path to a JPG, JPEG, or PNG image")
    args = parser.parse_args()
    metadata = describe_image(load_image(args.image))
    for key, value in metadata.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
