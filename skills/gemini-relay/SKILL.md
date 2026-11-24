---
name: gemini-relay
description: Let Gemini (via the Antigravity CLI, agy) explain things to the human and carry their ideas back to you. Gemini reads the files itself, so you spend few tokens. Use only when the human asks for Gemini ("ask Gemini to explain…", "让 Gemini 讲…", "talk it over with Gemini", "get Gemini's handoff"); never unasked, because files go to Google.
license: MIT
compatibility: Claude Code with the Antigravity CLI (agy) signed in; Python 3.9+; macOS or Linux; network access to Google.
---

# gemini-relay

You are the relay between the human and Gemini. Gemini reads and explains; the human talks with Gemini
through you; Gemini then tells you what they want. Use the human's language for everything you write to Gemini
and to the human; never default to English or any other language.

The three steps below are tools, not a pipeline: use any of them, in any order, and stop whenever the human's
need is met. You decide what comes next.

`$R` below is `scripts/relay.py` inside this skill's folder (its base directory). Run it from the project root.
Needs the Antigravity CLI signed in (`agy` once in a terminal).

## 1. Explain

Write Gemini a message in your own words, the way you would brief a colleague, and save it to a scratch file.
You know the project and the conversation; tell Gemini what it needs to give a good explanation. Name the files
it should read instead of pasting them, and do not read them yourself first.

Run in the background: `python3 $R explain --brief <file> --slug <topic>`
- `--style plain|eli5|feynman|expert`: only when the human asks for a style. By default no style is added.
- `--html` for an interactive page instead of Markdown.
- `--model`, `--effort`: the strongest Gemini the account has (`python3 $R models`).

Then:
1. If `answered` is false, tell the human the `error` and offer a retry. Do not write the explanation yourself.
2. Hand the answer over as it is: paste it if it is short, otherwise give the link to the file. Do not
   summarize or rewrite it.

## 2. Talk

When the human wants to ask Gemini something or discuss an idea, tell Gemini what they mean, in your words:
`python3 $R say "<message>"` (continues the latest conversation; `--new` starts a fresh one)
Make clear it comes from the human. Fix speech-to-text slips and add context Gemini lacks; keep their wording
when it matters. Show Gemini's reply (printed after the JSON) to the human as it is; if it is long, point to
the `-talk.md` file instead.

## 3. Handoff

When Gemini's understanding should come back into the work (the human asks, or you judge it useful, even right
after an explanation): `python3 $R handoff`. Gemini can be wrong and sound sure, so review the
handoff before you act on it:
- Compare it with what the human actually said to you. Their words win; if the two disagree, ask the human.
- Check facts and numbers you will rely on against the project's files. Tell the human what was wrong.
- Then move the work forward: do what the human asked for. Confirm first anything that changes direction,
  scope, or spends money, quoting their words. Undecided items stay undecided; Gemini's suggestions are not requests.
