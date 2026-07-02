---
name: devflow-audit
description: Review-only playbook — code review with severity-ranked findings, or a security audit (threat model → dependency scan → security review). Selected by devflow-dispatch for review requests; produces findings, never fixes.
framework: devflow
---

# Audit — Findings, Not Fixes

Evaluation only: this playbook changes no code. Confirmed problems exit to `devflow-fix` or `devflow-build` runs; after the fixes land, a confirmation review pass here closes the loop.

## Default: code review

1. **State the scope** — the diff, branch, or PR under review, and what is explicitly out of scope.
2. **Review** — correctness, regressions, standards, test adequacy. Fresh-context `code-reviewer` subagent at standard+ (inline at quick). When a contract exists in `docs/interfaces/`, verify the implementation matches it.
3. **Findings** — each with severity **Blocking / Non-blocking / Question**, file/line references, and a concrete reason. No rewrites unless explicitly asked.

## Security adapter

Run in order — each step hands off through a **durable artifact**, not conversation state:

1. **Threat model** (`threat-modeler`): map the change's attack surface — inputs, auth paths, trust boundaries, external calls, sensitive data flows — into an applicability-ranked threat checklist, written to `docs/audits/<date>-threat-model-<slug>.md`. Only the path and top priorities return here.
2. **Dependency scan** (`dependency-auditor`): ecosystem-native scanners (npm audit, pip-audit, cargo audit, …), focused by the threat model's package handoff; report written to `docs/audits/<date>-dependency-audit-<slug>.md`. If no scanner is available for the ecosystem, stop and report the gap — never produce findings from memory.
3. **Security review** (`find-bugs`): runs in its own isolated context (`context: fork`) and reads both artifacts from disk — pass their paths as arguments. Change-specific, not generic; the verbose diff-reading stays out of this session, and only the findings report returns.

The artifacts double as the audit trail: the confirmation pass at Exit re-reads them instead of reconstructing the threat model.

Security audit and functional code review are separate passes on the same change — do not conflate them.

## Exit

- Findings report delivered. Blocking findings → `devflow-fix`, one run per confirmed finding, with this report as triage input.
- Fixes applied → confirmation review pass here.
- No actionable findings → close; optionally record the clean audit in the project docs.

## Boundaries

- Does: review, rank findings by severity, route fixes, confirm after remediation.
- Does not: implement, fix, or refactor; run a security review without its threat-model context.
