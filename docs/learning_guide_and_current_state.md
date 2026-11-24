# Mountain to Music: current state and learning guide

## Purpose and honest scope

Mountain to Music converts a visible boundary in an image into a one-dimensional spatial profile and then into a deterministic musical contour. It does **not** infer real elevation, depth, distance, or terrain. A pixel row is an image coordinate, not a measurement of a mountain's physical height.

The current implementation is a pre-audio pipeline:

```text
image file or upload
  -> RGB image array
  -> HSV threshold mask
  -> one skyline row per image column
  -> upward-positive spatial height
  -> missing-value interpolation
  -> optional spatial smoothing
  -> min-max normalization
  -> scale-quantized MIDI pitch values
  -> equal-duration note events
  -> plots and Streamlit UI
```

The project currently creates note events and visual contours. It does not synthesize playable audio or export a MIDI file yet.

## Repository map

- [`src/image_io.py`](../src/image_io.py): image loading, OpenCV BGR-to-RGB conversion, shape validation, metadata.
- [`src/segmentation.py`](../src/segmentation.py): RGB-to-HSV conversion and inclusive HSV threshold masking.
- [`src/skyline.py`](../src/skyline.py): per-column skyline extraction, vertical-run filtering, row-to-height conversion, interpolation.
- [`src/signal_processing.py`](../src/signal_processing.py): min-max normalization, edge-padded moving average, edge-padded median filter.
- [`src/pipeline.py`](../src/pipeline.py): pure orchestration and `PipelineResult`.
- [`src/music_mapping.py`](../src/music_mapping.py): normalized profile to scale-constrained MIDI pitches and note events.
- [`src/visualization.py`](../src/visualization.py): reusable Matplotlib figures.
- [`app.py`](../app.py): Streamlit upload interface and visualization layer.
- [`tests/`](../tests): deterministic unit and pipeline tests.
- [`README.md`](../README.md): setup and run commands.
- [`docs/project_overview.md`](project_overview.md): broader project explanation.

## Running the project

From the repository root in PowerShell:

```powershell
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Upload a JPG, JPEG, or PNG. Adjust HSV controls, minimum vertical edge run, spatial filter, scale, MIDI range, and note duration. The interface shows the source image, segmentation mask, detected skyline overlay, spatial profile, note contour, and note table.

For tests:

```powershell
python -m pytest
```

## Concept 1: arrays, coordinates, and image conventions

An image loaded by OpenCV is a NumPy array with shape `(height, width, channels)`. The first index is the row (`y`), the second is the column (`x`), and the final index selects colour channels. Row zero is the top of the image; larger row numbers move downward.

The project standardizes images to RGB in [`src/image_io.py`](../src/image_io.py), because OpenCV normally decodes as BGR. The conversion is:

```python
cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
```

Learn:

- NumPy shape, dtype, slicing, boolean masks, and broadcasting.
- Difference between image coordinates `(column, row)` and array indexing `[row, column]`.
- `uint8` colour channels and the range `0..255`.
- Why displaying an RGB array as BGR produces incorrect colours.

Debugging questions:

- Is the array shape `(H, W, 3)`?
- Is the display RGB or BGR?
- Is the skyline plotted with `x = column` and `y = row`?

## Concept 2: colour spaces and HSV threshold segmentation

[`src/segmentation.py`](../src/segmentation.py) converts RGB to OpenCV HSV:

```python
hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
```

Then it uses `cv2.inRange` to select pixels between inclusive lower and upper bounds. The result is converted to a boolean mask where `True` means foreground.

HSV components:

- **Hue**: approximate colour family. In OpenCV's 8-bit HSV, hue is `0..179`, not `0..360`.
- **Saturation**: colour intensity. Low saturation is grey/white/cloud-like and can make hue unstable.
- **Value**: brightness. Sunset gradients and cloud highlights can overlap the brightness range of buildings.

The current mask is a **colour classifier**, not an edge detector and not semantic segmentation. A broad interval may classify sky, clouds, buildings, and foreground simultaneously. A threshold does not understand that buildings should be connected, low in the image, or part of one skyline.

The defaults in [`HSVThresholds`](../src/segmentation.py) are intentionally broad API defaults. They can select almost every pixel and produce a skyline at the top row. In the UI, tune the ranges while inspecting the mask and foreground coverage.

Learn:

- HSV versus RGB and why HSV can be easier for colour selection.
- Hue wrap-around near red (`0`/`179`).
- Threshold inclusivity and quantization.
- Illumination, saturation, shadows, and sunset/cloud colour overlap.
- Why one global colour threshold often fails on natural images.

## Concept 3: the mask is the main source of false skyline detections

The skyline extractor cannot recover information that the mask got wrong. If a cloud pixel is `True`, the extractor sees it as foreground. If a building pixel is `False`, no later stage can recreate it.

Always inspect the mask before changing skyline logic. In the UI, white pixels are selected foreground. For a good mask:

- the building/foreground region should be a coherent shape;
- open sky should be mostly black;
- clouds should not form white islands above the true skyline;
- the building tops should remain connected across columns where they are visible.

Useful measurements:

- foreground coverage: `mask.mean()`;
- number of true pixels per column: `mask.sum(axis=0)`;
- first true row per column;
- connected components and component areas;
- fraction of columns with no foreground.

## Concept 4: per-column skyline extraction

[`src/skyline.py`](../src/skyline.py) creates one output value per image column. For each column it finds foreground rows with:

```python
foreground_rows = np.flatnonzero(mask[:, column])
```

The old/simple rule chooses the smallest row, because that is the uppermost selected pixel. This is appropriate only when the foreground mask contains the intended silhouette and little noise.

The current implementation additionally accepts `min_run_length`. It splits the selected row indices into contiguous vertical runs and accepts the first run whose length is large enough. This rejects isolated or short foreground fragments such as cloud noise. The pipeline passes this option from [`src/pipeline.py`](../src/pipeline.py), and the UI exposes it as “Minimum vertical edge run”.

Important limitation: vertical-run filtering is a heuristic. A thin building edge may be rejected, while a tall cloud fragment may still pass. Also, real buildings can be separated by gaps, and clouds can form long vertical regions. The next improvement may need connected-component filtering, a lower-region prior, morphology, gradient-based edges, or an explicit foreground/background model.

Learn:

- `np.flatnonzero`, `np.diff`, contiguous runs, and NaN arrays.
- Silhouette extraction and coordinate geometry.
- Why “topmost selected pixel” is not the same as “true object boundary”.
- Connected components, morphology, and region-of-interest constraints.

## Concept 5: missing columns and interpolation

If a column has no accepted foreground run, the skyline value is `NaN`. [`interpolate_missing`](../src/skyline.py) uses `np.interp` to fill gaps:

- interior gaps are linearly interpolated;
- leading and trailing gaps are extended from the nearest valid value;
- all-missing profiles are rejected.

Interpolation creates estimates, not observations. A long missing region can materially change the final contour. The UI should eventually show observed and interpolated points separately and report the missing percentage.

Learn:

- missing data versus zero values;
- linear interpolation and edge extrapolation;
- why a filled profile can look plausible while being wrong;
- uncertainty and confidence in a computer-vision pipeline.

## Concept 6: image rows versus upward-positive height

[`skyline_height`](../src/skyline.py) converts a row coordinate into an upward-positive value:

```python
(image_height - 1) - rows
```

A smaller image row means a visually higher point, so it becomes a larger height. This is a coordinate transformation only. It does not imply physical elevation.

Learn:

- coordinate-system transformations;
- image y-axis direction versus graph y-axis direction;
- off-by-one behavior from `height - 1`;
- preserving NaN while rejecting infinities and out-of-range rows.

## Concept 7: spatial DSP

[`src/signal_processing.py`](../src/signal_processing.py) treats the skyline height as a one-dimensional spatial signal indexed by image column.

### Min-max normalization

`normalize_min_max` maps the minimum to `0` and maximum to `1`:

```python
(signal - minimum) / (maximum - minimum)
```

It rejects missing, non-finite, empty, and constant signals. This is not audio normalization; it is rescaling image-derived geometry.

### Moving average

`moving_average` pads both edges using the nearest value and computes a centered mean. It reduces small fluctuations but can blur peaks and shift the visual character of narrow structures.

### Median filter

`median_filter` replaces each point with the median in a centered edge-padded window. It is often better for isolated spikes because a single extreme point does not dominate the median.

The filters happen **after** skyline selection. They cannot determine whether a selected point came from a building or cloud. Filtering can smooth a bad boundary but cannot reliably correct a wrong mask.

Learn:

- convolution and sliding windows;
- mean versus median robustness;
- edge padding and boundary effects;
- noise, outliers, smoothing, and signal distortion;
- why spatial DSP is different from audio DSP.

## Concept 8: mapping profiles to notes

[`src/music_mapping.py`](../src/music_mapping.py) creates candidate MIDI notes in a configured range and keeps only notes whose pitch class belongs to the selected scale. Normalized profile values choose positions in that candidate list.

Supported scales include chromatic, major, minor, and pentatonic. `NoteEvent` validates pitch, start time, duration, and velocity. [`profile_to_events`](../src/music_mapping.py) gives each profile sample an equal duration.

This is a deterministic representation, not sound synthesis. Image columns are treated as event order, while note duration supplies a musical timeline.

Learn:

- MIDI pitch numbers and pitch classes modulo 12;
- scales and quantization;
- interpolation from `[0, 1]` to a discrete candidate set;
- event timing, duration, velocity;
- why many adjacent columns may create too many notes and why later downsampling/phrase extraction may be needed.

## Concept 9: visualization and UI architecture

[`src/visualization.py`](../src/visualization.py) provides reusable Matplotlib figures. [`app.py`](../app.py) adds a Streamlit interface, decodes uploads with Pillow, applies upload size/pixel limits, calls the pure pipeline, and displays:

- source image;
- detected mask;
- skyline overlay;
- spatial profile;
- note contour;
- event table.

The UI catches expected `ValueError` and `TypeError` exceptions and presents them as user-facing errors. It does not currently expose a true audio waveform because no audio synthesis module exists.

Learn:

- separation of pure computation from UI orchestration;
- Streamlit rerun model and widget state;
- Matplotlib axes, legends, labels, and coordinate overlays;
- resource limits and safe upload handling;
- accessibility, clear labels, and honest visual interpretation.

## Why the current edge detector fails on a city/sunset image

For the reported image, the likely causal chain is:

1. A broad HSV interval selects some cloud/sunset pixels on the left.
2. `extract_skyline` sees those selected pixels above the buildings.
3. The topmost accepted pixel in each affected column becomes the skyline row.
4. `interpolate_missing` and optional smoothing make the result continuous, but they do not know that the cloud points were false.
5. The overlay therefore jumps upward into open sky.

The right side works better because building silhouettes have stronger, more coherent regions that survive thresholding. This is an empirical hypothesis to verify by inspecting the mask; the mask is the decisive artifact.

## A disciplined debugging workflow for the edge issue

### Step 1: freeze the input and settings

Use the exact image and record its dimensions, color convention, threshold values, filter, window, and minimum run length. Do not change multiple controls at once.

### Step 2: inspect the mask first

If false white pixels exist in the left sky, fix segmentation before skyline extraction. Try:

- increase saturation minimum to reject low-saturation clouds;
- narrow value bounds to exclude bright sunset/cloud regions;
- choose a hue interval matching the foreground rather than the sky;
- display HSV channel histograms or sample pixel values from sky and buildings.

If the mask is clean but the line is wrong, continue to skyline logic.

### Step 3: inspect per-column evidence

For selected columns, print or plot:

```python
rows = np.flatnonzero(mask[:, x])
print(x, rows[:20], rows[-20:])
```

Compare a false-positive column on the left with a correct building column on the right. Ask whether the false run is isolated, short, connected, or repeated.

### Step 4: test vertical-run filtering

Try `min_run_length` values of `1`, `2`, `3`, `5`, and `8`. If false points disappear while buildings remain, the issue is small vertical components. If clouds still pass, use connected components or a spatial prior.

### Step 5: add a region-of-interest prior carefully

If the foreground is known to occupy the lower part of the image, reject candidate runs above a minimum row or search from the bottom upward. This is powerful for city skylines but must be configurable because a mountain can occupy much of the frame.

### Step 6: compare segmentation with gradient edges

Colour segmentation and gradient edge detection answer different questions:

- HSV thresholding finds pixels with selected colours.
- Sobel/Canny finds intensity boundaries.

Cloud gradients can create Canny edges too, so gradient detection alone is not a solution. A robust method may combine a colour/foreground mask with gradients and geometric continuity.

### Step 7: validate with synthetic masks

Create masks with known silhouettes and known noise:

- a stepped building skyline;
- isolated true pixels in the sky;
- short cloud runs;
- missing columns;
- narrow buildings.

Tests should assert that the recovered rows match the intended boundary and that filtering does not remove legitimate structures.

## Next computer-vision concepts to learn

1. **Connected-component analysis**: label white regions and remove small components by area, bounding box, or location. Relevant future code: `cv2.connectedComponentsWithStats`.
2. **Morphological operations**: opening removes small isolated foreground noise; closing fills small gaps. Learn structuring elements and how kernel size changes silhouettes.
3. **Region of interest and priors**: restrict candidate skyline to plausible image rows, but expose assumptions clearly.
4. **Canny/Sobel gradients**: understand derivative filters, hysteresis thresholds, non-maximum suppression, and why clouds create edges.
5. **Adaptive thresholding and color models**: local thresholds, clustering, Gaussian mixture models, and supervised segmentation.
6. **Graph/continuity optimization**: choose one row per column by minimizing an energy that rewards image evidence and penalizes implausible jumps. Dynamic programming or seam carving ideas are relevant.
7. **Robust curve fitting**: median filters, RANSAC, splines, and outlier rejection.
8. **Evaluation metrics**: manually labelled skyline ground truth, pixel row error, mean absolute error, percentage of columns within tolerance, and false-positive rate above the true skyline.
9. **Data visualization for debugging**: mask overlays, per-column counts, candidate rows, confidence scores, and synchronized plots.

## Suggested mastery sequence

### Phase A: Python and arrays

Master NumPy indexing, dtype, boolean masks, `np.flatnonzero`, `np.diff`, `np.interp`, NaN handling, and Matplotlib plotting. Trace one tiny synthetic image by hand through every array.

### Phase B: image processing

Learn RGB/BGR, HSV, threshold masks, connected components, morphology, and Canny/Sobel. For each technique, visualize both its output and its failure cases.

### Phase C: signal processing

Learn normalization, moving averages, medians, convolution, padding, sampling, outliers, and frequency-domain intuition. Keep remembering that the current signal axis is image column, not time.

### Phase D: software engineering

Learn typed boundaries, dataclasses, pure functions, deterministic tests, fixtures, CLI/UI separation, error handling, dependency management, and regression testing. The current implementations and tests in [`tests/`](../tests) are concrete examples.

### Phase E: music and audio

Learn MIDI pitch/scale theory first, then sampling rate, frequency in Hz, sine waves, envelopes, additive synthesis, aliasing, normalization, WAV output, and MIDI file structure. Implement audio only after the image-derived contour is trustworthy.

## Practical checklist for the next coding day

- [ ] Save the exact problematic image locally without committing it.
- [ ] Record image shape and RGB/BGR convention.
- [ ] Capture the exact HSV controls.
- [ ] Display the binary mask at full resolution.
- [ ] Measure mask coverage by left, middle, and right thirds.
- [ ] Compare `np.flatnonzero(mask[:, x])` for false and correct columns.
- [ ] Try `min_run_length` values systematically.
- [ ] Add a regression test using a synthetic noisy mask.
- [ ] Decide whether the next fix belongs in segmentation, morphology, connected components, ROI logic, or skyline continuity.
- [ ] Only then change production code.

## Current limitations to remember

- HSV thresholds are global and hand-tuned.
- The mask has no semantic understanding of “building” versus “cloud”.
- Vertical-run filtering is a heuristic, not a complete skyline detector.
- Interpolation can conceal missing evidence.
- Smoothing can hide errors rather than fix them.
- There is no confidence score or ground-truth evaluation yet.
- There is no audio synthesis or MIDI export yet.

This is the correct foundation for learning the project: every stage is explicit, testable, and inspectable. The edge problem is not mysterious; it is a measurable mismatch between the intended foreground and the segmentation mask, followed by a per-column selection rule that trusts the first accepted pixel.
