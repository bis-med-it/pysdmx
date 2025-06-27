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
    To use the VTL functionalities, you need to have the pysdmx[vtl] extra installed.

    It requires the pysdmx[data] extra to handle SDMX datasets as Pandas DataFrames,
    and the pysdmx[xml] extra to read and write SDMX-ML messages.

    Check the :ref:`installation guide <installation>` for more information.

Numerous types of operations can be performed; however, this
tutorial will focus exclusively on the fundamental ones.

.. contents::
   :local:
   :depth: 2

Step-by-Step Solution
---------------------

Using pysdmx we will read the Datasets, its Structures and the VTL objects. For the purpose of this tutorial, we shall employ the XML files
``structures.xml`` (data structure), ``data.xml`` (data) and ``vtl_ts.xml`` (Transformation and VTLMapping).

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

    The `get_datasets` function will read the SDMX-ML files and return a list of Pandas Datasets.
    Each Dataset will have its related metadata attached to it.

    The datasets are returned as a list of :class:`Pandas Dataset <pysdmx.io.pd.PandasDataset>`.
    You can access the data using the `data` attribute of each Dataset.

    This method is critical for this tutorial, as the run_sdmx method requires the datasets to be passed as a parameter
    and that the datasets have their related metadata attached to them.


For more information on how to read data and metadata, see the :ref:`General reader <general-reader>`,

Getting the Transformation Scheme and VTL Mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For the next step, we have three options available.
We can read the transformation scheme and VTL mapping from a file,
we can read a file from a Fusion Registry URL or we can create the pysdmx Model objects.

.. code-block:: python

    from pysdmx.io import read_sdmx
    from pathlib import Path
    # Path to the transformation file
    path_to_vtl_ts = Path(__file__).parent / "vtl_ts.xml"

    # Read the transformation file from the URL path
    message = read_sdmx("https://example.com/path/to/vtl_ts.xml")

    # Read the transformation file with read_sdmx
    message = read_sdmx(path_to_vtl_ts)

    # Get the Transformation Schemes
    ts = message.get_transformation_schemes()[0]
    # Get the VTL Mapping Scheme
    mapping_scheme = message.get_vtl_mapping_schemes()[0]
    # Get the VTL Dataflow Mapping from the items, assuming the first item is the one we want
    dataflow_mapping = mapping_scheme.items[0]

    #Exmple of Transformation Scheme object
    ts = TransformationScheme(
        id="TS1",
        version="1.0",
        agency="MD",
        vtl_version="2.1",
        items=[
            Transformation(
                id="T1",
                uri=None,
                urn=None,
                name=None,
                description=None,
                expression="DS_1 [calc Me_4 := OBS_VALUE]",
                is_persistent=True,
                result="DS_r",
                annotations=(),
                ),
            ],
    )
    # Example of VTL Dataflow Mapping object
    dataflow_mapping = VtlDataflowMapping(
        dataflow="urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=MD:TEST_DF(1.0)",
        dataflow_alias="DS_1",
        id="VTL_MAP_1",
    )

At this point you may use the :ref:`VTL Toolkit Model validations <vtl-validation>` to validate the Transformation Scheme.

Running the VTL Script
^^^^^^^^^^^^^^^^^^^^^^

.. _run_sdmx:

Now that we have the VTL script, we can run it using the
`vtlengine.run_sdmx method <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.run_sdmx>`_.

.. code-block:: python

    from vtlengine import run_sdmx

    # Run the VTL script with the datasets and the dataflow mapping
    run_sdmx(script=ts, datasets=datasets, mappings=dataflow_mapping)

The `run_sdmx` method will execute the VTL script using the provided datasets and dataflow mapping.

Summary
-------

In this tutorial, we have learned how to read SDMX data and metadata using ``pysdmx``,
extract the Pandas Datasets, and run a VTL script using the ``vtlengine.run_sdmx`` method.

Useful additional links:

- `VTL Engine Docs <https://docs.vtlengine.meaningfuldata.eu>`_.
- `10 Minutes to VTL Engine <https://docs.vtlengine.meaningfuldata.eu/walkthrough.html>`_.
- `VTL Documentation <https://sdmx-twg.github.io/vtl/2.1/html/index.html>`_
- `SDMX-VTL documentation <https://sdmx.org/wp-content/uploads/SDMX_3-1-0_SECTION_2_FINAL.pdf#page=143>`_
