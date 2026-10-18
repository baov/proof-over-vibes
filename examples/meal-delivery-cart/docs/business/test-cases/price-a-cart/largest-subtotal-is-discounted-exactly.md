---
feature: price-a-cart
type: functional
priority: high
source: PRD A12, D-39
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::the largest subtotal is discounted exactly at any rate
status: covered
---

# The largest subtotal is discounted exactly at any rate

- Given: a subtotal at the largest amount and rates of 10, 50, 100 and almost 100 percent at several scales
- When: the cart is priced with the code
- Then: the discount is the exact share rounded half up once, and the total is the subtotal minus the discount, at every scale from 1 to 18
