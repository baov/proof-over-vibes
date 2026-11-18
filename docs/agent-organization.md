# Agent organization

The skills of this repository can be chained by hand ([workflows.md](../workflows.md)). This organization chains them without a human in the loop: a request goes in, a merged merge request (MR; a pull request on some platforms) comes out, and a person is called on escalation, and to merge where the project has no CI.

A request is either a prompt, which is the request itself, or a ticket in whatever tracker the project uses. The organization names no tracker: the Orchestrator reads a ticket with the access the client gives it, or asks the human to paste it.

Each role is one file in [`agents/`](../agents), and most of them load skills. The files carry no model name and no reasoning effort: they work with any model, and each role inherits the one your session runs on.

## Principles

Inherited from the skills:

- A skill announces itself before applying, never silently.
- Structural decisions go through a multiple-choice question. Here the Product Owner answers.
- Plans, reports and invariants live in files of the repository, not in the context window.
- No silent auto-fix: only the Developer corrects, in a visible commit.

Specific to the organization:

- Roles do not call each other and share no context. Everything passes through files, and the Orchestrator reads them.

## The roles

Five of the roles judge: a wrong call there costs more than anywhere else.

| Role | Skills loaded | Judges | Steps in |
|---|---|---|---|
| Orchestrator | none: routes, keeps the brief, moves the ticket status, writes `.metrics/` | | every request |
| Product Owner | none: cuts a feature into stories and prioritizes them; answers multiple-choice questions from the PRD, the business documentation and the ticket | yes | every feature of several stories, every redesign, every multiple-choice question |
| Cartographer | `codebase-cartographer` | | onboarding, doc-gardening |
| Harness Engineer | `codebase-harness` | | onboarding, doc-gardening |
| Product Manager | `product-strategy` | yes | at the human's request, outside a run |
| UX Designer | `ux-redesign` | | UX redesign, new journey |
| Architect | `ddd-advisor` | yes | once per feature, empty project |
| Planner | `plan-driven-dev` (context and plan) | | feature |
| Developer | `plan-driven-dev`, `behavior-driven-testing` | | feature, bug after diagnosis |
| QA | `acceptance-proof` | | once per request before the code (example map), then after every implementation, before the reviewer |
| Diagnostician | `systematic-debugging` | yes | bug |
| Reviewer | `premerge-review` | yes | after qa |
| Failure Analyst | none: analyzes the failure, proposes an improvement of the harness in a separate MR | | at the iteration limit without a GO (5 by default) |
| Auditor | `ai-code-remediation` | | when the Orchestrator decides |
| Coach | `code-assimilation-quiz` | | when the human asks |

## The flows

![How a request flows between the roles: an idea goes from the Product Manager to the human, the Architect and the Harness Engineer; a feature goes from the Orchestrator to the Product Owner, then once through the Architect, then once through QA, which maps the criteria into examples, then each story through the Planner, the Developer, QA and the Reviewer, a NO-GO from QA or the Reviewer sending it back to the Developer, and the merge gate; a UX redesign goes through the UX Designer, one compliance review by the Product Owner and the human who picks the direction, then into the flow of a feature; a bug goes through the Diagnostician and the Reviewer into the same loop; after five NO-GO the Failure Analyst runs, then the human is called.](agent-organization.svg)

The same flows in text:

```
Feature   Orchestrator → Product Owner (stories) → Architect (once) → QA (example map, once) → for each story: Planner → Developer ⇄ QA ⇄ Reviewer → merge gate
Redesign  Orchestrator → UX Designer → Product Owner (one compliance review) → human picks the direction → then as a feature, with the design document as its PRD and the Product Owner always cutting it
Bug       Orchestrator → Diagnostician → Reviewer (checks the proof) → Developer ⇄ QA ⇄ Reviewer → merge gate
Idea      Product Manager → human validates → Architect → Harness Engineer (before any feature)
Empty     Orchestrator → Architect → Harness Engineer (before any feature)
Outside   Cartographer → Harness Engineer (onboarding, doc-gardening)
a ticket  Auditor (when the Orchestrator decides)
          Coach (when the human asks)
```

A feature goes through the Product Owner, which cuts it into ordered stories, then once through the Architect, which exits at once when there is nothing to decide. QA then writes the example map of the whole feature: each acceptance criterion as a business rule, with examples someone can observe and the questions they raise, which go to the Product Owner before any code; the Planner adds its own examples to the map. Each story then goes through the Planner, the Developer, QA and the Reviewer, one after the other, with its own brief and its own merge request. QA proves the acceptance criteria in the running app before the Reviewer reads the diff; a NO-GO from either sends the story back to the Developer. The Orchestrator stops at the first escalation. If the Planner finds that a story needs a structural decision, the Architect runs again for that story. A request that is a single story skips the Product Owner, not the example map; a redesign never skips the Product Owner. A bug has no map: its reproduction stands for the criterion. On an empty project the Architect and the Harness Engineer lay the foundations first. A UX redesign or a new journey goes through the UX Designer, which inspects the live product and writes a design document with three art directions; the Product Owner checks it once against the business rules, never the taste; the human picks the direction, since it is a matter of taste, not of evidence; then it follows the flow of a feature, the design document standing in for the PRD. A bug goes through the Diagnostician, and the Reviewer checks its proof before any fix is written. Then the Developer, QA and the Reviewer loop until a GO, and the merge gate takes over.

## Governance

A person steps in on escalation, and to merge where the project has no CI. Otherwise the merge happens at the merge gate: quality rests on the Product Owner, the Reviewer and the harness.

- **Multiple-choice questions.** The Product Owner answers, relying on the business documentation the Cartographer wrote and on the ticket, when there is one. When the sources do not settle a question, it escalates to the human.
- **Art direction.** The UX Designer recommends one of three directions; the human picks, never the Product Owner: it is a matter of taste, not of evidence. It is a planned step, not an escalation, recorded as a `direction:` line in the briefs. A direction other than the recommended one sends the UX Designer back once to rewrite the document for it. The Product Owner reviews the design document once, for business rules only, then always cuts it into stories: only the essential priorities, the rest left to the human.
- **Escalation to the human.** The Product Owner doubts; the Architect meets a choice that is costly to reverse (superseding an ADR, changing the stack, adding a dependency or service, breaking a public contract, choosing the architectural style of an empty project); the diff touches a sensitive zone, declared by the Harness Engineer in the `Sensitive zones` section of `docs/technical/invariants.md` (security, data and migration when the section is absent, which the metrics record as `undeclared`); or the Failure Analyst has run and the loop still has no GO. Any other role that returns `escalate` stops the run too.
- **Delegation.** When the human tells the Orchestrator to decide for them, the brief says `delegation: yes`: an escalation of the Product Owner then continues on its recommended option, logged `answered-by-delegate`. Delegation never covers a choice costly to reverse, a sensitive zone or a loop that still fails. An answer to a question the Product Owner escalated, from a person or a delegate, reaches the decision log through the Product Owner; a technical answer goes back to the role that asked.
- **Questions for the human come in rounds.** When several roles are blocked on a question for the human at the same moment, the Orchestrator asks them in one round, and goes on with the roles the answer does not block. It never holds back a question a blocked role waits for.
- **Merge gate.** The last step before the merge, and always outside the agents. With a CI, the CI merges when QA returns a GO or `not-applicable` (or the human waived QA in the brief), the Reviewer returns a GO and the checks are green, with no systematic human approval. With none, the default is that a person merges: the run ends on "GO, ready to merge", and for a feature the next story starts once the person says the previous one is merged. A project can instead run a local script that rereads the verdict, replays the gauntlet and merges, started by a person. Whichever applies, the Orchestrator never merges.
- **Product strategy.** The Product Manager runs outside a run, only at the human's request, and starts none. It writes `docs/product/` (framing of a brief, research, vision, roadmap, story map, backlog of epics and features, and the PRD of a feature the human picked). A vision, a positioning and a prioritization are bets: its questions go to the human, never to the Product Owner. The human picks a backlog item and creates the request, citing its PRD. It writes no user stories: the Product Owner cuts the picked feature into stories from its PRD and the story map, which it never modifies. On an existing product the map shows the features already built as `done`, with `docs/business/` as the source.
- **Technical debt.** The Architect proposes a migration or a refactor as an ADR with the status `proposed`, and never blocks the feature in hand for it. If the human accepts, they create the request themselves; the Orchestrator does not watch the ADRs.
- **Tracker.** Every role comments its step on the ticket; only the Orchestrator changes its status. A prompt has no ticket.
- **Writing to the code.** The Reviewer, the Diagnostician and QA do not modify code. That rule is an instruction in their prompt, with no technical restriction. It cannot be enforced by removing their write tool either: each of them has to write a file, the review report, the proof or the acceptance-proof report.

## The iteration loop and the Failure Analyst

The Developer, QA and the Reviewer loop at most 5 times in all, a limit the brief holds and the human may change. Beyond that, the Failure Analyst studies the failure and the human is told.

1. The Developer implements according to the plan until the acceptance criteria are covered by tests of behavior.
2. QA proves each acceptance criterion in the running app and returns a GO, a NO-GO or `not-applicable`.
3. On a GO or `not-applicable`, the Reviewer clears the gauntlet, then returns a GO or a NO-GO.
4. A NO-GO from QA or the Reviewer goes back to the Developer; each return counts toward the one limit of the brief, whichever role raised it.
5. At the iteration limit without a GO, the Failure Analyst looks for why the harness was not respected, and proposes its improvement as a new plan, in a separate MR.
6. If the loop still has no GO after the Failure Analyst, the Orchestrator escalates to the human (to confirm, see the open points).

The Failure Analyst has no other trigger: no log of violations, no retrospective after each merge.

## Hand-off

Roles share no context. Everything passes through files of the repository: the ones the skills already write, plus a brief.

| File | Written by | Read by |
|---|---|---|
| Brief (`brief.md`) | Orchestrator | every role it runs |
| Answers (`answers.md`) | Product Owner | Orchestrator, the role that asked |
| Stories (`stories.md`) | Product Owner | Orchestrator, Architect, QA, Planner |
| Example map (`example-map.md`) | QA, then the Planner | Orchestrator, Planner, Developer, QA |
| Decision log (`docs/business/decisions.md`) | Product Owner | Product Owner, Planner, the human. Statuses: `answered`, `answered-by-delegate` (nobody read it), `human-needed` |
| Product files (`docs/product/`) | Product Manager | human, Product Owner, Cartographer |
| Design document (`ux-designer.md`) | UX Designer | Product Owner, the human, Planner |
| Design review (`design-review.md`) | Product Owner | Orchestrator, UX Designer |
| Architect's note (`architect.md`) | Architect | Planner, Orchestrator |
| ADR (`docs/technical/adr/`) | Architect, Cartographer | Harness Engineer, Planner |
| Plan (`plan.md`) | Planner | Developer, QA, Reviewer |
| Proof of the cause (`diagnostician.md`) | Diagnostician | Reviewer, Developer |
| Acceptance-proof report (`qa-<n>.md`, evidence in `qa-<n>/`) | QA | Orchestrator, Developer, Reviewer |
| Hand-off note (`<role>.md`, `developer-<n>.md` for the Developer) | Cartographer, Harness Engineer, Product Manager, Developer | Orchestrator |
| Improvement plan (`<slug>-harness-improvement/plan.md`) | Failure Analyst | the human, Orchestrator |
| Review report (`.reviews/<branch>-<date>-<n>.md`) | Reviewer | Orchestrator, Developer |
| Audit report (`.audit/`) | Auditor | Orchestrator, Product Owner |
| Metrics (`.metrics/`) | Orchestrator | the human |

- The `.plans/` files above live in a **work folder**, `.plans/in-progress/<slug>/`, one per request. A feature has one folder for its shared files (`stories.md`, `architect.md`) and one subfolder per story, with the story's brief, plan and notes. The Orchestrator gives each role the path, and moves the folder to `.plans/done/` or `.plans/aborted/` when the run ends (a feature, story by story: each story's subfolder goes to `done/<feature>/<story>/` with its own merge request, the shared files with the last one), as `plan-driven-dev` does for a plan on its own. The Failure Analyst's improvement plan is a request of its own, so it gets its own folder.
- The brief holds the objective, the acceptance criteria, the type of request (ticket or prompt) and the iteration counter, which the Orchestrator updates.
- `<n>` is the iteration counter of the brief. The Developer's note, QA's report and the Reviewer's report carry it, so no round overwrites the previous one.
- **Versioning.** Working state stays out of the repository: `.plans/in-progress/` and `.reviews/` are git-ignored, and the Orchestrator adds them to `.gitignore` if needed. The record is versioned: `.plans/done/` (the Orchestrator commits it on the change's branch), `.plans/FEEDBACK.md`, `.audit/` and `.metrics/`. `.plans/aborted/` stays local until the human decides to commit it. Since the Orchestrator archives the folder before the merge gate, the plan and the decisions of a change ship in its own merge request.
- A role never asks the Product Owner directly. A role that needs a decision writes its multiple-choice question in its report and sets `status: blocked`. Any open point the consumer of the feature would see counts as a decision, not only business rules: order, tie-break, shape of a response, a parameter, what a second call does. The Product Owner will not write an acceptance criterion it cannot source, the Planner lists what its own plan adds (repeat, absent, invalid, edge, order), the Developer lists the public behaviors it added, the Reviewer rates an undecided one `major`, and the Orchestrator reads the plans' technical choices and sends back anything a consumer would see. The Orchestrator relays the question, appends the answer to the brief, and runs the role again.
- Every output opens on a YAML front-matter, followed by a report in prose. The Orchestrator reads only the front-matter to decide whether to resend or escalate.

```yaml
role: reviewer
status: done            # done | blocked | escalate
verdict: GO             # the Reviewer only: GO | NO-GO
proof: GO               # QA only: GO | NO-GO | not-applicable
reasons: []
severity: major         # blocking | major | minor, when there is something to report
open_majors: []         # the Reviewer only, at a GO: the major findings still open, carried to the next request
```

## Models and cost

The roles name no model and no reasoning effort. Each one inherits what your session runs on, so the organization works with any model.

The five roles that judge are marked in the table above. Give them your most capable model, or your highest reasoning effort, in the settings of your client: it is where an error costs most. The other roles do not need it.

Cost is tracked and raised as an alert, with no cap and no blocking: only the iteration limit bounds a run. Where and how cost is measured is still to be defined (see the open points).

## Metrics

Five indicators say whether the organization works. The Orchestrator writes one file in `.metrics/` per run.

| Indicator | What it reveals |
|---|---|
| Rate of GO on the Reviewer's first pass | quality of the plan and the development |
| Average number of iterations, rate at which the Failure Analyst is triggered | efficiency of the loop and the harness |
| Rate of escalation to the human | real autonomy of the organization |
| Questions answered before the code, criteria blocked after it | whether the example map finds the open points early enough to be worth its cost |
| Regressions or bugs that appear after merge | what the Reviewer and the merge gate let through |

Regressions show up after the run ends: the metrics file has to be completable afterwards, by linking the bug to the MR it came from.

## Installing and running

```bash
./install.sh --scope project --into ~/projects/my-app --with-agents
```

`--with-agents` is off by default: a role runs on its own, so it is never installed unasked. The skills are installed alongside, since the roles load them. `install.sh --help` lists the clients; the roles are written in the format of Claude Code, Codex and Gemini CLI.

Start the Orchestrator as the main agent of the session, so that it can hand work to the other roles. In Claude Code:

```bash
claude --agent orchestrator
```

Other clients have their own way of starting a session with a given agent, and their own limits on agents starting agents: check them before relying on the chain.

## Risks and open points

Three choices are assumed, and reduce the safeguards. Revisit them after the first runs.

**Assumed risks**

- No technical restriction of rights: a Reviewer or a Diagnostician could modify the code despite its instruction, and an automated merge gate merges without a human. The tool list of a subagent could take write access away from a role that does not need it, but these two do.
- No systematic human approval before the merge, where a CI merges: the Reviewer and the CI are the only safeguards. With no CI, the person who merges is the second one.
- No cost cap: only the iteration limit bounds a run.
- Roles inherit the session's model: nothing in the repository guarantees that the roles that judge run on a strong one. That is left to whoever configures the client.

**Open points**

- The Architect's and the Harness Engineer's questions (architectural style, harness blocks, sensitive zones) are technical: the Product Owner may not answer them, and nothing says where they go. Decide whether the Orchestrator routes them to the human by rule.
- A sensitive-zone escalation stays open until a person reviews the change; nothing records that the review happened.
- The Failure Analyst triggers at the iteration limit, and "Failure Analyst exhausted" is also an escalation trigger: specify exactly when the human is told.
- At onboarding the business documentation does not exist yet, since the Cartographer is writing it: the Product Owner has nothing to rely on, and its answers will mostly escalate to the human.
- Linking the verdict to the merge gate. With a CI: a check that reads `proof` in the latest QA report, `verdict` in the latest review report, and `status` for an escalation. With a local gate: a script. Both depend on the platform, so neither is provided.
- Measuring cost, and linking a regression to the original MR in `.metrics/`.
- Frequency of the scheduled doc-gardening task.
- A client QA cannot drive (no way to run the app, no way to observe its output): the Orchestrator escalates once and the human's decision — run the story without QA, or stop — is recorded in the brief, but nothing yet keeps that decision from being asked again on the next request of the same project.
- Cost of replaying the whole acceptance-proof plan on every iteration, not only the criteria a fix touched.
- The example map has not been checked on a real run: its value is a bet, measured by the two metrics above. Drop it if the questions keep coming after the code anyway.
- Weight of the evidence: the work folder is committed at archiving, so the screenshots of every QA round ship in the merge request. Nothing yet trims them to the last round.
- Found by paper simulations, not seen in a real run:
  - Delegation with no CI dead-ends: each story waits for a person to merge, and the human said they would not be reachable.
  - After the wait for a merge, nothing says how a run resumes at the next story rather than opening a new request.
  - Metrics are written per run, and a feature is one run: per-story rates and feature-level events (the cut, the Architect) have no home yet. No real run has written metrics so far.
  - A feature abandoned after some stories merged moves whole to `aborted/`, though part of it is already in `done/`.
  - The number of iterations after the Failure Analyst before the escalation is not set.
  - A delegated decision covers any Product Owner escalation, whether or not the choice is cheap to reverse.
