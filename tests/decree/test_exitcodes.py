import pytest

from decree.exitcodes import ExitCode, exit_with


def test_exit_with_message(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        exit_with(ExitCode.GENERAL_ERROR, "boom")
    assert excinfo.value.code == int(ExitCode.GENERAL_ERROR)
    captured = capsys.readouterr()
    assert captured.err.strip() == "boom"
