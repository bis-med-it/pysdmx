from pathlib import Path

import pytest

PATH_RULES = {
    "/tests/io/xml/sdmx21/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx30/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx31/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx30/reader/test_reader.py": ("xml", False),
    "/tests/io/xml/sdmx31/reader/test_reader.py": ("xml", False),
    "/tests/io/xml/sdmx21/writer/test_data_writing.py": ("xmlWithData", True),
    "/tests/io/xml/sdmx30/writer/test_data_writing.py": ("xmlWithData", True),
    "/tests/io/xml/sdmx31/writer/test_data_writing.py": ("xmlWithData", True),
    "/tests/io/xml/sdmx21/reader/test_reader.py": ("xmlWithData", False),
    "/tests/io/csv/": ("data", True),
    "/tests/io/test_general_reader.py": ("data", False),
    "/tests/io/test_input_processor.py": ("data", True),
    "/tests/toolkit/": ("vtl", True),
    "/tests/model/": ("noextra", True),
    "/tests/api/": ("noextra", True),
}

EXCLUDE_FROM_AUTOMARK = {
    "tests/io/test_input_processor.py::test_process_string_to_read_invalid_xml",
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
        if any(
            rel_norm.startswith(sp.rstrip("/"))
            for sp in EXCLUDE_FROM_AUTOMARK
            if sp.endswith("/")
        ):
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
