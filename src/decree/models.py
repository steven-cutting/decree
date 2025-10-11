"""Data structures used throughout the Decree package."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class AdrStatus(StrEnum):
    """Permitted lifecycle states for an architecture decision record."""

    Accepted = "Accepted"
    Proposed = "Proposed"
    Superseded = "Superseded"
    Deprecated = "Deprecated"
    Rejected = "Rejected"


@dataclass(frozen=True, slots=True)
class AdrRef:
    """Reference to an ADR by its numeric identifier."""

    number: int


@dataclass(frozen=True, slots=True)
class LinkSpec:
    """Relationship request between two ADRs."""

    src: AdrRef
    rel: str
    tgt: AdrRef
    reverse: bool = False


@dataclass(frozen=True, slots=True)
class AdrRecord:
    """Materialized ADR entry as persisted on disk."""

    number: int
    slug: str
    title: str
    status: AdrStatus
    date: str
    path: Path


AdrList = Iterable[AdrRecord]
