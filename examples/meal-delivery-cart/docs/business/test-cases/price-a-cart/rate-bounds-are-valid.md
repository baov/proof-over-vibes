---
feature: price-a-cart
type: functional
priority: high
source: D-29; Story 2 criterion 8
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::rates of 0 and 100 percent are valid
status: covered
---

# Rates of 0 and 100 percent are valid

- Given: a promotion at 0 percent, or at 100 percent written in several scales
- When: a cart is priced with the code
- Then: 0 percent gives no discount and no reason; 100 percent gives the whole subtotal
