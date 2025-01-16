``pysdmx`` in a nutshell
========================

What is ``pysdmx``?
-------------------

``pysdmx`` is a **pragmatic** and **opinionated** SDMX library written in
Python. It focuses on **simplicity**, providing a subset of SDMX
functionalities without requiring advanced knowledge of SDMX.

For a quick overview of SDMX, read the 
:ref:`"SDMX in 2 minutes" primer<model>` or refer to the SDMX documentation.

``pysdmx`` is developed as part of the ``sdmx.io`` project under the
`BIS Open Tech initiative
<https://www.bis.org/innovation/bis_open_tech.htm>`_.


What does it do?
----------------

``pysdmx`` aspires to be a versatile SDMX toolbox for Python, covering various
use cases. Here are some highlights:

SDMX information model in Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``pysdmx`` offers Python classes representing a **simplified subset of the
SDMX information model**, enabling a domain-driven development of
SDMX processes in Python.

The model classes support serialization in formats like ``JSON``, ``YAML``,
or ``MessagePack``. This functionality relies on the **msgspec** library.
Please refer to its `documentation <https://jcristharif.com/msgspec/>`_, to
learn more about serialization and deserialization of domain classes.

Explore the SDMX information model classes in the
:ref:`API documentation<model>`. These classes are part of the core
functionality and don't require additional installations.

Metadata in action
^^^^^^^^^^^^^^^^^^

SDMX metadata are very useful for documenting statistical processes. For
example, we can define the structure we expect for a data collection process
and share it with the organizations providing data so that they know what to
send.

However, metadata can do so much more than that, i.e. they can be "active" and
**drive various types of statistical processes**, such as:

- :ref:`fs`
- :ref:`physical-model`
- :ref:`validate`
- :ref:`map`
- :ref:`config`

``pysdmx`` supports retrieving metadata from an SDMX Registry or any service
compliant with the SDMX-REST 2.0.0 (or above) API.

These classes are part of the core functionality and don't require additional
installations.

Data discovery and data retrieval
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This functionality is **under development**. Once ready, ``pysdmx`` will
allow:

- Listing public SDMX services.
- Discovering data available in these services.
- Retrieving data from these services.

Although this functionality is still under development, it is already
possible to :ref:`build SDMX-REST queries and execute them against a 
web service<sdmx-rest>`.

Reading and writing SDMX datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Head to the :ref:`how-to guide<data-rw>` to learn how to read and write SDMX datasets.

How can I get it?
-----------------

``pysdmx`` is published on `PyPI <https://pypi.org/>`_ and can be
installed using your preferred method (``pip``, ``pipx``, ``poetry``,
etc.).

For the core functionality, use:

.. code:: bash

    pip install pysdmx

Some use cases require additional dependencies, which can be installed using 
`extras <https://peps.python.org/pep-0508/#extras>`_. For example,
to parse SDMX-ML messages, install the ``xml`` extra:

.. code:: bash

    pip install pysdmx[xml]

The following extras are available:

.. list-table:: Available extras
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Purpose
   * - ``xml``
     - Read and Write SDMX-ML messages
   * - ``pandas``
     - Handle SDMX datasets as Pandas data frames
