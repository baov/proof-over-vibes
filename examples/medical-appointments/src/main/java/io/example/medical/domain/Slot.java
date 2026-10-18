package io.example.medical.domain;

/** A time slot offered by a practitioner. Whether it is free is derived from its bookings. */
public record Slot(SlotId id, PractitionerId practitioner) {
}
