---
role: planner
status: done
reasons: []
---

# Plan: refuse a booking whose patient or slot identifier is missing

Skill announced: `plan-driven-dev` (context and plan steps only). Everything a caller can observe is settled by a document except the public name of the new reason.

## Answers applied

- D-36 (answered-by-delegate): the public name of the new reason is `MISSING_IDENTIFIER`.
- D-37 (answered-by-delegate): zero-width and invisible characters are not blank; only Unicode White_Space counts.

No question remains.

## Decisions applied

- D-30 (human): one new common reason for patient and slot, distinct from the four others.
- D-33 (delegate) and PRD req 1-3: absent, empty, or only Unicode white space is missing. "Absent" covers both a `null` reference (`book(null, slot)`) and a `null` value (`new PatientId(null)`): both are refused, never thrown (architect). Both are the same observable result.
- D-34 (delegate) and PRD req 5: the check is first: missing identifier, unknown slot, past, taken, overlap (extends D-21). So a request with a missing identifier gets the new reason even when the slot is unknown, past, taken, or overlapping.
- PRD req 6: both identifiers missing gives one refusal, the same reason.
- PRD req 7 (and req 12 of `book-a-slot.md`): the refusal changes nothing. It also closes the carried-over minor: a booking for a `null` patient can no longer be stored.
- D-21: the order is decided in one place, `BookingRule`.
- ADR-0001 / architect: no new package, no ADR; `BookingOutcome`, `PatientId`, `SlotId` keep their shape (a constant is added to `RefusalReason`, additive).

### Caller-visible list (twice / nothing / invalid / edge / order)

| Behavior | Decided by | Result |
|---|---|---|
| Same missing request twice | PRD req 7 | the same `Refused(MISSING_IDENTIFIER)` both times, nothing stored |
| Nothing (`null` reference, `null` value) | PRD req 1-2, architect | refused with the new reason |
| Empty `""`, white space only | PRD req 1-3 | refused with the new reason |
| Invalid, not blank (e.g. `"  p1 "`, `"p1"` unknown) | PRD scope "out" | not touched: passes on to the other rules (`"  slot-1 "` is `UNKNOWN_SLOT`; surrounding white space is not trimmed) |
| Edge of the white space class | PRD req 3 (Unicode White_Space) | see below |
| Both missing | PRD req 6 | one refusal, the new reason |
| Order against the other rules | D-34, PRD req 5 | missing first, in every combination |
| Effect on the store | PRD req 7 | none |
| Patient missing but slot also unknown / past / taken | D-34 | the new reason (never `UNKNOWN_SLOT`, `PAST`, `TAKEN`) |

White space class, by the letter of PRD req 3 ("no character other than Unicode white space"): the Unicode `White_Space` property: U+0009-000D, U+0020, U+0085, U+00A0, U+1680, U+2000-200A, U+2028, U+2029, U+202F, U+205F, U+3000. Consequences: non-breaking spaces (U+00A0, U+2007, U+202F) are blank, although `String.isBlank` and `Character.isWhitespace` miss some of them. Zero-width characters (U+200B, U+FEFF, U+180E) and the control characters U+001C-001F are NOT Unicode white space, so an identifier made of them is not blank (and is then treated as an ordinary identifier: a slot made of them is `UNKNOWN_SLOT`). This follows the PRD's wording, not a new rule; it is flagged in the report so the human can object.

## 1. Metadata
- **Type**: feature (edge case of `book-a-slot`)
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

A booking request whose patient identifier or slot identifier is absent, empty or only Unicode white space is refused first, with one reason for both, and changes nothing.

## 3. Context

- Code: `domain` (`BookingRule.decide(patient, Optional<Slot>, now, Optional<Booking>, List<Slot>)`, `RefusalReason`, `PatientId(String)`, `SlotId(String)` records with open constructors), `application` (`BookSlot.book` gathers `findSlot`, `activeBookingOf`, `slotsHeldBy` inside `atomically`, then `decide`, then saves on `Booked`), `adapters` (`InMemoryBookingStore`). Tests: `BookSlotTest` (helpers `slotAt`, `slot`, `snapshot`, fixed `CLOCK`, constants `A`, `B`, `S`...), `BookSlotConcurrencyTest`, `TimeRangeTest`, `ArchitectureTest`.
- Today `book(null, s)` stores a booking with a `null` patient; `book(a, null)` reads the store with a `null` slot id.
- Invariants: INV-001 (`domain` imports only `java.*`: `java.util.regex` is allowed; the rule and the predicate stay in `domain`); INV-002 (each new test-case points at an existing test, each test has a test-case; front-matter `feature`, `type`, `priority`, `source`, `automated_test`, `status`); INV-003 (PIT on `domain` and `application`, warn, no threshold, no baseline: human decision). Sensitive zones: nothing new is stored or exposed; a refusal stores nothing.
- Harness: `bash tools/harness/run_all.sh`, then `bash tools/harness/run_mutation.sh --scope diff`. Maven offline `-o` via `tools/harness/_maven.sh`.
- No `.plans/FEEDBACK.md`; no earlier lesson to apply. Carried over: no major. Minor 1 (null patient stored) closed by this feature. Minor 2 (no mutation baseline): stays a human decision, out of this plan.

## 4. Expected behaviors

Test boundary: the use case `BookSlot` on an `InMemoryBookingStore` with a fixed `Clock`, in `BookSlotTest` (same style as the story 2 tests). Effects are read through the store port. "Missing" examples, used by tests 1 and 2: `null` reference, a `null` value, `""`, `" "`, `"\t\n"`, `" "`, `" "`, `" "`, `"　"`, `"\u0085"`, `"   "` (mixed).

1. **Patient missing (criterion 1, PRD req 1, 3).** Given a store with a free future slot, when each missing patient example books it, then `Refused(MISSING_IDENTIFIER)` and the slot has no booking. Booking the same twice gives the same outcome. Method `refusesAPatientIdentifierThatIsAbsentEmptyOrBlank`.
2. **Slot missing (criterion 2, PRD req 2, 3).** Same list for the slot identifier, with a valid patient; the patient holds nothing afterwards. Method `refusesASlotIdentifierThatIsAbsentEmptyOrBlank`.
3. **Only white space makes an identifier blank (criterion 3, PRD req 3, edge).** Not missing, hence going on to the other rules: a patient `"​"`, `"﻿"`, `"\u001F"` books the free slot (`Booked`); `"  patient-x "` (surrounding white space) also books, stored as given; a slot `"​"` or `" slot-1 "` gives `UNKNOWN_SLOT`. Method `onlyWhiteSpaceMakesAnIdentifierBlank`.
4. **Both missing (criterion 4, PRD req 6).** `book(null, null)`, `book(new PatientId(null), new SlotId(null))`, `book(new PatientId(" "), new SlotId(""))` each give one `Refused(MISSING_IDENTIFIER)`. Method `reportsOneRefusalWhenBothIdentifiersAreMissing`.
5. **First in the order (criterion 5, PRD req 5, D-34).** A missing patient gets `MISSING_IDENTIFIER` when the slot is: unknown (absent id), past, held by B (taken); and a missing slot identifier gets it when the patient holds slots (that would also overlap) and the clock is after everything. Each assertion also checks that nothing changed. Method `reportsAMissingIdentifierBeforeAnyOtherRefusal`.
6. **A refusal changes nothing (criterion 6, PRD req 7, minor closed).** With several bookings held, after refusals with a `null` patient, a blank patient and a blank slot, a snapshot of all slots is identical before and after; then a valid booking by A of a free slot, and one by B, still succeed (no `null` patient was stored). Method `aMissingIdentifierRefusalChangesNothing`.

Order of calls: tests 5 and 6 interleave valid and missing requests in both orders; the outcomes do not depend on what came before.

## 5. Steps

Test first for each behavior, then the minimum code.

- [ ] Step 1: write test 1 (`refusesAPatientIdentifierThatIsAbsentEmptyOrBlank`), red; add `MISSING_IDENTIFIER` to `RefusalReason` (D-36); add the predicate (see technical choices) and the first check in `BookingRule`; `BookSlot` passes the identifiers and skips fact gathering when the predicate says so. Green.
- [ ] Step 2: test 2 (slot), then test 3 (what is not blank), then test 4 (both): one at a time, red then green; the predicate is the only code that grows.
- [ ] Step 3: test 5 (order) and test 6 (nothing changes, later bookings fine); they should pass at once with the first check at the top of `decide`; if one passes without having been red, break the order on purpose to see it fail, then restore.
- [ ] Step 4: write the test-cases below. Reword `refusal-order-unknown-first.md` ("... before any other reason, once the identifiers are present"): its test does not change.
- [ ] Step 5: `bash tools/harness/run_all.sh` (INV-001, INV-002 green), then `bash tools/harness/run_mutation.sh --scope diff`. For each surviving mutant in `domain` or `application`, add a test of the missing behavior or justify an exclusion in `pom.xml`. Likely survivors: the null-reference branch versus the null-value branch, the empty case (`""`), one white space class boundary, the skip of fact gathering in `BookSlot`. Do not record a threshold or a baseline.

### Business test-cases (docs/business/test-cases/book-a-slot/)

Common: `feature: book-a-slot`, `type: functional`, `status: covered`, `automated_test: src/test/java/io/example/medical/BookSlotTest.java::<method>`; body given / when / then in business words, no class names.

| File | priority | automated_test method | source |
|---|---|---|---|
| `refuse-missing-patient-identifier.md` | high | `refusesAPatientIdentifierThatIsAbsentEmptyOrBlank` | PRD edge-blank-ids req 1, 3, 4; D-30, D-33 |
| `refuse-missing-slot-identifier.md` | high | `refusesASlotIdentifierThatIsAbsentEmptyOrBlank` | PRD req 2, 3, 4; D-30, D-33 |
| `only-white-space-makes-an-identifier-blank.md` | medium | `onlyWhiteSpaceMakesAnIdentifierBlank` | PRD req 3; D-33 |
| `refuse-both-identifiers-missing.md` | medium | `reportsOneRefusalWhenBothIdentifiersAreMissing` | PRD req 6 |
| `refusal-order-missing-identifier-first.md` | high | `reportsAMissingIdentifierBeforeAnyOtherRefusal` | PRD req 5; D-34 (extends D-21) |
| `missing-identifier-refusal-changes-nothing.md` | high | `aMissingIdentifierRefusalChangesNothing` | PRD req 7; req 12 of `book-a-slot.md` |

Bodies state the examples in words (empty, spaces only, a non-breaking space, a tab; and "a zero-width character is not white space"), not the code points.

## 6. Risks & edge cases

- **White space class.** `String.isBlank` and `Character.isWhitespace` are wrong in both directions (miss U+00A0, U+2007, U+202F; accept U+001C-001F). The test examples above pin both directions; a developer swapping in `isBlank` fails tests 1 and 3.
- **Zero-width characters read as non-blank** (PRD wording). If the human wants them refused too, that is a new PRD requirement, not a change here.
- **Surrounding white space** is not trimmed and not normalized (out of scope): `"p1"` and `" p1"` are two patients.
- **Skipping the store** when an identifier is missing: otherwise a `null` slot id reaches `findSlot`; the tests with `null` would crash on a store that rejects `null` keys. The tests use the real in-memory store, which tolerates `null` keys, so a test-only store that throws on `null` is added to test 2 to prove that no fact is gathered (decorator local to the test file, like the one in the concurrency test).
- The atomic unit stays: the check happens inside it, so nothing outside can observe a half state; simultaneity is another request.
- Mutation: see Step 5.

## 7. Out of scope

Identifiers that are well-formed but unknown (`UNKNOWN_SLOT`); surrounding white space; identifier format or length; accounts and authentication; how a caller is shown the refusal; simultaneous booking; mutation threshold and baseline (human decisions).

## 8. Deviations

(none)

## 9. Self-review

(filled at closing)

## 10. Follow-up actions

(filled at closing)

## Technical choices (no caller can observe them; for the reviewer to challenge)

- The predicate lives in `domain` as a static method on `BookingRule` (`isMissing(PatientId, SlotId)`), built on `Pattern.compile("\\p{IsWhite_Space}*")` with `matches()` on the value, after the checks for a `null` reference and a `null` value. `domain` stays on `java.*` (INV-001).
- The order stays in one method: `decide` takes the two identifiers as first parameters and its first line is the missing check, then the existing four. `BookSlot` calls `BookingRule.isMissing` only to decide whether to read the store; when true it hands `decide` empty facts (`Optional.empty()`, the instant, `Optional.empty()`, `List.of()`) and the rule's first check answers. The use case never produces a refusal itself. Rejected: giving `decide` lazy facts (a supplier), heavier for no gain.
- `MISSING_IDENTIFIER` is added at the end of `RefusalReason` (no code depends on the order of constants).
- `PatientId` and `SlotId` constructors stay open (they must be able to carry a `null`/blank value for the service to refuse it).
- Test-only store that throws on a `null` key, local to `BookSlotTest`; no mocking framework.
