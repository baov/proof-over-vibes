---
feature: price-a-cart
type: functional
priority: medium
source: PRD R9, R17, D-25, D-23; Story 2 criterion 7
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::an empty cart with a code is a subtotal of zero
status: covered
---

# An empty cart with a code is a subtotal of zero

- Given: an empty cart and a code, with a positive minimum, with an unknown code, or with a minimum of zero
- When: the cart is priced with the code
- Then: every amount is zero and there is no fee line; the reason is subtotal below minimum, or unknown code, or none when the minimum is zero
