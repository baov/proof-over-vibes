package io.example.mealcart.domain.cart

import io.example.mealcart.domain.money.Money

/** A unit price and a quantity. A line of quantity zero or less, or of a negative unit price, cannot exist, so a cart never holds one. */
data class CartLine(val unitPrice: Money, val quantity: Int) {
    init {
        require(quantity > 0) { "A line of quantity zero or less is invalid, not $quantity" }
        require(unitPrice.minorUnits >= 0) { "A negative unit price is invalid, not ${unitPrice.minorUnits}" }
    }
}
