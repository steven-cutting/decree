from __future__ import annotations

import importlib

import click
import pytest

from decree import cli
from decree.exitcodes import ExitCode


@pytest.mark.parametrize(
    ("exc", "expected", "message"),
    [
        (click.UsageError("bad usage"), ExitCode.USAGE_ERROR, "bad usage"),
        (click.Abort(), ExitCode.GENERAL_ERROR, "Aborted!"),
        (click.ClickException("boom"), ExitCode.GENERAL_ERROR, "boom"),
        (FileNotFoundError("missing"), ExitCode.INPUT_MISSING, "missing"),
        (OSError("busy"), ExitCode.UNAVAILABLE, "busy"),
        (KeyboardInterrupt(), ExitCode.GENERAL_ERROR, "Aborted!"),
        (RuntimeError("explode"), ExitCode.GENERAL_ERROR, "explode"),
    ],
)
def test_main_exception_handling(
    exc: BaseException,
    expected: ExitCode,
    message: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_app(*, standalone_mode: bool) -> None:
        _ = standalone_mode
        raise exc

    monkeypatch.setattr(cli, "app", fake_app)

    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == int(expected)
    stderr = capsys.readouterr().err
    if isinstance(exc, click.ClickException):
        assert message in stderr
    else:
        assert message in stderr


def test_main_module_importable() -> None:
    module = importlib.import_module("decree.__main__")
    assert module.main is cli.main
