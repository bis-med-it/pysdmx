.. _data-rw:

Reading and writing SDMX
========================

.. note::

        This tutorial shows how to read and write SDMX files ``pysdmx``.

    - :ref:`data-rw`.

.. warning::
    To read and write data, you must use the extra "data". You may need to install it using the following command:

    .. code-block:: bash

        pip install pysdmx[data]

    For SDMX-ML format, you need to install the extra "xml" as well:

    .. code-block:: bash

        pip install pysdmx[data,xml]

.. _general-reader-tutorial:

Reading
-------

``pysdmx`` allows to read SDMX in the following formats:

- SDMX-CSV 1.0 (located in ``pysdmx.io.csv.sdmx10``)
- SDMX-CSV 2.0 (located in ``pysdmx.io.csv.sdmx20``)
- SDMX-JSON (located in ``pysdmx.io.json.sdmxjson2``)
- SDMX-ML 2.1 (located in ``pysdmx.io.xml.sdmx21``)
    - SDMX-ML 2.1 Generic
    - SDMX-ML 2.1 Structure Specific
    - SDMX-ML 2.1 Structure
- SDMX-ML 3.0 (located in ``pysdmx.io.xml.sdmx30``)
    - SDMX-ML 3.0 Structure Specific
    - SDMX-ML 3.0 Structure



A typical example to read data or metadata from a file, a string or a buffer, using read_sdmx:

.. code-block:: python

   from pysdmx.io import read_sdmx

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "sample.xml"

    # Read from file
    message = read_sdmx(file_path)

    # Read from URL
    message = read_sdmx("https://example.com/sample.xml")

By default, the read_sdmx function will automatically detect the format of the file and use the appropriate reader.

once the file is read, yo can acces the structure and data of the message:
.. code-block:: python

   # Access the structure of the message
   structure = message.structure

   # Access the data of the message
   data = message.data

The `structure` is returned as ``pysdmx`` objects, such as `DataStructure`, `ConceptScheme`, `Codelist`, etc. and the `data` is returned as a sequence of `Pandas Datasets`.

Writing
-------

Work in progress.