# Skills & Agents

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) custom skills and agent definitions that enforce disciplined, worker-routed AI-assisted development workflows.

## What's Inside

### Skills (`skills/`)

Reusable process guides that Claude Code invokes via slash commands. Each skill lives in its own directory with a `SKILL.md` file.

| Skill | Purpose |
|---|---|
| `using-devflow` | Router/gatekeeper — routes every task through the correct worker agent pipeline before any work begins |
| `writing-plans` | Structured implementation planning before coding |
| `test-driven-development` | RED-GREEN-REFACTOR cycle enforcement |
| `systematic-debugging` | Root-cause analysis before proposing fixes |
| `brainstorming` | Explores intent, requirements, and design before implementation |
| `interview` | In-depth user interviewing to create detailed specs |
| `writing-skills` | TDD-based approach to creating and testing new skills |
| `find-bugs` | Security and code quality review of local branch changes |
| `code-simplifier` | Refines code for clarity and consistency while preserving behavior |
| `requesting-code-review` | Verify work meets requirements before merging |
| `receiving-code-review` | Technical rigor when processing review feedback |
| `verification-before-completion` | Evidence-based verification before claiming work is done |
| `dispatching-parallel-agents` | Parallelizes independent tasks across subagents |
| `subagent-driven-development` | Executes plans with independent implementation agents |
| `executing-plans` | Runs implementation plans with review checkpoints |
| `finishing-a-development-branch` | Guides branch completion — merge, PR, or cleanup |
| `using-git-worktrees` | Creates an isolated git worktree and feature branch before implementation begins |
| `spike-executor` | Orchestrates the full spike/POC lifecycle — hypothesis → experiment → decision |
| `poc-retrospective` | Captures spike decision, learnings, carry-forwards, and cleanup after an investigation |
| `hypothesis-validator` | Designs and runs a minimal experiment to test one specific technical assumption |
| `session-continuity` | Writes/reads structured investigation state snapshots for multi-session work |

### Agents (`agents/`)

Worker agent definitions that skills route tasks to. Each agent has a focused role and strict boundaries.

| Agent | Role |
|---|---|
| `task-planner` | Translates tasks into minimal, executable implementation plans |
| `feature-implementer` | Implements one scoped plan step with minimal diff |
| `test-engineer` | Writes/updates tests, regression coverage, edge cases |
| `code-reviewer` | Reviews correctness, regressions, standards, test adequacy |
| `acceptance-checker` | Maps implementation to acceptance criteria with evidence |
| `docs-updater` | Keeps documentation aligned with recent code changes |
| `api-researcher` | Researches external APIs/libraries and produces guidance |
| `bug-repro-triager` | Produces repro steps, hypotheses, and investigation plans |
| `code-simplification` | Simplifies recently modified code while preserving behavior |
| `research` | General-purpose technical research for any domain, library, or concept |
| `spike-investigator` | Hands-on experimentation agent that validates a hypothesis in throwaway mode |
| `technology-selector` | Evaluates technology/library options and produces a single recommendation with trade-offs |
| `scope-estimator` | Rough effort/complexity sizing per work area before writing a full implementation plan |

## Installation

Copy skills and agents into your Claude Code configuration directory:

```sh
# Skills
cp -r skills/* ~/.claude/skills/

# Agents (if supported by your setup)
cp -r agents/* ~/.claude/agents/
```

Then add the routing instruction to your `~/.claude/CLAUDE.md`:

```markdown
For EVERY task — no exceptions — invoke the `using-devflow` skill before doing any work.
```

## How It Works

1. Every task triggers `using-devflow` first
2. The skill selects an ordered pipeline of worker agents (e.g. `task-planner -> feature-implementer -> test-engineer -> code-reviewer`)
3. Each worker self-identifies, stays in role, and produces structured output
4. No silent fallback to generic behavior — routing is always visible

## License

MIT
