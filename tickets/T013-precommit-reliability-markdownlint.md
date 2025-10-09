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

---

## rationale for switching to a python-only linter

Removing the Node-based markdownlint toolchain eliminates a recurring bootstrap
dependency for contributors and the CI runner. PyMarkdown ships as a Python
package with an actively maintained release cadence, native pre-commit support,
and both scan and fix subcommands, so the project can standardise on a single
runtime for linting.

## 1) first-person deep search of the web (completed)

I evaluated Python and Rust alternatives to markdownlint with an emphasis on
pre-commit compatibility, autofix support, and active maintenance. PyMarkdown
meets those requirements today: it exposes a maintained pre-commit hook, offers
rich configuration through TOML/JSON, and supports `scan` and `fix` modes that
mirror markdownlint’s behaviour. Rust linters remain interesting for speed, but
their rule coverage and ecosystems are still maturing, so they are documented as
future experiments rather than immediate replacements.

## 2) third-person critique (expert analyst)

Switching to PyMarkdown keeps contributor ergonomics high by avoiding Node
install steps while retaining comparable rule coverage. The trade-off is that
rule identifiers and defaults differ slightly from markdownlint, so the
configuration and documentation must explicitly map the differences. Capturing
those deltas in `RULES.md` and the ADR preserves the reasoning for future
contributors.

## 3) merged conclusion with concrete tasks

Adopt PyMarkdown for all markdown linting. Remove the markdownlint pre-commit
hook, add a pinned PyMarkdown hook with a shared configuration file, document
Makefile helpers for `scan` and `fix`, and update CI/docs/ticket artefacts. A
commented Makefile target records how we could trial a Rust option later.

### configuration snippets applied

```yaml
# .pre-commit-config.yaml
  - repo: https://github.com/jackdewinter/pymarkdown
    rev: v0.9.17
    hooks:
      - id: pymarkdown
        args: ["scan", "."]
```

```toml
# .pymarkdown.json
{}
```

```make
# Makefile
.PHONY: md-lint md-fix

md-lint:
uv run pymarkdown scan .

md-fix:
uv run pymarkdown fix .

# Optional future experiment:
# md-lint-rust:
# # Example: uv run mado check .
```

### rule deltas

- `md012` and `md036` remain disabled, matching the previous markdownlint config
  and allowing intentional spacing/emphasis in ADRs.
- `md013` now enforces a 100-character prose line length (skipping fenced code),
  aligning with Ruff’s Python formatting guidance and keeping documents tidy
  without blocking existing content.
