# T005 — PyPI Trusted Publishing: project + OIDC

**user story & rationale**  
As a maintainer, I want releases to publish to PyPI via OIDC without tokens.

**scope (in)**  
- Create `decree` project on PyPI.  
- Add GitHub repo as a Trusted Publisher.  
- Verify `release.yml` publishes on tag.  
- Confirm GitHub Releases flow exists or establish it as part of documenting the release pipeline (capture via ADR if needed).

**non-goals (out)**  
- TestPyPI flow (optional).

**acceptance criteria**  
- Tagging `v0.1.0` produces artifacts on PyPI.  
- Action logs show “trusted publishing” success.  
- Release process notes (including GitHub Releases expectations) captured in docs/ADR.

**test notes**  
- Dry run if needed with TestPyPI (optional).

**docs impact**  
- README: `pipx install decree` confirmed.

**dependencies**  
- None.

**estimate**  
- S (0.5 day)

**labels**  
- ci/release, area/dist, priority/p0
