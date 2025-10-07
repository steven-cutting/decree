
# 0012: CI/CD with GitHub Actions

Date: 2025-10-06
Status: Accepted

## Context

We need multi-OS testing and automated releases.

## Decision

Use a matrix on ubuntu/macos/windows for 3.11/3.12. Cache `uv`. Gates: ruff, mypy, pytest. Tag push triggers PyPI publish.

## Consequences

* Confidence before releases.
* Minimal manual work.

## Alternatives considered

* Other CI vendors.
