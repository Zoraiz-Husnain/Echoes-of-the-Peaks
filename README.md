# Mountain to Music

Convert the visible skyline of a mountain range in a static image into a musical sequence. The project treats the extracted profile as apparent image-space geometry; it does not infer real elevation, depth, distance, or terrain.

## Current stage

Day 1: repository and image loading. Segmentation and music generation are not implemented yet.

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

- No segmentation is implemented yet.
- The project currently reports image metadata only; it does not display or transform images in a UI.
- Do not commit private images, generated files, virtual environments, or secrets.
