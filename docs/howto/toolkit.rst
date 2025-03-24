.. _toolkit:
Description
===============================

The toolkit module is a set of functions that help to generate VTL script from metadata.
The purpose of this module is to provide a set of functions that can be used to validate the metadata from a transformation scheme,
ruleset scheme, and user defined operator scheme and generate the VTL script from the transformation scheme.


Generate VTL script
===============================

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

Reading the metadata
^^^^^^^^^^^^^^^^^^^^^^^^

we need to read the metadata from the SDMX reader.
First of all, we need to extract the metadata and the format with ``reader.sdmx.read_sdmx``.
The ``read_sdmx`` function reads the metadata from the input file and returns the metadata.
Then with  ``reader.sdmx.process_string_to_read`` we can extract the metadata structure.

input_str is the string of the metadata file and read_format is the format of the metadata file.


.. code-block:: python

    from pysdmx.reader.sdmx import read_sdmx
    from pysdmx.reader.sdmx import process_string_to_read
    from pysdmx.model import RulesetScheme, UserDefinedOperatorScheme, TransformationScheme

    data_path = "[metadata_file_path]"

    input_str, read_format = process_string_to_read(data_path)
    result = read_sdmx(input_str, validate=True).structures


Getting the metadata
^^^^^^^^^^^^^^^^^^^^^^^^

Now we have the metadata, we can extract the Transformation Scheme, Ruleset Scheme and User Defined Operator Scheme.

.. code-block:: python

        for scheme in result:
            if isinstance(scheme, RulesetScheme):
                ruleset_scheme = scheme
            elif isinstance(scheme, UserDefinedOperatorScheme):
                udo_scheme = scheme
            elif isinstance(scheme, TransformationScheme):
                transformation_scheme = scheme


Validating the metadata
^^^^^^^^^^^^^^^^^^^^^^^^

Now we have the metadata, we can validate the metadata with ``toolkit.vtl.model_validations.model_validations``.
The validation is done on every item of each scheme and the scheme itself.
This validation can be done later when we generate the VTL script.
We can validate every scheme individually, but if ruleset_scheme and udo_scheme are attached
to the transformation_scheme, we can validate the transformation_scheme and it will validate
the ruleset_scheme and udo_scheme.


.. code-block:: python

    from pysdmx.toolkit.vtl.model_validations import model_validations

    # validate the metadata
    model_validations(transformation_scheme)




Generating the VTL script
^^^^^^^^^^^^^^^^^^^^^^^^

Now we can generate the VTL script using the metadata with ``toolkit.vtl.generate_vtl_script.generate_vtl_script``.
If we want to do the validation in this step, we can do it just by
setting the model_validation parameter to True else we can set it to False if
we don't want to do the validation.
This function will generate the VTL script with the information form the items of the Transformation Scheme
and the attached Ruleset Scheme and User Defined Operator Scheme.

We can only generate the VTL script from a Transformation Scheme.

.. code-block:: python

    from pysdmx.toolkit.vtl.generate_vtl_script import generate_vtl_script

    # generate the VTL script
    vtl_script = generate_vtl_script(transformation_scheme, model_validation=True)

    print(vtl_script)


Summary
-------

In this tutorial, we learned how to generate a VTL script step by step using metadata stored in a
XML file with a Transformation Scheme structure.
We read the metadata from the XML file, validated the metadata, and generated the VTL script.
