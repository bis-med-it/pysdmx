.. |pypi badge| image:: https://img.shields.io/pypi/v/pysdmx.svg
   :target: https://pypi.org/project/pysdmx/

.. |awesome badge| image:: https://awesome.re/mentioned-badge.svg
   :target: http://www.awesomeofficialstatistics.org

|pypi badge| |awesome badge|

``pysdmx`` in a nutshell
************************

What is pysdmx?
===============

``pysdmx`` is a **pragmatic** and **opinionated** SDMX library written in
**Python**. It focuses on **simplicity**, providing a subset of SDMX functionalities
without requiring advanced knowledge of SDMX. ``pysdmx`` is developed as part of
the `sdmx.io <http://sdmx.io/>`_ project under the **BIS Open Tech initiative**.

What does it do?
================

``pysdmx`` aspires to be a versatile SDMX toolbox for Python, covering various
use cases. Here are some highlights:

SDMX information model in Python
--------------------------------

``pysdmx`` offers Python classes representing a **simplified subset of the SDMX
information model**, enabling a domain-driven development of SDMX processes in
Python. The model classes support serialization in formats like JSON, YAML, or
MessagePack. This functionality relies on the 
`msgspec library <https://jcristharif.com/msgspec/>`_.

Metadata in action
------------------

SDMX metadata are very useful for documenting statistical processes. For example,
they can define the structure we expect for a data collection process and share
it with the organizations providing data so that they know what to send.

However, metadata can do so much more than that, i.e., they can be “active” and
**drive various types of statistical processes**, such as generating the filesystem
layout, creating the physical data model, validating data, mapping data, and
configuring processes. To drive such processes, ``pysdmx`` supports retrieving
metadata from an SDMX Registry or any service compliant with the SDMX-REST 2.0.0 (or
above) API. Use these metadata to power your own statistical processes!

Reading and writing SDMX files
------------------------------

``pysdmx`` supports reading and writing SDMX data and structure messages, in various
formats, such as SDMX-CSV, SDMX-JSON, and SDMX-ML.

Data discovery and data retrieval
---------------------------------

This functionality is under development. Once ready, ``pysdmx`` will allow:
 
- **Listing public SDMX services**.
- **Discovering data** available in these services.
- **Retrieving data** from these services.
 
This functionality is based on the **SDMX Global Discovery Service initiative**.

Integration with the ecosystem
------------------------------

``pysdmx`` integrates nicely with other standards, like the `Validation and
Transformation Language (VTL) <https://sdmx.org/about-sdmx/about-vtl/>`_,
and major Python libraries like `Pandas <https://pandas.pydata.org/>`_.
Take a look at the ``pysdmx`` toolkit module to learn more.

``pysdmx`` is available on `PyPI <https://pypi.org/>`_ and can be
installed using options such as pip, pipx, poetry, etc.

For more details, check the `project documentation 
<https://py.sdmx.io>`_.
