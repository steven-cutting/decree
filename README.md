# decree

Python 3.11+ reimplementation of `adr-tools` with a typed API and a Typer CLI.

## install

```bash
pipx install decree
# or after release: brew install steven-cutting/decree/decree
````

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

## configuration

* `ADR_DATE`: if set, used verbatim as the ADR date after validation
* `ADR_TEMPLATE`: path to a custom template file

Template precedence is explicit CLI flag first, then the environment variable, then the
built-in default:

```bash
ADR_TEMPLATE=/path/to/template.md decree new "Use beartype"
decree new --template /other/path.md "Use beartype"  # CLI overrides env var
```

### Date handling and reproducibility

New ADRs always render `Date: YYYY-MM-DD` in their front matter. By default, the
current local date is used. Supply `--date YYYY-MM-DD` or set the `ADR_DATE`
environment variable to override the value (the CLI flag takes precedence). Any
override must already be in ISO format; otherwise, the command exits with an
error.

## license

BSD-3-Clause for our code. CC-BY-4.0 notices for any third-party snippets.
