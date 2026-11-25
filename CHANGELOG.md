# Changelog

## 0.2.1 — 2026-11-25

- Launch film, new cut (36 s), in Chinese and English: the five steps of one request play in the 3D opening, then the
  real recording, then the loop figure. `README.md` plays the English cut, `README.zh-CN.md` the Chinese one.

## 0.2.0 — 2026-11-25

- Language follows the human: one fixed line asks Gemini to write everything, progress notes included, in the
  language the human uses. No language is named anywhere; the `say` log labels are now language-neutral.
- The relay's fixed lines are labelled as the relay's, so Gemini's handoff no longer lists them as the
  human's requests.
- `relay.py doctor`: checks `agy`, sign-in, quota and Gemini models without spending a turn.
- README: a "How it differs" section against worker-style `agy` plugins.
- Canary test of the secret-file deny list (agy 1.5.16): no search or listing tool was available, `.env` was
  denied, no planted value leaked.
- README, both languages: rebuilt for a fast read. One-sentence definition, @Khazix0918's post as the lead
  picture, an "In 30 seconds" table, the request as a 3D loop figure with five steps, and a quick reference
  for agents.
- README pictures: a sharper screenshot of the post; an English rendering of it for `README.md`, marked as a
  translation.
- The 26-second launch film (Chinese) plays inline in both READMEs; the mp4 stays in `assets/`.

## 0.1.0 — 2026-11-24

First release, as claude-x-gemini (developed as gemini-relay).

- One skill, three tools: `explain`, `say`, `handoff`, through the Antigravity CLI (`agy`), read-only.
- Claude Code writes to Gemini in its own words; no brief template. Gemini's answers are passed on unedited.
- Optional styles (off by default): `plain` (~80% ASD-STE100), `eli5`, `feynman`, `expert`; optional `--html`.
- Second opinion: for big plans, Gemini writes an independent plan from the human's words; Claude merges.
- Gemini is asked to stay read-only and mark what it inferred.
- Likely secret files are denied by exact path; a fast startup failure is retried once.
