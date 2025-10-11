"""Automation sessions for local development."""

from __future__ import annotations

import nox

PY = ["3.11", "3.12", "3.13"]


@nox.session
def lint(session: nox.Session) -> None:
    """Run Ruff's lint pass across the repository."""
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    """Execute mypy in strict mode against sources and tests."""
    session.install("mypy", "beartype")
    session.run("mypy", "src", "tests")


@nox.session(python=PY)
def tests(session: nox.Session) -> None:
    """Run the pytest suite under the supported Python versions."""
    session.install(".[dev]")
    session.run("pytest", "-q")


@nox.session
def build(session: nox.Session) -> None:
    """Create source and wheel distributions."""
    session.install("uv-build")
    session.run("python", "-m", "uv_build", "sdist", "bdist_wheel")


@nox.session
def release_dry_run(session: nox.Session) -> None:
    """Build distributions and ensure they pass Twine's validation."""
    session.install("uv-build", "twine")
    session.run("python", "-m", "uv_build", "sdist", "bdist_wheel")
    session.run("twine", "check", "dist/*")
