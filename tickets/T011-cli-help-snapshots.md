# T011 — Snapshot tests for CLI --help

**user story & rationale**  
As a maintainer, I want to catch accidental UX changes in help text.

**scope (in)**

- Snapshot `decree --help`, `decree init --help`, `decree new --help`,
  `decree generate --help`.
- Normalize dynamic bits if any.

**non-goals (out)**

- Golden-testing entire runtime outputs beyond help.

**acceptance criteria**

- Tests fail on help text drift; maintainers update snapshots knowingly.

**test notes**

- `tests/test_cli_help.py` with Typer `CliRunner`.
- Store short golden strings or regex.

**docs impact**

- None.

**dependencies**

- None.

**estimate**

- S (0.5 day)

**labels**

- area/cli, quality/tests, priority/p1
