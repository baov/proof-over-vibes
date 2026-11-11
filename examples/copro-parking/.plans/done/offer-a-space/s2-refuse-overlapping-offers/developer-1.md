---
role: developer
status: done
reasons: ["sensitive zone touched: application/offer_use_cases.py (role check file); escalate to the human by the zone rule"]
---

# Developer note: S2 Refuse overlapping offers (iteration 1)

Skills applied: `plan-driven-dev` (implementation steps), `behavior-driven-testing`. Nothing committed.

## Done
- Test-cases written first as `pending` (`docs/business/test-cases/offer-a-space/s2-*.md`, 8 files), then marked `covered` once green.
- Red before green: tests written first and run against the code without the rule (only `OverlappingOffer` / `OverlapRefused` stubs so that the file imports): 14 failures (first run before the stubs: import errors). Then the rule was implemented: green.
- Domain: `Period.shares_a_day_with`, `OfferBook.add(space, period, today)` raises `OverlappingOffer(offer_number)` for the earliest-start, then lowest-number open offer of the space (D-64); `restore` unchanged (D-63, tolerated).
- Application: `offer_space` reads `clock.today()` once, passes it to `add`, maps the error to `OverlapRefused` (carries `offer_number`) before `save`; overlap is the last check.
- Infrastructure: untouched.
- Rewritten S1 tests that created overlaps (see plan section 8).

## Results
- `python3 -m unittest discover -s tests`: 188 tests OK (177 before).
- `bash tools/harness/run_all.sh`: exit 0, 77 test-cases all covered, 0 pending, 0 orphan.
- Harness selftests: 14 OK.
- Mutation `--scope critical --threshold 90`: 91.0% (171/188), above the threshold; 17 survivors, all pre-existing (`frozen=True`, `indent`, and `offers.py:52` `_next_number = 1`); none in the new code.
- Mutation `--scope diff`: "no source file in scope: nothing to mutate". Probable cause: the tool lists changed files with `git diff --name-only` from the repository root, so the paths are prefixed `examples/copro-parking/` and never match its `src/...` filter. Not fixed (out of scope); the critical scope covers the same files.

## Behaviors added (no document decides them)
- `OfferBook.add` has a required third parameter `today` (decided in the plan; public interface change).
- `OverlappingOffer` / `OverlapRefused` expose `offer_number` (decided in the plan) and their message reads "offer N of the same space shares a day with this period" (wording not decided; the number is in the text).
- The overlap compares the space as registered (`P1` and ` p1 ` are the same), decided in the plan.
- A stored offer on the same space number still blocks even if the space left the register (orphans, M1): deferred to S4 as planned.

## Reviewer minors of review 06
m2 (first number default is 1) and m3 (bad period + blank pair): the plan does not list them, so not done. The `_next_number = 1` mutant still survives.

## Sensitive zones
`application/offer_use_cases.py` touched (role check file; the role check itself is unchanged). `json_offer_repository.py` not touched. Expect escalation by the zone rule.

## Commits
None (instruction: do not touch git).
