---
feature: price-a-cart
type: functional
priority: high
source: PRD R15, D-13; Story 1 criterion 6
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::every amount is in the currency of the rules
status: covered
---

# Every amount is in the currency of the rules

- Given: rules in yen (no fraction digit) or in euros, with a delivery fee in the same currency
- When: a cart priced in that currency is priced
- Then: subtotal, discount (zero included), fee line and total are all in that currency
