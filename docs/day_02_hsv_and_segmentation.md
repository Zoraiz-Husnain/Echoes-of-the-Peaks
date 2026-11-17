# Day 2 — HSV and first segmentation

## What the failed command was about

The Day 1 command only prints metadata; it does not open a window. The path must be relative to the repository (or absolute), and Windows PowerShell uses backslashes. The saved image is `data\sample_images\download.jpg`, so from `C:\Users\HP\Desktop\mountain_music` run:

```powershell
python -m src.image_io data\sample_images\download.jpg
```

It reports the verified image as `(148, 270, 3)`, `uint8`, RGB. If Python is not available in a fresh terminal, activate the documented virtual environment first, or use `\.venv\Scripts\python.exe` directly.

## Implementation

`src/segmentation.py` keeps segmentation separate from image loading. `load_image` returns RGB, and `rgb_to_hsv` explicitly converts RGB to OpenCV HSV at the segmentation boundary.

`HSVThresholds` exposes inclusive lower and upper bounds. OpenCV uses H in `0..179` and S/V in `0..255`. `segment_foreground` returns a two-dimensional boolean mask with shape `(height, width)`; `True` means that the pixel is inside the configured HSV range and is therefore treated as foreground. This is a colour-threshold heuristic, not semantic segmentation or machine learning.

The CLI writes a black-and-white PNG where white is foreground:

```powershell
python -m src.segmentation data\sample_images\download.jpg --lower 0 0 0 --upper 179 255 150 --output outputs\download_mask.png
```

## HSV trade-offs

- **Hue** represents the base colour, but its meaning is weak when saturation is low.
- **Saturation** measures colour intensity. Restricting it can reject grey haze, but may also reject low-saturation mountain faces.
- **Value** measures brightness. A value ceiling can select darker terrain, but shadows and dark trees may become false positives.
- Wider bounds usually increase recall and false positives; narrower bounds usually reduce false positives and miss more real mountain pixels.

The first mask should be inspected visually and thresholds adjusted for the particular photograph. No morphology, ROI, skyline extraction, DSP, MIDI, or Streamlit features are included in Day 2.

## Tests

Focused deterministic tests cover RGB-to-HSV conversion, mask shape and dtype, foreground polarity, and invalid bounds. Run all current tests with:

```powershell
python -m pytest
```
