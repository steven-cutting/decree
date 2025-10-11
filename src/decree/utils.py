"""Utility helpers for string normalization and configuration resolution."""

import os
import re
from collections.abc import Callable, Mapping
from datetime import date

from boltons.strutils import slugify as _boltons_slugify

_NON_SLUG_CHARS = re.compile(r"[^a-z0-9-]+")
_HYPHEN_NORMALIZER = re.compile(r"-+")


def slugify(title: str) -> str:
    """Return a filesystem-friendly slug for ``title``."""
    slug_text: str = _boltons_slugify(title, delim="-", lower=True, ascii=True).decode("ascii")
    slug_text = _NON_SLUG_CHARS.sub("-", slug_text)
    return _HYPHEN_NORMALIZER.sub("-", slug_text).strip("-")


_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_date(value: str) -> str:
    if not _DATE_PATTERN.fullmatch(value):
        message = f"Invalid date format: {value}"
        raise ValueError(message)
    return value


def resolve_date(
    *,
    cli_date: str | None = None,
    env: Mapping[str, str] | None = None,
    today: Callable[[], date] = date.today,
) -> str:
    """Resolve the ADR date using CLI input, environment overrides, or the system clock."""
    actual_env: Mapping[str, str] = os.environ if env is None else env
    value = cli_date or actual_env.get("ADR_DATE")
    if value is None:
        value = today().isoformat()
    return _validate_date(value)
