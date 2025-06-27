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

   # Access the structures of the SDMX Structures message
   structures = message.structures

Check the :ref:`Message <message>` documentation for more information on how to access the structures.


.. _structure-writer-tutorial:

Writing
-------

Work in progress.

