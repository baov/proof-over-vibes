---
feature: price-a-cart
type: functional
priority: high
source: PRD C7, D-45
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::what counts as blank for a code is pinned by named characters
status: covered
---

# What counts as blank for a code

- Given: a code of one character: space, tab, line feed, carriage return, vertical tab, form feed, no-break space, figure space, narrow no-break space, em space, ideographic space, or the empty text; or zero-width space, byte order mark, a letter, a digit
- When: the cart is priced with that code
- Then: the first group is no code; the second group is an unknown code
