---
feature: price-a-cart
type: functional
priority: high
source: D-44
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::taking a rate of or from a negative amount is refused, zero is accepted
status: covered
---

# Taking a rate of or from a negative amount is refused, zero is accepted

- Given: a negative amount, or a rate with a negative numerator, and zero in either place
- When: a rate is taken off an amount
- Then: a negative amount or numerator gives an invalid-input error (IllegalArgumentException); zero in either place gives 0
