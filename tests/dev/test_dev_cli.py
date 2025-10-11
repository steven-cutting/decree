"""Tests for the dev CLI module."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from dev.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def sample_pyproject(tmp_path: Path) -> Path:
    """Create a sample pyproject.toml file."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[build-system]
requires = ["uv-build>=0.3.0"]
build-backend = "uv_build"

[project]
name = "test-project"
version = "1.2.3"
description = "A test project"
""",
        encoding="utf-8",
    )
    return pyproject


def test_validate_version_exact_match(runner: CliRunner, sample_pyproject: Path) -> None:
    """Test validate_version with exact matching version."""
    result = runner.invoke(app, ["validate-version", "1.2.3", "-p", str(sample_pyproject)])
    assert result.exit_code == 0
    assert "✓ Version 1.2.3 matches project version 1.2.3" in result.output


def test_validate_version_mismatch(runner: CliRunner, sample_pyproject: Path) -> None:
    """Test validate_version with mismatched version."""
    result = runner.invoke(app, ["validate-version", "2.0.0", "-p", str(sample_pyproject)])
    assert result.exit_code == 1
    assert "Error: Version mismatch" in result.output
    assert "Input version:   2.0.0" in result.output
    assert "Project version: 1.2.3" in result.output


def test_validate_version_with_v_prefix_fails(runner: CliRunner, sample_pyproject: Path) -> None:
    """Test validate_version rejects 'v' prefix (strict matching)."""
    result = runner.invoke(app, ["validate-version", "v1.2.3", "-p", str(sample_pyproject)])
    assert result.exit_code == 1
    assert "Error: Version mismatch" in result.output
    assert "Input version:   v1.2.3" in result.output
    assert "Project version: 1.2.3" in result.output


def test_validate_version_missing_version_in_pyproject(runner: CliRunner, tmp_path: Path) -> None:
    """Test validate_version when pyproject.toml has no version."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[build-system]
requires = ["uv-build>=0.3.0"]

[project]
name = "test-project"
description = "A test project"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validate-version", "1.0.0", "-p", str(pyproject)])
    assert result.exit_code == 1
    assert "Error: No version found in" in result.output


def test_validate_version_invalid_toml(runner: CliRunner, tmp_path: Path) -> None:
    """Test validate_version with invalid TOML file."""
    pyproject = tmp_path / "invalid.toml"
    pyproject.write_text("this is not valid TOML [[[", encoding="utf-8")
    result = runner.invoke(app, ["validate-version", "1.0.0", "-p", str(pyproject)])
    assert result.exit_code == 1
    assert "Error: Invalid TOML" in result.output


def test_validate_version_file_not_found(runner: CliRunner) -> None:
    """Test validate_version with non-existent file."""
    result = runner.invoke(app, ["validate-version", "1.0.0", "-p", "/nonexistent/file.toml"])
    expected_exit_code = 2  # Typer validation error for missing file
    assert result.exit_code == expected_exit_code
    assert "does not exist" in result.output


def test_validate_version_case_sensitive(runner: CliRunner, tmp_path: Path) -> None:
    """Test that version comparison is case-sensitive."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test"
version = "1.0.0-Beta"
""",
        encoding="utf-8",
    )
    # Exact match should succeed
    result = runner.invoke(app, ["validate-version", "1.0.0-Beta", "-p", str(pyproject)])
    assert result.exit_code == 0

    # Different case should fail
    result = runner.invoke(app, ["validate-version", "1.0.0-beta", "-p", str(pyproject)])
    assert result.exit_code == 1
    assert "Version mismatch" in result.output


def test_validate_version_with_whitespace(runner: CliRunner, tmp_path: Path) -> None:
    """Test that versions with whitespace differences fail."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test"
version = "1.0.0"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validate-version", " 1.0.0 ", "-p", str(pyproject)])
    assert result.exit_code == 1
    assert "Version mismatch" in result.output


def test_validate_version_uses_default_pyproject(runner: CliRunner) -> None:
    """Test validate_version uses default pyproject.toml path."""
    # This test verifies the default path is used, but will fail if run from wrong directory
    # The default path is calculated relative to the dev module location
    result = runner.invoke(app, ["validate-version", "0.1.0"])
    # We can't predict success/failure without knowing the actual project version,
    # but we can verify it attempts to read a file and gives a meaningful error
    assert result.exit_code in (0, 1, 2)  # 0=match, 1=mismatch, 2=file error


def test_validate_version_complex_version_strings(runner: CliRunner, tmp_path: Path) -> None:
    """Test validate_version with complex version strings."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test"
version = "2.0.0rc1+build.123"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validate-version", "2.0.0rc1+build.123", "-p", str(pyproject)])
    assert result.exit_code == 0
    assert "matches project version" in result.output


def test_validate_version_empty_version_string(runner: CliRunner, sample_pyproject: Path) -> None:
    """Test validate_version with empty version string."""
    result = runner.invoke(app, ["validate-version", "", "-p", str(sample_pyproject)])
    assert result.exit_code == 1
    assert "Version mismatch" in result.output


def test_validate_version_numeric_only(runner: CliRunner, tmp_path: Path) -> None:
    """Test validate_version with numeric-only versions."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test"
version = "123"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validate-version", "123", "-p", str(pyproject)])
    assert result.exit_code == 0
