from __future__ import annotations

import os
import re
import unicodedata
from collections.abc import Mapping
from datetime import datetime
from zoneinfo import ZoneInfo


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-")


def resolve_date(env: Mapping[str, str] | None = None) -> str:
    actual_env: Mapping[str, str] = os.environ if env is None else env
    if d := actual_env.get("ADR_DATE"):
        return d
    tz = actual_env.get("DECREE_TZ", "UTC")
    return datetime.now(ZoneInfo(tz)).strftime("%Y-%m-%d")
