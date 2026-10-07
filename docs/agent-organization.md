# Agent organization

The skills of this repository can be chained by hand ([workflows.md](../workflows.md)). This organization chains them without a human in the loop: a Jira ticket or a free-form request goes in, a merged merge request (MR) comes out, and a person is called only on escalation.

Each role is one file in [`agents/`](../agents), and loads one or more skills. The files carry no model name and no reasoning effort: they work with any model, and each role inherits the one your session runs on.

## Principles

Inherited from the skills:

- A skill announces itself before applying, never silently.
- Structural decisions go through a multiple-choice question. Here the Product Owner answers.
- Plans, reports and invariants live in files of the repository, not in the context window.
- No silent auto-fix: only the Developer corrects, in a visible commit.

Specific to the organization:

- Roles do not call each other and share no context. Everything passes through files, and the Orchestrator reads them.

## The roles

Eleven roles. Three of them judge: a wrong call there costs more than anywhere else.

| Role | Skills loaded | Judges | Steps in |
|---|---|---|---|
| Orchestrator | none: routes, keeps the brief, moves the Jira status, writes `.metrics/` | | every request |
| Product Owner | none: answers multiple-choice questions from the business documentation and Jira | yes | every multiple-choice question |
| Cartographer | `codebase-cartographer` | | onboarding, doc-gardening |
| Harness Engineer | `codebase-harness`, `ddd-advisor` | | onboarding, doc-gardening |
| Planner | `plan-driven-dev` (context and plan) | | feature |
| Developer | `plan-driven-dev`, `behavior-driven-testing` | | feature, bug after diagnosis |
| Diagnostician | `systematic-debugging` | yes | bug |
| Reviewer | `premerge-review` | yes | after every implementation |
| Failure Analyst | none: analyzes the failure, proposes an improvement of the harness in a separate MR | | after 5 iterations without a GO |
| Auditor | `ai-code-remediation` | | when the Orchestrator decides |
| Coach | `code-assimilation-quiz` | | when the human asks |

## The flows

```
Feature   Orchestrator → Planner → Developer ⇄ Reviewer → CI merges
Bug       Orchestrator → Diagnostician → Reviewer (checks the proof) → Developer ⇄ Reviewer → CI merges
Outside   Cartographer → Harness Engineer (onboarding, doc-gardening)
a ticket  Auditor (when the Orchestrator decides)
          Coach (when the human asks)
```

A feature goes through the Planner. A bug goes through the Diagnostician, and the Reviewer checks its proof before any fix is written. Then the Developer and the Reviewer loop until a GO, and the CI merges.

## Governance

A person steps in only on escalation, and the merge is done by the CI: quality rests on the Product Owner, the Reviewer and the harness.

- **Multiple-choice questions.** The Product Owner answers, relying on the business documentation the Cartographer wrote and on the Jira ticket. When the sources do not settle a question, it escalates to the human.
- **Escalation to the human.** The Product Owner doubts; the diff touches a sensitive zone (security, data, migration); or the Failure Analyst has run and the loop still has no GO.
- **Merge.** The CI merges when the Reviewer returns a GO and the checks are green. No systematic human approval before the merge.
- **Jira.** Every role comments its step; only the Orchestrator changes the ticket status.
- **Writing to the code.** The Reviewer and the Diagnostician do not modify code. That rule is an instruction in their prompt, with no technical restriction. It cannot be enforced by removing their write tool either: each of them has to write a file, the review report and the proof.

## The iteration loop and the Failure Analyst

The Developer and the Reviewer loop at most 5 times. Beyond that, the Failure Analyst studies the failure and the human is told.

1. The Developer implements according to the plan until the acceptance criteria are covered by tests of behavior.
2. The Reviewer clears the gauntlet, then returns a GO or a NO-GO.
3. A NO-GO goes back to the Developer; each return counts toward the 5 iterations.
4. At the 5th iteration without a GO, the Failure Analyst looks for why the harness was not respected, and proposes its improvement as a new plan, in a separate MR.
5. If the loop still has no GO after the Failure Analyst, the Orchestrator escalates to the human (to confirm, see the open points).

The Failure Analyst has no other trigger: no log of violations, no retrospective after each merge.

## Hand-off

Roles share no context. Everything passes through files of the repository: the ones the skills already write, plus a brief.

| File | Written by | Read by |
|---|---|---|
| Brief (`.plans/<slug>-brief.md`) | Orchestrator | every role |
| Answers (`.plans/<slug>-answers.md`) | Product Owner | Orchestrator, the role that asked |
| Plan (`.plans/<slug>.md`) | Planner | Developer, Reviewer |
| Hand-off note (`.plans/<slug>-<role>.md`) | Cartographer, Harness Engineer, Developer, Diagnostician | Orchestrator |
| Review report (`.reviews/`) | Reviewer | Orchestrator, Developer |
| Audit report (`.audit/`) | Auditor | Orchestrator, Product Owner |
| Metrics (`.metrics/`) | Orchestrator | the human |

- The brief holds the objective, the acceptance criteria, the type of request (Jira ticket or free-form) and the iteration counter, which the Orchestrator updates.
- A role never asks the Product Owner directly. A role that needs a decision writes its multiple-choice question in its report and sets `status: blocked`. The Orchestrator relays the question, appends the answer to the brief, and runs the role again.
- Every output opens on a YAML front-matter, followed by a report in prose. The Orchestrator reads only the front-matter to decide whether to resend or escalate.

```yaml
role: reviewer
status: done            # done | blocked | escalate
verdict: GO             # the Reviewer only: GO | NO-GO
reasons: []
severity: major         # blocking | major | minor, when there is something to report
```

## Models and cost

The roles name no model and no reasoning effort. Each one inherits what your session runs on, so the organization works with any model.

The three roles that judge are marked in the table above. Give them your most capable model, or your highest reasoning effort, in the settings of your client: it is where an error costs most. The other roles do not need it.

Cost is tracked and raised as an alert, with no cap and no blocking: only the 5 iterations bound a run. Where and how cost is measured is still to be defined (see the open points).

## Metrics

Four indicators say whether the organization works. The Orchestrator writes one file in `.metrics/` per run.

| Indicator | What it reveals |
|---|---|
| Rate of GO on the Reviewer's first pass | quality of the plan and the development |
| Average number of iterations, rate at which the Failure Analyst is triggered | efficiency of the loop and the harness |
| Rate of escalation to the human | real autonomy of the organization |
| Regressions or bugs that appear after merge | what the Reviewer and the CI let through |

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

- No technical restriction of rights: a Reviewer or a Diagnostician could modify the code despite its instruction, and the CI merges without a human. The tool list of a subagent could take write access away from a role that does not need it, but these two do.
- No systematic human approval before the merge: the Reviewer and the CI are the only safeguards.
- No cost cap: only the 5 iterations bound a run.
- Roles inherit the session's model: nothing in the repository guarantees that the roles that judge run on a strong one. That is left to whoever configures the client.

**Open points**

- The Failure Analyst triggers at the 5th iteration, and "Failure Analyst exhausted" is also an escalation trigger: specify exactly when the human is told.
- The Diagnostician must write the proof of the cause that the Reviewer checks. Until a location is defined, the proof sits in its hand-off note, `.plans/<slug>-diagnostician.md`.
- Who defines the "sensitive zones" (security, data, migration), and where: for example in the invariants of the harness. Until then the Orchestrator falls back on the three named above.
- At onboarding the business documentation does not exist yet, since the Cartographer is writing it: the Product Owner has nothing to rely on, and its answers will mostly escalate to the human.
- Measuring cost, and linking a regression to the original MR in `.metrics/`.
- Frequency of the scheduled doc-gardening task.
