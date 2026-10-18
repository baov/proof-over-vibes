---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, A3, D-38
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::subtracting stops exactly at the end of the range
status: covered
---

# Subtracting amounts stops exactly at the end of the range

- Given: amounts next to the largest and the smallest amount a Money holds
- When: one amount is subtracted from another
- Then: a difference that fits is exact; one unit beyond either end is refused as amount too large
