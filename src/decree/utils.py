"""Utility helpers for string normalization and configuration resolution."""

from __future__ import annotations

import os
import re
import typing
import unicodedata
from datetime import date


def slugify(title: str) -> str:
    """Return a filesystem-friendly slug for ``title``."""
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-")


_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_date(value: str) -> str:
    if not _DATE_PATTERN.fullmatch(value):
        message = f"Invalid date format: {value}"
        raise ValueError(message)
    return value


def resolve_date(
    *,
    cli_date: str | None = None,
    env: typing.Mapping[str, str] | None = None,
    today: typing.Callable[[], date] = date.today,
) -> str:
    """Resolve the ADR date using CLI input, environment overrides, or the system clock."""
    actual_env: typing.Mapping[str, str] = os.environ if env is None else env
    value = cli_date or actual_env.get("ADR_DATE")
    if value is None:
        value = today().isoformat()
    return _validate_date(value)
