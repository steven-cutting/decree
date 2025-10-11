"""Core domain logic for manipulating ADR repositories."""

from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

from beartype import beartype

from .models import AdrRecord, AdrRef, AdrStatus
from .templates import DEFAULT_TEMPLATE, SEED_0001_TITLE
from .utils import resolve_date, slugify

ADR_DIR_DEFAULT = Path("doc") / "adr"

# Base relationships adapted from npryce/adr-tools for parity with its linking
# behavior.  We expand the mapping so either side of the relationship can be
# used as a key.  See https://github.com/npryce/adr-tools for reference.
_BASE_RELATIONS: dict[str, str] = {
    "Supersedes": "Is superseded by",
    "Amends": "Is amended by",
    "References": "Is referenced by",
}
REVERSE_MAP: dict[str, str] = {
    **_BASE_RELATIONS,
    **{v: k for k, v in _BASE_RELATIONS.items()},
    "Relates to": "Relates to",
}


def _resolve_reverse_relation(rel: str) -> str:
    return REVERSE_MAP.get(rel, f"Is {rel.lower()} by")


def link_adr(src: Path, rel: str, tgt: Path, *, reverse: bool = True) -> None:
    """Link two ADR markdown files mirroring npryce/adr-tools semantics."""

    def _link_single(file: Path, relation: str, target: Path) -> None:
        target_num = target.name.split("-", 1)[0]
        line = f"{relation}: {target_num}"
        existing = file.read_text(encoding="utf-8").splitlines()
        if line in existing:
            return
        with file.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"\n{line}\n")

    _link_single(src, rel, tgt)

    if reverse:
        _link_single(tgt, _resolve_reverse_relation(rel), src)


def unlink_adr(src: Path, rel: str, tgt: Path, *, reverse: bool = True) -> None:
    """Remove ADR links keeping parity with npryce/adr-tools behavior."""

    def _unlink_single(file: Path, relation: str, target: Path) -> None:
        target_num = target.name.split("-", 1)[0]
        line = f"{relation}: {target_num}"
        text = file.read_text(encoding="utf-8")
        lines = text.splitlines()
        for idx, value in enumerate(lines):
            if value == line:
                del lines[idx]
                if idx > 0 and lines[idx - 1] == "":
                    del lines[idx - 1]
                break
        else:
            return

        new_text = "\n".join(lines)
        if text.endswith("\n"):
            new_text += "\n"
        file.write_text(new_text, encoding="utf-8")

    _unlink_single(src, rel, tgt)

    if reverse:
        _unlink_single(tgt, _resolve_reverse_relation(rel), src)


class AdrLog:
    """High-level operations for working with ADR repositories."""

    def __init__(self, directory: Path) -> None:
        """Create an ADR log bound to ``directory``."""
        self.dir = directory

    @classmethod
    @beartype
    def init(cls, directory: Path | None = None) -> "AdrLog":
        """Initialise an ADR repository, seeding record 0001 when absent."""
        base = Path.cwd()
        adr_dir = (directory or (base / ADR_DIR_DEFAULT)).resolve()
        adr_dir.mkdir(parents=True, exist_ok=True)
        log = cls(adr_dir)
        first = adr_dir / "0001-record-architecture-decisions.md"
        if not first.exists():
            log._write(number=1, title=SEED_0001_TITLE, status=AdrStatus.Accepted)
        return log

    @beartype
    def new(
        self,
        title: str,
        *,
        status: AdrStatus = AdrStatus.Accepted,
        template: Path | None = None,
        date: str | None = None,
    ) -> AdrRecord:
        """Write a new ADR entry to disk and return the resulting record."""
        next_num = self._next_number()
        return self._write(next_num, title, status, template, date)

    @beartype
    def list(self) -> Iterator[AdrRecord]:
        """Yield all ADR records sorted by numeric identifier."""
        for path in sorted(self.dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            number = int(path.name[:4])
            title = _read_title(path)
            meta = _read_meta(path)
            yield AdrRecord(
                number=number,
                slug=path.stem.split("-", 1)[1],
                title=title,
                status=AdrStatus(meta.get("Status", "Accepted")),
                date=meta.get("Date", ""),
                path=path,
            )

    @beartype
    def link(self, src: AdrRef, rel: str, tgt: AdrRef, *, reverse: bool = False) -> None:
        """Link two ADRs optionally inserting the reverse relationship."""
        s = self._path_for(src.number)
        t = self._path_for(tgt.number)
        link_adr(s, rel, t, reverse=reverse)

    @beartype
    def unlink(self, src: AdrRef, rel: str, tgt: AdrRef, *, reverse: bool = False) -> None:
        """Remove a relationship between two ADRs."""
        s = self._path_for(src.number)
        t = self._path_for(tgt.number)
        unlink_adr(s, rel, t, reverse=reverse)

    @beartype
    def generate_toc(self) -> str:
        """Produce a Markdown table of contents for the ADR log."""
        lines = ["# Architecture decision records", ""]
        for rec in self.list():
            rel = rec.path.relative_to(self.dir)
            lines.append(
                f"- {rec.number:04d}. [{rec.title}]({rel.as_posix()}) — {rec.status} ({rec.date})",
            )
        return "\n".join(lines) + "\n"

    @beartype
    def upgrade(self) -> None:
        """Perform idempotent repository upgrade tasks."""
        if not self.dir.exists():
            message = f"{self.dir} does not exist"
            _raise(FileNotFoundError(message))
        (self.dir / ".decree").mkdir(exist_ok=True)
        (self.dir / ".decree" / "upgrade.marker").write_text("v1", encoding="utf-8")

    def _next_number(self) -> int:
        nums = [int(p.name[:4]) for p in self.dir.glob("[0-9][0-9][0-9][0-9]-*.md")]
        return (max(nums) + 1) if nums else 1

    def _path_for(self, number: int) -> Path:
        for p in self.dir.glob(f"{number:04d}-*.md"):
            return p
        message = f"ADR {number:04d} not found"
        raise FileNotFoundError(message)

    def _write(
        self,
        number: int,
        title: str,
        status: AdrStatus,
        template: Path | None = None,
        date: str | None = None,
    ) -> AdrRecord:
        slug = slugify(title)
        path = self.dir / f"{number:04d}-{slug}.md"
        tpl = template.read_text(encoding="utf-8") if template else DEFAULT_TEMPLATE
        record_date = resolve_date(cli_date=date)
        content = tpl.format(
            number=number,
            title=title,
            status=status.value,
            date=record_date,
        )
        path.write_text(content, encoding="utf-8", newline="\n")
        return AdrRecord(
            number=number,
            slug=slug,
            title=title,
            status=status,
            date=record_date,
            path=path,
        )


def _read_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            parts = line[2:].split(":", 1)
            parts_with_label = 2
            return parts[1].strip() if len(parts) == parts_with_label else parts[0].strip()
    return path.stem


def _read_meta(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Date: "):
            meta["Date"] = line.split(":", 1)[1].strip()
        elif line.startswith("Status: "):
            meta["Status"] = line.split(":", 1)[1].strip()
        if line.strip() == "" and "Date" in meta and "Status" in meta:
            break
    return meta


def _raise(exc: Exception) -> NoReturn:
    raise exc
