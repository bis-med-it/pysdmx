from pathlib import Path

import pytest

# Mapa carpeta → marker
PATH_RULES = {
    "/tests/io/xml/": ("xml", True),
    "/tests/io/csv/": ("data", True),
    "/tests/io/test_general_reader.py": ("data", False),
    "/tests/io/test_input_processor.py": ("data", True),
    "/tests/toolkit/": ("vtl", True),
    "/tests/model/": ("model", True),
}


def pytest_collection_modifyitems(config, items):
    root = Path(config.rootdir).resolve()
    for item in items:
        rel = Path(item.fspath).resolve().relative_to(root).as_posix()
        rel_norm = "/" + rel
        for subpath, (markname, automark) in PATH_RULES.items():
            if subpath.endswith("/"):
                if rel_norm.startswith(subpath.rstrip("/")) and automark:
                    item.add_marker(getattr(pytest.mark, markname))
                    break
            else:
                if rel_norm == subpath and automark:
                    item.add_marker(getattr(pytest.mark, markname))
                    break


def pytest_ignore_collect(collection_path: Path, config):
    expr = (config.getoption("-m") or "").strip()
    if not expr or any(c in expr for c in " ()&|!"):
        return None

    root = Path(getattr(config, "rootpath", config.rootdir)).resolve()
    cand = collection_path.resolve()

    allowed = []
    for sp, (mark, _automark) in PATH_RULES.items():
        if mark != expr:
            continue
        ap = (root / sp.lstrip("/")).resolve()
        allowed.append((sp.endswith("/"), ap))

    if not allowed:
        return None

    for is_dir, ap in allowed:
        if is_dir:
            if cand == ap or cand.is_relative_to(ap) or ap.is_relative_to(cand):
                return False
        else:
            if cand == ap or ap.is_relative_to(cand):
                return False

    return True
