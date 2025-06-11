.. _general-reader:

General Reader
==============

This module offers a general reader for reading data and metadata,
from a URL, String data or a datapath of a file. This reader supports
several formats and versions as well as a great flexibility to introduce
new versions or formats in the future

Tutorial for using the general reader can be found in:
:ref:`general-reader-tutorial`.

List of formats and versions supported by the general reader:

- **SDMX-ML**

  - **SDMX-ML 2.1**

    - Generic Data
    - Structure Specific Data
    - Structure

  - **SDMX-ML 3.0**

    - Structure Specific Data
    - Structure

- **SDMX-CSV**

  - SDMX-CSV 1.0
  - SDMX-CSV 2.0


Reading Data and Metadata
-------------------------

.. autofunction:: pysdmx.io.read_sdmx


Get Datasets
------------

.. autofunction:: pysdmx.io.get_datasets