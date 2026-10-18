---
role: architect
status: done
structure: decided
reasons: [human chose hexagonal (option b); ADR-0001 accepted; stories pass: refusal order, free slot and preload decided below, refusal form left to the planner]
---

# Architect note: book a slot

Mode of ddd-advisor: guidance (a design question on a feature under way). Domain size: small core, one bounded context; the rules (taken, past, unknown, overlap) are the only part that deserves DDD. No other context to map.

## Question for the human (answered: option b, hexagonal)

What architectural style for the project?

Understood:
- Domain core small but rule-heavy; no UI, storage or accounts yet.
- Next: cancel, practitioner availability, data protection (health-related data).
- Stack fixed: Java 21, Maven, JUnit 5, no other dependency.

1. Which style?
   a) n-tier. Simplest, but the business layer tends to depend on data access; rules get shaped by a storage that does not exist.
   b) Hexagonal (recommended). Pure domain core, ports owned by the core, adapters outside (in-memory now, database or API later). Fits a small core, and keeps storage and E5 data-protection choices out of the rules.
   c) Clean architecture. Same direction as b, with more rings than a three-concept core needs.
   d) Modular monolith. Worth it with several contexts; here there is one.
   e) Other / let me explain.

Dependency rule if b (ADR-0001, status `accepted`): `domain` imports only the JDK; `application` depends on `domain`; `adapters` depend on `application` and `domain`; nothing in `domain` or `application` imports `adapters`.

## Decided by me (cheap to reverse; valid under any of a to d)

- One Maven module, packages `domain`, `application`, `adapters` under a single base package. No dependency beyond JUnit 5.
- The current moment is an input: the booking rule in the domain takes a point in time as a parameter (`Instant`), it never reads the system clock. The use case reads a `Clock` (injected) and passes the instant down. Tests pass fixed instants. This settles requirement 7 ("the current moment is an input of the rule") and makes the boundary case (start equals now) testable.
- Slot and booking identity: opaque identifiers owned by the domain as value objects (practitioner, patient, slot). The domain holds no name, no health data: only ids. This keeps the minimum-collection anti-goal; E5 will decide what adapters may store.
- Consistency: the rules "one active booking per slot" and "no overlap for a patient" are checked and applied as one unit in the use case through the store port; the port must offer an atomic check-and-save. In-memory adapter: a single lock. Alternative of a separate aggregate per slot is not enough, since the overlap rule crosses slots of one patient.
- Value objects: time range (start, end, overlap test with `start < otherEnd && otherStart < end`, so back-to-back does not overlap). Slot and booking as entities; refusal form: see the question for the planner.

## Stories pass (once per feature)

Nothing costly to reverse, no new ADR. Decided, cheap to reverse:

- **D-21, one total order of refusals.** The order (unknown slot, past, taken including own-held, overlap) lives in one place: the booking rule in `domain`, a single sequence of checks that returns the first failure. No other class orders or re-checks refusals; the use case only gathers the facts the rule needs and hands them over. This keeps the order testable as pairs (story 2, criteria 9-10) and unable to drift.
- **"Free slot" is derived, not stored as a flag.** A slot is free when it has no active booking. The domain rule receives the slot (or its absence), the bookings on that slot and the patient's held slots, and decides; the store port answers "slot by id", "active booking of a slot" and "slots held by a patient". Booked state is therefore one fact (the booking), which makes requirement 5 and 12 hold by construction.
- **Preloaded slots reach the domain only through the store port.** The domain and use case never know where slots come from; an unknown id is simply an absent slot. How the store is filled (seed, test fixture, later F4.1) is not designed here. For the tests, the in-memory adapter is built from a list of slots.
- **Atomicity unchanged:** the check and the save of the booking happen as one unit through the port (see above); the refusal order is applied inside that unit.

## Question for the planner (not settled by any document)

How is a refusal returned to the caller: a typed result (a sealed outcome: booked, or refused with a reason among unknown, past, taken, overlapping) or a domain exception? Both are visible to the caller and neither is in the PRD, the stories or ADR-0001. My lean, not a decision: a typed result, since a refusal is an expected business outcome and the order of reasons (D-21) is then a value tests can compare. Planner to settle, and to ask the human if it judges the contract public.

## Technical unknowns of the PRD

- **Simultaneous booking of one slot.** Mechanism is covered above (atomic check-and-save, so at most one succeeds, requirement 5). What the loser sees is the open product question, deliberately not decided in the PRD: I recommend it be treated as an ordinary "taken" refusal, to be confirmed by the human when that edge-case request is created. Nothing to build for it in this feature beyond the atomicity above.
- **Current moment.** Decided above.
- **Blank identifiers.** Not mine to decide (PRD reserves it for a later request); flagged as still open.
- **Sensitive data (E5).** Sensitive zone, not touched by this feature: no persistence, no personal data beyond ids. A later request on storage or exposure must come back to me and the human.

## Debt

None (empty project).

## Next

ADR-0001 is accepted with the dependency rule above. Hand over to `harness-engineer` to turn the rule into an invariant.
