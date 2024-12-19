# Development checklist

Run the following commands in this order to ensure every commit is properly formatted and linted.

## Ruff

### Check
```bash
poetry run ruff check
```

### Fix
```bash
poetry run ruff check --fix
```

### Unsafe fixes (to be checked manually)
```bash
poetry run ruff check --fix --unsafe-fixes
```

## MyPy

```bash
poetry run mypy
```

## Pytest

```bash
poetry run pytest --cov=pysdmx
```

## Code Coverage (must be always 100%)

```bash
coverage html
```
