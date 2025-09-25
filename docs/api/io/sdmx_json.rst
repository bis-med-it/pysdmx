.. _sdmx_json:

SDMX-JSON
=========

Currently, with this format, only structural metadata and reference metadata are
supported in pysdmx. The SDMX-JSON readers and writers are compatible with
SDMX-JSON 2.0.0 standard.

`SDMX-JSON 2.0.0 Structure Message <https://github.com/sdmx-twg/sdmx-json/blob/v2.0.0/structure-message/docs/1-sdmx-json-field-guide.md>`_

`SDMX-JSON 2.0.0 Metadata Message <https://github.com/sdmx-twg/sdmx-json/blob/v2.0.0/metadata-message/docs/1-sdmx-json-field-guide.md>`_

Reading
-------

Although the use of the :ref:`general reader<general-reader>` is always recommended,
specific readers for SDMX-JSON are also available:

.. _sdmx_json_20_reader_structure:

- STRUCTURE_SDMX_JSON_2_0_0 -> pysdmx.io.json.sdmxjson2.reader.structure

.. autofunction:: pysdmx.io.json.sdmxjson2.reader.structure.read

.. _sdmx_json_20_reader_refmeta:

- REFMETA_SDMX_JSON_2_0_0 -> pysdmx.io.json.sdmxjson2.reader.metadata

.. autofunction:: pysdmx.io.json.sdmxjson2.reader.metadata.read


Writing
-------

Although the use of the :ref:`general writer<general-writer>` is always recommended,
specific writers for SDMX-JSON are also available:

.. _sdmx_json_20_writer_structure:

- STRUCTURE_SDMX_JSON_2_0_0 -> pysdmx.io.json.sdmxjson2.writer.structure

.. autofunction:: pysdmx.io.json.sdmxjson2.writer.structure.write

.. _sdmx_json_20_writer_refmeta:

- REFMETA_SDMX_JSON_2_0_0 -> pysdmx.io.json.sdmxjson2.writer.metadata

.. autofunction:: pysdmx.io.json.sdmxjson2.writer.metadata.write
