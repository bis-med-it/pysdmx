# tests/conftest.py
from pathlib import Path

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        p = Path(str(item.fspath)).as_posix()
        if "/tests/api/dc/" in p or p.endswith("/tests/api/dc"):
            item.add_marker(pytest.mark.dc)
