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
    - :ref:`SDMX-CSV 2.1 <sdmx_csv_21_writer>`

- :ref:`SDMX-ML<sdmx_ml>`
    - :ref:`SDMX-ML 2.1 Generic <sdmx_ml_21_gen_writer>`
    - :ref:`SDMX-ML 2.1 Structure Specific <sdmx_ml_21_spe_writer>`
    - :ref:`SDMX-ML 2.1 Structure <sdmx_ml_21_structure_writer>`
    - :ref:`SDMX-ML 3.0 Structure Specific <sdmx_ml_30_spe_writer>`
    - :ref:`SDMX-ML 3.0 Structure <sdmx_ml_30_structure_writer>`
    - :ref:`SDMX-ML 3.1 Structure Specific <sdmx_ml_31_spe_writer>`
    - :ref:`SDMX-ML 3.1 Structure <sdmx_ml_31_structure_writer>`

.. _write-sdmx:

Write SDMX
----------

Serializes any SDMX object to a file or returns it as a string.

Examples of SDMX objects:

- :ref:`PandasDataset <pandas-ds>`
- MaintainableArtefacts (e.g. :class:`Codelist <pysdmx.model.code.Codelist>` ,
  :class:`DataStructureDefinition <pysdmx.model.dataflow.DataStructureDefinition>`,
  :class:`ConceptScheme <pysdmx.model.concept.ConceptScheme>`, etc.)

.. warning::

    Currently, the general writer is able to write one by one the objects, but it cannot access to the referenced objects
    (i.e we do not write the children/descendants of an object, we generate its references only even if the
    actual object is present). You may write the referenced objects by adding them as parameters to the
    write_sdmx function, as if you were writing them individually in the same SDMX Message.

    In a following release, we will add support for writing the referenced objects (if already present) or
    download them automatically.

.. autofunction:: pysdmx.io.write_sdmx