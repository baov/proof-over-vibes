---
role: reviewer
status: escalate
verdict: GO
reasons: [sensitive zones touched: manager-only role check (remove_space, change_space_number rewritten), the fail-closed OfferCheck call in both, offer_use_cases.py (withdraw_offer, role-check file); offers write path (json_offer_repository.py, atomic_file.py) untouched]
severity: major
open_majors:
  - "[M1] (carried, reduced) Orphan offers already stored in a pre-S4 file still come back under another owner when their number is registered again, and also when a space is renumbered INTO that number (change_space_number target), which D-69 and the plan do not mention. No use case can create a new orphan any more. Decide: leave (document the renumber path in D-69) or guard register_space and the renumber target against a stored orphan."
---

# Review 1 - F2 S4 A space with an open offer cannot be removed or renumbered

## TL;DR
GO. S4 does what AC1..AC6 and D-45..D-71 say. I reran the gauntlet myself and probed the real JSON adapters: no defect in the new code. The fail-closed call has no `except` and is pinned by tests with `OffersUnreadable` and an arbitrary exception. M1 (orphans) is closed for every new write; one narrow residue stays for pre-S4 files (M1 below). M2 of review 08 is closed (code, test, test-case, D-70). F2.1 as a whole (S1..S4) holds together: the "must not ship without S4" condition is met. Status `escalate`: sensitive zones are touched.

Skill `premerge-review`. Scope: working tree against HEAD (S3 is 09dbe9b): 14 modified files (+708/-71), 15 new `s3-*`/`s4-*` test-cases, all under `examples/copro-parking`. Criticality: critical (domain layer, role-check file, fail-closed data path, breaking public signatures, persisted-file behavior).

## Gauntlet (my own runs)
| Check | Result |
|---|---|
| Unit suite | OK, 303 tests (matches the developer's number) |
| Harness `run_all.sh` | OK, exit 0: 109 test-cases, 109 covered_ok, 0 pending, 0 broken, 0 orphan test |
| Harness self-tests | OK, 14 |
| Mutation `--scope critical` | 91.3% (188/206), threshold 90. 18 survivors, all of the known kinds (`frozen=True`, indent 2->3, `offers.py:60` `_next_number = 1`); none on a line S4 added or changed |
| Mutation `--scope diff` | still "nothing to mutate" (nested-folder defect, tools untouched); `--scope critical` is the substitute |
| Lint | none configured |
| Git | HEAD still 09dbe9b, no new commit, no stash; every changed path is under `examples/copro-parking`; `.plans` and `.reviews` are ignored |

Hand mutations on scratch copies (each run against the full suite), all KILLED: `except Exception: pass` around the offer call in `remove_space`, and the same in `change_space_number`; offers asked before the rental; `change_space_number` asking the typed number instead of the registered one; either offer check dropped; `has_open_offer` without `key()` (both sides); end boundary `>` instead of `>=`; adapter with a fixed date; adapter caching the book; offer check moved before the register's own change; same-value change exempted (D-71); `withdraw_offer` loading register before offers (D-70); `from error` instead of `from None` (m3).

## Probes (own script, real JSON adapters, temp dir)
- Nominal: open offer on P1 (end 25 Nov, today 11 Nov): `" p1 "` removal and renumbering to `P9`, `p1`, `" P1 "` all `SpaceOfferedRefused`, both files byte-identical; P2 removed; after `withdraw_offer` both actions succeed.
- Rank: rental and offer together gives `SpaceRentedRefused` and the offers port is not asked. Other roles (owner, resident, `None`, `"manager"`) are `ManagerOnly` first, even with a corrupt offers file. Blank/`None` number, unknown space and duplicate target win over a corrupt offers file (offers not read).
- Fail closed: corrupt offers file ends a valid removal or renumbering with `OffersUnreadable`, both files byte-identical; a port raising `RuntimeError` propagates in both use cases; a corrupt register gives `StoreUnreadable`.
- Dates: end day still blocks, day after frees it, future start blocks; the expired offer stays in the file (no purge).
- Old four-argument call fails with `TypeError` (no default, fail loud).
- Orphans (hand-written pre-S4 file with an offer on never-registered P9): not listed, withdraw is unknown offer (Martin included). After `register_space P9` under Martin it is listed under Martin, blocks his removal/renumbering, and he can withdraw it (D-69 as written). **Not covered by D-69**: `change_space_number(P1 -> P9)` by the manager is accepted and the orphan is listed under Durand (A12), and Durand's own offer on P9 is refused as overlap with an offer he never made (M1).

## Acceptance criteria and decisions
AC1..AC6 verified by test and by probe. D-50 (an offer is not a rental: `NoRentalYet` untouched, rank rental then offer), D-51, D-52 (end date included), D-57/D-71 (every change of an offered space refused, rank role, blank new number, unknown, duplicate, offered), D-62/D-65 (orphans unknown), D-69 (orphans left as they are, behavior matches the text for registration), D-70 (store error wins over unknown offer; both stores unreadable gives `OffersUnreadable`; blank offerer before bad number), D-71 all respected. INV-001 (port in `application`, adapter in `infrastructure`, domain imports nothing new), INV-003..006 (`remove_space` 5 parameters, 130-line module, short bodies), INV-008 (`has_open_offer` receives `today`; only `SystemClock` reads the date).

## Carried-over majors
- **M1 orphan offers: closed for new data, residue open** (see M1 below). Before S4 `remove_space`/`change_space_number` created orphans; now both refuse an offered space, and an expired offer left behind can never become open again. Only a pre-S4 file can hold a live orphan.
- **M2 of review 08: closed.** D-70, the `WithdrawStores` tests (every number kind with an unreadable register, both stores), the aligned test-cases `s3-unknown-offer-vs-unreadable-register.md` and `s3-refuse-unreadable-offers-on-withdraw.md`. Minors m1 (blank offerer before bad number, in D-70, already tested) and m3 (`from None`, `s3-unknown-offer-has-no-cause.md`) are closed too.

## Technical choices challenged
- `OfferCheck` as a one-method `bool` port, adapter loading on each question: agreed (no stale cache; mutant "cache" killed).
- Offer check after the register's own change, on the in-memory register: gives the D-71 rank for free, but see m1 (relies on `load()` returning a private copy).
- `_registered_number` helper swallowing `DomainError` to keep the register's refusal order: acceptable and documented in the plan's deviations; slightly roundabout, harmless.
- Passing the registered number (not the typed one) to the port and comparing by `key()` in the adapter: right; covers a pre-S4 case mismatch.
- "Behaviors added": all three confirmed. `has_open_offer` on a blank or non-text number raising `BlankValue` (a domain error, not a `Refusal`) is real (probe: `chk.has_open_offer("")`) but unreachable from the use cases; see m2. The `TypeError` on an old call is pinned and intended.

## Findings
### Major
- **[M1] Stored orphan offers still resurface, including through a renumbering** - `use_cases.py:change_space_number`, `use_cases.py:register_space`, D-69 - angle: bugs/compliance. A pre-S4 offers file may hold an open offer on a number with no space. D-69 leaves it and says it becomes live "if the number is registered again"; the plan's out of scope names `register_space` only. The probe shows the same resurrection when a space is renumbered into that number: the offer is listed under the renumbered space's owner, who never made it, and blocks that owner's own offer on the space (the refusal names an offer they can withdraw, thanks to S3). Visible to residents (a space shown on offer with dates its owner never chose). Reach is limited to pre-S4 data; no new write path creates it. Recommendation: either record the renumber path in D-69 (one line) and add a test-case, or have `register_space` and the renumber target refuse a number that has a stored open orphan. Hesitated with minor because of the reach; kept major as a consumer-visible behavior no document settles.

### Minor
- **[m1] The renumbering refusal relies on `load()` returning a private copy** - `use_cases.py:change_space_number` (check after `register.change_space_number`), `ports.py:RegisterRepository`. Probe: with a repository that caches and returns the same `Register`, a renumbering refused as `SpaceOfferedRefused` has still changed the cached register (`P1` became `P9`). The JSON adapter and the fake load afresh, so nothing is wrong today; `remove_space` is not affected (check before removal). Recommendation: say in the `load` docstring that it returns an independent register, or ask the offers before mutating (compute the register's refusals first), and pin it with a test.
- **[m2] The port can leak a domain error** - `domain/offers.py:has_open_offer`, `wiring.py:StoredOfferCheck`. A blank or non-text number raises `BlankValue`, while the port promises a `bool` or a store error. Unreachable today. Either note it in the port docstring or return `False`/raise a defined error; do not return `False` for blank in the use cases' path without thinking about fail-closed.
- **[m3] Carried: `OfferBook.add` compares the space exactly** - `domain/offers.py` (`o.space_number == space`). With a pre-S4 case mismatch an overlap can slip in. Out of scope per the plan; now reachable only through stored data.
- **[m4] Stale documents outside this story** - `README.md` says 47 test-cases (now 109), `docs/product/story-map.md` shows F2.1 as todo, and the note under S4 in `stories.md` ("the case disappears once removal is blocked") is not true for stored files (D-69). Product Owner's files.
- **[m5] Carried tooling items** - `run_mutation.py --scope diff` is a no-op in this folder; `_next_number = 1` survives. Not regressions. Concurrency (a removal racing an offer) is the documented ADR-0004 limit, untested.

## Does F2.1 (S1..S4) hold together?
Yes. End to end on the real adapters: register, offer (S1), overlap refused (S2), withdraw by the owner (S3), removal and renumbering refused while open and allowed after withdrawal or end date (S4). The three order chains (role, input, existence, ownership; manager, register refusals, rental, offer; stores before unknown offer) are consistent, and every refusal leaves both files byte-identical. The S1-S3 condition "must not ship without S4" is met for all data written from now on; the only residue is M1 for files written before S4.

## Checks not performed
Lint (none configured). Concurrency and performance (no declared target). The human decision on the sensitive zones below.

## Positive notes
The tests pin the right things: exact `True`/`False`, call order and call count of the ports with stubs, real semantics (open, ended, today, future) through the real use cases, and bytes plus restart on the real repositories; 15 of 15 hand mutants died. The plan's risk list (no `except`, wrong rank, bool-ish answer) was turned into tests one by one.

## Escalation
The diff touches three sensitive zones of `invariants.md`: the manager-only role check (`remove_space` and `change_space_number` rewritten; `_require_manager` unchanged and still the first statement, probes with four non-manager roles confirm), the fail-closed `OfferCheck` call (new, no `except`, mutants wrapping it die), and `offer_use_cases.py` (`withdraw_offer`: `_require_owner` untouched and first; only the read order and `from None` changed). The offers write path is untouched. The human decides before merge.
