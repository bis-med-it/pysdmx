.. _vtl_toolkit:

VTL Toolkit
===========

The VTL toolkit module is a set of functions that help to generate VTL script from metadata.
The purpose of this module is to provide a set of functions that can be used to validate the metadata from a transformation scheme,
ruleset scheme, and user defined operator scheme and generate the VTL script from the transformation scheme.


Generate VTL script
-------------------

In this tutorial, we learn how generate VTL script step by step using metadata stored in a
XML file with a Transformation Scheme structure.
We will be reading the metadata from the XML file, validating the metadata, and generating the VTL script.

Required Metadata
-----------------

For this use case, we need metadata read with the sdmx reader or generated from another source:

Transformation Scheme
    Define a set of Transformations to be used to create the VTL script.

Ruleset Schemes
    Define the ruleset to be used to create the VTL script.
    This Ruleset Schemes are attached to the Transformation Scheme.

User Defined Operator Schemes
    Define the user defined operators to be used in the VTL script.
    This User Defined Operator Schemes are attached to the Transformation Scheme.


Step-by-step Solution
---------------------

Reading the VTL objects
^^^^^^^^^^^^^^^^^^^^^^^

Firstly, we need to read the VTL objects with :meth:`pysdmx.io.read_sdmx`.
It returns a :meth:`pysdmx.io.Message`.


.. code-block:: python

    from pysdmx.io import read_sdmx

    url = "https://registry.sdmx.io/sdmx/v2/structure/transformationscheme/FR1/BPE_CENSUS/1.0?references=descendants"
    msg = read_sdmx(input_str, validate=True)


Getting the metadata
^^^^^^^^^^^^^^^^^^^^

Now we have the metadata, we can extract the Transformation Schemes with ``structures_msg.get_transformation_schemes()``, this will get a list of Transformation Schemes.
Then with the list of Transformation Schemes, we can get the first one with ``transformation_schemes[0]``, but we can get any of the Transformation Schemes in the list or
even iterate over the list to get all of them.

As the Transformation Scheme contains the references for Ruleset Scheme and User Defined Operator Scheme, there is no need to extract them separately.


.. code-block:: python

   transformation_scheme = msg.get_transformation_scheme("TransformationScheme=FR1:BPE_CENSUS(1.0)")

Validating the metadata
^^^^^^^^^^^^^^^^^^^^^^^

Now we have the transformation, we can validate it.
The :meth:`pysdmx.toolkit.vtl.model_validations` method ensures that both the structure and content of your metadata
are correct before generating the final VTL script:

- Ensure that each item and scheme are correctly related to each other.
- Syntax validation for each VTL definition and expression to ensure they are correctly defined.
- Validate the VTL definitions by checking that they are consistent with the properties of the corresponding SDMX objects.

.. note::
    This validation can also be deferred until the VTL script is generated.
    Additionally, the Ruleset Scheme and User Defined Operator Scheme can be validated independently if needed.

For more information, please check :ref:`vtl-validation`

.. code-block:: python

    from pysdmx.toolkit.vtl.model_validations import model_validations

    # validate the metadata
    model_validations(transformation_scheme)


Generating the VTL script
^^^^^^^^^^^^^^^^^^^^^^^^^

Now we can generate the VTL script using the metadata with :meth:`pysdmx.toolkit.vtl.generate_vtl_script`.

The model_validation parameter defines a flag to perform the validation of the VTL objects
(explained in previous step). Default value is True

This function will generate the VTL script with the information form the items of the Transformation Scheme
and the attached Ruleset Scheme and User Defined Operator Scheme.

We can only generate the VTL script from a Transformation Scheme.

.. code-block:: python

    from pysdmx.toolkit.vtl.generate_vtl_script import generate_vtl_script

    # generate the VTL script
    vtl_script = generate_vtl_script(transformation_scheme, model_validation=True)

    print(vtl_script)

For more information, please check :ref:`vtl-generation`

How to use the VTL script
^^^^^^^^^^^^^^^^^^^^^^^^^

Now that the VTL script has been generated,
you are ready to run it.

Useful links:

- `VTL Engine Docs <https://docs.vtlengine.meaningfuldata.eu/index.html>`_.
- `VTL Semantic validation <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.semantic_analysis>`_.
- `VTL Script run <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.run>`_.
- `VTL Documentation <https://sdmx-twg.github.io/vtl/2.1/html/index.html>`_

Summary
^^^^^^^

In this tutorial, we learned how to generate a VTL script step by step using metadata stored in a
XML file with a Transformation Scheme structure.

We read the metadata from the SDMX-ML file, validated the VTL objects, and generated the VTL script.
This script can later be used to execute the validations and transformations, using the VTL engine.