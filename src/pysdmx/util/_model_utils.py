from pysdmx.errors import Invalid, NotFound
from pysdmx.model import Reference
from pysdmx.model.dataflow import Schema
from pysdmx.model.message import Message
from pysdmx.util import parse_urn


def schema_generator(message: Message, dataset_ref: Reference) -> Schema:
    """Generates a Schema by resolving the short_urn in the message."""
    context = dataset_ref.sdmx_type.lower()
    if context == "datastructure":
        try:
            dsd = message.get_data_structure_definition(str(dataset_ref))
        except NotFound:
            raise Invalid(
                f"Missing DataStructure {dataset_ref} in structures message.",
            ) from None
        return dsd.to_schema()
    elif context == "dataflow":
        try:
            dataflow = message.get_dataflow(str(dataset_ref))
        except NotFound:
            raise Invalid(
                f"Missing Dataflow {dataset_ref} in structures message.",
            ) from None
        if dataflow.structure is None:
            raise Invalid(
                f"Dataflow {dataset_ref} does not have a structure defined.",
            )
        dsd_ref = parse_urn(dataflow.structure)  # type: ignore[arg-type]
        try:
            dsd = message.get_data_structure_definition(str(dsd_ref))
        except NotFound:
            raise Invalid(
                f"Not found referenced DataStructure {dsd_ref}"
                f"from Dataflow {dataset_ref}. "
                f"Please send the structures message using "
                f"references=children to include the DataStructureDefinition.",
            ) from None
        return Schema(
            context=context,  # type: ignore[arg-type]
            id=dataset_ref.id,
            version=dataset_ref.version,
            agency=dataset_ref.agency,
            components=dsd.components,
            artefacts=dsd.to_schema().artefacts,
        )
    elif context == "provisionagreement":
        raise NotImplementedError(
            "ProvisionAgreement schema generation is not supported yet."
        )
    else:
        raise Invalid(
            f"Unknown context: {context}",
            f"The dataset can only reference a DataStructureDefinition, "
            f"a Dataflow or a Provision Agreement, "
            f"found {dataset_ref.sdmx_type}.",
        )
