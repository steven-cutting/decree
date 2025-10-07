from __future__ import annotations

import nox

PY = ["3.11", "3.12", "3.13"]


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.install("mypy", "beartype")
    session.run("mypy", "src", "tests")


@nox.session(python=PY)
def tests(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("pytest", "-q")


@nox.session
def build(session: nox.Session) -> None:
    session.install("uv-build")
    session.run("python", "-m", "uv_build", "sdist", "bdist_wheel")


@nox.session
def release_dry_run(session: nox.Session) -> None:
    session.install("uv-build", "twine")
    session.run("python", "-m", "uv_build", "sdist", "bdist_wheel")
    session.run("twine", "check", "dist/*")
