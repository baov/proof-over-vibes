---
feature: price-a-cart
type: functional
priority: high
source: PRD R7, D-8; Story 2 criterion 1
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a valid code takes the rate off the subtotal
status: covered
---

# A valid code takes the rate off the subtotal

- Given: a subtotal of 2000, rules with the promotion code WELCOME10 at 10 percent (minimum 1000) and a fee of 250
- When: the cart is priced with the code WELCOME10
- Then: the discount is 200, no reason is given, and the total is 2050 (2000 - 200 + 250)
