.. _general-reader:

General Reader
==============

The pysdmx general reader is a set of methods to read any SDMX message, regardless of the format or version.

Tutorial on :ref:`reading SDMX Data messages <data-io-tutorial>`.

Tutorial on :ref:`reading SDMX Structure messages <structure-io-tutorial>`.

.. _io-reader-formats-supported:

Formats and Versions Supported
------------------------------

List of formats and versions supported by the general reader:

- :ref:`SDMX-CSV<sdmx_csv>`
    - :ref:`SDMX-CSV 1.0 <sdmx_csv_10_reader>`
    - :ref:`SDMX-CSV 2.0 <sdmx_csv_20_reader>`
    - :ref:`SDMX-CSV 2.1 <sdmx_csv_21_reader>`

- :ref:`SDMX-ML<sdmx_ml>`
    - :ref:`SDMX-ML 2.1 Generic <sdmx_ml_21_gen_reader>`
    - :ref:`SDMX-ML 2.1 Structure Specific <sdmx_ml_21_spe_reader>`
    - :ref:`SDMX-ML 2.1 Structure <sdmx_ml_21_structure_reader>`
    - :ref:`SDMX-ML 3.0 Structure Specific <sdmx_ml_30_spe_reader>`
    - :ref:`SDMX-ML 3.0 Structure <sdmx_ml_30_structure_reader>`
    - :ref:`SDMX-ML 3.1 Structure Specific <sdmx_ml_31_spe_reader>`
    - :ref:`SDMX-ML 3.1 Structure <sdmx_ml_31_structure_reader>`

.. _read-sdmx:

Read SDMX
---------

This method allows you to read any SDMX message, regardless of the format or version as long as it is supported.

.. autofunction:: pysdmx.io.read_sdmx

.. _get-datasets:

Get Datasets
------------

This method allows you to retrieve Pandas Datasets from a Data message, and add the related metadata
as a Schema object: :meth:`pysdmx.model.dataflow.Schema`.

.. autofunction:: pysdmx.io.get_datasets