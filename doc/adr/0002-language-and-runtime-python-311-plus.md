
# 0002: Language and runtime: Python 3.11+

Date: 2025-10-06
Status: Accepted

## Context

We want modern features and tight type checking with broad availability.

## Decision

Target Python 3.11 and newer for decree.

## Consequences

* Can use `StrEnum`, `zoneinfo`, and improved typing.
* Smaller compatibility surface.

## Alternatives considered

* Supporting 3.10 would increase maintenance for limited benefit.
