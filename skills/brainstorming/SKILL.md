---
name: brainstorming
description: Use before designing any software feature, component, or system behavior — explores requirements, constraints, and competing approaches through dialogue before moving to implementation planning
framework: devflow
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to proceed to implementation?"
- Use devflow:using-git-worktrees to create an isolated workspace and feature branch
- Then use devflow:writing-plans inside that workspace to create the implementation plan

## When NOT to Use

- Requirements are already clearly defined — skip directly to devflow:writing-plans
- Feasibility of the approach is unknown — use devflow:spike-executor first to validate before designing
- You need a detailed spec from a stakeholder — use devflow:interview first, then brainstorm

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense

---

## Related Skills and Agents

- **Preceded by:** devflow:interview (when requirements need extracting) or invoked directly
- **Followed by:** devflow:writing-plans
- Use devflow:interview first when the idea is vague and needs structured requirement extraction
- Use devflow:spike-executor when feasibility of an approach is unknown before committing to a design
- Use devflow:scope-estimator to size the work before committing to a plan
