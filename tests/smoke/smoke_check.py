#!/usr/bin/env python3
"""smoke_check.py — assertion core of the Devflow prompt-regression harness.

Design (D30): prompts are non-deterministic, outcomes are not. This checker
asserts scenario POSTCONDITIONS — artifacts, phase journals, ledger records,
gate denials — against a manifest, and is therefore model-version-independent.
It never inspects model output. The execution transport (in-session subagent
or headless CLI) is someone else's job; this file must stay deterministic,
stdlib-only, and itself unit-tested (tests/test_smoke_check.py).

Usage:
    python tests/smoke/smoke_check.py --scenario tests/smoke/scenarios/fix-basic.json \
                                      --workspace /tmp/smoke-fix-basic

Exit codes: 0 all assertions pass · 1 any failure · 2 bad manifest/arguments.
"""

import argparse
import json
import re
import sys
from pathlib import Path


class SmokeError(Exception):
    """Manifest or invocation problem — reported readably, exit 2."""


# --- assertion implementations --------------------------------------------------
# Each takes (assertion_dict, workspace_path) and returns (ok, detail).

def _read_jsonl(path):
    if not Path(path).exists():
        return None
    records = []
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _a_file_exists(a, ws):
    p = ws / a["path"]
    return p.exists(), (str(p) if p.exists() else f"{a['path']} not found")


def _a_file_absent(a, ws):
    p = ws / a["path"]
    return not p.exists(), ("absent as expected" if not p.exists()
                            else f"{a['path']} unexpectedly exists")


def _a_file_contains(a, ws):
    p = ws / a["path"]
    if not p.exists():
        return False, f"{a['path']} missing — cannot match pattern"
    text = p.read_text(encoding="utf-8", errors="ignore")
    ok = re.search(a["pattern"], text) is not None
    return ok, (f"pattern /{a['pattern']}/ "
                + ("found" if ok else f"NOT found in {a['path']}"))


def _is_ordered_subsequence(expected, actual):
    """True when `expected` appears in `actual` in order, gaps allowed.
    The `item in iterator` idiom advances the iterator past each match —
    so duplicates in `expected` require duplicates in `actual`."""
    it = iter(actual)
    return all(item in it for item in expected)


def _a_state_phases(a, ws):
    records = _read_jsonl(ws / ".devflow" / "marks-log.jsonl")
    if records is None:
        return False, "marks-log.jsonl missing — no phases were marked"
    phases = [r.get("phase") for r in records]
    ok = _is_ordered_subsequence(a["expect"], phases)
    return ok, f"expected subsequence {a['expect']}, journal has {phases}"


def _a_ledger_record(a, ws):
    records = _read_jsonl(ws / ".devflow" / "runs.jsonl")
    if not records:
        return False, "runs.jsonl missing or empty — no run was finished"
    last = records[-1]
    wanted = {k: v for k, v in a.items() if k != "type"}
    mismatches = {k: (v, last.get(k)) for k, v in wanted.items()
                  if last.get(k) != v}
    ok = not mismatches
    return ok, ("last run record matches" if ok
                else f"mismatches (expected, actual): {mismatches}")


def _a_no_run_opened(a, ws):
    state = (ws / ".devflow" / "state.json").exists()
    ledger = _read_jsonl(ws / ".devflow" / "runs.jsonl") or []
    marks = _read_jsonl(ws / ".devflow" / "marks-log.jsonl") or []
    ok = not state and not ledger and not marks
    return ok, ("no run, as expected" if ok else
                f"unexpected activity: state={state}, "
                f"ledger={len(ledger)} record(s), marks={len(marks)}")


def _a_gate_denied_before_red(a, ws):
    denials = [r for r in (_read_jsonl(ws / ".devflow" / "gate-log.jsonl") or [])
               if r.get("rule") == "red-phase"]
    if not denials:
        return False, "no red-phase denial in gate-log.jsonl"
    marks = _read_jsonl(ws / ".devflow" / "marks-log.jsonl") or []
    reds = [r.get("at", "") for r in marks if r.get("phase") == "red-confirmed"]
    if not reds:
        return False, "red-confirmed never marked"
    # ISO-Z timestamps compare lexicographically.
    ok = any(d.get("at", "") <= reds[0] for d in denials)
    return ok, (f"{len(denials)} red-phase denial(s); first red at {reds[0]}"
                if ok else "denials all occurred after red-confirmed")


_ASSERTIONS = {
    "file_exists": (_a_file_exists, ("path",)),
    "file_absent": (_a_file_absent, ("path",)),
    "file_contains": (_a_file_contains, ("path", "pattern")),
    "state_phases": (_a_state_phases, ("expect",)),
    "ledger_record": (_a_ledger_record, ()),
    "no_run_opened": (_a_no_run_opened, ()),
    "gate_denied_before_red": (_a_gate_denied_before_red, ()),
}


# --- manifest loading -------------------------------------------------------------

def load_manifest_data(data):
    """Validate an already-parsed manifest dict. Raises SmokeError readably."""
    if not isinstance(data, dict) or not data.get("name"):
        raise SmokeError("manifest needs a non-empty 'name'")
    assertions = data.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        raise SmokeError(f"{data.get('name')}: 'assertions' must be a non-empty list")
    for i, a in enumerate(assertions):
        a_type = a.get("type")
        if a_type not in _ASSERTIONS:
            raise SmokeError(
                f"{data['name']}: assertion {i} has unknown type '{a_type}' "
                f"— known: {', '.join(sorted(_ASSERTIONS))}")
        for field in _ASSERTIONS[a_type][1]:
            if field not in a:
                raise SmokeError(
                    f"{data['name']}: assertion {i} ({a_type}) missing '{field}'")
    return data


def load_manifest(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SmokeError(f"cannot read manifest {path}: {exc}")
    return load_manifest_data(raw)


# --- runner ------------------------------------------------------------------------

def run_assertions(manifest, workspace):
    """[(description, ok, detail)] — one per assertion, never raises per-item."""
    ws = Path(workspace)
    results = []
    for a in manifest["assertions"]:
        fn = _ASSERTIONS[a["type"]][0]
        desc = a["type"] + (f" {a.get('path', a.get('expect', ''))}"
                            if a.get("path") or a.get("expect") else "")
        try:
            ok, detail = fn(a, ws)
        except Exception as exc:  # a broken assertion is a FAIL, not a crash
            ok, detail = False, f"assertion error: {exc.__class__.__name__}: {exc}"
        results.append((desc.strip(), ok, detail))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.scenario)
    except SmokeError as exc:
        print(f"smoke: {exc}", file=sys.stderr)
        return 2

    results = run_assertions(manifest, args.workspace)
    failed = 0
    for desc, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  [{manifest['name']}] {desc} — {detail}")
        failed += 0 if ok else 1
    print(f"[{manifest['name']}] {len(results) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
