.. _sdmx_csv:

SDMX CSV
=========
In this package, we have the possibility to read and write SDMX CSV format.
This format is only used for data, not for Metadata.
The SDMX CSV readers and writers are compatible with SDMX-CSV 1.0 and 2.0 standards.


Reading
-------
Although the use of the general reader is always recommended,
specific readers for SDMX-CSV are also available.

We have the following readers available:

- DATA_SDMX_CSV_1_0_0 -> pysdmx.io.csv.sdmx10.reader

.. autofunction:: pysdmx.io.csv.sdmx10.reader.read

- DATA_SDMX_CSV_2_0_0 -> pysdmx.io.csv.sdmx20.reader

.. autofunction:: pysdmx.io.csv.sdmx20.reader.read



Writing
-------

As for reading, we can choose between SDMX-CSV 1.0 and 2.0 formats.
We also have different writers according to the version of the SDMX-CSV we are going to write.

We have the following writers available:

- CSV 1.0 -> pysdmx.io.csv.sdmx10.writer

.. autofunction:: pysdmx.io.csv.sdmx10.writer.write

- CSV 2.0 -> pysdmx.io.csv.sdmx20.writer

.. autofunction:: pysdmx.io.csv.sdmx20.writer.write


