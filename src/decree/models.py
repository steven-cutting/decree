from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterable


class AdrStatus(StrEnum):
    Accepted = "Accepted"
    Proposed = "Proposed"
    Superseded = "Superseded"
    Deprecated = "Deprecated"
    Rejected = "Rejected"


@dataclass(frozen=True, slots=True)
class AdrRef:
    number: int


@dataclass(frozen=True, slots=True)
class LinkSpec:
    src: AdrRef
    rel: str
    tgt: AdrRef
    reverse: bool = False


@dataclass(frozen=True, slots=True)
class AdrRecord:
    number: int
    slug: str
    title: str
    status: AdrStatus
    date: str
    path: Path


AdrList = Iterable[AdrRecord]
