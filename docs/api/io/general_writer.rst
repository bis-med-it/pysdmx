.. _general-writer:

General Writer
==============

The pysdmx general writer is a set of methods to read any SDMX message, regardless of the format or version.

Tutorial on :ref:`writing SDMX Data messages <data-io-writer-tutorial>`.

Tutorial on :ref:`writing SDMX Structure messages <structure-io-writer-tutorial>`.

.. _io-writer-formats-supported:

Formats and Versions Supported
------------------------------

List of formats and versions supported by the general writer:

- :ref:`SDMX-CSV<sdmx_csv>`
    - :ref:`SDMX-CSV 1.0 <sdmx_csv_10_writer>`
    - :ref:`SDMX-CSV 2.0 <sdmx_csv_20_writer>`

- :ref:`SDMX-ML<sdmx_ml>`
    - :ref:`SDMX-ML 2.1 Generic <sdmx_ml_21_gen_writer>`
    - :ref:`SDMX-ML 2.1 Structure Specific <sdmx_ml_21_spe_writer>`
    - :ref:`SDMX-ML 2.1 Structure <sdmx_ml_21_structure_writer>`
    - :ref:`SDMX-ML 3.0 Structure Specific <sdmx_ml_30_spe_writer>`
    - :ref:`SDMX-ML 3.0 Structure <sdmx_ml_30_structure_writer>`

.. _write-sdmx:

Write SDMX
----------

This method allows you to write any SDMX message, regardless of the format or version as long as it is supported.

.. autofunction:: pysdmx.io.write_sdmx