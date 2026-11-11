---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green; S1 AC1-AC10 verified by probe; no blocking finding, 2 open majors (undecided behaviors)
  - escalate: the diff touches the sensitive zones (manager-only check, JSON atomic write); the human confirms
severity: major
open_majors:
  - "Corrupt or malformed store file: load raises a raw JSONDecodeError / KeyError, no documented refusal or recovery (no decision, no test-case)"
  - "Sort is plain casefold text: 'P10' lists before 'P2'; no decision says natural order is not wanted (D-13 only says sorted)"
---

# Review 1: S1 Register lots and spaces and list them

Skill `premerge-review`, criticality critical (domain, role check, persisted format). No git diff: the whole of `src/`, `tests/`, the test-cases and `tools/` was reviewed.

## Gauntlet (run by me)
- `python3 -m unittest discover -s tests`: 27 OK.
- `bash tools/harness/run_all.sh`: exit 0, 12/12 test-cases covered, 0 orphan tests.
- Mutation `--scope critical`: 84.8% (28/33). `--scope diff` has nothing to mutate (no commit), so critical was used. The 5 survivors are equivalent: `frozen=True` -> `False` on 4 dataclasses, `indent=2` -> `3`. Agreed with the developer.

## Probes (own script, real JSON repository)
- AC1/AC2: `' A12 '` registers as `A12`; `a12` -> `DuplicateLotRefused`. AC3/AC7c: blank or `None` owner, blank identifier -> `BlankValueRefused`.
- AC4-AC6: `' p1 '` on lot `a12` ok, `P1` -> `DuplicateSpaceRefused`, unknown lot -> `UnknownLotRefused`, blank number or blank lot -> `BlankValueRefused`. Unicode `ß` / `SS` count as duplicates (casefold).
- AC8 and D-16: Owner role, the string `"manager"` and `None`, all with blank values, give `ManagerOnly` before any validation.
- AC7/AC7b, D-13, D-15: `[A12 (Dupont): p1, P2], [a2 (Z): p10]`: trimmed as typed, case kept, lots then spaces sorted, a lot without space listed (covered by tests).
- AC9: after two refusals the file is byte-identical, only `r.json` in the folder (no leftover temp file). AC10: a fresh repository reads the same listing.
- Atomic write: temp file in the same folder + `os.replace`, cleanup on error; a refused first write creates no file. A crash between write and replace is invisible to the tests (declared limit of the mutation tool); no fsync before the replace.

## Findings
- **major** Malformed store: a corrupt file or a missing key surfaces as `JSONDecodeError`/`KeyError` from `list_register` (probed). Nothing decides what the manager should see. Open.
- **major** Natural order: `p10` sorts before `p2`. D-13 says "sorted", not how; a consumer will notice on a real building. Open.
- **minor** `os.replace` without `fsync`: a power cut can leave an empty file on some systems. Not tested; acceptable for the demo, worth a line in ADR-0002.
- **minor** Process: production code written before the tests (developer-1.md). Mitigated by the 84.8% mutation score and by behavior-level tests; no defect found because of it.
- **minor** The developer's unlisted behaviors (three roles, open listing) are now settled by D-17/D-18; `frozen=True` cannot be tested away and is fine.

## Compliance
ADR-0001 layers respected (harness green), ADR-0002 JSON whole-file + atomic write, ADR-0003 explicit role as first check of every write. Test-cases match the stories; vocabulary consistent with the decision log.

Verdict: GO, status `escalate` for the human because of the two sensitive zones.
