---
feature: price-a-cart
type: functional
priority: high
source: PRD A11, A12, D-39
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::ten percent prices the same at every scale
status: covered
---

# Ten percent prices the same at every scale

- Given: 10 percent written at each scale from 1 to 18, and subtotals of 100, 100000, 100000000 and 9000000000000000000
- When: the cart is priced with the code
- Then: the whole price equals the one at 10 percent written 10 over 100; rates 0 and 100 percent at scale 0 give no discount and the whole subtotal
