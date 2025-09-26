.. _sdmx_ml:

SDMX-ML
=======
SDMX-ML is the most used format to exchange statistical data and metadata.
On pysdmx, we support the validation against XSD schemas.

`SDMX-ML 2.1 specification <https://github.com/sdmx-twg/sdmx-ml/tree/v2.1/documentation>`_

`SDMX-ML 2.1 XSD Schema <https://github.com/sdmx-twg/sdmx-ml/tree/v2.1/schemas>`_

`SDMX-ML 3.0 specification <https://github.com/sdmx-twg/sdmx-ml/tree/v3.0.0/documentation>`_

`SDMX-ML 3.0 XSD Schema <https://github.com/sdmx-twg/sdmx-ml/tree/v3.0.0/schemas>`_

`SDMX-ML 3.1 specification <https://github.com/sdmx-twg/sdmx-ml/tree/v3.1.0/documentation>`_

`SDMX-ML 3.1 XSD Schema <https://github.com/sdmx-twg/sdmx-ml/tree/v3.1.0/schemas>`_


.. important::

    To use the SDMX-ML functionalities, you need to install the `pysdmx[xml]` extra.

    Check the :ref:`installation guide <installation>` for more information.


Reading
-------
Although the use of the :ref:`general reader<general-reader>` is always recommended,
specific readers for SDMX-ML are also available:

.. _sdmx_ml_21_gen_reader:

- DATA_SDMX_ML_2_1_GEN -> pysdmx.io.xml.sdmx21.reader.generic

.. autofunction:: pysdmx.io.xml.sdmx21.reader.generic.read

.. _sdmx_ml_21_spe_reader:

- DATA_SDMX_ML_2_1_STR -> pysdmx.io.xml.sdmx21.reader.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure_specific.read

.. _sdmx_ml_21_structure_reader:

- STRUCTURE_SDMX_ML_2_1 -> pysdmx.io.xml.sdmx21.reader.structure

.. autofunction:: pysdmx.io.xml.sdmx21.reader.structure.read

.. _sdmx_ml_30_spe_reader:

- DATA_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx30.reader.structure_specific.read

.. _sdmx_ml_30_structure_reader:

- STRUCTURE_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.reader.structure

.. autofunction:: pysdmx.io.xml.sdmx30.reader.structure.read

.. _sdmx_ml_31_spe_reader:

- DATA_SDMX_ML_3_1 -> pysdmx.io.xml.sdmx31.reader.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx31.reader.structure_specific.read

.. _sdmx_ml_31_structure_reader:

- STRUCTURE_SDMX_ML_3_1 -> pysdmx.io.xml.sdmx31.reader.structure

.. autofunction:: pysdmx.io.xml.sdmx31.reader.structure.read

After reading the string, we will have a message object that contains a pandas
DataFrame with the data or a structure object with the metadata.


Writing
-------

Although the use of the :ref:`general writer<general-writer>` is always recommended,
specific writers for SDMX-ML are also available:

.. _sdmx_ml_21_gen_writer:

- DATA_SDMX_ML_2_1_GEN -> pysdmx.io.xml.sdmx21.writer.generic

.. autofunction:: pysdmx.io.xml.sdmx21.writer.generic.write

.. _sdmx_ml_21_spe_writer:

- DATA_SDMX_ML_2_1_STR -> pysdmx.io.xml.sdmx21.writer.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure_specific.write

.. _sdmx_ml_21_structure_writer:

- STRUCTURE_SDMX_ML_2_1 -> pysdmx.io.xml.sdmx21.writer.structure

.. autofunction:: pysdmx.io.xml.sdmx21.writer.structure.write

.. _sdmx_ml_30_spe_writer:

- DATA_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.writer.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx30.writer.structure_specific.write

.. _sdmx_ml_30_structure_writer:

- STRUCTURE_SDMX_ML_3_0 -> pysdmx.io.xml.sdmx30.writer.structure

.. autofunction:: pysdmx.io.xml.sdmx30.writer.structure.write

.. _sdmx_ml_31_spe_writer:

- DATA_SDMX_ML_3_1 -> pysdmx.io.xml.sdmx31.writer.structure_specific

.. autofunction:: pysdmx.io.xml.sdmx31.writer.structure_specific.write

.. _sdmx_ml_31_structure_writer:

- STRUCTURE_SDMX_ML_3_1 -> pysdmx.io.xml.sdmx31.writer.structure

.. autofunction:: pysdmx.io.xml.sdmx31.writer.structure.write

