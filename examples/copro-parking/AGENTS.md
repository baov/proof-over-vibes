# AGENTS.md

Python 3.14, tests with the standard library `unittest` (no dependency can be installed on this machine): `python3 -m unittest discover -s tests`.

## Harness

Rules made executable in `tools/harness/`; list and statuses in [docs/technical/invariants.md](docs/technical/invariants.md).

- Before any commit: `bash tools/harness/run_all.sh` (messages carry the remediation; `--explain` on a script describes its rule).
- Mutation testing, by hand: `python3 tools/harness/run_mutation.py --scope diff`. A survivor gets a test for the unprotected behavior, never a lowered threshold.
- Self-tests of the scripts: `python3 -m unittest discover -s tools/harness/selftest`.
