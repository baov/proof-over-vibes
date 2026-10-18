---
feature: price-a-cart
type: functional
priority: high
source: PRD R10; Story 2 criterion 9
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::the discount never exceeds the subtotal
status: covered
---

# The discount never exceeds the subtotal

- Given: a rate of 100 percent, or of 99.9 percent, with odd and even subtotals
- When: the cart is priced with the code
- Then: at 100 percent the discount is the whole subtotal and the total is the fee; at 99.9 percent the discount is rounded half up and stays below the subtotal
