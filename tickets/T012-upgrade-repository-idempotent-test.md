# T012 — upgrade-repository: idempotent test

**user story & rationale**  
As a maintainer, I want `upgrade-repository` to be safe to re-run.

**scope (in)**  
- Test creates `.decree/upgrade.marker` once; second run is no-op.

**non-goals (out)**  
- Implementing migrations.

**acceptance criteria**  
- Two consecutive runs both exit 0; marker unchanged.

**test notes**  
- `tests/test_upgrade_repository.py` using `tmp_path`.

**docs impact**  
- None.

**dependencies**  
- None.

**estimate**  
- S (0.25 day)

**labels**  
- area/cli, quality/tests, priority/p1
