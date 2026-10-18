---
feature: price-a-cart
type: functional
priority: high
source: PRD C8, C1, D-40, D-45
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::rules with a blank promotion code are refused at construction
status: covered
---

# Rules with a blank promotion code are refused

- Given: rules whose promotion code is empty or only blank (spaces, tab, line break, no-break space, ideographic space)
- When: the rules are built
- Then: the build is refused; a code of one letter, a code with spaces around it, or an invisible character is accepted and matches only its exact text; a promotion alone still builds
