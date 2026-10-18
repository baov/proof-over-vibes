package io.example.mealcart.domain.result

import io.example.mealcart.domain.money.Money

/** The breakdown of a priced cart. The fee line is absent when the cart is empty. */
data class Price(val subtotal: Money, val discount: Money, val feeLine: Money?, val total: Money)
