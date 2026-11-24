# Mountain to Music

Convert the visible skyline of a mountain range in a static image into a musical sequence. The project treats the extracted profile as apparent image-space geometry; it does not infer real elevation, depth, distance, or terrain.

## Current stage

The complete pre-music pipeline is available: HSV segmentation, skyline/edge extraction, missing-column interpolation, normalization and moving/median DSP, deterministic scale-quantized note generation, and optional Matplotlib inspection plots. The project still does not export audio or MIDI.

## Setup (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run this once for the current user or use the environment's Python directly:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Run the Day 1 image check

```powershell
python -m src.image_io path\to\image.jpg
```

The command validates JPG/JPEG/PNG input and prints the image shape, dtype, and colour convention. OpenCV decodes images as BGR; the loader returns RGB for display-oriented code.

## Run the Day 2 segmentation check

Use the saved sample image from this repository:

```powershell
python -m src.segmentation data\sample_images\download.jpg --output outputs\mask.png --hue 0 179 --saturation 0 255 --value 0 180
```

The CLI prints the aligned mask shape and foreground pixel count. Saved masks use white (`255`) for foreground and black (`0`) for background. See [docs/day_02_hsv_and_segmentation.md](docs/day_02_hsv_and_segmentation.md) for threshold guidance.

For a complete current-project walkthrough, including file responsibilities and the concepts behind the implementation, see [docs/project_overview.md](docs/project_overview.md). For a detailed, beginner-friendly explanation of Days 3 and 4, see [docs/day_03_04_skyline_and_signal_processing.md](docs/day_03_04_skyline_and_signal_processing.md). For a comprehensive learning guide, edge-detection debugging workflow, and concept-to-source map, see [docs/learning_guide_and_current_state.md](docs/learning_guide_and_current_state.md).

Day 3 extracts the topmost foreground row per image column. Day 4 interpolates missing columns and provides min-max normalization and moving-average smoothing for the resulting spatial profile.

## Run the local UI

After installing `requirements.txt`, launch the Streamlit app from the repository root:

```powershell
python -m streamlit run app.py
```

Streamlit prints a local URL (normally `http://localhost:8501`). Upload a JPG, JPEG, or PNG in the sidebar, tune HSV thresholds, choose a spatial filter and musical scale, then inspect the mask, skyline overlay, profile waves, and generated MIDI-note contour. This version presents note events only; the repository does not yet export audio or MIDI files.

The app uses the existing modules through the pure `src.pipeline.run_pipeline` orchestrator. The profile is a spatial signal indexed by image columns, not an audio waveform, and the result is apparent image-space geometry rather than inferred elevation.

## Test

```powershell
python -m pytest tests/test_pipeline.py
python -m pytest
```

## Planned structure

```text
mountain_music/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/sample_images/
├── src/
│   ├── image_io.py
│   ├── segmentation.py
│   ├── skyline.py
│   ├── signal_processing.py
│   ├── music_mapping.py
│   └── midi_export.py
├── tests/
├── outputs/
└── docs/
```

## Limitations

- HSV segmentation is a tunable colour-threshold heuristic, not semantic segmentation; lighting and scene content affect results.
- The UI currently displays spatial profile waves and note contours; it does not synthesize or export audio/MIDI files yet.
- Uploads are limited to 10 MB and 16 million pixels by the local UI.
- Do not commit private images, generated files, virtual environments, or secrets.
