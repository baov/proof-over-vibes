package io.example.medical.domain;

import java.time.Instant;

/** The stretch of time a slot covers. Valid by construction: the end is strictly after the start (D-27, D-29). */
public record TimeRange(Instant start, Instant end) {

    public TimeRange {
        if (start == null || end == null) {
            throw new IllegalArgumentException("a time range needs a start and an end");
        }
        if (!end.isAfter(start)) {
            throw new IllegalArgumentException("a time range must end after it starts: " + start + " .. " + end);
        }
    }

    /** Two ranges overlap when they share a stretch of time; back to back ranges do not (D-20). */
    public boolean overlaps(TimeRange other) {
        return start.isBefore(other.end) && other.start.isBefore(end);
    }
}
