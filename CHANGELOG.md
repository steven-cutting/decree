
# changelog

## 0.1.0

### Added

* Allow `decree new --template` to read from the `ADR_TEMPLATE` environment variable
  when omitted on the CLI, keeping CLI > env > default precedence.
* Initial CLI and API with `init`, `new`, `link`, `list`, `generate toc`,
  `generate graph` stub, `upgrade-repository` no-op.
* CI, nox, ruff, mypy strict, pytest harness.
