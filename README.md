# decree

Python 3.11+ reimplementation of `adr-tools` with a typed API and a Typer CLI.

## install

Decree is published on PyPI and can be installed on Linux, macOS, or Windows.
We recommend using either **pipx** or **uv** for a clean, isolated installation.

### Install with pipx

`pipx` installs Python CLI tools in their own virtual environments so they do
not interfere with system packages.

```bash
pipx ensurepath
pipx install decree
decree --help
```

Upgrade:

```bash
pipx upgrade decree
```

Uninstall:

```bash
pipx uninstall decree
```

Works on Ubuntu, Debian, macOS, and Windows.
Uses your system Python (3.11 or newer).
No sudo is required for the app itself.

### Install with uv

uv is a Rust-based Python toolchain designed for speed and reproducibility.

Install uv: [guide](https://docs.astral.sh/uv/getting-started/installation/)

Install decree:

```bash
uv tool install decree
decree --help
```

Upgrade:

```bash
uv tool upgrade decree
```

Uninstall:

```bash
uv tool uninstall decree
```

uv does not require system Python once installed.

## quickstart

```bash
decree init
decree new Use beartype on public API
decree list
decree generate toc > doc/adr/README.md
decree generate graph  # exits non-zero, not implemented
```

## cli

* `decree init [DIR]`
* `decree new [--status STATUS] [--template PATH] [--dir DIR] [--date YYYY-MM-DD] TITLE...`
* `decree link SRC REL TGT [--reverse / --no-reverse]`
* `decree list`
* `decree generate toc`
* `decree generate graph` (not implemented)
* `decree upgrade-repository`

## exit codes

Decree follows [sysexits](https://man.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3) where
available and falls back to portable numbers on platforms such as Windows. The
fallback values are listed below; on POSIX you will see the native `os.EX_*`
numbers (for example, usage errors exit with 64).

| Fallback | ExitCode member | Meaning |
| -------- | --------------- | ------- |
| 0 | `ExitCode.SUCCESS` | Successful run. |
| 1 | `ExitCode.GENERAL_ERROR` | Unexpected runtime failure or abort. |
| 2 | `ExitCode.USAGE_ERROR` | CLI usage error (missing/bad arguments). |
| 66 | `ExitCode.INPUT_MISSING` | Required input was missing or unreadable. |
| 69 | `ExitCode.UNAVAILABLE` | Service or dependency unavailable. |
| 78 | `ExitCode.CONFIG_ERROR` | Configuration or environment problem. |

Examples:

```bash
decree new "Valid ADR"              # -> 0
decree new --template missing.md foo # -> 66 (missing template)
ADR_DATE=bad-date decree new Foo     # -> 78 (invalid config)
```

Contributors should raise `click.UsageError` for argument problems and
`click.ClickException` with `ExitCode` for domain failures. See the
[Click exception guide](https://click.palletsprojects.com/en/stable/exceptions/)
for details.

## configuration

* `ADR_DATE`: if set, used verbatim as the ADR date after validation
* `ADR_TEMPLATE`: path to a custom template file

Template precedence is explicit CLI flag first, then the environment variable, then the
built-in default:

```bash
ADR_TEMPLATE=/path/to/template.md decree new "Use beartype"
decree new --template /other/path.md "Use beartype"  # CLI overrides env var
```

## dependabot

Dependabot checks uv dependencies and GitHub Actions every Monday at 09:00 America/Los_Angeles.
Edit `.github/dependabot.yml` to change the schedule window,
and adjust the `groups` block if you want different buckets for runtime versus dev tooling updates.

### Date handling and reproducibility

New ADRs always render `Date: YYYY-MM-DD` in their front matter. By default, the
current local date is used. Supply `--date YYYY-MM-DD` or set the `ADR_DATE`
environment variable to override the value (the CLI flag takes precedence). Any
override must already be in ISO format; otherwise, the command exits with an
error.
