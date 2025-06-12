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

    - :meth:`SDMX-ML 2.1 Generic <pysdmx.io.xml.sdmx21.reader.generic.read>`
    - :meth:`SDMX-ML 2.1 Structure Specific <pysdmx.io.xml.sdmx21.reader.structure_specific.read>`
    - :meth:`SDMX-ML 2.1 Structure <pysdmx.io.xml.sdmx21.reader.structure.read>`

  - **SDMX-ML 3.0**

    - :meth:`SDMX-ML 3.0 Structure Specific <pysdmx.io.xml.sdmx30.reader.structure_specific.read>`
    - :meth:`SDMX-ML 3.0 Structure <pysdmx.io.xml.sdmx30.reader.structure.read>`

- **SDMX-CSV**

  - :meth:`SDMX-CSV 1.0 <pysdmx.io.csv.sdmx10.reader.read>`
  - :meth:`SDMX-CSV 2.0 <pysdmx.io.csv.sdmx20.reader.read>`


Reading Data and Metadata
-------------------------

.. autofunction:: pysdmx.io.read_sdmx


Get Datasets
------------

.. autofunction:: pysdmx.io.get_datasets