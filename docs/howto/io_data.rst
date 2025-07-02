.. _data-io-tutorial:

SDMX Data IO operations
=======================

.. _data-io-reader-tutorial:

This tutorial provides an overview of how to read and write SDMX data using the
pysdmx.io package. It covers the general reader and writer with a focus on
data messages, and how to combine data with metadata for further processing.

.. important::

    To use the pysdmx.io data functionalities, you need to install the `pysdmx[data]` extra.

    For SDMX-ML support, you also need to install the `pysdmx[xml]` extra.

    Check the :ref:`installation guide <installation>` for more information.

Reading
-------
The general reader allows to read SDMX data and metadata from various formats

:ref:`IO Formats supported <io-reader-formats-supported>`.

It is recommended to use the general reader for all use cases,
as it automatically detects the format of the file and uses the appropriate reader.

Using Read SDMX
^^^^^^^^^^^^^^^

A typical example to read data or metadata from a file, a string or a URL, using read_sdmx:

.. code-block:: python

    from pysdmx.io import read_sdmx
    from pathlib import Path

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "sample.xml"

    # Read from file
    message = read_sdmx(file_path)

    # Read from URL
    message = read_sdmx("https://example.com/sample.xml")

By default, the :meth:`pysdmx.io.read_sdmx` function will automatically detect the
format of the file and use the appropriate reader.

The output is always a Message object, which holds the Datasets at the `data` attribute.

.. code-block:: python

   # Access the Pandas Datasets on a Data Message
   data = message.data

The `data` is returned as a list of :mod:`Pandas Dataset <pysdmx.io.pd.PandasDataset>`.

Using Get Datasets
^^^^^^^^^^^^^^^^^^

To combine the Datasets with the related metadata, you can use the `get_datasets` function:

.. code-block:: python

    from pysdmx.io import get_datasets

    datasets = get_datasets(data_path, metadata_path)

The `get_datasets` function will return a list of :mod:`Pandas Dataset <pysdmx.io.pd.PandasDataset>` objects,
each containing the data (as PandasDataframe) and the related metadata as
a :class:`pysdmx.model.dataflow.Schema` object.

The combination of data and structures is essential for:

- Data validation: Ensuring that the data conforms to the expected structure.
- Data serialization in Time Series: Converting the data into a format
  suitable for time series analysis (:ref:`see writer tutorial <data-io-writer-tutorial>`).
- VTL validations: Run a VTL Transformation Scheme over the data (:ref:`see VTL tutorial <vtl-handling>`.

This is needed when validating the data against the structure, or converting the data to other formats (
:ref:`see writer tutorial <data-io-writer-tutorial>`). The :ref:`VTL validation <vtl-handling>`
requires the data to be combined with the structures.

.. _data-io-writer-tutorial:

Writing
-------

The general writer allows to write SDMX data to various formats

:ref:`IO Formats supported <io-writer-formats-supported>`.

It is recommended to use the :meth:`pysdmx.io.write_sdmx` for all use cases, despite we include specific writers for
the supported formats.

.. important::

    To use the pysdmx.io data functionalities, you need to install the `pysdmx[data]` extra.

    For SDMX-ML support, you also need to install the `pysdmx[xml]` extra.

    Check the :ref:`installation guide <installation>` for more information.

.. important::

    To write SDMX-ML Generic or Series messages, the PandasDataset requires to have its structure
    defined as a :class:`Schema object <pysdmx.model.dataflow.Schema>`.

A typical example to write data from a Pandas Dataset to a file, using write_sdmx:

.. code-block:: python

    from pysdmx.io import write_sdmx
    from pysdmx.io.format import Format
    from pysdmx.io.pd import PandasDataset

    # Replace with actual structure and data
    dataset = PandasDataset(structure=..., data=...)

    write_sdmx(
        dataset,
        output_path="output.csv",
        sdmx_format=Format.DATA_SDMX_CSV_2_0_0,
    )


Additional arguments are available for SDMX-ML to:

- Pretty print the XML output (using the `prettyprint` argument).
- Use a custom :class:`Header <pysdmx.model.message.Header>` (using the `header` argument).
- Specify the dimension at observation level (using the `dimension_at_observation` argument). This is needed for Time Series
  data formats.


A typical example to write data in Time Series with a custom header (pretty printed):

.. note::

    The dataset.structure defined as a Schema is needed for SDMX-ML Generic or Series messages.
    We include here a simple example on how to create a Schema object from a DataStructureDefinition.
    The DataStructureDefinition can be extracted from a SDMX Structures message, the FMR or created manually. See the
    :ref:`Structures IO tutorial <structure-io-tutorial>` for more information.

.. code-block:: python

    from datetime import datetime

    from pysdmx.io import write_sdmx
    from pysdmx.io.format import Format
    from pysdmx.io.pd import PandasDataset
    from pysdmx.model import Organisation, DataStructureDefinition
    from pysdmx.model.message import Header

    dsd = DataStructureDefinition(id=...,
                                  name=...,
                                  components=...)

    dataset = PandasDataset(data=..., structure=dsd.to_schema())

    header = Header(
        id="TEST_MESSAGE",
        test=True,
        prepared=datetime.now(),
        sender=Organisation(id="MD", name="MeaningfulData"),
    )

    write_sdmx(
        dataset,
        output_path="output.xml",
        sdmx_format=Format.DATA_SDMX_ML_3_0,
        prettyprint=True,
        header=header,
        dimension_at_observation={"Dataflow=MD:TEST_DF(1.0)": "TIME_PERIOD"},
    )

.. _data-io-convert-tutorial:

Convert between formats
-----------------------

To convert SDMX Data messages between formats, you can combine the `get_datasets` and `write_sdmx` functions:

.. code-block:: python

    from pysdmx.io import get_datasets, write_sdmx
    from pathlib import Path
    from pysdmx.io.format import Format

    # Read the data and structures SDMX-ML messages (any supported format can be used)
    datasets = get_datasets("data.xml", "structures.xml")

    # Write the data to SDMX-CSV 2.0
    write_sdmx(
        sdmx_objects=datasets,
        sdmx_format=Format.DATA_SDMX_CSV_2_0_0,
        output_path="output.csv",
    )

