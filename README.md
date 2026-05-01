# Devflow

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) custom skills and worker agent definitions that enforce disciplined, pipeline-routed AI-assisted development workflows.

The framework routes every task through a named pipeline of specialized workers — planner, implementer, tester, reviewer, checker — before any code, test, or documentation is written. Workers self-identify, stay in role, and produce structured output. No silent fallback to generic behavior.

For full usage guidance, pipeline descriptions, and examples see [USER-MANUAL.md](USER-MANUAL.md).

## What's Inside

### Skills (`skills/`)

Reusable process guides that Claude Code invokes via slash commands. Each skill lives in its own directory with a `SKILL.md` file.

| Skill | Purpose |
|---|---|
| `using-devflow` | Router/gatekeeper — selects the correct named pipeline and routes every task through it before any work begins |
| `writing-plans` | Structured implementation planning before coding |
| `test-driven-development` | RED-GREEN-REFACTOR cycle enforcement |
| `systematic-debugging` | Root-cause analysis before proposing fixes |
| `brainstorming` | Explores intent, requirements, and design before implementation |
| `interview` | Structured requirements extraction through one-at-a-time questioning |
| `adr-writer` | Documents significant architectural decisions in `docs/decisions/` before implementation begins |
| `writing-skills` | TDD-based approach to creating and testing new skills |
| `find-bugs` | Security and code quality audit of local branch changes |
| `code-simplifier` | Orchestrates code cleanup for clarity and consistency while preserving behavior |
| `requesting-code-review` | Verifies work meets requirements before merging |
| `receiving-code-review` | Enforces technical rigor when processing review feedback |
| `verification-before-completion` | Evidence-based verification before claiming work is done |
| `dispatching-parallel-agents` | Parallelizes independent tasks across subagents for concurrent execution |
| `subagent-driven-development` | Executes plans with independent implementation agents |
| `executing-plans` | Runs implementation plans with review checkpoints |
| `finishing-a-development-branch` | Guides branch completion — merge, PR, or cleanup |
| `using-git-worktrees` | Creates an isolated git worktree and feature branch before implementation begins |
| `spike-executor` | Orchestrates the full spike/POC lifecycle — hypothesis → experiment → decision |
| `poc-retrospective` | Captures spike decision, learnings, carry-forwards, and cleanup after an investigation |
| `hypothesis-validator` | Designs and runs a minimal experiment to test one specific technical assumption |
| `session-continuity` | Writes/reads structured state snapshots for multi-session work |

### Agents (`agents/`)

Worker agent definitions that pipelines route tasks to. Each agent has a focused role, strict boundaries, and a model chosen for its cognitive tier.

| Agent | Role | Model |
|---|---|---|
| `task-planner` | Translates tasks into minimal, executable implementation plans | Opus |
| `context-mapper` | Traces dependency blast area and writes a context map for downstream workers | Haiku |
| `feature-implementer` | Implements one scoped plan step with minimal diff | Sonnet |
| `test-engineer` | Writes/updates tests, regression coverage, and edge cases | Sonnet |
| `code-reviewer` | Reviews correctness, regressions, standards, and test adequacy | Sonnet |
| `acceptance-checker` | Maps implementation to acceptance criteria with evidence | Sonnet |
| `docs-updater` | Keeps documentation aligned with recent code changes | Haiku |
| `api-researcher` | Researches external APIs/libraries and produces implementation guidance | Sonnet |
| `bug-repro-triager` | Produces repro steps, hypotheses, and investigation plans | Sonnet |
| `code-simplification` | Simplifies recently modified code while preserving exact behavior | Sonnet |
| `research` | General-purpose technical research for any domain, library, or concept | Sonnet |
| `spike-investigator` | Hands-on experimentation agent that validates a hypothesis in throwaway mode | Sonnet |
| `technology-selector` | Evaluates technology/library options and produces a single recommendation with trade-offs | Opus |
| `scope-estimator` | Rough effort/complexity sizing per work area before writing a full implementation plan | Sonnet |
| `performance-profiler` | Establishes baselines, identifies hotspots through profiling, defines measurable acceptance criteria before optimization | Sonnet |
| `threat-modeler` | Maps attack surface for a change (inputs, auth paths, trust boundaries, data flows) and produces a threat checklist for security review | Sonnet |
| `dependency-auditor` | Runs ecosystem-native scanners (npm/pip/cargo audit), flags CVEs, license issues, and outdated pins | Sonnet |
| `interface-designer` | Defines interface contracts (OpenAPI 3.x specs, TypeScript interfaces, AsyncAPI schemas) before implementation begins | Sonnet |

**Model tiers:** Opus for high-stakes reasoning (planning, architecture decisions); Haiku for mechanical tasks (dependency mapping, doc sync); Sonnet for everything in between.

## Pipelines

`using-devflow` maps every task to one of eleven named pipelines:

| # | Name | Default worker sequence |
|---|------|------------------------|
| 0 | Requirements gathering | `interview → brainstorming → scope-estimator → writing-plans` |
| 1 | Spike / POC investigation | `research → spike-investigator → poc-retrospective` |
| 2 | Unfamiliar API / library | `api-researcher` → transition to Pipeline 3 |
| 3 | New feature / behavior change | `task-planner → feature-implementer → test-engineer → code-reviewer → acceptance-checker` |
| 4 | Bug fix / runtime failure | `bug-repro-triager → test-engineer → feature-implementer → code-reviewer → acceptance-checker` |
| 5 | Refactor / simplification | `task-planner → code-simplifier → code-reviewer → acceptance-checker` |
| 6 | Test-only | `test-engineer → code-reviewer` |
| 7 | Review-only | `code-reviewer` |
| 8 | Docs-only | `docs-updater` |
| 9 | Performance / optimization | `performance-profiler → test-engineer → feature-implementer → code-reviewer → acceptance-checker` |
| 10 | Security audit | `threat-modeler → dependency-auditor → find-bugs` |

Each pipeline defines Variants (optional additions), Notes (discipline rules), and a Transition (what happens when the pipeline completes or loops back).

## Installation

Copy skills and agents into your Claude Code configuration directory:

```sh
# Skills
cp -r skills/* ~/.claude/skills/

# Agents
cp -r agents/* ~/.claude/agents/
```

Then add the routing instruction to your `~/.claude/CLAUDE.md`:

```markdown
For EVERY task — no exceptions — invoke the `using-devflow` skill before doing any work.
```

## How It Works

1. Every task triggers `using-devflow` first
2. The skill selects a named pipeline and announces the ordered worker sequence
3. Each worker self-identifies, stays in role, and produces structured output
4. Workers transition to the next worker in the pipeline — or loop back if review feedback or acceptance gaps require it
5. No silent fallback to generic behavior — routing is always visible and auditable

## License

MIT
