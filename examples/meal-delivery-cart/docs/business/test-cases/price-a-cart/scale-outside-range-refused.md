---
feature: price-a-cart
type: functional
priority: medium
source: ADR-0002; Story 2 criterion 15
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a rate with a scale outside 0 to 18 is refused
status: covered
---

# A rate with a scale outside 0 to 18 is refused

- Given: a rate with a scale of -1 or 19
- When: the rate is built
- Then: the construction is refused; scales 0 and 18 are accepted
