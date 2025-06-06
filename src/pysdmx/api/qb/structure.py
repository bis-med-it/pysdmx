"""Build SDMX-REST structure queries."""

from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Union

import msgspec

from pysdmx.api.qb.util import (
    REST_ALL,
    REST_LATEST,
    ApiVersion,
    CoreQuery,
    check_multiple_items,
)
from pysdmx.errors import Invalid
from pysdmx.io.format import StructureFormat
from pysdmx.model import ItemReference, Reference
from pysdmx.util import parse_urn


class StructureDetail(Enum):
    """The desired amount of information to be returned."""

    FULL = "full"
    ALL_STUBS = "allstubs"
    REFERENCE_STUBS = "referencestubs"
    ALL_COMPLETE_STUBS = "allcompletestubs"
    REFERENCE_COMPLETE_STUBS = "referencecompletestubs"
    REFERENCE_PARTIAL = "referencepartial"
    RAW = "raw"


class StructureReference(Enum):
    """Which additional artefacts to include in the response."""

    NONE = "none"
    PARENTS = "parents"
    PARENTSANDSIBLINGS = "parentsandsiblings"
    ANCESTORS = "ancestors"
    CHILDREN = "children"
    DESCENDANTS = "descendants"
    ALL = "all"
    DATA_STRUCTURE = "datastructure"
    METADATA_STRUCTURE = "metadatastructure"
    CATEGORY_SCHEME = "categoryscheme"
    CONCEPT_SCHEME = "conceptscheme"
    CODELIST = "codelist"
    HIERARCHICAL_CODELIST = "hierarchicalcodelist"
    ORGANISATION_SCHEME = "organisationscheme"
    AGENCY_SCHEME = "agencyscheme"
    DATA_PROVIDER_SCHEME = "dataproviderscheme"
    DATA_CONSUMER_SCHEME = "dataconsumerscheme"
    ORGANISATION_UNIT_SCHEME = "organisationunitscheme"
    DATAFLOW = "dataflow"
    METADATAFLOW = "metadataflow"
    REPORTING_TAXONOMY = "reportingtaxonomy"
    PROVISION_AGREEMENT = "provisionagreement"
    STRUCTURE_SET = "structureset"
    PROCESS = "process"
    CATEGORISATION = "categorisation"
    CONTENT_CONSTRAINT = "contentconstraint"
    ATTACHMENT_CONSTRAINT = "attachmentconstraint"
    ACTUAL_CONSTRAINT = "actualconstraint"
    ALLOWED_CONSTRAINT = "allowedconstraint"
    TRANSFORMATION_SCHEME = "transformationscheme"
    RULESET_SCHEME = "rulesetscheme"
    USER_DEFINED_OPERATOR_SCHEME = "userdefinedoperatorscheme"
    CUSTOM_TYPE_SCHEME = "customtypescheme"
    NAME_PERSONALISATION_SCHEME = "namepersonalisationscheme"
    NAME_ALIAS_SCHEME = "namealiasscheme"
    DATA_CONSTRAINT = "dataconstraint"
    METADATA_CONSTRAINT = "metadataconstraint"
    HIERARCHY = "hierarchy"
    HIERARCHY_ASSOCIATION = "hierarchyassociation"
    VTL_MAPPING_SCHEME = "vtlmappingscheme"
    VALUE_LIST = "valuelist"
    STRUCTURE_MAP = "structuremap"
    REPRESENTATION_MAP = "representationmap"
    CONCEPT_SCHEME_MAP = "conceptschememap"
    CATEGORY_SCHEME_MAP = "categoryschememap"
    ORGANISATION_SCHEME_MAP = "organisationschememap"
    REPORTING_TAXONOMY_MAP = "reportingtaxonomymap"
    METADATA_PROVIDER_SCHEME = "metadataproviderscheme"
    METADATA_PROVISION_AGREEMENT = "metadataprovisionagreement"

    def is_artefact_type(self) -> bool:
        """Whether the references points to a type of artefacts."""
        core_refs = [
            "none",
            "parents",
            "parentsandsiblings",
            "ancestors",
            "children",
            "descendants",
            "all",
        ]
        return self.value not in core_refs


class StructureType(Enum):
    """The type of structural metadata to be returned."""

    DATA_STRUCTURE = "datastructure"
    METADATA_STRUCTURE = "metadatastructure"
    CATEGORY_SCHEME = "categoryscheme"
    CONCEPT_SCHEME = "conceptscheme"
    CODELIST = "codelist"
    HIERARCHICAL_CODELIST = "hierarchicalcodelist"
    ORGANISATION_SCHEME = "organisationscheme"
    AGENCY_SCHEME = "agencyscheme"
    DATA_PROVIDER_SCHEME = "dataproviderscheme"
    DATA_CONSUMER_SCHEME = "dataconsumerscheme"
    ORGANISATION_UNIT_SCHEME = "organisationunitscheme"
    DATAFLOW = "dataflow"
    METADATAFLOW = "metadataflow"
    REPORTING_TAXONOMY = "reportingtaxonomy"
    PROVISION_AGREEMENT = "provisionagreement"
    STRUCTURE_SET = "structureset"
    PROCESS = "process"
    CATEGORISATION = "categorisation"
    CONTENT_CONSTRAINT = "contentconstraint"
    ATTACHMENT_CONSTRAINT = "attachmentconstraint"
    ACTUAL_CONSTRAINT = "actualconstraint"
    ALLOWED_CONSTRAINT = "allowedconstraint"
    TRANSFORMATION_SCHEME = "transformationscheme"
    RULESET_SCHEME = "rulesetscheme"
    USER_DEFINED_OPERATOR_SCHEME = "userdefinedoperatorscheme"
    CUSTOM_TYPE_SCHEME = "customtypescheme"
    NAME_PERSONALISATION_SCHEME = "namepersonalisationscheme"
    NAME_ALIAS_SCHEME = "namealiasscheme"
    DATA_CONSTRAINT = "dataconstraint"
    METADATA_CONSTRAINT = "metadataconstraint"
    HIERARCHY = "hierarchy"
    HIERARCHY_ASSOCIATION = "hierarchyassociation"
    VTL_MAPPING_SCHEME = "vtlmappingscheme"
    VALUE_LIST = "valuelist"
    STRUCTURE_MAP = "structuremap"
    REPRESENTATION_MAP = "representationmap"
    CONCEPT_SCHEME_MAP = "conceptschememap"
    CATEGORY_SCHEME_MAP = "categoryschememap"
    ORGANISATION_SCHEME_MAP = "organisationschememap"
    REPORTING_TAXONOMY_MAP = "reportingtaxonomymap"
    METADATA_PROVIDER_SCHEME = "metadataproviderscheme"
    METADATA_PROVISION_AGREEMENT = "metadataprovisionagreement"
    ALL = REST_ALL

    @classmethod
    def from_type(
        cls, sdmx_type: str, is_item: bool = False
    ) -> "StructureType":
        """Create a StructureType from an sdmx type string."""
        sdmx_type = sdmx_type.lower()
        if sdmx_type == "code":
            return StructureType.CODELIST
        elif sdmx_type == "reportingcategory":
            return StructureType.REPORTING_TAXONOMY
        elif sdmx_type == "hierarchicalcode":
            return StructureType.HIERARCHY
        else:
            val = f"{sdmx_type}scheme" if is_item else sdmx_type
            try:
                return StructureType(val)
            except ValueError as ve:
                raise Invalid(
                    "Unknow type",
                    f"The supplied artefact type is unknown: {val}",
                ) from ve


ITEM_SCHEMES = {
    StructureType.CATEGORY_SCHEME,
    StructureType.CONCEPT_SCHEME,
    StructureType.CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.AGENCY_SCHEME,
    StructureType.DATA_PROVIDER_SCHEME,
    StructureType.METADATA_PROVIDER_SCHEME,
    StructureType.DATA_CONSUMER_SCHEME,
    StructureType.ORGANISATION_UNIT_SCHEME,
    StructureType.REPORTING_TAXONOMY,
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
    StructureType.VTL_MAPPING_SCHEME,
    StructureType.VALUE_LIST,
    StructureType.HIERARCHICAL_CODELIST,
}

_INITIAL_RESOURCES = {
    StructureType.DATA_STRUCTURE,
    StructureType.METADATA_STRUCTURE,
    StructureType.CATEGORY_SCHEME,
    StructureType.CONCEPT_SCHEME,
    StructureType.CODELIST,
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.AGENCY_SCHEME,
    StructureType.DATA_PROVIDER_SCHEME,
    StructureType.DATA_CONSUMER_SCHEME,
    StructureType.ORGANISATION_UNIT_SCHEME,
    StructureType.DATAFLOW,
    StructureType.METADATAFLOW,
    StructureType.REPORTING_TAXONOMY,
    StructureType.PROVISION_AGREEMENT,
    StructureType.STRUCTURE_SET,
    StructureType.PROCESS,
    StructureType.CATEGORISATION,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.ALL,
}

_V1_3_RESOURCES = {
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
}.union(_INITIAL_RESOURCES)

_V1_5_RESOURCES = {
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
}.union(_V1_3_RESOURCES)

_V2_0_DEPRECATED = {
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.STRUCTURE_SET,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
    StructureType.NAME_ALIAS_SCHEME,
}

_V2_0_ADDED = {
    StructureType.DATA_CONSTRAINT,
    StructureType.METADATA_CONSTRAINT,
    StructureType.HIERARCHY,
    StructureType.HIERARCHY_ASSOCIATION,
    StructureType.VTL_MAPPING_SCHEME,
    StructureType.VALUE_LIST,
    StructureType.STRUCTURE_MAP,
    StructureType.REPRESENTATION_MAP,
    StructureType.CONCEPT_SCHEME_MAP,
    StructureType.CATEGORY_SCHEME_MAP,
    StructureType.ORGANISATION_SCHEME_MAP,
    StructureType.REPORTING_TAXONOMY_MAP,
    StructureType.METADATA_PROVIDER_SCHEME,
    StructureType.METADATA_PROVISION_AGREEMENT,
}

_V2_0_RESOURCES = (_V1_5_RESOURCES.difference(_V2_0_DEPRECATED)).union(
    _V2_0_ADDED
)

_API_RESOURCES = {
    "V1.0.0": _INITIAL_RESOURCES,
    "V1.0.1": _INITIAL_RESOURCES,
    "V1.0.2": _INITIAL_RESOURCES,
    "V1.1.0": _INITIAL_RESOURCES,
    "V1.2.0": _INITIAL_RESOURCES,
    "V1.3.0": _V1_3_RESOURCES,
    "V1.4.0": _V1_3_RESOURCES,
    "V1.5.0": _V1_5_RESOURCES,
    "V2.0.0": _V2_0_RESOURCES,
    "V2.1.0": _V2_0_RESOURCES,
    "V2.2.0": _V2_0_RESOURCES,
    "V2.2.1": _V2_0_RESOURCES,
    "LATEST": _V2_0_RESOURCES,
}


class StructureQuery(CoreQuery, frozen=True, omit_defaults=True):
    """A query for structural metadata.

    Attributes:
        artefact_type: The type of structural metadata to be returned.
        agency_id: The agency (or agencies) maintaining the artefact(s)
            to be returned.
        resource_id: The id(s) of the artefact(s) to be returned.
        version: The version(s) of the artefact(s) to be returned.
        item_id: The id(s) of the item(s) to be returned.
        detail: The desired amount of information to be returned.
        references: The additional artefact(s) to include in the response.
        as_of: Retrieve the artefact as it was at the specified point
            in time (aka time travel).
    """

    artefact_type: StructureType = StructureType.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    item_id: Union[str, Sequence[str]] = REST_ALL
    detail: StructureDetail = StructureDetail.FULL
    references: StructureReference = StructureReference.NONE
    as_of: Optional[datetime] = None

    @staticmethod
    def from_ref(
        ref: Union[ItemReference, Reference, str],
    ) -> "StructureQuery":
        """Create a StructureQuery out of the supplied reference.

        Args:
            ref: Either a reference object (Reference for maintainable
                artefacts, or ItemReference for items), or an SDMX urn.

        Returns:
            A StructureQuery to retrieve the supplied reference.

        Raises:
            Invalid: If reference is a string and it is not an SDMX urn,
                or if the type cannot be translated into a StructureType.
        """
        if isinstance(ref, str):
            ref = parse_urn(ref)
        item = ref.item_id if isinstance(ref, ItemReference) else REST_ALL
        atype = StructureType.from_type(
            ref.sdmx_type, isinstance(ref, ItemReference)
        )
        return StructureQuery(atype, ref.agency, ref.id, ref.version, item)

    def _validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__check_multiple_items(version)
        self.__check_artefact_type(self.artefact_type, version)
        self.__check_item(version)
        self.__check_detail(version)
        self.__check_references(version)
        self.__check_as_of(version)

    def __check_multiple_items(self, version: ApiVersion) -> None:
        check_multiple_items(self.agency_id, version)
        check_multiple_items(self.resource_id, version)
        check_multiple_items(self.version, version)
        check_multiple_items(self.item_id, version)

    def __check_as_of(self, version: ApiVersion) -> None:
        if self.as_of and version < ApiVersion.V2_2_0:
            raise Invalid(
                "Validation Error",
                f"as_of not supported in {version.value}.",
            )

    def __check_artefact_type(
        self, atyp: StructureType, version: ApiVersion
    ) -> None:
        if atyp not in _API_RESOURCES[version.name.replace("_", ".")]:
            raise Invalid(
                "Validation Error",
                f"{atyp} is not valid for SDMX-REST {version.name}.",
            )

    def __check_item(self, version: ApiVersion) -> None:
        if self.item_id != REST_ALL and version < ApiVersion.V1_1_0:
            raise Invalid(
                "Validation Error",
                f"Item query not supported in {version.value}.",
            )

    def __check_detail(self, version: ApiVersion) -> None:
        if (
            version < ApiVersion.V1_3_0
            and self.detail.value
            in [
                "referencepartial",
                "allcompletestubs",
                "referencecompletestubs",
            ]
        ) or (version < ApiVersion.V2_0_0 and self.detail.value == "raw"):
            raise Invalid(
                "Validation Error",
                f"{self.detail} not allowed in SDMX-REST {version.value}.",
            )

    def __check_references(self, version: ApiVersion) -> None:
        if self.references.is_artefact_type():
            rt = StructureType(self.references.value)
            self.__check_artefact_type(rt, version)
        elif (
            self.references == StructureReference.ANCESTORS
            and version < ApiVersion.V2_0_0
        ):
            raise Invalid(
                "Validation Error",
                f"{self.references} not allowed in SDMX-REST {version.value}.",
            )

    def __is_item_allowed(
        self, typ: StructureType, version: ApiVersion
    ) -> bool:
        if typ in ITEM_SCHEMES and version > ApiVersion.V1_0_2:
            return not (
                version == ApiVersion.V1_1_0
                and typ == StructureType.HIERARCHICAL_CODELIST
            )
        else:
            return False

    def __to_type_kw(self, val: StructureType, ver: ApiVersion) -> str:
        if val == StructureType.ALL and ver < ApiVersion.V2_0_0:
            out = "structure"
        else:
            out = val.value
        return out

    def __to_kws(
        self, vals: Union[str, Sequence[str]], ver: ApiVersion
    ) -> str:
        vals = [vals] if isinstance(vals, str) else vals
        mapped = [self._to_kw(v, ver) for v in vals]
        sep = "+" if ver < ApiVersion.V2_0_0 else ","
        return sep.join(mapped)

    def _create_full_query(self, ver: ApiVersion) -> str:
        u = "/"
        u += "structure/" if ver >= ApiVersion.V2_0_0 else ""
        t = self.__to_type_kw(self.artefact_type, ver)
        a = self.__to_kws(self.agency_id, ver)
        r = self.__to_kws(self.resource_id, ver)
        v = self.__to_kws(self.version, ver)
        i = self.__to_kws(self.item_id, ver)
        u += f"{t}/{a}/{r}/{v}"
        ck = [self.__is_item_allowed(self.artefact_type, ver)]
        u += f"/{i}" if all(ck) else ""
        u += f"?detail={self.detail.value}&references={self.references.value}"
        if self.as_of:
            u += f'&asOf={self.as_of.isoformat("T", "seconds")}'
        return u

    def _create_short_query(self, ver: ApiVersion) -> str:
        u = "/structure" if ver >= ApiVersion.V2_0_0 else ""
        t = self.__to_type_kw(self.artefact_type, ver)
        a = self.__to_kws(self.agency_id, ver)
        r = self.__to_kws(self.resource_id, ver)
        v = self.__to_kws(self.version, ver)
        i = self.__to_kws(self.item_id, ver)

        ck = self.__is_item_allowed(self.artefact_type, ver)
        iu = f"/{i}" if ck and self.item_id != REST_ALL else ""
        vu = f"/{v}{iu}" if iu or self.version != REST_LATEST else ""
        ru = f"/{r}{vu}" if vu or self.resource_id != REST_ALL else ""
        au = f"/{a}{ru}" if ru or self.agency_id != REST_ALL else ""

        if ver >= ApiVersion.V2_0_0:
            tu = (
                f"/{t}{au}"
                if au or self.artefact_type != StructureType.ALL
                else ""
            )
        else:
            tu = f"/{t}{au}"
        u += f"{tu}"
        u += (
            "?"
            if self.detail != StructureDetail.FULL
            or self.references != StructureReference.NONE
            or self.as_of
            else ""
        )
        u += (
            f"detail={self.detail.value}"
            if self.detail != StructureDetail.FULL
            else ""
        )
        u += (
            "&"
            if self.detail != StructureDetail.FULL
            and self.references != StructureReference.NONE
            else ""
        )
        u += (
            f"references={self.references.value}"
            if self.references != StructureReference.NONE
            else ""
        )
        u += (
            "&"
            if self.as_of
            and (
                self.detail != StructureDetail.FULL
                or self.references != StructureReference.NONE
            )
            else ""
        )
        u += (
            f'asOf={self.as_of.isoformat("T", "seconds")}'
            if self.as_of
            else ""
        )
        return u

    def _get_decoder(self) -> msgspec.json.Decoder:  # type: ignore[type-arg]
        return _decoder


_decoder = msgspec.json.Decoder(StructureQuery)


__all__ = [
    "ApiVersion",
    "StructureDetail",
    "StructureFormat",
    "StructureQuery",
    "StructureReference",
    "StructureType",
]
