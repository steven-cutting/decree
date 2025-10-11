"""Development CLI tools for the Decree project."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(add_completion=False, help="")
title_app = typer.Typer(add_completion=False, help="")
app.add_typer(title_app, name="title")

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PYPROJECT_FILE = PROJECT_ROOT / "pyproject.toml"


@app.command()
def validate_version(
    version: Annotated[
        str,
        typer.Argument(help="Version to validate"),
    ],
    pyproject_file: Annotated[
        Path,
        typer.Option(
            "--pyproject-file",
            "-p",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            writable=False,
            resolve_path=True,
            help="Path to the pyproject.toml file to validate against.",
        ),
    ] = PYPROJECT_FILE,
) -> None:
    """Validate the given version string against the version string in the pyproject.toml file."""
    # Parse the pyproject.toml file
    try:
        with pyproject_file.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        typer.echo(f"Error: Invalid TOML in {pyproject_file}: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        typer.echo(f"Error: Could not read {pyproject_file}: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    # Extract the project version
    project_version = data.get("project", {}).get("version")
    if project_version is None:
        typer.echo(f"Error: No version found in {pyproject_file}", err=True)
        raise typer.Exit(code=1)

    # Compare versions (strict match, no normalization)
    if version != project_version:
        typer.echo(
            f"Error: Version mismatch\n"
            f"  Input version:   {version}\n"
            f"  Project version: {project_version}\n"
            f"  from {pyproject_file}",
            err=True,
        )
        raise typer.Exit(code=1)

    # Success
    typer.echo(f"✓ Version {version} matches project version {project_version}")


def main() -> None:
    """Entrypoint for :mod:`dev.cli`."""
    app()


if __name__ == "__main__":
    main()
