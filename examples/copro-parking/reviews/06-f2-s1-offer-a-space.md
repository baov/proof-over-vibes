---
role: reviewer
status: escalate
verdict: GO
reasons: [sensitive zones touched: offer_use_cases.py role check (_require_owner), json_offer_repository.py write path via atomic_file.py]
severity: major
open_majors:
  - "[M1] Until S4, a space removed or renumbered leaves its offers in the file; if the number is registered again (other lot, other owner) they are listed again under the new owner, who never made them. D-62 settles the skip, not this return."
  - "[M2] S2 will add the load-time overlap check, but S1 already lets overlapping offers be written (D-48 not yet enforced); no decision says what S2 does with an existing file that contains them (unreadable = the feature is dead)."
---

# Review 1 - F2 S1 Offer a space and list the open offers

Skill `premerge-review`. Criticality: critical (domain layer, persisted format, role check, new public boundary). Scope: working tree against HEAD, nothing of S1 committed: 12 modified files, 14 new paths (22 test-cases).

## Gauntlet
| Check | Result |
|---|---|
| Unit suite | OK, 177 tests |
| Harness `run_all.sh` | OK: 69 test-cases, 69 covered_ok, 0 pending, 0 violation (INV-008 `check_clock.py` included, clean) |
| Mutation | `--scope diff` finds nothing to mutate (uncommitted), so `--scope critical`: 90.6% (164/181), threshold 90. 17 survivors: `frozen=True` -> False, `indent` 2 -> 3, plus `offers.py:49` (see m2) |
| Lint | none configured |

## Probes (own script, real JSON adapters, temp dir)
- AC6: manager, resident, `None`, the string `"owner"` with bad dates, unknown space and a corrupt offers file: `NotAllowedToOffer` each time. An owner with a corrupt file still gets `InvalidPeriodRefused` / `UnknownSpaceRefused` / `NotTheOwner` (register read, offers not); a valid offer on a corrupt file: `OffersUnreadable`, bytes identical.
- Dates: start = end ok; today ok; yesterday, end < start, `None`, `"2026-1-1"`, `"2026-02-30"`, `"2026-13-01"`, year 0000, full-width digits, `int`, `bool`, ISO datetime text, a `datetime` object: all `InvalidPeriodRefused`. Spaces and a trailing newline are ignored (D-60). End `9999-12-31` accepted.
- Space/offerer: case and spaces ignored and the space shown as registered; blank, `None`, `5` on either field -> `BlankValueRefused`; other owner -> `NotTheOwner`.
- Pairs of AC10: role > period > blank > unknown > not-the-owner as planned; bad period + blank space gives the period (not stated by D-59, see m3).
- AC8/AC9: sort by start then natural space (`P2` before `p10`), ties by number; open on the end day, gone the next; owner follows `change_lot_owner`; listing twice identical; restart gives the same list.
- AC11-AC13: a refusal on first use creates no file; offering leaves the register bytes identical and creates no rules file; numbers 1.. never reused; `os.replace` failing leaves the file unchanged and no `.tmp`.
- AC12: 31 corrupt files (invalid JSON, non-UTF-8, list/null/text root, `offers` null/text/dict, entry as text, missing end, impossible date, end < start, duplicate number, number >= `next_number`, `next_number` float/bool/0/negative/null/NaN/1e400/5000 digits, number float/bool/0, space blank/int, date int/datetime text, 100000 nested brackets): `OffersUnreadable` on list and offer, bytes identical every time. Lenient reads as D-61 and the developer say: empty/blank/`{}` = no offers; extra keys ignored; stored past offers load; a file with offers but no `next_number` is unreadable.
- Orphan (D-62): removing `P1` hides its 6 offers, as decided. See M1.

## Plan's technical choices
- Load-time overlap check moved to S2: **agreed**. S1 accepts overlaps, so enforcing it at load now would make S1 write files it cannot read. The consequence is M2.
- `Period` built with today passed in, one clock read per call: sound, INV-008 clean and tested (`reads` counter).
- Names only the developer sees (`Offer`, `OfferBook`, `Period`, `parse_date`): no clash with the glossary-level vocabulary found.

## Developer's "Behaviors added"
1. Dangling offer skipped: now decided by the human (D-62). Tested, but no test-case file describes it (m4); the follow-on is M1.
2. Period before blank fields: unstated by D-59, untested as a pair (m3).
3. Input and ownership refusals before reading the offers file: verified, consistent with AC6/AC10.
4. Missing `next_number` = 1 and offers present = unreadable: verified, safe (fails closed).
5. Past start refused only at creation: verified (`past offer` file loads).
6. Space stored as registered, trimmed: verified. After a space renumbering the stored number goes stale (M1).

## Findings
### Major
- **[M1] Orphan offers come back under another owner** - `offer_use_cases.py:list_open_offers`, `Register.lot_of` - angle: bugs. Probe: remove `P1` (6 offers by Durand vanish), register `P1` again in lot B2 (Martin): the six offers are listed again with lot B2, owner Martin. Same for a number freed by `change_space_number`. Consequence: until S4, a resident sees offers that nobody made for that lot, and a new owner could not withdraw them (S3 not there either). D-62 covers "skip", not the return. Recommendation: the human records one line (accepted until S4, or the skip also needs the offer to be dropped), and S4 AC1/AC6 must be reachable before any release of S1 alone. Not blocking: the window is closed by S4, the register is manager-only.
- **[M2] S1 files may break S2's load check** - plan "Technical choices", `OfferBook.add` - angle: compliance. D-48 forbids two offers sharing a day, but S1 stores them (probe: offers 9 and 10 on `P2`, same days, both listed). When S2 adds "two offers of the same space sharing a day is unreadable" at load, any file written by S1 with such a pair turns into `OffersUnreadable` and the whole offers feature stops. Recommendation: the planner of S2 asks the human (reject on load, or tolerate pre-existing pairs and only refuse new ones); and S1 should not be released alone.

### Minor
- **[m1] Mutation `--scope diff` is a no-op while the work is uncommitted** - gauntlet run with `--scope critical` instead; rerun `--scope diff` after the commit.
- **[m2] `OfferBook._next_number = 1` mutant survives** - `domain/offers.py:49`. The developer calls it equivalent (overwritten by `restore`); it is, in production, but no test asserts that a fresh `OfferBook().next_number` is 1 (the fake repository starts at 1 itself). Also the INV-007 baseline line in `invariants.md` still says "5 equivalent survivors" after S3; refresh it.
- **[m3] Pair "bad period + blank space/offerer" untested and unstated** - D-59 puts blank at the rank of a bad period; the code answers the period. Add a line to D-59 or a test.
- **[m4] D-62 has a test but no test-case file** - `test_an_offer_whose_space_left_the_register_is_not_listed`; the bridge checks per file, so the harness cannot flag it. Add `s1-*.md` once the decision is in.
- **[m5] Offers path that is a directory or unreadable by permission** - `json_offer_repository.py:_read`. A directory reads as "no offers" on list and raises a raw `IsADirectoryError` on offer; a permission error raises a raw `OSError`, not `OffersUnreadable`. Same code as the register and rules adapters; consistent, not widened.
- **[m6] Process** - the plan's "Deviations" section is empty although the developer wrote the 22 test-cases directly as `covered`, not `pending` first; the note carries it. Fill section 8.
- **[m7] Read normalises** - a hand-edited space (` p2 `) is trimmed on load and rewritten on the next save, as for the rules; mention only.

## Acceptance criteria (stories.md S1)
AC1-AC14 all verified by probe or test; AC7 (no price) holds (no field in request, entry or file); AC14 holds (docstrings of `offer_space` and `_require_owner`, tested). Decisions D-45..D-62 respected: D-45/46 (owner role, name by `key`), D-47/53 (today accepted), D-49, D-52 (open until the end day), D-54 (number in the listing), D-56 (current owner), D-59..D-61 as probed. D-48, D-51, D-55, D-57, D-58 belong to S2-S4 and are not yet enforced (D-48 and D-51 are the open windows of M1/M2).

## Checks not performed
Lint (none). Performance: no target declared. Concurrency: documented limit (ADR-0004, no lock), not tested.

## Positive notes
Role first and before any read is solid; fail-closed reads hold on 31 corrupt shapes; the clock invariant has its own harness check with self-tests.

## Escalation
Sensitive zones are touched (owner role check, offers write path). Verdict GO, status `escalate`: the human decides before merge, with M1 and M2 carried to the next request.
