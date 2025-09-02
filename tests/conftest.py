from pathlib import Path

import pytest

# Mapa carpeta → marker
PATH_TO_MARK = {
    "/tests/io/xml/": "xml",
    "/tests/io/csv/": "data",
    "/tests/api/dc/": "dc",
    "/tests/toolkit/": "vtl",
}


def pytest_collection_modifyitems(config, items):
    root = Path(config.rootdir)
    for item in items:
        rel = Path(item.fspath).resolve().relative_to(root).as_posix()
        for subpath, markname in PATH_TO_MARK.items():
            if subpath in f"/{rel}/":
                item.add_marker(getattr(pytest.mark, markname))
                break
