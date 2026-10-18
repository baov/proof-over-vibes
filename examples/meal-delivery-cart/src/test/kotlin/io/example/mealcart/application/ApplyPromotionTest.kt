package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.cart.CartLine
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.money.Percentage
import io.example.mealcart.domain.result.PromotionNotApplied
import io.example.mealcart.domain.rules.Promotion
import io.example.mealcart.domain.rules.PricingRules
import java.util.Currency
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

class ApplyPromotionTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    private fun line(unitPrice: Long, quantity: Int) = CartLine(eur(unitPrice), quantity)

    private fun cartOf(subtotal: Long) = Cart(listOf(line(subtotal, 1)))

    private val tenPercent = Percentage(10, 2)

    private fun rules(
        rate: Percentage = tenPercent,
        minimum: Long = 1000,
        fee: Long = 250,
        code: String = "WELCOME10",
    ) = PricingRules(eur, eur(fee), Promotion(code, rate, eur(minimum)))

    @Test
    fun `a valid code takes the rate off the subtotal`() {
        val price = PriceCart.price(cartOf(2000), rules(), "WELCOME10")

        assertEquals(eur(200), price.discount)
        assertNull(price.promotionNotApplied)
        assertEquals(eur(2050), price.total)
    }

    @Test
    fun `the discount is rounded once, half up, to the smallest unit`() {
        val fivePercent = rules(rate = Percentage(5, 2), minimum = 0)

        assertEquals(eur(50), PriceCart.price(cartOf(1009), fivePercent, "WELCOME10").discount)
        assertEquals(eur(51), PriceCart.price(cartOf(1010), fivePercent, "WELCOME10").discount)
        assertEquals(eur(51), PriceCart.price(cartOf(1011), fivePercent, "WELCOME10").discount)

        val twelveAndAHalf = rules(rate = Percentage(125, 3), minimum = 0)
        assertEquals(eur(125), PriceCart.price(cartOf(1001), twelveAndAHalf, "WELCOME10").discount)

        val yen = PricingRules(jpy, Money(300, jpy), Promotion("WELCOME10", Percentage(5, 2), Money.zero(jpy)))
        val inYen = PriceCart.price(Cart(listOf(CartLine(Money(1010, jpy), 1))), yen, "WELCOME10")
        assertEquals(Money(51, jpy), inYen.discount)
        assertEquals(Money(1010 - 51 + 300, jpy), inYen.total)

        val threeLines = Cart(listOf(line(333, 1), line(333, 1), line(333, 1)))
        assertEquals(eur(100), PriceCart.price(threeLines, rules(minimum = 0), "WELCOME10").discount)
    }

    @Test
    fun `the total is subtotal minus the rounded discount plus the fee`() {
        val cart = Cart(listOf(line(350, 2), line(1450, 1)))

        val price = PriceCart.price(cart, rules(), "WELCOME10")

        assertEquals(eur(2150), price.subtotal)
        assertEquals(eur(215), price.discount)
        assertEquals(eur(250), price.feeLine)
        assertEquals(eur(2185), price.total)
    }

    @Test
    fun `an unknown code gives no discount and says why`() {
        val price = PriceCart.price(cartOf(2000), rules(), "OTHER")

        assertEquals(eur(0), price.discount)
        assertEquals(PromotionNotApplied.UNKNOWN_CODE, price.promotionNotApplied)
        assertEquals(eur(2000), price.subtotal)
        assertEquals(eur(250), price.feeLine)
        assertEquals(eur(2250), price.total)

        val noPromotion = PricingRules(eur, eur(250))
        val withoutPromotion = PriceCart.price(cartOf(2000), noPromotion, "WELCOME10")
        assertEquals(eur(0), withoutPromotion.discount)
        assertEquals(PromotionNotApplied.UNKNOWN_CODE, withoutPromotion.promotionNotApplied)
        assertEquals(eur(2250), withoutPromotion.total)
    }

    @Test
    fun `a subtotal below the minimum gives no discount and says why`() {
        val price = PriceCart.price(cartOf(999), rules(), "WELCOME10")

        assertEquals(eur(0), price.discount)
        assertEquals(PromotionNotApplied.SUBTOTAL_BELOW_MINIMUM, price.promotionNotApplied)
        assertEquals(eur(250), price.feeLine)
        assertEquals(eur(1249), price.total)
    }

    @Test
    fun `a subtotal equal to the minimum still gets the promotion`() {
        val atMinimum = PriceCart.price(cartOf(1000), rules(), "WELCOME10")
        val aboveMinimum = PriceCart.price(cartOf(1001), rules(), "WELCOME10")

        assertEquals(eur(100), atMinimum.discount)
        assertNull(atMinimum.promotionNotApplied)
        assertEquals(eur(100), aboveMinimum.discount)
        assertNull(aboveMinimum.promotionNotApplied)
    }

    @Test
    fun `an unknown code is the only reason when the subtotal is also below the minimum`() {
        val price = PriceCart.price(cartOf(999), rules(), "OTHER")

        assertEquals(PromotionNotApplied.UNKNOWN_CODE, price.promotionNotApplied)
        assertEquals(eur(0), price.discount)
    }

    @Test
    fun `an empty cart with a code is a subtotal of zero`() {
        val empty = Cart(emptyList())

        val belowMinimum = PriceCart.price(empty, rules(), "WELCOME10")
        assertEquals(PromotionNotApplied.SUBTOTAL_BELOW_MINIMUM, belowMinimum.promotionNotApplied)
        assertEquals(listOf(eur(0), eur(0), null, eur(0)), listOf(belowMinimum.subtotal, belowMinimum.discount, belowMinimum.feeLine, belowMinimum.total))

        val unknown = PriceCart.price(empty, rules(), "OTHER")
        assertEquals(PromotionNotApplied.UNKNOWN_CODE, unknown.promotionNotApplied)
        assertEquals(eur(0), unknown.total)

        val noMinimum = PriceCart.price(empty, rules(minimum = 0), "WELCOME10")
        assertNull(noMinimum.promotionNotApplied)
        assertNull(noMinimum.feeLine)
        assertEquals(eur(0), noMinimum.discount)
        assertEquals(eur(0), noMinimum.total)
    }

    @Test
    fun `without a code the discount is zero even when the rules hold a promotion`() {
        val price = PriceCart.price(cartOf(2000), rules())

        assertEquals(eur(0), price.discount)
        assertNull(price.promotionNotApplied)
        assertEquals(eur(2250), price.total)
    }

    @Test
    fun `a discount that rounds to zero is applied with no reason`() {
        val price = PriceCart.price(cartOf(10), rules(rate = Percentage(1, 2), minimum = 0), "WELCOME10")

        assertEquals(eur(0), price.discount)
        assertNull(price.promotionNotApplied)
        assertEquals(eur(260), price.total)
    }

    @Test
    fun `rules with a rate below 0 or above 100 percent are refused`() {
        listOf(Percentage(101, 2), Percentage(1001, 3), Percentage(2, 0), Percentage(-1, 2)).forEach { rate ->
            assertFailsWith<IllegalArgumentException> { rules(rate = rate) }
        }
    }

    @Test
    fun `rates of 0 and 100 percent are valid`() {
        val none = PriceCart.price(cartOf(2000), rules(rate = Percentage(0, 2)), "WELCOME10")
        assertEquals(eur(0), none.discount)
        assertNull(none.promotionNotApplied)

        listOf(Percentage(100, 2), Percentage(1, 0), Percentage(1000, 3)).forEach { rate ->
            assertEquals(eur(2000), PriceCart.price(cartOf(2000), rules(rate = rate), "WELCOME10").discount)
        }
    }

    @Test
    fun `rules with a promotion minimum in another currency are refused`() {
        val minimumInYen = Promotion("WELCOME10", tenPercent, Money(1000, jpy))

        assertFailsWith<IllegalArgumentException> { PricingRules(eur, eur(250), minimumInYen) }
    }

    @Test
    fun `a rate with a scale outside 0 to 18 is refused`() {
        assertFailsWith<IllegalArgumentException> { Percentage(5, -1) }
        assertFailsWith<IllegalArgumentException> { Percentage(5, 19) }
        Percentage(5, 0)
        Percentage(1, 18)
    }

    @Test
    fun `the discount never exceeds the subtotal`() {
        val everything = rules(rate = Percentage(100, 2), minimum = 0)
        listOf(1L, 1001L, 2000L).forEach { subtotal ->
            val price = PriceCart.price(cartOf(subtotal), everything, "WELCOME10")

            assertEquals(eur(subtotal), price.discount)
            assertEquals(eur(250), price.total)
        }

        val almostEverything = rules(rate = Percentage(999, 3), minimum = 0)
        assertEquals(eur(1), PriceCart.price(cartOf(1), almostEverything, "WELCOME10").discount)
        assertEquals(eur(1000), PriceCart.price(cartOf(1001), almostEverything, "WELCOME10").discount)
    }

    @Test
    fun `the fee line is the same with and without a promotion`() {
        val cart = Cart(listOf(line(350, 2), line(1450, 1)))
        val everything = rules(rate = Percentage(1, 0), minimum = 0)

        val without = PriceCart.price(cart, everything)
        val with = PriceCart.price(cart, everything, "WELCOME10")

        assertEquals(eur(250), without.feeLine)
        assertEquals(without.feeLine, with.feeLine)
        assertEquals(eur(250), with.total)
    }

    @Test
    fun `a line of quantity zero is refused even with a code`() {
        assertFailsWith<IllegalArgumentException> {
            PriceCart.price(Cart(listOf(CartLine(eur(350), 0))), rules(), "WELCOME10")
        }
    }

    @Test
    fun `a code matches only the exact configured text`() {
        listOf("welcome10", " WELCOME10", "WELCOME10 ", "WELCOME1").forEach { almost ->
            val price = PriceCart.price(cartOf(2000), rules(), almost)

            assertEquals(eur(0), price.discount)
            assertEquals(PromotionNotApplied.UNKNOWN_CODE, price.promotionNotApplied)
        }
        assertEquals(eur(200), PriceCart.price(cartOf(2000), rules(), "WELCOME10").discount)
    }

    @Test
    fun `pricing with the same code twice gives the same result`() {
        val cart = Cart(listOf(line(350, 2), line(1450, 1)))
        val reversed = Cart(listOf(line(1450, 1), line(350, 2)))
        val promotionRules = rules()

        val first = PriceCart.price(cart, promotionRules, "WELCOME10")
        val second = PriceCart.price(cart, promotionRules, "WELCOME10")

        assertEquals(first, second)
        assertEquals(first, PriceCart.price(reversed, promotionRules, "WELCOME10"))
        assertEquals(listOf(line(350, 2), line(1450, 1)), cart.lines)
        assertEquals(rules(), promotionRules)
    }
}
