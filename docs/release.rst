Release notes
=============

1.0.0 (2025-01-20)
------------------

Added
^^^^^

- Offer core domain classes for the SDMX information model.
- Offer sync and async clients to retrieve metadata
  from an SDMX Registry or SDMX-REST service, and use them to
  drive statistical business processes.
- Offer SDMX-REST query builders and a service client to execute
  queries against SDMX-REST services.
- Offer functions to handle SDMX URNs.
- Offer data readers and writers for the following formats:
    - SDMX-ML 2.1
        - GenericData (Series & AllDimensions)
        - StructureSpecificData (Series & AllDimensions)
    - SDMX-CSV 2.0
    - SDMX-CSV 1.0
- Offers structures readers and writers for the following formats:
    - SDMX-ML 2.1
    - SDMX-JSON 2.0
    - FusionJSON
