from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch):
    for k in ("ADR_DATE", "DECREE_TZ", "ADR_TEMPLATE"):
        monkeypatch.delenv(k, raising=False)
    yield
