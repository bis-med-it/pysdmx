.. _sdmx_ml:

SDMX-ML
=======
SDMX-ML is a format for exchanging statistical data and metadata.
It is based on XML and is part of the SDMX standard.
In this package, we have the possibility to read and write SDMX-ML 2.1 and 3.0 formats
and also in different structure types depending of our needs.


Reading
-------
Although the use of the general reader is always recommended,
specific readers for SDMX-ML are also available.

We have the following readers available:

- DATA_SDMX_ML_2_1_GEN -> pysdmx.io.xml.sdmx21.reader.generic

.. autofunction:: pysdmx.io.xml.sdmx21.reader.generic.read

- DATA_SDMX_ML_2_1_STR -> pysdmx.io.xml.sdmx21.reader.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure_specific.read

- STRUCTURE_SDMX_ML_2_1 -> pysdmx.io.xml.sdmx21.reader.structure

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure.read

- DATA_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx30.reader.structure_specific.read

- STRUCTURE_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure

.. autofunction:: pysdmx.io.xml.sdmx30.reader.structure.read

After reading the string, we will have a message object that contains a pandas
DataFrame with the data or a structure object with the metadata.


Writing
-------

As for reading, we can choose between SDMX-ML 2.1 and 3.0 formats
we also have different writers according to the type of structure we are going to write.

We have the following writers available:

- Generic data 2.1 -> pysdmx.io.xml.sdmx21.writer.generic

.. autofunction:: pysdmx.io.xml.sdmx21.writer.generic.write

- Structure specific data 2.1 -> pysdmx.io.xml.sdmx21.writer.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure_specific.write

- Structure 2.1 -> pysdmx.io.xml.sdmx21.writer.structure

.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure.write

- Structure specific data 3.0 -> pysdmx.io.xml.sdmx30.writer.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx30.writer.structure_specific.write

- Structure 3.0 -> pysdmx.io.xml.sdmx30.writer.structure
