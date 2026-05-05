# Devflow Team Extension

**Devflow Team** extends the [Devflow](https://github.com/yuriyvsavchuk/devflow) individual framework into a team-oriented platform for coordinating multiple AI-assisted contributors within a shared software development process.

The individual Devflow framework makes a single developer more effective in isolation. The team extension addresses what happens next: when multiple AI-accelerated contributors work in parallel, structural decisions propagate faster than awareness does, Scrum ceremonies fall behind the delivery pace, and release governance lags the cadence of change.

---

## What the Team Extension Adds

### AI Trust Zones

A formal per-project classification that determines how much AI involvement is appropriate for each area of the codebase — from fully AI-generated infrastructure code to human-authored authentication and business calculation logic. Enforced through pipeline behavior and Git review levels, not arbitrary rules.

### Comprehension Gate

A structured author-produced summary required before any code review begins. Ensures that developers own the code in their pull requests — understanding what it does and why — regardless of how it was produced.

### Structural Ledger

A version-controlled index of structurally significant changes: interface contract updates, architectural decisions, module boundary changes, security constraints. Auto-populated as a side effect of running pipelines. Gives every contributor a shared, searchable record of what changed and when — without requiring additional documentation effort.

### Decision Broadcast

A session-start briefing that filters the decision index to each contributor's working context. New architectural decisions, settled trade-offs, and ruled-out alternatives surface automatically at the start of a session — no searching, no accidental relitigation.

### Specification-Driven Testing Pipeline

A two-pass test pipeline that enforces specification-driven tests before implementation begins, with an independent test audit step that distinguishes tests written from requirements from tests written to match code behavior.

### Scrum Integration

Pre-refinement pipelines for three story types (user stories, production incidents, technical debt) that run asynchronously before ceremonies. Sprint planning artifacts. A daily digest generated from the structural ledger and session state. Sprint review technical artifacts that complement — not replace — existing Jira Sprint Reports.

### Release Governance Support

Continuous release readiness tracking across pipeline completions. Optional SOC2 compliance mode that produces a full requirements-to-delivery traceability chain. Feature flag lifecycle management with mandatory removal deadlines. Automated release notes generation in technical and business formats.

---

## Who It Is For

Enterprise software development teams that include developers, QA/SDET, BA, DevOps, SRE, and customer support — working in Scrum or Agile-adjacent processes with AI-assisted development tools.

The extension is most valuable when:

- Multiple contributors are working in parallel on the same codebase with AI assistance
- Structural decisions are being made faster than the team can communicate them through existing channels
- Scrum refinement and planning ceremonies are becoming friction points as the pace of delivery accelerates
- Release governance (Go/NoGo, sign-offs, compliance evidence) is assembled manually from information that already exists in the development process

---

## Design Principles

**Model-agnostic.** Framework logic is expressed in Markdown and YAML — executable by any LLM that can follow structured instructions. Claude Code is the reference implementation. Integration points are standalone scripts.

**No new ceremonies.** Coordination artifacts are produced as side effects of existing pipelines. No separate documentation effort, no additional meetings.

**Compliance modes are optional.** The framework runs without compliance overhead for teams that do not need it. SOC2 traceability and other compliance layers activate via project configuration.

**Phased.** Each capability phase is independently useful. Teams can adopt the trust zone model without the Scrum integration, or the structural ledger without the release governance layer.

---

## Relationship to the Individual Framework

Devflow Team is an extension, not a replacement. It is built on top of the public [Devflow](https://github.com/yuriyvsavchuk/devflow) framework using an extension model: the individual framework is installed first, and the team extension adds new components alongside targeted modifications to existing ones.

The individual framework remains fully open-source under the MIT license. The team extension is separately licensed and available to granted collaborators.

---

## Getting Access

See [GETTING-ACCESS.md](GETTING-ACCESS.md) for instructions on requesting access to the private `devflow-team` repository.
