"""Title management for Architecture Decision Records.

This module provides functionality for updating and synchronizing ADR titles,
including renaming files and updating cross-references throughout the ADR directory.
"""

import os
import re
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import click

from .utils import slugify


@dataclass
class TitleConfig:
    """Configuration for title update operations.

    Attributes:
        rename: Whether to rename ADR files to match their titles.

    """

    rename: bool = True


@dataclass
class ExecutionContext:
    """Context for executing title operations.

    Attributes:
        dry_run: If True, preview changes without writing.
        emit: Callback function to output messages.

    """

    dry_run: bool
    emit: Callable[[str], None]


@dataclass
class HeadingInfo:
    """Information extracted from an ADR heading line.

    Attributes:
        hashes: The hash marks (e.g., '##') indicating heading level.
        space: Whitespace between hash marks and content.
        prefix: Optional numeric or date prefix (e.g., '0001' or '2025-10-10').
        separator: Separator between prefix and title (e.g., '. ' or ': ').
        title: The actual title text.

    """

    hashes: str
    space: str
    prefix: str | None
    separator: str | None
    title: str


_HEADING_LINE_RE = re.compile(r"^(?P<hashes>#+)(?P<space>\s*)(?P<body>.*)$")
_PREFIX_RE = re.compile(
    r"^(?P<prefix>\d{4}(?:-\d{2}){1,2}|\d+)(?P<sep>\s*(?:[:.])\s+)(?P<title>.*)$"
)
_DATE_PREFIX_RE = re.compile(r"^(?P<prefix>\d{4}(?:-\d{2}){1,2})-(?P<rest>.+)$")
_NUMBER_PREFIX_RE = re.compile(r"^(?P<prefix>\d+)-(?!$)(?P<rest>.+)$")
_INLINE_LINK_RE = re.compile(r"(?P<prefix>!?\[[^\]]*\]\()(?P<target>[^)]+)(?P<suffix>\))")
_REFERENCE_LINK_RE = re.compile(r"(?m)^(?P<prefix>\[[^\]]+\]:\s*)(?P<target>\S+)(?P<suffix>.*)$")


class TitleError(click.ClickException):
    """Exception raised when title operations fail."""

    def __init__(self, message: str) -> None:
        """Initialize the error with a message.

        Args:
            message: Human-readable error description.

        """
        super().__init__(message)


def update_title(
    adr_dir: Path,
    target: str,
    new_title: str,
    *,
    rename: bool | None,
    ctx: ExecutionContext,
) -> None:
    """Update a single ADR title and optionally rename the file."""
    base = _resolve_adr_dir(adr_dir)
    config = _load_config(base)
    rename_flag = config.rename if rename is None else rename

    path = _resolve_target(base, target)

    if _mutate_heading(path, new_title, dry_run=ctx.dry_run):
        ctx.emit(f"Updated title in {path.relative_to(base)}")

    if rename_flag:
        new_path, renamed = _rename_to_slug(path, new_title, dry_run=ctx.dry_run)
        if renamed:
            ctx.emit(f"Renamed {path.name} -> {new_path.name}")
            if not ctx.dry_run:
                updated = _rewrite_links(base, path, new_path)
                for entry in updated:
                    ctx.emit(f"Updated links in {entry.relative_to(base)}")
            path = new_path


def sync_titles(
    adr_dir: Path,
    *,
    rename: bool | None,
    ctx: ExecutionContext,
) -> None:
    """Ensure ADR headings and filenames align with their titles."""
    base = _resolve_adr_dir(adr_dir)
    config = _load_config(base)
    rename_flag = config.rename if rename is None else rename

    for path in sorted(base.glob("*.md")):
        heading = _get_heading(path)
        file_prefix, file_slug = _split_name(path)

        title_text = heading.title if heading and heading.title else _title_from_slug(file_slug)

        if file_prefix and (heading is None or heading.prefix != file_prefix):
            if _mutate_heading(
                path,
                title_text,
                prefix=file_prefix,
                default_sep=heading.separator if heading else ": ",
                dry_run=ctx.dry_run,
            ):
                ctx.emit(f"Updated title in {path.relative_to(base)}")
            heading = _get_heading(path)

        if rename_flag:
            new_path, renamed = _rename_to_slug(
                path,
                title_text,
                prefix=file_prefix,
                dry_run=ctx.dry_run,
            )
            if renamed:
                ctx.emit(f"Renamed {path.name} -> {new_path.name}")
                if not ctx.dry_run:
                    updated = _rewrite_links(base, path, new_path)
                    for entry in updated:
                        ctx.emit(f"Updated links in {entry.relative_to(base)}")


def _resolve_adr_dir(adr_dir: Path) -> Path:
    base = Path(adr_dir)
    if not base.exists():
        msg = f"ADR directory {base} does not exist"
        raise TitleError(msg)
    if not base.is_dir():
        msg = f"ADR directory {base} is not a directory"
        raise TitleError(msg)
    return base


def _resolve_target(adr_dir: Path, target: str) -> Path:
    candidate = Path(target)
    search_paths: Iterable[Path]

    base = adr_dir.resolve()
    path = candidate if candidate.is_absolute() else (base / candidate).resolve()

    if path.exists():
        if not path.is_file():
            msg = f"Target {path} is not a file"
            raise TitleError(msg)
        if not path.resolve().is_relative_to(base):
            msg = f"Target {path} is outside the ADR directory"
            raise TitleError(msg)
        return path

    search_paths = list(adr_dir.glob(f"{target}.md"))
    if search_paths:
        return search_paths[0]

    if target.isdigit():
        formatted = f"{int(target):04d}"
        matches = list(adr_dir.glob(f"{formatted}-*.md"))
        if matches:
            return matches[0]

    matches = list(adr_dir.glob(f"*-{target}.md"))
    if matches:
        return matches[0]

    msg = f"Could not find ADR for target '{target}'"
    raise TitleError(msg)


def _mutate_heading(
    path: Path,
    new_title: str,
    *,
    prefix: str | None = None,
    default_sep: str | None = None,
    dry_run: bool,
) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    trailing_newline = original.endswith("\n")

    index = None
    info: HeadingInfo | None = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            index = idx
            info = _parse_heading_line(line)
            break

    if info is None:
        info = HeadingInfo("#", " ", prefix=None, separator=None, title="")
        new_line = _build_heading_line(info, new_title, prefix=prefix, default_sep=default_sep)
        if dry_run:
            return True
        lines = [new_line, *lines]
        text = "\n".join(lines)
        if trailing_newline or text:
            text += "\n"
        path.write_text(text, encoding="utf-8")
        return True

    if index is None:
        msg = f"Could not find heading in {path}"
        raise TitleError(msg)
    actual_prefix = prefix if prefix is not None else info.prefix
    new_line = _build_heading_line(info, new_title, prefix=actual_prefix, default_sep=default_sep)
    if lines[index] == new_line:
        return False
    if dry_run:
        return True
    lines[index] = new_line
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return True


def _build_heading_line(
    info: HeadingInfo,
    new_title: str,
    *,
    prefix: str | None,
    default_sep: str | None,
) -> str:
    space = info.space or " "
    if prefix:
        separator = info.separator if info.separator is not None else (default_sep or ": ")
        return f"{info.hashes}{space}{prefix}{separator}{new_title}"
    return f"{info.hashes}{space}{new_title}"


def _parse_heading_line(line: str) -> HeadingInfo:
    match = _HEADING_LINE_RE.match(line)
    if not match:
        return HeadingInfo("#", " ", prefix=None, separator=None, title=line.strip())
    space = match.group("space") or " "
    body = match.group("body").strip()
    prefix_match = _PREFIX_RE.match(body)
    if prefix_match:
        prefix = prefix_match.group("prefix")
        separator = prefix_match.group("sep")
        title = prefix_match.group("title").strip()
        return HeadingInfo(
            match.group("hashes"), space, prefix=prefix, separator=separator, title=title
        )
    return HeadingInfo(match.group("hashes"), space, prefix=None, separator=None, title=body)


def _rename_to_slug(
    path: Path,
    title: str,
    *,
    prefix: str | None = None,
    dry_run: bool,
) -> tuple[Path, bool]:
    slug = slugify(title)
    if not slug:
        slug = "adr"
    if prefix is None:
        name_prefix, _ = _split_name(path)
        prefix = name_prefix
    new_name = _compose_name(prefix, slug, path.suffix)
    new_path = path.with_name(new_name)
    if new_path == path:
        return path, False
    if not dry_run and new_path.exists():
        msg = f"Cannot rename {path.name} to {new_path.name}: target already exists"
        raise TitleError(msg)
    if dry_run:
        return new_path, True
    path.rename(new_path)
    return new_path, True


def _compose_name(prefix: str | None, slug: str, suffix: str) -> str:
    if prefix:
        return f"{prefix}-{slug}{suffix}"
    return f"{slug}{suffix}"


def _split_name(path: Path) -> tuple[str | None, str]:
    stem = path.stem
    if match := _DATE_PREFIX_RE.match(stem):
        return match.group("prefix"), match.group("rest")
    if match := _NUMBER_PREFIX_RE.match(stem):
        return match.group("prefix"), match.group("rest")
    return None, stem


def _get_heading(path: Path) -> HeadingInfo | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            return _parse_heading_line(line)
    return None


def _rewrite_links(base: Path, old_path: Path, new_path: Path) -> list[Path]:
    updated: list[Path] = []
    for entry in sorted(base.rglob("*.md")):
        original = entry.read_text(encoding="utf-8")
        candidates = _link_candidates(entry.parent, old_path)
        if not _needs_link_update(original, candidates):
            continue
        new_rel = Path(os.path.relpath(new_path, entry.parent)).as_posix()
        new_text = _replace_links(original, candidates, new_rel)
        if new_text != original:
            entry.write_text(new_text, encoding="utf-8")
            updated.append(entry)
    return updated


def _replace_links(text: str, candidates: set[str], new_rel: str) -> str:
    def inline(match: re.Match[str]) -> str:
        target = match.group("target")
        base, suffix = _split_suffix(target)
        if base in candidates:
            return f"{match.group('prefix')}{new_rel}{suffix}{match.group('suffix')}"
        return match.group(0)

    def reference(match: re.Match[str]) -> str:
        target = match.group("target")
        base, suffix = _split_suffix(target)
        if base in candidates:
            return f"{match.group('prefix')}{new_rel}{suffix}{match.group('suffix')}"
        return match.group(0)

    text = _INLINE_LINK_RE.sub(inline, text)
    return _REFERENCE_LINK_RE.sub(reference, text)


def _link_candidates(start: Path, old_path: Path) -> set[str]:
    rel = Path(os.path.relpath(old_path, start)).as_posix()
    candidates = {rel}
    if not rel.startswith("../"):
        candidates.add(f"./{rel}")
    return candidates


def _needs_link_update(text: str, candidates: set[str]) -> bool:
    return any(candidate in text for candidate in candidates)


def _split_suffix(target: str) -> tuple[str, str]:
    for marker in ("#", "?"):
        if marker in target:
            idx = target.find(marker)
            return target[:idx], target[idx:]
    return target, ""


def _title_from_slug(slug: str) -> str:
    parts = [segment for segment in slug.replace("_", "-").split("-") if segment]
    if not parts:
        return "ADR"
    return " ".join(part.capitalize() for part in parts)


def _load_config(adr_dir: Path) -> TitleConfig:
    cfg_dir = adr_dir / ".decree"
    cfg_path = cfg_dir / "config.toml"
    if not cfg_path.exists():
        return TitleConfig()
    try:
        data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - configuration errors are rare
        msg = f"Invalid configuration in {cfg_path}: {exc}"
        raise TitleError(msg) from exc
    title_cfg = data.get("title", {})
    rename = title_cfg.get("rename", True)
    if isinstance(rename, str):
        rename = rename.lower() in {"1", "true", "yes", "on"}
    elif not isinstance(rename, bool):
        rename = bool(rename)
    return TitleConfig(rename=bool(rename))
