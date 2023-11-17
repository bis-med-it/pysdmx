``pysdmx`` in a nutshell
========================

``pysdmx`` is an **opinionated** and **pragmatic** SDMX library written in
Python. It supports a **subset** of what SDMX offers and aims at 
keeping things **simple** whenever possible, so that using the library does
**not** require advance knowledge of SDMX.

``pysdmx`` aims to be a versatile SDMX toolbox for Python and,
therefore, covers different use cases, a few of which are 
highlighted below:

- **SDMX information model in Python**: ``pysdmx`` offers Python classes
  representing a **simplified subset of the SDMX information model**, thereby
  enabling a domain-driven development of SDMX processes in Python. The model
  classes are serializable.
- **Metadata in action**: One of the main features of ``pysdmx`` is to
  support retrieving metadata from a SDMX Registry (or any service compliant
  with the SDMX-REST 2.0.0 API), so that you can use them to power statistical
  processes.
- **Data discovery and data retrieval**: This functionality is **not
  available yet** but is on the development roadmap. In a nutshell, ``pysdmx``
  will allow listing public SDMX services, discovering the data available in
  these various services and retrieving data from these various services.

``pysdmx`` is published to `PyPI <https://pypi.org/>`_ and can be
installed using your preferred option (``pip``, ``pipx``, ``poetry``,
etc.).

For additional information, please refer to the
`project documentation <https://bis-med-it.github.io/pysdmx>`_.