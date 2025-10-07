
# 0008: Testing approach: pytest + real filesystem

Date: 2025-10-06
Status: Accepted

## Context

CLI tools are best tested against real files.

## Decision

Use pytest with `tmp_path`, minimal mocking, and golden tests.
Vendor small CC-BY snippets in `third_party/`.

## Consequences

* Higher confidence in behavior.
* Slightly slower tests, acceptable.

## Alternatives considered

* Heavy mocking with brittle assumptions.
