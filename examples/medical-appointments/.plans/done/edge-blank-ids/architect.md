---
role: architect
status: done
structure: decided
reasons: [no ADR, dependency or external contract touched; cheap choices decided below; no escalation]
---

# Architect note: blank, empty or absent identifiers

The hexagonal structure (ADR-0001, INV-001) holds as it is: no new package, no ADR, no debt. Only cheap-to-reverse choices remain.

## Is this "breaking a public contract"?

No, and none is escalated. The role file lists API, data format, migration. Today the module has no API, no serialization, no persistence and no caller outside its own tests (the sensitive zones are still untouched). So:

- **Adding a constant to `RefusalReason`** (the public result type's reason set) is additive: no existing outcome changes meaning. Not breaking.
- **Changing the shape of `BookingOutcome` or of `PatientId` / `SlotId`** (new variant, `Optional`, constructor that throws, another type) would change what every caller compiles against and handles. That would count as breaking, and I would escalate it. I am not proposing it: the types stay as they are.

## How an absent value reaches the service (the PRD's unknown)

Two shapes of "absent" exist and both must be refused, never thrown:

- the identifier reference itself is `null` (`book(null, slot)`), and
- the identifier exists but wraps `null` (`new PatientId(null)`); empty and blank values are ordinary strings.

The record constructors stay open: validating there would throw instead of returning a refusal, and would make "refused, nothing changes" (req. 7) untestable through the service.

## Decided (cheap to reverse)

- **One check, one place (D-21).** "Missing identifier" is decided in `domain`: a predicate on the pair of identifiers, treating a null reference, a null value, an empty value and a value of Unicode white space only as missing. `BookingRule` runs it as the first step of its single sequence of checks (missing, unknown slot, past, taken, overlap). Both identifiers missing gives one refusal (req. 6).
- **The use case must not reach the store with a missing identifier.** `findSlot(null)` or `slotsHeldBy(null)` can throw on a map-backed store, and the booking would never be refused. When the identifiers are missing, `BookSlot` gathers no facts (it hands the rule absent ones) so the rule's first check answers. The use case does not re-implement the check or the order; it only asks the same domain predicate whether to skip fact gathering, or the rule is given the raw identifiers and the facts lazily. Planner chooses between these two shapes.
- **Nothing is saved on refusal**, which also closes the carried-over minor (a `null` patient stored makes later bookings throw): such a booking can no longer exist.
- **"Blank" means Unicode White_Space (PRD req. 3).** `String.isBlank` / `Character.isWhitespace` do not cover non-breaking spaces (U+00A0, U+2007, U+202F), which Unicode classes as white space. The planner must pick an implementation that does (for example `\p{IsWhite_Space}`) and cover one such character in a test. Surrounding white space in a non-blank identifier is not touched (out of scope).
- **Name of the reason:** `MISSING_IDENTIFIER`, one constant for both identifiers (D-26 style: upper snake, says what is wrong, not who). Planner may rename; the PRD leaves it to the plan.
- **Layers:** no new dependency; INV-001 unaffected. INV-002 needs test-cases for the new behaviors; INV-003 covers the new rule code.

## Debt

None.
