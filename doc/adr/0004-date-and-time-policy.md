
# 0004: Date and time policy

Date: 2025-10-06
Status: Accepted

## Context

Teams need deterministic dates for reproducible outputs.

## Decision

If the CLI flag `--date` is provided, use its value verbatim.
Else if `ADR_DATE` is set, use it verbatim.
Otherwise, format `YYYY-MM-DD` using the local date from `datetime.date.today()`.

## Consequences

* CI can pin dates.
* Local runs remain predictable.

## Alternatives considered

* Always use local time without overrides.
