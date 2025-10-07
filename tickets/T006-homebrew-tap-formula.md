# T006 — Homebrew tap & formula sha

**user story & rationale**  
As a macOS user, I want to install via Homebrew.

**scope (in)**  
- Create `steven-cutting/homebrew-decree`.  
- Add `Formula/decree.rb` with sdist URL + SHA256 post-PyPI release.  
- CI check on macOS runner (`brew install steven-cutting/decree/decree`).

**non-goals (out)**  
- Homebrew core submission.

**acceptance criteria**  
- `brew install` succeeds on macOS CI; `decree --help` works.

**test notes**  
- Simple GH Action in tap repo that installs from the formula.

**docs impact**  
- README: Homebrew install instructions.

**dependencies**  
- T005 (PyPI release live).

**estimate**  
- M (1 day)

**labels**  
- area/dist, ci/release, priority/p0
