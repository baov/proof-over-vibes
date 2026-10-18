---
feature: price-a-cart
type: functional
priority: high
source: D-22, D-28, D-36; Story 2 criteria 8, 15
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::rules with a rate below 0 or above 100 percent are refused
status: covered
---

# Rules with a rate below 0 or above 100 percent are refused

- Given: a promotion whose rate is below 0 or above 100 percent (101/100, 1001/1000, 2/1, -1/100)
- When: the rules are built
- Then: the construction is refused with an exception, so no cart is ever priced with those rules
