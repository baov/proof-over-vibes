# PRD: F5.1-F5.3 Legal rules, as a configurable skeleton

Epic E5. Picked by the human (backlog item 7) as a **skeleton**: the mechanism to configure and evaluate rules, with **no legal text encoded**. Every statement about French law in this document is *unverified*; none is asserted. Decisions Q1 to Q3 are answered by the human (see the end).

## Problem
The vision promises that the rules of the building and of the law are applied by default, but the human has not supplied the list of rules, and rentals (E2) do not exist yet. Without a place to put rules and a way to check a rental against them, E5 cannot start; with invented rules, the product would state law nobody verified.

## Goal and success
Goal: the manager can record rules as parameters, and any rental proposal can be checked against them, with the answer naming the rule that refused. Success: with a rule configured, a proposal that breaks it is refused with that rule's name and the observed value; with none, nothing changes; the product ships with no rule.

## Users and use
Manager (configures). Any role may ask for a check (a check changes nothing, as the listing in D-17). Main path: the manager adds a rule, submits a rental proposal, reads the answer, then changes or removes the rule.

## What is a rule, and what is evaluated

- **Rule**: a named condition with one parameter, set by the manager. It says nothing about law: the manager may note where it comes from (free text, not checked by the product).
- **Evaluated input, the smallest honest one: a rental proposal.** Rentals do not exist, so the check takes a record that stands for one: space number, resident name, start date, end date, and whether owner consent is recorded (yes / no). No price, no payment (out of scope). The record is not stored by this feature; when E2 builds real rentals, the proposal is replaced by the rental and the rules stay.
- **Answer**: `allowed`, or `refused` with every rule that refused (rule name, kind, parameter, observed value).

## Scope

- In: configure rules, list them, check a proposal against them, the answer.
- Out: any real legal content (lease form, duration, notice, consent as the law states them, taxes); offers, rentals, their storage and lifecycle (E2); notice and termination (F5.3 needs ending a rental, F2.4); price and money (E4); several co-ownerships (E6); accounts and login; deciding on a request (E3: the answer is advice to the manager, it does not approve or refuse a rental).
- Later stages, not this one: the human supplies the real rules and loads them; the check is wired to the real rental request (F2.2) and to the manager's decision (F3.1); notice rules once rentals can end.

## Requirements

Configuration
1. A rule has a name unique in the co-ownership (compared ignoring case and surrounding spaces, as D-11), a kind, a parameter, and an optional source note.
2. Two kinds exist: *duration bounds* (a minimum and/or a maximum number of days, at least one) and *owner consent required* (no parameter). Duration is counted in whole calendar days, start and end dates both included (a product convention, not a legal one).
3. The manager can add a rule, change its parameter or source note, remove it, and list all rules. Anyone can list.
4. Only the manager can add, change or remove a rule; any other role is refused as manager-only, before any validation (D-16, D-18).
5. These are refused with a named reason and leave the rules unchanged: blank name, duplicate name, unknown kind, a missing or non-positive number of days, a minimum above the maximum.
6. Rules survive a restart.
7. A new installation has no rule and no legal content in its data or its texts.

Evaluation
8. A check takes a proposal; any role may make it. It reads the register and the rules and changes neither.
9. A proposal with a blank resident name, an unknown space number (not in the register of F1.2), or an end date before the start date is refused as invalid; no rule is evaluated and the answer is not a rule verdict.
10. Every configured rule is evaluated; the proposal is `allowed` only if none refuses.
11. A `refused` answer lists every refusing rule with its name, kind, parameter and the observed value (for example, 400 days against a maximum of 365). The order of the list is the order of rule names, so that the answer does not depend on configuration order.
12. An `allowed` answer states how many rules were evaluated, so that "all rules passed" differs from "no rule applied".
13. With no rule configured, a valid proposal is `allowed`, and the answer says that no rule was evaluated.
14. The same rules and the same proposal always give the same answer.
15. If the rules cannot be read (corrupt or malformed storage), the check ends with a named "rules unreadable" error and never with `allowed`; the same on any write, and the stored rules are never overwritten (as D-19).

## Security and performance targets

- Security: who may do what is requirements 4 and 8 (manager-only writes, checks read-only); requirement 15 is the fail-closed rule: a broken rule store must not let a rental through. No personal data beyond the resident name already in the register's world.
- Performance: none stated. No volume or response time was given by the human or the market watch, and none is invented; see the open questions.

## Dependencies

- F1.2 register (a space number must exist): built.
- From the human, later and not blocking this feature: the list of real rules, with sources.
- E2 rentals and F2.4 end of rental: absent; the proposal record replaces them for now. The `no rental` port of F1.2 is untouched.

## Risks and open questions

- Assumption: two kinds are enough to prove the mechanism. If the real French rules (*unverified*: duration, consent by a person or a body other than the owner, form of the lease, notice) need other kinds or conditions, the list of kinds grows; the skeleton does not prove that the vision's bet "rules can be encoded as stated in the law" holds.
- The proposal record is a stand-in; its fields may differ from those of the real rental (F2.2).
- For the architect: where rules are stored (with the register or apart), how a kind is represented so a new one is added without touching the others, the shape of the answer as a public type (breaking-change cost, as ADR-0003), how the proposal gives way to the E2 rental, date and time-zone handling for durations, concurrent edits of rules, evolution of the stored format, expected number of rules and checks (performance target unknown).

## Decisions of the human

- Q1: a closed list of two rule kinds, duration bounds and owner consent required.
- Q2: every rule is evaluated; refused if any refuses; every refusing rule is listed.
- Q3: with no rule configured, a valid proposal is allowed, and the answer says no rule was evaluated.
- The manager alone configures (D-3, D-4 reused); checks are open to every role.

## Questions for the human

None open. The rental proposal stays a stand-in and a bet: the Product Owner re-checks its fields against the stories, and E2 replaces it.
