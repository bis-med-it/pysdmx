.. _general-rw:

Reading and writing SDMX Data
=============================

.. _general-reader-tutorial:

Reading
-------
The general reader allows to read SDMX data and metadata from various formats,
including SDMX-ML 2.1 and 3.0.
It is recommended to use the general reader for all use cases,
as it automatically detects the format of the file and uses the appropriate reader.
Also the reader give us the option to validate the structure against the SDMX-ML schema
with the parameter `validate` set to `True`. If we set it to `False`, the validation will not be performed.

A typical example to read data or metadata from a file, a string or a buffer, using read_sdmx:

.. code-block:: python

    from pysdmx.io.reader import read_sdmx
    from pathlib import Path

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "sample.xml"

    # Read from file
    message = read_sdmx(file_path, validate=True)

    # Read from URL
    message = read_sdmx("https://example.com/sample.xml", validate=True)

By default, the read_sdmx function will automatically detect the format of the file and use the appropriate reader.

once the file is read, yo can access the structure and data of the message:

.. code-block:: python

   # Access the structure of the message
   structure = message.structure

   # Access the data of the message
   data = message.data

The `structure` is returned as ``pysdmx``:ref:`Model Objects <model>` and
the `data` is returned as a sequence of :mod:`Pandas Dataset <pysdmx.io.pd.PandasDataset>`.


Other readers included in ``pysdmx`` are:

- :meth:`SDMX-CSV 1.0 <pysdmx.io.csv.sdmx10.reader.read>`
- :meth:`SDMX-CSV 2.0 <pysdmx.io.csv.sdmx20.reader.read>`
- SDMX-ML 2.1
    - :meth:`SDMX-ML 2.1 Generic <pysdmx.io.xml.sdmx21.reader.generic.read>`
    - :meth:`SDMX-ML 2.1 Structure Specific <pysdmx.io.xml.sdmx21.reader.structure_specific.read>`
    - :meth:`SDMX-ML 2.1 Structure <pysdmx.io.xml.sdmx21.reader.structure.read>`
- SDMX-ML 3.0
    - :meth:`SDMX-ML 3.0 Structure Specific <pysdmx.io.xml.sdmx30.reader.structure_specific.read>`
    - :meth:`SDMX-ML 3.0 Structure <pysdmx.io.xml.sdmx30.reader.structure.read>`

Writing
-------

Work in progress.