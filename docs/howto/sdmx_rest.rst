.. _sdmx-rest:

SDMX-REST services 
==================

``pysdmx`` allows **building SDMX-REST queries** and **executing them** 
against an SDMX-REST compliant web service.

For additional information about the SDMX-REST API, please refer to the
`SDMX documentation <https://github.com/sdmx-twg/sdmx-rest/>`_.

SDMX-REST queries
-----------------

The SDMX-REST API allows defining queries to retrieve 
`data <https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/data.md>`_, 
`structural <https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/structures.md>`_ and 
`reference metadata <https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/metadata.md>`_,
`schemas <https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/schema.md>`_
and `data availability <https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/availability.md>`_.

``pysdmx`` offers **query builders** for these different types of queries, as well as 
enumerations for some of the parameters available in the SDMX-REST API. 

For example, the following can be used to retrieve information about a dataflow and
all the artefacts referenced directly or indirectly by this dataflow.

.. code-block:: python

    from pysdmx.api.qb import (
        StructureDetail,
        StructureQuery,
        StructureReference,
        StructureType,
    )

    query = StructureQuery(
        StructureType.DATAFLOW,
        "SDMX",
        "NAMAIN_IDC_N",
        detail=StructureDetail.REFERENCE_PARTIAL,
        references=StructureReference.DESCENDANTS,
    )

SDMX services
-------------

Now that we have a query, we can execute it against the desired SDMX-REST service,
using the ``RestService`` class.

The ``RestService`` requires an endpoint to which the query will be sent,
as well as the version of the SDMX-REST API that the endpoint supports.

.. code-block:: python

    from pysdmx.api.qb import ApiVersion, RestService

    endpoint = "https://registry.sdmx.org/sdmx/v2/"
    version = ApiVersion.V2_0_0
    service = RestService(endpoint, version)
    resp = service.structure(query)

In case the query requires features that are not available in the version
of the API supported by the endpoint, an error will be raised.

Deserializing the response
--------------------------

The response of the web service will be returned as a sequence of bytes.
By default, the returned responses will be in the SDMX-JSON format, but
this can be configured when instantiating the ``RestService``.

You can then process the response using your preferred library for the
requested format, such as, for example, Python ``json`` module, for SDMX-JSON
responses.

Alternatively, for some messages, ``pysdmx.io.json.sdmxjson2`` deserializers
can be used. This is not well documented yet, as only a subset of messages
is currently supported, but further work will take place in this space.

The code below shows how to do that, using one of the supported messages.

.. code-block:: python

    import msgspec

    from pysdmx.api.qb import (
        ApiVersion,
        RestService,
        StructureQuery,
        StructureType,
    )
    from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelistMessage

    # Step 1: Build your query
    query = StructureQuery(StructureType.CODELIST, "SDMX", "CL_FREQ")

    # Step 2: Execute the query against your desired service
    endpoint = "https://registry.sdmx.org/sdmx/v2/"
    version = ApiVersion.V2_0_0
    service = RestService(endpoint, version)
    resp = service.structure(query)

    # Step 3: Deserialize the response into a domain object
    decoder = msgspec.json.Decoder(JsonCodelistMessage)
    cl = decoder.decode(resp).to_model()

    # Step 4: Use the object the way you see fit
    print(f"There are {len(cl.codes)} codes in the codelist")

    # Example output
    # There are 34 codes in the codelist


For additional information about the query builders and the SDMX-REST service
class, please refer to the :ref:`API documentation<qb_api>`.