"""Update ``pyproject.toml`` using the most recent Git tag."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import which


def resolve_tag() -> str:
    """Return the version tag from the environment or the Git repository."""
    tag = os.getenv("GIT_TAG")
    if tag:
        return tag

    git_executable = which("git")
    if git_executable is None:
        message = "git executable is required to resolve tags"
        raise SystemExit(message)

    return subprocess.check_output(  # noqa: S603  # command uses absolute path from `which`
        [
            git_executable,
            "describe",
            "--tags",
            "--abbrev=0",
        ],
        text=True,
        encoding="utf-8",
    ).strip()


def main() -> None:
    """Write the resolved version into ``pyproject.toml``."""
    root = Path(__file__).resolve().parents[1]
    tag = resolve_tag()
    match = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
    if match is None:
        message = "Tag must look like vX.Y.Z"
        raise SystemExit(message)
    version = match.group(1)

    pyproject_path = root / "pyproject.toml"
    pyproject = pyproject_path.read_text(encoding="utf-8")
    updated = re.sub(
        r'(?m)^version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"\s*#.*$',
        f'version = "{version}"  # updated from tag',
        pyproject,
    )
    pyproject_path.write_text(updated, encoding="utf-8")
    sys.stdout.write(f"Set version to {version}\n")


if __name__ == "__main__":
    main()
