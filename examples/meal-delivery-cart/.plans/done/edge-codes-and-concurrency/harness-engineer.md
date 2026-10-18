---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer: INV-007

- ADR-0004 turned into INV-007 (warn, active): every field of `domain` and `application` is final. ArchUnit rule `coreFieldsAreFinal` in `ArchitectureTest`, run by `check_layers.py` (severity map, `--explain`, remediation, same output contract); `run_all.sh` labels updated.
- Self-test: two tests in `ArchitectureTest` run the rule on throwaway fixtures (flags `var`, `lateinit var`, mutable `object` field; passes `val`, `const`, `object`, companion). Verified that a failing self-test makes `check_layers.py` exit 1.
- Known limit stated in `invariants.md`: the content of a final field (mutable list, `lazy`) is not seen; no ban on `synchronized`.
- ADR-0004 now has "Associated executable invariants: INV-007, INV-004".
- `bash tools/harness/run_all.sh` : exit 0 on the current code (no existing violation, nothing to report). No multiple-choice question was needed.
