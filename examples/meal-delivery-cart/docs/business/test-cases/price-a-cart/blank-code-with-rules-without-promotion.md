---
feature: price-a-cart
type: functional
priority: high
source: PRD C7, D-34, D-40, D-46
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank code with rules that have no promotion is no code
status: covered
---

# A blank code with rules that have no promotion is no code

- Given: rules with no promotion at all
- When: the cart is priced with an empty or blank code
- Then: no discount and no reason (not unknown code); a non-blank code on the same rules is still an unknown code
