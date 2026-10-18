---
feature: price-a-cart
type: functional
priority: high
source: PRD A6, A8, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::rules with a negative delivery fee are refused, a free delivery is valid
status: covered
---

# Rules with a negative delivery fee are refused, a free delivery is valid

- Given: rules with a fee of -1 or the lowest amount, and rules with a fee of 0
- When: the rules are built and a cart is priced with the free delivery
- Then: a negative fee gives an invalid-input error (IllegalArgumentException); a fee of 0 is accepted and gives a fee line of 0
