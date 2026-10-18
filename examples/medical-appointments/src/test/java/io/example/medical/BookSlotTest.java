package io.example.medical;

import io.example.medical.adapters.InMemoryBookingStore;
import io.example.medical.application.BookSlot;
import io.example.medical.application.BookingStore;
import io.example.medical.domain.Booking;
import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.PractitionerId;
import io.example.medical.domain.RefusalReason;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class BookSlotTest {

    private static final PractitionerId DOCTOR = new PractitionerId("dr-martin");
    private static final SlotId S = new SlotId("slot-1");
    private static final SlotId S2 = new SlotId("slot-2");
    private static final SlotId S3 = new SlotId("slot-3");
    private static final PatientId A = new PatientId("patient-a");
    private static final PatientId B = new PatientId("patient-b");

    private final BookingStore store = new InMemoryBookingStore(List.of(new Slot(S, DOCTOR)));
    private final BookSlot bookSlot = new BookSlot(store);

    @Test
    void booksAFreeSlotForThePatient() {
        BookingOutcome outcome = bookSlot.book(A, S);

        Booking expected = new Booking(A, S);
        assertEquals(new BookingOutcome.Booked(expected), outcome);
        assertEquals(Optional.of(expected), store.activeBookingOf(S));
    }

    @Test
    void slotIsNoLongerFreeAfterBooking() {
        assertEquals(Optional.empty(), store.activeBookingOf(S));

        bookSlot.book(A, S);

        assertTrue(store.activeBookingOf(S).isPresent());
    }

    @Test
    void refusesASlotBookedByAnotherPatient() {
        bookSlot.book(A, S);

        BookingOutcome outcome = bookSlot.book(B, S);

        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), outcome);
    }

    @Test
    void refusesASlotThePatientAlreadyHolds() {
        bookSlot.book(A, S);

        BookingOutcome outcome = bookSlot.book(A, S);

        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), outcome);
    }

    @Test
    void aTakenRefusalLeavesTheExistingBookingUnchanged() {
        bookSlot.book(A, S);

        bookSlot.book(B, S);
        bookSlot.book(A, S);

        assertEquals(Optional.of(new Booking(A, S)), store.activeBookingOf(S));
    }

    @Test
    void bookingOneSlotLeavesOtherSlotsFree() {
        BookingStore twoSlots = new InMemoryBookingStore(List.of(new Slot(S, DOCTOR), new Slot(S2, DOCTOR)));
        BookSlot book = new BookSlot(twoSlots);

        book.book(A, S);
        BookingOutcome outcome = book.book(B, S2);

        assertEquals(Optional.of(new Booking(A, S)), twoSlots.activeBookingOf(S));
        assertEquals(new BookingOutcome.Booked(new Booking(B, S2)), outcome);
        assertEquals(Optional.of(new Booking(B, S2)), twoSlots.activeBookingOf(S2));
    }

    @Test
    void aSlotNeverHoldsMoreThanOneBookingWhateverTheSequence() {
        PatientId c = new PatientId("patient-c");
        List<Attempt> attempts = List.of(
                new Attempt(B, S), new Attempt(B, S), new Attempt(A, S), new Attempt(c, S),
                new Attempt(A, S2), new Attempt(c, S2), new Attempt(B, S2), new Attempt(A, S3),
                new Attempt(A, S3), new Attempt(c, S3), new Attempt(B, S3), new Attempt(c, S));
        BookingStore all = new InMemoryBookingStore(
                List.of(new Slot(S, DOCTOR), new Slot(S2, DOCTOR), new Slot(S3, DOCTOR)));
        BookSlot book = new BookSlot(all);
        Map<SlotId, PatientId> firstSuccess = new HashMap<>();

        for (Attempt attempt : attempts) {
            BookingOutcome outcome = book.book(attempt.patient(), attempt.slot());
            if (outcome instanceof BookingOutcome.Booked) {
                assertNull(firstSuccess.putIfAbsent(attempt.slot(), attempt.patient()),
                        "a second booking succeeded on " + attempt.slot());
            } else {
                assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), outcome);
                assertTrue(firstSuccess.containsKey(attempt.slot()));
            }
        }

        assertEquals(Map.of(S, B, S2, A, S3, A), firstSuccess);
        firstSuccess.forEach((slot, patient) ->
                assertEquals(Optional.of(new Booking(patient, slot)), all.activeBookingOf(slot)));
    }

    private record Attempt(PatientId patient, SlotId slot) {
    }
}
