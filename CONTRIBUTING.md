
# contributing

* setup: `pip install uv && uv sync --all-extras --dev`
* checks: `uv run nox -s lint typecheck tests`
* style: ruff, mypy strict; no private telemetry
* tests: use `tmp_path`, avoid heavy mocking
* release: tag `vX.Y.Z` on `main`; CI builds and publishes to PyPI
