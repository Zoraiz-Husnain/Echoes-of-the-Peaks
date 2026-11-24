# Days 3 and 4 — From a Mask to a Skyline Signal

## The big idea

On Day 2, the project learned how to make a mask: for every pixel in the image, it stored either `True` or `False`. That mask was useful, but it was still a two-dimensional picture. The next question is:

> If the mask says which pixels belong to the foreground, where is the top edge of the mountain in each image column?

Days 3 and 4 answer that question in two steps:

1. **Day 3** turns the two-dimensional mask into a one-dimensional skyline profile.
2. **Day 4** cleans and prepares that profile as a spatial signal.

The result is not yet music. It is a reliable numerical description of the visible mountain boundary that later stages can map to musical notes.

The pipeline now looks like this:

```text
image file
    ↓
RGB image array, shape (H, W, 3)
    ↓
HSV threshold segmentation
    ↓
boolean mask, shape (H, W)
    ↓
topmost foreground row in each column
    ↓
skyline profile, shape (W,)
    ↓
missing-value handling and signal processing
    ↓
cleaned or normalized spatial profile, shape (W,)
```

`H` means image height and `W` means image width. The profile has one value for every horizontal image position.

---

## Day 3: Extracting the visible skyline

The implementation is in [`src/skyline.py`](../src/skyline.py).

### Why one value per column?

A mountain skyline is a boundary that travels across the image from left to right. If we examine one vertical column at a time, we can ask:

> What is the first foreground pixel encountered when moving downward from the top of the image?

That first pixel is the visible top edge in that column.

Suppose a column has this mask:

```text
row 0: False   ← sky/background
row 1: False   ← sky/background
row 2: True    ← first mountain pixel
row 3: True
row 4: True
```

The skyline row for that column is `2`. We do not need to store all the `True` pixels anymore for the skyline representation. We only need the first one.

Repeating this for every column produces a one-dimensional array:

```text
[2, 2, 3, 4, 3, 2, ...]
```

That array is the apparent skyline profile.

### `extract_skyline(mask)`

The function accepts a two-dimensional boolean NumPy array:

```python
mask.shape == (height, width)
```

Its result is a one-dimensional floating-point array:

```python
skyline_rows.shape == (width,)
```

Each output element corresponds to one image column. The output uses floating-point values because missing columns need to be represented with `NaN`.

The algorithm is deliberately straightforward:

1. Validate that the mask is two-dimensional and boolean.
2. Create an output array filled with `NaN`.
3. Visit each column.
4. Find the row indices where the mask is `True`.
5. If any foreground rows exist, store the first one.
6. If none exist, leave the output as `NaN`.
7. Reject an image whose entire mask is empty.

The first foreground row is chosen because image coordinates start at the top. Row `0` is higher in the image than row `20`, so the smaller number is the topmost boundary.

### Why use `NaN` for an empty column?

An empty column does not mean that the mountain has height zero. It means the algorithm could not observe a foreground boundary there.

Those are different statements:

```text
height = 0       means a real measured low point
height = NaN     means no measurement exists
```

If we replaced missing columns with zero immediately, later code would interpret missing data as a real valley. That could create a false dip in the skyline and eventually produce an incorrect musical note.

Keeping `NaN` preserves the difference between “measured” and “unknown” until we deliberately choose a missing-data policy.

### Why reject an all-empty mask?

If every column is empty, there is no skyline to extract. Returning an array full of missing values would allow the error to travel into later stages, where it would be harder to understand.

`extract_skyline` therefore raises:

```text
ValueError: Mask contains no foreground pixels
```

This is an example of validating an important assumption at the boundary where it first becomes relevant.

---

## Image rows versus mountain height

The raw skyline output stores image row positions. Image rows point downward:

```text
row 0       top of image
row 1
row 2
...
row H - 1   bottom of image
```

That means a smaller row number represents a visually higher mountain point. This is convenient for image processing, but it is the opposite of the usual mathematical idea of height, where larger values mean higher points.

### `skyline_height(skyline_rows, image_height)`

This function converts image rows into an upward-positive representation:

```python
height = (image_height - 1) - skyline_row
```

For an image with height `4`:

```text
skyline row 0 → height 3
skyline row 1 → height 2
skyline row 2 → height 1
skyline row 3 → height 0
```

So the mountain profile now behaves more naturally:

- larger height means a higher visible boundary;
- smaller height means a lower visible boundary.

The function preserves `NaN`, so missing measurements remain missing after conversion.

This is still apparent image-space height. It is not real-world elevation. A mountain that appears higher in the image may simply be closer, photographed from a different angle, or positioned differently in the frame.

---

## Missing skyline values and interpolation

### `interpolate_missing(values)`

After skyline extraction, some columns may contain `NaN`. The interpolation function fills those gaps when at least one valid measurement exists.

For example:

```text
before: [NaN, 2, NaN, 6, NaN]
after:  [  2, 2,  4, 6,   6]
```

The value between `2` and `6` is estimated as `4`. The missing value at the beginning uses the nearest known value `2`, and the missing value at the end uses `6`.

The function uses linear interpolation for interior gaps and nearest-known-value extension for edge gaps. This is a simple and transparent first policy for a learning project.

### Why does interpolation happen separately?

Extraction and repair are different responsibilities:

- extraction reports what the mask actually says;
- interpolation estimates values where the mask gave no observation.

Keeping them separate means the raw skyline can still be inspected. It also prevents later code from forgetting that some values were estimated rather than directly measured.

The input is copied before filling, so the caller's original profile is not modified. This matters because it is often useful to compare the raw profile and repaired profile side by side.

### Important limitation

Interpolation is reasonable for short gaps where neighboring columns probably belong to the same visible surface. It becomes less trustworthy for very long gaps, large occlusions, or masks that contain unrelated foreground objects. A future version may report gap lengths or refuse to extrapolate unusually long missing regions.

---

## Day 4: Treating the skyline as a signal

The implementation is in [`src/signal_processing.py`](../src/signal_processing.py).

A skyline profile is a sequence of numbers indexed by horizontal image position:

```text
x = 0, 1, 2, 3, ...
profile[x] = visible height at that column
```

This is a **one-dimensional spatial signal**. It is called a signal because it changes over an ordered axis, but that axis is image position, not time.

That distinction is important:

- the x-axis is distance across the photograph;
- it is not seconds;
- changes in the profile are not automatically audio frequencies;
- filtering smooths visual shape, not recorded sound.

Day 4 currently provides two small processing operations: normalization and moving-average smoothing.

---

## Normalization

### `normalize_min_max(values)`

Skyline values are initially measured in pixels. A profile from a 100-pixel-tall image and a profile from a 1,000-pixel-tall image will naturally have different numeric ranges.

Normalization puts the values into a common range:

```text
minimum input → 0.0
maximum input → 1.0
```

The formula is:

```python
normalized = (value - minimum) / (maximum - minimum)
```

For example:

```text
input:       [2, 4, 6]
normalized:  [0, 0.5, 1]
```

This preserves relative shape while removing the original pixel scale. Later, a value such as `0.75` can be mapped consistently into a configured musical pitch range.

### Why reject a constant profile?

If every value is the same, then:

```text
maximum - minimum == 0
```

Dividing by zero is not meaningful. More importantly, a constant skyline contains no variation to map to different pitches.

The implementation raises a clear error instead of silently returning an arbitrary result. This makes the lack of useful variation visible to the caller.

### Why reject `NaN` values here?

Normalization assumes that every input value is known and finite. Missing columns should be handled explicitly first, normally with `interpolate_missing` or another documented policy.

This ordering keeps the pipeline honest:

```text
extract → identify missing values → handle missing values → normalize
```

---

## Moving-average smoothing

### `moving_average(values, window_size)`

A threshold mask can create small irregularities in the extracted skyline. One isolated pixel can move the detected boundary up or down by one or more rows. A moving average reduces these rapid changes.

For a window size of `3`, each output point is based on nearby points:

```text
output[x] = average(input[x - 1], input[x], input[x + 1])
```

The implementation uses edge padding so the output remains the same length as the input. For example, the first point is treated as if the edge value continues just outside the image.

A five-point input with a three-point window produces another five-point output:

```text
input:  [1, 2, 3, 4, 5]
output: [4/3, 2, 3, 4, 14/3]
```

### Why must the window be odd?

An odd window has a clear center point. A window of `3` has one value before, one center value, and one value after. A window of `5` has two on each side.

An even window does not have one natural center, so the function rejects it. The window must also be positive and cannot be longer than the signal.

### Smoothing trade-off

Smoothing is not automatically better. It is a trade-off:

- a small window preserves sharp peaks but removes less noise;
- a large window creates a calmer profile but can flatten real mountain peaks;
- too much smoothing can make separate peaks look like one broad hill;
- too little smoothing can make threshold noise appear as musical jumps later.

The raw profile should be preserved so that the effect of smoothing can be inspected rather than hidden.

---

## How the code stays modular

The implementation deliberately separates four ideas:

```text
segmentation.py
    decides which pixels pass the colour rule

skyline.py
    converts the mask into visible boundary coordinates

signal_processing.py
    cleans and transforms the one-dimensional profile

future music modules
    map the processed profile to notes and export MIDI
```

This separation gives each module one clear reason to change. If the HSV thresholds need improvement, skyline extraction does not need to change. If smoothing changes, the mask does not need to be recomputed conceptually. If musical mapping changes, the image-processing modules remain reusable.

Each source file is also kept small. The functions have narrow inputs and outputs, making them easier to test independently.

---

## Tests and what they prove

The Day 3 tests are in [`tests/test_skyline.py`](../tests/test_skyline.py). They verify:

- the topmost foreground row is selected;
- empty columns become `NaN`;
- an all-empty mask raises an error;
- image rows are converted into upward-positive heights;
- interpolation fills interior and edge gaps;
- interpolation does not mutate the original array.

The Day 4 tests are in [`tests/test_signal_processing.py`](../tests/test_signal_processing.py). They verify:

- normalization produces the expected `0..1` values;
- constant signals are rejected;
- moving averages use the documented edge behavior;
- invalid window sizes are rejected.

The tests use small synthetic arrays rather than a photograph. That makes their expected answers unambiguous and keeps them deterministic.

Run the complete current suite from PowerShell:

```powershell
cd C:\Users\HP\Desktop\mountain_music
python -m pytest
```

At the time these stages were implemented, the suite result was:

```text
15 passed
```

---

## What has not been implemented yet

Days 3 and 4 stop before music generation. The repository does not yet include:

- connected-component cleanup or morphology;
- an ROI restriction;
- skyline overlay rendering;
- advanced interpolation policies;
- median or Butterworth filtering;
- peak detection;
- musical scale mapping;
- MIDI event generation;
- MIDI file export;
- a Streamlit interface.

These are future stages. Keeping them out of the current implementation makes it possible to verify each transformation before adding another layer of behavior.

---

## A simple way to explain Days 3 and 4

If someone asks what the new code does, the short explanation is:

> Day 2 produces a yes/no mask for every image pixel. Day 3 reads that mask column by column and records the first foreground pixel, which represents the visible skyline. Missing columns are kept as `NaN` instead of being mistaken for real low points. Day 4 treats those skyline values as a one-dimensional spatial signal: it fills missing values when requested, normalizes the profile to `0..1`, and can smooth small irregularities with a moving average. The result is a clean numerical shape that a later module can map to musical notes.
