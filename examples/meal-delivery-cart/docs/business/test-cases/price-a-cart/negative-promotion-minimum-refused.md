---
feature: price-a-cart
type: functional
priority: high
source: PRD A6, A8, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::rules with a negative promotion minimum are refused, a minimum of zero is valid
status: covered
---

# Rules with a negative promotion minimum are refused, a minimum of zero is valid

- Given: rules with a promotion whose minimum is -1 or the lowest amount, and rules with a minimum of 0
- When: the rules are built and carts are priced with the code
- Then: a negative minimum gives an invalid-input error (IllegalArgumentException); a minimum of 0 is accepted and the code applies on any subtotal, also on 0
