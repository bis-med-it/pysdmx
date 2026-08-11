"""Command-line entry point for the pysdmx MCP server.

Defaults to STDIO, which is the transport MCP clients such as Claude
Desktop, Claude Code and Cursor launch. Pass ``--transport http`` to
serve over Streamable HTTP instead.
"""

import argparse
from typing import Optional, Sequence

from pysdmx.toolkit.mcp.server import mcp


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Parse arguments and run the server.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.
    """
    parser = argparse.ArgumentParser(
        prog="python -m pysdmx.toolkit.mcp",
        description=(
            "MCP server that discovers and retrieves official statistics "
            "from SDMX-REST v2 services."
        ),
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport to serve on (default: stdio).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address for --transport http (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for --transport http (default: 8000).",
    )
    args = parser.parse_args(argv)

    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
