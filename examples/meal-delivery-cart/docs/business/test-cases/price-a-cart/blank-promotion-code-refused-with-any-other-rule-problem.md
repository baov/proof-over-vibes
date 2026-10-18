---
feature: price-a-cart
type: functional
priority: high
source: PRD C8, D-28, D-36, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank promotion code is refused whatever other rule problem there is
status: covered
---

# A blank promotion code is refused with any other rule problem

- Given: a blank promotion code together with a rate out of range, a negative minimum, a minimum in another currency or a fee in another currency
- When: the rules are built
- Then: the build is refused, whichever problem is found first; the same promotion with a valid code is accepted
