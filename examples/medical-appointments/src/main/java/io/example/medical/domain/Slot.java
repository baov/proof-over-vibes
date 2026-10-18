package io.example.medical.domain;

/** A time slot offered by a practitioner over a time range. Whether it is free is derived from its bookings. */
public record Slot(SlotId id, PractitionerId practitioner, TimeRange range) {
}
