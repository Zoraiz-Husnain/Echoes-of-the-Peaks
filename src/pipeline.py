"""Pure orchestration for the image-to-skyline-to-notes pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.music_mapping import NoteEvent, profile_to_events
from src.segmentation import HSVThresholds, segment_rgb
from src.signal_processing import median_filter, moving_average, normalize_min_max
from src.skyline import extract_skyline, interpolate_missing, skyline_height


@dataclass(frozen=True)
class PipelineResult:
    """All inspectable outputs from one deterministic pipeline run."""

    mask: np.ndarray
    skyline_rows: np.ndarray
    raw_profile: np.ndarray
    processed_profile: np.ndarray
    normalized_profile: np.ndarray
    pitches: np.ndarray
    events: tuple[NoteEvent, ...]
    filter_name: str
    window_size: int


def run_pipeline(
    image: np.ndarray,
    thresholds: HSVThresholds,
    *,
    filter_name: str = "moving average",
    window_size: int = 5,
    low_note: int = 48,
    high_note: int = 72,
    scale: str = "pentatonic",
    duration: float = 0.25,
    min_run_length: int = 1,
) -> PipelineResult:
    """Run segmentation, skyline extraction, DSP, and note mapping.

    The profile remains a spatial signal indexed by image columns; it is not an
    audio waveform and image x-position is not interpreted as elapsed time.
    """
    if filter_name not in {"none", "moving average", "median"}:
        raise ValueError("filter_name must be 'none', 'moving average', or 'median'")
    mask = segment_rgb(image, thresholds)
    rows = extract_skyline(mask, min_run_length=min_run_length)
    raw_profile = interpolate_missing(skyline_height(rows, image.shape[0]))
    if filter_name == "none":
        processed = raw_profile.copy()
    elif filter_name == "moving average":
        processed = moving_average(raw_profile, window_size)
    else:
        processed = median_filter(raw_profile, window_size)
    normalized = normalize_min_max(processed)
    events = tuple(profile_to_events(normalized, low_note=low_note, high_note=high_note, scale=scale, duration=duration))
    pitches = np.array([event.pitch for event in events], dtype=int)
    return PipelineResult(mask, rows, raw_profile, processed, normalized, pitches, events, filter_name, window_size)
