from pysdmx.errors import Invalid, NotFound
from pysdmx.model import Reference
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
    Schema,
)
from pysdmx.model.message import Message
from pysdmx.util import parse_urn


def _resolve_dsd(
    dataflow: Dataflow,
    message: Message,
    dataset_ref: Reference,
    source: str,
) -> DataStructureDefinition:
    """Resolve the DSD from a Dataflow's structure reference."""
    if dataflow.structure is None:
        raise Invalid(
            f"Dataflow {dataset_ref} does not have a structure defined.",
        )
    if isinstance(dataflow.structure, DataStructureDefinition):
        return dataflow.structure
    dsd_ref = parse_urn(dataflow.structure)
    try:
        return message.get_data_structure_definition(str(dsd_ref))
    except NotFound:
        hint = ""
        if source == "Dataflow":
            hint = (
                " Please send the structures message using "
                "references=children to include the "
                "DataStructureDefinition."
            )
        raise Invalid(
            f"Not found referenced DataStructure {dsd_ref}"
            f" from {source} {dataset_ref}.{hint}",
        ) from None


def _build_schema(
    context: str,
    dataset_ref: Reference,
    dsd: DataStructureDefinition,
) -> Schema:
    """Build a Schema from a resolved DSD."""
    return Schema(
        context=context,  # type: ignore[arg-type]
        id=dataset_ref.id,
        version=dataset_ref.version,
        agency=dataset_ref.agency,
        groups=dsd.groups,
        components=dsd.components,
        artefacts=dsd.to_schema().artefacts,
    )


def schema_generator(
    message: Message,
    dataset_ref: Reference,
) -> Schema:
    """Generates a Schema by resolving the short_urn in the message."""
    context = dataset_ref.sdmx_type.lower()
    if context == "datastructure":
        try:
            dsd = message.get_data_structure_definition(str(dataset_ref))
        except NotFound:
            raise Invalid(
                f"Missing DataStructure {dataset_ref} "
                f"in structures message.",
            ) from None
        return dsd.to_schema()
    elif context == "dataflow":
        try:
            dataflow = message.get_dataflow(str(dataset_ref))
        except NotFound:
            raise Invalid(
                f"Missing Dataflow {dataset_ref} in structures message.",
            ) from None
        dsd = _resolve_dsd(dataflow, message, dataset_ref, "Dataflow")
        return _build_schema(context, dataset_ref, dsd)
    elif context == "provisionagreement":
        try:
            prov_agree = message.get_provision_agreement(
                str(dataset_ref),
            )
        except NotFound:
            raise Invalid(
                f"Missing Provision Agreement {dataset_ref} "
                f"in structures message.",
            ) from None
        if prov_agree.dataflow is None:
            raise Invalid(
                f"Provision Agreement {dataset_ref} does not have a "
                f"Dataflow defined.",
            )
        dfw_ref = parse_urn(prov_agree.dataflow)
        try:
            dataflow = message.get_dataflow(str(dfw_ref))
        except NotFound:
            raise Invalid(
                f"Missing Dataflow in {dataset_ref} "
                f"structures message.",
            ) from None
        dsd = _resolve_dsd(
            dataflow, message, dataset_ref, "Provision Agreement"
        )
        return _build_schema(context, dataset_ref, dsd)
    else:
        raise Invalid(
            f"Unknown context: {context}",
            f"The dataset can only reference a DataStructureDefinition, "
            f"a Dataflow or a Provision Agreement, "
            f"found {dataset_ref.sdmx_type}.",
        )
