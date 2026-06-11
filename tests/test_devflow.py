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
