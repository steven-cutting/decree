from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import typer

from .core import AdrLog
from .models import AdrRef, AdrStatus

app = typer.Typer(add_completion=False, help="Decree: typed Python reimplementation of adr-tools")


@app.command()
def init(dir: Optional[Path] = typer.Argument(None, help="Directory to initialize (defaults to ./doc/adr)")) -> None:
    """Initialize ADR repository."""
    AdrLog.init(dir)
    typer.echo(f"Initialized ADR directory at {(dir or Path('doc/adr')).resolve()}")


@app.command()
def new(
    title: List[str] = typer.Argument(..., help="Title words of the ADR"),
    status: AdrStatus = typer.Option(AdrStatus.Accepted, "--status", case_sensitive=False),
    template: Optional[Path] = typer.Option(None, "--template", help="Path to template"),
    dir: Optional[Path] = typer.Option(None, "--dir", help="ADR directory"),
) -> None:
    """Create a new ADR."""
    rec = AdrLog(dir or Path("doc/adr")).new(" ".join(title), status=status, template=template)
    typer.echo(str(rec.path))


@app.command()
def link(
    src: int = typer.Argument(..., help="Source ADR number"),
    rel: str = typer.Argument(..., help="Relationship label, e.g., Supersedes"),
    tgt: int = typer.Argument(..., help="Target ADR number"),
    reverse: bool = typer.Option(False, "--reverse/--no-reverse", help="Also add reverse link"),
    dir: Optional[Path] = typer.Option(None, "--dir", help="ADR directory"),
) -> None:
    """Add a relationship between ADRs."""
    AdrLog(dir or Path("doc/adr")).link(AdrRef(src), rel, AdrRef(tgt), reverse=reverse)
    typer.echo("Linked")


@app.command("list")
def list_cmd(dir: Optional[Path] = typer.Option(None, "--dir", help="ADR directory")) -> None:
    """List ADRs."""
    for r in AdrLog(dir or Path("doc/adr")).list():
        typer.echo(f"{r.number:04d} {r.date} {r.status.value} {r.title}")


@app.command("generate")
def generate(
    what: str = typer.Argument(..., help="What to generate: toc|graph"),
    dir: Optional[Path] = typer.Option(None, "--dir", help="ADR directory"),
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
def upgrade_repository(dir: Optional[Path] = typer.Option(None, "--dir", help="ADR directory")) -> None:
    """Validate repository (v1 no-op)."""
    AdrLog(dir or Path("doc/adr")).upgrade()
    typer.echo("OK")


def main() -> None:
    try:
        app()
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=66)
    except OSError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=73)
