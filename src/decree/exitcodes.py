"""Utilities for consistent CLI exit codes."""

import os
import sys
from enum import IntEnum
from typing import NoReturn

try:
    _EX_OK = int(os.EX_OK)
except AttributeError:  # pragma: no cover - platform-specific branch
    _EX_OK = 0

try:
    _EX_USAGE = int(os.EX_USAGE)
except AttributeError:  # pragma: no cover - platform-specific branch
    _EX_USAGE = 2

try:
    _EX_NOINPUT = int(os.EX_NOINPUT)
except AttributeError:  # pragma: no cover - platform-specific branch
    _EX_NOINPUT = 66

try:
    _EX_UNAVAILABLE = int(os.EX_UNAVAILABLE)
except AttributeError:  # pragma: no cover - platform-specific branch
    _EX_UNAVAILABLE = 69

try:
    _EX_CONFIG = int(os.EX_CONFIG)
except AttributeError:  # pragma: no cover - platform-specific branch
    _EX_CONFIG = 78


class ExitCode(IntEnum):
    """Portable exit codes aligned with ``sysexits`` where available."""

    SUCCESS = _EX_OK
    GENERAL_ERROR = 1
    USAGE_ERROR = _EX_USAGE
    INPUT_MISSING = _EX_NOINPUT
    UNAVAILABLE = _EX_UNAVAILABLE
    CONFIG_ERROR = _EX_CONFIG


def exit_with(code: ExitCode, msg: str | None = None) -> NoReturn:
    """Exit the interpreter with ``code`` optionally emitting ``msg`` to stderr."""
    if msg:
        sys.stderr.write(f"{msg}\n")
    raise SystemExit(int(code))


__all__ = ["ExitCode", "exit_with"]
