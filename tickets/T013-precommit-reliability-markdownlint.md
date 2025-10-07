# T013 — Pre-commit reliability for markdown/yaml lint

**user story & rationale**  
As a contributor, I want pre-commit to run consistently without Node
bootstrap issues.

**scope (in)**

Choose one:

- (A) keep markdownlint in CI only; remove from pre-commit, or
- (B) pin markdownlint-cli2 + add Node setup step to CI/pre-commit docs, or
- (C) switch to a Python-only markdown linter for pre-commit (consider
  `pymarkdown` unless a better option is identified).
- Produce an ADR capturing the chosen option and rationale.

**non-goals (out)**

- Building custom Node environments per OS.

**acceptance criteria**

- `pre-commit run -a` works locally with documented setup; CI passes.
- ADR linked from the ticket records the lint tooling decision.

**test notes**

- Manual validation in CI and locally.

**docs impact**

- CONTRIBUTING: setup notes for chosen option.

**dependencies**

- None.

**estimate**

- S (0.5 day)

**labels**

- quality/tooling, area/docs, priority/p1
