---
role: architect
status: done
structure: decided
reasons: []
---

# Architect: register lots and spaces

Human's answers: clean architecture, JSON file, Python application API with an explicit role argument.

- ADR-0001 clean architecture, with the dependency rule: `domain` imports only the standard library (no I/O modules) and nothing inward-out; `application` imports `domain` only; `infrastructure` imports the others.
- ADR-0002 JSON file: no constraint from the store, so uniqueness and integrity live in the domain and use cases; atomic write (temp file + `os.replace`); single process.
- ADR-0003 application API: role passed to every write use case, manager only, named refusals.
- Cheap decisions: history of owner changes and concurrent edits out of scope; the rental check of requirement 7 is a port answering "no rental" until E3.
- Model: `Register` aggregate holding `Lot` and `ParkingSpace`; owner is a name value object.

ADRs: `docs/technical/adr/0001-clean-architecture.md`, `0002-json-file-persistence.md`, `0003-application-api-with-explicit-role.md`.
