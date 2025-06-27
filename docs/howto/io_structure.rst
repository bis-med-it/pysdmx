.. _structure-rw:

SDMX Structures IO operations
=============================

.. _structure-io-tutorial:

Reading
-------



.. code-block:: python

   from pysdmx.io import read_sdmx
   from pathlib import Path
    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "structure.xml"

    message = read_sdmx(filepath, validate=True)

Once the file is read, you can access the structures:

.. code-block:: python

   # Access the structure of the message_21
   structures = message.structures

The `structures` are returned as ``pysdmx``:ref:`Model Objects <model>`


.. _structure-writer-tutorial:

Writing
-------

Work in progress.

