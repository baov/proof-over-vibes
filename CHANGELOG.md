# Changelog

Notable changes to this repository. Format based on [Keep a Changelog](https://keepachangelog.com/1.1.0/), versioning follows [semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A decision answered by the human's delegate is `answered-by-delegate` in the decision log, not `answered`, and the Orchestrator counts them in the metrics (`delegated-decisions:`), so that a decision nobody read is visible.

### Changed

- Business decisions can no longer slip through silently. The Product Owner writes only acceptance criteria it can source, and lists the others as open points; the Planner also asks about the behaviors its own plan creates (a repeated call, an absent or invalid value, an edge, an order); the Developer lists the public behaviors it added and blocks on a consumer-visible one; the Reviewer rates an undecided consumer-visible behavior `major`, which carries to the next planner; and the Orchestrator reads the plans' technical choices and the stories' open points and sends back what a consumer would see.
- The files the roles write for a request now live in a work folder, `.plans/in-progress/<slug>/` (`brief.md`, `stories.md`, `architect.md`, `plan.md`, `<role>.md`), instead of flat `.plans/<slug>-*.md` files. A feature gets one folder with one subfolder per story. The Orchestrator archives the folder to `.plans/done/` or `.plans/aborted/` at the end of the run; a feature is archived story by story, so each merge request ships its own plan. `plan-driven-dev` follows the same layout: its plan is `.plans/in-progress/<slug>/plan.md`, archived as a folder. The Failure Analyst's improvement plan gets its own folder. The Product Manager is now listed among the hand-off note writers.
- The Developer's note is `developer-<n>.md` and the Reviewer's report `.reviews/<branch>-<date>-<n>.md`, `<n>` being the iteration counter of the brief: a round no longer overwrites the previous one. The Diagnostician's proof and the Failure Analyst's improvement plan have their own lines in the hand-off table, which closes the open point on where the proof sits.
- `.plans/in-progress/` and `.reviews/` are git-ignored (the Orchestrator and `plan-driven-dev` add the lines); `.plans/done/` (committed by the Orchestrator on the change's branch), `.plans/FEEDBACK.md`, `.audit/` and `.metrics/` are versioned; `.plans/aborted/` stays local. The Reviewer's check of a proof is written to `.reviews/<branch>-<date>-proof.md`, and a bug, which has no plan, has the proof stand in for it in the Developer's and the Reviewer's input.
- The Product Owner keeps a decision log, `docs/business/decisions.md`: it reads it before answering and appends every answer, `answered` or `human-needed`, so the same question is never asked twice and a pending decision is visible. The Orchestrator may continue on the recommended option of a pending decision when no person is reachable and the choice is cheap to reverse, and counts it in the metrics.
- A `GO` no longer buries a known defect: the Reviewer lists its open major findings in `open_majors`, the Orchestrator carries them into the brief of the project's next request, and the Planner plans or defers each one by a question.
- The iteration limit lives in the brief (5 by default), a single source that the Failure Analyst and the documentation read; the human may change it for a run.
- The Planner no longer settles an open point that the consumer of the feature would see (a business rule, an order, a tie-break, the shape of a response): it writes a multiple-choice question and stops, at most three per round. Only choices no consumer can observe stay in the plan.
- Sensitive zones have a home: a `Sensitive zones` section of `docs/technical/invariants.md`, written by the Harness Engineer, with `None` valid only after an explicit answer. The Orchestrator and the Reviewer escalate on those zones; when the section is absent they fall back on security, data and migration and the metrics record `sensitive-zones: undeclared`.

## [0.3.0] — 2026-10-18

Two roles and one skill for the work upstream of the plan: what to build, and
how it is structured. The Product Owner and the flow of a feature change with
them. The roles are written from the design and have not yet run end to end.

### Added

- `product-strategy` — a skill for the epic and the feature, never the user story: market watch (competitors, blue or red ocean), vision and roadmap, story map, a prioritized backlog, and the PRD of one chosen feature, written on demand. Everything goes under `docs/product/`; its conclusions are hypotheses the user validates, and without web access it says so and marks what it could not check.
- `agents/product-manager.md` — the Product Manager. It runs outside a run, only at the human's request, and starts none: the human picks a backlog item and creates the request, citing its PRD. On an existing product it maps the features already built as `done`, citing the business documentation. It judges, and its questions go to the human, never to the Product Owner.
- `agents/architect.md` — the Architect. It decides the structure before the Planner plans, once per feature, and exits at once when there is nothing to decide. A choice costly to reverse goes to the human; a lasting decision becomes an ADR; debt it meets becomes an ADR with the status `proposed`, without blocking the feature. On an empty project it runs first, with the Harness Engineer, and proposes the architectural style as ADR-0001. It judges.
- `structure: unchanged | decided | escalated` in the hand-off front-matter, written by the Architect only, in `docs/glossary.md`.

### Changed

- The Product Owner cuts a picked feature into ordered user stories from its PRD, the story map and the business documentation, and writes them to `.plans/<slug>-stories.md`. It keeps answering multiple-choice questions, and still never touches the roadmap or the story map.
- A feature now flows `Orchestrator → Product Owner → Architect → for each story: Planner → Developer ⇄ Reviewer → merge gate`. The Orchestrator runs the stories one by one, each with its own brief, iteration counter and merge request, and stops at the first escalation. A request that is a single story skips the Product Owner. The Planner stops with `status: blocked` when a story needs a structural decision, and the Architect runs again for that story.
- The Harness Engineer turns each ADR of the Architect into an invariant, starting in `warn`.
- `docs/agent-organization.md` and `README.md` now count thirteen roles, five of them judging. `docs/agent-organization.svg` is redrawn: idea, feature, bug and escalation paths. `workflows.md` lists `product-strategy` among the entry points.

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

[0.3.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.3.0
[0.2.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.2.0
[0.1.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.1.0
