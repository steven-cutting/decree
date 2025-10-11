from pathlib import Path

from decree.core import AdrLog
from decree.models import AdrStatus


def test_new_list_and_toc(tmp_path: Path) -> None:
    log = AdrLog.init(tmp_path / "doc" / "adr")
    log.new("Use beartype on public API", status=AdrStatus.Accepted)
    rows = list(log.list())
    expected_records = 2
    assert len(rows) == expected_records
    assert rows[1].number == expected_records
    toc = log.generate_toc()
    assert "Use beartype on public API" in toc
