# Changelog

## 0.1.0 — 2026-11-24

First release.

- One skill, three tools: `explain`, `say`, `handoff`, through the Antigravity CLI (`agy`), read-only.
- Claude Code writes to Gemini in its own words; no brief template. Gemini's answers are passed on unedited.
- Optional styles (off by default): `plain` (~80% ASD-STE100), `eli5`, `feynman`, `expert`; optional `--html`.
- Likely secret files are denied by exact path; a fast startup failure is retried once.
