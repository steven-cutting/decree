
# 0004: Date and time policy

Date: 2025-10-06
Status: Accepted

## Context

Teams need deterministic dates for reproducible outputs.

## Decision

If `ADR_DATE` is set, use it verbatim.
Otherwise, format `YYYY-MM-DD` using `DECREE_TZ` (default UTC).

## Consequences

* CI can pin dates.
* Local runs remain predictable.

## Alternatives considered

* Always use local time.
