.. _vtl:

Validate data using VTL
^^^^^^^^^^^^^^^^^^^^^^^

In this tutorial, we shall examine the utilization of ``pysdmx``
for reading **data** and **metadata** to generate a dataset and VTL script
and ``vtlengine`` for executing the VTL script.

Numerous types of operations can be performed; however, this
tutorial will focus exclusively on the fundamental ones.

.. contents::
   :local:
   :depth: 2

Step-by-Step Solution
---------------------

``pysdmx`` facilitates the reading of data and metadata from an SDMX
file or service. For the purpose of this tutorial, we shall employ the XML files
``metadata.xml`` (data structure), ``data.xml`` (data) and ``vtl_ts.xml`` (Transformation and VTLMapping).

Reading and Extracting Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initial step involves reading the data structure and data from the
SDMX files. The following code snippet demonstrates the process:

.. code-block:: python


    from pathlib import Path

    # Path to the structures file in SDMX-ML 2.1 (same directory as this script)
    path_to_metadata = Path(__file__).parent / "metadata.xml"

    # Path to the data file
    path_to_data = Path(__file__).parent / "data.xml"

Now we have the paths to the files, we can read the data structure and data
and extract the data:

.. code-block:: python

    from pysdmx.io import get_datasets
    # With the data and metadata path we extract de datasets
    datasets = get_datasets(path_to_data, path_to_metadata)

Getting The Transformation Scheme and VTL Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the next step, we have three options available.
We can read the transformation scheme and VTL mapping from a file,
we can read a file from a Fusion Registry URL or from a Objects we can create.

.. code-block:: python

    from pysdmx.io import read_sdmx
    from pathlib import Path
    # Path to the transformation file
    path_to_structure = Path(__file__).parent / "vtl_ts.xml"

    # Read the transformation file from the URL path
    message = read_sdmx("https://example.com/path/to/vtl_ts.xml")

    # Read the transformation file with read_sdmx
    message = read_sdmx(path_to_structure)

    # Get the Transformation Schemes
    schemes = message.get_transformation_schemes()
    # Get the first Transformation scheme, assuming the first scheme is the one we want
    trans_scheme = schemes[0]
    # Get the VTL Mapping Scheme
    mapping = message.get_vtl_mapping_schemes()
    # Get the VTL Dataflow Mapping from the items, assuming the first item is the one we want
    dataflow_mapping = vtl[0].items[0]

    #Exmple of Transformation Scheme object
    trans_scheme = TransformationScheme(
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



Creating the VTL Script
~~~~~~~~~~~~~~~~~~~~~~~~

Now we have the transformation scheme and the VTL mapping scheme,
we can create the VTL script from the Transformation Scheme.
We can also use the `model_validation` parameter to validate the model
and the `prettyprint` parameter to format the script for better readability.

.. code-block:: python


    from pysdmx.toolkit.vtl import generate_vtl_script
    # Create the VTL script from the Transformation Scheme
    vtl_script = generate_vtl_script(trans_scheme, model_validation=True, prettyprint=True)


Running the VTL Script
~~~~~~~~~~~~~~~~~~~~~~
Now that we have the VTL script, we can run it using the
``vtlengine`` library.

.. code-block:: python

    from vtlengine import run_sdmx

    # Run the VTL script with the datasets and the dataflow mapping
    run_sdmx(vtl_script, datasets=datasets, mappings=dataflow_mapping)


For more information on how to use the ``vtlengine``, please refer to the
`vtlengine run documentation <https://docs.vtlengine.meaningfuldata.eu/walkthrough.html>`_
