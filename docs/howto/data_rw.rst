.. _data-rw:

Reading and writing SDMX datasets
=================================

``pysdmx`` allows to read and write SDMX datasets in the following formats:

- SDMX-CSV 1.0 (located in ``pysdmx.io.csv.sdmx10``)
- SDMX-CSV 2.0 (located in ``pysdmx.io.csv.sdmx20``)
- SDMX-ML 2.1 (located in ``pysdmx.io.xml.sdmx21``)
    - SDMX-ML 2.1 Generic
    - SDMX-ML 2.1 Structure Specific

Currently, all data-related readers and writers are based on PandasDataset class.

.. autoclass:: pysdmx.io.pd.PandasDataset
    :show-inheritance:
    :undoc-members:

Reading data
------------

To read data, we may pass the string to the reading functions or use the input processor:

.. automodule:: pysdmx.io.input_processor
    :members: process_string_to_read

A typical example to read data from a file, a string or a buffer

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   # Import from desired reader

   # Read file sample.csv from the same folder as this code
   file_path = Path(__file__).parent / "sample.csv"
   input_str, extension = process_string_to_read(file_path)

   # Using reader, result will be a dictionary (key: dataset.short_urn, value: dataset)
   datasets = read(input_str)
   # Accessing the data of the test dataset
   df = dataset["DataStructure=TEST_AGENCY:TEST_ID(1.0)"].data

SDMX-CSV 1.0
^^^^^^^^^^^^

`SDMX-CSV 1.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v1.0/data-message/docs/sdmx-csv-field-guide.md>`_

.. warning::

        The SDMX-CSV 1.0 format is deprecated and should not be used for new implementations.
        It only allows a dataflow to be represented, which is not enough for most use cases.

.. autofunction:: pysdmx.io.csv.sdmx10.reader.read

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   from pysdmx.io.csv.sdmx10.reader import read
   from pathlib import Path

   # Read file sample.csv from the same folder as this code
   file_path = Path(__file__).parent / "sample10.csv"
   input_str, extension = process_string_to_read(file_path)

   # Using reader, result will be a dictionary (key: dataset.short_urn, value: dataset)
   datasets = read(input_str)
   # Accessing the data of the test dataset
   df = dataset["Dataflow=TEST_AGENCY:TEST_ID(1.0)"].data

SDMX-CSV 2.0
^^^^^^^^^^^^

`SDMX-CSV 2.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v2.0.0/data-message/docs/sdmx-csv-field-guide.md>`_

.. autofunction:: pysdmx.io.csv.sdmx20.reader.read

We currently support only comma as the delimiter.
Only the `ordinary case <https://github.com/sdmx-twg/sdmx-csv/blob/v2.0.0/data-message/docs/
sdmx-csv-field-guide.md#1-ordinary-case>`_ is supported.

You may use any custom script for the remaining use cases, if any one is interested in them, please
raise an issue in `GitHub <https://github.com/bis-med-it/pysdmx>`_.

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   from pysdmx.io.csv.sdmx20.reader import read
   from pathlib import Path

   # Read file from the same folder as this code
   file_path = Path(__file__).parent / "sample20.csv"
   input_str, extension = process_string_to_read(file_path)

   # Using reader, result will be a dictionary (key: dataset.short_urn, value: dataset)
   datasets = read(input_str)
   # Accessing the data of the test dataset
   df = dataset["DataStructure=TEST_AGENCY:TEST_ID(1.0)"].data

SDMX-ML 2.1
^^^^^^^^^^^

SDMX-ML 2.1 format is described
`here (pdf file for IM) <https://sdmx.org/wp-content/uploads/SDMX_2-1_SECTION_2_InformationModel_2020-07.pdf>`_

.. autofunction:: pysdmx.io.xml.sdmx21.reader.read_xml

We do not support the following elements:

- Dimension Group
- Reference to Provision Agreement

The reader supports both Generic and Structure Specific SDMX-ML 2.1.
It will automatically detect any structural validation errors (if validate=True) and raise an exception.

.. warning::

    The SDMX-ML 2.1 Generic format is deprecated and should not be used for new implementations.
    SDMX-ML 3.0 only uses the Structure Specific format, which is more efficient and easier to use.

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   from pysdmx.io.xml.sdmx21.reader import read_xml
   from pathlib import Path

   # Read file from the same folder as this code
   file_path = Path(__file__).parent / "sample21.xml"
   input_str, extension = process_string_to_read(file_path)

   # Using reader, result will be a dictionary (key: dataset.short_urn, value: dataset)
   datasets = read_xml(input_str, validate=True)

   # Accessing the data of the test dataset
   df = dataset["DataStructure=TEST_AGENCY:TEST_ID(1.0)"].data

Writing data
------------

``pysdmx`` allows to return the written data as a string or write it to a file. SDMX-CSV writers only allow one dataset to be written at a time, while SDMX-ML writers allow multiple datasets to be written at once.

SDMX-CSV 1.0
^^^^^^^^^^^^

`SDMX-CSV 1.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v1.0/data-message/docs/sdmx-csv-field-guide.md>`_

.. warning::

        The SDMX-CSV 1.0 format is deprecated and should not be used for new implementations.
        It only allows a dataflow to be represented, which is not enough for most use cases.

.. autofunction:: pysdmx.io.csv.sdmx10.writer.writer

.. code-block:: python

   from pysdmx.io.csv.sdmx10.writer import writer
   from pathlib import Path

   # Write to file sample.csv in the same folder as this code
   file_path = Path(__file__).parent / "sample.csv"
   writer(dataset, file_path)


SDMX-CSV 2.0
^^^^^^^^^^^^

`SDMX-CSV 2.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v2.0.0/data-message/docs/sdmx-csv-field-guide.md>`_

.. note::

        The SDMX-CSV 2.0 writer will write the data as the `ordinary case <https://github.com/sdmx-twg/sdmx-csv/blob/v2.0.0/data-message/docs/sdmx-csv-field-guide.md#1-ordinary-case>`_. If you need to write data in other cases, you may need to write a custom script.

.. warning::

        We use only comma as the delimiter.

.. autofunction:: pysdmx.io.csv.sdmx20.writer.writer

.. code-block:: python

   from pysdmx.io.csv.sdmx20.writer import writer
   from pathlib import Path

   # Write to file sample.csv in the same folder as this code
   file_path = Path(__file__).parent / "sample.csv"
   writer(dataset, file_path)

SDMX-ML 2.1
^^^^^^^^^^^

SDMX-ML 2.1 format is described
`here (pdf file for IM) <https://sdmx.org/wp-content/uploads/SDMX_2-1_SECTION_2_InformationModel_2020-07.pdf>`_

SDMX-ML 2.1 format allows to write multiple datasets at once. To use the Series format, you need to pass the dimension at observation dictionary, where the key is the dataset short urn and the value is the dimension id to be observed.

.. important::

    For each dataset, if dataset.structure is not a Schema, the writer can only write in the Structure Specific All Dimensions format.
    We perform a check to ensure that the dataset has a Schema structure for the remaining formats as we need to know the roles for each component. This check also ensures that the dataset.structure has at least one dimension and one measure defined.

.. autofunction:: pysdmx.io.xml.sdmx21.writer.writer

.. code-block:: python

    from pysdmx.io.xml.sdmx21.writer import writer
    from pysdmx.io.xml.enums import MessageType
    from pathlib import Path

    # Dictionary of datasets to write
    datasets = {
        "DataStructure=TEST_AGENCY:TEST_ID(1.0)": dataset
    }

    # Dimension at observation mapping
    dim_mapping = {
        "DataStructure=TEST_AGENCY:TEST_ID(1.0)": "TIME_PERIOD"
    }

    # Write to file sample.xml in the same folder as this code
    file_path = Path(__file__).parent / "sample.xml"
    writer(content=datasets, type_=MessageType.StructureSpecificDataSet, path=file_path, dimension_at_observation=dim_mapping)

