---
feature: price-a-cart
type: functional
priority: high
source: PRD R8, R14, D-11; Story 2 criterion 2
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::the discount is rounded once, half up, to the smallest unit
status: covered
---

# The discount is rounded once, half up, to the smallest unit

- Given: a promotion rate and a subtotal whose product has a fraction (5 percent of 1009, 1010, 1011; 12.5 percent of 1001; yen; three lines of 333 at 10 percent)
- When: the cart is priced with the code
- Then: below one half rounds down, exactly one half and above rounds up, the smallest unit is that of the currency, and the rounding happens once on the subtotal times the rate (99.9 gives 100, not 3 x 33.3 rounded)
