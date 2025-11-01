.. _structure-io-tutorial:

SDMX Structures IO operations
=============================

.. _structure-io-reader-tutorial:

Reading
-------

In this tutorial, we learn how to read SDMX Structures messages using the
``pysdmx.io`` module.

.. important::

    For SDMX-ML support, you need to install the `pysdmx[xml]` extra.

    For SDMX-JSON structural validation you need to install the `pysdmx[json]` extra.
    ``validate=True`` is the default behaviour on read_sdmx and get_datasets.


    Check the :ref:`installation guide <installation>` for more information.

``pysdmx`` provides the :ref:`read_sdmx <read-sdmx>` function, which allows reading SDMX Structures messages
from various sources, such as files or URLs.

.. code-block:: python

    from pysdmx.io import read_sdmx
    from pathlib import Path

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "structure.xml"

    message = read_sdmx(file_path)
    # Access the structures of the SDMX Structures message
    structures = message.structures

Check the :ref:`Message <message>` documentation for all the available methods.

You may download directly the structures from the FMR or the SDMX API:

- :ref:`FMR tutorial <fs>`
- :ref:`SDMX-REST tutorial <sdmx-rest>`


.. _structure-io-writer-tutorial:

Writing
-------

The general writer allows to write SDMX data to various formats

:ref:`IO Formats supported <io-writer-formats-supported>`.

It is recommended to use the :ref:`write_sdmx <write-sdmx>` method for all use cases,
despite we include specific writers for the supported formats.

.. important::

    For SDMX-ML support, you also to install the `pysdmx[xml]` extra.

    Check the :ref:`installation guide <installation>` for more information.

A typical example to write structures:

.. code-block:: python

    from pysdmx.io import write_sdmx
    from pysdmx.io.format import Format
    from pysdmx.model import DataStructureDefinition

    dsd = DataStructureDefinition(id=..., name=..., components=...)

    write_sdmx(
        dsd,
        output_path="output.xml",
        sdmx_format=Format.STRUCTURE_SDMX_ML_3_0,
    )


Additional arguments are available for SDMX-ML to:

- Pretty print the XML output (using the `prettyprint` argument).
- Use a custom :class:`Header <pysdmx.model.message.Header>` (using the `header` argument).

.. code-block:: python

    from datetime import datetime

    from pysdmx.io import write_sdmx
    from pysdmx.io.format import Format
    from pysdmx.model import DataStructureDefinition, Organisation

    from pysdmx.model.message import Header

    dsd = DataStructureDefinition(id=..., name=..., components=...)
    header = Header(
        id="TEST_MESSAGE",
        test=True,
        prepared=datetime.now(),
        sender=Organisation(id="MD", name="MeaningfulData"),
    )

    write_sdmx(
        dsd,
        output_path="output.xml",
        sdmx_format=Format.DATA_SDMX_ML_3_0,
        prettyprint=True,
        header=header,
    )

.. _structure-io-convert-tutorial:

Convert between formats
-----------------------

To convert SDMX Structure messages between formats, you can combine the `read_sdmx` and `write_sdmx` functions:

.. code-block:: python

    from pysdmx.io import read_sdmx, write_sdmx
    from pathlib import Path

    # Read the SDMX Structure message (any supported format can be used)
    message = read_sdmx("structures.xml")

    # Write the structures to a different format, e.g., SDMX-ML 3.0
    write_sdmx(
        message.structures,
        sdmx_format=Format.STRUCTURE_SDMX_ML_3_0,
        output_path="output.xml",
    )