---
feature: price-a-cart
type: functional
priority: medium
source: PRD R15; architect note (rules validation)
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::rules with a fee in another currency are refused
status: covered
---

# Rules with a fee in another currency are refused

- Given: rules in euros whose delivery fee is an amount in yen
- When: the rules are built
- Then: they are refused as invalid input (IllegalArgumentException); no cart is priced with them
