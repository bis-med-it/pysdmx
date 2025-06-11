.. _structure-rw:

Reading and writing SDMX Structures
===================================

.. _structure-reader-tutorial:

Reading
-------

``pysdmx`` allows to read SDMX Structures for SDMX-ML 2.1 and 3.0 formats.

Although we have specific readers for different formats, the use of the general
reader is always recommended for all use cases.
This reader also give us the option to validate the structure against the SDMX-ML schema
with the parameter ``validate`` set to ``True`` if we set it to ``False`` the validation will not be performed.

Tutorial for general reader : :ref:general-reader-tutorial:.

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
We can choose between SDMX-ML 2.1 and 3.0 formats.
We also have different writers according to the type of structure we are going to write.
We have the following writers available:

- :meth:`SDMX-ML 3.0 Structure Specific <pysdmx.io.xml.sdmx30.reader.structure_specific.read>`

- :meth:`SDMX-ML 3.0 Structure <pysdmx.io.xml.sdmx30.reader.structure.read>`

To write structures, we need to input a series ``pysdmx``:ref:`Model Objects <model>`
we can write a output path to save the structure into a file with ``output_path`` parameter,
also we can prettify the output with ``prettyprint`` parameter set to ``True``.

.. code-block:: python

   from pysdmx.io.xml.sdmx21.writer.structure import write as write_sdmx21
   from pysdmx.io.xml.sdmx30.writer.structure import write as write_sdmx30

   # Assuming you have a DataStructureDefinition object
   data_structure_21 = ...  # Your DataStructureDefinition for SDMX-ML 2.1
   data_structure_30 = ...  # Your DataStructureDefinition for SDMX-ML 3.0

   # Write the structure to SDMX-ML 2.1 with prettyprint
   xml_21 = write_sdmx21(data_structure_21, prettyprint=True)

   # Write the structure to SDMX-ML 3.0 without prettyprint
   xml_30 = write_sdmx30(data_structure_30)

The `write_sdmx21` and `write_sdmx30` functions will return a string containing the SDMX-ML structure in the specified format.

We can also save the output to a file by providing the ``output_path`` parameter:

.. code-block:: python

    from pysdmx.io.xml.sdmx21.writer.structure import write as write_sdmx21
    from pysdmx.io.xml.sdmx30.writer.structure import write as write_sdmx30
    # Write the structure to a file for SDMX-ML 2.1
    write_sdmx21(data_structure_21, output_path="structure_21.xml")

    # Write the structure to a file for SDMX-ML 3.0
    write_sdmx30(data_structure_30, output_path="structure_30.xml")


This will create files `structure_21.xml` and `structure_30.xml` in the current directory containing the SDMX-ML structures.

