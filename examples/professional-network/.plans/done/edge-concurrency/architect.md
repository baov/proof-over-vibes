---
role: architect
status: done
structure: decided
reasons:
  - "Serialization is inside the module (one in-process FIFO queue around every public operation): cheap to reverse, no dependency, no change of the store port, no change of the public contract."
  - "ADR-0002 written, accepted: the module is a single process instance; a multi-instance deployment or a shared store needs a new ADR and conditional writes."
  - "Nothing is escalated: no external dependency, no lock service, no store-contract change, ADR-0001 not superseded."
---

# Architect: simultaneous operations

## Cause

Each use case does read, decide, write across awaits. Two calls interleave at those awaits even in one process: both send checks see no reverse request; accept reads "pending" while withdraw writes. The in-memory `saveAccepted` also awaits between the request write and the connection write, so a read can see an accepted request without its connection (requirement 4).

## Decided (cheap to reverse, ADR-0002 records the lasting part)

- **Serialization.** One FIFO queue per `createConnections` instance. The five writes (send, accept, decline, withdraw, erase) and the two reads (pair state, pending list) all run through it, so a read never sees a half-finished operation. Winner = arrival order, no priority (requirement 6).
- **Where.** `infrastructure/serial-queue.ts` (plain promise chain, no dependency), applied in `index.ts` around each use call. The use cases stay unchanged and are not aware of it. A failed or throwing operation must not block the next one.
- **Atomic scope.** The whole use case (rules check plus write). Inside the store, `saveAccepted` stays one atomic write (already the port's promise).
- **Processes (PRD unknown 2).** One instance only. Stated in ADR-0002.
- **Erase during an operation (PRD unknown 4).** Erase is one more queued operation, so the outcome is erase-first or erase-last. No new business rule is needed; the Planner may add a test, and the Product Owner may record it as a decision if wanted.
- **Rejected:** lock per pair (needs a read to learn the pair from a request id, erase needs all pairs, gain is speed, out of scope); conditional writes in the port now; external lock service.

## Sides of the contract

- Public contract (`Connections` in `index.ts`): unchanged, same signatures and results. Nothing broken.
- Store port (internal): unchanged. Not a public contract today. I did not add conditional writes because that would bind every future store for a deployment that does not exist; ADR-0002 states the day it becomes necessary.
- `index.ts` and the infrastructure are sensitive zones: human review before merge.

## For the next roles

- **Planner.** Tests go through `createConnections` with `Promise.all([...])`: the interleaving already happens at microtask level, so the race reproduces deterministically without the queue and must fail without it. One test per requirement 1 to 5 (both orders for 3 and 5), plus erase against another operation, plus a failing operation not blocking the queue.
- **Harness engineer.** Candidate invariant from ADR-0002: every method built in `createConnections` goes through the queue. The queue is in `infrastructure`, outside the mutation scope (domain and application): tests must cover it by behavior.
- INV-001 to INV-008: no impact expected.

## Debt

None flagged. Single-writer throughput is a known limit, recorded in ADR-0002.
