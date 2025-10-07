# T010 — Windows newlines & paths: docs + check

**user story & rationale**

As a Windows user, I want to know about newline and path differences.

**scope (in)**

- Document CRLF differences and `pathlib` usage.
- Add Windows CI assertion that reading files is tolerant to `\n` writes.

**non-goals (out)**

- Auto-conversion of line endings.

**acceptance criteria**

- Windows runner stays green; doc section added.

**test notes**

- Extend an existing test to read file in text mode and assert content
  present (not exact byte EOL).

**docs impact**

- README “compatibility” section.

**dependencies**

- None.

**estimate**

- S (0.5 day)

**labels**

- area/docs, quality/tests, priority/p1
