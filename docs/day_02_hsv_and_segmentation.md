# Day 2 — HSV and first segmentation

## Goal

Day 2 adds a small, reusable HSV threshold stage. It accepts the RGB `uint8` arrays returned by `src.image_io.load_image`, converts them to OpenCV HSV at the module boundary, and returns a two-dimensional boolean mask aligned with the input. `True` always means foreground (the pixels inside the configured inclusive HSV range); `False` means background. The CLI writes that convention as white foreground and black background.

## HSV and OpenCV ranges

OpenCV represents 8-bit HSV as hue `0..179`, saturation `0..255`, and value `0..255`. Hue describes colour family, saturation describes colour intensity, and value describes brightness. Compared with RGB thresholds, HSV can separate a colour family from brightness more directly: for example, a sky or haze range can be constrained by saturation/value while hue remains relatively stable.

This is deliberately a heuristic, not semantic segmentation. Similar colours in clouds, trees, buildings, or haze can be selected, and shadows, exposure, season, and camera white balance can shift pixels outside the range. Hue is circular, so a range crossing red's `0/179` boundary is not represented by one interval in this first version; use two masks and combine them in a later change if needed. No morphology, ROI, skyline extraction, UI, or downstream music processing is included.

## API

`HSVThresholds` is a frozen dataclass with explicit inclusive `hue_min`, `hue_max`, `saturation_min`, `saturation_max`, `value_min`, and `value_max` fields. Bounds are validated against OpenCV's ranges. `segment_rgb(image, thresholds)` validates an RGB `(H, W, 3)` `uint8` array, performs `cv2.COLOR_RGB2HSV`, and returns a boolean `(H, W)` mask.

## Exact Windows PowerShell commands

From the repository root:

```powershell
cd C:\Users\HP\Desktop\mountain_music
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.image_io data\sample_images\download.jpg
python -m src.segmentation data\sample_images\download.jpg --output outputs\mask.png --hue 0 179 --saturation 0 255 --value 0 180
python -m pytest tests\test_segmentation.py
```

The `--output` argument is optional; without it the CLI only inspects and prints the mask shape and foreground count. Adjust the three ranges for the image, keeping hue within `0..179` and saturation/value within `0..255`.

## Tests

`tests/test_segmentation.py` uses deterministic synthetic RGB arrays to verify shape alignment, boolean dtype, foreground polarity, RGB-to-HSV conversion, and invalid-bound rejecti
