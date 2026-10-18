---
feature: price-a-cart
type: functional
priority: high
source: PRD R9; Story 2 criterion 3
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a subtotal equal to the minimum still gets the promotion
status: covered
---

# A subtotal equal to the minimum still gets the promotion

- Given: a valid code and a minimum of 1000; subtotals of 1000 and 1001
- When: the cart is priced with the code
- Then: the promotion applies at both: 100 off, no reason
