---
role: reviewer
status: escalate
verdict: GO
reasons: [sensitive zone touched: application/offer_use_cases.py (file of the owner role check, _require_owner, and the call to the offers save); json_offer_repository.py untouched]
severity: major
open_majors:
  - "[M1] (carried, S4) Orphan offers (space removed or renumbered) come back under another owner when the number is registered again; since S2 they also BLOCK that new owner, and the refusal names an offer the listing never shows. S4 AC1/AC6 closes it; S1 and S2 must not be released alone."
  - "[M2] The wording of the overlap refusal message is decided by no document. The offer number is contractual (attribute, D-64); the sentence is not. Record one line in decisions.md (message not contractual, consumers use offer_number) or fix the wording."
---

# Review 1 - F2 S2 Refuse overlapping offers of the same space

## TL;DR
GO. S2 does what its acceptance criteria and D-45..D-64 say; the gauntlet is green and my probes on the real JSON adapters found no defect in the new code. Carried major M2 (S1 files vs the load check) is closed by D-63; M1 stays open until S4 and is slightly worse. Status `escalate`: the diff touches `offer_use_cases.py`, a sensitive-zone file.

Skill `premerge-review`. Scope: working tree against HEAD (S1 is b2b1cc2): 10 modified files, 8 new test-cases, 6 source/test files with code. Criticality: critical (domain layer, persisted-file behavior, role-check file, new refusal on a public boundary).

## Gauntlet
| Check | Result |
|---|---|
| Unit suite | OK, 188 tests |
| Harness `run_all.sh` | OK: 77 test-cases, 77 covered_ok, 0 pending, 0 broken, 0 orphan |
| Harness self-tests | OK, 14 |
| Mutation `--scope critical --threshold 90` | 91.0% (171/188). 17 survivors, all pre-existing kinds (`frozen=True`, `indent` 2->3, `offers.py:52` `_next_number = 1`); none on the new lines (`shares_a_day_with`, the `min` key, the `today <=` filter are all killed) |
| Mutation `--scope diff` | "nothing to mutate": a tool defect, see below |
| Lint | none configured |

**`--scope diff` is a tool defect.** `select_files` runs `git diff --name-only HEAD -- src` with `cwd=root`; git prints paths relative to the repository root (`examples/copro-parking/src/...`), then the tool joins them to `root`, giving `.../copro-parking/examples/copro-parking/src/...`, which never matches. I confirmed the output: without `--relative` the paths carry the prefix, with `--relative` they read `src/...`. The tool is only correct when the example is the repository root, so every nested project (this one) silently gets "nothing to mutate" and exit 0: a gate that passes by doing nothing. Fix: add `--relative` to the git call. Not fixed here (read-only). Until then, `--scope critical` is the working substitute (it covers the same files).

## Probes (own script, real JSON adapters, temp dir)
- Overlap: offer P1 20-24; refused naming 1 for 24-30, 18-20, 22-22 (one day), a `date` object pair; accepted for 25-30 and 15-19 (adjacent days). Other space, same days: accepted; another owner's space, same days: accepted.
- Refusal changes nothing: offers file bytes identical after the refusal, no stray file, next offer gets the number it would have had (2). Corrupt file plus an overlap-shaped request: `OffersUnreadable`, bytes identical.
- Order (AC5): from an overlapping request, resident-as-manager, bad period, blank offerer, unknown space, not the owner each win over the overlap. In particular a non-owner asking for an overlapped space gets `NotTheOwner`: the existence of offers is not leaked to non-owners.
- Expiry: an offer ending today still blocks today; the day after it no longer blocks.
- D-63/D-64: a stored file written by hand with three overlapping offers (numbers unordered in the file) loads and lists; a tie on equal starts names the lowest number; a new offer on free days succeeds.
- Space comparison: ` p1 ` and `P1` are the same space (compared as registered).
- Orphan: offer on P2, remove P2, register P2 again for another lot (Martin): Martin's offer on those days is refused as `OverlapRefused` naming offer 1, which the listing does not show (M1).

## Acceptance criteria and decisions
AC1-AC6 verified by probe and test. D-48 (overlap refused), D-52 (open until the end day), D-61, D-63, D-64 and PRD 15 (overlap last) respected. INV-003..006: `offer_space` keeps 5 parameters, no new parameter; INV-008: `add` receives `today`, nothing reads the system date. ADR-0004 and the architect note were amended consistently with D-63 (the plan assigned this to the Architect; it is present in the working tree).

## Carried-over majors
- **M2 (S1 files vs load-time check): closed.** D-63 tolerates a stored overlapping pair; the code adds no load check (`restore` unchanged), and `test_a_stored_pair_of_overlapping_offers_loads_and_only_new_offers_are_checked` plus the test-case `s2-stored-overlap-is-tolerated` pin it. My probe agrees. One accepted consequence: until S3 (withdraw) nothing can remove such a pair.
- **M1 (orphan offers): stays open, deferred to S4 as the plan says**, with a worse symptom than in S1: the orphan now blocks a new owner of a re-registered number and the refusal names an offer that is invisible in the listing. The test-case `s2-refusal-names-the-earliest-offer` says "the number is the one the listing shows", which is false for an orphan.

## Plan's technical choices
- `today` as a third parameter of `OfferBook.add`: agreed. The domain stays clock-free (INV-008) and expiry is judged where the rule lives. It reuses the single clock read of the use case, so the period and the expiry cannot disagree. It is a public signature change, but the only caller is the use case.
- Overlap predicate on `Period`, naming rule in `OfferBook`: agreed; `a.start <= b.end and b.start <= a.end` is right on both ends (killed by mutation, tested on adjacent days).
- Mapping `OverlappingOffer` -> `OverlapRefused` inside `offer_use_cases.py` instead of `_REFUSALS`: justified (needs the number); it sits before `save`, so a refusal never writes. Cost: a second place that translates domain errors, with a `from error` chain: acceptable.
- `add` goes through `open_offers(today)`, which sorts the whole list on every add: O(n log n) per add. Irrelevant at the scale of a co-ownership (my 20k-offer probe was slow, but that is not a declared target); no finding.

## Developer's "Behaviors added"
- Wording of the message: see M2. A consumer that shows `str(error)` shows "offer N of the same space shares a day with this period". The number is also an attribute, so a consumer never needs to parse the sentence. What a consumer cannot get from the refusal is the dates of the blocking offer; the listing shows them (for a non-orphan). Practical risk is low, hence "record the contract" and not "change the code".
- Space compared as registered, `add` signature, orphan still blocking: verified; the last is M1.

## Rewrites of S1 tests: do they weaken S1?
- "same request twice" -> distinct periods, and the test-case `s1-offer-numbers` updated: no weakening. The old behavior is forbidden by D-48, and the new test still pins numbers 1 and 2; the repeated request is covered by S2.
- Restart test of the JSON repository (third offer on other days): no weakening.
- List-order test: the fourth offer changed from a second P2 offer (same start, same space) to P3/Martin. AC8 only requires "start, then natural space order", which the new test pins. What is lost is the old "ties keep creation order": same start and same space is now reachable only through a tolerated stored pair (D-63). I checked that the order is by number there (`[2, 5, 9]` from a file written unordered), but no test asserts it. Minor (m1).

## Findings
### Major
- **[M1] Orphan offers (carried, S4)** - `offers.py:add` (filter on `o.space_number`), `offer_use_cases.py:list_open_offers` skip - angle: bugs. See above. Recommendation: no change in S2; S4 AC1/AC6 must land before any release; fix the sentence "the number is the one the listing shows" in the S2 test-case when S4 closes it.
- **[M2] Message wording undecided** - `domain/errors.py:OverlappingOffer`, `offer_use_cases.py:offer_space` - angle: compliance. Recommendation: one line in `decisions.md` saying the sentence is not contractual and `offer_number` is, or have the human choose the wording. No code change needed.

### Minor
- **[m1] Tie order of a tolerated pair is untested** - `tests/test_offer_use_cases.py:ListOrder`. Add a test with a stored pair of equal start and space listing in number order.
- **[m2] `run_mutation.py --scope diff` is a no-op in a nested folder** - `tools/harness/run_mutation.py:141`. Add `--relative` to the git call; consider failing, not exiting 0, when the diff touches `src` and nothing is selected.
- **[m3] Test-case example differs from its test** - `s2-refusal-names-the-earliest-offer.md` describes offers 10-12 and 14-16; the test uses 24-26 and 20-22 (stronger: the earliest start is offer 2, not offer 1). Align the text.
- **[m4] Carried from review 06, still open** - the `_next_number = 1` mutant survives (no test of a fresh `OfferBook().next_number`); bad period plus blank pair still unstated in D-59. The plan left them out; not regressions.
- **[m5] Imports** - `tests/test_offer_use_cases.py` places the new domain imports before `application.use_cases`: order only.

## Checks not performed
Lint (none configured). Concurrency: two callers can both pass the check, documented limit of ADR-0004, not tested. Performance: no declared target.

## Positive notes
The overlap test is exercised on both ends and on every refusal rank with the overlap present. The D-63 tolerance is pinned both at domain and file level. The `min` key naming rule is proved with a case where the earliest start is not the lowest number.

## Escalation
`application/offer_use_cases.py` is in the sensitive zone "role check of the offer use cases". The role check is unchanged in meaning (probe: manager, resident and non-owners still refused first), but the file changed, so the human decides before merge. The offers write path (`json_offer_repository.py`, `atomic_file.py`) is untouched.
