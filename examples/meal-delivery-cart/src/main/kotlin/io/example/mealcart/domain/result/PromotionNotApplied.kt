package io.example.mealcart.domain.result

/** Why a supplied code gave no discount. */
enum class PromotionNotApplied { UNKNOWN_CODE, SUBTOTAL_BELOW_MINIMUM }
