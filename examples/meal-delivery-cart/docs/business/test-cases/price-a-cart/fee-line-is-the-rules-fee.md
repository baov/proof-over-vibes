---
feature: price-a-cart
type: functional
priority: high
source: PRD R12, D-10, D-26; Story 1 criteria 4, 12
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the fee line is the delivery fee of the rules, unchanged
status: covered
---

# The fee line is the delivery fee of the rules

- Given: a delivery fee of 250 in the rules (already in the smallest unit), a small or a large cart; also a fee of 0 with a non-empty cart
- When: the cart is priced
- Then: the fee line equals the fee unchanged, whatever the subtotal; a fee of 0 gives a present fee line of zero
