from __future__ import annotations

from pathlib import Path

import pytest

from decree.title import (
    HeadingInfo,
    TitleError,
    _build_heading_line,
    _link_candidates,
    _load_config,
    _mutate_heading,
    _needs_link_update,
    _rename_to_slug,
    _replace_links,
    _resolve_adr_dir,
    _resolve_target,
    _split_name,
    _split_suffix,
    _title_from_slug,
)


def test_resolve_adr_dir_validation(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(TitleError):
        _resolve_adr_dir(missing)

    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")
    with pytest.raises(TitleError):
        _resolve_adr_dir(file_path)


def test_resolve_target_variants(tmp_path: Path) -> None:
    adr_dir = tmp_path / "adr"
    adr_dir.mkdir()
    first = adr_dir / "0001-first-choice.md"
    first.write_text("# Heading\n", encoding="utf-8")
    dated = adr_dir / "2024-01-02-winter-plan.md"
    dated.write_text("# Plan\n", encoding="utf-8")

    assert _resolve_target(adr_dir, "0001-first-choice.md") == first
    assert _resolve_target(adr_dir, "1") == first
    assert _resolve_target(adr_dir, "first-choice") == first
    assert _resolve_target(adr_dir, str(first.resolve())) == first.resolve()
    assert _resolve_target(adr_dir, "2024-01-02-winter-plan") == dated

    nested_dir = adr_dir / "nested"
    nested_dir.mkdir()
    with pytest.raises(TitleError):
        _resolve_target(adr_dir, str(nested_dir))
    with pytest.raises(TitleError):
        _resolve_target(adr_dir, "does-not-exist")


def test_mutate_heading_variants(tmp_path: Path) -> None:
    without_heading = tmp_path / "no-heading.md"
    without_heading.write_text("Body only\n", encoding="utf-8")
    assert _mutate_heading(without_heading, "Inserted", dry_run=False)
    assert without_heading.read_text(encoding="utf-8").startswith("# Inserted")

    dry_run_path = tmp_path / "dry-run.md"
    dry_run_path.write_text("Body\n", encoding="utf-8")
    original = dry_run_path.read_text(encoding="utf-8")
    assert _mutate_heading(dry_run_path, "Preview", dry_run=True)
    assert dry_run_path.read_text(encoding="utf-8") == original

    prefixed = tmp_path / "prefixed.md"
    prefixed.write_text("# 0005: Old\n", encoding="utf-8")
    assert _mutate_heading(prefixed, "New", prefix="0005", dry_run=False)
    assert "# 0005: New" in prefixed.read_text(encoding="utf-8")

    unchanged = tmp_path / "unchanged.md"
    unchanged.write_text("# Title\n", encoding="utf-8")
    assert not _mutate_heading(unchanged, "Title", dry_run=False)


def test_build_heading_line_with_prefix() -> None:
    info = HeadingInfo("#", " ", prefix=None, separator=None, title="Old")
    assert _build_heading_line(info, "New", prefix="0007", default_sep=": ") == "# 0007: New"


def test_rename_to_slug_conflicts(tmp_path: Path) -> None:
    source = tmp_path / "0008-source.md"
    source.write_text("content", encoding="utf-8")
    existing = tmp_path / "0008-existing-slug.md"
    existing.write_text("content", encoding="utf-8")

    with pytest.raises(TitleError):
        _rename_to_slug(source, "Existing Slug", dry_run=False)

    dry_run_target = tmp_path / "0010-dry-run.md"
    dry_run_target.write_text("content", encoding="utf-8")
    new_path, renamed = _rename_to_slug(dry_run_target, "Preview", dry_run=True)
    assert renamed and new_path.name.endswith("preview.md")
    assert dry_run_target.exists()


def test_split_name_helpers(tmp_path: Path) -> None:
    dated = tmp_path / "2023-07-01-example.md"
    dated.write_text("# Title\n", encoding="utf-8")
    numbered = tmp_path / "0002-example.md"
    numbered.write_text("# Title\n", encoding="utf-8")
    plain = tmp_path / "plain.md"
    plain.write_text("# Title\n", encoding="utf-8")

    assert _split_name(dated) == ("2023-07-01", "example")
    assert _split_name(numbered) == ("0002", "example")
    assert _split_name(plain) == (None, "plain")


def test_link_rewrite_helpers(tmp_path: Path) -> None:
    base = tmp_path
    old_path = base / "old.md"
    new_path = base / "new.md"
    old_path.write_text("", encoding="utf-8")
    new_path.write_text("", encoding="utf-8")

    text = (
        "See [inline](old.md) and reference [ref][ref].\n\n"
        "[ref]: ./old.md#anchor\n"
        "Keep other links untouched.\n"
    )
    candidates = _link_candidates(base, old_path)
    assert _needs_link_update(text, candidates)
    rewritten = _replace_links(text, candidates, "new.md")
    assert "(new.md)" in rewritten
    assert "[ref]: new.md#anchor" in rewritten

    assert not _needs_link_update("No match", candidates)
    suffixed, suffix = _split_suffix("target.md?query")
    assert suffixed == "target.md" and suffix == "?query"


def test_title_from_slug_and_config(tmp_path: Path) -> None:
    assert _title_from_slug("modern-arch") == "Modern Arch"
    assert _title_from_slug("___") == "ADR"

    cfg_dir = tmp_path / ".decree"
    cfg_dir.mkdir()
    (cfg_dir / "config.toml").write_text("[title]\nrename = 'yes'\n", encoding="utf-8")
    config = _load_config(tmp_path)
    assert config.rename is True

    (cfg_dir / "config.toml").write_text("[title]\nrename = 0\n", encoding="utf-8")
    config_false = _load_config(tmp_path)
    assert config_false.rename is False
