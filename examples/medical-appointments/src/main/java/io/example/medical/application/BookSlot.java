package io.example.medical.application;

import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.BookingRule;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.SlotId;

/** Use case: a patient books a slot. It gathers the facts; the rule decides. */
public final class BookSlot {

    private final BookingStore store;
    private final BookingRule rule = new BookingRule();

    public BookSlot(BookingStore store) {
        this.store = store;
    }

    public BookingOutcome book(PatientId patient, SlotId slotId) {
        return store.atomically(() -> {
            var slot = store.findSlot(slotId).orElseThrow();
            var outcome = rule.decide(patient, slot, store.activeBookingOf(slotId));
            if (outcome instanceof BookingOutcome.Booked booked) {
                store.save(booked.booking());
            }
            return outcome;
        });
    }
}
