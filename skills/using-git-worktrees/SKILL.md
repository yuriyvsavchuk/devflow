---
name: using-git-worktrees
description: Use before starting any implementation work — creates an isolated git worktree and feature branch so all development happens in a clean, reversible workspace that does not touch the main branch
framework: devflow
---

# Using Git Worktrees

A git worktree is a second working directory linked to the same repository, with its own independent branch checked out. It lets implementation work happen in total isolation: the main branch stays clean, the feature branch is fully contained, and cleanup is a single command.

This skill creates the isolated workspace. devflow:finishing-a-development-branch is responsible for closing it.

---

## When to Use

- A design or spec is agreed (from devflow:brainstorming or devflow:interview) and implementation is about to begin
- Before invoking devflow:writing-plans, devflow:executing-plans, or devflow:subagent-driven-development
- When starting a spike that needs isolated code changes (devflow:spike-executor)
- Any time you would otherwise create a feature branch with `git checkout -b`

## When NOT to Use

- The change is a one-liner or trivial fix that will be committed directly to main
- A worktree for this feature already exists — verify with `git worktree list` first
- The repository has not been initialized with git

---

## Core Pattern

### Step 1 — Confirm Base Branch State

Before creating anything, verify the repository is in a clean state:

```bash
# Check current branch and status
git status
git branch --show-current
```

**If there are uncommitted changes:** stop and ask whether to stash, commit, or discard before continuing.

**If not on the base branch:** switch to it and pull latest:

```bash
git checkout main        # or master, or the agreed base branch
git pull origin main
```

### Step 2 — Derive Names

From the feature or task description, generate:

**Branch name** — kebab-case, prefixed by type:

| Work type | Prefix | Example |
|---|---|---|
| New feature | `feature/` | `feature/user-authentication` |
| Bug fix | `fix/` | `fix/login-redirect-loop` |
| Refactor | `refactor/` | `refactor/payment-service` |
| Spike / POC | `spike/` | `spike/redis-pubsub-feasibility` |

Keep slugs short (3–5 words max). Avoid dates in branch names — they belong in commit messages.

**Worktree path** — sibling of the project root, same slug as the branch:

```
# If project root is: /home/user/projects/myapp
# Worktree goes at:   /home/user/projects/myapp--user-authentication
```

Convention: project name + double dash + branch slug (without the type prefix). The double dash makes worktrees visually distinct from other project directories.

### Step 3 — Create the Worktree

```bash
git worktree add <worktree-path> -b <branch-name>
```

Full example:

```bash
git worktree add ../myapp--user-authentication -b feature/user-authentication
```

### Step 4 — Verify

```bash
git worktree list
```

Expected output shows two entries: the main repo and the new worktree with its branch.

### Step 5 — Announce and Hand Off

Report exactly:

```
Worktree created:
  Path:   <absolute-path-to-worktree>
  Branch: <branch-name>
  Base:   <base-branch> @ <short-sha>

Next step: open this path as the working directory, then invoke writing-plans or the
agreed execution skill. All implementation work must happen inside this path.
```

---

## Working Inside the Worktree

All subsequent implementation work — file edits, test runs, commits — must happen within the worktree directory, not in the main project directory.

In Claude Code: open a new session pointed at the worktree path, or set the working directory explicitly. Every `git` command run inside the worktree operates on the feature branch; the main repo directory is unaffected.

**Verify you are in the right place at any time:**

```bash
git branch --show-current   # should show the feature branch
git worktree list            # shows all active worktrees
```

---

## Cleanup

Worktree cleanup is handled by devflow:finishing-a-development-branch. Do not remove worktrees manually during development — they are the record of in-progress work.

Emergency cleanup (if needed outside the normal flow):

```bash
# From the main repo directory (not from inside the worktree)
git worktree remove <worktree-path>
git branch -d feature/<slug>          # after merge
git branch -D feature/<slug>          # force delete without merge
git worktree prune                    # remove stale worktree references
```

---

## Quick Reference

```bash
# Create
git worktree add ../myapp--<slug> -b feature/<slug>

# List
git worktree list

# Verify you are in the right worktree
git branch --show-current

# Remove (from main repo directory, after finishing-a-development-branch)
git worktree remove ../myapp--<slug>
```

---

## Common Mistakes

**Creating the worktree inside the project directory**
Nesting worktrees inside the project creates confusion with `.gitignore` and IDE tooling. Always place them as siblings of the project root.

**Starting implementation before creating the worktree**
Commits made on the main branch cannot be moved to a worktree retroactively without rewriting history. Create the worktree first.

**Forgetting to pull latest before branching**
A worktree created from a stale base branch will have conflicts at merge time. Always `git pull` before `git worktree add`.

**Working in the main repo directory instead of the worktree**
File edits made in the wrong directory go to the wrong branch. Confirm `git branch --show-current` before writing any code.

**Manually deleting the worktree directory without `git worktree remove`**
Git keeps a reference to the worktree even after the directory is gone, causing `git worktree list` to show stale entries. Always use `git worktree remove` or `git worktree prune` to clean up.

---

## Related Skills and Agents

- **Preceded by:** devflow:brainstorming or devflow:interview (design/spec must be agreed before creating the workspace)
- **Followed by:** devflow:writing-plans → devflow:subagent-driven-development or devflow:executing-plans
- **Closed by:** devflow:finishing-a-development-branch (handles merge/PR/discard + `git worktree remove`)
- For spikes: devflow:spike-executor may invoke this skill when the spike requires isolated code changes
- Use devflow:session-continuity to record the worktree path in the session snapshot if the work spans multiple sessions
