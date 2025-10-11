# 0016: Bidirectional ADR linking

Date: 2025-10-08
Status: Accepted

## Context

`AdrLog.link` previously hand-rolled link lines inside ADR markdown files. The
approach diverged from `npryce/adr-tools` by allowing duplicate link entries and
by only updating the forward direction by default, which led to asymmetric ADR
relationships.

## Decision

Introduce shared `link_adr` and `unlink_adr` helpers that mirror the
`adr-tools` behavior, including relationship reverse-mapping defaults such as
"Supersedes"/"Is superseded by". `AdrLog.link` now delegates to the helper and a
new `AdrLog.unlink` API removes relationships with the same parity guarantees.

## Consequences

* ADR link and unlink operations no longer create duplicate lines when repeated.
* Reverse relationships are written and removed automatically when requested,
  matching contributor expectations from `adr-tools`.
* Centralizing the IO logic simplifies future enhancements (e.g., custom
  relationship types) while keeping parity testable.

## Usage Examples

### Basic linking

```bash
# Add forward link only
decree link 2 Supersedes 1

# Adds to 0002: "Supersedes: 0001"
```

### Bidirectional linking with --reverse

```bash
# Add both forward and reverse links
decree link 2 Supersedes 1 --reverse

# Adds to 0002: "Supersedes: 0001"
# Adds to 0001: "Is superseded by: 0002"
```

### Other relationship types

```bash
decree link 3 Amends 1 --reverse
# Adds to 0003: "Amends: 0001"
# Adds to 0001: "Is amended by: 0003"
```

### Removing relationships

```bash
# Remove bidirectional link
decree unlink 2 Supersedes 1 --reverse

# Removes "Supersedes: 0001" from 0002
# Removes "Is superseded by: 0002" from 0001
```

## Alternatives considered

* Leave the previous implementation untouched – kept historical quirks and
  required manual cleanup when duplicates occurred.
* Only implement deduplication – still left reverse relationships inconsistent
  and made unlinking harder to reason about.
