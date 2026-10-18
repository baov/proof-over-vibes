package io.example.medical.domain;

/** The link between a patient and a slot. A slot has at most one active booking. */
public record Booking(PatientId patient, SlotId slot) {
}
