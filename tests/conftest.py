from pathlib import Path

import pytest

from pathlib import Path
import pytest

PATH_RULES = {
    "/tests/io/xml/": ("xml", True),
    "/tests/io/csv/": ("data", True),
    "/tests/io/test_general_reader.py": ("data", False),
    "/tests/io/test_input_processor.py": ("data", True),
    "/tests/toolkit/": ("vtl", True),
    "/tests/model/": ("model", True),
    "/tests/api/": ("api", True),
}

EXCLUDE_FROM_AUTOMARK = {
    "tests/io/test_input_processor.py::test_process_string_to_read_invalid_xml",
}

IGNORE_TREES = {
    "/tests/api/dc/",
}

def pytest_collection_modifyitems(config, items):
    root = Path(config.rootdir).resolve()
    for item in items:
        rel = Path(item.fspath).resolve().relative_to(root).as_posix()
        rel_norm = "/" + rel

        nodeid = item.nodeid.replace("\\", "/")
        if nodeid in EXCLUDE_FROM_AUTOMARK:
            continue

        for subpath, (markname, automark) in PATH_RULES.items():
            if not automark:
                continue
            if subpath.endswith("/"):
                if rel_norm.startswith(subpath.rstrip("/")):
                    item.add_marker(getattr(pytest.mark, markname))
                    break
            else:
                if rel_norm == subpath:
                    item.add_marker(getattr(pytest.mark, markname))
                    break


def pytest_ignore_collect(collection_path: Path, config):
    root = Path(getattr(config, "rootpath", config.rootdir)).resolve()
    cand = collection_path.resolve()

    for sp in IGNORE_TREES:
        ap = (root / sp.lstrip("/")).resolve()
        if cand == ap or cand.is_relative_to(ap):
            return True

    expr = (config.getoption("-m") or "").strip()
    if not expr or any(c in expr for c in " ()&|!"):
        return None

    allowed = []
    for sp, (mark, _automark) in PATH_RULES.items():
        if mark != expr:
            continue
        ap = (root / sp.lstrip("/")).resolve()
        allowed.append((sp.endswith("/"), ap))

    if not allowed:
        return None

    for _is_dir, ap in allowed:
        if cand == ap or cand.is_relative_to(ap) or ap.is_relative_to(cand):
            return False

    return True


