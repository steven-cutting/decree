# T002 — Ensure date consistency in AdrLog.new()

**user story & rationale**  
As a user, I want the `AdrRecord.date` returned by `new()` to match the `Date:` line written to disk so programmatic uses are deterministic.

**scope (in)**  
- Use a single `date_value` for both record and file content.  
- Unit test to enforce equality.

**non-goals (out)**  
- Alternate date formats.

**acceptance criteria**  
- New ADR’s `Date:` equals `rec.date` returned from `AdrLog.new()`.  
- Test fails if values diverge.

**test notes**  
- `tests/test_date_consistency.py`: call `new()`, read file, parse `Date:` and compare.

**docs impact**  
- None.

**dependencies**  
- None.

**estimate**  
- S (0.25 day)

**labels**  
- area/api, quality/tests, priority/p0
