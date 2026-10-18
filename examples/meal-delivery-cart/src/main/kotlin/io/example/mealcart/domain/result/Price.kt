package io.example.mealcart.domain.result

import io.example.mealcart.domain.money.Money

/**
 * The breakdown of a priced cart. The fee line is absent when the cart is empty.
 * [promotionNotApplied] says why a supplied code gave no discount; it is null when the promotion applied or no code was supplied.
 */
data class Price(
    val subtotal: Money,
    val discount: Money,
    val feeLine: Money?,
    val total: Money,
    val promotionNotApplied: PromotionNotApplied? = null,
)
