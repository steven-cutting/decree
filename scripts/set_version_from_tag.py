from __future__ import annotations

import os
import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
tag = (
    os.getenv("GIT_TAG")
    or subprocess.check_output(
        [
            "git",
            "describe",
            "--tags",
            "--abbrev=0",
        ]
    )
    .decode()
    .strip()
)
m = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
if not m:
    raise SystemExit("Tag must look like vX.Y.Z")
version = m.group(1)

pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
pyproject = re.sub(
    r'(?m)^version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"\s*#.*$',
    f'version = "{version}"  # updated from tag',
    pyproject,
)
(root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
print(f"Set version to {version}")
