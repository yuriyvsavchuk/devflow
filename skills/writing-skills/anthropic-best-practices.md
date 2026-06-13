# Skill authoring best practices — external reference

> **Why this is a pointer, not a copy.** Earlier revisions of this file vendored
> Anthropic's official "Skill authoring best practices" documentation verbatim.
> That text is © Anthropic and is **not** part of the MIT-licensed Devflow
> software, so it has been replaced with a link to the canonical source to keep
> the repository's licensing clean.

**Read Anthropic's official guidance:** Claude Docs → Agent Skills (the
*overview* and *best practices* pages):
<https://docs.claude.com/en/docs/agents-and-tools/agent-skills/>

It covers the points this skill builds on:

- **Concise is key** — the context window is shared; only add what Claude doesn't already know.
- **Progressive disclosure** — keep `SKILL.md` lean; push detail into separate files Claude reads only when needed.
- **Name and description drive discovery** — Claude uses the frontmatter to decide when to trigger a skill, so write them as precise triggers.
- **Iterate from observed behavior** — refine skills from how agents actually use them, not from assumptions.

Use that guidance alongside the TDD-for-skills approach in this skill
([SKILL.md](SKILL.md)): write a pressure test that makes an agent fail without
the rule, then write the minimal skill text that makes it comply, then close the
loopholes.
