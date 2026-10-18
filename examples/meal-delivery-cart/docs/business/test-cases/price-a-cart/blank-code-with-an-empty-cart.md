---
feature: price-a-cart
type: functional
priority: high
source: PRD C7, D-40
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank code with an empty cart is no code
status: covered
---

# A blank code with an empty cart is no code

- Given: an empty cart and rules with a promotion
- When: the cart is priced with an empty code
- Then: every amount is zero, no fee line and no reason; a real code on the same cart still gives subtotal below minimum
