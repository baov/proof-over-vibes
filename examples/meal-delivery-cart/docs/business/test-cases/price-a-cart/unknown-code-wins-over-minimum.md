---
feature: price-a-cart
type: functional
priority: high
source: PRD R9, D-23; Story 2 criterion 6
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::an unknown code is the only reason when the subtotal is also below the minimum
status: covered
---

# An unknown code is the only reason when the subtotal is also below the minimum

- Given: an unknown code and a subtotal of 999 against a minimum of 1000
- When: the cart is priced with the code
- Then: the only reason is the unknown code; the discount is zero
