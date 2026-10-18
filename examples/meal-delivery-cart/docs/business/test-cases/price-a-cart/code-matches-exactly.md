---
feature: price-a-cart
type: functional
priority: medium
source: PRD R9; Story 2 criterion 14
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a code matches only the exact configured text
status: covered
---

# A code matches only the exact configured text

- Given: a promotion with the code WELCOME10 and a supplied code that differs by case, by a space or by a character
- When: the cart is priced with that code
- Then: the code is unknown: no discount and the unknown-code reason; only the exact text applies
