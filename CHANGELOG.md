# Changelog

Notable changes to this repository. Format based on [Keep a Changelog](https://keepachangelog.com/1.1.0/), versioning follows [semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] — 2026-10-07

One `SKILL.md` changed, and only the last sentence of its `description`: nine of
the ten are still identical to 0.1.0, and the triggers of the tenth are untouched.
What is new is the layer of roles above them; the rest corrects the repository's
own documentation, one overstated claim and one description.

### Added

- Agent roles: eleven files in `agents/` — Orchestrator, Product Owner, Cartographer, Harness Engineer, Planner, Developer, Diagnostician, Reviewer, Failure Analyst, Auditor, Coach — most of them loading the skills that fit their job, all of them handing their result to the next through a file. They carry no model, no reasoning effort and no tracker: each inherits the session's model, and a request is a prompt or a ticket from any tracker.
- A merge gate ends every run, outside the agents: the CI where there is one, a person otherwise (the default), or a local script a person starts. The Orchestrator never merges.
- `docs/agent-organization.svg` — the diagram of the flows, standalone, with a dark mode.
- `docs/agent-organization.md` — the flows, the governance, the 5-iteration loop, the hand-off contract, the metrics, and the open risks.
- `install.sh --with-agents` installs the roles for Claude Code and Gemini CLI (linked or copied) and for Codex (generated as TOML). `--client` now also accepts `codex` and `gemini`. The Codex and Gemini CLI adapters are written from their documentation and not yet run end to end.
- `tools/validate-skills.py` checks the roles: name matching the file, one-line `description`, no model name, no tracker name.
- `docs/glossary.md` gains `role`, `brief`, `hand-off`, `escalation` and `iteration`, and the hand-off front-matter contract.

### Changed

- `AGENTS.md` forbids a model name anywhere in `agents/`, and limits naming a client to where it cannot be avoided.
- `docs/glossary.md` is now indexed on the English term rather than on the French
  one it replaced. The French column was migration scaffolding — it forced ten
  parallel translators onto one word per term — and it pointed at the wrong risk
  once the translation was done: the plausible slip is no longer a leftover
  French word, it is writing "module B" for "block B". Each term now lists the
  synonyms it displaces, and the "Renamed paths" table moved out, migration
  information belonging to the commit that performed the renames.
- `tools/check-glossary.sh` no longer exempts `docs/glossary.md`, which is now
  entirely English and checked like every other file.

### Fixed

- The `description` of `ddd-advisor` said that `codebase-cartographer` and
  `codebase-harness` may invoke it. Neither does: only `ai-code-remediation`
  invokes it, `ddd-advisor` reads the cartographer's glossary, and it hands
  confirmed boundaries to `codebase-harness`, not the reverse. The description now
  says so, as the body of the skill, the README and `workflows.md` already did.
- 0.1.0 described the glossary as "mechanically enforced" and the check as
  catching "off-glossary vocabulary". Both overstated it. The script catches
  leftover French — the mechanically checkable half. It does not catch rejected
  synonyms, and deliberately so: "module", "rule" and "framework" are ordinary
  English words elsewhere, so matching on them would raise false alarms far more
  often than real ones. One word per concept binds the writer and is caught in
  review. `AGENTS.md` and `README.md` now say so.

## [0.1.0] — 2026-09-21

First public version. Ten skills conformant to the [Agent Skills specification](https://agentskills.io/specification), the tooling that keeps them consistent, and the documentation that chains them.

### Skills

Entry points, triggered by a user request:

- `codebase-cartographer` — maps a project into business and technical documentation
- `codebase-harness` — the enforcement layer: executable invariants, test-case bridge, mutation testing, doc-gardening
- `plan-driven-dev` — implementation workflow: validated plan, behavior-driven TDD, invariants inside the loop
- `premerge-review` — pre-merge review: mechanical gauntlet, four angles, GO/NO-GO verdict
- `systematic-debugging` — diagnosis down to a proven root cause, no fix
- `ai-code-remediation` — cold audit of an AI-generated codebase, eight symptoms, Mikado plan
- `code-assimilation-quiz` — assimilation quiz on the diff, never automatic

Supporting skills, loaded by another skill:

- `behavior-driven-testing` — test doctrine: behaviors rather than classes
- `ddd-advisor` — Domain-Driven Design audit and guidance
- `clarify-with-choices` — multiple-choice validation doctrine, and its degraded mode per host agent

### Tooling

- `tools/validate-skills.py` — checks the specification rules and the 500-line cap on a `SKILL.md`; `--explain` describes each rule without checking anything
- `tools/check-glossary.sh` — catches leftover French and off-glossary vocabulary
- Both run in pre-commit and in CI, with no dependency to install
- `install.sh` — symlink or copy install, user or project scope, every conformant client
- `setup-repo.sh` — publishes your own copy to a private GitHub repository

### Documentation

- `README.md` — the ten skills, their installation, the conventions they share
- `workflows.md` — which skill to use when, how artifacts circulate, the common chaining mistakes
- `docs/glossary.md` — the binding vocabulary, mechanically enforced
- `AGENTS.md` — the contribution conventions

[0.2.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.2.0
[0.1.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.1.0
