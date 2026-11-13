import httpx
import pytest

from pysdmx.api.qb import ApiVersion, LenientRestService
from pysdmx.errors import Invalid

URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/"
    "dataflow/ESTAT/nrg_bal_c/1.0/*.*.*.*.LU,MT"
)
DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
# Eurostat's answer to the query, which it rejects
FAULT = (
    '<S:Fault xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">'
    "<faultcode>140</faultcode><faultstring>INVALID_URL_VALUE: Invalid "
    "value &apos;,&apos; in key parameter.</faultstring></S:Fault>"
)


@pytest.mark.parametrize(
    "body",
    [
        DECLARATION + FAULT,
        # A fault in an envelope, as in other SOAP services
        DECLARATION
        + '<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/'
        f'envelope/"><env:Body>{FAULT}</env:Body></env:Envelope>',
    ],
    ids=["fault", "fault in an envelope"],
)
def test_raises_a_soap_fault(respx_mock, body):
    respx_mock.get(URL).mock(
        return_value=httpx.Response(
            400, headers={"Content-Type": "application/xml"}, content=body
        )
    )
    service = LenientRestService(URL, ApiVersion.V2_0_0)

    with pytest.raises(Invalid, match="INVALID_URL_VALUE: Invalid value"):
        "".join(service.stream_message(URL))
