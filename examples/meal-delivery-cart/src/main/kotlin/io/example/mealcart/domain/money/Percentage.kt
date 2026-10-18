package io.example.mealcart.domain.money

/**
 * A rate as a fraction of an amount: numerator over 10 to the power of scale (10, 2 is 10 percent; 125, 3 is 12.5 percent).
 * Only the scale is checked here; the rules decide which rates they accept.
 */
data class Percentage(val numerator: Long, val scale: Int) {
    init {
        require(scale in 0..18) { "The scale of a rate is 0 to 18, not $scale" }
    }

    internal val denominator: Long = (1..scale).fold(1L) { power, _ -> power * 10 }
}
