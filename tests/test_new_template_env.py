from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from decree.cli import app

runner = CliRunner()


def _ensure_adr_dir(base: Path) -> Path:
    target = base / "doc" / "adr"
    target.mkdir(parents=True, exist_ok=True)
    return target


def _read_created_path(result_stdout: str) -> Path:
    created = Path(result_stdout.strip())
    assert created.exists()
    return created


def test_new_uses_template_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target_dir = _ensure_adr_dir(tmp_path)
    template_path = tmp_path / "template-env.md"
    sentinel = "__ENV_SENTINEL__"
    template_path.write_text(f"{sentinel}\n", encoding="utf-8")
    monkeypatch.setenv("ADR_TEMPLATE", str(template_path))

    result = runner.invoke(app, ["new", "--dir", str(target_dir), "Env", "First"])

    assert result.exit_code == 0, result.stderr
    created_path = _read_created_path(result.stdout)
    content = created_path.read_text(encoding="utf-8")
    assert sentinel in content


def test_cli_template_overrides_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target_dir = _ensure_adr_dir(tmp_path)
    env_template = tmp_path / "template-env.md"
    env_template.write_text("__ENV_ONLY__\n", encoding="utf-8")
    cli_template = tmp_path / "template-cli.md"
    cli_sentinel = "__CLI_SENTINEL__"
    cli_template.write_text(f"{cli_sentinel}\n", encoding="utf-8")
    monkeypatch.setenv("ADR_TEMPLATE", str(env_template))

    result = runner.invoke(
        app,
        [
            "new",
            "--dir",
            str(target_dir),
            "--template",
            str(cli_template),
            "Cli",
            "Wins",
        ],
    )

    assert result.exit_code == 0, result.stderr
    created_path = _read_created_path(result.stdout)
    content = created_path.read_text(encoding="utf-8")
    assert cli_sentinel in content
    assert "__ENV_ONLY__" not in content


def test_new_uses_default_template_when_not_overridden(tmp_path: Path) -> None:
    target_dir = _ensure_adr_dir(tmp_path)

    result = runner.invoke(
        app,
        ["new", "--dir", str(target_dir), "Default", "Template"],
    )

    assert result.exit_code == 0, result.stderr
    created_path = _read_created_path(result.stdout)
    content = created_path.read_text(encoding="utf-8")
    assert "__ENV_SENTINEL__" not in content
    assert "__CLI_SENTINEL__" not in content


def test_new_errors_on_missing_template_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target_dir = _ensure_adr_dir(tmp_path)
    missing = tmp_path / "missing-template.md"
    monkeypatch.setenv("ADR_TEMPLATE", str(missing))

    result = runner.invoke(
        app,
        ["new", "--dir", str(target_dir), "Missing", "Template"],
    )

    assert result.exit_code != 0
    output = result.stderr
    assert str(missing.resolve()) in output
    assert "Template" in output
