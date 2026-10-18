package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.pricing.price as priceCart
import io.example.mealcart.domain.result.Price
import io.example.mealcart.domain.rules.PricingRules

/** The entry point the caller uses to price a cart. Stateless. */
object PriceCart {
    fun price(cart: Cart, rules: PricingRules, code: String? = null): Price = priceCart(cart, rules, code)
}
