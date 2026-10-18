---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, A4, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::lines that fit alone but not together are refused
status: covered
---

# Lines that fit alone but not together are refused

- Given: two lines whose sum is the largest amount, and two whose sum is a unit beyond
- When: the cart is priced
- Then: the sum that fits is the subtotal; the other is refused as amount too large
