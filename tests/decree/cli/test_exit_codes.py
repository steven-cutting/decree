from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from decree.exitcodes import ExitCode

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
CLI = [sys.executable, "-m", "decree"]


def _build_env(extra_env: dict[str, str] | None, python_paths: list[str] | None) -> dict[str, str]:
    env = os.environ.copy()
    paths: list[str] = []
    if python_paths:
        paths.extend(python_paths)
    paths.append(str(SRC_DIR))
    existing = env.get("PYTHONPATH")
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(p for p in paths if p)
    if extra_env:
        for key, value in extra_env.items():
            if key == "PYTHONPATH":
                continue
            env[key] = value
    return env


def run_cli(
    cwd: Path,
    *args: str,
    env: dict[str, str] | None = None,
    python_paths: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [*CLI, *args]
    final_env = _build_env(env or {}, python_paths)
    return subprocess.run(  # noqa: S603 - command is built from trusted arguments
        command,
        check=False,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=final_env,
    )


@pytest.mark.parametrize(
    ("args", "expected_code"),
    [
        (("--help",), ExitCode.SUCCESS),
        (("generate",), ExitCode.USAGE_ERROR),
    ],
)
def test_basic_invocations(tmp_path: Path, args: tuple[str, ...], expected_code: ExitCode) -> None:
    result = run_cli(tmp_path, *args)
    assert result.returncode == int(expected_code)
    assert "Traceback" not in result.stderr


def test_missing_input_path(tmp_path: Path) -> None:
    target = tmp_path / "missing"
    result = run_cli(
        tmp_path,
        "link",
        "1",
        "Relates to",
        "2",
        "--dir",
        str(target),
    )
    assert result.returncode == int(ExitCode.INPUT_MISSING)
    assert "Traceback" not in result.stderr


def test_invalid_configuration(tmp_path: Path) -> None:
    init = run_cli(tmp_path, "init")
    assert init.returncode == int(ExitCode.SUCCESS)

    env = {"ADR_DATE": "bad-date"}
    result = run_cli(tmp_path, "new", "Example", env=env)
    assert result.returncode == int(ExitCode.CONFIG_ERROR)
    assert "Invalid date format" in result.stderr
    assert "Traceback" not in result.stderr


def test_service_unavailable(tmp_path: Path) -> None:
    bad_dir = tmp_path / "adr-file"
    bad_dir.write_text("not a directory", encoding="utf-8")
    result = run_cli(tmp_path, "new", "Example", "--dir", str(bad_dir))
    assert result.returncode == int(ExitCode.UNAVAILABLE)
    assert "Traceback" not in result.stderr


def test_runtime_failure_maps_to_general_error(tmp_path: Path) -> None:
    sitecustomize = tmp_path / "sitecustomize.py"
    sitecustomize.write_text(
        "import decree.core\n"
        "def _boom(*_args, **_kwargs):\n"
        "    raise RuntimeError('boom')\n"
        "decree.core.AdrLog.list = _boom\n",
        encoding="utf-8",
    )
    result = run_cli(tmp_path, "list", python_paths=[str(tmp_path)])
    assert result.returncode == int(ExitCode.GENERAL_ERROR)
    assert "boom" in result.stderr
    assert "Traceback" not in result.stderr


def test_keyboard_interrupt_maps_to_abort(tmp_path: Path) -> None:
    sitecustomize = tmp_path / "sitecustomize.py"
    sitecustomize.write_text(
        "import click\n"
        "import decree.core\n"
        "def _abort(*_args, **_kwargs):\n"
        "    raise click.Abort()\n"
        "decree.core.AdrLog.list = _abort\n",
        encoding="utf-8",
    )
    result = run_cli(tmp_path, "list", python_paths=[str(tmp_path)])
    assert result.returncode == int(ExitCode.GENERAL_ERROR)
    assert "Aborted!" in result.stderr
    assert "Traceback" not in result.stderr


def test_generate_graph_reports_unavailable(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "generate", "graph")
    assert result.returncode == int(ExitCode.UNAVAILABLE)
    assert "not implemented" in result.stderr
    assert "Traceback" not in result.stderr
