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
* `decree new [--status STATUS] [--template PATH] [--dir DIR] TITLE...`
* `decree link SRC REL TGT [--reverse / --no-reverse]`
* `decree list`
* `decree generate toc`
* `decree generate graph` (not implemented)
* `decree upgrade-repository`

## configuration

* `ADR_DATE`: if set, used verbatim as the ADR date
* `DECREE_TZ`: IANA timezone for date formatting (default: `UTC`)
* `ADR_TEMPLATE`: path to a custom template file

## license

BSD-3-Clause for our code. CC-BY-4.0 notices for any third-party snippets.
