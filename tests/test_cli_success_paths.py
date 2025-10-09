from __future__ import annotations

from pathlib import Path

import click
import pytest
from typer.testing import CliRunner

from decree import cli
from decree.cli import app
from decree.exitcodes import ExitCode


def test_init_new_and_list(tmp_path: Path) -> None:
    runner = CliRunner()
    adr_dir = tmp_path / "doc" / "adr"

    result_init = runner.invoke(app, ["init", str(adr_dir)])
    assert result_init.exit_code == 0

    result_new = runner.invoke(app, ["new", "Sample", "ADR", "--dir", str(adr_dir)])
    assert result_new.exit_code == 0

    result_list = runner.invoke(app, ["list", "--dir", str(adr_dir)])
    assert result_list.exit_code == 0
    assert "Sample ADR" in result_list.stdout

    result_toc = runner.invoke(app, ["generate", "toc", "--dir", str(adr_dir)])
    assert result_toc.exit_code == 0
    assert "Architecture decision records" in result_toc.stdout


def test_link_command(tmp_path: Path) -> None:
    runner = CliRunner()
    adr_dir = tmp_path / "doc" / "adr"

    runner.invoke(app, ["init", str(adr_dir)])
    runner.invoke(app, ["new", "First", "Record", "--dir", str(adr_dir)])
    runner.invoke(app, ["new", "Second", "Record", "--dir", str(adr_dir)])

    result_link = runner.invoke(
        app,
        ["link", "1", "Supersedes", "2", "--dir", str(adr_dir)],
    )
    assert result_link.exit_code == 0
    assert "Linked" in result_link.stdout


def test_resolve_template_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    with pytest.raises(click.ClickException) as excinfo:
        cli._resolve_template_path(missing)
    assert excinfo.value.exit_code == int(ExitCode.INPUT_MISSING)


def test_resolve_template_not_file(tmp_path: Path) -> None:
    directory = tmp_path / "dir"
    directory.mkdir()
    with pytest.raises(click.ClickException) as excinfo:
        cli._resolve_template_path(directory)
    assert excinfo.value.exit_code == int(ExitCode.INPUT_MISSING)


def test_resolve_template_unreadable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    template = tmp_path / "template.md"
    template.write_text("content", encoding="utf-8")
    original_exists = Path.exists
    original_open = Path.open

    def fake_exists(path: Path) -> bool:
        if path == template:
            raise OSError("no access")
        return original_exists(path)

    def fake_open(self: Path, *args: object, **kwargs: object):
        class RaiseOnEnter:
            def __enter__(self):
                raise OSError("cannot open")
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        return RaiseOnEnter()

    monkeypatch.setattr(Path, "exists", fake_exists)
    with pytest.raises(click.ClickException) as excinfo:
        cli._resolve_template_path(template)
    assert excinfo.value.exit_code == int(ExitCode.UNAVAILABLE)

    monkeypatch.setattr(Path, "exists", original_exists)
    monkeypatch.setattr(Path, "open", fake_open)
    with pytest.raises(click.ClickException) as excinfo:
        cli._resolve_template_path(template)
    assert excinfo.value.exit_code == int(ExitCode.INPUT_MISSING)

    monkeypatch.setattr(Path, "open", original_open)
