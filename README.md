# POV — Proof Over Vibes

> Agent skills for software development: documented, enforced, reviewed — not guessed.

Software development skills for AI agents — a disciplined workflow, mechanical enforcement, defect-oriented review.

Ten skills that chain together: documentation feeds the invariants, the invariants constrain the implementation, the implementation clears the gauntlet before the review. An optional layer of roles chains them for you, calling on a person only where a decision is needed.

Conformant to the [Agent Skills specification](https://agentskills.io/specification), so they load natively — with their description-based triggering — in Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, Amp, OpenCode and every other conformant client.

## Contents

**Entry points** — triggered by a user request.

| Skill | Role | Produces |
|---|---|---|
| [`codebase-cartographer`](skills/codebase-cartographer) | Maps a project into business + technical documentation (glossary, features, test-cases, ADRs) | `docs/`, a section in `AGENTS.md` |
| [`codebase-harness`](skills/codebase-harness) | The enforcement layer: executable invariants, test-case bridge, mutation testing, doc-gardening | `tools/harness/`, `docs/technical/invariants.md` |
| [`plan-driven-dev`](skills/plan-driven-dev) | Implementation workflow: validated plan, behavior-driven TDD, invariants inside the loop | `.plans/` |
| [`premerge-review`](skills/premerge-review) | Pre-merge review: mechanical gauntlet, then four angles, GO/NO-GO verdict | `.reviews/` |
| [`systematic-debugging`](skills/systematic-debugging) | Diagnosis down to a proven root cause — no fix | — |
| [`ai-code-remediation`](skills/ai-code-remediation) | Cold audit of an AI-generated codebase, eight symptoms, Mikado plan | `.audit/` |
| [`code-assimilation-quiz`](skills/code-assimilation-quiz) | An assimilation quiz on the diff — learning, not review. **Never automatic** | — |

**Supporting skills** — loaded by another skill, rarely requested directly.

| Skill | Role | Loaded by |
|---|---|---|
| [`behavior-driven-testing`](skills/behavior-driven-testing) | Test doctrine: behaviors rather than classes | `plan-driven-dev`, `ai-code-remediation` |
| [`ddd-advisor`](skills/ddd-advisor) | Domain-Driven Design audit and guidance | `ai-code-remediation` |
| [`clarify-with-choices`](skills/clarify-with-choices) | Multiple-choice validation doctrine, and its degraded mode per host agent | `codebase-cartographer`, `codebase-harness`, `ddd-advisor` |

## How to chain them

The nominal case — a feature on an already-tooled project:

```
codebase-cartographer → codebase-harness      (once, to tool the project)
plan-driven-dev → premerge-review             (on every feature or bug)
```

The other cases (a production bug, a vibe-coded codebase, hollow tests…), how artifacts circulate between skills, and the common chaining mistakes are in **[workflows.md](workflows.md)**.

## Roles: an optional layer

The skills work on their own, chained by you or by your agent as above. If you want the chain to run without a human in the loop, an optional layer of eleven roles sits on top: one file each in [`agents/`](agents) — Orchestrator, Product Owner, Planner, Developer, Reviewer and the others — each loading the skills that fit its job. A request goes in, a ticket or a prompt, a merge request comes out, and a person is called on escalation, and to merge where the project has no CI.

The roles name no model and no reasoning effort: they inherit your session's, so the organization works with any model. Flows, governance, the iteration loop, the open risks: **[docs/agent-organization.md](docs/agent-organization.md)**.

## Installation

```bash
./install.sh                    # for you, on this machine
./install.sh --scope project --into ~/projects/my-app
```

The script lays down symlinks — repository updates are picked up without reinstalling. `--copy` produces independent copies, `--help` details the options.

To install the agent roles as well, add `--with-agents`. They are written for Claude Code (`.claude/agents/`), Codex (`.codex/agents/`, generated as TOML) and Gemini CLI (`.gemini/agents/`):

```bash
./install.sh --scope project --into ~/projects/my-app --with-agents
```

Off by default, because a role acts on its own. The Codex and Gemini CLI adapters are written from their documentation and have not been run end to end: report what you find.

By hand, if you prefer: skills are folders, so just put them where the client looks for them.

| Client | User scope | Project scope |
|---|---|---|
| Codex, Cursor, Gemini CLI, Copilot, Amp, OpenCode… | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |

`.agents/skills/` is the interoperable directory: most conformant clients look there, often ahead of their own.

**Claude (web / desktop)** — zip each skill individually and upload it under Customize > Skills:

```bash
cd skills && for d in */; do zip -r "../${d%/}.zip" "$d"; done
```

**Publishing your own copy** — `setup-repo.sh` creates a private GitHub repository and pushes the contents to it, using your existing `gh` authentication:

```bash
./setup-repo.sh [repo-name]
```

## Conventions

Every skill follows the same rules:

- **Announcement** — the skill announces itself before applying, never silently
- **Validation by multiple-choice question** — structural decisions go through the user, nothing is applied unasked
- **File-backed persistence** — plans, reports and invariants live in the repository, not in the context window
- **Explicit degraded mode** — a skill works without its reference material, but says so
- **No silent auto-fix** — the harness reports; a human or an agent fixes it in a visible commit
- **English repository, project-language output** — the skills are written in English, but what they write into your project follows your project's language

## Contributing

The writing conventions — format, language, what is forbidden — are in [AGENTS.md](AGENTS.md), and the binding vocabulary is in [docs/glossary.md](docs/glossary.md).

They are checked mechanically, because a check that never runs is not a check:

```bash
python3 tools/validate-skills.py --root .
tools/check-glossary.sh
```

No dependency to install. The validator covers the specification's rules (name, the 1024-character cap on `description`, name/folder match) and flags any `SKILL.md` over 500 lines. It also checks the agent roles: a name matching the file, a one-line `description`, and no model name anywhere. The glossary check catches leftover French; the one-word-per-concept rule binds the writer and is caught in review, since its rejected synonyms are ordinary English elsewhere. Both run in pre-commit (`pre-commit install`) and in CI. `--explain` describes each rule without checking anything.
