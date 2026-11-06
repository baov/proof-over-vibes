# Duration analysis of the three worked examples

Measured on 2026-10-27 from the session logs: 64 sub-agents, 123 passes (a pass is an agent's first launch, or a resume by message), and the main session. The time counted runs from the first to the last agent of each example; the setup and the final README are outside the window. The analysis scripts lived in the session's temporary folder and are not in the repository, so the figures can be checked against the three examples' `.plans/done/` and `.metrics/` folders but not regenerated.

## Machine time per example (minutes)

The time spent waiting for the human's answers is left out: the human was busy elsewhere during the runs, so that time says nothing about the chain. What remains is the time an agent was running, and the Orchestrator's time between two agents.

| Example | Machine time | Agents running | Orchestration and latency |
|---|---|---|---|
| 1, professional network (TypeScript, everything delegated) | 68 | 60 | 9 |
| 2, medical appointments (Java) | 72 | 66 | 6 |
| 3, meal delivery cart (Kotlin) | 165 | 158 | 7 |

- **Questions put to the human:** 18 rounds, 46 questions. Their machine cost is resuming the blocked role after the answer; all resumes together come to 34 minutes (see below).
- **No parallelism:** the sum of the agents' times equals the time during which at least one agent was running. Everything ran in series.
- **Orchestration:** 22 minutes in all, negligible.

## Where the 284 agent minutes go

| Role | Passes | Minutes | Share | Longest pass | What weighs |
|---|---|---|---|---|---|
| Reviewer | 14 | 106 | 37 % | 36 min | experiments in a scratch copy of the project |
| Developer | 13 | 90 | 32 % | 17 min | Maven and npm builds after every small step |
| Planner | 25 | 35 | 12 % | 4 min | the model's reasoning, 2 to 3 passes per plan |
| Harness Engineer | 9 | 20 | 7 % | 6 min | installing and self-testing the harness |
| Product Manager | 20 | 12 | 4 % | 1 min | |
| Architect | 15 | 9 | 3 % | 1 min | |
| Product Owner | 25 | 8 | 3 % | 1 min | |
| Diagnostician, regression-planting agent | 2 | 3 | 1 % | 2 min | |

Tool time and model time are roughly equal (about 143 and 141 minutes). The short resumes (59 passes, median 0.3 minute) weigh only 34 minutes.

### Shell commands of the sub-agents

| Kind | Minutes | Calls |
|---|---|---|
| Scratch copy of the project, then a build | 34 | 36 |
| Builds, tests and harness | 25 | 176 |
| Other (reading, git, files) | 23 | 410 |
| Repeated test runs (flakiness, mutations by hand) | 22 | 82 |
| Oracle scripts (comparison with a computed reference) | 19 | 95 |
| Mutation (PIT, Stryker) | 16 | 123 |

### Longest passes

| Minutes | Example | Pass | Of which |
|---|---|---|---|
| 36 | cart | Reviewer, blank codes and simultaneity | 28 min in three commands: the harness on a scratch copy, a loop of mutants, 30 reruns of the concurrency test |
| 20 | medical | Reviewer, simultaneous bookings | 14 min in two loops of hand-made mutants (lock removed, lock per slot…) |
| 17 | cart | Developer, blank codes and simultaneity | 35 reruns of the concurrency test, a shared-state experiment |
| 15 | cart | Reviewer, amounts | a `BigInteger` oracle over about 12.5 million cases, mutations by hand |
| 13 | cart | Reviewer, story 2 | 10 min in a loop of mutants on a scratch copy |
| 13 | cart | Developer, story 2 | builds after every step |
| 12 | cart | Developer, amounts | builds after every step, mutations by hand |
| 11 | cart | Developer, story 1 | builds after every step |

The Kotlin example costs 2.5 times as much as the other two. Two reasons: the Kotlin compilation on every `mvn -o test` is slow, and it is the example whose briefs asked for the deepest reviews.

## What can be optimized, by decreasing gain

Ranked on machine time alone: the human's waiting is not counted.

1. **Limit the depth of reviews.** The adversarial checks (scratch copy, millions of cases, 30 reruns) came from the Orchestrator's briefs, not from the role file. They should start from a named suspicion and stay short. Gain: about 60 of the 106 review minutes.
2. **Do not widen the mutation.** The briefs asked for mutation over the whole `critical` scope, from the Developer and from the Reviewer. The skills limit it to the diff, and for the review to critical criticality only. Gain: about 10 to 15 minutes.
3. **Target the builds during the TDD loop.** During the red-green cycle, run only the tests of the behavior in hand and the invariants of the files touched; run the full suite and the gauntlet once before handing over. There were 176 build calls, mostly in Kotlin. Gain: about 15 to 20 minutes.
4. **Run independent requests in parallel.** The two edge-case requests do not depend on each other: their Architects and Planners can go ahead together, as long as the Developers do not touch the same files. Gain: about 10 to 15 % of agent time.
5. **Group the questions put to the human.** Without the waiting time, the gain is limited to a few agent resumes: all resumes together weigh 34 minutes, only part of which would come from grouped questions. The main benefit is fewer interruptions for the human, which this measure does not count.

Levers 1 to 4 would bring the Kotlin example from about 158 to about 80 agent minutes. Lever 4 was never measured, and it is the only part of that estimate that was not applied (see below).

## What was done

| Lever | Where | Change |
|---|---|---|
| 1, 2, 3 | `agents/reviewer.md`, `agents/developer.md`: the Reviewer always runs the gauntlet itself (the judge's independence), with mutation on the diff; an experiment beyond the gauntlet starts from a named suspicion and stays short; the Developer targets its builds during the loop | "Developer and Reviewer: build time where it pays" |
| 5 | `agents/orchestrator.md`: questions for the human asked in rounds | "Orchestrator: independent requests side by side, questions for the human in rounds" (the side-by-side part was removed afterwards, see below) |
| Other effects of a confirmed defect | `agents/reviewer.md`: once a defect is confirmed, the Reviewer looks for the other effects of the same cause before concluding (added after the blind test below) | "Reviewer: look for the other effects of a confirmed defect" |

**Lever 4 (parallel requests) was written, then removed.** It changes how requests and branches are managed, and no run exercised it: the validation tests below do not cover it. It stays an idea until two independent requests are replayed side by side. The tests below cover levers 1 to 3 only.

One idea was dropped on the way: having the Reviewer reuse the Developer's report for the same commit. It would have taken away the judge's own check; the time lost came from the experiments and the widened mutation anyway, not from the gauntlet itself.

## Validation test: story 2 of the Kotlin example, replayed

Replayed on 2026-10-27 in a throwaway worktree at the commit just before the story's code (story 1's code, decisions D-1 to D-36, the original plan), with the modified roles, neutral briefs (the role and its inputs, with no request for deeper checks) and the same model as the original run (Sonnet).

| Pass | Original | Replayed |
|---|---|---|
| Developer | 12.8 min (4.9 of builds) | 9.4 min (3.4 of builds) |
| Reviewer | 12.8 min (10.0 of builds and experiments) | 3.2 min (0.6 of builds) |
| Total | 25.6 min | 12.6 min |
| Mutation on the diff | 98.0 % (one survivor) | 100 % |
| The fine-scale defect (overflow of `subtotal x numerator`) | found by the Reviewer, thanks to a brief that cited "scale 18" and "`Long` limits" | reported by the Developer in its note, kept as `major` by the Reviewer and checked by calculation |
| Verdict | GO, 1 major | GO, 1 major and 5 minors |

What it shows:

- **Time cut in half** on this pass. The gain comes mostly from the Reviewer: it ran the gauntlet itself, then no costly experiment.
- **The defect is still found**, and earlier: the Developer saw it, by listing what the code allows that no document decides. The Reviewer confirmed it by calculation (10^15 x 9,224 exceeds 2^63) instead of looking for it by experiment.
- **No visible loss of depth:** the Reviewer raised five minors that the original review did not (a required parameter added to `Price`, a decision written twice, a test with no test-case).

What it does not show:

- **A single attempt.** An agent's duration varies from one run to the next; this is not an average.
- **The hint was in the inputs.** The brief already carried "the overflow reaches the caller as a raw `ArithmeticException`" since the review of story 1. A defect with no hint in the inputs still has to be tested, with the planted regression of example 1.
- **Parallelism** (lever 4) is not tested here, and the rule was removed.

## Validation test: the planted regression, reviewed blind

Replayed on 2026-10-28. The commit of example 1's planted regression (the pair key `[a, b].sort().join(":")` in the in-memory store) is submitted to a Reviewer as an ordinary request: "speed up the lookup of an existing connection, with no change of behavior". There is no bug report, no plan, no Developer's note. Two Reviewers on Sonnet, with the same neutral brief, each in its own worktree, one after the other: one reads the former `reviewer.md` (before the changes above), the other the new one.

In the original run, no Reviewer had seen this commit: the regression was planted outside the chain.

| | Former role | New role |
|---|---|---|
| Duration | 2.0 min | 1.4 min |
| Verdict | NO-GO, collision found and reproduced (`a:b` + `c` against `a` + `b:c`) | NO-GO, collision found and reproduced |
| Second symptom (a connection overwritten, then `eraseMember` changing another pair's state) | found | missed: the overwrite is a minor, with the wrong remark "no path reaches this today" |
| Dead code `connects()` | reported | not reported |
| Harness gap: the mutation scope excludes `infrastructure` | reported, with a Stryker mutation run by hand | noted ("nothing to mutate"), not kept as a finding |

What it shows:

- **The regression is found blind** by both roles, in under two minutes.
- **The slowness of the original reviews came from the briefs.** With a neutral brief, the former role also runs in 2 minutes. The 13 to 36 minute reviews came from checks the Orchestrator asked for. The new roles write that restraint into the role file, but their own gain is small when the brief is neutral.
- **A possible loss of depth with the "short experiment" rule.** The new role stopped at the first confirmation and missed the neighboring effect of the same cause. Hence a rule added to `reviewer.md`: once a defect is confirmed, look for the other effects of the same cause before concluding, and do not call an effect unreachable without trying a path to it.

What it does not show: one attempt per role, without repetition. The new rule has not been replayed.

What it says about the harness: the mutation scope (domain and application) excludes `infrastructure`, where the store lives, a declared sensitive zone. That is a gap of the example, for the Harness Engineer to decide, not a change to a role.

## Limits of the measure

- **Human time left out:** the waiting for answers is not counted. The window of each example is still the one from the first to the last agent.
- **Approximate ranking:** shell commands are ranked by pattern; a compound command is filed under a single kind.
- **Temporary scripts:** the analysis scripts are not in the repository (see the top of this file).
