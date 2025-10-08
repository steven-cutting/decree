from __future__ import annotations

import os
import re
import unicodedata
from collections.abc import Callable, Mapping
from datetime import date


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-")


_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_date(value: str) -> str:
    if not _DATE_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid date format: {value}")
    return value


def resolve_date(
    *,
    cli_date: str | None = None,
    env: Mapping[str, str] | None = None,
    today: Callable[[], date] = date.today,
) -> str:
    actual_env: Mapping[str, str] = os.environ if env is None else env
    value = cli_date or actual_env.get("ADR_DATE")
    if value is None:
        value = today().isoformat()
    return _validate_date(value)
