# 0017: CLI integration tests without inline coverage harnessing

Date: 2025-10-09
Status: Accepted

## Context

While implementing exit-code regression tests for the Typer-based CLI we briefly
experimented with wrapping each subprocess invocation in `coverage run` so that
integration scenarios would feed coverage totals. The approach required
threading repository-specific environment variables, a bespoke rcfile, and
special-case hooks inside the tests themselves. Review feedback highlighted that
this complexity made the tests harder to follow and duplicated configuration
already declared in `pyproject.toml`.

## Decision

Keep the CLI integration suite focused on behavioral assertions by invoking the
entry point directly (`python -m decree`) without attempting to capture coverage
from those subprocesses. Rely on the standard pytest-cov plugin, configured via
`pyproject.toml`, to gather coverage from in-process unit tests.

## Consequences

* Coverage gates remain enforced uniformly through pytest-cov without bespoke
  environment variables or rcfiles.
* The CLI integration tests stay portable across platforms because they no
  longer assume the presence of extra tooling inside the child process.
* Future contributors can revisit subprocess coverage if requirements change,
  but doing so will warrant a fresh ADR.

## Alternatives considered

* Maintaining per-test coverage wiring – rejected for the reasons above.
* Dropping the CLI integration tests – rejected because the exit-code contract
  needs end-to-end validation independent of coverage collection.
