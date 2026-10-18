# ADR-0001: Hexagonal architecture, light

Status: accepted (chosen by the human).

## Context

The project is empty. The first feature is a pure, money-heavy pricing core; the roadmap adds fee lines, tax, tip, promotion variants, then order handoff, the first contact with the outside.

## Decision

Hexagonal, light. Ports are created only when a real outside appears (order handoff), not before. Packages: `domain` (cart, money, rules, pricing, result) and `application` (the pricing entry point).

## Dependency rule

- `domain` imports only the Kotlin and JDK standard library: no adapter, no framework, no `application`.
- `application` depends on `domain` only.
- Any future adapter depends inward on `application` or `domain`, never the reverse.
- Rounding happens in one function of `domain.money`; no other code rounds.

## Consequences

Pure core, testable with no infrastructure. A modular split is revisited when a second capability exists (order handoff). Rejected: modular monolith (empty modules today), clean architecture (extra rings for one function), n-tier (invites an anemic service layer).

Associated executable invariants: INV-001 (dependency rule), INV-002 (single rounding point), INV-004 (purity of the core).
