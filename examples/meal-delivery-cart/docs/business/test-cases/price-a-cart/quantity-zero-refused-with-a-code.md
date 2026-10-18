---
feature: price-a-cart
type: functional
priority: high
source: PRD R18, R9; Story 2 criterion 11
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a line of quantity zero is refused even with a code
status: covered
---

# A line of quantity zero is refused even with a code

- Given: a cart holding a line of quantity zero and a valid code
- When: the cart is priced with the code
- Then: the call is refused: no price and no discount are returned
