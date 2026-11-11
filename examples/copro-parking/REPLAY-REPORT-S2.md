# Replay report: story 2 (refuse overlapping offers), roles before and after the test-volume doctrine, Reviewer included

## TL;DR

- **Question.** On a second story, and with the Reviewer in the chain, do the NEW roles (`dd55185`) add fewer tests than the OLD ones (`1e746d7`)?
- **Result.** Weakly, and not clearly. Methods added: OLD 10 and 19, NEW 10 and 9 (means 14.5 against 9.5, about a third fewer, the same ratio as on story 3). But the ranges overlap (10 appears in both variants), and the spread inside OLD (9) is as large as the gap between the means (5). Lines of tests: OLD 79 and 122, NEW 110 and 68, no visible gap. Every run is green, bridged, GO at the first review, mutation 90.9 to 91.1 %.
- **Reviewer.** All four reviews are `GO` with no blocking or major finding, so there was no fix iteration and the Developer's answer to a surplus-test finding was not exercised. Surplus tests were reported as `minor` in all four runs, NEW included (3 of 4 findings in NEW 1), so the two-way "Tests" check did not push any verdict.
- **Reading.** Story 2 is a small rule (baseline: 13 methods), so there is less to trim than in story 3 (baseline 54). Together the two stories point the same way for methods, but story 2 alone is within noise.

## Method

The method of the previous report (`claude/replay-story3-0104fe`, `examples/copro-parking/REPLAY-REPORT.md`) applies, with these differences.

- **Start.** `b2b1cc2` (parent of `26dcd7d`, story 1 done, untrimmed suite of 177 tests), one detached worktree per run. OLD = `skills/` and `agents/` of `1e746d7` (identical to `b2b1cc2`), NEW = those of `dd55185`.
- **Roles run.** Planner, Developer, Reviewer, each a subagent of the same model and effort, told to read its prompt and skills from its own worktree and not to consult git history (the Reviewer got the diff from the start to the Developer's result). The Orchestrator was played by this session. Nothing was committed by the Developers; the orchestrator committed their result as one checkpoint to give the Reviewer a diff.
- **Feature files.** The brief of story 2 is the original one. `stories.md` and `architect.md` exist in git only from `1e746d7` (archived with story 4), so they were taken from there. **Caveat:** that `architect.md` was amended after story 2 (it already cites D-63 and D-64 and the "tolerated on load" answer, and `stories.md` cites D-69). The four Planners noticed that those decisions were missing from the log and still asked the questions, but they all saw the recommended answers. Same input in every run, so it does not bias the comparison, but it lowers the questions asked.
- **Product Owner answers.** From the original decisions of story 2: D-63 (a stored overlapping pair is tolerated on load) and D-64 (the refusal names the earliest start, ties by lowest number). All four Planners asked Q1 (D-63); three asked Q2 (D-64, applied also to OLD 2, whose Q1 context covered it). One question had no matching decision: NEW 2 asked **how the refusal carries the existing offer (message only, or message plus a field)**; I answered "message plus a field holding the number", which is what the original plan decided. The other three runs decided that point inside their plan without asking. Developers asked nothing. M1 (orphan offers) was deferred to S4 in every plan, as the brief says.
- **Measures.** After the last Developer pass, in each worktree: `python3 -m unittest discover -s tests`, `bash tools/harness/run_all.sh`, `python3 tools/harness/run_mutation.py --scope critical` (`--scope diff` is a no-op in this nested example, which the Developers and Reviewers reported too). Methods = added `def test_` lines in the diff of `tests/` (and the net growth of the unittest count).

## Results

| | Baseline (original run) | OLD 1 | OLD 2 | NEW 1 | NEW 2 |
|---|---|---|---|---|---|
| Test methods added (net growth of the suite) | 13 (11) | 10 (10) | 19 (19) | 10 (9) | 9 (8) |
| Suite after (from 177) | 188 | 187 | 196 | 186 | 185 |
| Lines of tests added | 100 | 79 | 122 | 110 | 68 |
| `subTest` lines added | 1 | 1 | 2 | 2 | 1 |
| Lines of source added | 42 | 42 | 42 | 43 | 55 |
| Suite green | yes | yes | yes | yes | yes |
| Mutation (critical) | 91.0 % (171/188) | 91.0 % (171/188) | 90.9 % (169/186) | 91.1 % (174/191) | 91.0 % (172/189) |
| Bridge (`run_all.sh`) | exit 0, 77 | exit 0, 79 | exit 0, 76 | exit 0, 77 | exit 0, 77 |
| S2 test-case files written | 8 | 10 | 7 | 8 | 8 |
| Review verdict | GO | GO | GO | GO | GO |
| Findings blocking / major / minor | 0 / 2 (M1 carried, M2 wording) / minor not counted | 0 / 0 / 4 | 0 / 0 / 5 | 0 / 0 / 4 | 0 / 0 / 3 |
| Findings about surplus tests | n/a | 1 (2 items) | 3 | 3 | 1 |
| Tests after a fix iteration | n/a | no iteration | no iteration | no iteration | no iteration |

In the baseline column, the review figures are those of the original run (`reviews/07-f2-s2-refuse-overlapping-offers.md`: GO with two open majors, M1 orphan offers carried to S4 and M2 undecided message wording; the original Reviewer also asked for a missing tie-order test, a minor). None of the four replay Reviewers raised the wording as major (NEW 2 called it a close call), not re-measured. The baseline's 13 added / 2 removed lines come from rewriting the S1 tests that created overlaps; the replays did the same (one to three S1 tests adapted per run).

## Reviewer findings on tests

- **OLD 1** (minor): `issubclass` pins a type hierarchy; the `saves` call count restates what the unchanged-state helper and the next offer number prove. "Drop both."
- **OLD 2** (3 minor): the same type pin and call count; `the overlap is refused when every earlier rule passes` repeats the nominal test; the tolerated-pair test written twice (use case and JSON store); the byte-identical-file check written twice.
- **NEW 1** (3 minor): a test pins the class hierarchy and repeats the call twice; the "overlap is the last refusal" test restates the refusal-order tests; the stored-pair test in the JSON store restates the use-case test, and the Rule 5 test pins a save count.
- **NEW 2** (1 surplus, 1 weak): the "refusal saves nothing" test pins the fake repository's save counter; plus `assertIn("1", str(error))` that passes through the "1" of "P1" (a weak assertion, not a surplus).
- **Missing tests:** none reported by any Reviewer. No finding was rated above `minor`, so there was no NO-GO and no second iteration: **how a Developer answers a surplus-test finding is not measured here.**
- The same three patterns recur in OLD and NEW (type pin, save-count pin, a rule restated at two layers). NEW Developers applied "group the examples, drop restating tests" and still left them, which is where the Reviewer check would act, only as a minor.

## What differed

- **Granularity.** OLD 2 (19 methods) wrote the finest tests; OLD 1 (10) and NEW 1 (10) are equal in count. NEW 1 has fewer methods than lines would suggest (110 lines for 10 methods: wider tests), NEW 2 the fewest lines (68).
- **Design.** OLD 1 and the others put the check in `OfferBook.add`; OLD 1 chose a separate `ensure_free` (a deviation the Reviewer flagged as minor). Not related to the doctrine.
- **Source** is the same size (42 to 43 lines), except NEW 2 (55).
- **Mutation** does not move; survivors are the pre-existing equivalent ones.

## Both stories together

| | Story 3 (previous report) | Story 2 (this report) |
|---|---|---|
| Baseline methods | 54 | 13 |
| OLD runs, methods | 31, 37 (mean 34, spread 6) | 10, 19 (mean 14.5, spread 9) |
| NEW runs, methods | 23, 22 (mean 22.5, spread 1) | 10, 9 (mean 9.5, spread 1) |
| Gap between means | 11.5 | 5 |
| OLD runs, lines of tests | 281, 318 | 79, 122 |
| NEW runs, lines of tests | 250, 223 | 110, 68 |
| Mutation range | 90.8 to 91.0 % | 90.9 to 91.1 % |

**Honest reading of the noise.**
- Methods, direction: NEW is below OLD in both stories, by the same relative amount (about 34 %). In story 3 no NEW run exceeds an OLD run. In story 2 NEW 1 equals OLD 1 (10 = 10), so the ranges overlap.
- Methods, noise: the OLD spread is 6 and 9, and in story 2 the gap between variants (5) is smaller than the OLD spread (9). The NEW spreads (1 and 1) are small in both stories; that the NEW runs agree with each other might be a sign that the doctrine is a constraint, but with n = 2 it is also what chance gives.
- Lines of tests: no consistent effect. In story 2 the NEW mean (89) is below the OLD mean (100.5) only because of NEW 2; NEW 1 has more lines than OLD 1. Story 3 showed 21 %.
- Baselines: story 2's original run (13) falls inside the OLD range, story 3's (54) far above it. Run-to-run variance across sessions is at least as large as the effect.
- Conclusion I can support: no evidence that the NEW roles add more tests, a likely reduction in methods that is small compared with the variance on a small story, and nothing at all on the Reviewer's side because no run reached a NO-GO. No significance claim: 4 runs per story, two stories, one model.
- Not measured: the fix iteration (needs a story where the Reviewer rates a surplus finding `major`, or a Developer run with a seeded NO-GO), a third story, another model, and the cost in tokens of the extra check.

## Reproduce

`git worktree add --detach <dir> b2b1cc2`, then `git checkout 1e746d7 -- skills agents` (OLD) or `dd55185` (NEW), commit if NEW; put `brief.md`, `stories.md`, `architect.md` (from `1e746d7`) and the story 2 brief (from `26dcd7d`) under `examples/copro-parking/.plans/in-progress/offer-a-space/`; run the Planner, the Developer and the Reviewer from `agents/`; answer the questions with D-63 and D-64 of `docs/business/decisions.md`. The run worktrees were temporary and removed at the end.
