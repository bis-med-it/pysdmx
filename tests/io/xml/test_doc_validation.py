import threading
from pathlib import Path

import pytest

from pysdmx.io.xml.doc_validation import load_schema, validate_doc

IO = Path(__file__).parents[1]
SAMPLES = {
    "2.1": IO / "samples" / "datastructure.xml",
    "3.0": IO / "samples" / "datastructure3_0.xml",
    "3.1": IO / "xml" / "sdmx31" / "reader" / "samples" / "codelist.xml",
}


def _message(version):
    return SAMPLES[version].read_text(encoding="utf-8")


@pytest.mark.parametrize("version", ["2.1", "3.0", "3.1"])
def test_load_schema_reuses_the_schema_of_a_version(version):
    message = _message(version)

    assert load_schema(message) is load_schema(message)


def test_load_schema_gives_each_version_its_own_schema():
    schemas = [load_schema(_message(version)) for version in SAMPLES]

    assert len({id(schema) for schema in schemas}) == 3
    # Each message validates against the schema kept for its version
    for version in SAMPLES:
        validate_doc(_message(version))


def test_load_schema_gives_each_thread_its_own_schema():
    # A schema holds the errors of its last validation, so two threads
    # validating with the same one would mix them up.
    message = _message("2.1")
    schemas = []
    thread = threading.Thread(
        target=lambda: schemas.append(load_schema(message))
    )

    thread.start()
    thread.join()

    assert schemas[0] is not load_schema(message)
