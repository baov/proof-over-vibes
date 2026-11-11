# ADR-0001: Clean architecture

Status: accepted

## Context
Empty project; the register has real rules (uniqueness, one owner per lot, role check, a refusal changes nothing). Chosen by the human among hexagonal, modular monolith, n-tier and clean architecture.

## Decision
Clean architecture, in one package `copro_parking` under `src/`, with three rings:

- `copro_parking/domain`: entities and value objects (`Lot`, `ParkingSpace`, `Owner`, the register rules) and domain errors.
- `copro_parking/application`: use cases, the role check, the output types (results, named refusals) and the ports (repository, rental check) as abstract interfaces.
- `copro_parking/infrastructure`: adapters that implement the ports (JSON file repository, "no rental" check). Entry points and wiring live here too.

## Dependency rule (for the harness)
Imports point inward only:
- `domain` imports nothing from `application` or `infrastructure`, and only the standard library (no `json`, `os`, `pathlib`, `sqlite3`, `io`).
- `application` imports `domain` and the standard library; never `infrastructure`.
- `infrastructure` may import `application` and `domain`.
- `tests` may import any ring.
Checkable by scanning `import` / `from` lines of the files of each ring.

## Consequences
More files than n-tier for a small feature; the domain stays testable with `unittest` alone and no file system.
