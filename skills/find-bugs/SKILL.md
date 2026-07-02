---
name: find-bugs
description: Find bugs, security vulnerabilities, and code quality issues in local branch changes. Use when asked to review changes, find bugs, security review, or audit code on the current branch.
framework: devflow
context: fork
agent: general-purpose
---

# Find Bugs

Review changes on this branch for bugs, security vulnerabilities, and code quality issues.

## Phase 0: Artifact Check (Required Before Any Review Work)

This skill runs in its own isolated context (`context: fork`) — it does not see the parent conversation. Upstream security context arrives as **artifacts on disk**, never as conversation state. Before reading any code:

1. If the invocation arguments name artifact paths, use those.
2. Otherwise discover them: the newest `docs/audits/*threat-model*.md` and the newest `docs/audits/*dependency-audit*.md`, if any exist.

**If a threat-model artifact is found:**
- State: `Running with threat-model artifact <path> — review is targeted to its checklist`
- If the artifact predates the newest commit on the branch under review, note that the threat model may be stale
- Skip Phase 2 (Attack Surface Mapping) — the artifact already contains it
- In Phase 3, work through the artifact's threat checklist ranked by priority, not the generic list below — confirm or refute each applicable threat with code-level evidence
- In Phase 3, also incorporate the dependency-audit artifact's CVE and package-risk notes if present — flag call sites for affected packages

**If no threat-model artifact is found (standalone invocation):**
- State: `Running without threat-model context — review uses generic heuristics`
- Note: `For a full change-specific security audit, run the devflow-audit security adapter (threat-modeler → dependency-auditor → find-bugs) first`
- Proceed with Phase 2 (Attack Surface Mapping) as the fallback scoping step
- Proceed with the full generic checklist in Phase 3

Do not skip this check. The review quality and scope depend on which mode applies.

---

## Phase 1: Complete Input Gathering

1. Get the FULL diff: `git diff $(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')...HEAD`
2. If output is truncated, read each changed file individually until you have seen every changed line
3. List all files modified in this branch before proceeding

## Phase 2: Attack Surface Mapping (standalone only — skip if threat-modeler context is present)

For each changed file, identify and list:

* All user inputs (request params, headers, body, URL components)
* All database queries
* All authentication/authorization checks
* All session/state operations
* All external calls
* All cryptographic operations

## Phase 3: Security Review
### With threat-model context: work through the ranked threat checklist from `threat-modeler`, confirming or refuting each applicable threat with code-level evidence
### Without threat-model context: check EVERY item below for EVERY file

* [ ] **Injection**: SQL, command, template, header injection
* [ ] **XSS**: All outputs in templates properly escaped?
* [ ] **Authentication**: Auth checks on all protected operations?
* [ ] **Authorization/IDOR**: Access control verified, not just auth?
* [ ] **CSRF**: State-changing operations protected?
* [ ] **Race conditions**: TOCTOU in any read-then-write patterns?
* [ ] **Session**: Fixation, expiration, secure flags?
* [ ] **Cryptography**: Secure random, proper algorithms, no secrets in logs?
* [ ] **Information disclosure**: Error messages, logs, timing attacks?
* [ ] **DoS**: Unbounded operations, missing rate limits, resource exhaustion?
* [ ] **Business logic**: Edge cases, state machine violations, numeric overflow?

## Phase 4: Verification

For each potential issue:

* Check if it's already handled elsewhere in the changed code
* Search for existing tests covering the scenario
* Read surrounding context to verify the issue is real

## Phase 5: Pre-Conclusion Audit

Before finalizing, you MUST:

1. List every file you reviewed and confirm you read it completely
2. List every checklist item and note whether you found issues or confirmed it's clean
3. List any areas you could NOT fully verify and why
4. Only then provide your final findings

## Output Format

**Prioritize**: security vulnerabilities > bugs > code quality

**Skip**: stylistic/formatting issues

For each issue:

* **File:Line** - Brief description
* **Severity**: Critical/High/Medium/Low
* **Problem**: What's wrong
* **Evidence**: Why this is real (not already fixed, no existing test, etc.)
* **Fix**: Concrete suggestion
* **References**: OWASP, RFCs, or other standards if applicable

If you find nothing significant, say so — do not invent issues.

Do not make changes — just report findings. The requester decides what to address.

## When NOT to Use

- Debugging a known failure — use devflow:systematic-debugging to find root cause first
- Reviewing for code quality or readability only — use devflow:code-reviewer
- The branch has no changes — this skill only reviews branch diffs

## Related Skills and Agents

- **Called by:** devflow:requesting-code-review (as part of pre-merge workflow)
- **Preceded by:** devflow:threat-modeler in the devflow-audit security adapter — its threat-model artifact under `docs/audits/` is the investigation context for this skill; without it, the review operates on generic heuristics
- **Preceded by:** devflow:dependency-auditor — its report artifact's CVE and package-risk notes feed directly into which code paths to scrutinize
- **Use after:** any implementation to catch security and logic issues before merge
- Use devflow:code-reviewer for broader code quality review (standards, test adequacy, maintainability)
- Use devflow:systematic-debugging when a specific failure needs root cause investigation
- Use the devflow-audit security adapter (threat-modeler → dependency-auditor → find-bugs) for a full proactive security audit rather than this skill standalone
