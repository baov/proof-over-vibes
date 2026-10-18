---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, A3, D-38
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::multiplying by a quantity stops exactly at the end of the range
status: covered
---

# Multiplying by a quantity stops exactly at the end of the range

- Given: amounts and quantities whose product is next to either end of the range
- When: an amount is multiplied by a quantity
- Then: a product that fits is exact; one unit beyond either end is refused as amount too large
