# Replay report: story 3 (withdraw an offer), roles before and after the test-volume doctrine

## TL;DR

- **Question.** Do the Planner and Developer produce fewer tests at generation time once the doctrine of `dd55185` ("How many tests", one test per rule, examples as cases) is in place?
- **Result.** Yes, on this story: the NEW runs add **22 and 23** test methods, the OLD runs **31 and 37**. Mean 22.5 against 34, so about a third fewer methods and 21 % fewer lines of tests. Every run is green, bridged and above the mutation threshold (90.8 to 91.0 %, same band as the baseline's 91.0 %).
- **Reading.** An indication, not a proof: 2 runs per variant, one story, one model. The spread inside NEW (1) is small, the spread inside OLD (6) is not, and the gap between the variants (11.5) is about twice the OLD spread. The two ranges do not overlap, but n = 2.
- **Caveat that matters.** The original run (54 methods) is far above both OLD replays (31, 37), though it used the same OLD roles. Run-to-run and model variance is therefore larger than the OLD-vs-NEW gap: do not read "54 to 22" as the effect of the doctrine.

## Method

- **Start.** `examples/copro-parking` as of `26dcd7d` (story 2 done, untrimmed suite of 188 tests), one detached git worktree per run.
- **Variants.** OLD = `skills/` and `agents/` of `1e746d7`; NEW = those of `dd55185`. The role prompts differ only by the doctrine (the OLD overlay is identical to `26dcd7d`).
- **Roles run.** Planner, then Developer, each as a subagent of the same model and effort as the orchestrating session, told to read its role prompt and skills from its own worktree and not to consult git history. The Orchestrator was played by this session. The Reviewer was **not** run (cost; the doctrine's review check is not what is measured here), so there is no GO/NO-GO and no iteration 2.
- **Product Owner answers.** Identical in every run: each planner question was answered from the original run's decisions D-65 (refusal order, orphan offer is unknown), D-66 (unusable number or offerer is invalid input), D-67 (returns the withdrawn entry), D-68 (wording not relied upon), recorded in the run's `decisions.md`. Where a planner's question differed from the original one, the matching decision was applied to the point it covered (OLD 1, OLD 2 and NEW 1 proposed "bad number = unknown offer" as the recommended option; D-66 overrode it; NEW 1 had planned "returns nothing" without asking and was corrected to D-67). The Developer of OLD 2 raised one extra blocking question (a clause of D-65 about a re-registered number cannot be implemented: M1, deferred to S4); it was answered "accept, S4 closes it", which is what the original run did.
- **Measures.** Run by the orchestrator in each worktree after the Developer finished: `python3 -m unittest discover -s tests`, `bash tools/harness/run_all.sh` (the bridge check), `python3 tools/harness/run_mutation.py --scope critical`. Test methods = `def test_` added in the diff against the start (and equal to the growth of the unittest count in every run); subtests = added lines mentioning `subTest`. `--scope diff` is a no-op in this nested example, hence `critical`.

## Results

| | Baseline (original run) | OLD run 1 | OLD run 2 | NEW run 1 | NEW run 2 |
|---|---|---|---|---|---|
| Test methods added | 54 | 31 | 37 | 23 | 22 |
| Suite after (from 188) | 242 | 219 | 225 | 211 | 210 |
| Lines of tests added | 429 | 281 | 318 | 250 | 223 |
| `subTest` lines added | 9 | 6 | 11 | 8 | 5 |
| Lines of source added | 88 | 85 | 88 | 93 | 93 |
| Suite green | yes | yes | yes | yes | yes |
| Mutation (critical) | 91.0 % (181/199) | 90.9 % (179/197) | 91.0 % (182/200) | 90.8 % (178/196) | 91.0 % (183/201) |
| Bridge (`run_all.sh`) | exit 0 | exit 0, 101/101 | exit 0, 90/90 | exit 0, 88/88 | exit 0, 99/99 |
| S3 test-cases written | 17 | 24 | 13 | 11 | 22 |
| Deviation / question | none | none | 1 developer question (M1 clause) | planned "returns nothing", corrected | none |

Test methods are the number the doctrine targets. Lines of source are about equal everywhere (85 to 93): the same behavior was built, only the tests moved.

## Coverage of story 3

All runs cover the same behaviors, judged from the test-case files and the tests: withdraw by the current owner and see it leave the list; role refusal first; unknown, already withdrawn and ended offers; not the owner; unusable number or offerer; refusal order; refusals leave the offers unchanged; unreadable offers file; persistence across re-read or restart; the withdrawn days are free again; other files untouched; the tie order of a stored overlapping pair.

Differences in granularity, not in behavior:
- The baseline and OLD 1 write one test-case per example (17 and 24 files); NEW 1 and OLD 2 group them per rule (11 and 13). NEW 2 has 22 test-cases yet only 22 methods: its test-cases are fine-grained but its tests are grouped per rule (examples as subtests).
- The orphan offer (space gone from the register) has its own test-case in the baseline, OLD 1 and NEW 2; in OLD 2 and NEW 1 it is covered inside a broader test (OLD 2 also pins the re-registered number). I did not check each behavior down to the assertion; this list comes from names and reports.

## What differed

- **NEW runs state fewer, wider tests.** Their developer notes say the examples were grouped per rule and restating tests dropped (NEW 2: "grouped examples per rule and dropped two tests that restated others"), which is the doctrine's text.
- **The NEW Planners did not ask fewer questions** (3 each, like OLD); the doctrine does not touch that.
- **Mutation score does not move** (90.8 to 91.0 %): the survivors are the same pre-existing equivalent ones (`frozen=True`, `indent`, the first `next_number`) in every run. Fewer tests did not cost a killed mutant on this code.
- **Source is slightly larger in NEW** (93 against 85 and 88 lines), within noise.

## Honest reading of the noise

- Methods: OLD 31 and 37 (spread 6, i.e. 18 % of their mean), NEW 23 and 22 (spread 1). Gap between means: 11.5, about twice the OLD spread. Lines of tests: OLD 281 and 318, NEW 250 and 223; the ranges are closer (250 against 281) and lines show a smaller effect (21 %) than methods (34 %), because NEW tests are longer on average (about 10.5 lines per method against 8.8 in OLD: wider tests, as intended).
- With two runs per variant, a Mann-Whitney style statement is impossible and I do not claim significance. What can be said: in four runs, every NEW run is below every OLD run, and the two NEW runs are almost identical.
- The baseline is an outlier for both variants (54). The original session ran the same OLD roles but is a different execution (different model state, a human in the loop for decisions, an earlier pass). So run-to-run variance across sessions is at least as large as the effect measured here. The replays do not let us attribute the baseline's 54 to anything.
- Not measured: the Reviewer's side of the doctrine (the two-way "Tests" check), a second story, other models, and whether a later trimming pass would bring OLD to NEW's volume (the earlier trim study suggests it would, at a cost).

## Reproduce

Worktrees were temporary and removed at the end. To redo a run: `git worktree add --detach <dir> 26dcd7d`, `git checkout 1e746d7 -- skills agents` (OLD) or `dd55185` (NEW) inside it, put the feature brief, `stories.md`, `architect.md` and the story brief under `.plans/in-progress/offer-a-space/`, run the Planner then the Developer prompts from `agents/`, answer the questions with D-65 to D-68 of `docs/business/decisions.md`.
