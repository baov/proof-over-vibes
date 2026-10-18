---
feature: price-a-cart
type: functional
priority: high
source: PRD C7, D-40, D-45
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank code is no code
status: covered
---

# A blank code is no code

- Given: a cart above the minimum and a cart below it, rules with a promotion, and a code that is empty or only blank (spaces, tab, line breaks, no-break space, ideographic space)
- When: the cart is priced with that code
- Then: the whole price equals the price with no code: no discount, no reason (not even subtotal below minimum), the fee line kept
