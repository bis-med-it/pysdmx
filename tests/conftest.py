from pathlib import Path

import pytest


def pytest_collection_xml(items):
    for item in items:
        p = Path(str(item.fspath)).as_posix()
        if "/tests/io/xml/" in p or p.endswith("/tests/io/xml"):
            item.add_marker(pytest.mark.xml)


def pytest_collection_data(items):
    for item in items:
        p = Path(str(item.fspath)).as_posix()
        if "/tests/io/csv/" in p or p.endswith("/tests/io/csv"):
            item.add_marker(pytest.mark.data)


def pytest_collection_dc(items):
    for item in items:
        p = Path(str(item.fspath)).as_posix()
        if "/tests/api/dc/" in p or p.endswith("/tests/api/dc"):
            item.add_marker(pytest.mark.dc)


def pytest_collection_vtl(items):
    for item in items:
        p = Path(str(item.fspath)).as_posix()
        if "/tests/toolkit/" in p or p.endswith("/tests/toolkit/"):
            item.add_marker(pytest.mark.vtl)
