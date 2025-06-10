.. _structure-rw:

Structure Reading and writing SDMX
==================================

.. note::

        This tutorial shows how to read and write SDMX Structure files ``pysdmx``.

    - :ref:`structure-rw`.


.. _structure-reader-tutorial:

Reading
-------

``pysdmx`` allows to read SDMX Structures for SDMX-ML 2.1 and 3.0 formats.

First of all, you need to ensure the SDMX-ML format you are reading.
For this task, we have at our disposal `process_string_to_read` from `pysdmx.io.input_processor`,
then we only need to select the necessary reader and read the string returned by the `process_string_to_read` function.

We have the following readers available for structures:

- STRUCTURE_SDMX_ML_2_1 -> `pysdmx.io.xml.sdmx21.reader.structure`

- STRUCTURE_SDMX_ML_3_0 -> `pysdmx.io.xml.sdmx30.reader.structure`

This reader algo give us the option to validate the structure against the SDMX-ML schema
with the parameter `validate` set to `True` if we set it to `False` the validation will not be performed.

.. code-block:: python

   from pysdmx.io.input_processor import process_string_to_read
   from pysdmx.io.xml.sdmx21.reader.structure import read as read_sdmx21
   from pysdmx.io.xml.sdmx30.reader.structure import read as read_sdmx30

    # Read file from the same folder as this code
    file_path = Path(__file__).parent / "structure.xml"

    # Process the file to get the string and format
    string_data, format = process_string_to_read(file_path)

    # Read the structure based on the format
    # For SDMX-ML 2.1
    message_21 = read_sdmx21(string_data, validate=True)
    # For SDMX-ML 3.0
    message_30 = read_sdmx30(string_data, validate=True)


once the file is read, yo can access the structures:

.. code-block:: python

   # Access the structure of the message_21
   structures_21 = message_21.structures

   # Access the structure of the message_30
   structures_30 = message_30.structures

The `structures` are returned as ``pysdmx`` objects, such as `DataStructureDefinition`, `ConceptScheme`, `Codelist`, etc.


.. _structure-writer-tutorial:

Writing
-------
As for reading, we can choose between SDMX-ML 2.1 and 3.0 formats.
We also have different writers according to the type of structure we are going to write.
We have the following writers available:

- Structure 2.1 -> `pysdmx.io.xml.sdmx21.writer.structure`

- Structure 3.0 -> `pysdmx.io.xml.sdmx30.writer.structure`

To write structures, we need to input a series of data structure objects like `Dataflow`, `DataStructureDefinition`, etc.
we can write a output path to save the structure into a file with `output_path` parameter,
also we can prettify the output with `prettyprint` parameter set to `True`.

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

We can also save the output to a file by providing the `output_path` parameter:

.. code-block:: python

   # Write the structure to a file for SDMX-ML 2.1
   write_sdmx21(data_structure_21, output_path="structure_21.xml")

   # Write the structure to a file for SDMX-ML 3.0
   write_sdmx30(data_structure_30, output_path="structure_30.xml")


This will create files `structure_21.xml` and `structure_30.xml` in the current directory containing the SDMX-ML structures.

