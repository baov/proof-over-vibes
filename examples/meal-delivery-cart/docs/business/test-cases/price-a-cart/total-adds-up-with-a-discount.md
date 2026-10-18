---
feature: price-a-cart
type: functional
priority: medium
source: PRD R13, R16; Story 2 criteria 2, 10
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::the total is subtotal minus the rounded discount plus the fee
status: covered
---

# The total is subtotal minus the rounded discount plus the fee

- Given: lines 350 x 2 and 1450 x 1, a 10 percent promotion, a fee of 250
- When: the cart is priced with the code
- Then: the subtotal is 2150, the discount 215, the fee line 250 and the total 2185
