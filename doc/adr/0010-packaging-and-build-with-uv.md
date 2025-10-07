
# 0010: Packaging and build with uv

Date: 2025-10-06
Status: Accepted

## Context

We want reproducible, fast builds.

## Decision

Use `uv` and `uv_build` to build sdists and wheels.

## Consequences

* Deterministic CI.
* Simple developer workflow.

## Alternatives considered

* Plain setuptools.
