package io.example.mealcart.domain.cart

/** The lines to price. Holds its own copy of the list it is given. */
class Cart(lines: List<CartLine>) {
    val lines: List<CartLine> = lines.toList()
}
