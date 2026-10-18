---
feature: price-a-cart
type: functional
priority: medium
source: PRD R3, R5; Story 2 criteria 2, 4
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::pricing with the same code twice gives the same result
status: covered
---

# Pricing with the same code twice gives the same result

- Given: a cart, rules with a promotion and a code
- When: the cart is priced twice, and once with the lines in the reverse order
- Then: the three results are equal, the discount does not accumulate, and the cart and the rules are unchanged
