---
feature: price-a-cart
type: functional
priority: high
source: PRD A6, A7, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a line of negative unit price is refused, a free line is valid
status: covered
---

# A line of negative unit price is refused, a free line is valid

- Given: a line with a unit price of -1 or the lowest amount, and a line with unit price 0
- When: the line is built and the free line is priced
- Then: a negative unit price gives an invalid-input error (IllegalArgumentException); a free line is accepted and the cart still has its fee line
