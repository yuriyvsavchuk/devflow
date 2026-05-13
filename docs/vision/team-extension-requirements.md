# Devflow Team Extension — Requirements & Vision

**Date:** 2026-05-04
**Status:** Requirements settled — ready for implementation planning
**Author:** Yuriy Savchuk + Claude (collaborative session)
**Next action:** Open implementation plans per phase, starting with Phase 1 (Coding Practices foundation)

---

## Purpose

This document captures the settled requirements and design decisions for extending Devflow from a solo-practitioner framework into a team-oriented platform for enterprise software development.

**Target:** Enterprise software product and project teams with full role coverage — developers, QA/SDET, BA, DevOps, SRE, customer support. Not targeting a specific project or team configuration.

**Design authority:** Requirements and decisions derived from experience across software developer, team lead, scrum master, delivery manager, and engineering manager roles.

Devflow v1 (current) makes one developer more effective in isolation by enforcing disciplined pipeline-routed development. This extension addresses the coordination gap: when multiple AI-accelerated contributors work in parallel, the framework must ensure structural awareness, decision propagation, and sustainable team rhythm — not just individual discipline.

---

## Immutable Design Principles

These principles govern every implementation decision. They were established through the requirements discussion and cannot be relaxed without explicit revision.

1. **Model-agnostic from day one.** Framework logic (pipelines, routing rules, agent definitions, templates) is expressed in Markdown and YAML — executable by any LLM that can follow structured instructions. Claude Code is the reference implementation. Integration points (git hooks, Jira, ledger writes) are implemented as standalone scripts invokable by any LLM as tools. No Claude-specific API calls in framework logic.

2. **Coordination artifacts are pipeline side effects, not ceremonies.** Every new mandatory step must be the natural output of an existing pipeline step. Coordination overhead that requires a separate contributor action defeats the AI-acceleration benefit.

3. **Push over pull for critical structural information.** Contributors should not need to know to look for decisions. The framework delivers relevant information to their working context automatically.

4. **Framework produces evidence; humans make decisions.** No gate, approval, or release decision is automated. The framework pre-assembles evidence packages; humans act on them.

5. **Compliance modes are optional layers.** Framework runs without compliance overhead for teams that do not require it. SOC2 mode and other compliance layers activate via project configuration.

6. **Phased delivery — each phase works independently.** Phase 1 is useful without Phase 2. Do not couple phases.

7. **No technical blocking for process guidance.** The framework provides guardrails through process and tooling, not hard locks. Team leads enforce compliance through people management.

---

## Problem Statements

### Problem 1 — Contributor Isolation and Structural Drift

AI-accelerated contributors accumulate structural assumptions — architecture decisions, interface changes, module boundaries — faster than teammates can track through normal review cycles. A decision made in the morning is baked into three modules by the next day. The teammate who would have caught the conflict finds it at code review, when reversing it is expensive.

**Root cause:** Pipeline outputs (ADRs, interface contracts, context maps) are local files. Nothing notifies other contributors that structurally significant changes occurred.

### Problem 2 — Technical Decision Communication Gap

ADRs and interface contracts exist but there is no mechanism to push decision awareness into teammates' working contexts. A contributor starting a new session has no automated signal that a relevant decision was made while they were away.

### Problem 3 — Scrum Friction at AI-Accelerated Pace

Refinement and Planning ceremonies are the most friction-filled events when development pace accelerates. The estimation and decomposition work they perform can be largely shifted to async, AI-assisted pipelines — reducing ceremony time and improving the quality of inputs.

### Problem 4 — Release Governance Lag

Approval and compliance structures designed for 2–3 month release cycles create bottlenecks at 1–2 week cycles. Evidence collection for Go/NoGo meetings and sign-offs is manual assembly of already-known information.

---

## Settled Decisions by Domain

### Domain 1 — Coding Practices

#### AI Trust Zones

Code is classified into three zones per project. The team lead owns the classification. Git-based branch protection enforces review level independently — no separate Devflow enforcement layer.

| Zone | Label | AI Involvement | Examples |
|---|---|---|---|
| **Green** | AI-authored | AI writes; developer reviews for correctness | Logging, boilerplate, infrastructure wiring, interface stubs |
| **Yellow** | AI-assisted | Developer writes; AI proposes; developer decides | Solution structure, data analysis algorithms, compliance checks |
| **Red** | Human-authored | Developer writes from scratch; AI may scaffold structure only | Authentication and role models, business calculation logic, critical state machine transitions |

**Trust zone configuration:** Declared in `devflow-trust.yaml` at project root. Managed by team lead.

#### Mixed-Zone Pipeline Behavior

- Developer declares scope of each pipeline run against `devflow-trust.yaml`
- `feature-implementer` generates Green and Yellow zones; stops at Red zone boundaries
- At every Red zone location skipped, the agent inserts: `TODO: [RED ZONE — human authorship required: <description>]`
- A `grep` or CI check verifies no Red zone TODOs remain unresolved before merge

#### PR Comprehension Summary

- Author-produced; positioned between `feature-implementer` and `code-reviewer`
- Required before code review begins
- Reviewer may optionally initiate an additional checklist step if further confirmation is needed

**Comprehension summary format:**
```markdown
## Comprehension Summary

**What this change does:** [author's own words — no copying from commit message]

**Critical sections I understand:**
- [file/function]: [what it does and why]

**Red zone code in this PR:** [list or "none"]
- If present: [explain the logic and why it is correct]

**AI-generated sections I did not author:** [list or "none"]
- If present: [describe validation performed to confirm correctness]
```

#### Contributor Tier Model

Three tiers. Guidance only — no technical blocking. Team lead enforces through process.

| Tier | AI generation access | Required process |
|---|---|---|
| **L1 — Junior** | Green zone only; Yellow/Red must be human-authored | Comprehension summary mandatory for every PR; Red zone requires senior co-review |
| **L2 — Mid** | Green and Yellow zones | Comprehension summary mandatory for Red-adjacent changes |
| **L3 — Senior/Lead** | All zones | Comprehension summary required for Red zone only |

#### Additional Decisions

- Post-merge AI provenance tracking: **not required**. Comprehension summary at merge time is sufficient.
- Domain-aware reviewer: **not formalized**. Technical reviewer and domain expert are the same person by convention.
- Legacy system risk: Managed through **reviewer pairing** — eliminates bus factor and forces knowledge transfer. `legacy-risk` flag in pre-refinement output triggers Yellow zone treatment for affected modules regardless of trust zone classification.

---

### Domain 2 — QA and Testing

#### Specification-Driven Testing as Primary Mechanism

Specification-driven tests are the primary black-box quality mechanism and a required part of business acceptance. `test-engineer` runs in two passes:

1. **First pass (spec-driven):** Reads acceptance criteria only — implementation files blocked. Runs in parallel with coding, not after. Produces the black-box test contract.
2. **Second pass (implementation-aware, optional):** Reads implementation for supplementary edge-case coverage after the first pass is complete.

#### AI Trust Zones Applied to Tests

| Zone | Test type | AI involvement | Constraint |
|---|---|---|---|
| **Green** | Unit tests for non-critical functions | AI writes; developer reviews | Standard review |
| **Yellow** | Integration tests, API contract tests | AI drafts; developer validates assertions | Assertions require explicit developer review |
| **Red** | Business logic, auth/role, financial calculation | AI scaffolds structure only | **Assertions must be human-authored** |

#### Commented Assertion Pattern (Red Zone)

For Red zone tests, AI generates the expected assertion as commented-out code. Developer must explicitly uncomment as the act of verification. Without uncommenting, the test is inert. The uncomment action is the forcing function — it proves the assertion was reviewed, not passively accepted.

```python
# result = calculate_tax(income=50000, rate=0.21)
# ASSERT [RED ZONE — verify and uncomment]:
# assert result == 10500.00, f"Expected 10500.00, got {result}"
```

#### Test Reviewer Sub-Agent

A dedicated `test-reviewer` sub-agent inserted after `test-engineer`, before `code-reviewer`. Goal: independent audit of test quality based on specification compliance — not structure, naming, or coverage metrics. Primary function: detect implementation-driven tests (written from code behavior) masquerading as specification-driven tests (written from requirements).

This is the primary safeguard against the developer mindset risk: developers writing automated tests tend toward implementation-driven assertions. The `test-reviewer` audits independently.

#### Testing by Layer

| Layer | Owner | AI involvement | Constraint |
|---|---|---|---|
| Spec-driven / black-box | SDET (primary) or developer (shift-left) | Yellow: AI drafts, human validates assertions | First pass before implementation |
| Unit / white-box | Developer | Green/Yellow per trust zone | Standard comprehension summary |
| E2E scenarios | SDET (from exploratory knowledge) | Yellow: human authors scenario; AI translates to test code | Scenario authorship is human-only |
| Performance | Engineering / SRE | AI scaffolds load scripts; human defines thresholds | **Threshold is a required field — pipeline blocks if absent** |
| Security | External team + internal Veracode | Green: AI runs known-pattern checks only | AI is first-pass filter only; external audit is the gate |

#### Shift-Left Role Clarification

- Developers write specification-driven tests in shift-left context
- SDET role shifts to: test architecture, tooling ownership, quality governance, and test-reviewer function
- SDETs may still author individual automated tests, particularly E2E scenarios
- `test-reviewer` sub-agent is the structural safeguard against developer implementation-mindset bias in tests

---

### Domain 3 — Scrum / Agile Practices

#### Story Input Sources

Three types of sprint input, each handled by a distinct pre-refinement template:

| Type | Primary source | Template |
|---|---|---|
| `user-story` | Product Owner (business requirements) | Interview → acceptance criteria → scope-estimator → DoR checklist |
| `incident` | Production bugs, customer success team | Root cause context → impact → acceptance criteria → scope-estimator → DoR checklist |
| `tech-debt` | Technical backlog | Problem statement → affected modules → acceptance criteria → scope-estimator → DoR checklist |

Sprint scope = compromise between PO priority and dev team capacity. Framework supports, not overrides, this negotiation.

#### Pre-Refinement Pipeline

Runs asynchronously before the refinement ceremony. Output per story:
- Clarified story with acceptance criteria
- `scope-estimator` complexity rating and confidence level mapped to story points
- Explicit assumptions list
- **Definition of Ready (DoR) checklist** — unresolved external dependencies flagged as blockers

Refinement ceremony shifts from estimation-and-decomposition to: review pre-refinement output, challenge assumptions, and resolve cross-story dependencies. Story dependencies are a refinement topic; planning receives already-dependency-cleared stories.

#### Sprint Planning Artifact

Produced before the planning ceremony:
- Refined stories with scope-estimator ratings (mapped to story points for Scrum metric continuity)
- Capacity snapshot from open session-continuity files
- Sprint goal field (team-completed)
- Suggested sprint scope at team-set confidence threshold

Planning ceremony = validation and commitment, not construction.

#### Daily Digest (`devflow:daily-digest`)

Auto-generated before standup from ledger and session-continuity snapshots. Content:
- Structural changes since previous digest (from ledger)
- New ADRs settled (from decision index)
- Open Red zone TODOs across the team
- In-progress pipeline runs per contributor

**Explicit incompleteness label (required):**
> *The following reflects Devflow pipeline activity only. Changes made outside pipelines are not included — report them in standup.*

Activities reported verbally in standup can be appended to the digest via AI transcription tools. Digest is a living artifact, updated after standup if needed.

#### Sprint Review Artifacts

**Technical artifact** (internal, auto-generated):
- Completed pipeline runs with acceptance-checker evidence
- Structural changes from ledger
- ADR index delta
- Test coverage delta
- Open items carried forward
- Structured to complement — not replace — existing Jira Sprint Report and test coverage exports

**Business artifact** (external, human-narrated):
- Live demo with stakeholder conversation — unchanged from current practice
- Acceptance criteria from `task-planner` serve as demo script structure
- Technical artifact provides completeness evidence the presenter references

#### Jira Integration

Three integration levels, all supported:
1. **API** (primary): automated ticket status updates, evidence linking, acceptance criteria closure
2. **Import/export files** (fallback): semi-automatic or manual Jira working item updates
3. **Human-mediated** (baseline): contributor acts as interface; framework produces artifacts in Jira-compatible format

Scrum metric continuity preserved: `scope-estimator` output maps to story points; velocity remains calculable from framework outputs.

---

### Domain 4 — Release Processes

#### Continuous Release Readiness Tracking

Each completed pipeline run (acceptance-checker passed) contributes to a release readiness record:

| Check | Source |
|---|---|
| Feature complete | acceptance-checker evidence |
| Tests passed | test-reviewer cleared + spec-driven suite green |
| Security scanned | Veracode / internal scan result attached |
| Review complete | code-reviewer cleared + comprehension summary present |
| Documentation updated | docs-updater ran (if applicable) |

At any point, the release readiness artifact shows: stories fully ready, stories pending specific gates, open blockers. Go/NoGo meeting (when present) reviews the artifact — it does not construct it.

**Approval models supported:**
- Go/NoGo meeting: artifact distributed before meeting; meeting addresses exceptions only
- Sign-off model: same artifact routed to named approvers (Engineering, Business, Infrastructure) for async approval

#### SOC2 Compliance Mode

**Optional.** Activated by `compliance: soc2` in `devflow-trust.yaml`.

When enabled, all pipeline steps produce timestamped, named evidence records forming a full traceability chain:

| Traceability link | Framework evidence |
|---|---|
| Requirements → implementation | task-planner acceptance criteria → feature-implementer PR |
| Implementation → quality verification | PR comprehension summary → test-reviewer clearance → acceptance-checker evidence |
| Quality verification → distribution set | Release readiness artifact → release notes |
| Distribution set → delivery | Release notes → deployment record |

Each record includes: who performed the action, when, and what the outcome was. Evidence format compatible with Git records, Jira records, and release notes — the formats auditors already accept.

**Other compliance types:**
- Financial, GDPR compliance: handled at requirements level (pre-refinement template); verification outside framework scope
- Future compliance extensions: implementable as separate optional layers

#### Feature Flag Lifecycle

Decision makers: PO (business reasons) and/or tech lead (technical reasons), independently.

Required fields:
- Flag name
- Default state (always `off` for new features)
- Owner (PO, tech lead, or both)
- **Removal deadline** (mandatory)

Optional fields:
- Rollout strategy (percentage, user segment, internal-first)
- Activation conditions

Flag state may be changed after informal customer communication — framework records the change, does not require formal justification.

Lifecycle stages managed by framework:
1. **Declaration** — at pre-refinement or task-planner stage
2. **Implementation** — code written behind flag from the start
3. **Activation** — per rollout strategy or ad hoc decision
4. **Removal** — triggered by deadline; cleanup is a tracked pipeline run

#### Release Notes (`devflow:release-notes`)

Auto-generated from ledger + pipeline evidence, bounded by version/date/sprint identifier.

**Technical format** (for engineering and DevOps): structured changelog with PR links, ADR references, breaking changes, trust zone changes.

**Business format** (for internal stakeholders): plain language summary requiring human review before distribution.

Ownership: engineering produces, product management approves. Internal teams are primary audience. External customer-facing format is a future extension.

---

### Domain 5 — Cross-Cutting Risks

#### Partial Ledger Risk

Digest carries explicit incompleteness label at all times. Future option: git hook integration to flag commits without corresponding pipeline runs. Not required for initial implementation.

#### Legacy System Risk

Managed through reviewer pairing — not pipeline classification alone. When `legacy-risk` flag is set in pre-refinement output:
- Affected modules treated as Yellow zone regardless of trust zone file
- Reviewer must be a contributor with documented knowledge of the legacy behavior
- Reviewer pairing eliminates bus factor and drives knowledge sharing

#### Model-Agnosticism (Strict)

Framework logic: Markdown and YAML only. No LLM-specific syntax, API calls, or tool bindings in pipeline definitions, agent files, or skill files.

Integration points (git hooks, Jira connector, ledger writer): implemented as standalone scripts callable as generic tool use by any LLM.

Claude Code is the reference implementation and preferred runtime. Any LLM capable of following structured Markdown instructions can execute the framework.

---

## New Framework Components

### New Skills

| Skill | Purpose | Domain |
|---|---|---|
| `devflow:sync-context` | Session-start briefing — filters ADR index and ledger to contributor's working context | 1, 2 |
| `devflow:daily-digest` | Auto-generated standup digest from ledger + session-continuity | 3 |
| `devflow:sprint-review` | Sprint review technical artifact — ledger query + pipeline completion evidence | 3 |
| `devflow:release-notes` | Release notes generation from ledger + acceptance evidence | 4 |
| `devflow:pre-refinement` | Story clarification pipeline — three templates (user-story, incident, tech-debt) | 3 |
| `devflow:sprint-planning` | Sprint planning artifact — scope-estimator outputs + capacity snapshot | 3 |

### New Agents

| Agent | Purpose | Domain |
|---|---|---|
| `ledger-writer` | Writes structured ledger entries as final step of structural pipelines | 1, 2 |
| `test-reviewer` | Independent audit of test quality against specification compliance | 2 |

### New Configuration

| File | Purpose | Domain |
|---|---|---|
| `devflow-trust.yaml` | Per-project trust zone classification, compliance mode, legacy risk flags | 1, 4 |
| `docs/ledger/index.md` | Auto-updated ledger index, sorted by date, tagged by subsystem | 1 |
| `docs/decisions/index.md` | Auto-updated ADR index with tags and subsystem links | 1 |

### Modified Existing Components

| Component | Change | Domain |
|---|---|---|
| `test-engineer` | Two-pass structure; spec-driven pass reads spec only (implementation blocked) | 2 |
| `feature-implementer` | Respects trust zone boundaries; inserts Red zone TODO annotations | 1 |
| `code-reviewer` | Checks for comprehension summary before proceeding | 1 |
| `adr-writer` | Writes ledger entry + updates decision index on completion | 1 |
| `interface-designer` | Writes ledger entry on contract creation/update | 1 |
| `task-planner` | Accepts pre-refinement artifact as input; outputs acceptance criteria for test-engineer first pass | 3 |
| `session-continuity` | Read mode optionally invokes `sync-context` for team decision briefing | 1 |

### New Pipeline Steps

| Step | Position | Domain |
|---|---|---|
| Comprehension summary | Between `feature-implementer` and `code-reviewer` | 1 |
| `test-reviewer` | After `test-engineer`, before `code-reviewer` | 2 |
| Ledger write | Final step in structural pipelines (P3 with interface-designer, P0 with adr-writer) | 1 |
| DoR checklist | Final step in pre-refinement pipeline | 3 |
| Release readiness update | After acceptance-checker passes | 4 |

---

## Implementation Phases

### Phase 1 — Coding Foundation

Build the trust zone model and comprehension gate. These are independent of team coordination infrastructure and deliver immediate value to individual contributors.

**Deliverables:**
- `devflow-trust.yaml` schema and documentation
- `feature-implementer` trust zone boundary behavior + Red zone TODO annotations
- Comprehension summary template and `code-reviewer` integration
- Contributor tier model documented in USER-MANUAL.md
- `legacy-risk` flag in pre-refinement output

**Acceptance criteria:**
- Running a P3 pipeline on a mixed-zone feature produces TODO annotations at Red zone boundaries
- `code-reviewer` blocks if comprehension summary is absent
- Trust zone classification can be declared and modified by team lead

### Phase 2 — Structural Ledger and Decision Broadcast

Build the shared artifact infrastructure before the session-start briefing.

**Deliverables:**
- `ledger-writer` agent
- Ledger entry format and `docs/ledger/index.md` auto-update
- ADR front-matter tagging convention and `docs/decisions/index.md` auto-update
- `adr-writer` and `interface-designer` updated to write ledger entries
- `devflow:sync-context` skill
- `session-continuity` read mode integration (optional sync-context invocation)

**Acceptance criteria:**
- P3 pipeline with interface-designer produces a ledger entry and updates the index
- `sync-context` returns a ≤5 item briefing filtered to the contributor's working subsystems
- ADRs tagged for unrelated subsystems do not appear in the briefing

### Phase 3 — QA Pipeline Extension

Build specification-driven test infrastructure on top of Phase 1 trust zone foundation.

**Deliverables:**
- Two-pass `test-engineer` (spec-driven first, spec-blocked from implementation)
- Commented assertion pattern for Red zone tests
- `test-reviewer` sub-agent
- E2E scenario template (human-authored scenario → AI-translated test code)
- Performance test threshold field (required; pipeline blocks if absent)

**Acceptance criteria:**
- `test-engineer` first pass cannot read implementation files
- Red zone test assertions are generated as commented code; pipeline flags if any remain uncommented at review
- `test-reviewer` identifies and flags implementation-driven assertions in specification-driven test files

### Phase 4 — Scrum Integration

Build the Agile ceremony support layer.

**Deliverables:**
- `devflow:pre-refinement` skill with three input templates
- `devflow:sprint-planning` artifact
- `devflow:daily-digest` skill with explicit incompleteness label
- `devflow:sprint-review` technical artifact
- Jira integration layer (API + file import/export + human-mediated baseline)

**Acceptance criteria:**
- Pre-refinement produces DoR checklist with unresolved dependencies flagged
- Daily digest is generated from ledger and session-continuity with incompleteness label
- Sprint review artifact complements (does not replace) Jira Sprint Report

### Phase 5 — Release Governance

Build the release readiness and compliance layer.

**Deliverables:**
- Continuous release readiness tracking (per completed pipeline)
- SOC2 compliance mode in `devflow-trust.yaml`
- Feature flag lifecycle template with required removal deadline
- `devflow:release-notes` skill (technical + business formats)
- Approval workflow (Go/NoGo artifact + sign-off routing)

**Acceptance criteria:**
- Release readiness artifact shows complete status per story without manual assembly
- SOC2 mode produces full requirements → delivery traceability chain
- Feature flag removal deadline triggers cleanup pipeline at deadline

### Phase 6 — Project Management Extension (Future)

Cross-sprint planning, dependency tracking, stakeholder reporting, capacity modeling. Not yet scoped — opens after Phase 5 is in production use and its gaps are known.

---

## Open Questions

| # | Question | Phase |
|---|---|---|
| Q1 | What is the minimum ledger entry that is useful without becoming noise for large teams? | 2 |
| Q2 | How does sync-context handle a contributor whose working context spans many subsystems (briefing overflow)? | 2 |
| Q3 | Should "ruled out" alternatives in ADRs surface with higher priority than settled decisions in the briefing? | 2 |
| Q4 | At what team size does the ledger require a UI or query interface to remain navigable? | 6 |
| Q5 | How does the framework behave in monorepo vs. multi-repo setups — one devflow-trust.yaml or many? | All |
| Q6 | What is the integration contract between devflow:pre-refinement and existing Jira story creation workflows? | 4 |

---

## Repository Structure

### Public repository — `devflow` (`github.com/yuriyvsavchuk/devflow`)

License: MIT. Individual framework — all files publicly visible.

```
devflow/
  skills/                         ← individual framework skills
  agents/                         ← individual framework agents
  tools/                          ← lint-framework.py and other tools
  USER-MANUAL.md                  ← individual framework manual
  README.md
  team/
    README.md                     ← what the team extension is, who it's for
    GETTING-ACCESS.md             ← how to request access to devflow-team
```

### Private repository — `devflow-team`

Granted access only. Extension model — contains new components and modified versions of individual framework components.

```
devflow-team/
  skills/                         ← new and modified skills
  agents/                         ← new and modified agents
  config/
    devflow-trust.yaml.template
  docs/
    vision/                       ← this requirements document and future specs
  USER-MANUAL-TEAM.md             ← full team manual (private)
```

---

## Related Artifacts

| Type | Location | Notes |
|---|---|---|
| Public framework root | `devflow/` (public) | Current v1 individual framework |
| Team extension root | `devflow-team/` (private) | Team extension — granted access |
| Public team landing | `devflow/team/README.md` (public) | Describes team extension; links to access request |
| Access request guide | `devflow/team/GETTING-ACCESS.md` (public) | Instructions to request devflow-team access |
| Team manual | `devflow-team/USER-MANUAL-TEAM.md` (private) | Full team framework manual |
| Framework routing skill | `devflow/skills/using-devflow/SKILL.md` | Modified in devflow-team to add team pipelines |
| ADR writer agent | `devflow/agents/adr-writer.agent.md` | Phase 2 integration point — modified in devflow-team |
| Interface designer agent | `devflow/agents/interface-designer.agent.md` | Phase 2 integration point — modified in devflow-team |
| Session continuity skill | `devflow/skills/session-continuity/SKILL.md` | Phase 2 integration point — modified in devflow-team |
| Lint tool | `devflow/tools/lint-framework.py` | May need team-extension checks in Phase 3+ |
| Individual user manual | `devflow/USER-MANUAL.md` | Individual framework manual — unchanged by team extension |
| This requirements document | `devflow-team/docs/vision/team-extension-requirements.md` | Private |
| MemPalace reference | https://github.com/MemPalace/mempalace | Inspiration for decision broadcast model |
