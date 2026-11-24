---
name: deep-review
description: Review a change as a skeptical senior engineer for correctness, regressions, tests, maintainability, and security.
---

# Deep review

Review the diff and surrounding code without editing. Check behavior against README and docs, public API compatibility, input validation, numerical edge cases, test quality, dependency changes, and generated-file hygiene. Run targeted tests if useful. Report only actionable findings with severity, file/line, evidence, impact, and a concrete fix. Explicitly state when no findings remain.
