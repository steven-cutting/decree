from __future__ import annotations

import os
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-")


def resolve_date(env: dict[str, str] | None = None) -> str:
    env = env or os.environ
    if (d := env.get("ADR_DATE")):
        return d
    tz = env.get("DECREE_TZ", "UTC")
    return datetime.now(ZoneInfo(tz)).strftime("%Y-%m-%d")
