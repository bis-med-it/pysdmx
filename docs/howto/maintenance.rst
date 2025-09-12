.. _maintenance:

Maintaining metadata
====================

In this tutorial, we explore how ``pysdmx`` facilitates **metadata 
maintenance** using an instance of Fusion Metadata Registry (FMR) 
as metadata store.

While retrieving metadata is generally open to all, creating or
updating metadata typically checks whether the requester is allowed 
to maintain metadata. So, in order to follow along, you will need a
user with write access to an FMR instance. 

Connecting to the FMR
---------------------

First, we need an instance of the maintenance client to connect to our target
FMR. When instantiating the client, we pass the endpoint of the
`FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_ instance to
which metadata must be uploaded.

In addition to the endpoint, the credentials of a user who is allowed to
maintain metadata are required.

.. code-block:: python

    from pysdmx.api.fm.maintenance import RegistryMaintenanceClient

    target = "https://registry.sdmx.org"
    user = "your_username"
    pwd = "your_password"

    client = RegistryMaintenanceClient(target, user, pwd)


Uploading structures
--------------------

Then you need metadata to be uploaded to the FMR. For this example, we will
manually create a very simple codelist. 

.. code-block:: python

    from pysdmx.model import Code, Codelist

    cd = Code("A", name="Code A")
    cl = Codelist("CL_TEST", agency="TEST", name="Test CL", items=[cd])


.. note::

    The agency owning the metadata to be uploaded must already exist
    in the target FMR, and the selected user must have permissions to upload
    metadata for that agency.

Once we have the metadata ready, we can now upload it to the FMR:

.. code-block:: python

    client.put_structures([cl])



Uploading metadata reports
--------------------------

Maintenance activities are also supported for metadata reports.

.. code-block:: python

    from pysdmx.model import MetadataAttribute, MetadataReport

    attr = Attribute("A", "My attribute")
    report = MetadataReport(
        "MR_TEST", 
        agency="TEST", 
        name="Test Report", 
        attributes=[attr],
        targets=[
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=TS:T1(1.0)"
        ]
    )
    client.put_metadata_reports([report])


Supported upload modes
----------------------

The FMR supports various integration modes, and the 
``RegistryMaintenanceClient`` supports the following ones:


Append
    Metadata uploaded with action 'Append' may only add new metadata and
    may not overwrite any existing metadata, i.e. any attempt to update
    existing metadata will be rejected.

Merge
    Metadata uploaded with action 'Merge' may add new metadata and replace
    existing metadata. However, for Item Schemes (codelists, concept schemes,
    etc.), the items submitted will be added to the existing scheme. For
    example, if a codelist exists with codes A, B, and C, and the same codelist
    is submitted with codes B and X, then the resulting codelist will have
    codes A, B, C, X, i.e. code B has been replaced while code X has been
    added.

Replace
    Metadata uploaded with action 'Replace' may add new metadata, and can also
    replace existing metadata with new ones. This is the default.

Summary
-------

In this tutorial, we created a client to update metadata in the FMR, using
the ``RegistryMaintenanceClient``.