.. _map:

Map Your Data
=============

In this tutorial, we explore how ``pysdmx`` facilitates **mapping data** in
a metadata-driven fashion, relying solely on the metadata stored in an SDMX
Registry.

Required Metadata
-----------------

SDMX supports various mapping rules, ranging from simple mappings (e.g.,
mapping a list of non-standard country codes to ISO 3166 2-letter country
codes) to more complex ones (e.g., many-to-many and time-dependent mapping
rules). To support the definition of mapping rules, SDMX offers **structure
maps**, **component maps**, **representation maps**, **fixed value maps**,
**epoch maps**, and **date pattern maps**. ``pysdmx`` supports all these
types except epoch maps. Examples demonstrating how these can be used to
define mapping rules are provided below.

For additional information about the various types of SDMX artifacts, please
refer to the `SDMX documentation <https://sdmx.org/>`_.

Step-by-step Solution
---------------------

``pysdmx`` allows retrieving metadata from an SDMX Registry in either a
synchronous manner (via ``pymedal.fmr.RegistryClient``) or asynchronously
(via ``pymedal.fmr.AsyncRegistryClient``). The choice depends on the use case
(and preference), but we tend to use the asynchronous client by default as
it is non-blocking.

Connecting to a Registry
^^^^^^^^^^^^^^^^^^^^^^^^

First, we need an instance of the client to connect to our target Registry.
When instantiating the client, we pass the SDMX-REST endpoint of the Registry.
If we use the `FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_,
i.e., the reference Implementation of the SDMX Registry specification, the
endpoint will be the URL at which the FMR is available, followed by
``/sdmx/v2/``.

.. code-block:: python

    from pysdmx.api.fmr import AsyncRegistryClient
    client = AsyncRegistryClient("[Your_endpoint_comes_here]")

Retrieving Simple Code Mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A common use case is mapping codes used by external parties to codes used by
internal processes. For example, a third party might use their own "standard"
to represent currencies (e.g., ``C$`` for the Canadian dollar), while
internal data compilation processes prefer widely adopted standards, such as
ISO 4217 3-letter currency codes (e.g., ``CAD``). This type of mapping
(``C$ => CAD``) is expressed in SDMX using a ``RepresentationMap``.

``pysdmx`` allows retrieving such mappings via the ``get_code_map`` method
exposed by the client. For example, let's assume the BIS maintains a map of
the IMF 3-digit country codes to the ISO 3166 2-letter country codes, and
that the ID of this map is ``IMF_2_ISO``:

.. code-block:: python

    rm = client.get_code_map("BIS", "IMF_2_ISO")

Now we have a list of code maps that can be iterated over. Each mapping
includes the source and target codes and may include business validity
details describing when the association is valid (via its `valid_from` and
`valid_to` properties).

.. code-block:: python

    for m in rm:
        print(m)
        # Output example:
        # ValueMap(source='146', target='CH', valid_from=None, valid_to=None)

Applying Structure Maps
^^^^^^^^^^^^^^^^^^^^^^^

While the example above is quite simple, SDMX also allows more complex
mappings, such as mapping a source dataflow to a target dataflow.

Let's assume the following mapping definition:

+---------------+-------------+-----------+--------------------+
| Source        | Target      | Comp Type | Mapping Type       |
+===============+=============+===========+====================+
|               | FREQ        | Dimension | Fixed Value        |
+---------------+-------------+-----------+--------------------+
| CONTRACT      | CONTRACT    | Dimension | Representation Map |
+---------------+-------------+-----------+--------------------+
| OPT_TYP       | OPTION_TYPE | Dimension | Implicit           |
+---------------+-------------+-----------+--------------------+
| ACTIVITY_DATE | TIME_PERIOD | Dimension | Date Pattern       |
+---------------+-------------+-----------+--------------------+
| TO            | TO          | Measure   | Implicit           |
+---------------+-------------+-----------+--------------------+
| OI            | OI          | Measure   | Implicit           |
+---------------+-------------+-----------+--------------------+
|               | CONF_STATUS | Attribute | Fixed Value        |
+---------------+-------------+-----------+--------------------+

In a nutshell, we need to:

- Copy the values for ``OPTION_TYPE``, ``TO``, and ``OI`` (Implicit).
- Map codes for ``CONTRACT`` (Representation Map).
- Parse dates and then reformat them for ``ACTIVITY_DATE`` (Date Pattern).
- Set fixed values for ``FREQ`` and ``CONF_STATUS`` (Fixed Value).

Let's retrieve the structure map, using the ``get_mapping`` function exposed
by the client, assuming its ID is ``SRC_2_TGT`` and it is maintained by the
BIS:

.. code-block:: python

    mapping = client.get_mapping("BIS", "SRC_2_TGT")

The object returns the different mapping rules that need to be applied,
organized by mapping types. Each mapping type is available via its property.

Copying Values
""""""""""""""
Some values merely need to be copied from the source to the target. This type
of mapping can be retrieved via the ``implicit_maps`` property. As we know,
this is the case for ``OPTION_TYPE``, ``TO``, and ``OI``.

.. code-block:: python

    for m in mapping.implicit_maps:
        print(m)
        # Output example:
        # ImplicitComponentMap(source='OPT_TYP', target='OPTION_TYPE')

As seen, the operation to be applied is fairly simple:

- The value must be copied from the source to the target.
- The target component might need to be renamed (this is the case for
  ``OPT_TYP``).

Setting Fixed Values
""""""""""""""""""""
Another fairly simple case is setting fixed values. This is the case for
``FREQ`` and ``CONF_STATUS``, where we need to set the value to ``M``
(Monthly) and ``C`` (Confidential) respectively.

.. code-block:: python

    for m in mapping.fixed_value_maps:
        print(m)
        # Output example:
        # FixedValueMap(target='FREQ', value='M')

Mapping Codes
"""""""""""""

Then we have one component (``CONTRACT``) for which the values in the source
need to be mapped to another value in the target, using a mapping table. Such
mappings can be retrieved via the ``component_maps`` property:

.. code-block:: python

    for m in mapping.component_maps:
        print(m)
        # Output example:
        # ComponentMap(
        #     source='CONTRACT',
        #     target='CONTRACT',
        #     values=[
        #         ValueMap(source='PROD TYPE', target='_T', valid_from=None, valid_to=None),
        #         ValueMap(source=re.compile('^([A-Z0-9]+)$'), target='\\1', valid_from=None, valid_to=None)
        #     ]
        # )

As can be seen, this mapping is quite interesting:

- Whenever we find the value ``PROD TYPE`` in the source, we need to map it to
  ``_T`` in the target. This is easy.
- But the next one is a ... regular expression with a capture group. Basically,
  it says that whatever is between the beginning and the end of the cell
  should be copied over to the target, i.e. an implicit mapping...

From the above, we can learn two things:

- Mappings don't necessarily map simple values to another; sometimes, it
  can be a complex regular expression, with one or more capture groups.
- Mappings need to be executed in order. In the example above, if the regular
  expression was executed first, ``PROD TYPE`` would never be matched to
  ``_T``.

At this stage, it is also worth noting that SDMX allows mapping N components
in the source to N components in the target (for example, 2 components in the
source to 6 components in the target). This type of mapping is available via
the ``multiple_component_maps`` property. The objects returned are similar to
the objects returned by ``component_maps`` except that the source and target
properties, as well as their values, allow a list of values instead of a
single one.

Reformatting Dates
""""""""""""""""""
We still need to map one component, i.e. ``ACTIVITY_DATE``. For this, we need
to use a date pattern. Such mapping types are available via the ``date_maps``
property:

.. code-block:: python

    for m in rm.date_maps:
        print(m)
        # Output example:
        # PatternMap(source='ACTIVITY_DATE', target='TIME_PERIOD', pattern='MM/dd/yyyy', frequency='M')

Here, we need to parse the date using the supplied pattern, ``MM/dd/yyyy``,
i.e., dates like ``12/25/2013``. Once this is done, we need to format them to
SDMX reporting periods of monthly frequency (i.e., ``2013-12`` in this
example). Such operations can be achieved using Python ``strptime`` and
``strftime`` provided by the ``datetime`` module.

We have now mapped the 5 components in the source to the 7 components in the
target, thereby completing the work needed for this tutorial.

Summary
-------

In this tutorial, we have created a client to retrieve metadata from the SDMX
Global Registry, and we have used the ``get_mapping`` and ``get_code_map``
methods to retrieve mapping definitions.

This tutorial only scratches the surface of what SDMX mappings can do.
Nevertheless, we now have a good idea of how ``pysdmx`` can help
write SDMX mapping code in Python.
