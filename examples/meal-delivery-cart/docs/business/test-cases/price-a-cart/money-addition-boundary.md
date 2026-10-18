---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, A3, D-38
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::adding stops exactly at the end of the range
status: covered
---

# Adding amounts stops exactly at the end of the range

- Given: amounts next to the largest and the smallest amount a Money holds
- When: two amounts are added
- Then: a sum that fits is exact; one unit beyond is refused as amount too large; amounts in two currencies are still refused as invalid input
