# ADR-0003: Python application API with an explicit role

Status: accepted

## Context
Public contract of the register: how the manager acts on it, and where requirement 8 (only the manager writes) is checked.

## Decision
The application ring exposes use cases as plain Python callables (one per action: register lot, register space, list, change owner, change space number, remove space). Each write use case takes the actor's role as an explicit argument and refuses any role other than manager. A refusal is a named, typed reason returned or raised as a documented application error; the register is unchanged. No UI or command line for now.

## Consequences
- The role check lives in `application`, tested without storage.
- Public types (use case signatures, role, refusal reasons) become a contract; changing them is a breaking change.
- A later CLI or UI is a new adapter in `infrastructure` over the same use cases.
