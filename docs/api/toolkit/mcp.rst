MCP Server
==========

The MCP Toolkit exposes pysdmx data discovery and retrieval over the
`Model Context Protocol <https://modelcontextprotocol.io>`_, so that AI
assistants can find statistical datasets and retrieve the observations
themselves.

Requires the ``mcp`` and ``data`` extras::

    pip install pysdmx[mcp,data]

Run it over STDIO, the transport MCP clients launch::

    python -m pysdmx.toolkit.mcp

Or over Streamable HTTP::

    python -m pysdmx.toolkit.mcp --transport http --port 8000

Tools
-----

.. autofunction:: pysdmx.toolkit.mcp.list_services

.. autofunction:: pysdmx.toolkit.mcp.search_dataflows

.. autofunction:: pysdmx.toolkit.mcp.inspect_dataflow

.. autofunction:: pysdmx.toolkit.mcp.get_data
