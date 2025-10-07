
# 0003: Status enum with StrEnum

Date: 2025-10-06
Status: Accepted

## Context

ADRs use canonical status labels that appear in files and CLI output.

## Decision

Model statuses with `AdrStatus(StrEnum)` and store values as strings.

## Consequences

* Stable text in files.
* Easy CLI flags and parsing.

## Alternatives considered

* Plain strings with ad-hoc validation.
