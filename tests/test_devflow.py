"""Tests for devflow.py — state core (Phase 2, Task 2).

Run:  python -m unittest discover tests -v   (from the repo root)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import devflow  # noqa: E402


class StateCoreBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".devflow").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def read_state(self):
        return json.loads((self.root / ".devflow" / "state.json").read_text(encoding="utf-8"))

    def ledger_lines(self):
        p = self.root / ".devflow" / "runs.jsonl"
        if not p.exists():
            return []
        return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestStart(StateCoreBase):
    def test_start_creates_state(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="null deref in parser")
        st = self.read_state()
        self.assertEqual(st["playbook"], "fix")
        self.assertEqual(st["tier"], "standard")
        self.assertEqual(st["phase"], "started")
        self.assertEqual(st["loop_backs"], 0)
        self.assertEqual(st["task"], "null deref in parser")
        self.assertTrue(st["run_id"].startswith("fix-"))
        self.assertIn("started", st)
        self.assertEqual(st["version"], 1)

    def test_start_refuses_second_run(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="a")
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_start(self.root, "build", tier="standard", task="b")

    def test_start_force_abandons_previous(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="a")
        devflow.cmd_start(self.root, "build", tier="quick", task="b", force=True)
        lines = self.ledger_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["status"], "abandoned")
        self.assertEqual(lines[0]["playbook"], "fix")
        self.assertEqual(self.read_state()["playbook"], "build")

    def test_start_unknown_playbook_rejected(self):
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_start(self.root, "deploy", tier="standard", task="x")


class TestMark(StateCoreBase):
    def test_mark_forward(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed", evidence="repro.md")
        devflow.cmd_mark(self.root, "red-confirmed", evidence="tests/test_x.py")
        st = self.read_state()
        self.assertEqual(st["phase"], "red-confirmed")
        self.assertEqual(st["loop_backs"], 0)
        self.assertEqual(len(st["marks"]), 2)
        self.assertEqual(st["marks"][1]["evidence"], "tests/test_x.py")

    def test_mark_backward_increments_loopback(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        devflow.cmd_mark(self.root, "fix-applied")
        devflow.cmd_mark(self.root, "red-confirmed")  # loop back after review feedback
        st = self.read_state()
        self.assertEqual(st["phase"], "red-confirmed")
        self.assertEqual(st["loop_backs"], 1)

    def test_mark_unknown_phase_rejected(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_mark(self.root, "shipped")

    def test_mark_without_run_rejected(self):
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_mark(self.root, "red-confirmed")

    def test_fix_cannot_skip_red(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_mark(self.root, "fix-applied")  # red-confirmed never marked

    def test_build_skip_red_requires_no_tdd_reason(self):
        devflow.cmd_start(self.root, "build", tier="standard", task="t")
        devflow.cmd_mark(self.root, "plan-confirmed")
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_mark(self.root, "implemented")  # silent skip of red
        devflow.cmd_mark(self.root, "implemented", no_tdd_reason="exploratory after spike")
        st = self.read_state()
        self.assertEqual(st["phase"], "implemented")
        self.assertEqual(st["marks"][-1]["no_tdd"], "exploratory after spike")


class TestFinish(StateCoreBase):
    def test_finish_writes_single_ledger_line_and_clears_state(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        devflow.cmd_mark(self.root, "fix-applied")
        devflow.cmd_mark(self.root, "review-passed")
        devflow.cmd_mark(self.root, "accepted")
        devflow.cmd_finish(self.root)
        lines = self.ledger_lines()
        self.assertEqual(len(lines), 1)
        rec = lines[0]
        self.assertEqual(rec["status"], "completed")
        self.assertEqual(rec["playbook"], "fix")
        self.assertEqual(rec["tier"], "standard")
        self.assertEqual(rec["loop_backs"], 0)
        self.assertEqual(rec["marks"], 5)
        self.assertIn("finished", rec)
        self.assertFalse((self.root / ".devflow" / "state.json").exists())

    def test_finish_abandoned_status(self):
        devflow.cmd_start(self.root, "spike", tier="quick", task="t")
        devflow.cmd_finish(self.root, abandoned=True)
        self.assertEqual(self.ledger_lines()[0]["status"], "abandoned")

    def test_finish_without_run_rejected(self):
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_finish(self.root)

    def test_two_runs_two_ledger_lines(self):
        devflow.cmd_start(self.root, "spike", tier="quick", task="a")
        devflow.cmd_finish(self.root)
        devflow.cmd_start(self.root, "audit", tier="standard", task="b")
        devflow.cmd_finish(self.root)
        self.assertEqual(len(self.ledger_lines()), 2)


class TestEvidenceJournals(StateCoreBase):
    """Phase 4: marks and gate denials must leave durable evidence that
    survives `finish` — the smoke harness asserts on these journals."""

    def test_marks_journal_survives_finish(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        devflow.cmd_mark(self.root, "fix-applied")
        devflow.cmd_mark(self.root, "review-passed")
        devflow.cmd_mark(self.root, "accepted")
        devflow.cmd_finish(self.root)
        jp = self.root / ".devflow" / "marks-log.jsonl"
        self.assertTrue(jp.exists())
        entries = [json.loads(l) for l in jp.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([e["phase"] for e in entries],
                         ["repro-confirmed", "red-confirmed", "fix-applied",
                          "review-passed", "accepted"])
        self.assertTrue(all("run_id" in e and "at" in e for e in entries))

    def test_gate_denial_logged_with_rule(self):
        cfg = dict(devflow.DEFAULT_CONFIG)
        cfg["protected_paths"] = ["secret/*"]
        (self.root / ".devflow" / "config.json").write_text(
            json.dumps(cfg), encoding="utf-8")
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        payload = lambda p: json.dumps({"tool_name": "Write",
                                        "tool_input": {"file_path": str(p)},
                                        "cwd": str(self.root)})
        code, _ = devflow.cmd_gate(self.root, payload(self.root / "src" / "a.py"))
        self.assertEqual(code, 2)
        code, _ = devflow.cmd_gate(self.root, payload(self.root / "secret" / "k.pem"))
        self.assertEqual(code, 2)
        gp = self.root / ".devflow" / "gate-log.jsonl"
        entries = [json.loads(l) for l in gp.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([e["rule"] for e in entries], ["red-phase", "protected"])
        self.assertIn("a.py", entries[0]["path"])

    def test_gate_allow_writes_no_log(self):
        devflow.cmd_start(self.root, "fix", tier="quick", task="t")
        payload = json.dumps({"tool_name": "Write",
                              "tool_input": {"file_path": str(self.root / "x.py")},
                              "cwd": str(self.root)})
        code, _ = devflow.cmd_gate(self.root, payload)
        self.assertEqual(code, 0)
        self.assertFalse((self.root / ".devflow" / "gate-log.jsonl").exists())


class TestStateRobustness(StateCoreBase):
    def test_save_load_roundtrip_unicode(self):
        devflow.cmd_start(self.root, "shape", tier="standard", task="зробити пошук — résumé")
        self.assertEqual(self.read_state()["task"], "зробити пошук — résumé")

    def test_corrupt_state_quarantined(self):
        sp = self.root / ".devflow" / "state.json"
        sp.write_text("{not json", encoding="utf-8")
        st = devflow.load_state(self.root)
        self.assertIsNone(st)
        self.assertFalse(sp.exists())
        self.assertTrue((self.root / ".devflow" / "state.json.corrupt").exists())

    def test_load_state_absent_returns_none(self):
        self.assertIsNone(devflow.load_state(self.root))


class GateBase(StateCoreBase):
    """Gate tests feed cmd_gate the same JSON the spike captured from the harness."""

    def payload(self, file_path, tool="Write"):
        return json.dumps({
            "session_id": "t", "hook_event_name": "PreToolUse",
            "tool_name": tool, "tool_input": {"file_path": str(file_path)},
            "cwd": str(self.root), "permission_mode": "acceptEdits",
        })

    def write_config(self, **overrides):
        cfg = dict(devflow.DEFAULT_CONFIG)
        cfg.update(overrides)
        (self.root / ".devflow" / "config.json").write_text(
            json.dumps(cfg), encoding="utf-8")

    def gate(self, file_path, tool="Write"):
        return devflow.cmd_gate(self.root, self.payload(file_path, tool))


class TestGateProtectedPaths(GateBase):
    def test_protected_path_denied_without_any_run(self):
        self.write_config(protected_paths=["src/auth/*"])
        code, msg = self.gate(self.root / "src" / "auth" / "login.py")
        self.assertEqual(code, 2)
        self.assertIn("PROTECTED", msg)
        self.assertIn("human authorship", msg)

    def test_protected_path_denied_even_after_red(self):
        self.write_config(protected_paths=["src/auth/*"])
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        code, _ = self.gate(self.root / "src" / "auth" / "login.py")
        self.assertEqual(code, 2)

    def test_unprotected_sibling_allowed(self):
        self.write_config(protected_paths=["src/auth/*"])
        code, _ = self.gate(self.root / "src" / "billing" / "x.py")
        self.assertEqual(code, 0)


class TestGateRedPhase(GateBase):
    def setUp(self):
        super().setUp()
        self.write_config()

    def test_pre_red_production_edit_denied(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        code, msg = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 2)
        self.assertIn("red", msg.lower())
        self.assertIn("mark red-confirmed", msg)

    def test_post_red_allowed(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_quick_tier_not_gated(self):
        devflow.cmd_start(self.root, "fix", tier="quick", task="t")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_tests_and_docs_excluded(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        for p in [self.root / "tests" / "test_app.py", self.root / "notes.md",
                  self.root / "docs" / "spec.txt"]:
            code, _ = self.gate(p)
            self.assertEqual(code, 0, f"should be excluded: {p}")

    def test_no_run_allows(self):
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_non_gated_playbook_allows(self):
        devflow.cmd_start(self.root, "shape", tier="standard", task="t")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_build_no_tdd_exception_opens_gate(self):
        devflow.cmd_start(self.root, "build", tier="standard", task="t")
        devflow.cmd_mark(self.root, "plan-confirmed")
        devflow.cmd_mark(self.root, "implemented", no_tdd_reason="post-spike")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_loop_back_before_red_re_arms_gate(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_mark(self.root, "repro-confirmed")
        devflow.cmd_mark(self.root, "red-confirmed")
        devflow.cmd_mark(self.root, "repro-confirmed")  # loop back before red
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 2)

    def test_no_tdd_exception_re_arms_after_loop_back(self):
        """Review finding: a loop-back to a pre-red phase invalidates the
        earlier --no-tdd exception — the gate must re-arm."""
        devflow.cmd_start(self.root, "build", tier="standard", task="t")
        devflow.cmd_mark(self.root, "plan-confirmed")
        devflow.cmd_mark(self.root, "implemented", no_tdd_reason="post-spike")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)  # exception in effect
        devflow.cmd_mark(self.root, "plan-confirmed", no_tdd_reason="rework")
        code, msg = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 2)  # re-armed
        self.assertIn("red", msg.lower())

    def test_gate_notebook_path(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        payload = json.dumps({"tool_name": "NotebookEdit",
                              "tool_input": {"notebook_path":
                                             str(self.root / "src" / "nb.ipynb")},
                              "cwd": str(self.root)})
        code, _ = devflow.cmd_gate(self.root, payload)
        self.assertEqual(code, 2)

    def test_gate_null_config_values_fail_open(self):
        self.write_config(enabled=None, protected_paths=["*"])
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)  # enabled=null -> disabled
        self.write_config(protected_paths=None)
        devflow.cmd_start(self.root, "shape", tier="standard", task="t")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)  # null list -> fail-open, no crash


class TestGateFailOpen(GateBase):
    def test_malformed_stdin_allows(self):
        code, _ = devflow.cmd_gate(self.root, "{this is not json")
        self.assertEqual(code, 0)

    def test_disabled_config_allows_everything(self):
        self.write_config(enabled=False, protected_paths=["*"])
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        code, _ = self.gate(self.root / "src" / "app.py")
        self.assertEqual(code, 0)

    def test_missing_devflow_dir_allows(self):
        with tempfile.TemporaryDirectory() as bare:
            payload = json.dumps({"tool_name": "Write",
                                  "tool_input": {"file_path": str(Path(bare) / "a.py")},
                                  "cwd": bare})
            code, _ = devflow.cmd_gate(Path(bare), payload)
            self.assertEqual(code, 0)

    def test_path_outside_root_allows(self):
        self.write_config(protected_paths=["*"])
        code, _ = self.gate(Path(self._tmp.name).parent / "elsewhere" / "x.py")
        self.assertEqual(code, 0)

    def test_payload_without_file_path_allows(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        code, _ = devflow.cmd_gate(self.root, json.dumps(
            {"tool_name": "Write", "tool_input": {}, "cwd": str(self.root)}))
        self.assertEqual(code, 0)


class TestBrief(StateCoreBase):
    def write_debt(self, slug, status):
        d = self.root / "docs" / "sessions"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"hotfix-debt-{slug}.md").write_text(
            f"---\ntype: hotfix-debt\nstatus: {status}\ndate: 2026-06-10\n---\n\n# Hotfix: {slug}\n",
            encoding="utf-8")

    def write_index(self, rel, entries):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Index\n\n" + "\n".join(f"- {e}" for e in entries) + "\n",
                     encoding="utf-8")

    def test_brief_with_everything(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="parser bug")
        devflow.cmd_mark(self.root, "repro-confirmed")
        self.write_debt("checkout-500s", "open")
        self.write_debt("old-one", "closed")
        self.write_index("docs/decisions/index.md", ["0001 a", "0002 b", "0003 c", "0004 d"])
        self.write_index("docs/interfaces/index.md", ["users-api v2"])
        lines = devflow.cmd_brief(self.root)
        text = "\n".join(lines)
        self.assertLessEqual(len(lines), devflow.DEFAULT_CONFIG["brief_lines"])
        self.assertIn("fix", text)
        self.assertIn("repro-confirmed", text)
        self.assertIn("checkout-500s", text)
        self.assertNotIn("old-one", text)          # closed debt not shown
        self.assertIn("0004 d", text)               # newest decision shown
        self.assertNotIn("0001 a", text)            # older than last 3 not shown
        self.assertIn("users-api v2", text)

    def test_brief_tolerates_total_absence(self):
        bare_lines = devflow.cmd_brief(self.root)   # .devflow exists, nothing else
        self.assertIsInstance(bare_lines, list)
        with tempfile.TemporaryDirectory() as bare:
            self.assertEqual(devflow.cmd_brief(Path(bare)), [])  # no .devflow at all

    def test_brief_stale_run_nudge(self):
        devflow.cmd_start(self.root, "build", tier="standard", task="t")
        st = devflow.load_state(self.root)
        st["started"] = "2026-05-01T00:00:00Z"
        devflow.save_state(self.root, st)
        text = "\n".join(devflow.cmd_brief(self.root))
        self.assertIn("open for", text)

    def test_brief_never_raises_on_garbage_sources(self):
        (self.root / "docs" / "sessions").mkdir(parents=True)
        (self.root / "docs" / "sessions" / "hotfix-debt-x.md").write_bytes(b"\xff\xfe garbage")
        lines = devflow.cmd_brief(self.root)
        self.assertIsInstance(lines, list)


class TestStopCheck(StateCoreBase):
    def test_open_run_yields_advisory(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        out = devflow.cmd_stop_check(self.root)
        self.assertIsNotNone(out)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "Stop")
        self.assertIn("open", out["hookSpecificOutput"]["additionalContext"])

    def test_advisory_debounced_within_an_hour(self):
        """Live finding: each advisory re-invokes the model -> nudge loop.
        Only the first stop in an hour may nudge."""
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        first = devflow.cmd_stop_check(self.root)
        self.assertIsNotNone(first)
        second = devflow.cmd_stop_check(self.root)
        self.assertIsNone(second)

    def test_advisory_returns_after_debounce_window(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="t")
        devflow.cmd_stop_check(self.root)
        st = devflow.load_state(self.root)
        st["stop_nudged_epoch"] = st["stop_nudged_epoch"] - 3700
        devflow.save_state(self.root, st)
        self.assertIsNotNone(devflow.cmd_stop_check(self.root))

    def test_accepted_run_silent(self):
        devflow.cmd_start(self.root, "spike", tier="quick", task="t")
        devflow.cmd_mark(self.root, "accepted")
        self.assertIsNone(devflow.cmd_stop_check(self.root))

    def test_no_run_silent(self):
        self.assertIsNone(devflow.cmd_stop_check(self.root))


class TestInitDoctor(unittest.TestCase):
    """init starts from a bare project root — no pre-made .devflow."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def settings(self):
        return json.loads(
            (self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))

    def test_init_scaffolds_everything(self):
        devflow.cmd_init(self.root)
        self.assertTrue((self.root / ".devflow" / "devflow.py").exists())
        cfg = json.loads(
            (self.root / ".devflow" / "config.json").read_text(encoding="utf-8"))
        self.assertTrue(cfg["enabled"])
        hooks = self.settings()["hooks"]
        for event in ("SessionStart", "PreToolUse", "Stop"):
            self.assertIn(event, hooks)
        pre = hooks["PreToolUse"][0]
        self.assertEqual(pre["matcher"], "Edit|Write|MultiEdit|NotebookEdit")
        self.assertIn(".devflow/devflow.py", pre["hooks"][0]["command"])
        self.assertEqual(hooks["SessionStart"][0]["matcher"], "startup|resume|compact")

    def test_init_preserves_existing_settings_and_is_idempotent(self):
        sp = self.root / ".claude" / "settings.json"
        sp.parent.mkdir(parents=True)
        pre_existing = {
            "permissions": {"allow": ["Bash(npm:*)"]},
            "hooks": {"PreToolUse": [
                {"matcher": "Bash",
                 "hooks": [{"type": "command", "command": "echo custom"}]}]},
        }
        sp.write_text(json.dumps(pre_existing, indent=2), encoding="utf-8")

        devflow.cmd_init(self.root)
        merged = self.settings()
        self.assertEqual(merged["permissions"]["allow"], ["Bash(npm:*)"])
        pre_entries = merged["hooks"]["PreToolUse"]
        self.assertEqual(len(pre_entries), 2)  # custom + ours
        self.assertEqual(pre_entries[0]["hooks"][0]["command"], "echo custom")
        self.assertTrue((self.root / ".claude" / "settings.json.bak").exists())
        bak = json.loads((self.root / ".claude" / "settings.json.bak").read_text(
            encoding="utf-8"))
        self.assertNotIn("SessionStart", bak.get("hooks", {}))

        first = sp.read_text(encoding="utf-8")
        devflow.cmd_init(self.root)  # second run
        self.assertEqual(sp.read_text(encoding="utf-8"), first)  # byte-identical

    def test_init_gitignore_append_without_duplicates(self):
        (self.root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        devflow.cmd_init(self.root)
        devflow.cmd_init(self.root)
        gi_lines = (self.root / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("node_modules/", gi_lines)
        self.assertEqual(gi_lines.count(".devflow/state.json"), 1)
        self.assertEqual(gi_lines.count(".devflow/runs.jsonl"), 1)

    def test_init_creates_gitignore_when_absent(self):
        devflow.cmd_init(self.root)
        gi = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".devflow/state.json", gi)

    def test_init_does_not_overwrite_user_config(self):
        (self.root / ".devflow").mkdir()
        (self.root / ".devflow" / "config.json").write_text(
            json.dumps({"enabled": False}), encoding="utf-8")
        devflow.cmd_init(self.root)
        cfg = json.loads(
            (self.root / ".devflow" / "config.json").read_text(encoding="utf-8"))
        self.assertFalse(cfg["enabled"])

    def test_doctor_all_pass_after_init(self):
        devflow.cmd_init(self.root)
        checks = devflow.cmd_doctor(self.root)
        failures = [c for c in checks if not c[1]]
        self.assertEqual(failures, [], f"doctor failures: {failures}")

    def test_doctor_detects_version_skew(self):
        devflow.cmd_init(self.root)
        copy = self.root / ".devflow" / "devflow.py"
        copy.write_text(copy.read_text(encoding="utf-8").replace(
            f'VERSION = "{devflow.VERSION}"', 'VERSION = "0.0.1"'), encoding="utf-8")
        checks = dict((c[0], c[1]) for c in devflow.cmd_doctor(self.root))
        self.assertFalse(checks["version match"])

    def test_doctor_detects_missing_hooks(self):
        devflow.cmd_init(self.root)
        (self.root / ".claude" / "settings.json").unlink()
        checks = dict((c[0], c[1]) for c in devflow.cmd_doctor(self.root))
        self.assertFalse(checks["hooks wired"])

    def test_init_rejects_malformed_hooks_value(self):
        """Review finding: a string where a hooks list belongs must raise a
        readable DevflowError, not an AttributeError."""
        sp = self.root / ".claude" / "settings.json"
        sp.parent.mkdir(parents=True)
        sp.write_text(json.dumps({"hooks": {"PreToolUse": "bad_string"}}),
                      encoding="utf-8")
        with self.assertRaises(devflow.DevflowError):
            devflow.cmd_init(self.root)


class TestBashCheck(unittest.TestCase):
    """Review finding: WSL's bash on PATH must not produce a false PASS,
    and Git Bash reachable via git's install dir must not produce a false FAIL."""

    WSL = "GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)"
    GIT = "GNU bash, version 5.2.26(1)-release (x86_64-pc-msys)"

    def test_wsl_bash_rejected(self):
        ok, detail = devflow._bash_check(
            platform="win32", candidates=[r"C:\WINDOWS\system32\bash.EXE"],
            version_runner=lambda p: self.WSL)
        self.assertFalse(ok)
        self.assertIn("Git", detail)

    def test_git_bash_accepted_even_when_wsl_first(self):
        cands = [r"C:\WINDOWS\system32\bash.EXE", r"C:\Program Files\Git\bin\bash.exe"]
        ok, detail = devflow._bash_check(
            platform="win32", candidates=cands,
            version_runner=lambda p: self.WSL if "system32" in p.lower() else self.GIT)
        self.assertTrue(ok)
        self.assertIn("Git", detail)

    def test_no_bash_fails(self):
        ok, _ = devflow._bash_check(platform="win32", candidates=[])
        self.assertFalse(ok)

    def test_posix_passes(self):
        ok, _ = devflow._bash_check(platform="linux", candidates=[])
        self.assertTrue(ok)

    def test_probe_exception_is_not_crash(self):
        def boom(_path):
            raise OSError("not found")
        ok, _ = devflow._bash_check(platform="win32",
                                    candidates=[r"C:\ghost\bash.exe"],
                                    version_runner=boom)
        self.assertFalse(ok)


class VerifyBase(StateCoreBase):
    """Phase 3: verify chain tests. findings = [(check, msg)], notes = [(check, reason)]."""

    def write_spec(self, name, status="agreed", acs=(1, 2)):
        d = self.root / "docs" / "specs"
        d.mkdir(parents=True, exist_ok=True)
        ac_lines = "\n".join(f"- AC-{n}: criterion {n}" for n in acs)
        (d / name).write_text(
            f"---\ntype: spec\nstatus: {status}\ndate: 2026-06-11\n---\n\n"
            f"# Spec {name}\n\n## Acceptance criteria\n{ac_lines}\n",
            encoding="utf-8")

    def write_plan(self, name, spec_ref, ac_refs):
        d = self.root / "docs" / "plans"
        d.mkdir(parents=True, exist_ok=True)
        refs = " and ".join(f"AC-{n}" for n in ac_refs)
        (d / name).write_text(
            f"# Plan {name}\n\nPer spec docs/specs/{spec_ref} this covers {refs}.\n",
            encoding="utf-8")

    def run_verify(self, **kw):
        return devflow.cmd_verify(self.root, **kw)

    def findings_for(self, check, findings):
        return [m for c, m in findings if c == check]

    def notes_for(self, check, notes):
        return [m for c, m in notes if c == check]


class TestVerifySpecLinks(VerifyBase):
    def test_no_specs_dir_skips(self):
        findings, notes = self.run_verify()
        self.assertTrue(self.notes_for("spec-links", notes))
        self.assertFalse(self.findings_for("spec-links", findings))

    def test_agreed_spec_without_acs_flagged(self):
        self.write_spec("empty.md", status="agreed", acs=())
        findings, _ = self.run_verify()
        hits = self.findings_for("spec-links", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("empty.md", hits[0])

    def test_draft_spec_without_acs_clean(self):
        self.write_spec("draft.md", status="draft", acs=())
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("spec-links", findings))

    def test_plan_referencing_existing_acs_clean(self):
        self.write_spec("s.md", acs=(1, 2, 3))
        self.write_plan("p.md", "s.md", (1, 3))
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("spec-links", findings))

    def test_plan_referencing_missing_ac_flagged(self):
        self.write_spec("s.md", acs=(1, 2))
        self.write_plan("p.md", "s.md", (1, 7))
        findings, _ = self.run_verify()
        hits = self.findings_for("spec-links", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("AC-7", hits[0])
        self.assertIn("p.md", hits[0])

    def test_plan_without_spec_reference_ignored(self):
        self.write_spec("s.md", acs=(1,))
        (self.root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "plans" / "free.md").write_text(
            "# Standalone plan, no spec, mentions AC-9 informally\n", encoding="utf-8")
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("spec-links", findings))

    def test_check_crash_becomes_note_never_raises(self):
        (self.root / "docs" / "specs").mkdir(parents=True)
        (self.root / "docs" / "specs" / "binary.md").write_bytes(b"\xff\xfe\x00garbage")
        findings, notes = self.run_verify()  # must not raise
        self.assertIsInstance(findings, list)

    def test_plan_spanning_two_specs_clean(self):
        """Review Blocking-1: a plan may reference several specs — ACs must be
        unioned across all of them, not checked against the first only."""
        self.write_spec("a.md", acs=(1, 2, 3))
        self.write_spec("b.md", acs=(4, 5, 6))
        d = self.root / "docs" / "plans"
        d.mkdir(parents=True, exist_ok=True)
        (d / "multi.md").write_text(
            "Per docs/specs/a.md this covers AC-1 and AC-3; "
            "per docs/specs/b.md it also covers AC-4 and AC-6.\n",
            encoding="utf-8")
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("spec-links", findings))

    def test_plan_spanning_two_specs_still_flags_missing(self):
        self.write_spec("a.md", acs=(1,))
        self.write_spec("b.md", acs=(4,))
        d = self.root / "docs" / "plans"
        d.mkdir(parents=True, exist_ok=True)
        (d / "multi.md").write_text(
            "Per docs/specs/a.md and docs/specs/b.md covering AC-1, AC-4, AC-9.\n",
            encoding="utf-8")
        findings, _ = self.run_verify()
        hits = self.findings_for("spec-links", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("AC-9", hits[0])

    def test_genuinely_crashing_check_becomes_note(self):
        """The dispatch loop's crash containment, exercised for real."""
        def boom(root, cfg, window):
            raise RuntimeError("boom")
        original = devflow._VERIFY_CHECKS
        devflow._VERIFY_CHECKS = list(original) + [("boom-check", boom)]
        try:
            findings, notes = self.run_verify()
            self.assertTrue(any(c == "boom-check" and "failed safely" in m
                                for c, m in notes))
        finally:
            devflow._VERIFY_CHECKS = original


class GitFixtureBase(VerifyBase):
    """Real temp git repos with controlled commit timestamps."""

    LEDGER_FMT = "%Y-%m-%dT%H:%M:%SZ"

    def git(self, *args, env_extra=None):
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        subprocess.run(["git", "-C", str(self.root), *args],
                       check=True, capture_output=True, env=env)

    def init_repo(self):
        self.git("init", "-q")
        self.git("config", "user.email", "t@test.local")
        self.git("config", "user.name", "tester")

    def commit_at(self, relpath, when_utc):
        p = self.root / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content at {when_utc.isoformat()}\n", encoding="utf-8")
        stamp = f"@{int(when_utc.timestamp())} +0000"
        self.git("add", relpath)
        self.git("commit", "-q", "-m", f"commit {relpath}",
                 env_extra={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})

    def seed_run(self, started_utc, finished_utc):
        rec = {"run_id": "r", "playbook": "build", "tier": "standard", "task": "t",
               "started": started_utc.strftime(self.LEDGER_FMT),
               "finished": finished_utc.strftime(self.LEDGER_FMT),
               "status": "completed", "loop_backs": 0, "marks": 1}
        with open(self.root / ".devflow" / "runs.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")

    @staticmethod
    def now():
        return datetime.now(timezone.utc)


class TestVerifyOutOfBand(GitFixtureBase):
    def test_commit_inside_run_window_clean(self):
        self.init_repo()
        t = self.now() - timedelta(hours=5)
        self.commit_at("src/a.py", t)
        self.seed_run(t - timedelta(hours=1), t + timedelta(hours=1))
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("out-of-band", findings))

    def test_commit_outside_all_windows_flagged(self):
        self.init_repo()
        self.commit_at("src/a.py", self.now() - timedelta(days=2))
        far = self.now() - timedelta(days=10)
        self.seed_run(far, far + timedelta(hours=1))
        findings, _ = self.run_verify()
        hits = self.findings_for("out-of-band", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("1 of 1", hits[0])

    def test_open_run_covers_recent_commit(self):
        self.init_repo()
        devflow.cmd_start(self.root, "build", tier="standard", task="t")
        self.commit_at("src/b.py", self.now())
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("out-of-band", findings))

    def test_non_git_root_skips(self):
        findings, notes = self.run_verify()
        self.assertTrue(any("git" in n.lower()
                            for n in self.notes_for("out-of-band", notes)))

    def test_no_runs_uses_manual_framing(self):
        self.init_repo()
        self.commit_at("src/a.py", self.now() - timedelta(days=1))
        findings, _ = self.run_verify()
        hits = self.findings_for("out-of-band", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("manual", hits[0])

    def test_empty_repo_clean(self):
        self.init_repo()  # no commits at all
        findings, notes = self.run_verify()
        self.assertFalse(self.findings_for("out-of-band", findings))


class TestVerifyContractStale(GitFixtureBase):
    def set_config(self, **overrides):
        cfg = dict(devflow.DEFAULT_CONFIG)
        cfg.update(overrides)
        (self.root / ".devflow" / "config.json").write_text(
            json.dumps(cfg), encoding="utf-8")

    def test_stale_contract_flagged(self):
        self.init_repo()
        self.commit_at("docs/interfaces/users-api.yaml", self.now() - timedelta(days=3))
        self.commit_at("src/api/users.py", self.now() - timedelta(days=1))
        self.set_config(contract_map={"docs/interfaces/users-api.yaml": ["src/api/*"]})
        findings, _ = self.run_verify()
        hits = self.findings_for("contract-stale", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("users-api.yaml", hits[0])

    def test_fresh_contract_clean(self):
        self.init_repo()
        self.commit_at("src/api/users.py", self.now() - timedelta(days=3))
        self.commit_at("docs/interfaces/users-api.yaml", self.now() - timedelta(days=1))
        self.set_config(contract_map={"docs/interfaces/users-api.yaml": ["src/api/*"]})
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("contract-stale", findings))

    def test_unmapped_contract_noted(self):
        self.init_repo()
        self.commit_at("docs/interfaces/orders-api.yaml", self.now() - timedelta(days=1))
        findings, notes = self.run_verify()
        self.assertFalse(self.findings_for("contract-stale", findings))
        self.assertTrue(any("contract_map" in n
                            for n in self.notes_for("contract-stale", notes)))

    def test_no_interfaces_dir_skips(self):
        self.init_repo()
        _, notes = self.run_verify()
        self.assertTrue(self.notes_for("contract-stale", notes))


class TestVerifyAdrStale(GitFixtureBase):
    def write_adr(self, name, status="Accepted", relates_to="src/auth/*",
                  when=None):
        rel_line = f"**Relates-to:** {relates_to}\n" if relates_to else ""
        content = (f"# ADR-{name[:4]}: demo decision\n\n"
                   f"**Date:** 2026-06-01\n**Status:** {status}\n{rel_line}\n"
                   f"## Context\n\nx\n")
        p = self.root / "docs" / "decisions" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        stamp = f"@{int((when or self.now()).timestamp())} +0000"
        self.git("add", f"docs/decisions/{name}")
        self.git("commit", "-q", "-m", f"adr {name}",
                 env_extra={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})

    def test_stale_adr_flagged(self):
        self.init_repo()
        self.write_adr("0001-auth-model.md", when=self.now() - timedelta(days=5))
        self.commit_at("src/auth/login.py", self.now() - timedelta(days=1))
        findings, _ = self.run_verify()
        hits = self.findings_for("adr-stale", findings)
        self.assertEqual(len(hits), 1)
        self.assertIn("0001-auth-model.md", hits[0])

    def test_adr_newer_than_churn_clean(self):
        self.init_repo()
        self.commit_at("src/auth/login.py", self.now() - timedelta(days=5))
        self.write_adr("0001-auth-model.md", when=self.now() - timedelta(days=1))
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("adr-stale", findings))

    def test_accepted_without_relates_to_noted(self):
        self.init_repo()
        self.write_adr("0002-naming.md", relates_to=None,
                       when=self.now() - timedelta(days=2))
        findings, notes = self.run_verify()
        self.assertFalse(self.findings_for("adr-stale", findings))
        self.assertTrue(any("Relates-to" in n
                            for n in self.notes_for("adr-stale", notes)))

    def test_superseded_ignored(self):
        self.init_repo()
        self.write_adr("0003-old.md", status="Superseded",
                       when=self.now() - timedelta(days=5))
        self.commit_at("src/auth/login.py", self.now() - timedelta(days=1))
        findings, _ = self.run_verify()
        self.assertFalse(self.findings_for("adr-stale", findings))

    def test_no_adrs_skips(self):
        self.init_repo()
        _, notes = self.run_verify()
        self.assertTrue(self.notes_for("adr-stale", notes))

    def test_blank_relates_to_counted_not_silently_skipped(self):
        """Review NB-2: '**Relates-to:** ' with no globs must surface in the
        without-Relates-to note, never vanish."""
        self.init_repo()
        self.write_adr("0004-blank.md", relates_to=" ",
                       when=self.now() - timedelta(days=2))
        findings, notes = self.run_verify()
        self.assertFalse(self.findings_for("adr-stale", findings))
        self.assertTrue(any("1 Accepted ADR" in n
                            for n in self.notes_for("adr-stale", notes)))

    def test_plain_title_case_relates_to_matched(self):
        """Review NB-4: 'Relates-to:' without bold markers must also count."""
        self.init_repo()
        p = self.root / "docs" / "decisions" / "0005-plain.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# ADR-0005: plain header form\n\n**Date:** 2026-06-01\n"
                     "**Status:** Accepted\nRelates-to: src/auth/*\n\n## Context\nx\n",
                     encoding="utf-8")
        stamp = f"@{int((self.now() - timedelta(days=5)).timestamp())} +0000"
        self.git("add", "docs/decisions/0005-plain.md")
        self.git("commit", "-q", "-m", "adr plain",
                 env_extra={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
        self.commit_at("src/auth/login.py", self.now() - timedelta(days=1))
        findings, _ = self.run_verify()
        self.assertEqual(len(self.findings_for("adr-stale", findings)), 1)


class TestDigest(GitFixtureBase):
    """digest = the windowed middle lens: brief is 'now', stats is 'all time',
    digest is 'what happened in the last N days'."""

    def seed_finished(self, days_ago, playbook="build", tier="standard",
                      status="completed", loop_backs=0, task="some task"):
        end = self.now() - timedelta(days=days_ago)
        self.seed_run(end - timedelta(hours=2), end)
        # rewrite last record with the requested fields
        lp = self.root / ".devflow" / "runs.jsonl"
        recs = [json.loads(l) for l in lp.read_text(encoding="utf-8").splitlines()]
        recs[-1].update({"playbook": playbook, "tier": tier, "status": status,
                         "loop_backs": loop_backs, "task": task})
        lp.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")

    def write_debt(self, slug, status):
        d = self.root / "docs" / "sessions"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"hotfix-debt-{slug}.md").write_text(
            f"---\ntype: hotfix-debt\nstatus: {status}\ndate: 2026-06-10\n---\n",
            encoding="utf-8")

    def test_window_filters_old_runs(self):
        self.seed_finished(2, task="recent work")
        self.seed_finished(30, task="ancient work")
        text = "\n".join(devflow.cmd_digest(self.root))
        self.assertIn("recent work", text)
        self.assertNotIn("ancient work", text)
        self.assertIn("1 completed", text)

    def test_counts_abandoned_and_loopbacks(self):
        self.seed_finished(1, status="completed", loop_backs=2)
        self.seed_finished(2, status="completed")
        self.seed_finished(3, status="abandoned", loop_backs=1)
        text = "\n".join(devflow.cmd_digest(self.root))
        self.assertIn("2 completed", text)
        self.assertIn("1 abandoned", text)
        self.assertIn("3 loop-back", text)

    def test_open_run_shown_in_flight(self):
        devflow.cmd_start(self.root, "fix", tier="standard", task="live bug")
        text = "\n".join(devflow.cmd_digest(self.root))
        self.assertIn("in flight", text)
        self.assertIn("live bug", text)

    def test_open_debt_listed(self):
        self.write_debt("payment-timeout", "open")
        self.write_debt("old-closed", "closed")
        text = "\n".join(devflow.cmd_digest(self.root))
        self.assertIn("payment-timeout", text)
        self.assertNotIn("old-closed", text)

    def test_line_cap(self):
        for i in range(12):
            self.seed_finished(1, task=f"run number {i}")
        lines = devflow.cmd_digest(self.root)
        self.assertLessEqual(len(lines), 20)

    def test_days_override_includes_older(self):
        self.seed_finished(10, task="ten days ago")
        text7 = "\n".join(devflow.cmd_digest(self.root))
        text30 = "\n".join(devflow.cmd_digest(self.root, days=30))
        self.assertNotIn("ten days ago", text7)
        self.assertIn("ten days ago", text30)

    def test_explicit_zero_days_honored(self):
        """Review NB-1: `days or 7` swallowed an explicit 0 — None means
        default, 0 means an empty window."""
        self.seed_finished(1, task="yesterday")
        text = "\n".join(devflow.cmd_digest(self.root, days=0))
        self.assertIn("last 0 days", text)
        self.assertNotIn("yesterday", text)

    def test_absence_and_garbage_tolerated(self):
        lines = devflow.cmd_digest(self.root)  # empty .devflow only
        self.assertTrue(lines)
        with open(self.root / ".devflow" / "runs.jsonl", "a", encoding="utf-8") as fh:
            fh.write("{broken json\n")
        self.assertTrue(devflow.cmd_digest(self.root))


class TestVerifySkipFlag(GitFixtureBase):
    """CI cannot run out-of-band (the ledger is gitignored) — --skip makes
    that exclusion explicit and visible, never silent."""

    def test_skip_turns_check_into_note(self):
        self.init_repo()
        self.commit_at("src/a.py", self.now() - timedelta(days=1))  # would flag
        findings, notes = devflow.cmd_verify(self.root, skip=("out-of-band",))
        self.assertFalse(self.findings_for("out-of-band", findings))
        self.assertTrue(any("request" in n
                            for n in self.notes_for("out-of-band", notes)))

    def test_skip_via_main_cli(self):
        self.init_repo()
        self.commit_at("src/a.py", self.now() - timedelta(days=1))
        rc = devflow.main(["--root", str(self.root), "verify", "--strict",
                           "--skip", "out-of-band"])
        self.assertEqual(rc, 0)  # the only finding source was skipped


class TestCiTemplates(unittest.TestCase):
    REPO = Path(__file__).resolve().parent.parent

    def read(self, name):
        return (self.REPO / "ci" / "github-actions" / name).read_text(encoding="utf-8")

    def test_verify_template_essentials(self):
        text = self.read("devflow-verify.yml")
        self.assertIn("pull_request", text)
        self.assertIn(".devflow/devflow.py", text)       # fork-safe guard target
        self.assertIn("--skip out-of-band", text)         # ledger is gitignored
        self.assertIn("--strict", text)
        self.assertIn("STRICT_GATE", text)                # documented hard-gate switch
        self.assertIn("fetch-depth: 0", text)             # git-date checks need history
        self.assertIn("grep -v ': note '", text)          # PR comment: findings only

    def test_protected_gate_template_essentials(self):
        text = self.read("protected-todo-gate.yml")
        self.assertIn("pull_request", text)
        self.assertIn("TODO: \\[PROTECTED", text)
        self.assertIn("exit 1", text)                     # this one IS a gate

    def test_added_line_regex_behavior(self):
        """The gate greps only ADDED diff lines for the protected marker."""
        pattern = re.compile(r"^\+.*TODO: \[PROTECTED", re.M)
        diff = ("+++ b/src/auth/login.py\n"
                "+    # TODO: [PROTECTED — human authorship required: token check]\n"
                "-    # TODO: [PROTECTED — removed marker]\n"
                "     # TODO: [PROTECTED — context line, unchanged]\n")
        hits = pattern.findall(diff)
        self.assertEqual(len(hits), 1)
        self.assertNotIn("removed", hits[0])


class TestVerifyStrictExit(VerifyBase):
    def test_strict_exit_codes_via_main(self):
        self.write_spec("bad.md", status="agreed", acs=())
        rc_default = devflow.main(["--root", str(self.root), "verify"])
        rc_strict = devflow.main(["--root", str(self.root), "verify", "--strict"])
        self.assertEqual(rc_default, 0)
        self.assertEqual(rc_strict, 1)

    def test_strict_clean_is_zero(self):
        self.write_spec("ok.md", acs=(1,))
        rc = devflow.main(["--root", str(self.root), "verify", "--strict"])
        self.assertEqual(rc, 0)


class TestStats(StateCoreBase):
    def seed_ledger(self):
        records = [
            {"run_id": "fix-1", "playbook": "fix", "tier": "standard", "task": "a",
             "started": "2026-06-10T10:00:00Z", "finished": "2026-06-10T10:30:00Z",
             "status": "completed", "loop_backs": 2, "marks": 5},
            {"run_id": "fix-2", "playbook": "fix", "tier": "quick", "task": "b",
             "started": "2026-06-10T11:00:00Z", "finished": "2026-06-10T11:10:00Z",
             "status": "completed", "loop_backs": 0, "marks": 3},
            {"run_id": "build-1", "playbook": "build", "tier": "standard", "task": "c",
             "started": "2026-06-10T12:00:00Z", "finished": "2026-06-10T12:20:00Z",
             "status": "abandoned", "loop_backs": 1, "marks": 2},
            {"run_id": "spike-1", "playbook": "spike", "tier": "quick", "task": "d",
             "started": "2026-06-10T13:00:00Z", "finished": "2026-06-10T13:40:00Z",
             "status": "completed", "loop_backs": 0, "marks": 2},
        ]
        lp = self.root / ".devflow" / "runs.jsonl"
        lp.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")

    def test_stats_aggregates(self):
        self.seed_ledger()
        text = devflow.cmd_stats(self.root)
        self.assertIn("runs: 4", text)
        self.assertIn("completed: 3", text)
        self.assertIn("abandoned: 1", text)
        self.assertIn("loop-backs: 3", text)
        self.assertIn("fix", text)
        self.assertIn("build", text)
        self.assertRegex(text, r"mean duration: 25(\.0)? min")  # (30+10+20+40)/4

    def test_stats_empty(self):
        self.assertIn("no runs", devflow.cmd_stats(self.root).lower())

    def test_stats_tolerates_garbage_lines(self):
        self.seed_ledger()
        with open(self.root / ".devflow" / "runs.jsonl", "a", encoding="utf-8") as fh:
            fh.write("{broken\n")
        self.assertIn("runs: 4", devflow.cmd_stats(self.root))


if __name__ == "__main__":
    unittest.main()
