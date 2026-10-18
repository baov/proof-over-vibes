---
feature: price-a-cart
type: functional
priority: high
source: PRD R12, R13, D-10; Story 2 criterion 10
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::the fee line is the same with and without a promotion
status: covered
---

# The fee line is the same with and without a promotion

- Given: the same cart and rules, a promotion at 100 percent, priced with and without the code
- When: both are priced
- Then: the fee line is identical and the total with the code is the fee, never below it
