# Development checklist

Run the following commands in this order to ensure every commit is properly formatted and linted.

- Flake8

```bash
poetry run flake8 src tests
```

- MyPy

```bash
poetry run mypy
```

- Pytest

```bash
poetry run pytest
```

- Code Coverage (must be always 100%)
