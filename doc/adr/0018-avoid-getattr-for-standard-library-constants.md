# 0018: Avoid `getattr` for standard library constants

Date: 2025-10-10
Status: Accepted

## Context

During the CLI exit-code work we briefly relied on `getattr(os, "EX_OK", 0)` style
helpers to read optional `sysexits` constants. Review feedback highlighted that
indirect attribute access makes it harder for static type checkers such as
mypy, runtime validators like beartype, and linters including Ruff to reason
about the code. When the attribute name lives in a string literal those tools
lose track of the symbol, which in turn weakens import-time validation and
static analysis.

## Decision

Prefer direct attribute access wrapped in explicit `try`/`except AttributeError`
blocks when dealing with optional standard-library constants. This keeps the
attribute lookup visible to type checkers and tooling while still providing a
portable fallback when the constant is missing on a platform.

## Consequences

* Static analysis sees the attribute names directly, preserving strict typing
  guarantees.
* Fallback values remain explicit and documented in the same module where they
  are used.
* Contributors have a clear pattern to follow whenever optional constants are
  required.

## Alternatives considered

* Keeping the `getattr` helper – rejected because it hides attribute names from
  tooling and encourages more dynamic patterns across the codebase.
* Introducing a custom registry or mapping – unnecessary indirection for a
  handful of constants and would require additional maintenance.
