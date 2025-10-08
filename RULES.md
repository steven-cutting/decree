# Markdown lint rules

This project migrated from `markdownlint-cli2` to [PyMarkdown](https://github.com/jackdewinter/pymarkdown)
to remove the Node toolchain requirement while keeping comparable coverage.

## Baseline mapping

| Concern | markdownlint-cli2 | PyMarkdown | Notes |
| --- | --- | --- | --- |
| Runner | `markdownlint-cli2` (Node) | `pymarkdown` (Python) | Executed through pre-commit and the Makefile helper. |
| Line length | Default rule (`MD013`) relied on defaults | `md013` line length raised to 100, skip code blocks | Aligns with project Ruff line length of 100 and avoids noisy code snippets. |
| Multiple blank lines | `MD012` disabled | `md012` disabled | Keeps existing layout flexibility for long ADRs. |
| Emphasis as heading | `MD036` disabled | `md036` disabled | Allows intentional use of emphasis in historical ADR imports. |

## Disabled or tuned rules

- **md012** – still disabled so ADR templates with extra spacing continue to pass.
- **md036** – disabled to avoid flagging emphasized text copied from upstream docs.
- **md013** – configured to allow 100 character prose lines and longer fenced blocks.

## Usage

- `make md-lint` runs `pymarkdown --config .pymarkdown.toml scan .` via `uv`.
- `make md-fix` runs the automated fixer.
- The pre-commit hook is pinned to `pymarkdown` `v0.9.32` and uses the same configuration file.

## Optional experiments

A commented `md-lint-rust` target in the `Makefile` documents how we could trial a Rust tool
without enabling it by default.
