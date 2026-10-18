---
feature: price-a-cart
type: functional
priority: high
source: PRD A7, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a line of negative quantity is refused
status: covered
---

# A line of negative quantity is refused

- Given: a line with a quantity of -1 or the lowest integer, and one with quantity 1
- When: the line is built
- Then: a negative quantity gives an invalid-input error (IllegalArgumentException); quantity 1 is accepted; quantity zero is still refused
