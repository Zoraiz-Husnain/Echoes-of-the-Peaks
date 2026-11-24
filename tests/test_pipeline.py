import numpy as np

from src.pipeline import run_pipeline
from src.segmentation import HSVThresholds


def test_run_pipeline_returns_aligned_profiles_and_deterministic_notes() -> None:
    image = np.zeros((8, 7, 3), dtype=np.uint8)
    image[:4, :, 0] = 255
    image[:3, 1, 0] = 0
    image[:2, 4, 0] = 0
    result = run_pipeline(
        image,
        HSVThresholds(hue_min=0, hue_max=179, saturation_min=200, value_min=200),
        filter_name="none",
        low_note=48,
        high_note=60,
        scale="major",
    )
    assert result.mask.shape == (8, 7)
    assert result.raw_profile.shape == (7,)
    assert result.processed_profile.shape == (7,)
    assert result.normalized_profile.shape == (7,)
    assert len(result.events) == 7
    assert np.array_equal(result.pitches, result.pitches)
    assert np.all((result.pitches >= 48) & (result.pitches <= 60))
    assert np.array_equal(result.pitches, run_pipeline(
        image,
        HSVThresholds(hue_min=0, hue_max=179, saturation_min=200, value_min=200),
        filter_name="none", low_note=48, high_note=60, scale="major",
    ).pitches)


def test_run_pipeline_rejects_unknown_filter() -> None:
    image = np.full((3, 3, 3), 255, dtype=np.uint8)
    with np.testing.assert_raises_regex(ValueError, "filter_name"):
        run_pipeline(image, HSVThresholds(), filter_name="wavelet")
