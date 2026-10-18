---
feature: price-a-cart
type: functional
priority: high
source: PRD C1, D-34
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a non-blank code is never trimmed or reinterpreted
status: covered
---

# A non-blank code is never trimmed or reinterpreted

- Given: a promotion with the code WELCOME10
- When: the cart is priced with the exact code, then with the code surrounded by spaces or a line break, in another case, with a space inside, or made only of an invisible character
- Then: the exact code applies; each other one is an unknown code with no discount; an invisible character is a character, not blank
