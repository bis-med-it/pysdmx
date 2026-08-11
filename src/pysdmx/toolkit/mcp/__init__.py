"""MCP server exposing SDMX data discovery and retrieval to AI assistants.

Requires the ``mcp`` and ``data`` extras::

    pip install pysdmx[mcp,data]

Run it over STDIO, which is what MCP clients launch::

    python -m pysdmx.toolkit.mcp

Or serve it over Streamable HTTP::

    python -m pysdmx.toolkit.mcp --transport http --port 8000
"""

from pysdmx.toolkit.mcp.server import (
    get_data,
    inspect_dataflow,
    list_services,
    mcp,
    search_dataflows,
)

__all__ = [
    "get_data",
    "inspect_dataflow",
    "list_services",
    "mcp",
    "search_dataflows",
]
