---
feature: price-a-cart
type: functional
priority: medium
source: PRD R15; architect note; Story 2 criterion 13 (derived)
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::rules with a promotion minimum in another currency are refused
status: covered
---

# Rules with a promotion minimum in another currency are refused

- Given: rules in euros with a promotion whose minimum is in yen
- When: the rules are built
- Then: the construction is refused with an exception
