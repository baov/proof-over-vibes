# ADR-0004: Pricing is a pure function over immutable inputs, safe for simultaneous use

Status: accepted (cheap-to-reverse decision of the architect; records the stance taken in the `price-a-cart` architect note "Purity (R3, R5)", which no ADR carried; supersedes nothing).

## Context

PRD R3 and R5 (same input, same result; pricing changes nothing) and requirements C2 to C6 of the edge-codes PRD ask that any number of simultaneous pricings of one cart each give the answer they would give alone. The business asks for the property, not the mechanism (D-41). The property is cheap today and costly the day someone adds a cache, a counter or a lazily built field.

## Decision

- `PriceCart.price` and `domain.pricing.price` stay stateless functions over `Cart`, `PricingRules` and the code; they return a new `Price` and never write to their arguments.
- `domain` and `application` hold no mutable shared state: every field of every class is final (`val`), no `object` or `companion` keeps a `var`, no cache, memo or counter. `Cart` copies the list it is given.
- No locks, no `synchronized`, no `java.util.concurrent`: a pricing never waits for another (C4). INV-004 already bans the concurrency package and the clock.
- Simultaneous use is verified by tests (repeated and parallel calls compared with the solo result) and enforced by structure (INV-007).

## Consequences

A later feature that edits a cart while it is priced, or caches a result, needs a new ADR that supersedes this one (the PRD already says C5 would be read again). Tests alone cannot prove the absence of a race; this ADR and INV-007 are what carry the guarantee.

Associated executable invariants: INV-007 (every field of the core is final), INV-004 (purity of the core: no clock, no `java.util.concurrent`).
