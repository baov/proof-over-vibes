---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer: offer a space (F2.1)

## TL;DR
INV-008 added (warn), three sensitive zones declared. The existing code passes; harness and selftests green.

## Added
- `tools/harness/check_clock.py` (INV-008): scans `domain/` and `application/` for any call or reference to the system clock (`date.today`, `datetime.now/today/utcnow`, `time.time/time_ns/localtime/gmtime/ctime`), alias-aware. Remediation message, `--explain`, missing rings or files skipped. Wired in `run_all.sh`, listed in `docs/technical/invariants.md`.
- 4 selftests in `tools/harness/selftest/test_harness.py` (violations, clean cases, missing code, `--explain`). 14 tests OK.
- Sensitive zones: owner role check in `offer_use_cases.py`; offers write path (JSON offers adapter); fail-closed `OfferCheck` call in `remove_space` and `change_space_number`.
- Check on the current code: `check_clock.py` exit 0; `run_all.sh` exit 0.

## Not enforceable by the harness
- Fail-closed (no `except` around the `OfferCheck` call) and the owner-only check: semantic, left to tests, mutation score (INV-007) and the human review of the sensitive zones.
- Dynamic clock access (`getattr`, `importlib`) is invisible; `infrastructure` is deliberately free to read the clock.
- Concurrent offers (overlap race) is a stated limit of ADR-0004, not checkable.
