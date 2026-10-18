package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.cart.CartLine
import io.example.mealcart.domain.money.AmountTooLargeException
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.money.Percentage
import io.example.mealcart.domain.rules.PricingRules
import io.example.mealcart.domain.rules.Promotion
import java.util.Currency
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

/** Edge cases on amounts: negative inputs, amounts beyond the money range, every rate scale. */
class EdgeAmountsTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")
    private val max = Long.MAX_VALUE

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    private fun line(unitPrice: Long, quantity: Int = 1) = CartLine(eur(unitPrice), quantity)

    private fun cartOf(vararg unitPrices: Long) = Cart(unitPrices.map { line(it) })

    private fun rules(fee: Long = 0) = PricingRules(eur, eur(fee))

    private fun rulesWithRate(rate: Percentage, fee: Long = 0, minimum: Long = 0) =
        PricingRules(eur, eur(fee), Promotion("WELCOME10", rate, eur(minimum)))

    private val code = "WELCOME10"

    @Test
    fun `a line of negative quantity is refused`() {
        assertFailsWith<IllegalArgumentException> { CartLine(eur(350), -1) }
        assertFailsWith<IllegalArgumentException> { CartLine(eur(350), Int.MIN_VALUE) }
        assertFailsWith<IllegalArgumentException> { CartLine(eur(350), 0) }
        assertEquals(1, CartLine(eur(350), 1).quantity)
    }

    @Test
    fun `a line of negative unit price is refused, a free line is valid`() {
        assertFailsWith<IllegalArgumentException> { CartLine(eur(-1), 1) }
        assertFailsWith<IllegalArgumentException> { CartLine(Money(Long.MIN_VALUE, eur), 1) }
        val free = Cart(listOf(CartLine(eur(0), 1)))
        assertEquals(eur(250), PriceCart.price(free, rules(fee = 250)).feeLine)
    }

    @Test
    fun `rules with a negative delivery fee are refused, a free delivery is valid`() {
        assertFailsWith<IllegalArgumentException> { PricingRules(eur, eur(-1)) }
        assertFailsWith<IllegalArgumentException> { PricingRules(eur, Money(Long.MIN_VALUE, eur)) }
        val price = PriceCart.price(cartOf(500), PricingRules(eur, eur(0)))
        assertEquals(eur(0), price.feeLine)
        assertEquals(eur(500), price.total)
    }

    @Test
    fun `rules with a negative promotion minimum are refused, a minimum of zero is valid`() {
        val ten = Percentage(10, 2)
        assertFailsWith<IllegalArgumentException> { rulesWithRate(ten, minimum = -1) }
        assertFailsWith<IllegalArgumentException> { rulesWithRate(ten, minimum = Long.MIN_VALUE) }
        assertEquals(eur(0), PriceCart.price(cartOf(), rulesWithRate(ten, minimum = 0), code).discount)
        assertEquals(eur(50), PriceCart.price(cartOf(500), rulesWithRate(ten, minimum = 0), code).discount)
    }

    @Test
    fun `no amount of a price is negative`() {
        val cases = listOf(
            cartOf(0) to rulesWithRate(Percentage(1, 0), fee = 250),
            cartOf(501) to rulesWithRate(Percentage(1, 0), fee = 250),
            cartOf(500) to rulesWithRate(Percentage(1, 0)),
            cartOf(1) to rulesWithRate(Percentage(999, 3)),
        )
        cases.forEach { (cart, rules) ->
            val price = PriceCart.price(cart, rules, code)
            val fee = price.feeLine ?: Money.zero(eur)
            assertTrue(price.subtotal.minorUnits >= 0)
            assertTrue(price.discount.minorUnits >= 0)
            assertTrue(fee.minorUnits >= 0)
            assertTrue(price.total.minorUnits >= 0)
            assertTrue(price.discount <= price.subtotal)
            assertEquals(price.subtotal - price.discount + fee, price.total)
        }
    }

    @Test
    fun `a line beyond the money range is refused, one at the limit is priced`() {
        val atTheLimit = Cart(listOf(line(1317624576693539401, 7)))
        assertEquals(eur(max), PriceCart.price(atTheLimit, rules()).subtotal)
        assertFailsWith<AmountTooLargeException> {
            PriceCart.price(Cart(listOf(line(1317624576693539402, 7))), rules())
        }
        assertEquals(
            eur(max - 1),
            PriceCart.price(Cart(listOf(line(4294967298, Int.MAX_VALUE))), rules()).subtotal,
        )
        assertFailsWith<AmountTooLargeException> {
            PriceCart.price(Cart(listOf(line(4294967299, Int.MAX_VALUE))), rules())
        }
    }

    @Test
    fun `lines that fit alone but not together are refused`() {
        assertEquals(eur(max), PriceCart.price(cartOf(max - 5, 5), rules()).subtotal)
        assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(max - 5, 6), rules()) }
    }

    @Test
    fun `a total beyond the money range is refused when the subtotal alone fits`() {
        assertEquals(eur(max), PriceCart.price(cartOf(max - 250), rules(fee = 250)).total)
        assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(max - 250), rules(fee = 251)) }
        assertEquals(eur(max - 250), PriceCart.price(cartOf(max - 250), rules(fee = 0)).total)
        assertEquals(eur(max), PriceCart.price(cartOf(0), rules(fee = max)).total)
        assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(1), rules(fee = max)) }
    }

    @Test
    fun `amount too large is its own refusal, apart from invalid input`() {
        val tooLarge = assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(max, 1), rules()) }
        assertTrue(tooLarge is ArithmeticException)
        assertTrue(tooLarge !is IllegalArgumentException)
        val zeroQuantity = assertFailsWith<IllegalArgumentException> { CartLine(eur(1), 0) }
        assertTrue(zeroQuantity !is ArithmeticException)
        val badRate = assertFailsWith<IllegalArgumentException> { rulesWithRate(Percentage(101, 2)) }
        assertTrue(badRate !is ArithmeticException)
    }

    private fun pow10(exponent: Int) = (1..exponent).fold(1L) { power, _ -> power * 10 }

    private val scales = 1..18

    @Test
    fun `ten percent prices the same at every scale`() {
        val reference = rulesWithRate(Percentage(10, 2), fee = 250)
        scales.forEach { scale ->
            val rules = rulesWithRate(Percentage(pow10(scale - 1), scale), fee = 250)
            listOf(100L, 100_000L, 100_000_000L, 9_000_000_000_000_000_000L).forEach { subtotal ->
                assertEquals(
                    PriceCart.price(cartOf(subtotal), reference, code),
                    PriceCart.price(cartOf(subtotal), rules, code),
                    "scale $scale, subtotal $subtotal",
                )
            }
        }
        assertEquals(eur(900_000_000_000_000_000), PriceCart.price(cartOf(9_000_000_000_000_000_000L), reference, code).discount)
        assertEquals(eur(0), PriceCart.price(cartOf(777), rulesWithRate(Percentage(0, 0)), code).discount)
        assertEquals(eur(777), PriceCart.price(cartOf(777), rulesWithRate(Percentage(1, 0)), code).discount)
    }

    @Test
    fun `a discount is rounded half up at every scale`() {
        scales.forEach { scale ->
            val rules = rulesWithRate(Percentage(5, scale))
            val half = pow10(scale - 1)
            assertEquals(eur(1), PriceCart.price(cartOf(half), rules, code).discount, "scale $scale, exactly half")
            assertEquals(eur(0), PriceCart.price(cartOf(half - 1), rules, code).discount, "scale $scale, just under half")
        }
    }

    @Test
    fun `the largest subtotal is discounted exactly at any rate`() {
        val tenPercent = PriceCart.price(cartOf(max), rulesWithRate(Percentage(10, 2)), code)
        assertEquals(eur(922337203685477581), tenPercent.discount)
        assertEquals(eur(max - 922337203685477581), tenPercent.total)
        assertEquals(eur(4611686018427387904), PriceCart.price(cartOf(max), rulesWithRate(Percentage(50, 2)), code).discount)
        listOf(0, 1, 9, 18).forEach { scale ->
            val wholeSubtotal = PriceCart.price(cartOf(max), rulesWithRate(Percentage(pow10(scale), scale)), code)
            assertEquals(eur(max), wholeSubtotal.discount, "scale $scale")
            assertEquals(eur(0), wholeSubtotal.total, "scale $scale")
        }
        val almostAll = PriceCart.price(cartOf(max), rulesWithRate(Percentage(pow10(18) - 1, 18)), code)
        assertEquals(eur(9223372036854775798), almostAll.discount)
        assertEquals(eur(9), almostAll.total)
        scales.forEach { scale ->
            val price = PriceCart.price(cartOf(max), rulesWithRate(Percentage(pow10(scale - 1), scale)), code)
            assertEquals(eur(922337203685477581), price.discount, "scale $scale")
        }
    }

    @Test
    fun `the bounds of a rate hold at the widest scale`() {
        rulesWithRate(Percentage(pow10(18), 18))
        rulesWithRate(Percentage(0, 18))
        listOf(pow10(18) + 1, -1L, max).forEach { numerator ->
            assertFailsWith<IllegalArgumentException> { rulesWithRate(Percentage(numerator, 18)) }
        }
    }

    private val maxSubtotalLine = line(1317624576693539401, 7)

    @Test
    fun `a total that fits after the discount is accepted although subtotal plus fee does not`() {
        val maxSubtotal = Cart(listOf(maxSubtotalLine))
        listOf(Percentage(1, 0), Percentage(pow10(18), 18)).forEach { wholeSubtotal ->
            val price = PriceCart.price(maxSubtotal, rulesWithRate(wholeSubtotal, fee = 1000), code)
            assertEquals(eur(max), price.discount)
            assertEquals(eur(1000), price.total)
        }
        val nineBillionBillion = cartOf(9_000_000_000_000_000_000L)
        val fits = PriceCart.price(nineBillionBillion, rulesWithRate(Percentage(10, 2), fee = 1123372036854775807), code)
        assertEquals(eur(900_000_000_000_000_000), fits.discount)
        assertEquals(eur(max), fits.total)
        assertFailsWith<AmountTooLargeException> {
            PriceCart.price(nineBillionBillion, rulesWithRate(Percentage(10, 2), fee = 1123372036854775808), code)
        }
    }

    @Test
    fun `a refused pricing changes nothing and can be redone`() {
        val oversized = Cart(listOf(line(max - 5), line(6)))
        val linesBefore = oversized.lines.toList()
        val rules = rules(fee = 250)
        val rulesBefore = rules.copy()

        assertFailsWith<AmountTooLargeException> { PriceCart.price(oversized, rules) }
        assertFailsWith<AmountTooLargeException> { PriceCart.price(oversized, rules) }

        assertEquals(linesBefore, oversized.lines)
        assertEquals(rulesBefore, rules)
        val corrected = Cart(listOf(line(max - 500), line(5)))
        assertEquals(PriceCart.price(corrected, rules), PriceCart.price(Cart(listOf(line(max - 500), line(5))), rules))
        assertEquals(eur(max - 245), PriceCart.price(corrected, rules).total)
        val onlyTheFeeIsTooMuch = cartOf(max - 250)
        assertFailsWith<AmountTooLargeException> { PriceCart.price(onlyTheFeeIsTooMuch, rules(fee = 251)) }
        assertEquals(eur(max - 250), PriceCart.price(onlyTheFeeIsTooMuch, rules(fee = 0)).total)
        assertFailsWith<IllegalArgumentException> { rules(fee = -1) }
        assertEquals(eur(250), PriceCart.price(cartOf(100), rules(fee = 250)).feeLine)
    }

    @Test
    fun `the refusal does not depend on the order of the lines`() {
        assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(max - 5, 6), rules()) }
        assertFailsWith<AmountTooLargeException> { PriceCart.price(cartOf(6, max - 5), rules()) }
        assertEquals(eur(max), PriceCart.price(cartOf(max - 5, 5), rules()).subtotal)
        assertEquals(eur(max), PriceCart.price(cartOf(5, max - 5), rules()).subtotal)
    }

    @Test
    fun `an empty cart ignores a fee of any size`() {
        val price = PriceCart.price(cartOf(), rules(fee = max))

        assertEquals(eur(0), price.subtotal)
        assertEquals(eur(0), price.discount)
        assertEquals(null, price.feeLine)
        assertEquals(eur(0), price.total)
    }

    @Test
    fun `a code never hides an amount that is too large`() {
        val rules = PricingRules(eur, eur(max), Promotion(code, Percentage(10, 2), eur(1000)))
        listOf("OTHER" to 2000L, code to 500L, code to 2000L).forEach { (suppliedCode, subtotal) ->
            assertFailsWith<AmountTooLargeException>("$suppliedCode on $subtotal") {
                PriceCart.price(cartOf(subtotal), rules, suppliedCode)
            }
        }
    }

    @Test
    fun `a line in another currency is refused before any amount is looked at`() {
        val tooLargeLine = line(1317624576693539402, 7)
        val foreignLine = CartLine(Money(1, jpy), 1)
        val tooLargeForeignLine = CartLine(Money(1317624576693539402, jpy), 7)
        listOf(
            Cart(listOf(tooLargeLine, foreignLine)),
            Cart(listOf(tooLargeForeignLine)),
            Cart(listOf(line(max - 5), line(6), foreignLine)),
        ).forEach { cart ->
            assertFailsWith<IllegalArgumentException> { PriceCart.price(cart, rules()) }
        }
    }
}
