---
name: build-verify
description: Build or change this project and verify it with focused tests followed by a full pytest run when practical.
---

# Build and verify

Use this workflow for implementation tasks in Mountain to Music:

1. Read the relevant source, tests, README, and docs.
2. Make the smallest complete change.
3. Run the focused pytest tests for touched modules.
4. Run `python -m pytest` from the repository root when practical.
5. Inspect `git diff --check` and `git status --short`.
6. Report changed files, validation commands, results, and any limitations.

Do not treat a successful import as a substitute for tests. Do not include `.venv`, caches, private images, or generated outputs in a change.
