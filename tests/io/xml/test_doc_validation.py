import pytest
from lxml import etree

from pysdmx.io.xml.doc_validation import validate_doc

SDMX_ML_21_MESSAGE_NS = (
    "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
)


def test_validate_doc_does_not_resolve_external_entities(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET", encoding="utf-8")
    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!DOCTYPE mes:Structure [<!ENTITY ext SYSTEM "{secret.as_uri()}">]>'
        f'\n<mes:Structure xmlns:mes="{SDMX_ML_21_MESSAGE_NS}">'
        "<mes:Header><mes:ID>&ext;</mes:ID></mes:Header></mes:Structure>"
    )

    # lxml refuses the undefined external entity instead of reading the file
    with pytest.raises(etree.XMLSyntaxError, match="ext") as exc_info:
        validate_doc(doc)

    assert "TOP-SECRET" not in str(exc_info.value)
