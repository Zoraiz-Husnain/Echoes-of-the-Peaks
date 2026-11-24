import numpy as np
import pytest

from src.music_mapping import NoteEvent, map_profile_to_midi, profile_to_events


def test_mapping_is_deterministic_and_uses_requested_range() -> None:
    profile = np.array([0.0, 0.5, 1.0])
    first = map_profile_to_midi(profile, 48, 60, "major")
    assert np.array_equal(first, [48, 55, 60])
    assert np.array_equal(first, map_profile_to_midi(profile, 48, 60, "major"))


def test_events_have_positive_duration_and_valid_pitches() -> None:
    events = profile_to_events(np.array([0.0, 1.0]), low_note=60, high_note=72, duration=0.5)
    assert events == [NoteEvent(60, 0.0, 0.5), NoteEvent(72, 0.5, 0.5)]


def test_mapping_validates_profile_and_scale() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        map_profile_to_midi(np.array([-0.1]))
    with pytest.raises(ValueError, match="Unknown scale"):
        map_profile_to_midi(np.array([0.5]), scale="unknown")
