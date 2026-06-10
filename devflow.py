#!/usr/bin/env python3
"""devflow.py — Devflow v2 rails: run state, gates, brief, ledger.

Single-file, stdlib-only. Ships at the repo root; `init` copies it into a
project's `.devflow/` directory (version-stamped — `doctor` detects skew).

Design: devflow-team/docs/plans/2026-06-10-v2-phase2-rails-design.md (D20-D24)
Spec:   devflow-team/docs/specs/2026-06-10-v2-phase2-rails.md (AC-1..AC-9)

Exit codes: 0 success/allow · 1 command error · 2 gate denial (reserved).
"""

import argparse
import json
import os
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

    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else resolve_root()

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
    except DevflowError as exc:
        print(f"devflow: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
