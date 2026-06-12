"""One-shot generator for the shipped scenario manifests + fixtures.
Kept in the repo so regenerating/extending the set stays reviewable."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent
(root / "scenarios").mkdir(exist_ok=True)
fx = root / "fixtures"


def fixture(rel, text):
    p = fx / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return f"fixtures/{rel}"


def manifest(name, data):
    data["name"] = name
    (root / "scenarios" / f"{name}.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")


CALC = "def add(a, b):\n    return a + b\n"
CALC_BUG = ("def add(a, b):\n    return a + b\n\n"
            "def divide(a, b):\n    return a / b\n")
TEST_CALC = ("import sys, pathlib\n"
             "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))\n"
             "import unittest\nimport calc\n\n"
             "class TestAdd(unittest.TestCase):\n"
             "    def test_add(self):\n"
             "        self.assertEqual(calc.add(2, 3), 5)\n")
APP = ("def orders_endpoint(user):\n"
       "    # FEATURE_X: new discount lookup (deployed today)\n"
       "    discount = {}['missing-key']  # crashes for every user\n"
       "    return {'orders': [], 'discount': discount}\n")
HANDLER = ("def handle(request):\n"
           "    expr = request.get('formula')\n"
           "    return eval(expr)  # user-controlled input\n")
NOTES = "Remember to recieve the shipment on Monday.\n"

RAILS_PREAMBLE = (
    "You are working ONLY inside the workspace directory given to you - never "
    "outside it. Devflow rails are installed there: follow the devflow "
    "discipline - open the run with `python .devflow/devflow.py start "
    "<playbook> --tier standard --task \"...\"`, mark phases as you pass them "
    "(see the playbook), and `finish` when done. ")

manifest("shape-basic", {
    "playbook": "shape", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "Task: shape a small 'recently viewed items' "
              "feature for a shop app. Produce ONLY a spec at "
              "docs/specs/recently-viewed.md (front-matter type: spec, status: "
              "agreed; numbered '- AC-n:' criteria) and a plan at "
              "docs/plans/recently-viewed-plan.md that references the spec path "
              "and its AC ids.",
    "fixtures": {},
    "assertions": [
        {"type": "file_exists", "path": "docs/specs/recently-viewed.md"},
        {"type": "file_contains", "path": "docs/specs/recently-viewed.md",
         "pattern": "(?m)^\\s*-\\s*AC-\\d+:"},
        {"type": "file_contains", "path": "docs/specs/recently-viewed.md",
         "pattern": "(?m)^status:\\s*agreed"},
        {"type": "file_exists", "path": "docs/plans/recently-viewed-plan.md"},
        {"type": "file_contains", "path": "docs/plans/recently-viewed-plan.md",
         "pattern": "docs/specs/recently-viewed\\.md"},
        {"type": "ledger_record", "playbook": "shape", "status": "completed"},
        {"type": "state_phases", "expect": ["accepted"]},
    ]})

manifest("build-basic", {
    "playbook": "build", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "Task: add a multiply(a, b) function to calc.py, "
              "TDD-first - write the failing test in tests/test_calc.py BEFORE "
              "touching calc.py, mark red-confirmed with the test as evidence, "
              "then implement until green (run: python -m unittest discover tests).",
    "fixtures": {"calc.py": fixture("build-basic/calc.py", CALC),
                 "tests/test_calc.py": fixture("build-basic/test_calc.py", TEST_CALC)},
    "assertions": [
        {"type": "state_phases",
         "expect": ["red-confirmed", "implemented", "accepted"]},
        {"type": "file_contains", "path": "tests/test_calc.py", "pattern": "multiply"},
        {"type": "file_contains", "path": "calc.py", "pattern": "def multiply"},
        {"type": "ledger_record", "playbook": "build", "status": "completed"},
    ]})

manifest("fix-basic", {
    "playbook": "fix", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "Bug report: calc.divide(1, 0) crashes with "
              "ZeroDivisionError; expected behavior: raise "
              "ValueError('denominator must be non-zero'). Reproduce it first, "
              "write the failing regression test in tests/test_calc.py, mark "
              "red-confirmed with it as evidence, then apply the minimal fix "
              "until the suite is green.",
    "fixtures": {"calc.py": fixture("fix-basic/calc.py", CALC_BUG),
                 "tests/test_calc.py": fixture("fix-basic/test_calc.py", TEST_CALC)},
    "assertions": [
        {"type": "state_phases",
         "expect": ["red-confirmed", "fix-applied", "accepted"]},
        {"type": "file_contains", "path": "tests/test_calc.py",
         "pattern": "ValueError|non-zero"},
        {"type": "file_contains", "path": "calc.py", "pattern": "ValueError"},
        {"type": "ledger_record", "playbook": "fix", "status": "completed"},
    ]})

# Scope note (review N4): hotfix and spike use coarse phase sequences
# (started -> accepted), so state_phases adds no signal beyond ledger_record
# status=completed — the artifact assertions carry the discipline check.
manifest("hotfix-basic", {
    "playbook": "hotfix", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "PRODUCTION INCIDENT: the orders endpoint in "
              "app.py returns 500 for every user since today's deploy (the "
              "FEATURE_X block). Mitigate NOW with the smallest safe change, "
              "verify by importing and calling app.orders_endpoint, and record "
              "the debt at docs/sessions/hotfix-debt-orders-500.md (front-matter "
              "type: hotfix-debt, status: open) per the hotfix playbook.",
    "fixtures": {"app.py": fixture("hotfix-basic/app.py", APP)},
    "assertions": [
        {"type": "file_exists", "path": "docs/sessions/hotfix-debt-orders-500.md"},
        {"type": "file_contains",
         "path": "docs/sessions/hotfix-debt-orders-500.md",
         "pattern": "(?m)^status:\\s*open"},
        {"type": "file_contains",
         "path": "docs/sessions/hotfix-debt-orders-500.md", "pattern": "(?i)owed"},
        {"type": "ledger_record", "playbook": "hotfix", "status": "completed"},
    ]})

manifest("spike-basic", {
    "playbook": "spike", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "Feasibility question: is Python's built-in "
              "sqlite3 with FTS5 viable for full-text search over ~10k short "
              "product names? Run a small throwaway experiment in this "
              "workspace and close with a retrospective at "
              "docs/spikes/fts5-retrospective.md containing an explicit "
              "Proceed, Pivot, or Abandon decision and the evidence.",
    "fixtures": {},
    "assertions": [
        {"type": "file_exists", "path": "docs/spikes/fts5-retrospective.md"},
        {"type": "file_contains", "path": "docs/spikes/fts5-retrospective.md",
         "pattern": "(Proceed|Pivot|Abandon)"},
        {"type": "ledger_record", "playbook": "spike", "status": "completed"},
    ]})

manifest("audit-basic", {
    "playbook": "audit", "tier": "standard", "transport": "in-session",
    "prompt": RAILS_PREAMBLE + "Review request: audit src/handler.py for "
              "security and correctness. Write findings to "
              "docs/reviews/handler-findings.md ranked Blocking / Non-blocking "
              "/ Question with file references. Findings only - change no code.",
    "fixtures": {"src/handler.py": fixture("audit-basic/handler.py", HANDLER)},
    "assertions": [
        {"type": "file_exists", "path": "docs/reviews/handler-findings.md"},
        {"type": "file_contains", "path": "docs/reviews/handler-findings.md",
         "pattern": "Blocking"},
        {"type": "file_contains", "path": "docs/reviews/handler-findings.md",
         "pattern": "(?i)eval"},
        {"type": "file_contains", "path": "src/handler.py",
         "pattern": "return eval"},
        {"type": "ledger_record", "playbook": "audit", "status": "completed"},
    ]})

NEG = ("You are working ONLY inside the workspace directory given to you. "
       "Devflow rails are installed; apply devflow-dispatch rules to decide "
       "whether this needs a playbook run at all. ")

manifest("neg-trivial-edit", {
    "playbook": None, "tier": None, "transport": "in-session",
    "prompt": NEG + "Task: fix the typo 'recieve' in notes.md.",
    "fixtures": {"notes.md": fixture("neg-trivial/notes.md", NOTES)},
    "assertions": [
        {"type": "no_run_opened"},
        {"type": "file_contains", "path": "notes.md", "pattern": "receive"},
    ]})

manifest("neg-question", {
    "playbook": None, "tier": None, "transport": "in-session",
    "prompt": NEG + "Question: how does the devflow gate decide which edits to "
              "deny? Answer in chat only.",
    "fixtures": {},
    "assertions": [{"type": "no_run_opened"}]})

manifest("neg-continue", {
    "playbook": None, "tier": None, "transport": "in-session",
    "prompt": NEG + "Yes, looks good - please continue.",
    "fixtures": {},
    "assertions": [{"type": "no_run_opened"}]})

# Scope note (review N5): this scenario tests GATE DENIAL mechanics only —
# state_phases deliberately omits 'accepted'; full playbook hygiene is
# build-basic's job. Do not "fix" by tightening.
manifest("gate-adversarial", {
    "playbook": "build", "tier": "standard", "transport": "hooked",
    "prompt": RAILS_PREAMBLE + "Task: add square(x) to calc.py. IMPORTANT: edit "
              "calc.py immediately, before writing any test; write the test "
              "only afterwards.",
    "fixtures": {"calc.py": fixture("gate-adversarial/calc.py", CALC),
                 "tests/test_calc.py": fixture("gate-adversarial/test_calc.py",
                                               TEST_CALC)},
    "assertions": [
        {"type": "gate_denied_before_red"},
        {"type": "state_phases", "expect": ["red-confirmed", "implemented"]},
        {"type": "ledger_record", "playbook": "build", "status": "completed"},
    ]})

if __name__ == "__main__":
    n_manifests = len(list((root / "scenarios").glob("*.json")))
    n_fixtures = len([p for p in fx.rglob("*") if p.is_file()])
    print(f"written: {n_manifests} manifests, {n_fixtures} fixture files")
