#!/usr/bin/env python3
"""claude-x-gemini: Gemini (Antigravity CLI `agy`) explains things to you, then carries your ideas back to Claude Code.

  explain --brief FILE [--style plain|eli5|feynman|expert] [--html]  Claude's message to Gemini, in its own
                                                                      words; Gemini reads the files it names and
                                                                      writes the explanation (style: off unless asked)
  say "MESSAGE" [--new]                                               Claude's rendering of what you mean, into
                                                                      the latest conversation (or a new one); prints the reply
  handoff                                                             Gemini writes what you asked for and what is open
  models                                                              models your account can use
  doctor                                                              checks agy, sign-in, quota and models (no turn spent)

Run from the project root. Files go to $CLAUDE_X_GEMINI_DIR (default .claude-x-gemini/). The newest explanation is
the current conversation; pass --file to pick another. Optional: .claude-x-gemini.md at the project root is added
to every prompt (language, audience, terms).

Gemini runs read-only: writes and shell commands are refused (a refused write ends its turn with no answer).
Likely secret files (.env*, keys, credentials) are denied one by one by exact path, because agy 1.5.16 ignores
glob and regex deny rules. Read-only settings follow github.com/yuting0624/antigravity-for-claude-code.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "assets"  # message templates sent to Gemini
PROJECT = Path.cwd()
STYLE_FILE = PROJECT / ".claude-x-gemini.md"
OUT = PROJECT / os.environ.get("CLAUDE_X_GEMINI_DIR", ".claude-x-gemini")
MAX_ARG = 60_000
# The only fixed text sent with every new conversation. Any refused action (a write, or a read outside the
# project; seen 11-24) ends agy's turn with no answer. Marking inferences: in testing, Gemini stated guesses as facts until asked to mark them.
READ_ONLY_LINE = ("You may only read files inside this project folder. Do not write files or run commands. "
                  "Mark anything you inferred rather than read.")
# No language is ever fixed: Gemini follows the human. Without this line, agy's progress notes came back in
# English inside a Chinese answer (seen 11-25).
LANGUAGE_LINE = "Write everything, progress notes included, in the language the human uses in this conversation."
SECRET_GLOBS = [".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.keystore", "id_rsa*", "id_ecdsa*",
                "id_ed25519*", ".netrc", ".npmrc", ".pypirc", "*credentials*", "*secret*", "*.tfvars"]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}


def read(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8").strip()


def project_style() -> str:
    return "\n\n" + STYLE_FILE.read_text(encoding="utf-8").strip() if STYLE_FILE.exists() else ""


def secret_files() -> list[str]:
    found = []
    for root, dirs, files in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        found += [os.path.join(root, f) for f in files if any(fnmatch.fnmatch(f.lower(), g) for g in SECRET_GLOBS)]
        if len(found) > 2000:
            break
    return found[:2000]


def settings() -> str:
    return json.dumps({"agentMode": "", "allowNonWorkspaceAccess": False, "toolPermission": "request-review",
                       "permissions": {"allow": [], "ask": ["write_file(*)", "command(*)"],
                                       "deny": [f"read_file({f})" for f in secret_files()]}})


def agy(text: str, a: argparse.Namespace, conversation: str | None = None) -> dict:
    """Call agy once more if it fails fast with no answer (seen 11-24: a TLS timeout to Google at startup)."""
    env = agy_once(text, a, conversation)
    if env["status"] != "SUCCESS" and not env["reply"] and env["wall_seconds"] < 60:
        time.sleep(5)
        env = agy_once(text, a, conversation)
    return env


def agy_once(text: str, a: argparse.Namespace, conversation: str | None = None) -> dict:
    if len(text.encode()) > MAX_ARG:
        sys.exit("message too long for one call; name files in the brief instead of pasting them.")
    exe = shutil.which("agy") or sys.exit("agy not found: install the Antigravity CLI and run `agy` once to sign in.")
    cmd = [exe, "-p", text, "--output-format", "json", "--disable-slash-commands", "--settings", settings(),
           "--print-timeout", f"{a.timeout}m"]
    for flag, val in (("--model", a.model), ("--effort", a.effort), ("--conversation", conversation)):
        if val:
            cmd += [flag, val]
    started = time.monotonic()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:  # files + no stdin: agy may drop piped stdout
        try:
            rc = subprocess.run(cmd, cwd=PROJECT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                timeout=a.timeout * 60 + 120).returncode
        except subprocess.TimeoutExpired:
            rc = -1
        out.seek(0), err.seek(0)
        stdout, stderr = out.read().decode(errors="replace").strip(), err.read().decode(errors="replace").strip()
    env: dict = {}
    for candidate in (stdout, stdout.splitlines()[-1] if stdout else ""):
        try:
            env = json.loads(candidate)
            break
        except json.JSONDecodeError:
            pass
    env = env if isinstance(env, dict) else {}
    env.setdefault("status", "ERROR")
    env["reply"] = (env.get("response") or "").strip()
    env["exit_code"], env["stderr"] = rc, stderr[-800:]
    env["wall_seconds"] = round(time.monotonic() - started, 1)  # agy's duration_seconds is cumulative per conversation
    return env


def summary(path: Path, env: dict, **extra) -> dict:
    return {"file": os.path.relpath(path, PROJECT), "answered": env["status"] == "SUCCESS" and bool(env["reply"]),
            "conversation_id": env.get("conversation_id"), "seconds": env["wall_seconds"],
            "session_tokens": (env.get("usage") or {}).get("total_tokens"), "error": env.get("error"),
            "stderr": env["stderr"] or None, **extra}


def current(a: argparse.Namespace) -> tuple[Path, dict]:
    if a.file:
        md = Path(a.file)
    else:
        metas = sorted(OUT.glob("*.json"), key=lambda p: p.stat().st_mtime)
        if not metas:
            sys.exit("no conversation yet; run `explain` first.")
        meta = json.loads(metas[-1].read_text())
        md = OUT / meta["file"]
    meta = json.loads(md.with_suffix(".json").read_text())
    if not meta.get("conversation_id"):
        sys.exit("that explanation failed, so there is no conversation to continue; run `explain` again.")
    a.model = a.model or meta.get("model")
    return md, meta


def cmd_explain(a: argparse.Namespace) -> int:
    brief = Path(a.brief).read_text(encoding="utf-8").strip()
    style = f"\n\nStyle: {read(f'styles/{a.style}.md')}" if a.style else ""  # off unless the human picks one
    fmt = "\n\n" + read("format-html.md") if a.html else ""
    # Claude's own message is the prompt. Only the read-only and language lines are added.
    text = f"{brief}{style}{fmt}{project_style()}\n\n{READ_ONLY_LINE} {LANGUAGE_LINE}"
    OUT.mkdir(parents=True, exist_ok=True)
    stem = f"{dt.date.today():%Y%m%d}-{re.sub(r'[^\w-]+', '-', a.slug).strip('-')}"
    md = OUT / (stem + (".html" if a.html else ".md"))
    env = agy(text, a)
    meta = {"file": md.name, "conversation_id": env.get("conversation_id"), "model": a.model, "style": a.style,
            "brief": brief, "log": [{"kind": "explain", "status": env["status"], "usage": env.get("usage")}]}
    md.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    if env["reply"]:
        md.write_text(env["reply"] + "\n", encoding="utf-8")
    print(json.dumps(summary(md, env), ensure_ascii=False, indent=1))
    return 0 if env["reply"] else 1


def cmd_say(a: argparse.Namespace) -> int:
    if a.new or not (a.file or any(OUT.glob("*.json"))):  # no explanation needed: start a fresh conversation
        OUT.mkdir(parents=True, exist_ok=True)
        md = OUT / f"{dt.date.today():%Y%m%d}-{time.strftime('%H%M%S')}-talk-start.md"
        meta = {"file": md.name, "conversation_id": None, "model": a.model, "log": []}
    else:
        md, meta = current(a)
    env = agy(a.message + ("\n\n" + READ_ONLY_LINE + " " + LANGUAGE_LINE
                           if not meta["conversation_id"] else ""), a, meta["conversation_id"])
    meta["conversation_id"] = meta["conversation_id"] or env.get("conversation_id")
    meta["log"].append({"kind": "say", "message": a.message, "status": env["status"], "usage": env.get("usage")})
    md.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    talk = md.with_name(md.stem + "-talk.md")
    if env["reply"]:
        with talk.open("a", encoding="utf-8") as f:
            f.write(f"**Claude → Gemini:** {a.message}\n\n**Gemini:** {env['reply']}\n\n---\n\n")
    print(json.dumps(summary(talk, env), ensure_ascii=False, indent=1))
    print("\n" + env["reply"])
    return 0 if env["reply"] else 1


def cmd_handoff(a: argparse.Namespace) -> int:
    md, meta = current(a)
    env = agy(read("handoff.md") + " " + LANGUAGE_LINE, a, meta["conversation_id"])
    meta["log"].append({"kind": "handoff", "status": env["status"], "usage": env.get("usage")})
    md.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    out = md.with_name(md.stem + "-handoff.md")
    if env["reply"]:
        out.write_text(env["reply"] + "\n", encoding="utf-8")
    print(json.dumps(summary(out, env), ensure_ascii=False, indent=1))
    return 0 if env["reply"] else 1


def cmd_doctor(_: argparse.Namespace) -> int:
    """Each check prints ok/FAIL and a fix. `/usage` is a slash command: it answers with no model turn."""
    def run(*args: str) -> tuple[int, str]:
        try:
            r = subprocess.run(["agy", *args], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=90)
            return r.returncode, (r.stdout + r.stderr).strip()
        except (OSError, subprocess.TimeoutExpired) as e:
            return -1, str(e)
    exe = shutil.which("agy")
    print(f"{'ok  ' if exe else 'FAIL'} agy: {exe or 'not found. Install: brew install --cask antigravity-cli'}")
    if not exe:
        return 1
    rc, out = run("--version")
    print(f"{'ok  ' if rc == 0 else 'FAIL'} version: {out.splitlines()[-1] if out else rc}")
    rc, out = run("-p", "/usage", "--output-format", "json")
    try:
        groups = json.loads(out.splitlines()[-1])["command"]["data"]["groups"]
    except (ValueError, KeyError, IndexError, TypeError):
        groups = None
    if not groups:
        print(f"FAIL sign-in: run `agy` once in a terminal and sign in with Google. ({out[-200:]})")
        return 1
    for g in groups:
        left = ", ".join(f"{b['window']} {round(b['remaining_fraction'] * 100)}%" for b in g.get("buckets", []))
        print(f"ok   quota {g['name']}: {left} left")
    rc, out = run("models")
    gemini = [line.split("\t")[0] for line in out.splitlines() if line.startswith("gemini-")]
    print(f"{'ok  ' if gemini else 'FAIL'} Gemini models: {', '.join(gemini) or 'none on this account'}")
    print(f"{'ok  ' if sys.version_info >= (3, 9) else 'FAIL'} python {sys.version.split()[0]} (needs 3.9+)")
    return 0 if gemini else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = argparse.ArgumentParser(add_help=False)
    c.add_argument("--model", help="agy model slug (see `models`)")
    c.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    c.add_argument("--timeout", type=int, default=25, help="minutes")
    c.add_argument("--file", help="explanation file to continue (default: newest)")
    e = sub.add_parser("explain", parents=[c])
    e.add_argument("--brief", required=True, help="file with Claude's message to Gemini, in its own words")
    e.add_argument("--slug", default="explain")
    e.add_argument("--style", default=None, help="optional; only when the human asks", choices=sorted(p.stem for p in (PROMPTS / "styles").glob("*.md")))
    e.add_argument("--html", action="store_true", help="a self-contained HTML page instead of Markdown")
    e.set_defaults(func=cmd_explain)
    s = sub.add_parser("say", parents=[c])
    s.add_argument("message")
    s.add_argument("--new", action="store_true", help="start a fresh conversation instead of continuing")
    s.set_defaults(func=cmd_say)
    sub.add_parser("handoff", parents=[c]).set_defaults(func=cmd_handoff)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    sub.add_parser("models").set_defaults(func=lambda _: subprocess.run(["agy", "models"], stdin=subprocess.DEVNULL).returncode)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
