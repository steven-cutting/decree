# T003 — Link behavior + reverse mapping tests

**user story & rationale**  
As a user, I want `link` to append correct relationship lines and, with `--reverse`, write the appropriate reverse label.

**scope (in)**  
- Verify forward link line `REL: NNNN`.  
- Reverse mapping: `Supersedes` ↔ `Superseded by`, `Amends` ↔ `Amended by`.  
- Tests for CLI and API.

**non-goals (out)**  
- Validating that numbers exist across directories.

**acceptance criteria**  
- `decree link 2 Supersedes 1 --reverse` appends `Supersedes: 0001` to ADR 0002 and `Superseded by: 0002` to ADR 0001.  
- Tests assert exact lines and idempotency on repeated runs (no duplicate lines if already present).

**test notes**  
- `tests/test_linking.py`: create ADRs, call API and CLI.  
- Consider adding a simple dedupe when exact line exists (or document current behavior).

**docs impact**  
- CLI examples include `--reverse`.

**dependencies**  
- T007 list/numbering (implicit via existing code).

**estimate**  
- M (1 day)

**labels**  
- area/cli, area/api, quality/tests, priority/p0
