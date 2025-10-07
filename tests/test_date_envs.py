import pytest

from decree.utils import resolve_date


def test_adr_date_verbatim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADR_DATE", "1999-12-31")
    assert resolve_date() == "1999-12-31"


def test_deceree_tz_changes_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DECREE_TZ", "UTC")
    d = resolve_date()
    assert len(d) == 10 and d[4] == "-" and d[7] == "-"
