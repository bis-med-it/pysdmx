.. _sdmx_ml:

SDMX-ML
=======
SDMX-ML is a format for exchanging statistical data and metadata.
It is based on XML and is part of the SDMX standard.
In this package, we have the possibility to read and write SDMX-ML 2.1 and 3.0 formats
and also in different structure types depending of our needs.


Reading
-------
To read a SDMX-ML, first we need to ensure the SDMX-ML format we are reading,
for this task, we have at our disposal `process_string_to_read` from `pysdmx.io.input_processor`,
which returns both the format of the file to read and a string containing the file.

.. autofunction:: pysdmx.io.input_processor.process_string_to_read

Once we know the format we want to read, we only have to select the
necessary reader and read the string returned by the `process_string_to_read` function.

We hace the following readers available:

- DATA_SDMX_ML_2_1_GEN -> pysdmx.io.xml.sdmx21.reader.generic

- DATA_SDMX_ML_2_1_STR -> pysdmx.io.xml.sdmx21.reader.structure_specific

- STRUCTURE_SDMX_ML_2_1 -> pysdmx.io.xml.sdmx21.reader.structure

- DATA_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure_specific

- STRUCTURE_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure

After reading the string, we will have a message object that contains a pandas
DataFrame with the data or a structure object with the structure of the message.

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure.read



Writing
-------

As for reading, we can choose between SDMX-ML 2.1 and 3.0 formats
we also have different writers according to the type of structure we are going to write.
To write data we need to input a pandas Dataframe and to write a structure
we need a series of data structure objects like `Dataflow`, `DataStructureDefinition`, etc.

We have the following writers available:

- Generic data 2.1 -> pysdmx.io.xml.sdmx21.writer.generic

- Structure specific data 2.1 -> pysdmx.io.xml.sdmx21.writer.structure_specific

- Structure 2.1 -> pysdmx.io.xml.sdmx21.writer.structure

- Structure specific data 3.0 -> pysdmx.io.xml.sdmx30.writer.structure_specific

- Structure 3.0 -> pysdmx.io.xml.sdmx30.writer.structure

One we have the data or structure objects, we only need to input them on the correct writer.

.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure.write

