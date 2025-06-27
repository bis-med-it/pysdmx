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

:ref:`IO Formats supported <io-formats-supported>`.

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

Work in progress.