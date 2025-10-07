from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for k in ("ADR_DATE", "DECREE_TZ", "ADR_TEMPLATE"):
        monkeypatch.delenv(k, raising=False)
    yield
