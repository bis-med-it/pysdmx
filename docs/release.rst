Release notes
=============

1.1.0 (2025-02-06)
------------------

Added
^^^^^

- Support SDMX-REST v2.1.0 (and registration queries).
- Asynchronous client for SDMX-REST services.
- Option to set a timeout to SDMX-REST services client.

Fixed
^^^^^

- Handling of empty item schemes in SDMX-JSON and Fusion-JSON.
- Wrong URN returned by Schema objects.
- Wrong media type for mapping queries in the fmr module (SDMX-JSON only).


1.0.0 (2025-01-20)
------------------

Added
^^^^^

- Core domain classes for the SDMX information model.
- Sync and async clients to retrieve metadata
  from an SDMX Registry or SDMX-REST service, and use them to
  drive statistical business processes.
- Data readers and writers for SDMX-ML 2.1, SDMX-CSV 2.0 and
  SDMX-CSV 1.0
- Structures readers and writers SDMX-ML 2.1, SDMX-JSON 2.0 and
  Fusion-JSON
- SDMX-REST query builders and a service client to execute
  queries against SDMX-REST services.
- Utility functions to handle SDMX URNs.
