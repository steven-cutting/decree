from __future__ import annotations

from collections.abc import Iterable
from typing import NoReturn
from pathlib import Path

from beartype import beartype

from .models import AdrRecord, AdrRef, AdrStatus
from .templates import DEFAULT_TEMPLATE, SEED_0001_TITLE
from .utils import resolve_date, slugify

ADR_DIR_DEFAULT = Path("doc") / "adr"


class AdrLog:
    def __init__(self, dir: Path):
        self.dir = dir

    @classmethod
    @beartype
    def init(cls, dir: Path | None = None) -> AdrLog:
        base = Path.cwd()
        adr_dir = (dir or (base / ADR_DIR_DEFAULT)).resolve()
        adr_dir.mkdir(parents=True, exist_ok=True)
        log = cls(adr_dir)
        first = adr_dir / "0001-record-architecture-decisions.md"
        if not first.exists():
            rec = log._write(number=1, title=SEED_0001_TITLE, status=AdrStatus.Accepted)
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
        next_num = self._next_number()
        return self._write(next_num, title, status, template, date)

    @beartype
    def list(self) -> Iterable[AdrRecord]:
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
        s = self._path_for(src.number)
        t = self._path_for(tgt.number)
        _append_link_line(s, rel, t)
        if reverse:
            _append_link_line(t, _reverse_rel(rel), s)

    @beartype
    def generate_toc(self) -> str:
        lines = ["# Architecture decision records", ""]
        for rec in self.list():
            rel = rec.path.relative_to(self.dir)
            lines.append(
                f"- {rec.number:04d}. [{rec.title}]({rel.as_posix()}) — {rec.status} ({rec.date})"
            )
        return "\n".join(lines) + "\n"

    @beartype
    def upgrade(self) -> None:
        self.dir.exists() or (_raise(FileNotFoundError(f"{self.dir} does not exist")))
        (self.dir / ".decree").mkdir(exist_ok=True)
        (self.dir / ".decree" / "upgrade.marker").write_text("v1", encoding="utf-8")

    def _next_number(self) -> int:
        nums = [int(p.name[:4]) for p in self.dir.glob("[0-9][0-9][0-9][0-9]-*.md")]
        return (max(nums) + 1) if nums else 1

    def _path_for(self, number: int) -> Path:
        for p in self.dir.glob(f"{number:04d}-*.md"):
            return p
        raise FileNotFoundError(f"ADR {number:04d} not found")

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
        record_date = date or resolve_date()
        content = tpl.format(
            number=number,
            title=title,
            status=status.value,
            date=record_date,
        )
        path.write_text(content, encoding="utf-8", newline="\n")
        return AdrRecord(
            number=number, slug=slug, title=title, status=status, date=record_date, path=path
        )


def _read_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            parts = line[2:].split(":", 1)
            return parts[1].strip() if len(parts) == 2 else parts[0].strip()
    return path.stem


def _read_meta(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Date: "):
            meta["Date"] = line.split(":", 1)[1].strip()
        elif line.startswith("Status: "):
            meta["Status"] = line.split(":", 1)[1].strip()
        if line.strip() == "":
            if "Date" in meta and "Status" in meta:
                break
    return meta


def _append_link_line(file: Path, rel: str, target: Path) -> None:
    target_num = target.name.split("-", 1)[0]
    with file.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(f"\n{rel}: {target_num}\n")


def _reverse_rel(rel: str) -> str:
    mapping = {"Supersedes": "Superseded by", "Amends": "Amended by"}
    return mapping.get(rel, f"{rel} (reverse)")


def _raise(exc: Exception) -> NoReturn:
    raise exc
