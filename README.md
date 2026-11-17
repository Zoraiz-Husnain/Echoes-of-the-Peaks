# Mountain to Music

Convert the visible skyline of a mountain range in a static image into a musical sequence. The project treats the extracted profile as apparent image-space geometry; it does not infer real elevation, depth, distance, or terrain.

## Current stage

Day 2: HSV threshold segmentation. The loader and first tunable foreground mask are implemented; morphology, skyline extraction, and music generation remain future stages.

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

For a complete current-project walkthrough, including file responsibilities and the concepts behind the implementation, see [docs/project_overview.md](docs/project_overview.md).

## Test

```powershell
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
- The project currently reports image metadata only; it does not display or transform images in a UI.
- Do not commit private images, generated files, virtual environments, or secrets.
