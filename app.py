"""Local Streamlit UI for Mountain to Music."""

from __future__ import annotations

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UPLOAD_PIXELS = 16_000_000
from PIL import Image

from src.image_io import describe_image
from src.pipeline import PipelineResult, run_pipeline
from src.segmentation import HSVThresholds


st.set_page_config(page_title="Mountain to Music", page_icon="⛰️", layout="wide")


def _uploaded_rgb(uploaded_file) -> np.ndarray:
    """Decode and size-limit an uploaded file into RGB uint8 convention."""
    payload = uploaded_file.getvalue()
    if len(payload) > MAX_UPLOAD_BYTES:
        raise ValueError("The image is too large; please upload a file smaller than 10 MB.")
    try:
        with Image.open(BytesIO(payload)) as decoded:
            width, height = decoded.size
            if width <= 0 or height <= 0 or width * height > MAX_UPLOAD_PIXELS:
                raise ValueError("The image dimensions are too large to process safely.")
            image = np.asarray(decoded.convert("RGB"), dtype=np.uint8)
    except ValueError:
        raise
    except Exception as error:
        raise ValueError("The upload could not be decoded as a colour image.") from error
    describe_image(image)
    return image


def _overlay_figure(image: np.ndarray, rows: np.ndarray):
    figure, axis = plt.subplots(figsize=(10, 4))
    axis.imshow(image)
    axis.plot(np.arange(rows.size), rows, color="#ff5572", linewidth=1.5)
    axis.set(title="Detected skyline edge", xlabel="image column", ylabel="image row")
    figure.tight_layout()
    return figure


def _profiles_figure(result: PipelineResult):
    figure, axis = plt.subplots(figsize=(10, 3.5))
    axis.plot(result.raw_profile, label="raw / interpolated", color="#8da2c8", alpha=0.8)
    axis.plot(result.processed_profile, label=result.filter_name, color="#ffb454", linewidth=2)
    axis.set(title="Skyline profile (image-space height)", xlabel="image column", ylabel="height")
    axis.legend(frameon=False)
    figure.tight_layout()
    return figure


def _notes_figure(result: PipelineResult):
    figure, axis = plt.subplots(figsize=(10, 2.8))
    starts = [event.start for event in result.events]
    axis.step(starts, result.pitches, where="post", color="#78e0c0", linewidth=1.5)
    axis.scatter(starts, result.pitches, color="#f5f1e8", s=10)
    axis.set(title="Generated note contour", xlabel="event position (seconds)", ylabel="MIDI pitch")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    return figure


def main() -> None:
    st.markdown("# ⛰️ Mountain to Music")
    st.caption("Turn an apparent image-space skyline into a deterministic musical contour.")
    st.info("This is a colour-threshold heuristic. The extracted profile describes apparent skyline geometry in image coordinates, not real elevation or terrain.")

    with st.sidebar:
        st.header("Controls")
        uploaded = st.file_uploader("Upload a JPG, JPEG, or PNG", type=["jpg", "jpeg", "png"])
        st.subheader("Segmentation")
        hue = st.slider("Hue", 0, 179, (0, 179))
        saturation = st.slider("Saturation", 0, 255, (0, 255))
        value = st.slider("Value", 0, 255, (0, 180))
        min_run_length = st.slider(
            "Minimum vertical edge run",
            1,
            12,
            3,
            help="Ignore isolated foreground pixels shorter than this. Building edges usually form longer vertical runs than cloud noise.",
        )
        st.subheader("DSP")
        filter_name = st.selectbox("Profile filter", ["moving average", "median", "none"])
        window_size = st.slider("Odd filter window", 1, 31, 5, step=2, disabled=filter_name == "none")
        st.subheader("Notes")
        scale = st.selectbox("Scale", ["pentatonic", "major", "minor", "chromatic"])
        low_note, high_note = st.slider("MIDI range", 0, 127, (48, 72))
        duration = st.slider("Seconds per note", 0.05, 1.0, 0.25, 0.05)

    if uploaded is None:
        st.markdown("### Start with a landscape image")
        st.write("Choose an image in the sidebar. The three panels below will show the source, detected edge, and generated spatial wave.")
        return
    try:
        image = _uploaded_rgb(uploaded)
        thresholds = HSVThresholds(hue[0], hue[1], saturation[0], saturation[1], value[0], value[1])
        result = run_pipeline(
            image,
            thresholds,
            filter_name=filter_name,
            window_size=window_size,
            low_note=low_note,
            high_note=high_note,
            scale=scale,
            duration=duration,
            min_run_length=min_run_length,
        )
    except (ValueError, TypeError) as error:
        st.error(f"Pipeline could not run: {error}")
        return

    metadata = describe_image(image)
    first, second = st.columns(2)
    with first:
        st.subheader("Source image")
        st.image(image, use_container_width=True)
        st.caption(f"{metadata['width']} × {metadata['height']} px")
    with second:
        st.subheader("Detected edge")
        st.pyplot(_overlay_figure(image, result.skyline_rows), clear_figure=True)
        st.caption(f"Foreground mask coverage: {result.mask.mean():.1%}")

    st.subheader("Segmentation mask")
    st.image(result.mask.astype(np.uint8) * 255, clamp=True, caption="White pixels are selected foreground; black pixels are background.")

    st.subheader("Generated spatial waves and notes")
    st.pyplot(_profiles_figure(result), clear_figure=True)
    st.pyplot(_notes_figure(result), clear_figure=True)
    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("Columns / notes", len(result.events))
    metric_two.metric("Filter", result.filter_name)
    metric_three.metric("Pitch span", f"{result.pitches.min()}–{result.pitches.max()}")
    st.caption("The profile plot is a spatial wave across image columns; it is not an audio waveform.")
    st.dataframe({"event": range(len(result.events)), "MIDI pitch": result.pitches}, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
