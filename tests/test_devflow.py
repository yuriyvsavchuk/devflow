"""Tests for devflow.py — state core (Phase 2, Task 2).

Run:  python -m unittest discover tests -v   (from the repo root)
"""

import json
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
