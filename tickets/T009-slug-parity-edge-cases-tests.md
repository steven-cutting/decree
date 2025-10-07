# T009 — Slug parity edge cases tests

**user story & rationale**  
As a user, I expect stable slug rules across odd inputs.

**scope (in)**  
- Tests for: digits-only titles, leading/trailing punctuation, repeated punctuation, non-ASCII removal, whitespace collapse.  
- Ensure duplicate titles produce distinct filenames due to numbering (no change needed).

**non-goals (out)**  
- i18n beyond ASCII stripping.

**acceptance criteria**  
- `tests/test_slugify.py` expanded; all green on 3 OSes.

**test notes**  
- Add cases: `"123" -> "123"`, `"--wow--" -> "wow"`, `"你好 world" -> "world"`.

**docs impact**  
- README: clarify slug rule examples.

**dependencies**  
- None.

**estimate**  
- S (0.5 day)

**labels**  
- area/api, quality/tests, priority/p1
