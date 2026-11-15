---
name: acceptance-proof
description: Proves that a developed feature behaves as expected, in the running app, with evidence kept as files. Takes the acceptance criteria, runs each one against the real app, keeps a screenshot (or captured output) per observation, gives each criterion a proof mark (PROVEN, DISPROVEN, UNPROVEN) and ends in a GO/NO-GO verdict. Use whenever someone wants to validate a feature end to end or show it works - "prove the feature works", "validate the acceptance criteria", "test it in the app and take screenshots", "give me evidence before the merge", "is the feature really done", "demo what changed" - typically after plan-driven-dev and before premerge-review. Covers any surface the agent can drive (web, mobile, desktop, CLI, API). Not to be confused with premerge-review (reads the diff, does not run the app), behavior-driven-testing (writes automated tests), or systematic-debugging (explains a failure, does not prove a feature).
---

# Acceptance Proof

Run a feature in the real app and prove, criterion by criterion, that it behaves as expected. Output: a report, the evidence next to it, and a GO / NO-GO verdict that another person can check without redoing the work.

The skill proves; it does not fix and it does not diagnose. A criterion that fails is reported with the evidence of what happened, then handed off.

## Initial announcement

Before applying this skill, announce it to the user:

> I suggest applying the `acceptance-proof` skill: each acceptance criterion run in the real app, evidence kept per observation, a proof mark per criterion, and a GO/NO-GO verdict in `.proofs/`. OK?

Phrase that message in the target project's language, as with every question this skill puts to the user. Do not invoke it silently. If the user declines, follow their instructions.

## Principles

1. **An observation is proof only when read against an assertion.** Every piece of evidence is paired with one sentence: "expected X, observed Y". A screenshot alone is a picture; the observed value is read from the page, the state or the output and written down.
2. **The three proof marks are defined by the evidence.**
   - **PROVEN**: the evidence shows the expected observation.
   - **DISPROVEN**: the evidence shows something else; the actual state is captured.
   - **UNPROVEN**: the state could not be reached or observed; the reason is written down.
3. **The verdict is GO only when every criterion is PROVEN.** A single DISPROVEN or UNPROVEN makes it NO-GO. UNPROVEN is never rounded up to PROVEN.
4. **A mark rests on what was observed in the running app**, never on a reading of the code, the tests or the diff.
5. **The code under test stays untouched.** Proving never edits it (no silent auto-fix), and a failure is explained by `systematic-debugging`, not here.
6. **Test environment, test data.** The app runs locally or in a test environment, with data created for the run. Any step that deletes or sends something outside that environment is confirmed with the user first.
7. **Everything is a file.** Report, evidence and steps live in the repository so that someone else can replay the run cold.

## Workflow

### Phase 0 - Framing

Establish, and record at the top of the report:
- **Where the criteria come from**, in this order: the brief or the request, then the test cases under `docs/business/test-cases/` if they exist, then what the user states. State which source was used.
- **Observable form.** Each criterion is rewritten as Given / When / Then with the visible state expected at the end ("the badge reads `1 item`"). A criterion with nothing observable from outside (a pure internal rule) is left to automated tests and listed as out of scope.
- **Environment**: how the app is started, its address or command, the version or commit, and the test data needed.

A criterion that is ambiguous goes through a multiple-choice question (shape and degraded mode: see `clarify-with-choices`). Never settle an ambiguity by picking the reading that happens to pass.

### Phase 1 - Proof plan

For each criterion, write:
- the **starting state** (and a capture of it, so the change is shown and not only the final state);
- the **steps**;
- the **expected observation**, as a precise assertion;
- the **evidence** planned (see `references/evidence-by-surface.md`).

Validate the plan with the user through a multiple-choice question: go as written, adjust a criterion, or drop one. Do not run before the plan is validated.

### Phase 2 - Run

For each criterion, from its starting state:
1. Perform the steps exactly as planned.
2. At each step that carries an expectation, read the observed value and capture the evidence, named `NN-<criterion>-<step>.<ext>` and kept at full resolution.
3. Append to the raw log: step, expected, observed, evidence file. Facts go in the log; interpretations stay out of it.

If the state cannot be reached, stop that criterion there and mark it UNPROVEN with the reason. If a step fails for a reason outside the feature (app not started, port taken), fix the environment, record both attempts, and rerun the criterion once.

### Phase 3 - Marks and verdict

Give each criterion its proof mark from its log lines, then the verdict from principle 3. When a criterion mixes outcomes (two assertions, one holding and one not), it is DISPROVEN and the report names the assertion that failed.

### Phase 4 - Report and hand-off

Write the report from `references/report-template.md` in the target project's language:
- into the run's work folder when there is one;
- otherwise into `.proofs/<slug>-<YYYY-MM-DD>/REPORT.md`, with the evidence in a `screenshots/` folder beside it (create the folders if needed).

The report opens with the verdict and a TL;DR, and ends with the steps to replay the run. A script that automates those steps, if one was used, is saved in the same folder as the report, so the folder alone is enough to replay it.

Then hand off:
- **GO**: `premerge-review` can read the report as evidence of the acceptance criteria.
- **NO-GO**: each DISPROVEN criterion goes to `systematic-debugging` with its evidence as the symptom; each UNPROVEN criterion says what is needed to reach the state. Ask the user which to pursue.
- **After a fix**, replay the whole plan, not only the failed criteria: a fix can break a criterion that held. Write a new report with a new date, keep the old one, and say which evidence was retaken.

## Inside a run of roles

When this skill runs as a role in an agent organization, the request's brief stands in for the announcement and for the Phase 1 validation: the acceptance criteria are already written there, so write the proof plan from them and run, without asking the user again. An ambiguity still never gets resolved by picking the reading that passes: return it as a blocked hand-off with the multiple-choice question, same as any other role. Add the hand-off front-matter the organization asks for above the report produced here. A step that would delete or send something outside the test environment is never taken on the brief's authority: escalate it. A DISPROVEN criterion goes back to whoever corrects the code in that organization, not to `systematic-debugging` directly.

## Degraded mode

If the agent cannot drive the app or capture a screen, say so at the start. Criteria that need the UI are marked UNPROVEN with that reason; where a command or a request can still observe the behavior, use captured output as the evidence. The report lists these under "Checks not performed". A run with no way of observing anything produces a NO-GO report, not an empty one.

Without `docs/business/` or a brief, the criteria come from the user; without them, ask for them (multiple-choice question) before anything else.

## Common slips

| Slip | Correction |
|---|---|
| Marking PROVEN because the screenshot "looks right" | Write the assertion and the observed value next to it |
| Reaching the state by editing data or code by hand | Reach it through the app, as a user would; else UNPROVEN |
| Explaining the failure from the source | Report the observation, hand off to `systematic-debugging` |
| Reporting only the final state | Capture the starting state too |
| Retaking a screenshot after a fix and replacing the old one | New report, new date, old one kept |
