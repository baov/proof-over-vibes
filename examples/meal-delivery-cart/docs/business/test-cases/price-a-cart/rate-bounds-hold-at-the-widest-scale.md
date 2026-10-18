---
feature: price-a-cart
type: functional
priority: high
source: PRD A12, D-39
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::the bounds of a rate hold at the widest scale
status: covered
---

# The bounds of a rate hold at the widest scale

- Given: rates at scale 18 from 0 to 100 percent, and rates just above, below and far above
- When: the rules are built
- Then: 0 and 100 percent are accepted; any other is refused as invalid input, never as amount too large
