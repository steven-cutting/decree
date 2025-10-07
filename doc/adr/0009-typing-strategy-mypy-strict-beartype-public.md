
# 0009: Typing strategy: mypy strict + beartype on public API

Date: 2025-10-06
Status: Accepted

## Context

We value early error detection.

## Decision

Enable mypy strict across the codebase and beartype runtime checks on public API only.

## Consequences

* Better contracts.
* Minimal runtime overhead.

## Alternatives considered

* No runtime checks.
