# Markdown lint rules

This project migrated from `markdownlint-cli2` to
[PyMarkdown](https://github.com/jackdewinter/pymarkdown).
The goal was to remove the Node toolchain requirement while keeping
comparable coverage.

> **Note:** `.pymarkdown.json` is currently a minimal placeholder while we
> rebuild the tuned rule set.

## Baseline mapping

- **Runner**: `markdownlint-cli2` (Node) has been replaced by `pymarkdown` (Python). We execute it via
  pre-commit and the Makefile helpers.
- **Line length**: markdownlint's default `MD013` became `md013` with a 100-character limit that skips
  fenced code. The value matches the Ruff configuration.
- **Multiple blank lines**: `MD012` remains disabled as `md012` so longer ADR sections stay intact.
- **Emphasis as heading**: `MD036` stays disabled as `md036` to allow emphasis inherited from
  legacy ADRs.

## Disabled or tuned rules

- **md012** – still disabled so ADR templates with extra spacing continue to pass.
- **md036** – disabled to avoid flagging emphasized text copied from upstream docs.
- **md013** – configured to allow 100 character prose lines and longer fenced blocks.

## Usage

- `make md-lint` runs `pymarkdown scan .` via `uv`.
- `make md-fix` runs the automated fixer.
- The pre-commit hook is pinned to `pymarkdown` `v0.9.17` and auto-discovers `.pymarkdown.json`.

## Optional experiments

A commented `md-lint-rust` target in the `Makefile` documents how we could trial a Rust tool
without enabling it by default.
