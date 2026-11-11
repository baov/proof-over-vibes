# ADR-0002: JSON file persistence

Status: accepted

## Context
The register must survive a restart. Offline, no dependency, standard library only. Chosen by the human over SQLite and in-memory.

## Decision
The repository adapter stores the whole register in one JSON file (stdlib `json`), in `infrastructure`. The use cases see only the repository port.

## Consequences
- The store enforces no constraint: uniqueness of lot id and space number, one owner per lot, and a space on a known lot are enforced in the domain and use cases, never delegated to the file.
- Writes are atomic: write a temporary file in the same folder, then `os.replace` it onto the target; a failed write or a refusal leaves the file unchanged (requirement 9).
- Single process, single manager: no locking; concurrent edits are unsupported and out of scope.
- The file format is a contract of the adapter only; changing it needs a migration of existing files.
- A rewrite of the whole file at each change is acceptable at this size.
