.. _fs:

Generate the Filesystem Layout
===============================

In this tutorial, we learn how ``pysdmx`` aids in **generating the
filesystem structure** in a metadata-driven fashion, relying solely on
metadata stored in an SDMX Registry.

What we want is to store data in folders organized by **dataflows**.
In each dataflow folder, we create sub-folders by **data providers**.
Access to folders should be granted via appropriate **roles** with access
requests approved by the manager of the organizational unit owning
the **dataflow**.

Required Metadata
-----------------

For this use case, we need metadata in our SDMX Registry:

Dataflows
    Define the **first-level of the filesystem**. Dataflows, related
    artifacts, and provisioning metadata are needed to create roles for
    data access.

Provisioning Metadata
    **Provision agreements** and **data providers** indicate which
    providers supply data for a dataflow, defining the **second-level of
    the filesystem**.

Agencies
    Define the **organizational unit owning the data**. Contacts associated
    with agencies define the person in charge of approving (or denying)
    requests to access the data.

Category Schemes
    Define the dataflows to be considered when creating the filesystem
    structure. Dataflows are attached to categories of the category scheme
    via **categorizations**.

Step-by-step Solution
---------------------

``pysdmx`` allows retrieving metadata from an SDMX Registry either
synchronously (via ``pymedal.fmr.RegistryClient``) or asynchronously
(via ``pymedal.fmr.AsyncRegistryClient``).

Connecting to a Registry
^^^^^^^^^^^^^^^^^^^^^^^^

First, we need a client instance to connect to our target Registry.
When instantiating the client, we pass the SDMX-REST endpoint of our Registry.
If using the `FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_,
the endpoint is the URL at which the FMR is available, followed by ``/sdmx/v2/``.

.. code-block:: python

    from pysdmx.api.fmr import AsyncRegistryClient
    client = AsyncRegistryClient("[endpoint_comes_here]")

Creating the Dataflow Folders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once we have a client, we use it to get the list of dataflows needed
to consider when creating the filesystem. This information is captured
in a **category scheme** and related **categorizations**.

.. code-block:: python

    cs = await client.get_categories("MY_AGENCY", "MY_DATAFLOWS")

Now we iterate over the categories (and their sub-categories) to find
the dataflows attached to them. Use the ``dataflows`` property to get a set
with the dataflows attached at any level. Iterate through the set to create
a folder using ``os.mkdir``.

We can now iterate over the categories (and their sub-categories, if any) to
find the dataflows attached to them. However, there is a convenience property,
``dataflows``, that we can use to get a set with the dataflows attached at any
level. As this is a set, we no longer need to worry about duplicates, i.e.
each dataflow will appear only once, regardless of how many categories it is
attached to. We can then use the dataflow ID to create a folder, using
``os.mkdir``.

.. code-block:: python

    import os
    for flow in cs.dataflows:
        os.mkdir(flow.id)

Creating the Providers Folders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create the second level, i.e., one folder per provider of data for a dataflow.
Use the ``get_providers`` method to receive the respective dataflows for
each provider. Reorganize to have a dataflow as the key and the list of providers
for that dataflow as the value.

.. code-block:: python

    from collections import defaultdict
    flow_provs = defaultdict(set)
    providers = client.get_providers("MY_AGENCY", True)
    for prov in providers:
        for flow in prov.dataflows:
            flow_provs[flow.id].add(prov.id)

Now iterate over the keys of the ``flow_provs`` dictionary to create one folder
per item in the set associated with the key. Check if the dataflow folder exists
before creating provider folders.

.. code-block:: python

    for flow, providers in flow_provs.items():
        if os.path.exists(flow):
            for provider in providers:
                os.mkdir(f"{flow}/{provider}")

Creating the Roles
^^^^^^^^^^^^^^^^^^

Creating roles in the target directory service is a crucial step, although
details of this process depend on the specific service being used (e.g.,
OpenLDAP, Active Directory, etc.). The key information needed for role
creation includes the **role ID** and the **ID of the person (or group)**
responsible for granting access to the role.

The role ID and name can be constructed using information from the dataflow.
For example, the role ID might follow a convention like starting with an "R",
followed by the system name, dataflow ID, and access type (e.g., RO for read-only
access vs. RW for read and write access). Let's assume our application is
called ``MYAPP.``

Another critical aspect is linking the role to its approver. To achieve this,
we leverage contacts associated with SDMX agencies. Agencies might have multiple
contacts, so we use the **contact role** to identify the person tasked with
approving access requests. While the contact information may include various
details (such as name, address, unit, telephone, email, etc.), we specifically
use the ``ìd`` property to capture the username of the user responsible for
approving requests.

Now, let's dive into the implementation steps:

.. code-block:: python

    # Get extended information about the sub-agencies
    agencies = await client.get_agencies("MY_AGENCY")
    
    # Organize the agencies as a map for quick lookup
    agency_map = {a.id: a for a in agencies}

    # Assume that the role of the person approving access requests is "APPROVER"
    for flow in cs.dataflows:
        for access in ["RO", "RW"]:
            # Fetch the contact responsible for approving access requests
            contact = [c for c in agency_map[flow.agency].contacts if c.role == "APPROVER"][0]

            # Construct role information
            role = {
                "id": f"R_MYAPP_{flow.id}_{access}",
                "name": f"{access} access to {flow.id} ({flow.name})",
                "approver": contact.id
            }

            # Print the role information (actual implementation will involve creating roles in the directory service)
            print(role)

The roles, once created, play a pivotal role in defining access permissions to the
folders we've created previously. The details of setting these permissions are
specific to the operating system and the chosen directory service.

Summary
-------

In this tutorial, we have created a client to retrieve metadata from an SDMX
Registry and used its ``get_categories``, ``get_providers``, and
``get_agencies`` methods to create a filesystem layout, organize dataflows,
and grant access via dedicated roles.
