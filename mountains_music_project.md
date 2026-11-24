**This document is the implementation contract for the coding agent.** The human developer has a separate Personal Learning Guide. Your job is to help implement the project in small, reviewable increments while explaining the code and preserving the developer's ownership of the work.

Do not treat this document as permission to generate the entire application in one response. Follow the current day/stage requested by the developer. Do not implement later stages early.

---

# 1. Product definition

Build a Python application that converts the visible skyline of a mountain range in a static panoramic image into a musical sequence.

Input:
- user-uploaded static image (JPG, JPEG, PNG initially);
- processing and music-mapping parameters selected in the UI.

Core processing:
1. load and validate image;
​2. segment mountain pixels from background;
3. extract topmost mountain boundary per image column;
4. handle missing columns;
5. represent the skyline as a 1D spatial signal;
6. apply selectable smoothing/filtering;
7. normalize profile;
8. map profile to musical notes and durations;
9. export MIDI;
10. display intermediate results and parameter effects.

**Scientific language:** This system analyses apparent skyline geometry in image coordinates. It does not infer true mountain elevation, geographic distance, depth, or physical terrain. Do not describe image x-position as time. The profile is a spatial signal.

# 2. Non-negotiable agent behaviour

## 2.1 Work incrementally
- Implement only the stage/day the developer asks for.
- Before editing, inspect the existing project structure and relevant files.
- Do not overwrite working code without explaining why.
- Prefer small changes over large rewrites.
- After each change, run the most relevant tests or a minimal reproducible check.
- Report exact commands run and actual results. Never invent test outcomes.
- If a test cannot run due to missing dependencies or environment limitations, state that explicitly.

## 2.2 Teach while building
For every meaningful code change, provide:
1. the problem being solved;
​2. the concept behind the solution;
3. the files changed;
4. a walkthrough of the important functions;
5. input/output types and array shapes;
6. assumptions and edge cases;
7. how the developer can verify it;
8. one small exercise or modification the developer should attempt.

Do not dump a large block of unexplained code. Keep functions small and names descriptive. The developer is learning Python, computer vision, DSP, and software engineering.

## 2.3 Preserve developer agency
- If the developer asks for a hint, do not immediately reveal the full solution.
- If they provide code, review it before replacing it.
- Explain errors using the actual traceback and relevant code.
- Do not silently add libraries or architecture.
- Ask before introducing a major dependency, external service, paid API, large model, or deployment platform.
- Do not use a cloud GPU or assume a GPU exists.
- Do not claim the project uses AI/deep learning unless an actual model is implemented.

## 2.4 No premature complexity
For the MVP, prefer conventional OpenCV thresholding, ROI constraints, and morphology. Do not introduce SAM, YOLO, large segmentation models, neural audio generation, databases, authentication, cloud storage, or microservices unless explicitly requested after the MVP works.

## 2.5 Maintain project notes
If the repository contains `docs/learning_log.md` or `docs/experiments.md`, update them only with facts confirmed by the developer or actual test results. Do not fabricate learning reflections or experiment outcomes. If uncertain, propose text and ask the developer to confirm before recording it.

---

# 3. Technical architecture

Keep processing logic independent from the Streamlit interface.

Suggested structure:

```text
mountain-to-music/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_images/
├── src/
│   ├── __init__.py
│   ├── image_io.py
│   ├── segmentation.py
│   ├── skyline.py
│   ├── signal_processing.py
│   ├── music_mapping.py
│   └── midi_export.py
├── tests/
│   ├── test_skyline.py
│   ├── test_signal_processing.py
│   └── test_music_mapping.py
├── outputs/
└── docs/
    ├── learning_log.md
    └── experiments.md
```

Adapt this structure if the existing repository already has a sound organization. Do not create empty files merely to match the diagram.

## Module responsibilities

### `image_io.py`
- Decode uploaded image bytes or accept a supported image object.
- Validate image dimensions, channels, and dtype.
- Convert to a documented internal colour convention.
- Avoid accidental BGR/RGB confusion.
- Provide clear errors for unsupported or invalid images.

### `segmentation.py`
- Convert to HSV or another explicitly selected colour space.
- Create a mountain/background mask using tunable thresholds and ROI.
- Apply optional morphology.
- Return the mask and useful diagnostics.
- Make mask polarity explicit: document whether mountain pixels are `True/1` or `False/0`.
- Do not pretend colour thresholding is semantic segmentation.

### `skyline.py`
- For each column, find the topmost foreground mountain pixel.
- If the mask is boolean with `True` meaning mountain, this is the smallest row index where the mask is true.
- Return both raw row coordinates and an upward-positive height profile, or a clearly documented single convention.
- Represent empty columns as missing values (`NaN` or a documented equivalent), not as a real zero-height mountain.
- Provide a separate missing-value handling function.
- Include an overlay helper for visual verification.

### `signal_processing.py`
- Missing-value interpolation or handling.
- Min-max normalization with constant-signal protection.
- Moving average.
- Median filter.
- Butterworth low-pass filter using SciPy second-order sections (`output="sos"`).
- Optional derivative and peak detection.
- Validate all parameters and signal lengths.
- Keep raw and processed arrays separate; never mutate caller input unexpectedly.

### `music_mapping.py`
- Map normalized profile values to a configured MIDI note range.
- Quantize to a selected scale.
- Generate deterministic note events.
- Start with equal-duration notes; peak-informed rhythm is a later optional extension.
- Define note-event data clearly (pitch, start, duration, velocity).
- Validate MIDI pitch range and positive duration.

### `midi_export.py`
- Convert note events to a valid MIDI file.
- Ensure note-on/note-off events are paired.
- Expose tempo and instrument/program settings if supported.
- Write to a safe temporary/output path and return a usable file handle or bytes for Streamlit download.
- Do not assume MIDI playback is available on every operating system.

### `app.py`
- Streamlit presentation layer only.
- Upload image, show controls, invoke module functions, display plots, and provide downloads.
- Avoid embedding all image/DSP/music logic in this file.
- Cache expensive deterministic stages where appropriate.
- Changing a smoothing control should not rerun segmentation if the source image and segmentation settings have not changed.

---

# 4. Data conventions and algorithmic requirements

## 4.1 Image conventions
- OpenCV images are typically BGR. Convert explicitly when required.
- Document image shape as `(height, width, channels)` for colour images.
- Validate non-empty dimensions.
- Avoid resizing unless necessary; if resizing is used, document target dimensions and interpolation method.
- Keep a copy of the original image for overlays.

## 4.2 Segmentation conventions
- A binary mask must have an explicit foreground convention.
- If `True` represents mountain, skyline extraction searches for `True`.
- Thresholds must be adjustable and visible to the user.
- Morphology kernel shape and size must be configurable or have documented defaults.
- ROI must not silently crop off the skyline.
- A colour threshold is a heuristic. Show failure cases and do not label it as a trained segmentation model.

## 4.3 Skyline extraction
For each column `c`:
- find row indices `r` for which `mask[r, c]` is foreground;
- if any exist, `skyline_row[c] = min(r)`;
- otherwise set `skyline_row[c] = NaN`.

With image height `H`, upward-positive height can be:
`height[c] = (H - 1) - skyline_row[c]`.

Important:
- `NaN` columns must remain identifiable until an explicit handling step.
- If all columns are missing, raise a clear error.
- If only some columns are missing, interpolate only according to a documented policy.
- Avoid extrapolating long missing regions without warning.
- Plot the skyline overlay on the original image to validate alignment.

## 4.4 Signal processing
- Do not silently normalize a constant signal; return a documented safe result or raise a clear validation error.
- Filter parameters must be checked before calling SciPy.
- Butterworth cutoff must be valid relative to Nyquist and the chosen SciPy API.
- Prefer `scipy.signal.butter(..., output="sos")`.
- `sosfiltfilt` may fail or behave poorly on short signals; handle this case and explain the fallback.
- Explain edge effects in the UI or documentation.
- Do not claim FFT spatial frequencies are audio frequencies.
- FFT is optional and must not block MVP completion.

## 4.5 Musical mapping
- MIDI note 69 corresponds to A4 = 440 Hz.
- Equal-tempered frequency relation: `f = 440 * 2 ** ((midi_note - 69) / 12)`.
- Define scale pitch classes explicitly.
- Quantize to the nearest allowed note in the selected range.
- Keep note durations positive.
- Begin with equal-duration events.
- Peak-informed rhythm, velocity from prominence, or articulation from slope are optional extensions after baseline MIDI is correct.
- The output must be deterministic for identical input and parameters.

---

# 5. Interface requirements

Use Streamlit for the first version. It is a practical browser-based interface and can be opened from a phone on the same network if the developer chooses to configure that. Do not claim it is a native mobile app.

Minimum UI:
- image uploader;
- source image preview;
- segmentation controls;
- mountain mask preview;
- skyline overlay;
- raw profile plot;
- filter selection and parameters;
- processed profile plot;
- pitch range and scale selection;
- note-sequence summary or piano-roll-like plot;
- MIDI download.

Optional:
- audio preview/rendering, only if a reliable local synthesizer/rendering route is available;
- FFT spectrum;
- manual mask correction;
- multiple layers;
- time-lapse processing.

UI must state that the extracted profile represents apparent image-space skyline geometry.

---

# 6. Testing requirements

Write tests for deterministic functions. Use synthetic arrays where possible so tests do not depend on a particular photograph.

## Skyline tests
1. A simple mask with known topmost foreground row per column.
​2. A column with no foreground pixels.
3. All-empty mask.
4. A mask with one mountain pixel.
5. Correct upward-positive conversion.
6. Missing-value interpolation behaviour.

## Signal-processing tests
1. Normalization maps a non-constant signal into the expected range.
​2. Constant signal is handled safely.
3. Moving average returns a sensible output shape.
4. Median filter suppresses an artificial isolated spike.
5. Butterworth rejects invalid cutoff values.
6. Short-signal filtering has an explicit, tested behaviour.
7. Input arrays are not unexpectedly modified.

## Music-mapping tests
1. Low and high normalized values map to the intended note range.
​2. Scale quantization returns only allowed pitch classes.
3. Every pitch is a valid MIDI note.
4. Every duration is positive.
5. Identical inputs and parameters produce identical events.

## Integration checks
- A valid sample image can pass through segmentation, skyline extraction, processing, mapping, and MIDI export.
- An invalid or sky-only image produces a helpful error rather than a crash.
- MIDI file exists or download bytes are non-empty.
- Run the actual tests before reporting success.

---

# 7. The 21-day staged build plan

**Rule:** Work on the stage explicitly requested. At the end of a stage, stop and report. Do not automatically continue to the next stage.

## Week 1 — Computer vision and profile extraction

### Day 1: Repository and image loading
Build:
- initial project structure;
- virtual-environment and dependency instructions;
- `.gitignore`;
- image loading/display script;
- basic image validation.

Explain Python modules, environment setup, paths, image shape, dtype, and BGR/RGB.

Acceptance criteria:
- one supplied sample image loads;
- dimensions and dtype print correctly;
- image displays with correct colours;
- invalid path or unsupported image gives a useful error.

Do not implement segmentation yet.

### Day 2: HSV and first segmentation
Build:
- BGR-to-HSV conversion;
- adjustable threshold-based mask;
- visual display of mask;
- clear threshold configuration.

Explain HSV channels and threshold trade-offs.

Acceptance criteria:
- mask has same height and width as image;
- foreground convention is documented;
- user can inspect false positives and false negatives.

Do not implement morphology unless the developer requests it as part of this day.

### Day 3: Morphology and ROI
Build:
- optional opening and closing;
- configurable kernel size;
- ROI support if needed;
- before/after mask comparison.

Explain kernel shape/size and why morphology can remove real features.

Acceptance criteria:
- operations can be enabled/disabled;
- mask dimensions remain correct;
- parameters are validated.

### Day 4: Skyline extraction
Build:
- topmost foreground pixel per column;
- explicit missing values;
- upward-positive height conversion;
- skyline overlay plot.

Explain image row coordinates and NumPy column indexing.

Acceptance criteria:
- synthetic mask test passes;
- overlay aligns with image;
- empty columns are not silently interpreted as zero.

### Day 5: Validation and edge cases
Build:
- unit tests for skyline extraction;
- missing-column handling;
- all-empty-mask error;
- simple image-quality diagnostics.

Acceptance criteria:
- tests run and actual output is reported;
- known failure cases are documented;
- no fabricated test claims.

### Day 6: Spatial profile and normalization
Build:
- explicit profile-cleaning function;
- documented missing-value policy;
- min-max normalization;
- raw/clean/normalized plots.

Explain that x is image position and the profile is spatial.

Acceptance criteria:
- constant-signal case handled;
- normalized range is correct;
- input profile remains unchanged.

### Day 7: Week 1 review
Do not add new major features. Review modules, tests, documentation, and a real sample image. Identify unresolved segmentation limitations.

Acceptance criteria:
- developer can explain image -> mask -> skyline -> profile;
- README has setup and current functionality;
- all current tests pass or failures are clearly listed.

## Week 2 — DSP and music generation

### Day 8: Moving average
Build:
- moving-average filter;
- validated window length;
- comparison plot with raw profile.

Explain convolution and edge policy.

### Day 9: Median filter
Build:
- median-filter option;
- configurable window;
- artificial-spike comparison.

Explain robustness to isolated outliers.

### Day 10: Butterworth low-pass
Build:
- SciPy Butterworth low-pass using SOS;
- cutoff/order controls;
- validation and short-signal fallback/error;
- filter response plot if practical.

Explain cutoff, order, Nyquist, and phase/edge effects.

### Day 11: Filter comparison
Build:
- consistent comparison of raw, moving-average, median, and Butterworth outputs;
- a default filter choice only after inspecting results.

Do not claim an objectively best filter without evaluation.

### Day 12: Derivative and peak detection
Build:
- first difference/slope plot;
- `find_peaks` with prominence and distance controls;
- peak overlay.

Explain sign convention and noise sensitivity.

### Day 13: Pitch mapping
Build:
- normalized height to MIDI pitch range;
- scale quantization (at least pentatonic);
- note sequence display.

Explain MIDI pitch and quantization. Keep mapping deterministic.

### Day 14: MIDI export
Build:
- equal-duration note events;
- MIDI file export;
- tempo and basic instrument setting if library supports it;
- validation tests.

Acceptance criteria:
- valid non-empty MIDI file;
- note count, pitch range, and durations verified;
- no dependency on audio playback for MIDI correctness.

## Week 3 — Streamlit, integration, and release

### Day 15: Streamlit shell
Build:
- image upload;
- image preview;
- app calls existing modules;
- clear UI layout.

Do not move processing logic into `app.py`.

### Day 16: Processing controls
Build:
- segmentation and filtering controls;
- mask and skyline visualizations;
- raw/processed signal plots;
- appropriate caching.

Cache only deterministic expensive stages. Changing filter settings should not redo segmentation when source and segmentation parameters are unchanged.

### Day 17: MIDI integration
Build:
- pitch/scale controls;
- MIDI download;
- note summary.
Audio rendering is optional and must not delay a working MIDI export.

### Day 18: Robustness
Test:
- portrait and landscape images;
- small images;
- invalid files;
- sky-only image;
- partial mask;
- short profiles;
- invalid parameters.

Add useful error messages.

### Day 19: End-to-end tests
Build/run:
- deterministic pipeline integration test;
- same input/settings repeatability check;
- performance observation on developer's actual machine.

Do not claim performance numbers without measuring them.

### Day 20: Documentation and repository polish
Build:
- complete README;
- architecture diagram (Mermaid is acceptable);
- sample screenshots;
- installation and run instructions;
- limitations and future work;
- clean dependency list.

Do not include private data or huge unnecessary images.

### Day 21: Final demo and handover
Prepare:
- short demo flow;
- one or more tested sample inputs;
- pipeline explanation;
- experiment results that were actually measured;
- known limitations;
- next-step recommendations.

Do not invent user feedback, benchmark results, or test outcomes.

---

# 8. Coding standards

- Use clear names and small functions.
- Add type hints where they improve clarity.
- Add docstrings for public functions, including expected shapes and conventions.
- Avoid global mutable state.
- Avoid unnecessary classes; simple functions are sufficient initially.
- Keep image processing, DSP, music mapping, and UI separate.
- Validate external inputs at module boundaries.
- Prefer deterministic pure functions for transformations.
- Use logging or clear error messages rather than swallowing exceptions.
- Do not catch every exception and hide the traceback during development.
- Keep dependencies minimal.
- Use pathlib for filesystem paths.
- Do not hardcode machine-specific absolute paths.
- Do not commit generated caches, virtual environments, or secrets.

---

# 9. Required response format after each coding task

After implementing a requested stage, respond using these headings:

## What changed
List the files created or modified.

## Concept
Explain the key idea in plain language, then give the technical explanation.

## Code walkthrough
Explain important functions, inputs, outputs, and array shapes.

## Verification
List commands actually run and their actual results. If none were run, say so.

## Limitations
State what is not handled yet and any assumptions.

## Your turn
Give the developer one small task to perform or one question to answer to verify understanding.

## Stop point
State the next stage, but do not implement it until requested.

---

# 10. How to handle debugging requests

When the developer reports a bug:
1. Ask for or inspect the exact traceback, relevant code, input shape, and expected versus actual output if missing.
​2. Identify the earliest pipeline stage that produces an incorrect result.
3. Create a minimal reproduction if possible.
4. Explain the root cause before changing code.
5. Make the smallest reliable fix.
6. Add a regression test.
7. Run the relevant test and report the actual result.

Do not respond to every bug by rewriting the entire module. Do not alter unrelated code.

---

# 11. OmniRoute / model usage guidance

The developer may route requests to different coding models through OmniRoute. Do not assume a specific model's capabilities or claim that a provider is available. Work with the model selected by the developer.

For large tasks:
- inspect repository context first;
- split work into one module or feature at a time;
- keep prompts and diffs focused;
- ask before making broad architectural changes;
- summarize changed files and verification.

If context is getting large, produce a concise handover note containing:
- current project stage;
- implemented files;
- current architecture;
- tests run and results;
- known bugs;
- next exact task.

Never invent repository state. If you cannot inspect a file or execute a command, tell the developer.

---

# 12. First instruction to the coding agent

When this document is first supplied, do **not** build the full project.

1. Inspect the existing VS Code workspace.
​2. Report whether it is empty or contains an existing project.
3. Check Python availability and the current environment without changing system configuration.
4. Propose the minimal Day 1 setup.
5. Explain each command before asking the developer to run it.
6. Wait for the developer's confirmation before making changes that alter the environment or repository.

**The goal is a working project that the student understands, not a large codebase the student cannot maintain.**