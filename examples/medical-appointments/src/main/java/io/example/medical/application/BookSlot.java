package io.example.medical.application;

import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.BookingRule;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.SlotId;

import java.time.Clock;
import java.time.Instant;

/** Use case: a patient books a slot. It gathers the facts; the rule decides. */
public final class BookSlot {

    private final BookingStore store;
    private final BookingRule rule = new BookingRule();

    private final Clock clock;

    public BookSlot(BookingStore store, Clock clock) {
        this.store = store;
        this.clock = clock;
    }

    public BookingOutcome book(PatientId patient, SlotId slotId) {
        return store.atomically(() -> {
            Instant now = clock.instant();
            var slot = store.findSlot(slotId);
            var outcome = rule.decide(patient, slot, now, store.activeBookingOf(slotId),
                    store.slotsHeldBy(patient));
            if (outcome instanceof BookingOutcome.Booked booked) {
                store.save(booked.booking());
            }
            return outcome;
        });
    }
}
