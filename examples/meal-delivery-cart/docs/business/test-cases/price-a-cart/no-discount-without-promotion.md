---
feature: price-a-cart
type: functional
priority: high
source: PRD R11; Story 1 criterion 3; Story 2 criterion 12
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the discount is zero
status: covered
---

# Without a promotion the discount is zero

- Given: any cart and rules; no code is supplied
- When: the cart is priced
- Then: the discount is zero, in the currency of the rules
