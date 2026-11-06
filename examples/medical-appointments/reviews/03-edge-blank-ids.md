---
role: reviewer
status: done
verdict: GO
reasons: [gauntlet green, no blocking finding, no major finding, behavior matches PRD req 1-7 and D-30, D-33 to D-37, no sensitive zone touched]
severity: minor
open_majors: []
---

# Pre-merge review, claude-bank-account-poc-1435f8 (medical-appointments, edge-blank-ids), iteration n=1

**Verdict: GO**
**Date**: 2026-10-18 · **Base**: 0d2c042..HEAD (8eda0b6) · **Scope**: 11 files, +283/-7 lines, 4 commits, folder examples/medical-appointments only
**Criticality**: critical. Signals: domain layer (`BookingRule`, `RefusalReason`), test-cases `priority: high`, a change of an internal public signature (`BookingRule.decide`) and of the public reason set.

Skill announced: `premerge-review`.

## Summary

A missing patient or slot identifier (null reference, null value, empty, Unicode White_Space only) is refused first with `MISSING_IDENTIFIER`, nothing is stored, and the refusal order is now missing, unknown, past, taken, overlap. I tried to break it in a scratch copy outside the repository (results below) and found no deviation from the PRD or the decisions. Only minor findings. No sensitive zone is touched (no `adapters` change, nothing stored or exposed).

## Gauntlet

| Check | Result |
|---|---|
| Test suite | OK (28 tests: BookSlotTest 25, concurrency 2, TimeRange 1) |
| Lint / format | not available (no linter configured, D-18) |
| Harness invariants | INV-001 exit 0; INV-002: 28 test-cases, 28 covered_ok, 0 broken, 0 orphan |
| Test-case bridge | OK (part of INV-002) |
| Mutation (critical) | INV-003: 100.0% (29 killed / 29 generated), no threshold set (warn, human decision) |
| Test-cases touched | 6 new and 1 reworded, all read |

## Attempts to break it (scratch copy, outside the repository, nothing kept)

- Single code points as patient: U+0085, U+00A0, U+2028, U+2029, U+3000, U+2007, U+202F, U+1680, U+2000-200A, U+205F, U+000B/C all `MISSING_IDENTIFIER`. U+200B, U+200C, U+2060, U+FEFF, U+180E, U+001C-001F are not blank (reach the other rules: `UNKNOWN_SLOT` with an unknown slot), as D-37 says.
- `book(null,null)`, `PatientId(null)`/`SlotId(null)`, `book(a, null)`: refused, never thrown.
- Mixed blank and valid: `" ​ "` is not blank and is booked, stored as given (D-37, no trimming); `"  　"` is blank.
- 20 million white-space characters (patient and slot): refused, no stack overflow. 20 million spaces plus `x`: ordinary identifier (`UNKNOWN_SLOT`).
- Blank patient on a slot taken by B: `MISSING_IDENTIFIER` (not `TAKEN`); a valid patient on the same slot still gets `TAKEN`; the booking of B is intact. Blank on the unknown, past, overlapping sides is pinned by the existing order test, which I read.
- The PRD text and D-33 to D-37 agree with the behavior, exactly. PRD req 3 and D-33 are the same rule; D-37 only makes explicit what req 3 implies; D-36 names what req 4 left to the plan.

## Findings

### Blocking
None.
### Major
None.
### Minor
- **[m1] The brief is stale on the decisions range** — `.plans/in-progress/edge-blank-ids/brief.md` · angle: compliance. It cites D-1 to D-35 while D-36 and D-37 now exist and are applied. Cosmetic; update at closing.
- **[m2] `isMissing` is evaluated twice** — `BookSlot.java:29` and `BookingRule.java:26` · angle: debt. The use case asks to skip the store, then the rule asks again. Harmless and documented in the plan (the rule alone decides the refusal); a lazy-facts shape would remove it if it ever grows.
- **[m3] A slot created with a blank identifier can never be booked** — `Slot` constructor (not in the diff) · angle: bugs. A `Slot` whose id is blank is accepted at creation but every request for it is `MISSING_IDENTIFIER`. Not reachable today (no slot creation path for a caller); out of the PRD scope. Worth a question when slot creation is specified.
- **[m4] U+200B-only patient is booked** — behavior of D-37 · angle: compliance. An identifier made only of invisible characters is stored as a real patient. This is settled (D-37, "a person may revisit", answered-by-delegate, never read by a human) so it is not an open major; I list it so the human who reads it can revisit.

## Checks not performed

No linter. Sensitive zones: checked against `docs/technical/invariants.md`, the diff does not touch storage or exposure, so no escalation. Simultaneous booking is another request.

## Positive notes

- The order stays decided in one place (`BookingRule`, D-21); the use case never produces a refusal itself.
- The white-space class is Unicode White_Space with tests pinning both directions (U+00A0 blank, U+200B/U+001F not), where `String.isBlank` would fail.
- A store decorator that throws on a missing identifier proves no lookup is made; the carried-over minor (null patient stored) is closed.
