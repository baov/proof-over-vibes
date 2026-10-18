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
import io.example.medical.domain.TimeRange;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class BookSlotTest {

    private static final PractitionerId DOCTOR = new PractitionerId("dr-martin");
    private static final PractitionerId OTHER_DOCTOR = new PractitionerId("dr-durand");
    private static final SlotId S = new SlotId("slot-1");
    private static final SlotId S2 = new SlotId("slot-2");
    private static final SlotId S3 = new SlotId("slot-3");
    private static final PatientId A = new PatientId("patient-a");
    private static final PatientId B = new PatientId("patient-b");

    private static final Instant NOW = Instant.parse("2030-01-01T09:00:00Z");
    private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);

    private final BookingStore store = new InMemoryBookingStore(List.of(slot(S, 1)));
    private final BookSlot bookSlot = new BookSlot(store, CLOCK);

    /** A slot lasting from startMinutes to endMinutes after NOW. */
    private static Slot slotAt(SlotId id, PractitionerId practitioner, int startMinutes, int endMinutes) {
        return new Slot(id, practitioner, new TimeRange(
                NOW.plus(Duration.ofMinutes(startMinutes)), NOW.plus(Duration.ofMinutes(endMinutes))));
    }

    private static Slot slotStartingAt(SlotId id, Instant start) {
        return new Slot(id, DOCTOR, new TimeRange(start, start.plus(Duration.ofMinutes(30))));
    }

    /** A half-hour slot of the doctor starting the given number of hours after NOW. */
    private static Slot slot(SlotId id, int hoursAfterNow) {
        return slotStartingAt(id, NOW.plus(Duration.ofHours(hoursAfterNow)));
    }

    @Test
    void refusesAnUnknownSlot() {
        SlotId unknown = new SlotId("no-such-slot");

        BookingOutcome first = bookSlot.book(A, unknown);
        BookingOutcome second = bookSlot.book(A, unknown);

        assertEquals(new BookingOutcome.Refused(RefusalReason.UNKNOWN_SLOT), first);
        assertEquals(first, second);
        assertEquals(Optional.empty(), store.activeBookingOf(unknown));
        assertEquals(Optional.empty(), store.activeBookingOf(S));
    }

    @Test
    void refusesASlotStartingBeforeNow() {
        SlotId justBefore = new SlotId("just-before");
        SlotId farBefore = new SlotId("far-before");
        BookingStore past = new InMemoryBookingStore(List.of(
                slotStartingAt(justBefore, NOW.minusNanos(1)), slotStartingAt(farBefore, NOW.minus(Duration.ofHours(5)))));
        BookSlot book = new BookSlot(past, CLOCK);

        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, justBefore));
        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, farBefore));
        assertEquals(Optional.empty(), past.activeBookingOf(justBefore));
        assertEquals(Optional.empty(), past.activeBookingOf(farBefore));
    }

    @Test
    void booksASlotStartingExactlyNow() {
        SlotId atNow = new SlotId("at-now");
        SlotId justAfter = new SlotId("just-after");
        BookingStore store = new InMemoryBookingStore(List.of(
                slotStartingAt(atNow, NOW), slotStartingAt(justAfter, NOW.plusNanos(1))));
        BookSlot book = new BookSlot(store, CLOCK);

        assertEquals(new BookingOutcome.Booked(new Booking(A, atNow)), book.book(A, atNow));
        assertEquals(new BookingOutcome.Booked(new Booking(B, justAfter)), book.book(B, justAfter));
    }

    @Test
    void aPatientHoldsSeveralSlotsThatDoNotOverlap() {
        Slot first = slotAt(S, DOCTOR, 60, 90);
        Slot sameDoctor = slotAt(S2, DOCTOR, 120, 150);
        Slot otherDoctor = slotAt(S3, OTHER_DOCTOR, 180, 210);
        BookingStore all = new InMemoryBookingStore(List.of(first, sameDoctor, otherDoctor));
        BookSlot book = new BookSlot(all, CLOCK);

        assertEquals(new BookingOutcome.Booked(new Booking(A, S)), book.book(A, S));
        assertEquals(new BookingOutcome.Booked(new Booking(A, S2)), book.book(A, S2));
        assertEquals(new BookingOutcome.Booked(new Booking(A, S3)), book.book(A, S3));

        assertEquals(Set.of(first, sameDoctor, otherDoctor), Set.copyOf(all.slotsHeldBy(A)));
    }

    @Test
    void refusesASlotOverlappingOneThePatientHolds() {
        Slot held = slotAt(S, DOCTOR, 60, 120);
        Slot clashing = slotAt(S2, OTHER_DOCTOR, 90, 150);

        BookingStore heldFirst = new InMemoryBookingStore(List.of(held, clashing));
        BookSlot book = new BookSlot(heldFirst, CLOCK);
        book.book(A, S);
        assertEquals(new BookingOutcome.Refused(RefusalReason.OVERLAPPING), book.book(A, S2));
        assertEquals(List.of(held), heldFirst.slotsHeldBy(A));
        assertEquals(Optional.empty(), heldFirst.activeBookingOf(S2));
        assertEquals(new BookingOutcome.Booked(new Booking(B, S2)), book.book(B, S2), "the clash is per patient");

        BookingStore clashingFirst = new InMemoryBookingStore(List.of(held, clashing));
        BookSlot otherOrder = new BookSlot(clashingFirst, CLOCK);
        otherOrder.book(A, S2);
        assertEquals(new BookingOutcome.Refused(RefusalReason.OVERLAPPING), otherOrder.book(A, S));
    }

    @Test
    void overlappingSlotsOfOnePractitionerCanBeBookedByDifferentPatients() {
        BookingStore both = new InMemoryBookingStore(List.of(slotAt(S, DOCTOR, 60, 120), slotAt(S2, DOCTOR, 90, 150)));
        BookSlot book = new BookSlot(both, CLOCK);

        assertEquals(new BookingOutcome.Booked(new Booking(A, S)), book.book(A, S));
        assertEquals(new BookingOutcome.Booked(new Booking(B, S2)), book.book(B, S2));
    }

    @Test
    void overlapMeansSharingAStretchOfTime() {
        Slot held = slotAt(S, DOCTOR, 60, 120);
        Instant heldStart = held.range().start();
        Instant heldEnd = held.range().end();
        Map<String, Slot> shapes = new LinkedHashMap<>();
        shapes.put("starts inside and ends after", slotAt(S2, OTHER_DOCTOR, 90, 150));
        shapes.put("starts before and ends inside", slotAt(S2, OTHER_DOCTOR, 30, 90));
        shapes.put("contains the held slot", slotAt(S2, OTHER_DOCTOR, 30, 150));
        shapes.put("is contained in the held slot", slotAt(S2, OTHER_DOCTOR, 70, 100));
        shapes.put("has the same range", slotAt(S2, OTHER_DOCTOR, 60, 120));
        shapes.put("overlaps by one nanosecond at the end",
                new Slot(S2, OTHER_DOCTOR, new TimeRange(heldEnd.minusNanos(1), heldEnd.plusSeconds(60))));
        shapes.put("overlaps by one nanosecond at the start",
                new Slot(S2, OTHER_DOCTOR, new TimeRange(heldStart.minusSeconds(60), heldStart.plusNanos(1))));

        shapes.forEach((name, candidate) -> {
            BookingStore store = new InMemoryBookingStore(List.of(held, candidate));
            BookSlot book = new BookSlot(store, CLOCK);
            book.book(A, S);

            assertEquals(new BookingOutcome.Refused(RefusalReason.OVERLAPPING), book.book(A, S2),
                    "a slot that " + name + " must be refused as overlapping");
        });
    }

    @Test
    void backToBackSlotsDoNotOverlap() {
        Slot held = slotAt(S, DOCTOR, 60, 120);
        Slot after = slotAt(S2, OTHER_DOCTOR, 120, 180);
        Slot before = slotAt(S3, OTHER_DOCTOR, 0, 60);
        BookingStore all = new InMemoryBookingStore(List.of(held, after, before));
        BookSlot book = new BookSlot(all, CLOCK);

        book.book(A, S);

        assertEquals(new BookingOutcome.Booked(new Booking(A, S2)), book.book(A, S2));
        assertEquals(new BookingOutcome.Booked(new Booking(A, S3)), book.book(A, S3));
    }

    @Test
    void anUnhonourableRefusalChangesNothing() {
        SlotId held = new SlotId("held");
        SlotId heldByB = new SlotId("held-by-b");
        SlotId clashing = new SlotId("clashing");
        SlotId past = new SlotId("past");
        BookingStore store = new InMemoryBookingStore(List.of(
                slotAt(held, DOCTOR, 60, 120), slotAt(heldByB, DOCTOR, 200, 260),
                slotAt(clashing, OTHER_DOCTOR, 90, 150), slotAt(past, DOCTOR, -60, -30)));
        BookSlot book = new BookSlot(store, CLOCK);
        book.book(A, held);
        book.book(B, heldByB);
        Map<String, Object> before = snapshot(store, held, heldByB, clashing, past);

        assertEquals(new BookingOutcome.Refused(RefusalReason.UNKNOWN_SLOT), book.book(A, new SlotId("absent")));
        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, past));
        assertEquals(new BookingOutcome.Refused(RefusalReason.OVERLAPPING), book.book(A, clashing));

        assertEquals(before, snapshot(store, held, heldByB, clashing, past));
    }

    @Test
    void reportsUnknownBeforeAnyOtherRefusal() {
        BookingStore store = new InMemoryBookingStore(List.of(slotAt(S, DOCTOR, 0, 30), slotAt(S2, DOCTOR, 10, 40)));
        new BookSlot(store, CLOCK).book(A, S);
        BookSlot later = new BookSlot(store, Clock.fixed(NOW.plus(Duration.ofHours(5)), ZoneOffset.UTC));

        assertEquals(new BookingOutcome.Refused(RefusalReason.UNKNOWN_SLOT), later.book(A, new SlotId("absent")));
        assertEquals(Optional.of(new Booking(A, S)), store.activeBookingOf(S));
        assertEquals(Optional.empty(), store.activeBookingOf(S2));
    }

    @Test
    void reportsPastBeforeTakenAndOverlap() {
        SlotId pastTakenOverlapping = new SlotId("past-taken-overlapping");
        SlotId pastTaken = new SlotId("past-taken");
        SlotId pastOverlapping = new SlotId("past-overlapping");
        SlotId heldByA = new SlotId("held-by-a");
        BookingStore store = new InMemoryBookingStore(List.of(
                slotAt(heldByA, DOCTOR, -90, -45),
                slotAt(pastTakenOverlapping, OTHER_DOCTOR, -60, -30),
                slotAt(pastTaken, DOCTOR, -20, -10),
                slotAt(pastOverlapping, OTHER_DOCTOR, -80, -50)));
        BookSlot whenSlotsWereFuture = new BookSlot(store, Clock.fixed(NOW.minus(Duration.ofHours(3)), ZoneOffset.UTC));
        whenSlotsWereFuture.book(A, heldByA);
        whenSlotsWereFuture.book(B, pastTakenOverlapping);
        whenSlotsWereFuture.book(B, pastTaken);
        BookSlot book = new BookSlot(store, CLOCK);

        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, pastTakenOverlapping));
        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, pastTaken));
        assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), book.book(A, pastOverlapping));
    }

    @Test
    void reportsTakenBeforeOverlap() {
        SlotId heldByA = new SlotId("held-by-a");
        SlotId takenAndOverlapping = new SlotId("taken-and-overlapping");
        BookingStore store = new InMemoryBookingStore(List.of(
                slotAt(heldByA, DOCTOR, 60, 120), slotAt(takenAndOverlapping, OTHER_DOCTOR, 90, 150)));
        BookSlot book = new BookSlot(store, CLOCK);
        book.book(A, heldByA);
        book.book(B, takenAndOverlapping);

        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), book.book(A, takenAndOverlapping));
        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), book.book(A, heldByA),
                "a slot the patient holds overlaps itself, and is still reported as taken");
    }

    private static Map<String, Object> snapshot(BookingStore store, SlotId... slots) {
        Map<String, Object> state = new LinkedHashMap<>();
        for (SlotId slot : slots) {
            state.put(slot.value(), store.activeBookingOf(slot));
        }
        state.put("held by A", Set.copyOf(store.slotsHeldBy(A)));
        state.put("held by B", Set.copyOf(store.slotsHeldBy(B)));
        return state;
    }

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

        assertEquals(Optional.of(new Booking(A, S)), store.activeBookingOf(S));
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
        BookingStore twoSlots = new InMemoryBookingStore(List.of(slot(S, 1), slot(S2, 2)));
        BookSlot book = new BookSlot(twoSlots, CLOCK);

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
                List.of(slot(S, 1), slot(S2, 2), slot(S3, 3)));
        BookSlot book = new BookSlot(all, CLOCK);
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
