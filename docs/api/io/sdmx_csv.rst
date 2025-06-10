.. _sdmx_csv:

SDMX CSV
=========
In this package, we have the possibility to read and write SDMX CSV format.
This format is only used for data, not for Metadata.
The SDMX CSV readers and writers are compatible with SDMX-CSV 1.0 and 2.0 standards.


Reading
-------

To read a SDMX-CSV, first we need to ensure the SDMX-CSV format we are reading,
for this task, we have at our disposal `process_string_to_read` from `pysdmx.io.input_processor`,
which returns both the format of the file to read and a string containing the file.

Once we know the format we want to read, we only have to select the
necessary reader and read the string returned by the `process_string_to_read` function.

We have the following readers available:

- DATA_SDMX_CSV_1_0_0 -> pysdmx.io.csv.sdmx10.reader

- DATA_SDMX_CSV_2_0_0 -> pysdmx.io.csv.sdmx20.reader


.. autofunction:: pysdmx.io.csv.sdmx10.reader.read

After reading the string, we will have a message object that contains a pandas
DataFrame with the data.


Writing
-------

As for reading, we can choose between SDMX-CSV 1.0 and 2.0 formats.
We also have different writers according to the version of the SDMX-CSV we are going to write.

We have the following writers available:

- CSV 1.0 -> pysdmx.io.csv.sdmx10.writer

- CSV 2.0 -> pysdmx.io.csv.sdmx20.writer

One we have `the Pandas Dataset`, we only need to input them on the correct writer.

.. autofunction:: pysdmx.io.csv.sdmx10.writer.write