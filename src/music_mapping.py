"""Deterministic mapping from normalized skyline profiles to musical notes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

SCALES: dict[str, tuple[int, ...]] = {
    "chromatic": tuple(range(12)),
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "pentatonic": (0, 2, 4, 7, 9),
}


@dataclass(frozen=True)
class NoteEvent:
    """One equal-duration MIDI note."""

    pitch: int
    start: float
    duration: float
    velocity: int = 80

    def __post_init__(self) -> None:
        if not 0 <= self.pitch <= 127:
            raise ValueError("pitch must be between 0 and 127")
        if self.start < 0 or self.duration <= 0:
            raise ValueError("start must be non-negative and duration must be positive")
        if not 1 <= self.velocity <= 127:
            raise ValueError("velocity must be between 1 and 127")


def map_profile_to_midi(
    profile: np.ndarray,
    low_note: int = 48,
    high_note: int = 72,
    scale: str = "pentatonic",
) -> np.ndarray:
    """Map finite normalized values in ``0..1`` to scale-quantized MIDI pitches."""
    values = np.asarray(profile, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("profile must be a non-empty finite one-dimensional array")
    if np.any((values < 0) | (values > 1)):
        raise ValueError("profile values must be between 0 and 1")
    if not isinstance(low_note, (int, np.integer)) or not isinstance(high_note, (int, np.integer)):
        raise TypeError("note bounds must be integers")
    if not 0 <= low_note <= high_note <= 127:
        raise ValueError("note bounds must satisfy 0 <= low_note <= high_note <= 127")
    if scale not in SCALES:
        raise ValueError(f"Unknown scale '{scale}'; choose from {', '.join(SCALES)}")
    candidates = np.array([note for note in range(low_note, high_note + 1) if note % 12 in SCALES[scale]], dtype=int)
    if candidates.size == 0:
        raise ValueError("note range contains no notes from the selected scale")
    indices = np.rint(values * (candidates.size - 1)).astype(int)
    return candidates[indices]


def profile_to_events(
    profile: np.ndarray,
    *,
    low_note: int = 48,
    high_note: int = 72,
    scale: str = "pentatonic",
    duration: float = 0.25,
    velocity: int = 80,
) -> list[NoteEvent]:
    """Create deterministic, equally spaced note events from a normalized profile."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    pitches = map_profile_to_midi(profile, low_note, high_note, scale)
    return [NoteEvent(int(pitch), index * duration, duration, velocity) for index, pitch in enumerate(pitches)]
