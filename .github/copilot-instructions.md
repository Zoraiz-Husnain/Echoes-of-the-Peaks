# Mountain to Music contribution guidance

## Goal
Convert a mountain skyline extracted from an image into a musical sequence. Treat the skyline as image-space geometry; do not imply real elevation, depth, distance, or terrain.

## Required workflow
- Read the relevant README, docs, source, and tests before changing behavior.
- Make precise, scoped changes and update directly related documentation.
- Add focused regression tests for new or changed behavior.
- Run targeted tests, then `python -m pytest` when practical.
- Inspect `git diff --check` and `git status --short` before reporting completion.
- Report commands and results accurately; distinguish unrun checks from passing checks.

## Python conventions
- Keep functions small, typed, deterministic, and easy to test.
- Validate public inputs at boundaries with useful exceptions.
- Preserve existing APIs unless the task explicitly changes them.
- Prefer NumPy/OpenCV operations already used by the project; avoid unnecessary dependencies.
- Use synthetic arrays and temporary paths for deterministic tests.

## Repository hygiene
Never commit secrets, private images, virtual environments, caches, or generated output files. Treat segmentation and skyline extraction as heuristics and document assumptions that affect results.
