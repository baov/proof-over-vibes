package io.example.medical.domain;

/** Why a booking is refused (D-26). */
public enum RefusalReason {
    UNKNOWN_SLOT,
    PAST,
    TAKEN,
    OVERLAPPING
}
