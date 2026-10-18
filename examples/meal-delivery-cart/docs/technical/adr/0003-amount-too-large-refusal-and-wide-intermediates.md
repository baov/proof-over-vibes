# ADR-0003: Amount too large is a typed refusal; the rate product is computed wide

Status: accepted (cheap-to-reverse decision of the architect; completes ADR-0002, does not supersede it).

## Context

ADR-0002 left open what the caller sees on overflow. D-37 to D-39 settle it: no price on an amount beyond the range, a refusal named "amount too large", and every accepted rate scale (0 to 18) must price correctly. Today `subtotal x numerator` overflows a `Long` before the division, and the caller gets a raw `ArithmeticException`.

## Decision

- `Money` stays `Long` minor units. Only the intermediate `minorUnits x numerator` of `Money.times(Percentage)` is computed wider than `Long` (128 bits or `BigInteger`, an implementation choice), then divided half up once; the result is narrowed back to `Long`. Nothing wide is stored or exposed.
- A new public exception `AmountTooLargeException` in `domain.money`, a subclass of `ArithmeticException`. `Money` converts every `Math.*Exact` overflow, and a narrowing that does not fit, into it. It is distinct from `IllegalArgumentException`, which stays the refusal of invalid input (quantity, rate, currency, negative amounts).
- `PriceCart.price(cart, rules, code)` keeps its signature and return type.

## Consequences

Every amount computed along the way (subtotal, discount, fee line, total) goes through `Money` and therefore through the same check. A caller that caught `ArithmeticException` still catches it. Rejected: a result type in place of the exception (breaks the signature of `PriceCart.price`).

Associated invariants: INV-003 (unchanged: `BigInteger` is not floating point), INV-002 (rounding stays in `domain.money`).
