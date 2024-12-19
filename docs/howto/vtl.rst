.. _vtl:

Using VTL for Validation
^^^^^^^^^^^^^^^^^^^^^^^^^

.. important::
    A seamless integration of ``pysdmx`` and ``vtlengine`` will modify this
    tutorial. The current version is a placeholder for the upcoming changes.
    For the latest updates, please check
    `issue #158 <https://github.com/bis-med-it/pysdmx/issues/158>`_.

In this tutorial, we shall examine the utilization of ``pysdmx``
for reading **data** and **metadata** to generate and operate on
datapoints using ``vtlengine``.

Numerous types of operations can be performed; however, this
tutorial will focus exclusively on the fundamental ones.

.. contents::
   :local:
   :depth: 2

Required Metadata
-----------------

For the present scenario, the requisite metadata is contingent
upon the desired operations. For reference please check
`sdmx to vtl documentation <https://sdmx.org/wp-content/uploads/SDMX_3-0-0_SECTION_2_FINAL-1_0.pdf#%5B%7B%22num%22%3A295%2C%22gen%22%3A0[…]e%22%3A%22XYZ%22%7D%2C87%2C736%2C0%5D>`_

Step-by-Step Solution
---------------------

``pysdmx`` facilitates the reading of data and metadata from an SDMX
file. For the purpose of this tutorial, we shall employ the XML files
``metadata.xml`` (data structure) and ``data.xml`` (data).

Reading the Data
~~~~~~~~~~~~~~~~

The initial step involves reading the data structure and data from the
SDMX files:

.. code-block:: python

    def read_sample(path: Path):
        with open(path, "r") as f:
            return f.read()

    # Read metadata
    metadata_sample = read_sample(Path("metadata.xml"))
    meta_content, filetype = process_string_to_read(metadata_sample)
    metadata_result = read_xml(meta_content, validate=True)

    # Read data
    data_sample = read_sample(Path("data.xml"))
    data_content, filetype = process_string_to_read(data_sample)
    data_result = read_xml(data_content, validate=True)

Filtering the Data
~~~~~~~~~~~~~~~~~~

Subsequent to obtaining the metadata and data, the desired dataflows and
data structures must be filtered:

.. code-block:: python

    data_structure_1 = metadata_result["DataStructures"]["DS_1"]
    data_1 = data_result["DS_1"].data

    data_structure_2 = metadata_result["DataStructures"]["DS_2"]
    data_2 = data_result["DS_2"].data

Parsing the Metadata
~~~~~~~~~~~~~~~~~~~~

To construct the datapoint, the metadata must be converted to the VTL
format using the ``to_vtl_json`` upcoming **DataStructureDefinition** method:

.. code-block:: python

    from pysdmx.model.dataflow import Component, DataStructureDefinition, Role
    from pysdmx.model.__utils import VTL_DTYPES_MAPPING, VTL_ROLE_MAPPING

    def to_vtl_json(
        dsd: DataStructureDefinition, path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Formats the DataStructureDefinition as a VTL DataStructure."""

        dataset_name = dsd.id
        components = []
        NAME = "name"
        ROLE = "role"
        TYPE = "type"
        NULLABLE = "nullable"

        _components: List[Component] = []
        _components.extend(dsd.components.dimensions)
        _components.extend(dsd.components.measures)
        _components.extend(dsd.components.attributes)

        for c in _components:
            _type = VTL_DTYPES_MAPPING[c.dtype]
            _nullability = c.role != Role.DIMENSION
            _role = VTL_ROLE_MAPPING[c.role]

            component = {
                NAME: c.id,
                ROLE: _role,
                TYPE: _type,
                NULLABLE: _nullability,
            }

            components.append(component)

        result = {
            "datasets": [{"name": dataset_name, "DataStructure": components}]
        }
        if path is not None:
            with open(path, "w") as fp:
                json.dump(result, fp)
            return None

        return result

    vtl_data_structure_1 = to_vtl_json(data_structure_1)
    vtl_data_structure_2 = to_vtl_json(data_structure_2)

Preparing the Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~

To create the datapoint, a dictionary containing the required data and
structures must first be prepared. The arguments `data_structures` and
`datapoints` support the following types:

- `Dict[str, Any]`
- `Path`
- `List[Union[Dict[str, Any], Path]]`

The example below uses dictionaries for simplicity:

.. code-block:: python

    vtl_data_structures = {
        "DS_1": vtl_data_structure_1,
        "DS_2": vtl_data_structure_2,
    }

    datapoints = {
        "DS_1": data_1,
        "DS_2": data_2,
    }

Defining the Expression and Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, define the expression to be executed and utilize the ``run``
method of ``vtlengine`` to perform the operation. The following example
demonstrates the addition of the datapoints `DS_1` and `DS_2`, with the
result assigned to a new datapoint `DS_r`:

For reference please check
`vtlengine run documentation <https://docs.vtlengine.meaningfuldata.eu/api.html#vtlengine.run>`_

.. code-block:: python

    import vtlengine

    expression = "DS_r <- DS_1 + DS_2;"

    run_result = run(
        script=expression,
        data_structures=vtl_data_structures,
        datapoints=datapoints,
        return_only_persistent=True,
    )
