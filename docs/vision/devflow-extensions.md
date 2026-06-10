# Devflow Extensions — Team and Project Vision

**Date:** 2026-05-19
**Author:** Yuriy Savchuk + Claude (collaborative sessions)

| Extension | Status |
|---|---|
| Team Extension — Phases 1–4 | ✅ Complete |
| Team Extension — Phase 5 (Release Governance) | 🔲 Planned |
| Project Extension | 💡 Vision |

---

## Framework Evolution

Devflow v1 addresses the individual contributor: one developer, one pipeline, one session. It enforces discipline, routes tasks, and produces structured evidence. It works.

The extensions address what v1 leaves unsolved: **coordination** and **continuity above the sprint level**.

When multiple AI-accelerated contributors work in parallel, individual discipline is necessary but not sufficient. Decisions made in the morning are baked into three modules by afternoon. A teammate who would have caught the conflict finds it at code review — when reversing it is expensive. Structural information accumulates faster than review cycles can propagate it.

The Team Extension solves this for sprint-level work. The Project Extension extends the same principles across sprints, portfolios, and stakeholder boundaries.

---

## Immutable Design Principles

These principles govern all extension decisions. Established through the requirements process and cannot be relaxed without explicit revision.

1. **Model-agnostic from day one.** Framework logic is expressed in Markdown and YAML — executable by any LLM. Claude Code is the reference implementation. Integration points are standalone scripts callable as generic tool use.

2. **Coordination artifacts are pipeline side effects, not ceremonies.** Every mandatory step is the natural output of an existing pipeline step. Coordination overhead that requires a separate contributor action defeats the AI-acceleration benefit.

3. **Push over pull for critical structural information.** Contributors should not need to know to look for decisions. The framework delivers relevant information to their working context automatically.

4. **Framework produces evidence; humans make decisions.** No gate, approval, or release decision is automated. The framework pre-assembles evidence packages; humans act on them.

5. **Compliance modes are optional layers.** Framework runs without compliance overhead by default. SOC2 mode and other layers activate via project configuration.

6. **Phased delivery — each phase works independently.** Phase 1 is useful without Phase 2. Phases are not coupled.

7. **No technical blocking for process guidance.** The framework provides guardrails through process and tooling, not hard locks.

---

## Team Extension — Completed (Phases 1–4)

The Team Extension transforms Devflow from a solo-practitioner tool into a coordination platform for enterprise software development teams: developers, QA/SDET, BA, DevOps, SRE, and Scrum roles.

### What it enables

#### AI Trust Zones (Phase 1)

Teams define three zones per project — Green (AI-authored), Yellow (AI-assisted), Red (human-authored) — in a `devflow-trust.yaml` file owned by the team lead. Pipeline workers respect zone boundaries automatically: `feature-implementer` stops at Red zone boundaries and inserts explicit `TODO: [RED ZONE]` annotations that CI can verify. Contributors know exactly where human judgment is required without reading the entire codebase.

#### PR Comprehension Gate (Phase 1)

Authors produce a structured comprehension summary before code review begins — written in their own words, covering what the change does, which sections they understand, and which AI-generated sections they validated. The gate proves understanding was demonstrated, not passively accepted. `code-reviewer` checks for the summary and will not proceed without it.

An optional **PR Review Policy** (`devflow-review-policy.md`) extends the review process with team-defined standards: review points (what must be checked), severity levels (Blocking / Non-blocking / Question), SLA thresholds surfaced as digest signals, and reviewer tier requirements per contributor tier. When present, `code-reviewer` runs a policy compliance assessment in both self-review and reviewer modes. Two independent assessments per PR are preserved in `docs/team/pr-reviews/` and feed Daily Digest SLA signals, Sprint Review compliance summaries, and Sprint Retrospective policy trend analysis. If the file is absent, all existing review behavior is unchanged.

#### Structural Ledger and Decision Broadcast (Phase 2)

Every structurally significant pipeline run — ADR settled, interface contract created or updated — produces a ledger entry and updates a shared index. When a contributor starts a new session, `devflow:sync-context` filters the ADR and ledger indexes to their working subsystems and delivers a targeted briefing. Decisions made by teammates propagate automatically into working contexts. No manual scanning of the shared repo required.

#### Specification-Driven Testing (Phase 3)

`test-engineer` runs in two passes: the first pass reads acceptance criteria only — implementation files are blocked — producing a black-box test contract before implementation is complete. A dedicated `test-reviewer` sub-agent audits test quality against specification compliance, catching implementation-driven assertions masquerading as specification-driven ones. Red zone test assertions are generated as commented-out code; the developer must explicitly uncomment them as the act of verification.

#### Scrum Ceremony Support (Phase 4)

Three pre-refinement templates (user-story, incident, tech-debt) run asynchronously before the refinement ceremony, producing clarified stories with acceptance criteria, scope-estimator ratings mapped to story points, assumption lists, and Definition of Ready checklists. Refinement shifts from estimation-and-decomposition to reviewing and challenging pre-assembled output. A `devflow:daily-digest` auto-generates before standup from ledger and session-continuity snapshots. A `devflow:sprint-review` technical artifact assembles pipeline completion evidence, ledger deltas, and ADR index changes for the sprint review.

---

## Team Extension — Phase 5: Release Governance (Planned)

**Goal:** Eliminate manual evidence assembly for Go/NoGo decisions and make release readiness continuously visible.

**What it will enable:**

- **Continuous release readiness tracking** — every completed pipeline run contributes to a release readiness artifact. At any point the artifact shows: stories fully ready, stories pending specific gates, open blockers. The Go/NoGo meeting reviews the artifact; it does not construct it.
- **SOC2 compliance mode** — activated via `devflow-trust.yaml`. Pipeline steps produce timestamped, named evidence records forming a full requirements → delivery traceability chain in formats auditors already accept (Git records, Jira records, release notes).
- **Feature flag lifecycle** — declaration at pre-refinement, implementation behind flag from the start, activation per rollout strategy, and a mandatory removal deadline that triggers a tracked cleanup pipeline.
- **Release notes generation** — `devflow:release-notes` produces a technical changelog and a plain-language business summary from ledger and pipeline evidence, bounded by version or sprint identifier.

---

## Project Extension — Vision

The Team Extension operates within a sprint. The Project Extension operates above it.

**What it addresses:** Teams running multiple parallel workstreams — or managing a portfolio of products — need structural awareness that spans sprints: cross-sprint dependency tracking, capacity signals that account for work in flight across multiple repos, and reporting surfaces that speak to stakeholders who never open a sprint board.

**Capabilities envisioned:**

- **Cross-sprint continuity** — session-continuity and ledger infrastructure extended across sprint boundaries. Decisions and structural changes from Sprint N are surfaced in Sprint N+1 planning without manual carry-forward. Multi-sprint epics maintain a living state record across sessions and contributors.
- **Portfolio-level signals** — aggregated digest across multiple active sprints or products. Engineering manager and delivery manager views: what completed, what is blocked, what structural changes occurred, where Red zone TODOs remain unresolved across the portfolio.
- **Cross-team dependency tracking** — when two teams' work intersects at a shared interface or module, the framework surfaces the dependency before both teams have committed implementation work. Interface contract ledger entries are the raw signal; the Project Extension makes them cross-team visible.
- **Stakeholder reporting surface** — sprint review business artifacts aggregated across multiple teams into a single stakeholder briefing. Produced from pipeline evidence; narrated and approved by humans. The framework does not replace stakeholder conversation — it removes the preparation labor.

**What it is not:**

- A project management tool (it does not replace Jira, Linear, or Azure DevOps)
- A portfolio management system (it does not track resource allocation or budget)
- An autonomous decision-maker (humans remain the decision layer at every level)
- A replacement for the Team Extension (it requires Team Extension infrastructure as its foundation)

**Current state:** Vision only. Scoping begins after Phase 5 is in production use and its gaps are known.

---

## Related Artifacts

| Type | Location | Notes |
|---|---|---|
| Public framework root | `devflow/` (public) | Devflow v1 — individual framework |
| Team extension root | `devflow-team/` (private) | Phases 1–4 complete; Phase 5 planned |
| Public team landing | `devflow/team/README.md` (public) | Describes team extension; links to access request |
| Access request guide | `devflow/team/GETTING-ACCESS.md` (public) | Instructions to request devflow-team access |
| Team manual | `devflow-team/USER-MANUAL-TEAM.md` (private) | Full team framework manual |
| This document | `devflow/docs/vision/devflow-extensions.md` (public) | Extensions vision — team and project |
| Detailed requirements | `devflow-team/docs/vision/team-extension-requirements.md` (private) | Full domain decisions, phase deliverables, acceptance criteria |
