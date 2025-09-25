.. _sdmx_csv:

SDMX CSV
=========

This format is only used for data, not for Structures.
The SDMX CSV readers and writers are compatible with SDMX-CSV 1.0 and 2.0 standards on the Basic format.

`SDMX-CSV 1.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v1.0/data-message/docs/sdmx-csv-field-guide.md>`_

`SDMX-CSV 2.0 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v2.0.0/data-message/docs/sdmx-csv-field-guide.md>`_

`SDMX-CSV 2.1 specification <https://github.com/sdmx-twg/sdmx-csv/blob/v2.1.0/data-message/docs/sdmx-csv-field-guide.md>`_

.. important::

    To use the SDMX-CSV functionalities, you need to install the `pysdmx[data]` extra.

    Check the :ref:`installation guide <installation>` for more information.

Reading
-------
Although the use of the :ref:`general reader<general-reader>` is always recommended,
specific readers for SDMX-CSV are also available:

.. _sdmx_csv_10_reader:

- DATA_SDMX_CSV_1_0_0 -> pysdmx.io.csv.sdmx10.reader

.. autofunction:: pysdmx.io.csv.sdmx10.reader.read

.. _sdmx_csv_20_reader:

- DATA_SDMX_CSV_2_0_0 -> pysdmx.io.csv.sdmx20.reader

.. autofunction:: pysdmx.io.csv.sdmx20.reader.read


.. _sdmx_csv_21_reader:

- DATA_SDMX_CSV_2_1_0 -> pysdmx.io.csv.sdmx21.reader

.. autofunction:: pysdmx.io.csv.sdmx21.reader.read



Writing
-------

Although the use of the :ref:`general writer<general-writer>` is always recommended,
specific writers for SDMX-CSV are also available:

.. _sdmx_csv_10_writer:

- DATA_SDMX_CSV_1_0_0 -> pysdmx.io.csv.sdmx10.writer

.. autofunction:: pysdmx.io.csv.sdmx10.writer.write

.. _sdmx_csv_20_writer:

- DATA_SDMX_CSV_2_0_0 -> pysdmx.io.csv.sdmx20.writer

.. autofunction:: pysdmx.io.csv.sdmx20.writer.write

.. _sdmx_csv_21_writer:

- DATA_SDMX_CSV_2_1_0 -> pysdmx.io.csv.sdmx21.writer

.. autofunction:: pysdmx.io.csv.sdmx21.writer.write


