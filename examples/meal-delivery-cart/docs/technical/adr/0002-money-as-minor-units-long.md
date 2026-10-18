# ADR-0002: Money as minor units in a Long

Status: accepted (chosen by the human).

## Context

`Money` is the public type on every line, rule and result; changing it later breaks callers. The PRD requires exact amounts in the smallest unit (R14, R15) and totals that never come from unrounded values (R16).

## Decision

`Money(minorUnits: Long, currency: java.util.Currency)`: an immutable value object. The percentage rate is an exact decimal (`Percentage`, integer numerator over a power of ten), never `Double`, so half-up rounding is pure integer arithmetic. Overflow is detected with exact arithmetic (`Math.multiplyExact`, `addExact`); what the caller sees on overflow or on a negative amount stays reserved (PRD section 6).

## Consequences

Range limited to `Long`, ample for a cart. The currency travels with every amount. Rejected: `BigDecimal` amount (invites unrounded values), raw `Long` (loses the currency guard).

Associated executable invariants: INV-003 (no Double, Float or BigDecimal), INV-002 (rounding in `domain.money` only).
