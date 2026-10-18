# ADR-0001: Architectural style

Status: accepted (the human chose option B, hexagonal)

## Context

Empty project, Java 21, Maven, JUnit 5. The first feature, book a slot, is pure domain behavior: slots, bookings, rules on taken, past, unknown and overlapping slots. The next features are cancel (F3.1), practitioner availability (F4.1) and data protection (E5). No UI, no storage, no accounts yet; the booking links a person to a health practitioner, so storage and exposure will come with constraints (GDPR Article 9, unverified).

## Options weighed

- A. n-tier (presentation, business, data). Simple, but the usual rule makes business depend on data access; the domain rules would be shaped by the storage that does not exist yet.
- B. Hexagonal (ports and adapters). A pure domain core, ports defined by the core, adapters (in-memory store, later a database or an API) outside. Fits a small rule-heavy core and keeps storage and data-protection choices out of the rules.
- C. Clean architecture. Same dependency direction as B with extra rings (entities, use cases, interface adapters, frameworks). More ceremony than a core of two or three concepts justifies.
- D. Modular monolith. Pays off with several bounded contexts; here there is one, so the module boundaries would be empty.

## Decision (option B, chosen by the human)

Hexagonal, in one Maven module, packages by role:

- `domain`: slots, bookings, the booking rules. Imports only `java.*`.
- `application`: use cases (book now, cancel and others later) and the ports they need (store of slots and bookings). Depends on `domain`.
- `adapters`: implementations of the ports (in-memory first). Depend on `application` and `domain`.

## Dependency rule

`domain` depends on nothing but the JDK. `application` depends on `domain` only. `adapters` depend on `application` and `domain`. Nothing in `domain` or `application` imports `adapters`. The harness engineer turns this into an architecture invariant.

Associated executable invariants: INV-001 (see `docs/technical/invariants.md`).

## Consequences

- Rules are tested without any infrastructure (JUnit only, no dependency added).
- Data protection (E5) lands in adapters and ports, not in the rules.
- Moving to a modular monolith later, if contexts multiply, is a regrouping of packages, not a rewrite.
