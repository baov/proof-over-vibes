---
feature: price-a-cart
type: functional
priority: high
source: PRD C2, C8
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::refused rules leave nothing behind
status: covered
---

# Refused rules leave nothing behind

- Given: rules refused for a blank promotion code, twice
- When: corrected rules are built and a cart is priced
- Then: the refusal is the same both times and the corrected rules price like fresh ones
