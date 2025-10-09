from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for older runtimes
    import tomli as tomllib  # type: ignore[no-redef]


def load_project_version(pyproject_path: Path) -> str:
    with pyproject_path.open("rb") as pyproject_file:
        data = tomllib.load(pyproject_file)

    try:
        return data["project"]["version"]
    except KeyError as exc:  # pragma: no cover - defensive
        missing_path = " -> ".join(str(part) for part in exc.args)
        raise SystemExit(
            f"Unable to read project version at 'project.version' ({missing_path})."
        ) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that a release tag matches the project's declared version.",
    )
    parser.add_argument(
        "tag",
        help="Release tag to validate against the project version.",
    )
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=Path("pyproject.toml"),
        help="Path to the pyproject.toml file (default: %(default)s).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    version = load_project_version(args.pyproject)

    if args.tag != version:
        raise SystemExit(
            f"Tag {args.tag!r} does not match project version {version!r}."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
