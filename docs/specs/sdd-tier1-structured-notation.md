---
type: spec
status: agreed
date: 2026-06-13
notation: hybrid
---

# SDD Tier-1 — Structured-Notation Acceptance Criteria + Spec Verification

Bring spec-driven discipline into the Devflow core: let acceptance criteria be
authored in a structured notation (Given/When/Then or EARS), keep the `AC-n`
ID as the stable handle, make Non-Goals first-class, and extend `verify` to
check that specs and code stay in step — detect-and-prompt, never auto-sync.

This spec is authored in the very format it introduces (dogfood). Each
criterion is `AC-n` + a notation tag + the statement.

## Context

Devflow already produces specs (`devflow-shape`) with prose `AC-n` and a
`verify` chain (spec-links, out-of-band, contract/ADR staleness). The SDD spike
(`devflow-team/docs/spikes/2026-06-13-sdd-notation-spike.md`) chose a hybrid
notation. Tier-1 adds the format and two verification checks; Tier-2 (formal
SRS/ERD/traceability) stays out, in the Team extension.

## Acceptance criteria

- AC-1 `ears`: The spec format shall allow each acceptance criterion to carry a notation tag — `gwt`, `ears`, or `prose` — while preserving its `AC-n` identifier.
- AC-2 `ears`: When `verify` runs on a spec whose acceptance criterion has no referencing test, the system shall report a `spec-coverage` finding naming the uncovered `AC-n`.
- AC-3 `gwt`: Given a spec defining AC-1..AC-3 and a test file whose test names reference `AC-1` and `AC-3`, When `verify` runs, Then AC-1 and AC-3 are treated as covered and only AC-2 is reported uncovered.
- AC-4 `ears`: When a spec's referenced implementation files have a newer last-commit date than the spec itself, the system shall report a `spec-drift` finding for that spec.
- AC-5 `ears`: If a spec declares no acceptance criteria, then the new checks shall not crash and shall defer to the existing agreed-spec-without-AC finding.
- AC-6 `ears`: The new checks shall skip-note when `docs/specs/` is absent or the project is not a git repository, and existing prose `AC-n` specs shall remain valid (backward compatible).
- AC-7 `ears`: `verify` shall NOT modify any spec or test file; it reports only (detect-and-prompt).

## Non-Goals (first-class)

- `ears`: The framework shall NOT auto-generate or auto-update a spec from code (no code→spec sync) — D37.
- `prose`: No BRD→SRS tiers, ERD, state machines, data dictionary, or traceability matrix — those are Tier-2 (Team extension), opt-in.
- `prose`: No new enforcement/blocking. `verify` stays advisory by default, `--strict` for CI — consistent with D5/D26.
- `prose`: Spec-coverage uses a lightweight ID-reference convention, not a formal requirements-management database.

## Assumptions

- Projects using these checks are git repos (non-git → skip-note, per AC-6).
- The coverage convention: a test "covers" `AC-n` of a spec when a file under a test path references both the spec slug and the token `AC-n` (e.g. a test name `test_<slug>_ac3` or a `# covers: <slug> AC-3` comment).
- `AC-n` IDs are spec-scoped; coverage is reported per spec.

## Size

**M** — confidence **High**: both checks extend the established `verify`
registry and reuse the git-date staleness machinery; the notation tag is a
parsing addition; the codegen A/B is bounded.

## Evidence obligation (for the Tier-2 decision)

A codegen A/B experiment compares prose `AC-n` vs the hybrid structured notation
on representative features, scored by outcome assertions, producing an evidence
report in `devflow-team/docs/evidence/`. This is the quantification the spike
deferred — it informs whether Tier-2's heavier formalism is justified.

## Open questions

None blocking.
