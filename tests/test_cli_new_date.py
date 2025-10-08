from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from decree import cli
from decree.utils import resolve_date


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


def _init_repo(cli_runner: CliRunner, adr_dir: Path) -> None:
    init_result = cli_runner.invoke(cli.app, ["init", str(adr_dir)])
    assert init_result.exit_code == 0


def test_cli_new_defaults_to_today(tmp_path: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    adr_dir = tmp_path / "adr"
    _init_repo(cli_runner, adr_dir)
    frozen_today = date(2024, 1, 2)
    expected_date = frozen_today.isoformat()

    def _resolve_date(*, cli_date: str | None = None) -> str:
        return resolve_date(cli_date=cli_date, today=lambda: frozen_today)

    monkeypatch.setattr("decree.core.resolve_date", _resolve_date)

    result = cli_runner.invoke(
        cli.app,
        ["new", "Capture", "Decision", "--dir", str(adr_dir)],
    )
    assert result.exit_code == 0
    created_path = Path(result.stdout.strip())
    assert created_path.exists()
    content = created_path.read_text(encoding="utf-8")
    assert f"Date: {expected_date}" in content


def test_cli_new_accepts_date_option(tmp_path: Path, cli_runner: CliRunner) -> None:
    adr_dir = tmp_path / "adr"
    _init_repo(cli_runner, adr_dir)
    override_date = "2024-01-01"

    result = cli_runner.invoke(
        cli.app,
        [
            "new",
            "Explicit",
            "Date",
            "--dir",
            str(adr_dir),
            "--date",
            override_date,
        ],
    )
    assert result.exit_code == 0
    created_path = Path(result.stdout.strip())
    assert created_path.exists()
    content = created_path.read_text(encoding="utf-8")
    assert f"Date: {override_date}" in content


def test_cli_new_prefers_env_over_today(tmp_path: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    adr_dir = tmp_path / "adr"
    _init_repo(cli_runner, adr_dir)
    env_date = "2024-03-04"
    monkeypatch.setenv("ADR_DATE", env_date)

    result = cli_runner.invoke(
        cli.app,
        ["new", "Env", "Override", "--dir", str(adr_dir)],
    )
    assert result.exit_code == 0
    created_path = Path(result.stdout.strip())
    assert created_path.exists()
    content = created_path.read_text(encoding="utf-8")
    assert f"Date: {env_date}" in content


def test_cli_new_rejects_invalid_date(tmp_path: Path, cli_runner: CliRunner) -> None:
    adr_dir = tmp_path / "adr"
    _init_repo(cli_runner, adr_dir)
    invalid_date = "20240101"

    result = cli_runner.invoke(
        cli.app,
        [
            "new",
            "Bad",
            "Date",
            "--dir",
            str(adr_dir),
            "--date",
            invalid_date,
        ],
    )
    assert result.exit_code == 2
    expected_message = f"Invalid date format: {invalid_date}"
    assert expected_message in result.output

