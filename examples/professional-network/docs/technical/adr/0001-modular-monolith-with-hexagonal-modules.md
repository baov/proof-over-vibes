# ADR-0001: Modular monolith, each module hexagonal inside

Status: accepted (answered by delegate, recommended option)

## Context

The project is empty. Stack fixed by the human: TypeScript, Node 22, npm, Vitest. The first feature, connection requests, is a small domain core with real rules between members. Profiles, posts and the connections feed, and data rights (erasure, export) follow. The vision's differentiator is "posts readable by connections only", so every later module will ask "are these two members connected?", and erasure will touch every module.

## Decision

One deployable and one repository, cut by business module under `src/` (`connections` first; `profiles`, `posts`, `data-rights` later). Each module is hexagonal: `domain`, `application`, `infrastructure`.

Considered and rejected: single-module hexagonal (cut by module becomes a costly refactoring once profiles and posts arrive), clean architecture (ceremony with no behavior to carry for a core this small), n-tier (rules end up written against storage).

## Dependency rule

- `domain` imports nothing outside its own module (no framework, no storage, no Node API).
- `application` imports the `domain` of the same module only.
- `infrastructure` (adapters) imports the `application` and `domain` of the same module.
- One module reaches another only through that module's public entry point (`src/<module>/index.ts`); no deep imports into another module's folders.

Associated executable invariants: INV-001 to INV-004 (docs/technical/invariants.md).

## Consequences

- Domain rules are tested in memory with no storage; a storage product stays a separate decision.
- Cross-module needs (the feed asking whether two members are connected, erasure) go through the public entry point.
- The harness engineer turns the dependency rule into an invariant.
