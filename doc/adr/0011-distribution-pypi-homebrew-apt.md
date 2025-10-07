
# 0011: Distribution: PyPI, Homebrew, and Apt

Date: 2025-10-06
Status: Accepted

## Context

Users prefer native package managers.

## Decision

Trusted publishing to PyPI on tags.
Homebrew tap using `Language::Python::Virtualenv` installs from PyPI.
Apt repo published via `reprepro` with a long-lived GPG key.

## Consequences

* Easy install on macOS and Debian/Ubuntu.
* Keys and repo hosting managed in CI.

## Alternatives considered

* Conda, Nix (post-1.0).
