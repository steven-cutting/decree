# 0015: Markdown linting with PyMarkdown

Date: 2025-10-08
Status: Accepted

## Context

Pre-commit previously relied on `markdownlint-cli2`, which required Node tooling
both locally and in CI. Contributors regularly hit bootstrap issues while Python
checks continued to run smoothly.

## Decision

Replace the markdownlint hook with PyMarkdown pinned at `v0.9.32`, share a
project-wide `.pymarkdown.toml`, and document `make md-lint`/`make md-fix`
helpers that invoke the Python CLI through `uv`.

## Consequences

* Pre-commit and CI no longer need Node to lint Markdown.
* Contributors have an explicit autofix workflow via `make md-fix`.
* Rule mappings live in `RULES.md` for easy future tuning.

## Alternatives considered

* Keeping markdownlint only in CI – still required Node in automation and
  created drift with local hooks.
* Pinning markdownlint-cli2 and documenting Node – increased setup complexity
  without reducing long-term maintenance.
* Adopting a Rust markdown linter – promising for speed but lacks parity today,
  so recorded as a future experiment only.
