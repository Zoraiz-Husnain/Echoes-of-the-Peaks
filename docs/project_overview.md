# Mountain to Music — Project Overview

This document explains the project as it exists after Day 2. It is intended as a review and interview guide: it covers what the repository contains, why each stage exists, how the data flows, and where the implementation stops.

## 1. Project goal

Mountain to Music converts the apparent skyline of a mountain range in a static image into a musical sequence.

The current pipeline boundary is intentionally small:

```text
image file
  -> validated RGB NumPy array
  -> HSV colour-space array
  -> boolean foreground/background mask
```

Later stages will extract the skyline profile, process that profile as a spatial signal, map it to notes, and export MIDI.

This project does **not** infer real elevation, geographic depth, distance, or terrain. Image pixels are analysis coordinates, and x-position is currently not a timestamp. The phrase "visible skyline" is important: the output can only describe the boundary visible in the photograph.

## 2. Current repository structure

```text
mountain_music/
├── README.md
├── requirements.txt
├── data/
│   └── sample_images/
├── docs/
│   ├── day_01_repository_and_image_loading.md
│   ├── day_02_hsv_and_segmentation.md
│   └── project_overview.md
├── outputs/
├── src/
│   ├── __init__.py
│   ├── image_io.py
│   └── segmentation.py
└── tests/
    ├── test_image_io.py
    └── test_segmentation.py
```

The planned modules for later stages are described in the project contract, but they should not be created until their stages are requested.

## 3. File responsibilities

### `src/image_io.py`

This module owns reading and validating source images.

`SUPPORTED_EXTENSIONS` contains `.jpg`, `.jpeg`, and `.png`.

`load_image(path)`:

1. Converts the input path to `pathlib.Path`.
2. Checks the lowercase file extension.
3. Checks that the path is an existing file.
4. Decodes it with `cv2.imread(..., cv2.IMREAD_COLOR)`.
5. Rejects failed or empty decodes.
6. Checks for a three-channel colour array.
7. Converts OpenCV's decoded BGR order to RGB.
8. Returns an RGB `uint8` NumPy array.

The function documents and preserves the RGB convention for code above the OpenCV file-loading boundary.

OpenCV ordinarily decodes colour images as BGR, while RGB code and many display libraries store the channels as red, green, and blue. The conversion is explicit so later modules do not accidentally mix conventions.

`describe_image(image)` validates an RGB `(height, width, 3)` array and returns shape, height, width, channel count, dtype, and colour convention.

The command-line `main()` loads and describes one image.

### `src/segmentation.py`

This module owns configurable HSV threshold segmentation.

`HSVThresholds` is an immutable dataclass containing:

- `hue_min` and `hue_max`;
- `saturation_min` and `saturation_max`;
- `value_min` and `value_max`.

The fields use inclusive bounds. Validation ensures integer values and restricts hue to `0..179`, saturation to `0..255`, and value to `0..255`, matching the ranges used by 8-bit OpenCV HSV.

The `lower` and `upper` properties produce NumPy `uint8` HSV boundary arrays for `cv2.inRange`.

`segment_rgb(image, thresholds)`:

1. Checks that `image` is a NumPy array.
2. Checks the `(height, width, 3)` shape.
3. Checks that the dtype is `uint8`.
4. Converts RGB to HSV with `cv2.COLOR_RGB2HSV`.
5. Uses `cv2.inRange` to test every pixel against the inclusive thresholds.
6. Converts the OpenCV result to a boolean array.

The result shape is `(height, width)`. `True` means foreground and `False` means background. This polarity is the project's mask convention and must remain consistent.

The module's CLI can:

- load an RGB image using `load_image`;
- accept separate H/S/V bounds;
- print mask shape and foreground-pixel count;
- optionally save a PNG with white foreground and black background.

It does not add morphology, regions of interest, skyline extraction, filters, UI, or MIDI logic.

### `src/__init__.py`

This marks `src` as a Python package, allowing imports such as `from src.image_io import load_image` and module execution such as `python -m src.segmentation`.

### `tests/test_image_io.py`

This file contains focused tests for Day 1 behavior:

- valid RGB metadata;
- rejection of an array without three colour channels;
- rejection of unsupported file extensions.

It uses synthetic NumPy arrays where image content is not relevant.

### `tests/test_segmentation.py`

This file contains deterministic synthetic segmentation tests:

- a `(H, W, 3)` image produces a boolean `(H, W)` mask;
- green can be selected by a green HSV range;
- `segment_rgb` really applies an RGB-to-HSV conversion;
- invalid hue bounds are rejected;
- floating-point images and two-dimensional arrays are rejected.

No photograph is required for these tests, so they do not depend on downloaded files or subjective visual output.

### `README.md`

The README provides the Windows setup, Day 1 image check, Day 2 segmentation command, test command, repository plan, limitations, and links to detailed records.

### `docs/day_01_repository_and_image_loading.md`

This is the learning record for repository setup and image loading. It explains the original setup, why RGB/BGR distinction matters, array shape and dtype conventions, validation, test coverage, and repository state.

### `docs/day_02_hsv_and_segmentation.md`

This records the current HSV implementation. It explains OpenCV channel ranges, threshold trade-offs, API usage, the mask convention, and exact Windows commands.

## 4. End-to-end data flow

### Image loading

```text
download.jpg
  -> cv2.imread returns BGR uint8
  -> cv2.cvtColor returns RGB uint8
  -> shape (148, 270, 3)
```

The sample image gives the same height and width as the file; loading does not resize it.

### Segmentation

```text
RGB array (H, W, 3)
  -> cv2.cvtColor(..., RGB2HSV)
  -> HSV array (H, W, 3)
  -> cv2.inRange with lower and upper H/S/V bounds
  -> boolean mask (H, W)
```

Example inspection for the repository's sample:

```text
shape: (148, 270)
foreground_pixels: 39778
```

This count is only for the default smoke-test range used during validation. It is not a universal mountain-pixel count.

## 5. NumPy, dtype, and shape concepts

### NumPy array

A NumPy array is the main in-memory representation for image data.

For a colour image:

```text
(height, width, 3)
```

- axis 0 is row, or y-coordinate;
- axis 1 is column, or x-coordinate;
- axis 2 is channel.

For a two-dimensional mask:

```text
(height, width)
```

The third axis disappears because each pixel has one boolean foreground/background value.

### `uint8`

The project expects standard 8-bit pixel values. A `uint8` value is an unsigned 8-bit integer in `0..255`.

OpenCV's HSV representation under this convention is:

```text
H: 0..179
S: 0..255
V: 0..255
```

### Boolean dtype

The final segmentation mask is `dtype=bool`, not `uint8`. Boolean values are `True` and `False`; this is convenient for clear Python logic and expression:

```python
foreground_count = int(mask.sum())
```

For file output, the module converts `True` to `255` and `False` to `0`.

## 6. RGB and HSV concepts

### RGB

RGB describes a colour by its red, green, and blue channel values.

For example:

```text
red   = (255, 0, 0)
green = (0, 255, 0)
blue  = (0, 0, 255)
```

RGB is useful for display, but brightness changes affect all three channels.

### HSV

HSV separates visual information into:

- **Hue:** base colour family;
- **Saturation:** how strong or pure the colour is;
- **Value:** brightness.

Compared with RGB, HSV can make a colour threshold less dependent on brightness.

OpenCV represents hue in a half-circle scale from `0` to `179` because 8-bit storage is more efficient than storing `0..359`.

### Inclusive thresholds

`cv2.inRange` keeps pixels where every channel is inside its configured bounds:

```text
hue_min      <= H <= hue_max
saturation_min <= S <= saturation_max
value_min    <= V <= value_max
```

This means the boundaries are inclusive.

## 7. Foreground convention

The mask convention is explicit:

```text
True / 255 = foreground
False / 0  = background
```

At the current stage, "foreground" means "pixel selected by the colour threshold," not "pixel semantically identified as a mountain." The threshold is a heuristic.

This convention is important for future skyline extraction. Skyline logic should find the smallest row index containing `True` for each column.

## 8. Dataclass and validation concepts

`HSVThresholds` is a frozen dataclass:

- the fields are named, so threshold meaning is visible;
- the dataclass is immutable;
- `__post_init__` validates the values at construction time;
- invalid configurations fail before image processing.

The validation separates configuration errors from NumPy/OpenCV processing errors and makes expected ranges easier to understand.

## 9. Test concepts

The tests are deterministic:

- synthetic arrays do not depend on weather, camera settings, or real photographs;
- exact masks are compared to exact expected arrays;
- output shape and dtype are checked;
- invalid inputs verify that the API rejects unsupported data clearly.

`pytest` discovers test functions beginning with `test_` and asserts expected behavior.

The command used to validate the implementation is:

```powershell
python -m pytest tests\test_segmentation.py tests\test_image_io.py
```

## 10. CLI concepts

Both modules expose `main()` functions guarded by:

```python
if __name__ == "__main__":
    main()
```

This means the file can be imported without immediately running CLI arguments. Running it as a module executes `main()`.

Example:

```powershell
python -m src.segmentation data\sample_images\download.jpg `
    --output outputs\mask.png `
    --hue 0 179 `
    --saturation 0 255 `
    --value 0 180
```

The CLI:

- prints `shape`;
- prints `foreground_pixels`;
- saves the mask only when `--output` is supplied.

Saving foreground as `255` makes the PNG a conventional two-tone grayscale display.

## 11. Trade-offs and limitations

Colour thresholding can select visually similar mountain, sky, haze, cloud, water, or building pixels.

Important trade-offs:

- wider hue/saturation/value bounds increase matches but can add false positives;
- narrower bounds reduce matches but can omit valid mountain pixels;
- low saturation makes hue less informative;
- shadows change value;
- haze and fog change saturation;
- illumination and camera white balance shift HSV values;
- hue wraps near `0/179`, so this dataclass cannot represent a wrapping hue interval directly.
- compression and sensor noise create variations even within an apparently uniform region.

The mask does not include:

- morphology;
- connected-component cleanup;
- ROI constraints;
- skyline extraction;
- missing-column interpolation;
- image smoothing or DSP;
- MIDI mapping;
- MIDI export;
- Streamlit UI.

These omissions are deliberate for the current stage.

## 12. Future pipeline

The next module will consume the boolean mask:

### `skyline.py`

For each image column:

1. find foreground row positions;
2. choose the smallest row as the topmost mountain boundary;
3. return missing values for columns with no foreground pixel;
4. convert image-row coordinates to an upward-positive height convention if desired.

This stage should not interpret a missing column as height zero.

### `signal_processing.py`

The skyline values will be a one-dimensional spatial signal. Later work can interpolate missing values, normalize amplitude, apply smoothing, and analyze profile shape.

The spatial signal is not a waveform at this stage, and spatial frequency must not be presented as audio frequency.

### `music_mapping.py`

Normalized skyline height can later map to MIDI pitch ranges and scales.

### `midi_export.py`

Note events can later be paired and written as valid MIDI files.

### `app.py`

A Streamlit interface may later invoke these modules, display intermediate images and plots, and expose downloads. Processing logic should remain in `src/`, not in the presentation file.

## 13. Windows commands

Setup:

```powershell
cd C:\Users\HP\Desktop\mountain_music
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inspect the source image:

```powershell
python -m src.image_io data\sample_images\download.jpg
```

Inspect and save a mask:

```powershell
python -m src.segmentation data\sample_images\download.jpg `
    --output outputs\mask.png `
    --hue 0 179 `
    --saturation 0 255 `
    --value 0 180
```

Run the focused tests:

```powershell
python -m pytest tests\test_segmentation.py tests\test_image_io.py
```

Run the complete current suite:

```powershell
python -m pytest
```

## 14. Key definitions for explanation

- **RGB:** red/green/blue pixel channels.
- **BGR:** OpenCV's native blue/green/red channel order.
- **HSV:** hue/saturation/value colour representation.
- **Mask:** an image-sized array marking foreground versus background.
- **Foreground:** pixels selected by the configured threshold at this stage.
- **Boolean mask:** mask values are `True` or `False`.
- **Inclusive threshold:** pixels exactly on a lower or upper bound remain selected.
- **Synthetic test:** a small hand-built array used to test deterministic behavior.
- **Segmentation heuristic:** a rule-based boundary between groups of pixels, not a learned semantic model.
- **Skyline:** for each column, the topmost selected foreground row.
- **Spatial signal:** a sequence indexed by image position; not yet an audio waveform.
- **MIDI:** a future note-event export format, not a sound file.
