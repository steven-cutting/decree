from pathlib import Path

from decree.core import AdrLog
from decree.models import AdrRef


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_link_with_reverse_adds_bidirectional_relationships(tmp_path: Path) -> None:
    log = AdrLog.init(tmp_path / "doc" / "adr")
    src_record = log.new("Prefer dedicated reverse link helper")
    tgt_record = log.new("Adopt unlink parity")

    src_ref = AdrRef(src_record.number)
    tgt_ref = AdrRef(tgt_record.number)

    log.link(src_ref, "Supersedes", tgt_ref, reverse=True)
    log.link(src_ref, "Supersedes", tgt_ref, reverse=True)

    src_lines = _read_lines(src_record.path)
    tgt_lines = _read_lines(tgt_record.path)

    forward_line = f"Supersedes: {tgt_record.number:04d}"
    reverse_line = f"Is superseded by: {src_record.number:04d}"

    assert src_lines.count(forward_line) == 1
    assert tgt_lines.count(reverse_line) == 1


def test_unlink_with_reverse_removes_relationships(tmp_path: Path) -> None:
    log = AdrLog.init(tmp_path / "doc" / "adr")
    src_record = log.new("Create bidirectional links by default")
    tgt_record = log.new("Document unlink expectations")

    src_ref = AdrRef(src_record.number)
    tgt_ref = AdrRef(tgt_record.number)

    log.link(src_ref, "References", tgt_ref, reverse=True)
    log.unlink(src_ref, "References", tgt_ref, reverse=True)

    src_text = src_record.path.read_text(encoding="utf-8")
    tgt_text = tgt_record.path.read_text(encoding="utf-8")

    assert "References:" not in src_text
    assert "Is referenced by:" not in tgt_text
    assert src_text.endswith("\n")
    assert tgt_text.endswith("\n")


def test_link_then_unlink_restores_original_content(tmp_path: Path) -> None:
    log = AdrLog.init(tmp_path / "doc" / "adr")
    src_record = log.new("Preserve file content when unlinking")
    tgt_record = log.new("Ensure unlink only removes targeted relation")

    src_ref = AdrRef(src_record.number)
    tgt_ref = AdrRef(tgt_record.number)

    original_src = src_record.path.read_text(encoding="utf-8")
    original_tgt = tgt_record.path.read_text(encoding="utf-8")

    log.link(src_ref, "Relates to", tgt_ref, reverse=True)
    log.unlink(src_ref, "Relates to", tgt_ref, reverse=True)

    assert src_record.path.read_text(encoding="utf-8") == original_src
    assert tgt_record.path.read_text(encoding="utf-8") == original_tgt
