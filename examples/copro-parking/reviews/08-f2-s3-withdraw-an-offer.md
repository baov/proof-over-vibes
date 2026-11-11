---
role: reviewer
status: escalate
verdict: GO
reasons: [sensitive zone touched: application/offer_use_cases.py (file of the owner role check, _require_owner, and a new owner-only write entry point withdraw_offer); json_offer_repository.py and atomic_file.py untouched]
severity: major
open_majors:
  - "[M1] (carried, S4) Orphan offers (space removed or renumbered) come back under another owner when the number is registered again, and block that owner's new offers. S3 does not make it worse (it gives the blocked owner a way out). S4 AC1/AC6 closes it; S1, S2 and S3 must not be released without S4."
  - "[M2] Two refusal-order edges of withdraw_offer are decided by no document, and one is pinned by no test: an unreadable register with an unknown offer answers UnknownOfferRefused, not StoreUnreadable (the offers are read first). One line in decisions.md (D-69) settles it, with the inner order of the two invalid-input cases (m1)."
---

# Review 1 - F2 S3 Withdraw an offer

## TL;DR
GO. S3 does what its acceptance criteria and D-45..D-68 say; the gauntlet is green and my probes on the real JSON adapters found no defect, and no owner-identity leak through the type or message of a refusal. Two majors stay open (M1 carried to S4, M2 new: an undecided, untested ordering edge). Status `escalate`: the diff touches `offer_use_cases.py`, a sensitive-zone file.

Skill `premerge-review`. Scope: working tree against HEAD (S2 is 26dcd7d): 8 modified files (6 source/docs, 2 test files; +541/-13 with `decisions.md`), 17 new `s3-*` test-cases. Criticality: critical (domain layer, role-check file, new owner-only write on a persisted file, new refusals on a public boundary).

## Gauntlet
| Check | Result |
|---|---|
| Unit suite | OK, 242 tests |
| Harness `run_all.sh` | OK, exit 0, no warning: 94 test-cases, 94 covered_ok, 0 pending, 0 broken, 0 orphan |
| Harness self-tests | OK, 14 |
| Mutation `--scope critical --threshold 90` | 91.0% (181/199). 18 survivors, all of the kinds known from review 07 (`frozen=True`, `indent` 2->3, `offers.py:60` `_next_number = 1`); none on a line of S3 behavior |
| Mutation `--scope diff` | "nothing to mutate", exit 0: the nested-folder defect of review 07 m2 is still there (tools untouched). `--scope critical` is the working substitute |
| Lint | none configured |
| Test-cases touched | critical: the 17 `s3-*` read; `s2-stored-overlap-is-tolerated.md` unchanged and still true |

By-hand mutations on a scratch copy (suite stays 242 green at the start, then each mutant): dropping `save` in `withdraw_offer`, removing the owner check, comparing names without `key()`, swapping the offerer/number validation, not catching `UnknownSpace`, moving the role check after validation, `withdraw` deleting every offer of the space, `withdraw` ignoring `today`, `withdraw` resetting `next_number`: all killed. Two survive, both discussed below: removing `o.number` from the `open_offers` sort key (m2) and loading the register before the offer lookup (M2).

## Probes (own script, real JSON adapters, temp dir)
- Nominal: open offer withdrawn by "Durand", " durand " (case/space), an offer ending today withdrawn; after `change_lot_owner` the old name is `NotTheOwner` and "moreau" withdraws (D-56). One `clock.today()` read per call.
- Refusals: manager, resident, `None`, `"owner"`, `1` are `NotAllowedToOffer` with unreadable offers too, first. Invalid: blank/`None`/non-text offerer, number `0`, `-1`, `True`, `1.0`, `"1"`, `None` give `BlankValueRefused` / `InvalidOfferNumberRefused`; `2**70` is an unknown offer (D-66). Offers file bytes identical after every refusal; unreadable offers file: `OffersUnreadable`, bytes identical; non-owner role and blank offerer are refused before that.
- Identity leak, the point asked: a stranger ("Martin", or a name that owns nothing) gets `NotTheOwner` for an open offer, and `UnknownOfferRefused` with the same type and message for a number never made, a withdrawn one, an expired one and an orphan. So the only fact a stranger learns is "this number is an open offer", which the public listing already shows (number, space, lot, owner). The `NotTheOwner` message echoes the caller's own name and never names the owner. No leak of the owner's identity, of closed offers or of orphans through type or message.
- Orphan: offer on P9 (lot B3), space removed: unknown offer for everyone. P9 registered again under A12: it is listed under Durand, Durand's own new offer is refused naming offer 1 (S2), and Durand can now withdraw offer 1 and then offer. Martin (the old owner) gets `NotTheOwner`.
- Stored pair (hand-written file: numbers 3, 1 unordered, a P2 offer already ended, `next_number` 5): listing `[1, 3]`; withdrawing 3 leaves 1 listed; the file keeps the expired offer 2 and `next_number` 5 (no purge, no reset).

## Acceptance criteria and decisions
S3 AC1..AC5 verified by probe and by test. D-51, D-52, D-54, D-55, D-56, D-58, D-65, D-66, D-67 respected; D-54/D-55/D-58 are the same "unknown offer" path for withdrawn and ended offers; D-65 order (role, invalid input, unknown offer, not the owner) holds in every pairing I tried. D-68 closes review 07 M2 (the wording); it says consumers rely on `offer_number`, and S3's new refusals carry none, which is consistent. INV-003..006: `withdraw_offer` has 5 parameters and stays short; INV-008: `withdraw`/`open_offer` receive `today`, nothing reads the system date. INV-001: the domain imports nothing new from the application.

## Carried-over majors
- **M1 (orphan offers): stays open, deferred to S4 as the brief says. S3 does not make it worse; it slightly mitigates it.** Before S3 an owner blocked by an orphan of a re-registered number had no way out; now the refusal names the offer, the listing shows it under their lot, and they can withdraw it. Cost: that owner can delete an offer made by the previous owner of the number (consistent with D-56, the current owner decides). An orphan whose number is not registered again still cannot be withdrawn by anyone (D-65) and stays in the file until nothing reads it: harmless, since it blocks nothing without a space. S1, S2 and S3 still must not be released without S4.
- **M2 of review 07 (wording of the refusal): closed** by D-68.
- **m1 of review 07 (tie order of a stored pair): closed in effect** by the test, but see m2: the code change that goes with it is redundant.

## Plan's technical choices
- `open_offer`/`withdraw` taking `today`, one clock read in the use case: agreed, as `add` does.
- Finding the offer by number only, then checking the owner against the register: agreed; it keeps "unknown for everyone" simple and never compares on list position.
- Mapping `UnknownOffer` through `_REFUSALS` and reusing `NotAllowedToOffer`/`NotTheOwner`: agreed, one refusal per reason; the reworded `_require_owner` message is covered by D-68.
- No change in `infrastructure/`: right, the adapter saves the whole book. The sensitive write path is exercised by the new restart/bytes tests, not modified.

## Findings
### Major
- **[M2] Refusal-order edges not decided, one not tested** - `offer_use_cases.py:withdraw_offer` (offers loaded before the register), `s3-refuse-unreadable-offers-on-withdraw.md` - angle: compliance. With an unreadable register, a withdrawal of an unknown/expired number ends with `UnknownOfferRefused`, a withdrawal of an open number (or an orphan) with `StoreUnreadable`. The developer disclosed it; D-65 ranks four refusals and says nothing of a store error. No test pins it (swapping the two loads leaves 242 green) and the test-case says "with an unreadable register it ends with the store unreadable error" without the exception. Consequence: a consumer sees a different class for the same failing store depending on the number; it also tells a stranger whether an open offer (an orphan included) exists while the register is broken, which the listing cannot show in that state. Low impact, but a consumer-visible behavior that no decision settled. Recommendation: one line D-69 (either "unreadable store wins over unknown offer" and load the register right after the offers, or "unknown offer wins" and keep the code), one test for the chosen side, and the test-case text aligned. Hesitated with minor because the impact is small; kept at major as the role requires for an undecided visible behavior.

### Minor
- **[m1] Inner order of the two invalid-input refusals is undecided** - `offer_use_cases.py:withdraw_offer` (`clean(offerer)` then `offer_number`). Blank offerer plus bad number reports `BlankValueRefused`; D-66 only says "invalid input". It is tested (`test_a_blank_offerer_is_reported_before_a_bad_number`) and both are invalid input of the same rank, so I keep it minor (hesitated with major). Put it in the same D-69 line as M2.
- **[m2] The explicit sort key in `open_offers` is redundant and its test pins nothing** - `domain/offers.py:open_offers`, `tests/test_offer_use_cases.py:OfferBookWithdrawal.test_the_open_offers_of_a_stored_pair_with_the_same_start_are_ordered_by_number`. `_offers` is number-ordered by construction (`restore` sorts, `add` appends a higher number), so the stable sort already ties by number; I removed `o.number` from the key on a scratch copy and all 242 tests stay green. The change is harmless and documents the intent, but the developer note's "the test pins it" is not true of the key. Either keep it as documentation (say so in a comment) or drop it; do not count it as protection.
- **[m3] The cause chain differs between an orphan and an unknown offer** - `offer_use_cases.py:withdraw_offer` (`raise UnknownOfferRefused(...) from error`). Type and message are identical, but `__cause__` is `UnknownSpace('P9')` for an orphan and `UnknownOffer` otherwise. A consumer that logs the traceback to a stranger-facing channel would reveal the orphan and its space. Use `from None`, or raise one cause for both.
- **[m4] Carried, still open** - `run_mutation.py --scope diff` is a no-op in this nested folder (review 07 m2); the `_next_number = 1` mutant survives (m4 of review 06/07). Not regressions.
- **[m5] Concurrency** - a withdrawal is load, delete, save: a concurrent offer can be lost, or a withdrawn offer can come back, if two callers interleave. Documented limit of ADR-0004, not tested; the plan says so.

## Checks not performed
Lint (none configured). Concurrency (above). Performance: no declared target; `open_offer` sorts the open offers on each call, bounded by the size of the file, no target asked.

## Positive notes
The refusal ranks are tested pair by pair, each with the later refusals also present, and every non-owner role is fed with unreadable stores. A refusal is shown to leave the file bytes, `next_number` and the other offers (expired ones included) untouched, on the real repository. Withdrawing never branches on list position, so the stored pair cannot make it delete the wrong offer.

## Escalation
`application/offer_use_cases.py` is in the sensitive zone "role check of the offer use cases" and gained a second owner-only write entry point. `_require_owner` is unchanged in meaning (its message now covers both actions; D-68) and is the first statement of `withdraw_offer`: probes with manager, resident, `None`, a string and an integer are all refused first, with unreadable stores. The offers write path (`json_offer_repository.py`, `atomic_file.py`) is untouched. The human decides before merge.
