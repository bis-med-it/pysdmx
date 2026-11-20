.. _vtl-toolkit-api:

VTL Toolkit
===========

The VTL Toolkit provides a set of methods to help the user in the SDMX-VTL interconnection.
Currently, it includes functionality to generate VTL scripts, validate the SDMX-VTL objects
and convert datasets and codelists between SDMX and VTL formats.

.. _vtl-generation:

Generate VTL script
-------------------

.. autofunction:: pysdmx.toolkit.vtl.generate_vtl_script

.. _vtl-validation:

Validate VTL objects
--------------------

.. autofunction:: pysdmx.toolkit.vtl.model_validations

.. _vtl-conversion:

Convert dataset between SDMX and VTL formats
--------------------------------------------

.. autofunction:: pysdmx.toolkit.vtl.convert_dataset_to_vtl

.. autofunction:: pysdmx.toolkit.vtl.convert_dataset_to_sdmx

.. autofunction:: pysdmx.toolkit.vtl.convert_codelist_to_vtl

.. autofunction:: pysdmx.toolkit.vtl.convert_value_domain_to_sdmx