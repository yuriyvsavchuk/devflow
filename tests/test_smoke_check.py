"""Tests for tests/smoke/smoke_check.py — the smoke harness assertion core.

The checker is the durable half of the prompt-regression design (D30): it
asserts scenario OUTCOMES (files, phase journals, ledger, gate log) and must
itself be trustworthy — a wrong checker is worse than no checker.

Run:  python -m unittest discover tests -v   (from the repo root)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "smoke"))

import smoke_check  # noqa: E402


class CheckerBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self._tmp.name)
        (self.ws / ".devflow").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.ws / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def journal(self, name, records):
        self.write(f".devflow/{name}",
                   "".join(json.dumps(r) + "\n" for r in records))

    def run_one(self, assertion):
        results = smoke_check.run_assertions({"name": "t",
                                              "assertions": [assertion]}, self.ws)
        self.assertEqual(len(results), 1)
        return results[0]  # (description, ok, detail)


class TestFileAssertions(CheckerBase):
    def test_file_exists_pass_and_fail(self):
        self.write("docs/specs/a.md", "x")
        self.assertTrue(self.run_one(
            {"type": "file_exists", "path": "docs/specs/a.md"})[1])
        self.assertFalse(self.run_one(
            {"type": "file_exists", "path": "docs/specs/missing.md"})[1])

    def test_file_absent(self):
        self.assertTrue(self.run_one(
            {"type": "file_absent", "path": "should/not/exist.md"})[1])
        self.write("oops.md", "x")
        self.assertFalse(self.run_one(
            {"type": "file_absent", "path": "oops.md"})[1])

    def test_file_contains_regex(self):
        self.write("docs/specs/a.md", "## Acceptance criteria\n- AC-1: works\n")
        self.assertTrue(self.run_one(
            {"type": "file_contains", "path": "docs/specs/a.md",
             "pattern": r"AC-\d+:"})[1])
        self.assertFalse(self.run_one(
            {"type": "file_contains", "path": "docs/specs/a.md",
             "pattern": "nonexistent-token"})[1])

    def test_file_contains_missing_file_fails_with_detail(self):
        desc, ok, detail = self.run_one(
            {"type": "file_contains", "path": "gone.md", "pattern": "x"})
        self.assertFalse(ok)
        self.assertIn("gone.md", detail)


class TestJournalAssertions(CheckerBase):
    def test_state_phases_ordered_subsequence(self):
        self.journal("marks-log.jsonl", [
            {"run_id": "r", "phase": "repro-confirmed", "at": "1"},
            {"run_id": "r", "phase": "red-confirmed", "at": "2"},
            {"run_id": "r", "phase": "fix-applied", "at": "3"},
            {"run_id": "r", "phase": "accepted", "at": "4"},
        ])
        self.assertTrue(self.run_one(
            {"type": "state_phases",
             "expect": ["red-confirmed", "accepted"]})[1])  # gaps allowed
        self.assertFalse(self.run_one(
            {"type": "state_phases",
             "expect": ["fix-applied", "red-confirmed"]})[1])  # wrong order

    def test_state_phases_missing_journal_fails(self):
        self.assertFalse(self.run_one(
            {"type": "state_phases", "expect": ["red-confirmed"]})[1])

    def test_ledger_record_field_match_on_last(self):
        self.journal("runs.jsonl", [
            {"run_id": "a", "playbook": "fix", "status": "abandoned"},
            {"run_id": "b", "playbook": "fix", "status": "completed",
             "loop_backs": 0},
        ])
        self.assertTrue(self.run_one(
            {"type": "ledger_record", "playbook": "fix",
             "status": "completed"})[1])
        self.assertFalse(self.run_one(
            {"type": "ledger_record", "playbook": "build",
             "status": "completed"})[1])

    def test_no_run_opened(self):
        self.assertTrue(self.run_one({"type": "no_run_opened"})[1])
        self.journal("runs.jsonl", [{"run_id": "x"}])
        self.assertFalse(self.run_one({"type": "no_run_opened"})[1])

    def test_no_run_opened_fails_on_live_state(self):
        self.write(".devflow/state.json", json.dumps({"run_id": "live"}))
        self.assertFalse(self.run_one({"type": "no_run_opened"})[1])

    def test_gate_denied_before_red(self):
        self.journal("gate-log.jsonl", [
            {"rule": "red-phase", "path": "src/a.py",
             "at": "2026-06-12T10:00:00Z"}])
        self.journal("marks-log.jsonl", [
            {"run_id": "r", "phase": "red-confirmed",
             "at": "2026-06-12T10:05:00Z"}])
        self.assertTrue(self.run_one({"type": "gate_denied_before_red"})[1])

    def test_gate_denied_before_red_fails_without_denial(self):
        self.journal("marks-log.jsonl", [
            {"run_id": "r", "phase": "red-confirmed",
             "at": "2026-06-12T10:05:00Z"}])
        self.assertFalse(self.run_one({"type": "gate_denied_before_red"})[1])


class TestManifestValidation(CheckerBase):
    def test_unknown_assertion_type_is_readable_error(self):
        with self.assertRaises(smoke_check.SmokeError) as ctx:
            smoke_check.load_manifest_data(
                {"name": "bad", "assertions": [{"type": "teleport"}]})
        self.assertIn("teleport", str(ctx.exception))

    def test_missing_required_keys_rejected(self):
        with self.assertRaises(smoke_check.SmokeError):
            smoke_check.load_manifest_data({"assertions": []})  # no name

    def test_main_exit_codes(self):
        self.write("ok.md", "content")
        manifest = self.ws / "scenario.json"
        manifest.write_text(json.dumps({
            "name": "t",
            "assertions": [{"type": "file_exists", "path": "ok.md"}]}),
            encoding="utf-8")
        rc = smoke_check.main(["--scenario", str(manifest),
                               "--workspace", str(self.ws)])
        self.assertEqual(rc, 0)
        manifest.write_text(json.dumps({
            "name": "t",
            "assertions": [{"type": "file_exists", "path": "missing.md"}]}),
            encoding="utf-8")
        rc = smoke_check.main(["--scenario", str(manifest),
                               "--workspace", str(self.ws)])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
