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

To read data, we recommend using the read_sdmx function or the get_datasets function:

.. automodule:: pysdmx.io.reader
    :members: read_sdmx

A typical example to read data from a file, a string or a buffer, using read_sdmx

.. code-block:: python

   from pysdmx.io import read_sdmx

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "sample.csv"

    # Read from file
    data_msg = read_sdmx(file_path)

    # Read from URL
    data_msg = read_sdmx("https://example.com/sample.csv")

    # Extracting the datasets (list of Dataset)
    datasets = data_msg.data

    # Accessing the data of the test dataset by its Short URN
    df = data_msg.get_dataset("DataStructure=TEST_AGENCY:TEST_ID(1.0)").data

    # Accessing the data of the test dataset by its position in the SDMX Message
    df = data_msg.data[0].data


By default, the read_sdmx function will automatically detect the format of the file and use the appropriate reader. We may as well use the get_datasets to associate a dataset to its Schema:

.. automodule:: pysdmx.io.reader
    :members: get_datasets

.. important::

        If the structures message is used, the get_datasets function will associate the dataset to its Schema. If the structures message is not used, the get_datasets function will return a list of datasets without any Schema association.
        If a dataset references a dataflow, the structure message requires to have the dataflow children (or all descendants), i.e. the DataStructureDefinitions associated to this Dataflow in the same SDMX Message (with or without referenced artefacts like Codelists, ConceptSchemes, etc).

.. code-block:: python

    from pysdmx.io import get_datasets

    # Read file from the same folder as this code (SDMX-CSV 2.0)
    data_path = Path(__file__).parent / "sample.csv"

    # Data contains a reference to the dataflow ``Dataflow=MD:TEST(1.0)``
    datasets = get_datasets(data_path)

    print(datasets[0].structure)  # Outputs a string with the Schema Short URN -> "Dataflow=MD:TEST(1.0)"

    # Reading the datasets and associating the schema
    datasets = get_datasets(data_path, "https://example.com/dataflow/MD/TEST/1.0?references=descendants")

    print(datasets[0].structure)  # Outputs a Schema object with the associated components


Both methods are based on the individual readers for each format supported, which are described below.
All individual readers will have as input a string.

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
   input_str, format = process_string_to_read(file_path)

   # Using reader, result will be a list of datasets
   datasets = read(input_str)
   # Accessing the data of the test dataset
   df = dataset[0].data

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
   input_str, format = process_string_to_read(file_path)

   # Using reader, result will be a list of datasets
   datasets = read(input_str)
   # Accessing the data of the test dataset
   df = dataset[0].data

SDMX-ML 2.1 Data Readers
^^^^^^^^^^^^^^^^^^^^^^^^

SDMX-ML 2.1 format is described
`here (pdf file for IM) <https://sdmx.org/wp-content/uploads/SDMX_2-1_SECTION_2_InformationModel_2020-07.pdf>`_

```pysdmx`` supports both Generic and Structure Specific SDMX-ML 2.1 to handle data on SDMX-ML, both as All Dimensions or Series format.

.. autofunction:: pysdmx.io.xml.sdmx21.reader.generic.read

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure_specific.read

We do not support the following elements:

- Dimension Group
- Reference to Provision Agreement

The reader supports both Generic and Structure Specific SDMX-ML 2.1.
It will automatically detect any structural validation errors (if validate=True) and raise an exception.

.. warning::

    The SDMX-ML 2.1 Generic format is deprecated and should not be used for new implementations. SDMX-ML 3.0 only uses the Structure Specific format, which is more efficient and easier to use.

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   from pysdmx.io.xml.sdmx21.reader.generic import read as read_generic  # For Generic format
   from pysdmx.io.xml.sdmx21.reader.structure_specific import read # For Structure Specific format
   from pathlib import Path

   # Read file from the same folder as this code
   file_path = Path(__file__).parent / "sample21.xml"
   input_str, format = process_string_to_read(file_path)

   # Using reader, result will be a list of datasets
   datasets = read(input_str, validate=True)

   # Accessing the data of the test dataset
   df = dataset[0].data


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

   # Write the datasets (list of Dataset or PandasDataset) to the file
   writer(datasets, file_path)


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

SDMX-ML 2.1 Data Writers
^^^^^^^^^^^^^^^^^^^^^^^^

SDMX-ML 2.1 format is described
`here (pdf file for IM) <https://sdmx.org/wp-content/uploads/SDMX_2-1_SECTION_2_InformationModel_2020-07.pdf>`_

SDMX-ML 2.1 format allows to write multiple datasets at once. To use the Series format, you need to pass the dimension at observation dictionary, where the key is the dataset short urn and the value is the dimension id to be observed.

.. important::

    For each dataset, if dataset.structure is not a Schema, the writer can only write in the Structure Specific All Dimensions format.
    We perform a check to ensure that the dataset has a Schema structure for the remaining formats as we need to know the roles for each component.
    This check also ensures that the dataset.structure has at least one dimension and one measure defined.

.. autofunction:: pysdmx.io.xml.sdmx21.writer.generic.write
.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure_specific.write

.. code-block:: python

    from pysdmx.io.xml.sdmx21.writer.generic import write as write_generic  # For Generic format
    from pysdmx.io.xml.sdmx21.writer.structure_specific import write  # For StructureSpecific format
    from pysdmx.io.xml.enums import MessageType
    from pathlib import Path

    # List of datasets to write
    datasets = [dataset1, dataset2]

    # Dimension at observation mapping (do not need to set them all if not needed
    dim_mapping = {
        "DataStructure=TEST_AGENCY:TEST_ID(1.0)": "TIME_PERIOD"
    }

    # Write to file sample.xml in the same folder as this code
    file_path = Path(__file__).parent / "sample.xml"
    write(datasets, file_path, dimension_at_observation=dim_mapping)  # This will write a Dataset in Series and another in AllDimensions format

