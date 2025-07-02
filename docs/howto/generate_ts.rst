.. _generate_ts:

Generate a TransformationScheme from VTL Script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this tutorial, we will generate pysdmx VTL objects from a VTL script using the `vtlengine` library.

.. important::

    For this tutorial, you also need to install the `pysdmx[vtl]` extra.

    Check the :ref:`installation guide <installation>` for more information.

Firstly, we generate a VTL Script as a String, or read it from a file.

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

Secondly, to generate a :class:`Transformation Scheme <pysdmx.model.vtl.TransformationScheme>` object,
we use the `generate_sdmx <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.generate_sdmx>`_
function from the ``vtlengine`` library. We will need to pass the ``script``, ``agency_id``, ``id`` and ``version``

.. code-block:: python

    from vtlengine import generate_sdmx

    # Generate a Transformation Scheme from the VTL script
    ts_scheme = generate_sdmx(script=vtl_script, agency_id="MD", id="TS1", version="1.0")

    print(repr(ts_scheme))

Finally, the generated `TransformationScheme` object can now be serialized in a SDMX message or may be used to
perform further operations, like :ref:`running the TransformationScheme <run_sdmx>`.

Check the :ref:`VTL Toolkit <vtl_toolkit>` for more information on how to use the generated TransformationScheme.
