"""Typer-powered command line interface for Decree."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import click
import typer

from .core import AdrLog
from .exitcodes import ExitCode, exit_with
from .models import AdrRef, AdrStatus
from .utils import resolve_date

app = typer.Typer(add_completion=False, help="Decree: typed Python reimplementation of adr-tools")


def _validate_date_option(
    ctx: typer.Context,
    param: typer.CallbackParam,
    value: str | None,
) -> str | None:
    if value is None:
        return None
    try:
        resolve_date(cli_date=value, env={})
    except ValueError as exc:
        raise typer.BadParameter(str(exc), ctx=ctx, param=param) from exc
    return value


@app.command()
def init(
    directory: Annotated[
        Path | None,
        typer.Argument(help="Directory to initialize (defaults to ./doc/adr)"),
    ] = None,
) -> None:
    """Initialize ADR repository."""
    log = AdrLog.init(directory)
    typer.echo(f"Initialized ADR directory at {log.dir}")


@app.command()
def new(
    title: Annotated[list[str], typer.Argument(help="Title words of the ADR")],
    status: Annotated[
        AdrStatus,
        typer.Option("--status", case_sensitive=False),
    ] = AdrStatus.Accepted,
    template: Annotated[
        Path | None,
        typer.Option(
            "--template",
            envvar="ADR_TEMPLATE",
            help="Path to template (can also be set via ADR_TEMPLATE)",
        ),
    ] = None,
    directory: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
    date: Annotated[
        str | None,
        typer.Option(
            "--date",
            help="Set ADR date (YYYY-MM-DD). Overrides ADR_DATE environment variable.",
            callback=_validate_date_option,
        ),
    ] = None,
) -> None:
    """Create a new ADR."""
    template_path = _resolve_template_path(template)

    try:
        rec = AdrLog(directory or Path("doc/adr")).new(
            " ".join(title),
            status=status,
            template=template_path,
            date=date,
        )
    except ValueError as exc:
        raise _click_exception(str(exc), ExitCode.CONFIG_ERROR) from exc
    typer.echo(str(rec.path))


def _resolve_template_path(template: Path | None) -> Path | None:
    if template is None:
        return None

    expanded = Path(template).expanduser()
    try:
        candidate = expanded.resolve()
    except OSError as exc:  # pragma: no cover - resolution errors are rare but handled
        message = f"Could not resolve template path {expanded}: {exc}"
        raise _click_exception(message, ExitCode.UNAVAILABLE) from exc

    try:
        exists = candidate.exists()
    except OSError as exc:
        message = f"Could not access template path {candidate}: {exc}"
        raise _click_exception(message, ExitCode.UNAVAILABLE) from exc

    if not exists:
        message = f"Template not found: {candidate}"
        raise _click_exception(message, ExitCode.INPUT_MISSING)
    if not candidate.is_file():
        message = f"Template path is not a file: {candidate}"
        raise _click_exception(message, ExitCode.INPUT_MISSING)

    try:
        with candidate.open("r", encoding="utf-8"):
            pass
    except OSError as exc:
        message = f"Could not read template at {candidate}: {exc}"
        raise _click_exception(message, ExitCode.INPUT_MISSING) from exc

    return candidate


@app.command()
def link(
    src: Annotated[int, typer.Argument(help="Source ADR number")],
    rel: Annotated[str, typer.Argument(help="Relationship label, e.g., Supersedes")],
    tgt: Annotated[int, typer.Argument(help="Target ADR number")],
    reverse: Annotated[  # noqa: FBT002 - Typer option uses boolean defaults
        bool,
        typer.Option("--reverse/--no-reverse", help="Also add reverse link"),
    ] = False,
    directory: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Add a relationship between ADRs."""
    AdrLog(directory or Path("doc/adr")).link(AdrRef(src), rel, AdrRef(tgt), reverse=reverse)
    typer.echo("Linked")


@app.command("list")
def list_cmd(
    directory: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """List ADRs."""
    for r in AdrLog(directory or Path("doc/adr")).list():
        typer.echo(f"{r.number:04d} {r.date} {r.status.value} {r.title}")


@app.command("generate")
def generate(
    what: Annotated[str, typer.Argument(help="What to generate: toc|graph")],
    directory: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Generate artifacts (toc; graph not implemented)."""
    log = AdrLog(directory or Path("doc/adr"))
    if what == "toc":
        typer.echo(log.generate_toc())
    elif what == "graph":
        message = "generate graph is not implemented"
        raise _click_exception(message, ExitCode.UNAVAILABLE)
    else:
        message = "unknown artifact, expected 'toc' or 'graph'"
        raise click.UsageError(message)


@app.command("upgrade-repository")
def upgrade_repository(
    directory: Annotated[Path | None, typer.Option("--dir", help="ADR directory")] = None,
) -> None:
    """Validate repository (v1 no-op)."""
    AdrLog(directory or Path("doc/adr")).upgrade()
    typer.echo("OK")


def main() -> None:
    """Entrypoint for :mod:`decree.cli` that maps exceptions to exit codes."""
    try:
        app(standalone_mode=False)
    except click.UsageError as exc:
        exc.show(file=sys.stderr)  # Click prints help/usage to stderr
        exit_with(ExitCode.USAGE_ERROR)
    except click.Abort:
        exit_with(ExitCode.GENERAL_ERROR, "Aborted!")
    except click.ClickException as exc:
        exc.show(file=sys.stderr)
        code = getattr(exc, "exit_code", None)
        if isinstance(code, int):
            raise SystemExit(code) from exc
        exit_with(ExitCode.GENERAL_ERROR)
    except FileNotFoundError as exc:
        exit_with(ExitCode.INPUT_MISSING, str(exc))
    except OSError as exc:
        exit_with(ExitCode.UNAVAILABLE, str(exc))
    except KeyboardInterrupt:
        exit_with(ExitCode.GENERAL_ERROR, "Aborted!")
    except Exception as exc:  # noqa: BLE001 - fall back to a generic exit code
        exit_with(ExitCode.GENERAL_ERROR, str(exc))


class DecreeClickException(click.ClickException):
    """An exception class for Decree CLI errors that allows specifying a custom exit code.

    This class extends `click.ClickException` by adding an `exit_code` attribute,
    which is used to control the exit status of the CLI when the exception is raised.
    The `exit_code` should be an integer representing the desired process exit code.
    """

    def __init__(self, message: str, exit_code: int) -> None:
        """Capture a custom exit code alongside the Click message."""
        super().__init__(message)
        self.exit_code = exit_code


def _click_exception(message: str, code: ExitCode) -> click.ClickException:
    return DecreeClickException(message, int(code))
