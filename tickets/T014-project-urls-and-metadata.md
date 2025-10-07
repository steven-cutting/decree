# T014 — Add project.urls and metadata polish

**user story & rationale**  
As a user, I want package metadata to link to the repo, issues, and homepage.

**scope (in)**  
- Add `[project.urls]` to `pyproject.toml` (Homepage, Repository, Issues).  
- Verify `twine check` passes in `nox -s release_dry_run`.

**non-goals (out)**  
- Changing license or classifiers.

**acceptance criteria**  
- Build metadata includes URLs; `twine check dist/*` passes.

**test notes**  
- Run `nox -s release_dry_run` locally or in CI.

**docs impact**  
- None.

**dependencies**  
- None.

**estimate**  
- S (0.25 day)

**labels**  
- area/build, ci/release, priority/p2
