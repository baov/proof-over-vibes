package io.example.medical;

import io.example.medical.domain.TimeRange;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class TimeRangeTest {

    private static final Instant START = Instant.parse("2030-01-01T10:00:00Z");

    @Test
    void aRangeEndingNotAfterItsStartIsRejected() {
        assertDoesNotThrow(() -> new TimeRange(START, START.plusNanos(1)), "one nanosecond long is valid");
        assertThrows(IllegalArgumentException.class, () -> new TimeRange(START, START), "zero length");
        assertThrows(IllegalArgumentException.class, () -> new TimeRange(START, START.minusNanos(1)), "inverted");
        assertThrows(IllegalArgumentException.class, () -> new TimeRange(null, START), "absent start");
        assertThrows(IllegalArgumentException.class, () -> new TimeRange(START, null), "absent end");
    }
}
