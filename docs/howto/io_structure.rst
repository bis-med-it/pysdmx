.. _structure-io-tutorial:

SDMX Structures IO operations
=============================

.. _structure-io-reader-tutorial:

Reading
-------

In this tutorial, we learn how to read SDMX Structures messages using the
``pysdmx.io`` module.

``pysdmx`` provides the :ref:`read_sdmx <read-sdmx>` function, which allows reading SDMX Structures messages
from various sources, such as files or URLs.

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

Check the :ref:`Message <message>` documentation for all the available methods.

You may download directly the structures from the FMR or the SDMX API:

- :ref:`FMR tutorial <fs>`
- :ref:`SDMX-REST tutorial <sdmx-rest>`


.. _structure-io-writer-tutorial:

Writing
-------

Work in progress.

