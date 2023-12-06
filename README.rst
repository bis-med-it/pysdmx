.. image:: https://img.shields.io/pypi/v/pysdmx.svg
   :target: https://pypi.org/project/pysdmx/

``pysdmx`` in a nutshell
========================

``pysdmx`` is a pragmatic and **opinionated** library written in Python. It
focuses on simplicity, providing a subset of SDMX functionalities without
requiring advanced knowledge of SDMX.

Key features:

- **SDMX information model in Python**: ``pysdmx`` offers Python classes
  representing a **simplified subset of the SDMX information model**,
  enabling a domain-driven development of SDMX processes with Python. These
  classes are serializable.
- **Metadata in action**: ``pysdmx`` supports retrieving metadata from an SDMX
  Registry or any service compliant with the SDMX-REST 2.0.0 API. Use these
  metadata to power statistical processes.
- **Data discovery and retrieval**: This functionality is under development.
  ``pysdmx`` will enable listing public SDMX services, discovering available
  data available, and retrieving data from these services.

``pysdmx`` is available on `PyPI <https://pypi.org/>`_ and can be
installed using options such as pip, pipx, poetry, etc.

For more details, check the `project documentation 
<https://py.sdmx.io>`_.
