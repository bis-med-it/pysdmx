.. _generate_sdmx:

Generate VTL Objects from VTL Script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this tutorial, we shall examine the utilization of ``vtlengine``
for the generation of VTL objects from a VTL script.

Generate Objects
----------------
First of all, we need a VTL Script, we can get it from a File or
from a string we create.

.. code-block:: python

    from pathlib import Path

    # Path to the VTL script file in the same directory as this script
    vtl_script = Path(__file__).parent / "vtl_script.vtl"

    vtl_script = """
    define datapoint ruleset signValidation
            (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
                is
                sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
                "sign1c" errorlevel 1
                end datapoint ruleset;
    define operator filter_ds
            (ds1 dataset, great_cons string default "1",
             less_cons number default 4.0)
            returns dataset
            is ds1[filter Me_1 > great_cons and Me_2 < less_cons]
            end operator;
    DS_r <- DS_1 + 1;
                    """


Now we have the VTL script, we can generate the VTL objects from it.

To do this, we need the ``script``, ``agency_id``, ``id`` and ``Version``
of the generated :class:`Transformation Scheme <pysdmx.model.vtl.TransformationScheme>`

.. code-block:: python

    from vtlengine import generate_sdmx

    # Generate a Transformation Scheme from the VTL script
    ts_scheme = generate_sdmx(script=vtl_script, agency_id="MD", id="TS1", version="1.0")

Now we have the `ts_scheme` object, which is an instance of a :class:`Transformation Scheme <pysdmx.model.vtl.TransformationScheme>`


For more information on how to use the ``vtlengine``, please refer to the
`vtlengine run documentation <https://docs.vtlengine.meaningfuldata.eu/walkthrough.html>`_
