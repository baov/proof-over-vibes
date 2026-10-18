package io.example.mealcart.domain.cart

import io.example.mealcart.domain.money.Money

/** A unit price and a quantity. A line of quantity zero cannot exist, so a cart never holds one. */
data class CartLine(val unitPrice: Money, val quantity: Int) {
    init {
        require(quantity != 0) { "A line of quantity zero is invalid" }
    }
}
