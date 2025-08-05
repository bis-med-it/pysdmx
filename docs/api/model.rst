.. _model:

Information model
=================

SDMX in 2 minutes
-----------------

To derive meaning from statistical data, understanding the associated
**concepts** is essential. For instance, the number ``1.2953``, on its own,
is meaningless. However, if we know it represents the *exchange rate* for
the *US dollar* against the *euro* on *23 November 2006*, the data becomes
more meaningful.

Concepts are categorized into three types based on their roles:

- **Dimensions**: **Identify** and **describe** the data. The
  combination of dimension values uniquely identifies statistical
  data (similar to a *primary key*). For exchange rates, examples of
  dimensions include numerator and denominator currencies, exchange rates
  types, and reference periods.
- **Attributes**: Do not contribute to data identification but **provide
  useful descriptive information**. For example, the confidentiality
  status of statistical data.
- **Measures**: Hold the values we care about, i.e. the statistical
  data.

Concepts usually have an **expected type** (representation). For instance,
currencies are typically represented using ISO 3-letter currency codes.
Many concepts expect a finite number of codes (**codelist** in SDMX), while
others have characteristics such as data type, minimum and maximum length,
or regular expressions (**facets** in SDMX).

All data in a statistical domain belong to a **dataset** (**dataflow** in
SDMX). Data are reported by various **providers** and must comply with the
**expected structure** of that dataflow (data structure definition or DSD
in SDMX). The structure specifies relevant concepts, their roles, and
expected types.

Metadata-driven processes
-------------------------

While the above outlines the metadata needed to describe statistical data,
SDMX boasts a rich information model with various metadata types. These
metadata can power diverse statistical processes, including data collection,
validation, and mapping.

``pysdmx`` provides an opinionated implementation of a subset of the SDMX
information model through Python classes. These classes enable the definition
of APIs for statistical data processes.

To efficiently support these processes, pysdmx model classes can be serialized
in various formats, such as JSON, YAML, or MessagePack.

Refer to the pages below for detailed descriptions of the key model classes
defined by ``pysdmx``.

API Reference
-------------

.. toctree::
   :maxdepth: 1

   model/code
   model/concept
   model/dataflow
   model/dataset
   model/category
   model/gds
   model/map
   model/message
   model/refmeta
   model/organisation
   model/vtl