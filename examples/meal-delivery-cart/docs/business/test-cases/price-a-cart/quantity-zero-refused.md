---
feature: price-a-cart
type: functional
priority: high
source: PRD R18, D-24; Story 1 criterion 10
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::a line of quantity zero is refused
status: covered
---

# A line of quantity zero is refused

- Given: a line with a unit price and a quantity of zero
- When: the line is built
- Then: it is refused as invalid input (IllegalArgumentException); no cart can hold it, so no price is returned
