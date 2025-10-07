# T008 — Add parity deviation log

**user story & rationale**  
As a migrator from `adr-tools`, I need a clear list of intentional differences.

**scope (in)**  
- Add `doc/parity-deviations.md`.  
- Seed entries: “generate graph (not implemented, exit 2)”, “wording may differ”, “Windows newline behavior”.  
- Link from README.

**non-goals (out)**  
- Exhaustive mapping to every shell script edge case (can grow later).

**acceptance criteria**  
- File exists and is linked; content lists deviations clearly.

**test notes**  
- Docs only.

**docs impact**  
- README link.

**dependencies**  
- None.

**estimate**  
- S (0.25 day)

**labels**  
- area/docs, priority/p1
