from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from decree.cli import app
from decree.core import AdrLog

runner = CliRunner()


def _init_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    AdrLog.init()
    return tmp_path / "doc" / "adr"


def test_env_template_used_when_option_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_dir = _init_repo(tmp_path, monkeypatch)
    env_template = tmp_path / "env_template.md"
    env_template.write_text(
        "__ENV_SENTINEL__\n# {number} {title}\nStatus: {status}\nDate: {date}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ADR_TEMPLATE", str(env_template))

    result = runner.invoke(app, ["new", "Env", "First"])

    assert result.exit_code == 0, result.stdout
    adr_path = next(repo_dir.glob("0002-*.md"))
    assert "__ENV_SENTINEL__" in adr_path.read_text(encoding="utf-8")


def test_cli_template_overrides_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_dir = _init_repo(tmp_path, monkeypatch)
    env_template = tmp_path / "env_template.md"
    env_template.write_text(
        "__ENV_SENTINEL__\n# {title}\nStatus: {status}\nDate: {date}\n",
        encoding="utf-8",
    )
    cli_template = tmp_path / "cli_template.md"
    cli_template.write_text(
        "__CLI_SENTINEL__\n# {title}\nStatus: {status}\nDate: {date}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ADR_TEMPLATE", str(env_template))

    result = runner.invoke(app, ["new", "--template", str(cli_template), "Cli", "Wins"])

    assert result.exit_code == 0, result.stdout
    adr_path = next(repo_dir.glob("0002-*.md"))
    content = adr_path.read_text(encoding="utf-8")
    assert "__CLI_SENTINEL__" in content
    assert "__ENV_SENTINEL__" not in content


def test_default_template_used_without_env_or_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_dir = _init_repo(tmp_path, monkeypatch)
    sentinel_template = tmp_path / "sentinel.md"
    sentinel_template.write_text("__SHOULD_NOT_APPEAR__", encoding="utf-8")

    result = runner.invoke(app, ["new", "Default", "Path"])

    assert result.exit_code == 0, result.stdout
    adr_path = next(repo_dir.glob("0002-*.md"))
    content = adr_path.read_text(encoding="utf-8")
    assert "__SHOULD_NOT_APPEAR__" not in content


def test_invalid_env_template_path_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _init_repo(tmp_path, monkeypatch)
    missing = "/tmp/nope/missing_template.md"
    monkeypatch.setenv("ADR_TEMPLATE", str(missing))

    result = runner.invoke(app, ["new", "Broken"])

    assert result.exit_code != 0
    assert str(missing) in result.output
