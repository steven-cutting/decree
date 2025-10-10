from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from decree.cli import app

runner = CliRunner()


@pytest.fixture
def adr_dir() -> Iterator[Path]:
    with runner.isolated_filesystem():
        adr_dir = Path("doc") / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        yield adr_dir


def test_title_set_renames_and_rewrites_links(adr_dir: Path) -> None:
    (adr_dir / "0001-first-decision.md").write_text(
        "# 0001: First decision\n\nSee [other](0002-second-decision.md).\n",
        encoding="utf-8",
    )
    second = adr_dir / "0002-second-decision.md"
    second.write_text(
        "# 0002: Second\n\nBack to [first](0001-first-decision.md).\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["title", "set", "1", "Adopt", "New", "Title"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "Renamed 0001-first-decision.md -> 0001-adopt-new-title.md" in result.stdout
    assert "Updated links in 0002-second-decision.md" in result.stdout

    renamed = adr_dir / "0001-adopt-new-title.md"
    assert renamed.exists()
    assert "# 0001: Adopt New Title" in renamed.read_text(encoding="utf-8")
    assert "0001-adopt-new-title.md" in second.read_text(encoding="utf-8")


def test_title_set_respects_no_rename_and_config_default(adr_dir: Path) -> None:
    (adr_dir / "0003-sample.md").write_text("# 0003: Sample\n", encoding="utf-8")
    cfg_dir = adr_dir / ".decree"
    cfg_dir.mkdir()
    (cfg_dir / "config.toml").write_text("[title]\nrename = false\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["title", "set", "0003", "Config", "Rename"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "Renamed" not in result.stdout

    file_path = adr_dir / "0003-sample.md"
    assert file_path.exists()
    assert "# 0003: Config Rename" in file_path.read_text(encoding="utf-8")

    result_no_rename = runner.invoke(
        app,
        [
            "title",
            "set",
            "0003-sample.md",
            "Explicit",
            "No",
            "Rename",
            "--no-rename",
        ],
        catch_exceptions=False,
    )
    assert result_no_rename.exit_code == 0, result_no_rename.stdout
    assert "Renamed" not in result_no_rename.stdout
    assert "# 0003: Explicit No Rename" in file_path.read_text(encoding="utf-8")


def test_title_set_dry_run_leaves_files_unchanged(adr_dir: Path) -> None:
    source = adr_dir / "0005-dry-run.md"
    source.write_text("# 0005: Original\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["title", "set", "5", "Dry", "Run", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "DRY-RUN: Updated title" in result.stdout
    assert source.name == "0005-dry-run.md"
    assert "# 0005: Original" in source.read_text(encoding="utf-8")


def test_title_sync_updates_madr_links(adr_dir: Path) -> None:
    madr = adr_dir / "0007-old-madr.md"
    madr.write_text(
        "# 7. Revised Decision\n\nRefer to [summary](2021-06-15-summary.md).\n",
        encoding="utf-8",
    )
    summary = adr_dir / "2021-06-15-summary.md"
    summary.write_text(
        "# Summary\n\nSee [decision](0007-old-madr.md).\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["title", "sync"], catch_exceptions=False)
    assert result.exit_code == 0, result.stdout
    assert "Renamed 0007-old-madr.md -> 0007-revised-decision.md" in result.stdout
    assert "Updated links in 2021-06-15-summary.md" in result.stdout

    madr_new = adr_dir / "0007-revised-decision.md"
    assert madr_new.exists()
    assert "# 0007. Revised Decision" in madr_new.read_text(encoding="utf-8")
    assert "0007-revised-decision.md" in summary.read_text(encoding="utf-8")


def test_title_sync_updates_log4brains_links(adr_dir: Path) -> None:
    log4brains = adr_dir / "2020-05-01-legacy-architecture.md"
    log4brains.write_text(
        "# Modern Architecture\n\nSee [decision](0007-revised-decision.md).\n",
        encoding="utf-8",
    )
    other = adr_dir / "2021-06-15-summary.md"
    other.write_text(
        (
            "# Summary\n\nReview [architecture](2020-05-01-legacy-architecture.md) "
            "and [log](2020-05-01-legacy-architecture.md#section).\n"
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["title", "sync"], catch_exceptions=False)
    assert result.exit_code == 0, result.stdout
    assert (
        "Renamed 2020-05-01-legacy-architecture.md -> 2020-05-01-modern-architecture.md"
        in result.stdout
    )
    assert "Updated links in 2021-06-15-summary.md" in result.stdout

    log_new = adr_dir / "2020-05-01-modern-architecture.md"
    assert log_new.exists()
    assert "# 2020-05-01: Modern Architecture" in log_new.read_text(encoding="utf-8")

    other_text = other.read_text(encoding="utf-8")
    assert "2020-05-01-modern-architecture.md" in other_text
    assert "2020-05-01-modern-architecture.md#section" in other_text
