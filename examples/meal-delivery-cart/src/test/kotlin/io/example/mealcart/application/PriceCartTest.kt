package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.cart.CartLine
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.rules.PricingRules
import java.util.Currency
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

class PriceCartTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    private fun line(unitPrice: Long, quantity: Int) = CartLine(eur(unitPrice), quantity)

    private fun eurRules(deliveryFee: Long = 0) = PricingRules(eur, eur(deliveryFee))

    @Test
    fun `the subtotal is the sum of unit price times quantity`() {
        val cart = Cart(listOf(line(350, 2), line(1200, 1)))

        val price = PriceCart.price(cart, eurRules())

        assertEquals(eur(1900), price.subtotal)
        assertEquals(1900L, price.subtotal.minorUnits)
        assertEquals(eur(725), PriceCart.price(Cart(listOf(line(725, 1))), eurRules()).subtotal)
    }

    @Test
    fun `the result exposes subtotal, discount, fee line and total`() {
        val cart = Cart(listOf(line(350, 2), line(1200, 1)))

        val (subtotal, discount, feeLine, total) = PriceCart.price(cart, eurRules(deliveryFee = 250))

        assertEquals(eur(1900), subtotal)
        assertEquals(eur(0), discount)
        assertEquals(eur(250), feeLine)
        assertEquals(eur(2150), total)
    }

    @Test
    fun `the discount is zero`() {
        val price = PriceCart.price(Cart(listOf(line(350, 2))), eurRules())

        assertEquals(eur(0), price.discount)
    }

    @Test
    fun `the fee line is the delivery fee of the rules, unchanged`() {
        val smallCart = Cart(listOf(line(100, 1)))
        val bigCart = Cart(listOf(line(5000, 3), line(1200, 2)))

        assertEquals(eur(250), PriceCart.price(smallCart, eurRules(deliveryFee = 250)).feeLine)
        assertEquals(eur(250), PriceCart.price(bigCart, eurRules(deliveryFee = 250)).feeLine)
        assertEquals(eur(0), PriceCart.price(smallCart, eurRules(deliveryFee = 0)).feeLine)
    }

    @Test
    fun `the total is subtotal minus discount plus the fee line`() {
        val cart = Cart(listOf(line(350, 2), line(1200, 1)))

        val price = PriceCart.price(cart, eurRules(deliveryFee = 250))

        assertEquals(eur(2150), price.total)
        assertEquals(price.subtotal - price.discount + price.feeLine!!, price.total)
        assertEquals(eur(1900), PriceCart.price(cart, eurRules(deliveryFee = 0)).total)
    }

    @Test
    fun `an empty cart gives zero amounts and no fee line`() {
        val price = PriceCart.price(Cart(emptyList()), eurRules(deliveryFee = 250))

        assertEquals(eur(0), price.subtotal)
        assertEquals(eur(0), price.discount)
        assertNull(price.feeLine)
        assertEquals(eur(0), price.total)
    }

    @Test
    fun `a line of quantity zero is refused`() {
        assertFailsWith<IllegalArgumentException> { CartLine(eur(350), 0) }
    }

    @Test
    fun `every amount is in the currency of the rules`() {
        val inYen = PriceCart.price(
            Cart(listOf(CartLine(Money(500, jpy), 2))),
            PricingRules(jpy, Money(300, jpy)),
        )
        val inEuros = PriceCart.price(Cart(listOf(line(500, 2))), PricingRules(eur, eur(300)))

        assertEquals(
            listOf(Money(1000, jpy), Money.zero(jpy), Money(300, jpy), Money(1300, jpy)),
            listOf(inYen.subtotal, inYen.discount, inYen.feeLine, inYen.total),
        )
        assertEquals(
            listOf(eur(1000), eur(0), eur(300), eur(1300)),
            listOf(inEuros.subtotal, inEuros.discount, inEuros.feeLine, inEuros.total),
        )
    }

    @Test
    fun `a line priced in another currency than the rules is refused`() {
        val cart = Cart(listOf(line(350, 1), CartLine(Money(500, jpy), 1)))

        assertFailsWith<IllegalArgumentException> { PriceCart.price(cart, eurRules()) }
    }

    @Test
    fun `rules with a fee in another currency are refused`() {
        assertFailsWith<IllegalArgumentException> { PricingRules(eur, Money(250, jpy)) }
    }

    @Test
    fun `changing one rule parameter changes the result and nothing else`() {
        val cart = Cart(listOf(line(350, 2), line(1200, 1)))

        val before = PriceCart.price(cart, eurRules(deliveryFee = 250))
        val dearerDelivery = PriceCart.price(cart, eurRules(deliveryFee = 400))
        val otherCurrency = PriceCart.price(
            Cart(listOf(CartLine(Money(350, jpy), 2), CartLine(Money(1200, jpy), 1))),
            PricingRules(jpy, Money(250, jpy)),
        )

        assertEquals(before.copy(feeLine = eur(400), total = eur(2300)), dearerDelivery)
        assertEquals(Money(1900, jpy), otherCurrency.subtotal)
        assertEquals(Money(250, jpy), otherCurrency.feeLine)
        assertEquals(Money(2150, jpy), otherCurrency.total)
    }

    @Test
    fun `the same cart and rules give the same result, whatever the line order`() {
        val first = line(350, 2)
        val second = line(1200, 1)
        val third = line(99, 3)
        val rules = eurRules(deliveryFee = 250)

        val price = PriceCart.price(Cart(listOf(first, second, third)), rules)

        assertEquals(price, PriceCart.price(Cart(listOf(first, second, third)), rules))
        assertEquals(price, PriceCart.price(Cart(listOf(third, first, second)), rules))
    }

    @Test
    fun `pricing leaves the cart unchanged`() {
        val lines = mutableListOf(line(350, 2), line(1200, 1))
        val cart = Cart(lines)
        val rules = eurRules(deliveryFee = 250)

        val price = PriceCart.price(cart, rules)
        lines.add(line(5000, 1))

        assertEquals(listOf(line(350, 2), line(1200, 1)), cart.lines)
        assertEquals(price, PriceCart.price(cart, rules))
    }

    @Test
    fun `the same line twice in a cart counts twice`() {
        val cart = Cart(listOf(line(350, 2), line(350, 2)))

        assertEquals(eur(1400), PriceCart.price(cart, eurRules()).subtotal)
    }

    @Test
    fun `a cart of free lines still has the fee line`() {
        val price = PriceCart.price(Cart(listOf(line(0, 3), line(0, 1))), eurRules(deliveryFee = 250))

        assertEquals(eur(0), price.subtotal)
        assertEquals(eur(0), price.discount)
        assertEquals(eur(250), price.feeLine)
        assertEquals(eur(250), price.total)
    }
}
