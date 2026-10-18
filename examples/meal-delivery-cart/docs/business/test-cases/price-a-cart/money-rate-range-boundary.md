---
feature: price-a-cart
type: functional
priority: high
source: PRD A4, A10, D-38
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::taking a rate stops exactly at the end of the range
status: covered
---

# Taking a rate stops exactly at the end of the range

- Given: amounts and rates whose share is next to the largest amount
- When: a rate is taken off an amount
- Then: a share that fits is exact; one unit beyond is refused as amount too large, though the wide product itself did not overflow
