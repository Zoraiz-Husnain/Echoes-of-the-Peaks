from pathlib import Path

import numpy as np
import pytest

from src.image_io import describe_image, load_image


def test_describe_image_reports_rgb_metadata() -> None:
    image = np.zeros((12, 20, 3), dtype=np.uint8)
    metadata = describe_image(image)
    assert metadata["shape"] == (12, 20, 3)
    assert metadata["colour_convention"] == "RGB"


def test_describe_image_rejects_non_colour_array() -> None:
    with pytest.raises(ValueError, match="Expected RGB shape"):
        describe_image(np.zeros((12, 20), dtype=np.uint8))


def test_load_image_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "image.gif"
    path.write_bytes(b"not an image")
    with pytest.raises(ValueError, match="Unsupported image extension"):
        load_image(path)
