from pathlib import Path

from decree.core import AdrLog


def test_init_seeds_0001(tmp_path: Path):
    log = AdrLog.init(tmp_path / "doc" / "adr")
    p = tmp_path / "doc" / "adr" / "0001-record-architecture-decisions.md"
    assert p.exists()
