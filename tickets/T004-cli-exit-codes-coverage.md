# T004 — CLI exit codes: coverage & tests

**user story & rationale**  
As a user, I want predictable exit codes for scripting.

**scope (in)**  
- Tests for:  
  - `decree generate graph` → exit 2; stderr says “not implemented”.  
  - `decree generate badthing` → exit 64.  
  - File-not-found scenarios → exit 66.  
  - Write failures (simulate) → exit 73.

**non-goals (out)**  
- Changing the defined codes.

**acceptance criteria**  
- Pytest captures codes and stderr messages exactly.  
- No flaky tests.

**test notes**  
- `tests/test_cli_exit_codes.py` using Typer’s `CliRunner`.  
- Simulate write error with read-only dir (skip on Windows if flaky).

**docs impact**  
- README’s exit code table (add/update).

**dependencies**  
- None.

**estimate**  
- M (1 day)

**labels**  
- area/cli, quality/tests, priority/p0
