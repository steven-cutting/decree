# Copilot Instructions for Decree

## Project Overview

Decree is a Python 3.11+ reimplementation of `adr-tools` - a CLI for
managing Architecture Decision Records (ADRs). The core architecture centers
around the `AdrLog` class that manages ADR files in `doc/adr/` directories.

### Key Components

- **`AdrLog`** (`src/decree/core.py`): Main API class managing ADR
  operations
- **`AdrRecord`/`AdrRef`** (`src/decree/models.py`): Typed data models using
  dataclasses and `StrEnum`
- **CLI** (`src/decree/cli.py`): Typer-based command interface with beartype
  validation
- **Templates** (`src/decree/templates.py`): ADR markdown templates with
  format strings

### Data Flow

ADRs are numbered markdown files (e.g.,
`0001-record-architecture-decisions.md`) with structured metadata headers.
The `AdrLog` class handles file I/O, numbering, and linking between records.

## Development Conventions

### Type Safety Strategy (ADR-0009)

- **mypy strict mode**: All code must pass mypy strict checks
- **beartype on public APIs only**: Runtime type validation using `@beartype`
  decorator on `AdrLog` methods
- **Frozen dataclasses**: Use `@dataclass(frozen=True, slots=True)` for
  immutable models

### Testing Approach (ADR-0008)

- **Real filesystem**: Use `tmp_path` fixtures, avoid mocking file operations
- **Golden tests**: Test actual file outputs against expected content
- **Minimal dependencies**: Keep test dependencies light

### Build & Development Workflow

- **uv-based builds**: Use `uv` for dependency management and `uv_build` for
  packaging
- **nox sessions**: Run `nox -s tests` (multi-version), `nox -s lint`, `nox
  -s typecheck`
- **File structure**: ADRs live in `doc/adr/`, tests use real filesystem via
  `tmp_path`

## Code Patterns

### Error Handling

```python
# Use helper for control flow in expressions
def _raise(exc: Exception) -> NoReturn:
    raise exc

# Usage in core logic
self.dir.exists() or (_raise(FileNotFoundError(f"{self.dir} does not exist")))
```

### Environment Variable Handling

Environment variables follow the pattern: `ADR_DATE` (override), `DECREE_TZ`
(timezone), `ADR_TEMPLATE` (custom templates). Use `os.environ` directly with
fallbacks.

### File Naming Convention

ADR files: `NNNN-slug.md` where NNNN is zero-padded number and slug is from
`slugify()` function.

## Key Files to Understand

- **`doc/adr/`**: Live ADR documents showing the actual format and conventions
- **`src/decree/core.py`**: Core business logic and file operations  
- **`tests/`**: Real filesystem testing patterns using pytest `tmp_path`
- **`noxfile.py`**: Development workflow automation
- **Third-party code**: Goes in `third_party/` with CC-BY-4.0 licensing

## Common Tasks

- **Add new CLI command**: Extend `cli.py` with Typer decorators, add
  corresponding `AdrLog` method
- **Modify ADR format**: Update `templates.py` and corresponding parsing in
  `core.py`
- **Add validation**: Use beartype decorators on public methods, mypy handles
  static checks
- **Testing**: Use `tmp_path`, create real ADR files, assert against file
  contents
