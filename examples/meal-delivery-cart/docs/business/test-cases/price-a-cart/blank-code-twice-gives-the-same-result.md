---
feature: price-a-cart
type: functional
priority: high
source: PRD C6, C7
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank code priced twice gives the same result and changes nothing
status: covered
---

# A blank code priced twice gives the same result

- Given: a cart and rules, priced with an empty code
- When: the same cart is priced twice with an empty code, then with a blank code and with no code
- Then: all prices are equal and the cart and the rules are unchanged
