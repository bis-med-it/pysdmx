import pytest

from pysdmx.api.gds import __BaseGdsClient
from pysdmx.errors import Invalid


def test_gds_catalog():
    """Test the GdsQuery for catalog."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
    )
    assert query.get_url() == "/catalog/ECB"


def test_gds_catalog_with_version():
    """Test the GdsQuery for catalog with version."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        version="1.0",
    )
    assert query.get_url() == "/catalog/ECB/*/1.0"


def test_gds_catalog_with_resource_id():
    """Test the GdsQuery for catalog with resource ID."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="123",
    )
    assert query.get_url() == "/catalog/ECB/123"


def test_gds_catalog_with_all():
    """Test the GdsQuery for catalog with all parameters."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
    )
    assert query.get_url() == "/catalog/ECB/TEST/1.0"


def test_gds_catalog_with_all_params():
    """Test the GdsQuery for catalog with all parameters."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
        resource_type="data",
        message_format="json",
        api_version="1.0",
        detail="full",
        references="children",
    )
    assert (
        query.get_url() == "/catalog/ECB/TEST/1.0/?resource_type=data&"
        "message_format=json&api_version=1.0&detail=full&"
        "references=children"
    )


def test_invalid_gds_catalog_resource_type():
    """Test invalid GdsQuery for catalog."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
        resource_type="invalid_type",  # Invalid resource type
    )
    with pytest.raises(Invalid, match="invalid_type"):
        query.get_url()


def test_invalid_gds_catalog_message_format():
    """Test invalid GdsQuery for catalog with message format."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
        message_format="invalid_format",  # Invalid message format
    )
    with pytest.raises(Invalid, match="invalid_format"):
        query.get_url()


def tests_invalid_gds_catalog_detail():
    """Test invalid GdsQuery for catalog with detail."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
        detail="invalid_detail",  # Invalid detail
    )
    with pytest.raises(Invalid, match="invalid_detail"):
        query.get_url()


def test_invalid_gds_catalog_references():
    """Test invalid GdsQuery for catalog with references."""
    query = __BaseGdsClient()._catalogs_q(
        agency="ECB",
        resource="TEST",
        version="1.0",
        references="invalid_references",  # Invalid references
    )
    with pytest.raises(Invalid, match="invalid_references"):
        query.get_url()
