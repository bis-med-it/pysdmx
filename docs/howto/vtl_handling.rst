.. _vtl-handling:

Validate data using VTL
=======================

In this tutorial, we shall examine the utilization of ``pysdmx``
for reading **data** and **metadata** to generate a dataset and VTL script
and the ``vtlengine`` library to execute the VTL script.

.. note::
    This tutorial assumes that you have a basic understanding of SDMX and VTL concepts.
    If you are new to these topics, please refer to the
    `VTL documentation <https://sdmx-twg.github.io/vtl/2.1/html/index.html>`_ and
    `SDMX-VTL documentation <https://sdmx.org/wp-content/uploads/SDMX_3-1-0_SECTION_2_FINAL.pdf#page=143>`_


.. important::
    To use the VTL functionalities, you need to install the `pysdmx[vtl]` extra.

    This tutorial requires the `pysdmx[data]` extra to handle SDMX datasets as Pandas DataFrames,
    and the `pysdmx[xml]` extra to read and write SDMX-ML messages.

    Check the :ref:`installation guide <installation>` for more information.

Numerous types of operations can be performed; however, this
tutorial will focus exclusively on the fundamental ones.

.. contents::
   :local:
   :depth: 2

Step-by-Step Solution
---------------------

Using pysdmx we will read the Datasets, its Structures and the VTL objects. For the purpose of this tutorial, we shall employ the XML files
``structures.xml`` (data structure), ``data.xml`` (data) and ``vtl_ts.xml`` (Transformation Scheme and
VTL Mapping Scheme, in SDMX-ML 3.2).

Files used in the example can be found here:

- :download:`data.xml <../_static/data.xml>`
- :download:`structures.xml <../_static/structures.xml>`
- :download:`vtl_ts.xml <../_static/vtl_ts.xml>`

Reading Data and Structures messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The initial step involves reading the data structure and data from the
SDMX files. The following code snippet demonstrates the process:

.. code-block:: python


    from pathlib import Path

    # Path to the structures file (same directory as this script)
    path_to_structures = Path(__file__).parent / "structures.xml"

    # Path to the data file (same directory as this script)
    path_to_data = Path(__file__).parent / "data.xml"

Now we have the paths to the files, we can read the data structure and data
and extract the data:

.. code-block:: python

    from pysdmx.io import get_datasets
    # With the data and metadata path we extract the datasets with their related structures
    datasets = get_datasets(path_to_data, path_to_structures)

.. important::

    Check the :ref:`Get Datasets method docs <get-datasets>` for more information on how to generate a PandasDataset
    with both data and related structures.

    This method is the recommended way to read SDMX data and structures, as it combines them in a
    single Pandas Dataset, allowing you to work with the data and its structure seamlessly.


Getting the Transformation Scheme and VTL Mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The VTL statements reference the SDMX artefacts through aliases, and the VTL mappings
say which artefact each alias stands for. Since SDMX 3.2:

- a :class:`~pysdmx.model.vtl.VtlDatasetMapping` maps a VTL Data Set to a Data Structure Definition,
  Dataflow or Provision Agreement, and says whether it is an input of the VTL program (``is_input``);
- a :class:`~pysdmx.model.vtl.VtlCodelistMapping` maps a VTL Value Domain to a codelist.

Every mapping has the alias (``vtl_alias``) and the URN of the mapped artefact (``sdmx_urn``).

For the next step, we have three options available.
We can read the transformation scheme and VTL mapping from a file,
we can read a file from a Fusion Registry URL or we can create the pysdmx Model objects.

.. code-block:: python

    from pysdmx.io import read_sdmx
    from pathlib import Path
    # Path to the transformation file
    path_to_vtl_ts = Path(__file__).parent / "vtl_ts.xml"

    # Read the transformation file with read_sdmx
    message = read_sdmx(path_to_vtl_ts)

    # Get the Transformation Schemes
    ts = message.get_transformation_schemes()[0]
    # Get the VTL Mapping Scheme, with the VTL dataset mappings
    mapping_scheme = message.get_vtl_mapping_schemes()[0]

Optionally, we can also create the Transformation Scheme and VTL Mapping objects directly in code.

.. code-block:: python

    from pysdmx.model import (
        Reference,
        Transformation,
        TransformationScheme,
        VtlDatasetMapping,
        VtlMappingScheme,
    )

    # The VTL Data Set DS_1 is an input, mapped to the Dataflow MD:TEST_DF(1.0)
    dataset_mapping = VtlDatasetMapping(
        id="VTL_MAP_1",
        name="VTL Mapping 1",
        vtl_alias="DS_1",
        sdmx_artefact=Reference("Dataflow", "MD", "TEST_DF", "1.0"),
        is_input=True,
    )
    mapping_scheme = VtlMappingScheme(
        id="VTL_MAP_SCHEME_1",
        name="VTL Mapping Scheme 1",
        version="1.0",
        agency="MD",
        items=[dataset_mapping],
    )

    # Transformation Scheme object
    ts = TransformationScheme(
        id="TS1",
        version="1.0",
        agency="MD",
        vtl_version="2.1",
        name="Transformation Scheme 1",
        items=[
            Transformation(
                id="T1",
                name="Transformation 1",
                expression="DS_1 [calc Me_4 := OBS_VALUE]",
                is_persistent=True,
                result="DS_r",
            ),
        ],
        vtl_mapping_scheme=mapping_scheme,
    )

.. note::

    The messages of SDMX-ML 2.1, 3.0 and 3.1 and of SDMX-JSON 2.0 and 2.1 have the mappings
    deprecated in SDMX 3.2, which are read as :class:`~pysdmx.model.vtl.VtlDataflowMapping`
    (with its ``dataflow`` and ``dataflow_alias``). A ``VtlDatasetMapping`` can only be written
    in SDMX-ML 3.2 and SDMX-JSON 2.2.

You may download as well directly the structures from the FMR or the SDMX API:

- :ref:`FMR tutorial <fs>`
- :ref:`SDMX-REST tutorial <sdmx-rest>`

At this point you may use the :ref:`VTL Toolkit Model validations <vtl-validation>` to validate the Transformation Scheme
and its VTL mappings.

Running the VTL Script
^^^^^^^^^^^^^^^^^^^^^^

.. _run_sdmx:

Now that we have the VTL script, we can run it using the
`vtlengine.run_sdmx method <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.run_sdmx>`_.

.. code-block:: python

    from pysdmx.model import VtlDatasetMapping
    from pysdmx.util import parse_urn
    from vtlengine import run_sdmx

    # The inputs of the VTL program: the SDMX artefact of each one and its VTL alias
    mappings = {
        str(parse_urn(mapping.sdmx_urn)): mapping.vtl_alias
        for mapping in mapping_scheme.items
        if isinstance(mapping, VtlDatasetMapping) and mapping.is_input
    }
    # {"Dataflow=MD:TEST_DF(1.0)": "DS_1"}

    # Run the VTL script with the datasets and the mappings
    run_sdmx(script=ts, datasets=datasets, mappings=mappings)

The `run_sdmx` method will execute the Transformation Scheme (VTL Script) using the provided
datasets, each one named after the alias of its mapping.

Defining how the data are retrieved
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this tutorial the data come from a file. In SDMX 3.2, a :class:`~pysdmx.model.vtl.VtlExecution`
can also say where the data of each input are retrieved from: a query to a web service
compliant with the SDMX REST API (:class:`~pysdmx.model.vtl.QueryExtraction`) or a URL built from a
template (:class:`~pysdmx.model.vtl.UrlExtraction`), with parameters that are fixed or can be
given at run time.

.. code-block:: python

    from pysdmx.model import ItemReference, QueryExtraction, QueryParameter, VtlExecution

    execution = VtlExecution(
        id="EXEC_TS1",
        agency="MD",
        name="Execution of TS1",
        transformation_scheme=ts,
        extractions=[
            QueryExtraction(
                dataset_mapping=ItemReference(
                    "VtlDatasetMapping", "MD", "VTL_MAP_SCHEME_1", "1.0", "VTL_MAP_1"
                ),
                entry_point="https://sdmx.example.org/rest",
                sdmx_api_version="2.1",
                parameters=[
                    QueryParameter(name="key", value="*.A", is_fixed=True),
                    QueryParameter(name="c[TIME_PERIOD]", value="ge:2020", is_fixed=False),
                ],
            )
        ],
    )

``pysdmx`` reads and writes the VTL executions (``message.get_vtl_executions()``) and validates them
with the :ref:`VTL Toolkit Model validations <vtl-validation>`. Building the queries and retrieving
the data is up to the application that runs the VTL program.

Summary
-------

In this tutorial, we have learned how to read SDMX data and metadata using ``pysdmx``,
extract the Pandas Datasets, and run a VTL script using the ``vtlengine.run_sdmx`` method.

Useful additional links:

- `VTL Engine Docs <https://docs.vtlengine.meaningfuldata.eu>`_.
- `10 Minutes to VTL Engine <https://docs.vtlengine.meaningfuldata.eu/walkthrough.html>`_.
- `VTL Documentation <https://sdmx-twg.github.io/vtl/2.1/html/index.html>`_
- `SDMX-VTL documentation <https://sdmx.org/wp-content/uploads/SDMX_3-1-0_SECTION_2_FINAL.pdf#page=143>`_
