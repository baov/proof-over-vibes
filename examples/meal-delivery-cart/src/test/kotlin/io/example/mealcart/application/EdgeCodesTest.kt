package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.cart.CartLine
import io.example.mealcart.domain.money.AmountTooLargeException
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.money.Percentage
import io.example.mealcart.domain.result.PromotionNotApplied
import io.example.mealcart.domain.rules.PricingRules
import io.example.mealcart.domain.rules.Promotion
import java.util.Currency
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

/** Edge cases on codes: a blank code is no code, a non-blank code is never trimmed, rules refuse a blank promotion code. */
class EdgeCodesTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    private fun cartOf(vararg unitPrices: Long) = Cart(unitPrices.map { CartLine(eur(it), 1) })

    private val code = "WELCOME10"

    private val tab = "\t"
    private val newline = "\n"
    private val carriageReturn = "\r"
    private val noBreakSpace = " "
    private val ideographicSpace = "　"

    private fun rules(promotionCode: String = code, rate: Percentage = Percentage(10, 2), minimum: Long = 1000) =
        PricingRules(eur, eur(250), Promotion(promotionCode, rate, eur(minimum)))

    private val blankCodes = listOf(
        "", " ", "   ", tab, newline, carriageReturn, noBreakSpace, ideographicSpace, " $tab$newline ",
    )

    @Test
    fun `a blank code is no code`() {
        val withPromotion = rules()
        for (subtotal in listOf(2000L, 999L)) {
            val cart = cartOf(subtotal)
            val noCode = PriceCart.price(cart, withPromotion)
            assertEquals(noCode, PriceCart.price(cart, withPromotion, null))
            for (blank in blankCodes) {
                assertEquals(noCode, PriceCart.price(cart, withPromotion, blank), "code ${blank.map { it.code }}")
            }
        }
        val above = PriceCart.price(cartOf(2000), withPromotion, "")
        assertEquals(eur(0), above.discount)
        assertNull(above.promotionNotApplied)
        assertEquals(eur(2250), above.total)
        val below = PriceCart.price(cartOf(999), withPromotion, " ")
        assertNull(below.promotionNotApplied)
        assertEquals(eur(1249), below.total)
    }

    @Test
    fun `a blank code with rules that have no promotion is no code`() {
        val noPromotion = PricingRules(eur, eur(250))
        val cart = cartOf(2000)
        for (blank in listOf("", " ")) {
            val price = PriceCart.price(cart, noPromotion, blank)
            assertNull(price.promotionNotApplied)
            assertEquals(eur(0), price.discount)
            assertEquals(PriceCart.price(cart, noPromotion), price)
        }
        assertEquals(PromotionNotApplied.UNKNOWN_CODE, PriceCart.price(cart, noPromotion, code).promotionNotApplied)
    }

    @Test
    fun `a blank code with an empty cart is no code`() {
        val price = PriceCart.price(Cart(emptyList()), rules(), "")
        assertEquals(eur(0), price.subtotal)
        assertEquals(eur(0), price.discount)
        assertEquals(eur(0), price.total)
        assertNull(price.feeLine)
        assertNull(price.promotionNotApplied)
        assertEquals(
            PromotionNotApplied.SUBTOTAL_BELOW_MINIMUM,
            PriceCart.price(Cart(emptyList()), rules(), code).promotionNotApplied,
        )
    }

    @Test
    fun `a blank code hides no refusal`() {
        val foreign = Cart(listOf(CartLine(Money(500, jpy), 1)))
        assertFailsWith<IllegalArgumentException> { PriceCart.price(foreign, rules()) }
        assertFailsWith<IllegalArgumentException> { PriceCart.price(foreign, rules(), "") }
        val tooLarge = Cart(listOf(CartLine(eur(Long.MAX_VALUE), 1)))
        assertFailsWith<AmountTooLargeException> { PriceCart.price(tooLarge, rules()) }
        assertFailsWith<AmountTooLargeException> { PriceCart.price(tooLarge, rules(), " ") }
    }

    private val zeroWidthSpace = "\u200B"

    @Test
    fun `a non-blank code is never trimmed or reinterpreted`() {
        val cart = cartOf(2000)
        val exact = PriceCart.price(cart, rules(), code)
        assertEquals(eur(200), exact.discount)
        assertNull(exact.promotionNotApplied)
        val unknown = listOf(
            " $code", "$code ", " $code ", "$code$newline", "welcome10", "WELCOME 10",
            zeroWidthSpace, "$zeroWidthSpace ",
        )
        for (supplied in unknown) {
            val price = PriceCart.price(cart, rules(), supplied)
            assertEquals(PromotionNotApplied.UNKNOWN_CODE, price.promotionNotApplied, "code ${supplied.map { it.code }}")
            assertEquals(eur(0), price.discount)
        }
    }

    @Test
    fun `what counts as blank for a code is pinned by named characters`() {
        val cart = cartOf(2000)
        val noCode = PriceCart.price(cart, rules())
        val blank = mapOf(
            "empty" to "", "space" to " ", "tab" to "\u0009", "newline" to "\u000A", "carriage return" to "\u000D",
            "vertical tab" to "\u000B", "form feed" to "\u000C", "no-break space" to "\u00A0",
            "figure space" to "\u2007", "narrow no-break space" to "\u202F", "em space" to "\u2003",
            "ideographic space" to "\u3000",
        )
        for ((name, character) in blank) {
            assertEquals(noCode, PriceCart.price(cart, rules(), character), "$name is blank")
        }
        val notBlank = mapOf(
            "zero-width space" to "\u200B", "byte order mark" to "\uFEFF", "letter" to "A", "digit" to "0",
        )
        for ((name, character) in notBlank) {
            assertEquals(
                PromotionNotApplied.UNKNOWN_CODE,
                PriceCart.price(cart, rules(), character).promotionNotApplied,
                "$name is a code",
            )
        }
    }

    @Test
    fun `a blank code priced twice gives the same result and changes nothing`() {
        val cart = cartOf(2000, 500)
        val rules = rules()
        val linesBefore = cart.lines.toList()
        val rulesBefore = rules.copy()
        val first = PriceCart.price(cart, rules, "")
        val second = PriceCart.price(cart, rules, "")
        assertEquals(first, second)
        assertEquals(first, PriceCart.price(cart, rules, " "))
        assertEquals(first, PriceCart.price(cart, rules))
        assertEquals(linesBefore, cart.lines)
        assertEquals(rulesBefore, rules)
    }

    @Test
    fun `rules with a blank promotion code are refused at construction`() {
        for (blank in blankCodes) {
            assertFailsWith<IllegalArgumentException>("code ${blank.map { it.code }}") { rules(promotionCode = blank) }
        }
        for (accepted in listOf(code, "A", " $code ", zeroWidthSpace)) {
            assertEquals(accepted, rules(promotionCode = accepted).promotion?.code)
        }
        assertEquals("", Promotion("", Percentage(10, 2), eur(1000)).code)
        val spaced = rules(promotionCode = " SAVE10 ")
        assertEquals(eur(200), PriceCart.price(cartOf(2000), spaced, " SAVE10 ").discount)
        assertEquals(PromotionNotApplied.UNKNOWN_CODE, PriceCart.price(cartOf(2000), spaced, "SAVE10").promotionNotApplied)
    }

    @Test
    fun `a blank promotion code is refused whatever other rule problem there is`() {
        assertFailsWith<IllegalArgumentException> { rules(promotionCode = " ", rate = Percentage(101, 2)) }
        assertFailsWith<IllegalArgumentException> { rules(promotionCode = "", minimum = -1) }
        assertFailsWith<IllegalArgumentException> {
            PricingRules(eur, eur(250), Promotion(" ", Percentage(10, 2), Money(1000, jpy)))
        }
        assertFailsWith<IllegalArgumentException> {
            PricingRules(eur, Money(250, jpy), Promotion("", Percentage(10, 2), eur(1000)))
        }
        assertEquals(code, rules(promotionCode = code, rate = Percentage(100, 2), minimum = 0).promotion?.code)
    }

    @Test
    fun `refused rules leave nothing behind`() {
        assertFailsWith<IllegalArgumentException> { rules(promotionCode = " ") }
        assertFailsWith<IllegalArgumentException> { rules(promotionCode = " ") }
        val corrected = rules()
        val cart = cartOf(2000)
        val fresh = PriceCart.price(cart, rules(), code)
        assertEquals(fresh, PriceCart.price(cart, corrected, code))
        assertEquals(eur(200), fresh.discount)
    }
}
