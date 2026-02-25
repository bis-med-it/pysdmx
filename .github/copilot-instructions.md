# pysdmx - Claude Code Instructions

## Project Overview

pysdmx is an opinionated Python library for working with SDMX (Statistical Data and Metadata eXchange). It provides Python classes representing a simplified SDMX information model, support for metadata-driven statistical processes, reading/writing SDMX files in multiple formats (CSV, JSON, XML), and data discovery/retrieval capabilities.

- **Homepage**: <https://sdmx.io/tools/pysdmx>
- **Documentation**: <https://bis-med-it.github.io/pysdmx>
- **Repository**: <https://github.com/bis-med-it/pysdmx>
- **License**: Apache 2.0
- **Python**: >=3.9, <4.0

## Core Architecture

### Package Structure (`src/pysdmx/`)

- **`api/`**: Service clients for SDMX data access
  - `fmr/` — Fusion Metadata Registry client
  - `dc/` — Data discovery client
  - `gds/` — Generic Data Service client
  - `qb/` — Query builder
- **`io/`**: Format readers and writers
  - `csv/` — CSV formats (SDMX 1.0, 2.0, 2.1)
  - `json/` — JSON formats (Fusion-JSON, GDS, SDMX-JSON 2.0)
  - `xml/` — XML formats (SDMX 2.1, 3.0, 3.1)
  - `reader.py`, `writer.py` — Unified entry points
  - `format.py` — Format enum definitions
  - `pd.py` — Pandas integration for I/O
- **`model/`**: SDMX information model classes
  - `dataset.py` — Dataset representations
  - `dataflow.py` — Dataflow definitions
  - `code.py`, `concept.py` — Codelists and concepts
  - `category.py` — Category schemes
  - `constraint.py` — Content constraints
  - `map.py` — Structure mappings
  - `organisation.py` — Agencies, data providers
  - `metadata.py` — Reference metadata
  - `vtl.py` — VTL-related models
  - `__base.py` — Base classes with serialization via `msgspec.Struct`
- **`toolkit/`**: Integration helpers (Pandas, VTL)
- **`util/`**: Shared utilities
- **`errors.py`**: Exception hierarchy

### Data Models

Models use `msgspec.Struct` (frozen, immutable). Validation happens in `__post_init__` methods.

### Error Hierarchy

- `PysdmxError` (base)
  - `RetriableError` → `Unavailable`
  - `Invalid` (non-retriable, client error)
  - `InternalError` (non-retriable, server error)
  - `NotFound`
  - `NotImplemented`
  - `Unauthorized`

### Core Dependencies

- **httpx[http2]**: Async HTTP client
- **msgspec**: Serialization (Struct-based models)
- **parsy**: Parser combinators

### Optional Extras

| Extra | Dependencies | Purpose |
| ----- | ------------ | ------- |
| `data` | pandas, numpy | DataFrame support |
| `dc` | python-dateutil | Date/time handling |
| `vtl` | vtlengine, numpy | VTL support |
| `json` | sdmxschemas, jsonschema | JSON format I/O |
| `xml` | lxml, xmltodict, sdmxschemas | XML format I/O |
| `all` | All of the above | Everything |

## Documentation (`docs/`)

Sphinx-based documentation published at <https://bis-med-it.github.io/pysdmx>.

- `docs/conf.py` — Sphinx config (theme: `sphinx_rtd_theme`, autodoc with napoleon)
- `docs/index.rst` — Main entry point and toctree
- Google-style docstrings (via `sphinx.ext.napoleon`)

Build docs locally:

```bash
poetry run sphinx-build docs _site
```

## Testing

### Organization

- Tests mirror `src/pysdmx/` structure: `tests/api/`, `tests/io/`, `tests/model/`, `tests/toolkit/`, `tests/util/`
- Pytest markers auto-assigned via `conftest.py` based on test path
- HTTP mocking via `respx`

### Markers

```
xml       — Tests that require the xml extra
xml_data  — Tests that require both the xml and data extras
data      — Tests that require the data extra
vtl       — Tests that require the vtl extra
dc        — Tests that require the dc extra
json      — Tests that require the json extra
noextra   — Tests that do not require any extra
```

### Running Tests

```bash
poetry run pytest --cov=pysdmx --cov-branch --cov-report=term-missing --verbose --tb=short --strict-markers --strict-config --durations=10 tests/
```

### Coverage

- **Minimum coverage: 100%** (enforced in CI)
- Branch coverage required
- `__extras_check.py` excluded (not testable with pytest since all extras are always installed)

Verify coverage:

```bash
poetry run coverage report --fail-under=100 --show-missing --skip-covered
```

## Code Quality (mandatory before every commit)

```bash
poetry run ruff format
poetry run ruff check --fix
poetry run mypy
```

All errors from `ruff format` and `ruff check` MUST be fixed before committing. Do not leave any warnings or errors unresolved.

### Ruff Rules

- **Line length**: 79
- **Max complexity**: 10
- **Docstring convention**: Google
- **Enabled checks**: ASYNC, B, C4, C90, D, DTZ, E, ERA, F, FURB, I, LOG, PERF, PT, S, SIM, W
- **Ignored**: D411, E203, F901
- **Test overrides**: Tests ignore C901, DTZ, D100, D103, D104, PERF, S101, S311

### Mypy

- Strict mode for `src/` directory
- All functions MUST have type annotations
- No implicit optionals
- Error codes enabled: `redundant-expr`, `truthy-bool`

### Docstrings

Google-style docstrings are required for all public modules, classes, and functions:

```python
"""Short description of class/function.

Longer description with context.

Attributes:
    field1: Description of field1.
    field2: Description of field2.

Raises:
    CustomError: Description of when this error is raised.
"""
```

## CI/CD

### CI Pipeline (3 OS × 5 Python versions)

- **Matrix**: ubuntu-latest, windows-latest, macos-latest × Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Steps**: ruff format check → ruff check → mypy → pytest (100% coverage) → coverage report
- **Fail-fast**: disabled (all matrix combinations run)

### Extra Dependencies Testing

- Validates each optional extra installs correctly and only its dependencies are present

### Documentation

- Published to GitHub Pages on push to main via `sphinx-build`

### Publishing

- PyPI publishing triggered on GitHub release via `poetry build` + PyPI token

## GitHub Project

### Labels

Labels indicate cross-cutting concerns. Use only the following:

| Label | Purpose |
| ----- | ------- |
| `bug` | Something isn't working |
| `documentation` | Improvements or additions to documentation |
| `duplicate` | This issue or pull request already exists |
| `enhancement` | Update to an existing feature |
| `new feature` | Add new functionality |
| `major` | A complex issue or an issue with a big impact |
| `normal` | An issue of normal complexity |
| `minor` | An issue that is easy to address |
| `dependencies` | Pull requests that update a dependency file |
| `Chores` | An issue affecting the CI/CD pipelines, the project setup, etc. |
| `python` | Pull requests that update python code |

**Never create new labels** — only use the existing set listed above.

## Git Workflow

### Branch Naming

Pattern: `cr-{issue_number}` (e.g., `cr-457` for issue #457)

### Workflow

1. Create branch: `git checkout -b cr-{issue_number}`
2. Make changes with descriptive commits
3. Run all quality checks (ruff format, ruff check, mypy, pytest)
4. Push and create PR

### Commit Message Style

Follow conventional-style messages. Examples from the project:

- `test: assert full self-closing Series tag`
- `Add tests for exclusive keysets`
- `Add support for exclusive keysets in SDMX-JSON`
- `Address linting issue`
- `Format SDMX-JSON reports`
- `Add test reproducing the issue for Fusion-JSON`

## Version Updates

When bumping version, update `pyproject.toml` (`[project] version`) and `src/pysdmx/__init__.py` (`__version__`). Both must match.

## File Sync Rules

- `.github/copilot-instructions.md` must always have the same content as `.claude/CLAUDE.md`. When updating one, always update the other to match.
