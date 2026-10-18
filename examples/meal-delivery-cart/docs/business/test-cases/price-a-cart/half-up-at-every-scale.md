---
feature: price-a-cart
type: functional
priority: high
source: PRD A11, D-39
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a discount is rounded half up at every scale
status: covered
---

# A discount is rounded half up at every scale

- Given: a rate of 5 at each scale from 1 to 18 and a subtotal of exactly half a unit, or just under
- When: the cart is priced with the code
- Then: exactly half a unit rounds up to 1; just under half gives 0
