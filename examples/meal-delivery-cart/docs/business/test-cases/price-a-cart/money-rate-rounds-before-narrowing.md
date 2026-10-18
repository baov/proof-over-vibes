---
feature: price-a-cart
type: functional
priority: high
source: PRD A10, D-38
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::a rate rounds half up before the result is checked against the range
status: covered
---

# A rate rounds half up before the result is checked against the range

- Given: a share exactly half a unit below the largest amount, and one exactly half above
- When: a rate is taken off an amount
- Then: the first rounds up to the largest amount and fits; the second rounds beyond it and is refused as amount too large
