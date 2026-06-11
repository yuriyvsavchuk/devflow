#!/usr/bin/env python3
"""devflow.py — Devflow v2 rails: run state, gates, brief, ledger.

Single-file, stdlib-only. Ships at the repo root; `init` copies it into a
project's `.devflow/` directory (version-stamped — `doctor` detects skew).

Design: devflow-team/docs/plans/2026-06-10-v2-phase2-rails-design.md (D20-D24)
Spec:   devflow-team/docs/specs/2026-06-10-v2-phase2-rails.md (AC-1..AC-9)

Exit codes: 0 success/allow · 1 command error · 2 gate denial (reserved).
"""

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "2.0.0"

# Phase sequences per playbook. Forward marks may skip optional phases;
# skipping "red-confirmed" is special-cased (see cmd_mark).
PHASES = {
    "fix":    ["started", "repro-confirmed", "red-confirmed", "fix-applied",
               "review-passed", "accepted"],
    "build":  ["started", "plan-confirmed", "contract-confirmed", "red-confirmed",
               "implemented", "review-passed", "accepted"],
    "shape":  ["started", "accepted"],
    "spike":  ["started", "accepted"],
    "audit":  ["started", "accepted"],
    "hotfix": ["started", "accepted"],
}

RED_PHASE = "red-confirmed"
RED_GATED = ("fix", "build")  # playbooks whose edit gate watches the RED phase


class DevflowError(Exception):
    """User-facing command error (exit 1)."""


# --- paths & state -------------------------------------------------------------

def devflow_dir(root):
    return Path(root) / ".devflow"


def state_path(root):
    return devflow_dir(root) / "state.json"


def ledger_path(root):
    return devflow_dir(root) / "runs.jsonl"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path, text):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_state(root):
    """Return the active run dict, or None. A corrupt file is quarantined."""
    sp = state_path(root)
    if not sp.exists():
        return None
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        quarantine = sp.with_suffix(".json.corrupt")
        try:
            os.replace(sp, quarantine)
        except OSError:
            pass
        return None


def save_state(root, state):
    _atomic_write(state_path(root), json.dumps(state, ensure_ascii=False, indent=2))


def _append_ledger(root, record):
    lp = ledger_path(root)
    lp.parent.mkdir(parents=True, exist_ok=True)
    with open(lp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# --- commands: run lifecycle ----------------------------------------------------

def cmd_start(root, playbook, tier="standard", task="", force=False):
    if playbook not in PHASES:
        raise DevflowError(
            f"unknown playbook '{playbook}' — one of: {', '.join(PHASES)}")
    if load_state(root) is not None:
        if not force:
            raise DevflowError(
                "a run is already active — `finish` it (or start --force to abandon it)")
        cmd_finish(root, abandoned=True)
    state = {
        "version": 1,
        "run_id": f"{playbook}-{datetime.now():%Y%m%d-%H%M%S}",
        "playbook": playbook,
        "tier": tier,
        "task": task,
        "started": _now(),
        "phase": "started",
        "marks": [],
        "loop_backs": 0,
    }
    devflow_dir(root).mkdir(parents=True, exist_ok=True)
    save_state(root, state)
    return state


def cmd_mark(root, phase, evidence=None, note=None, no_tdd_reason=None):
    state = load_state(root)
    if state is None:
        raise DevflowError("no active run — `start <playbook>` first")
    seq = PHASES[state["playbook"]]
    if phase not in seq:
        raise DevflowError(
            f"'{phase}' is not a phase of {state['playbook']} — one of: {', '.join(seq)}")

    cur_idx, new_idx = seq.index(state["phase"]), seq.index(phase)
    red_idx = seq.index(RED_PHASE) if RED_PHASE in seq else None

    # Skipping RED silently defeats the gate. fix: never; build: explicit exception.
    if (red_idx is not None and new_idx > red_idx
            and RED_PHASE not in (m["phase"] for m in state["marks"])
            and no_tdd_reason is None):
        if state["playbook"] == "fix":
            raise DevflowError(
                "fix runs cannot skip red-confirmed — write the failing regression test first")
        raise DevflowError(
            "skipping red-confirmed requires an explicit reason: --no-tdd \"<why>\"")

    if new_idx <= cur_idx:
        state["loop_backs"] += 1

    mark = {"phase": phase, "at": _now()}
    if evidence:
        mark["evidence"] = evidence
    if note:
        mark["note"] = note
    if no_tdd_reason:
        mark["no_tdd"] = no_tdd_reason
    state["marks"].append(mark)
    state["phase"] = phase
    save_state(root, state)
    return state


def cmd_finish(root, abandoned=False):
    state = load_state(root)
    if state is None:
        raise DevflowError("no active run to finish")
    record = {
        "run_id": state["run_id"],
        "playbook": state["playbook"],
        "tier": state["tier"],
        "task": state["task"],
        "started": state["started"],
        "finished": _now(),
        "status": "abandoned" if abandoned else "completed",
        "loop_backs": state["loop_backs"],
        "marks": len(state["marks"]),
    }
    _append_ledger(root, record)
    state_path(root).unlink()
    return record


# --- gate (PreToolUse hook) -------------------------------------------------------

DEFAULT_CONFIG = {
    "enabled": True,
    # Production = anything not excluded. fnmatch semantics: '*' crosses '/'.
    "production_globs": ["*"],
    "exclude_globs": ["tests/*", "test/*", "*test*", "docs/*", "*.md",
                      ".devflow/*", ".claude/*", "local/*", "specs/*"],
    "protected_paths": [],
    "brief_lines": 15,
}

_RED_DENY_MSG = (
    "Devflow gate: RED phase not confirmed for this {playbook} run. "
    "Write the failing test first, then run: "
    "python .devflow/devflow.py mark red-confirmed --evidence <test-path>. "
    "(Tests/docs are not gated; quick-tier runs are not gated.)"
)
_PROTECTED_DENY_MSG = (
    "Devflow gate: '{path}' is a PROTECTED path — human authorship required. "
    "Do not edit it; insert `TODO: [PROTECTED — human authorship required: <what>]` "
    "at the integration point and continue around it."
)


def load_config(root):
    cfg = dict(DEFAULT_CONFIG)
    cp = devflow_dir(root) / "config.json"
    if cp.exists():
        try:
            cfg.update(json.loads(cp.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # fail-open: defaults
    return cfg


def _relativize(file_path, root):
    """Project-relative posix path, or None when outside the project."""
    try:
        return Path(file_path).resolve().relative_to(Path(root).resolve()).as_posix()
    except (ValueError, OSError):
        return None


def _match_any(rel_path, patterns):
    return any(fnmatch.fnmatch(rel_path, pat) for pat in patterns)


def cmd_gate(root, raw_stdin):
    """Decide a PreToolUse call: (0, None) allow · (2, message) deny.

    Order per design D23: fail-open → protected paths → RED phase → allow.
    Any internal error allows (AC-8) — the gate must never break the harness.
    """
    try:
        cfg = load_config(root)
        if not cfg.get("enabled", True):
            return 0, None

        data = json.loads(raw_stdin)
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not file_path:
            return 0, None
        rel = _relativize(file_path, root)
        if rel is None:
            return 0, None  # outside the project — not ours to gate

        if _match_any(rel, cfg["protected_paths"]):
            return 2, _PROTECTED_DENY_MSG.format(path=rel)

        state = load_state(root)
        if state is None or state["playbook"] not in RED_GATED:
            return 0, None
        if state.get("tier") == "quick":
            return 0, None

        # The current-phase index alone decides: a --no-tdd exception moves the
        # phase past RED (cmd_mark validates the reason), and a loop-back to a
        # pre-RED phase re-arms the gate — old exceptions do not survive it.
        seq = PHASES[state["playbook"]]
        if seq.index(state["phase"]) >= seq.index(RED_PHASE):
            return 0, None

        if _match_any(rel, cfg["production_globs"]) and not _match_any(rel, cfg["exclude_globs"]):
            return 2, _RED_DENY_MSG.format(playbook=state["playbook"])
        return 0, None
    except Exception:
        return 0, None  # fail-open, always


# --- brief (SessionStart hook) + stop-check (Stop hook, advisory) -----------------

def cmd_brief(root):
    """Session orientation lines (AC-2). Every source tolerates absence."""
    lines = []
    try:
        if not devflow_dir(root).exists():
            return []
        cap = load_config(root).get("brief_lines", 15)

        state = load_state(root)
        if state:
            lines.append(
                f"[devflow] run {state['run_id']}: {state['playbook']} "
                f"({state['tier']}) at {state['phase']} — {state['task']}")
            try:
                started = datetime.strptime(
                    state["started"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                days = (datetime.now(timezone.utc) - started).days
                if days >= 7:
                    lines.append(f"[devflow] this run has been open for {days} days — "
                                 "finish it, or abandon it honestly")
            except Exception:
                pass
        else:
            lines.append("[devflow] no active run")

        try:
            debts = []
            for p in sorted((Path(root) / "docs" / "sessions").glob("hotfix-debt-*.md")):
                try:
                    head = p.read_text(encoding="utf-8", errors="ignore")[:400]
                    if re.search(r"^status:\s*open\b", head, re.M):
                        debts.append(p.name)
                except OSError:
                    continue
            if debts:
                shown = ", ".join(debts[:3]) + (
                    f" (+{len(debts) - 3} more)" if len(debts) > 3 else "")
                lines.append(f"[devflow] OPEN HOTFIX DEBT: {shown} — "
                             "owed: root-cause fix + regression test (devflow-fix)")
        except Exception:
            pass

        for rel, label in (("docs/decisions/index.md", "decisions"),
                           ("docs/interfaces/index.md", "interfaces")):
            try:
                p = Path(root) / rel
                if p.exists():
                    entries = [ln.strip()[2:].strip()
                               for ln in p.read_text(encoding="utf-8",
                                                     errors="ignore").splitlines()
                               if ln.strip().startswith("- ")]
                    if entries:
                        lines.append(f"[devflow] recent {label}: "
                                     + " | ".join(reversed(entries[-3:])))
            except Exception:
                pass

        return lines[:cap]
    except Exception:
        return lines[:15]


def cmd_stop_check(root):
    """Advisory-only Stop output (D23): a dict to print as JSON, or None."""
    try:
        state = load_state(root)
        if state is None or state.get("phase") == "accepted":
            return None
        return {"hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"[devflow] run {state['run_id']} is still open at phase "
                f"'{state['phase']}'. If the work is done, mark the remaining "
                "phases and `finish`; if pausing intentionally, this is fine."),
        }}
    except Exception:
        return None


# --- stats ---------------------------------------------------------------------

def cmd_stats(root):
    """Plain-text aggregates from the run ledger (AC-5)."""
    lp = ledger_path(root)
    records = []
    if lp.exists():
        for line in lp.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not records:
        return "no runs recorded yet"

    def minutes(rec):
        try:
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            return (datetime.strptime(rec["finished"], fmt)
                    - datetime.strptime(rec["started"], fmt)).total_seconds() / 60
        except (KeyError, ValueError):
            return None

    completed = sum(1 for r in records if r.get("status") == "completed")
    abandoned = sum(1 for r in records if r.get("status") == "abandoned")
    loop_backs = sum(r.get("loop_backs", 0) for r in records)
    durations = [m for m in (minutes(r) for r in records) if m is not None]

    by_playbook = {}
    for r in records:
        key = f"{r.get('playbook', '?')}/{r.get('tier', '?')}"
        by_playbook[key] = by_playbook.get(key, 0) + 1

    lines = [
        f"runs: {len(records)}  completed: {completed}  abandoned: {abandoned}",
        f"loop-backs: {loop_backs}",
    ]
    if durations:
        lines.append(f"mean duration: {sum(durations) / len(durations):.1f} min")
    lines.append("by playbook/tier:")
    for key in sorted(by_playbook):
        lines.append(f"  {key}: {by_playbook[key]}")
    return "\n".join(lines)


# --- init + doctor -----------------------------------------------------------------

_HOOK_CMD = 'python "$CLAUDE_PROJECT_DIR/.devflow/devflow.py" {cmd}'
HOOK_WIRING = (
    ("SessionStart", "startup|resume|compact", "brief"),
    ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit", "gate"),
    ("Stop", None, "stop-check"),
)
# Note: user projects commit .devflow/devflow.py as their pinned copy — only the
# framework repo itself additionally ignores it (added by hand in its .gitignore).
_GITIGNORE_LINES = (".devflow/state.json", ".devflow/state.json.corrupt",
                    ".devflow/runs.jsonl")


def cmd_init(root):
    """Scaffold .devflow/, copy self, wire hooks merge-safe + idempotent (AC-1)."""
    root = Path(root)
    summary = []
    dd = devflow_dir(root)
    dd.mkdir(parents=True, exist_ok=True)

    cfg_path = dd / "config.json"
    if not cfg_path.exists():
        _atomic_write(cfg_path, json.dumps(DEFAULT_CONFIG, indent=2) + "\n")
        summary.append("config.json created (defaults)")

    src = Path(__file__).resolve()
    dest = dd / "devflow.py"
    if src != dest.resolve():
        _atomic_write(dest, src.read_text(encoding="utf-8"))
        summary.append(f"devflow.py {VERSION} copied into .devflow/")

    sp = root / ".claude" / "settings.json"
    sp.parent.mkdir(parents=True, exist_ok=True)
    original_text = sp.read_text(encoding="utf-8") if sp.exists() else None
    try:
        settings = json.loads(original_text) if original_text else {}
    except json.JSONDecodeError:
        raise DevflowError(f"{sp} is not valid JSON — fix it before init")
    hooks = settings.setdefault("hooks", {})
    modified = False
    try:
        for event, matcher, cmd in HOOK_WIRING:
            entries = hooks.setdefault(event, [])
            cmd_str = _HOOK_CMD.format(cmd=cmd)
            wired = any(h.get("command") == cmd_str
                        for entry in entries for h in entry.get("hooks", []))
            if not wired:
                entry = {"hooks": [{"type": "command", "command": cmd_str,
                                    "timeout": 10}]}
                if matcher:
                    entry["matcher"] = matcher
                entries.append(entry)
                modified = True
    except (AttributeError, TypeError):
        raise DevflowError(
            f"{sp} has an unexpected hooks structure (an event's value must be "
            "a list of matcher entries) — fix it before init")
    if modified:
        bak = sp.with_suffix(".json.bak")
        if original_text is not None and not bak.exists():
            bak.write_text(original_text, encoding="utf-8")
        _atomic_write(sp, json.dumps(settings, indent=2) + "\n")
        summary.append("hooks wired into .claude/settings.json"
                       + (" (backup: settings.json.bak)" if original_text else ""))

    gi = root / ".gitignore"
    gi_text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    existing_lines = {ln.strip() for ln in gi_text.splitlines()}
    missing = [ln for ln in _GITIGNORE_LINES if ln not in existing_lines]
    if missing:
        if gi_text and not gi_text.endswith("\n"):
            gi_text += "\n"
        gi_text += "\n".join(missing) + "\n"
        _atomic_write(gi, gi_text)
        summary.append(".gitignore updated (state + ledger stay local)")

    return summary or ["already initialized — nothing to do"]


def _bash_version(path):
    return subprocess.run([path, "--version"], capture_output=True, text=True,
                          timeout=5).stdout


def _git_bash_candidates():
    """bash on PATH plus bash inside the Git for Windows install dir —
    Claude Code uses Git Bash even when WSL's bash shadows it on PATH."""
    out = []
    b = shutil.which("bash")
    if b:
        out.append(str(Path(b)))
    g = shutil.which("git")
    if g:
        groot = Path(g).resolve().parent
        for rel in ("../bin/bash.exe", "../usr/bin/bash.exe",
                    "../../bin/bash.exe", "../../usr/bin/bash.exe"):
            c = (groot / rel).resolve()
            if c.exists() and str(c) not in out:
                out.append(str(c))
    return out


def _bash_check(platform=None, candidates=None, version_runner=None):
    """(ok, detail): is a Git Bash (msys/mingw) available for hook execution?
    WSL's bash is not it — it resolves paths against the Linux filesystem."""
    platform = platform or sys.platform
    if platform != "win32":
        return True, "POSIX shell"
    cands = candidates if candidates is not None else _git_bash_candidates()
    if not cands:
        return False, "bash not found — install Git for Windows"
    probe = version_runner or _bash_version
    non_git = None
    for cand in cands:
        try:
            out = probe(cand).lower()
        except Exception:
            continue
        if "msys" in out or "mingw" in out:
            return True, cand
        non_git = cand
    return False, (f"{non_git or cands[0]} is not Git Bash (WSL?) — "
                   "install Git for Windows")


def cmd_doctor(root):
    """Install health checks: list of (name, ok, detail) (AC-6)."""
    root = Path(root)
    checks = []

    checks.append(("python", True, sys.executable))
    bash_ok, bash_detail = _bash_check()
    checks.append(("bash (hook shell on Windows)", bash_ok, bash_detail))

    dd = devflow_dir(root)
    try:
        dd.mkdir(parents=True, exist_ok=True)
        probe = dd / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append((".devflow writable", True, str(dd)))
    except OSError as exc:
        checks.append((".devflow writable", False, repr(exc)))

    try:
        load_config(root)
        checks.append(("config parses", True, str(dd / "config.json")))
    except Exception as exc:  # load_config is fail-open; belt-and-suspenders
        checks.append(("config parses", False, repr(exc)))

    sp = root / ".claude" / "settings.json"
    wired = False
    if sp.exists():
        try:
            settings = json.loads(sp.read_text(encoding="utf-8"))
            commands = {h.get("command")
                        for entries in settings.get("hooks", {}).values()
                        for entry in entries for h in entry.get("hooks", [])}
            wired = all(_HOOK_CMD.format(cmd=cmd) in commands
                        for _, _, cmd in HOOK_WIRING)
        except (OSError, json.JSONDecodeError):
            wired = False
    checks.append(("hooks wired", wired,
                   str(sp) if wired else "missing hooks — run init"))

    copy = dd / "devflow.py"
    if copy.exists():
        m = re.search(r'^VERSION = "([^"]+)"', copy.read_text(encoding="utf-8"),
                      re.M)
        copy_ver = m.group(1) if m else "unknown"
        checks.append(("version match", copy_ver == VERSION,
                       f"copy={copy_ver} running={VERSION}"
                       + ("" if copy_ver == VERSION else " — run init to upgrade")))
    else:
        checks.append(("version match", False, "no .devflow/devflow.py — run init"))

    return checks


# --- CLI -------------------------------------------------------------------------

def resolve_root():
    env = os.environ.get("DEVFLOW_ROOT")
    if env:
        return Path(env)
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == ".devflow":
        return script_dir.parent
    return Path.cwd()


def main(argv=None):
    # argparse exits 2 on bad arguments — in a PreToolUse hook the harness would
    # read that as a deliberate denial. Hook command strings are fixed by init,
    # so this cannot fire from wired hooks; keep it that way.
    parser = argparse.ArgumentParser(prog="devflow", description=__doc__)
    parser.add_argument("--root", default=None, help="project root (default: auto)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start", help="open a run")
    p.add_argument("playbook", choices=sorted(PHASES))
    p.add_argument("--tier", default="standard", choices=["quick", "standard", "full"])
    p.add_argument("--task", default="")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("mark", help="advance/record a phase")
    p.add_argument("phase")
    p.add_argument("--evidence")
    p.add_argument("--note")
    p.add_argument("--no-tdd", dest="no_tdd_reason", metavar="REASON")

    p = sub.add_parser("finish", help="close the run into the ledger")
    p.add_argument("--abandoned", action="store_true")

    sub.add_parser("gate", help="PreToolUse hook: read payload on stdin, exit 0/2")
    sub.add_parser("brief", help="SessionStart hook: print orientation lines")
    sub.add_parser("stop-check", help="Stop hook: advisory JSON when a run is open")
    sub.add_parser("init", help="scaffold .devflow/ and wire hooks (merge-safe)")
    sub.add_parser("doctor", help="install health checks")
    sub.add_parser("stats", help="aggregates from the run ledger")

    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else resolve_root()

    if args.command == "gate":
        code, message = cmd_gate(root, sys.stdin.read())
        if message:
            print(message, file=sys.stderr)
        return code
    if args.command == "brief":
        lines = cmd_brief(root)
        if lines:
            print("\n".join(lines))
        return 0
    if args.command == "stop-check":
        out = cmd_stop_check(root)
        if out:
            print(json.dumps(out, ensure_ascii=False))
        return 0

    try:
        if args.command == "start":
            st = cmd_start(root, args.playbook, tier=args.tier, task=args.task,
                           force=args.force)
            print(f"run {st['run_id']} started ({st['playbook']}, {st['tier']})")
        elif args.command == "mark":
            st = cmd_mark(root, args.phase, evidence=args.evidence, note=args.note,
                          no_tdd_reason=args.no_tdd_reason)
            print(f"phase: {st['phase']} (loop-backs: {st['loop_backs']})")
        elif args.command == "finish":
            rec = cmd_finish(root, abandoned=args.abandoned)
            print(f"run {rec['run_id']} {rec['status']} "
                  f"({rec['marks']} marks, {rec['loop_backs']} loop-backs)")
        elif args.command == "init":
            for line in cmd_init(root):
                print(line)
        elif args.command == "doctor":
            checks = cmd_doctor(root)
            for name, ok, detail in checks:
                print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
            return 0 if all(ok for _, ok, _ in checks) else 1
        elif args.command == "stats":
            print(cmd_stats(root))
    except DevflowError as exc:
        print(f"devflow: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
