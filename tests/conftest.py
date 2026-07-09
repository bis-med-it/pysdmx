from pathlib import Path

import pytest

PATH_RULES = {
    # xml tests
    "/tests/io/xml/sdmx21/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx30/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx31/writer/test_structures_writing.py": ("xml", True),
    "/tests/io/xml/sdmx30/reader/test_reader.py": ("xml", False),
    "/tests/io/xml/sdmx31/reader/test_reader.py": ("xml", False),
    # xml and data tests
    "/tests/io/xml/sdmx21/writer/test_data_writing.py": ("xml_data", True),
    "/tests/io/xml/sdmx30/writer/test_data_writing.py": ("xml_data", True),
    "/tests/io/xml/sdmx31/writer/test_data_writing.py": ("xml_data", True),
    "/tests/io/xml/sdmx21/reader/test_reader.py": ("xml_data", False),
    # data tests
    "/tests/io/csv/sdmx10/reader/": ("data", True),
    "/tests/io/csv/sdmx10/writer/": ("data", False),
    "/tests/io/csv/sdmx20/reader/": ("data", True),
    "/tests/io/csv/sdmx20/writer/": ("data", False),
    "/tests/io/csv/sdmx21/reader/": ("data", True),
    "/tests/io/csv/sdmx21/writer/": ("data", False),
    "/tests/io/test_general_reader.py": ("data", False),
    "/tests/io/test_input_processor.py": ("data", True),
    # vtl tests
    "/tests/toolkit/vtl/": ("vtl", True),
    # noextra tests
    "/tests/model/": ("noextra", True),
    "/tests/api/fmr/": ("noextra", True),
    "/tests/api/gds/": ("noextra", True),
    "/tests/api/qb/": ("noextra", True),
    # stat connector tests (need xml for SDMX-ML 2.1 + data for PandasDataset)
    "/tests/api/stat/test_connector.py": ("xml_data", True),
    "/tests/api/stat/test_upload.py": ("xml_data", True),
    "/tests/api/stat/test_integration.py": ("xml_data", True),
    # dc tests
    "/tests/api/dc/test_model.py": ("dc", True),
    "/tests/api/dc/test_multi_filters.py": ("dc", True),
    "/tests/api/dc/test_parser.py": ("dc", True),
    "/tests/api/dc/test_parsing_model.py": ("dc", True),
    "/tests/api/dc/test_py_parser.py": ("dc", True),
    "/tests/api/dc/test_rest_client.py": ("dc", True),
    "/tests/api/dc/test_sortby.py": ("dc", True),
    "/tests/api/dc/test_sql_parser.py": ("dc", True),
    "/tests/api/dc/test_util.py": ("dc", True),
    "/tests/api/dc/test_pd_client.py": ("data", True),
    # json tests
    "/tests/io/json/sdmxjson2/": ("json", True),
    "/tests/io/json/sdmxjson2/deser/test_read_validations.py": ("json", True),
}

EXCLUDE_FROM_AUTOMARK = {
    "tests/io/test_input_processor.py::test_process_string_to_read_invalid_xml",
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
