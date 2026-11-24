# Changelog

## 0.1.0 — 2026-11-24

First release, as claude-x-gemini (developed as gemini-relay).

- One skill, three tools: `explain`, `say`, `handoff`, through the Antigravity CLI (`agy`), read-only.
- Claude Code writes to Gemini in its own words; no brief template. Gemini's answers are passed on unedited.
- Optional styles (off by default): `plain` (~80% ASD-STE100), `eli5`, `feynman`, `expert`; optional `--html`.
- Second opinion: for big plans, Gemini writes an independent plan from the human's words; Claude merges.
- Gemini is asked to stay read-only and mark what it inferred.
- Likely secret files are denied by exact path; a fast startup failure is retried once.
