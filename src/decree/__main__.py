"""Command-line entrypoint for ``python -m decree``."""

from .cli import main

# The module-level entrypoint is invoked by ``python -m decree`` which runs in a
# separate interpreter process during integration tests. Coverage from that
# subprocess is not collected, so we explicitly exclude the guard from metrics.
if __name__ == "__main__":  # pragma: no cover - exercised via subprocess CLI
    main()
