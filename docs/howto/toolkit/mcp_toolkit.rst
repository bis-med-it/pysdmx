.. _mcp_toolkit:

MCP Server
==========

The MCP Toolkit turns pysdmx into a
`Model Context Protocol <https://modelcontextprotocol.io>`_ server, so an
AI assistant can discover SDMX dataflows and **retrieve the observations**,
rather than being handed a query URL to fetch by itself.

It wraps :class:`pysdmx.api.dc.pd.PandasConnector` and exposes four tools.

Installation
------------

.. code-block:: bash

    pip install pysdmx[mcp,data]

The ``mcp`` extra brings in FastMCP; ``data`` brings in Pandas, which the
underlying connector needs.

Running the server
------------------

Most MCP clients launch the server themselves over STDIO:

.. code-block:: bash

    python -m pysdmx.toolkit.mcp

To share one instance over the network instead, use Streamable HTTP:

.. code-block:: bash

    python -m pysdmx.toolkit.mcp --transport http --host 127.0.0.1 --port 8000

Client configuration
--------------------

**Claude Desktop** — add to ``claude_desktop_config.json``:

.. code-block:: json

    {
      "mcpServers": {
        "sdmx": {
          "command": "python",
          "args": ["-m", "pysdmx.toolkit.mcp"]
        }
      }
    }

**Claude Code** — from the command line:

.. code-block:: bash

    claude mcp add sdmx -- python -m pysdmx.toolkit.mcp

**Cursor** — add to ``.cursor/mcp.json``:

.. code-block:: json

    {
      "mcpServers": {
        "sdmx": {
          "command": "python",
          "args": ["-m", "pysdmx.toolkit.mcp"]
        }
      }
    }

Point ``command`` at the Python interpreter of the environment where
pysdmx is installed if it is not the one on your ``PATH``.

The tools
---------

The four tools are meant to be called in order.

``list_services``
    Reports the endpoints in :class:`pysdmx.api.dc.Endpoints` with
    capability notes. Any SDMX-REST v2 base URL can also be passed to
    the other tools as ``service``.

``search_dataflows``
    Issues a single ``dataflows()`` call and matches terms locally
    against each dataflow's ID, name and description. Space-separated
    words are treated as alternatives, so synonyms cost nothing extra.

``inspect_dataflow``
    Returns components, availability-backed codes and size signals.
    Accepts ``filters`` to scope availability, and ``find_code`` to
    locate a value across every component that carries it.

``get_data``
    Retrieves the observations as records, capped and with an explicit
    truncation flag.

A worked example
----------------

Asking an assistant *"how much do Swiss banks have in foreign claims
since 2020?"* drives the following sequence against the BIS.

**1. Find the dataflow.**

.. code-block:: text

    search_dataflows(query="consolidated banking")

    -> ref: BIS:WS_CBS_PUB(1.0)
       name: Consolidated banking
       matched_on: name
       next_step: Call inspect_dataflow with ref='BIS:WS_CBS_PUB(1.0)' ...

**2. Work out what "Swiss" means here.**

.. code-block:: text

    inspect_dataflow(ref="BIS:WS_CBS_PUB(1.0)", find_code="CH")

    -> code_locations:
         L_REP_CTY      (reporting country)
         CBS_BANK_TYPE  (bank type (shares a country codelist))
         L_CP_COUNTRY   (counterparty country)
       series_count: 228370
       size_warning: This scope holds 228,370 series ...
       next_step: That code is ambiguous - it appears in 3 components ...

This is the step that prevents a confidently wrong answer. ``CH`` is
valid in three different components of this dataflow, and each answers a
different question: claims *by* Swiss banks, claims *on* Switzerland, or
a bank-type code that happens to share the country codelist.

**3. Scope it, and check the size.**

.. code-block:: text

    inspect_dataflow(
        ref="BIS:WS_CBS_PUB(1.0)",
        filters="L_MEASURE = 'S' AND L_REP_CTY = 'CH' AND FREQ = 'Q'",
    )

    -> series_count: 6671   (down from 228370)

If the question were only *whether* data exist, the answer is already
here and ``get_data`` should not be called.

**4. Retrieve the numbers.**

.. code-block:: text

    get_data(
        ref="BIS:WS_CBS_PUB(1.0)",
        filters="L_MEASURE = 'S' AND L_REP_CTY = 'CH' AND FREQ = 'Q'"
                " AND TIME_PERIOD >= '2020-Q1'",
        columns=["OBS_VALUE"],
        limit=500,
    )

    -> row_count: 500
       total_rows_available: 112648
       truncated: true
       next_step: Truncated: 112,648 rows matched but only 500 were
                  returned. These are the first rows in service order,
                  not a sample ...

Things worth knowing
--------------------

**Conjunctions only.** The query parser supports ``AND`` between
clauses. Never generate ``OR``; for several values of one component use
``IN ('A', 'B')``.

**Availability is not validity.** ``inspect_dataflow`` reports the codes
for which data currently exist. A code absent from that list may still
be valid in the full codelist, so its absence is not evidence that
something does not exist.

**Size before retrieval.** ``obs_count`` is often unreported — the BIS
returns ``None`` for it — so ``series_count`` is the signal to rely on.
The tools warn when a scope is large enough that retrieval will
truncate.

**Truncation is not sampling.** When ``truncated`` is true the rows
returned are the first ones in service order. They must not be
aggregated as though they were a representative sample; narrow the
filter instead.

**Time filters degrade gracefully.** ``TIME_PERIOD`` comparisons are
pushed down to the service when it supports them. If the service
rejects the query, the clause is stripped, the narrower query is
retried, and the cutoff is applied with Pandas. The response reports
this in ``filter_fallback``.

**Errors keep their meaning.** Every failure is reported with the kind
of error it was, so an assistant can tell a transient outage
(``unavailable``, retriable) from a bad reference (``not_found``, not
retriable) rather than retrying blindly or giving up too early.
