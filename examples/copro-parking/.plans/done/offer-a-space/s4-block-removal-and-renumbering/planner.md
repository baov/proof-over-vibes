---
role: planner
status: done
reasons: []
---

# Planner: S4 A space with an open offer cannot be removed or renumbered

Q1 A, Q2 A, Q3 A taken by delegate and recorded as D-69, D-70, D-71 in `docs/business/decisions.md`; `plan.md` is final. The questions and options are kept below for the record. Two public signatures change (`remove_space`, `change_space_number`); every caller is listed in step 3 and 4 of the plan (all in `tests/`, none in `src/`).

Not a question (decided by documents): order manager, unknown space, rental, offer (architect); an offer is not a rental (AC3, D-50); ended offers do not block (D-52); unreadable offers stop the write with `OffersUnreadable`, nothing saved (D-19, invariants); no default for the new `offers` argument.

## Q1. Orphan offers already in a stored file (written by S1 to S3, space no longer registered): what does S4 do about them?
From now on no use case can create one. Today they are skipped by the listing (D-62) and unknown for withdrawal (D-65); if the number is registered again they come back under the new lot.
- A. Nothing to the data. They keep D-62 and D-65; if the number is registered again the offer counts as an open offer (removal and renumbering refused) until its new owner withdraws it (S3 allows it). Documented limit, tested. **Recommended.** S1 to S3 were never released without S4, so no real file holds one; no new operation.
- B. As A, plus a manager use case that deletes every offer whose space is not registered. Cleans old files, but it is a new public operation, a new write path in a sensitive zone and a story of its own.
- C. An offer whose space is not registered makes the offers file unreadable (`OffersUnreadable`). Loud, but D-62 rejected it: it locks the feature.

## Q2. Withdrawing with an unreadable register: which error for a number that is not an open offer? (M2 of review 08; also the order of blank offerer vs bad number, m1)
Today the offers are read first: an unknown, ended or withdrawn number gives "unknown offer", an open number gives the store error.
- A. A store error wins: every valid-input withdrawal reads both stores before looking the offer up; unreadable register gives `StoreUnreadable` whatever the number, both unreadable gives `OffersUnreadable`. Blank offerer is reported before a bad number (invalid input, same rank, as tested today). **Recommended.** One answer per failing store, and a stranger learns nothing about which numbers are open while the register is broken.
- B. Unknown offer wins: keep the code, pin it with a test. The register is read only for a number that is open; the answer for a broken register depends on the number.

## Q3. Renumbering a space that has an open offer: the edges
- A. Any change of number is refused as "space offered", including a same-value or case-only change (`P1` to `p1`); the refusal comes after the register's own refusals (blank new number, unknown space, duplicate number), as for removal. **Recommended.** The offer keeps the number text it was made on, and the overlap check compares that text exactly, so a case change would silently weaken it.
- B. A same-value or case-only change is accepted (the offer still finds its space ignoring case); other changes are refused. Needs the overlap check changed to ignore case, outside this story.
- C. As A, but "space offered" wins over duplicate number and blank new number (only the role and the unknown space come first).

## Output
- `plan.md` (7 steps, section 4 gives each behavior with its test boundary), applicable invariants INV-001 to INV-008 noted.
- Sensitive zones for the human: role check and fail-closed offer call in `remove_space` and `change_space_number`; `offer_use_cases.py` (step 5). The offers write path is not touched.
- Notes for others: `OfferBook.add` compares space numbers exactly (latent for pre-S4 files with a case-only correction); `invariants.md` still says the fail-closed zone is "Not written yet".
