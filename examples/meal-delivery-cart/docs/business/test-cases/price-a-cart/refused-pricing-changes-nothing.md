---
feature: price-a-cart
type: functional
priority: high
source: PRD A5, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a refused pricing changes nothing and can be redone
status: covered
---

# A refused pricing changes nothing and can be redone

- Given: a cart beyond the money range, then a corrected cart and smaller rules
- When: the cart is priced twice, then the corrected one
- Then: the refusal is the same both times; the cart and the rules are unchanged; the corrected cart and the smaller rules are priced correctly; rules refused at construction leave corrected rules buildable
