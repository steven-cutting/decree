from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .core import AdrLog
from .models import AdrRef, AdrStatus

app = typer.Typer(add_completion=False, help="Decree: typed Python reimplementation of adr-tools")


@app.command()
def init(
    dir: Annotated[
        Path | None, typer.Argument(help="Directory to initialize (defaults to ./doc/adr)")
    ] = None,
) -> None:
    """Initialize ADR repository."""
    AdrLog.init(dir)
    typer.echo(f"Initialized ADR directory at {(dir or Path('doc/adr')).resolve()}")


@app.command()
def new(
    title: Annotated[list[str], typer.Argument(help="Title words of the ADR")],
    status: Annotated[
        AdrStatus, typer.Option("--status", case_sensitive=False)
    ] = AdrStatus.Accepted,
    template: Annotated[
        Path | None,
        typer.Option(
            "--template",
            envvar="ADR_TEMPLATE",
            help="Path to template (can also be set via ADR_TEMPLATE)",
        ),
    ] = None,
    dir: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Create a new ADR."""
    template_path = _resolve_template_path(template)
    rec = AdrLog(dir or Path("doc/adr")).new(" ".join(title), status=status, template=template_path)
    typer.echo(str(rec.path))


def _resolve_template_path(template: Path | None) -> Path | None:
    if template is None:
        return None

    expanded = Path(template).expanduser()
    try:
        candidate = expanded.resolve()
    except OSError as exc:  # pragma: no cover - resolution errors are rare but handled
        typer.echo(f"Could not resolve template path {expanded}: {exc}", err=True)
        raise typer.Exit(code=73) from exc

    try:
        exists = candidate.exists()
    except OSError as exc:
        typer.echo(f"Could not access template path {candidate}: {exc}", err=True)
        raise typer.Exit(code=73) from exc

    if not exists:
        typer.echo(f"Template not found: {candidate}", err=True)
        raise typer.Exit(code=66)
    if not candidate.is_file():
        typer.echo(f"Template path is not a file: {candidate}", err=True)
        raise typer.Exit(code=66)

    try:
        with candidate.open("r", encoding="utf-8"):
            pass
    except OSError as exc:
        typer.echo(f"Could not read template at {candidate}: {exc}", err=True)
        raise typer.Exit(code=73) from exc

    return candidate


@app.command()
def link(
    src: Annotated[int, typer.Argument(help="Source ADR number")],
    rel: Annotated[str, typer.Argument(help="Relationship label, e.g., Supersedes")],
    tgt: Annotated[int, typer.Argument(help="Target ADR number")],
    reverse: Annotated[
        bool, typer.Option("--reverse/--no-reverse", help="Also add reverse link")
    ] = False,
    dir: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Add a relationship between ADRs."""
    AdrLog(dir or Path("doc/adr")).link(AdrRef(src), rel, AdrRef(tgt), reverse=reverse)
    typer.echo("Linked")


@app.command("list")
def list_cmd(
    dir: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """List ADRs."""
    for r in AdrLog(dir or Path("doc/adr")).list():
        typer.echo(f"{r.number:04d} {r.date} {r.status.value} {r.title}")


@app.command("generate")
def generate(
    what: Annotated[str, typer.Argument(help="What to generate: toc|graph")],
    dir: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Generate artifacts (toc; graph not implemented)."""
    log = AdrLog(dir or Path("doc/adr"))
    if what == "toc":
        typer.echo(log.generate_toc())
    elif what == "graph":
        typer.echo("generate graph is not implemented", err=True)
        raise typer.Exit(code=2)
    else:
        typer.echo("unknown artifact, expected 'toc' or 'graph'", err=True)
        raise typer.Exit(code=64)


@app.command("upgrade-repository")
def upgrade_repository(
    dir: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Validate repository (v1 no-op)."""
    AdrLog(dir or Path("doc/adr")).upgrade()
    typer.echo("OK")


def main() -> None:
    try:
        app()
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=66) from e
    except OSError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=73) from e
