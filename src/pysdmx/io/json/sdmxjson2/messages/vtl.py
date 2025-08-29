"""Collection of SDMX-JSON schemas for VTL artefacts."""

from typing import Literal, Optional, Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
    NameableType,
)
from pysdmx.model.__base import Agency, DataflowRef
from pysdmx.model.vtl import (
    CustomType,
    CustomTypeScheme,
    FromVtlMapping,
    NamePersonalisation,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    ToVtlMapping,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMapping,
    VtlMappingScheme,
)
from pysdmx.util import parse_urn


class JsonCustomType(NameableType, frozen=True):
    """SDMX-JSON payload for custom types."""

    vtlScalarType: str = ""
    dataType: str = ""
    vtlLiteralFormat: Optional[str] = None
    outputFormat: Optional[str] = None
    nullValue: Optional[str] = None

    def to_model(self) -> CustomType:
        """Converts deserialized class to pysdmx model class."""
        return CustomType(
            id=self.id,
            name=self.name,
            description=self.description,
            data_type=self.dataType,
            null_value=self.nullValue,
            output_format=self.outputFormat,
            vtl_literal_format=self.vtlLiteralFormat,
            vtl_scalar_type=self.vtlScalarType,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(self, ct: CustomType) -> "JsonCustomType":
        """Converts a pysdmx custom type to an SDMX-JSON one."""
        if not ct.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON custom types must have a name",
                {"custom_type": ct.id},
            )
        return JsonCustomType(
            id=ct.id,
            name=ct.name,
            description=ct.description,
            annotations=[JsonAnnotation.from_model(a) for a in ct.annotations],
            vtlScalarType=ct.vtl_scalar_type,
            dataType=ct.data_type,
            vtlLiteralFormat=ct.vtl_literal_format,
            outputFormat=ct.output_format,
            nullValue=ct.null_value,
        )


class JsonCustomTypeScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for custom type schemes."""

    vtlVersion: str = ""
    customTypes: Sequence[JsonCustomType] = ()

    def to_model(self) -> CustomTypeScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.customTypes]
        return CustomTypeScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(self, cts: CustomTypeScheme) -> "JsonCustomTypeScheme":
        """Converts a pysdmx custom type scheme to an SDMX-JSON one."""
        if not cts.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON custom type schemes must have a name",
                {"custom_type_scheme": cts.id},
            )
        return JsonCustomTypeScheme(
            agency=(
                cts.agency.id if isinstance(cts.agency, Agency) else cts.agency
            ),
            id=cts.id,
            name=cts.name,
            version=cts.version,
            isExternalReference=cts.is_external_reference,
            validFrom=cts.valid_from,
            validTo=cts.valid_to,
            description=cts.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in cts.annotations
            ],
            isPartial=cts.is_partial,
            vtlVersion=cts.vtl_version,  # type: ignore[arg-type]
            customTypes=[JsonCustomType.from_model(i) for i in cts.items],
        )


class JsonNamePersonalisation(NameableType, frozen=True):
    """SDMX-JSON payload for name personalisations."""

    vtlDefaultName: str = ""
    personalisedName: str = ""
    vtlArtefact: str = ""

    def to_model(self) -> NamePersonalisation:
        """Converts deserialized class to pysdmx model class."""
        return NamePersonalisation(
            self.id,
            name=self.name,
            description=self.description,
            vtl_default_name=self.vtlDefaultName,
            personalised_name=self.personalisedName,
            vtl_artefact=self.vtlArtefact,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(cls, np: NamePersonalisation) -> "JsonNamePersonalisation":
        """Converts a pysdmx name personalisation to an SDMX-JSON one."""
        if not np.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON name personalisations must have a name",
                {"name_personalisation": np.id},
            )
        return JsonNamePersonalisation(
            id=np.id,
            name=np.name,
            description=np.description,
            annotations=[JsonAnnotation.from_model(a) for a in np.annotations],
            vtlDefaultName=np.vtl_default_name,
            personalisedName=np.personalised_name,
            vtlArtefact=np.vtl_artefact,
        )


class JsonNamePersonalisationScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for name personalisation schemes."""

    vtlVersion: str = ""
    namePersonalisations: Sequence[JsonNamePersonalisation] = ()

    def to_model(self) -> NamePersonalisationScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.namePersonalisations]
        return NamePersonalisationScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(
        cls, nps: NamePersonalisationScheme
    ) -> "JsonNamePersonalisationScheme":
        """Converts a pysdmx name personalisation scheme to an SDMX-JSON one."""
        if not nps.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON name personalisation schemes must have a name",
                {"name_personalisation_scheme": nps.id},
            )
        return JsonNamePersonalisationScheme(
            agency=(
                nps.agency.id if isinstance(nps.agency, Agency) else nps.agency
            ),
            id=nps.id,
            name=nps.name,
            version=nps.version,
            isExternalReference=nps.is_external_reference,
            validFrom=nps.valid_from,
            validTo=nps.valid_to,
            description=nps.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in nps.annotations
            ],
            isPartial=nps.is_partial,
            vtlVersion=nps.vtl_version,  # type: ignore[arg-type]
            namePersonalisations=[
                JsonNamePersonalisation.from_model(i) for i in nps.items
            ],
        )


class JsonUserDefinedOperator(NameableType, frozen=True):
    """SDMX-JSON payload for user defined operator."""

    operatorDefinition: str = ""

    def to_model(self) -> UserDefinedOperator:
        """Converts deserialized class to pysdmx model class."""
        return UserDefinedOperator(
            self.id,
            name=self.name,
            description=self.description,
            operator_definition=self.operatorDefinition,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(cls, udo: UserDefinedOperator) -> "JsonUserDefinedOperator":
        """Converts a pysdmx user defined operator to an SDMX-JSON one."""
        if not udo.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON user defined operators must have a name",
                {"user_defined_operator": udo.id},
            )
        return JsonUserDefinedOperator(
            id=udo.id,
            name=udo.name,
            description=udo.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in udo.annotations
            ],
            operatorDefinition=udo.operator_definition,
        )


class JsonUserDefinedOperatorScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for user defined operator schemes."""

    vtlVersion: str = ""
    userDefinedOperators: Sequence[JsonUserDefinedOperator] = ()
    vtlMappingScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()

    def to_model(self) -> UserDefinedOperatorScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.userDefinedOperators]
        return UserDefinedOperatorScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=self.vtlMappingScheme,
            ruleset_schemes=self.rulesetSchemes,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(
        cls, udos: UserDefinedOperatorScheme
    ) -> "JsonUserDefinedOperatorScheme":
        """Converts a pysdmx user defined operator scheme to SDMX-JSON."""
        if not udos.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON user defined operator schemes must have a name",
                {"user_defined_operator_scheme": udos.id},
            )

        # Convert vtl_mapping_scheme to URN string
        vtl_mapping_ref = None
        if udos.vtl_mapping_scheme:
            if isinstance(udos.vtl_mapping_scheme, str):
                vtl_mapping_ref = udos.vtl_mapping_scheme
            else:
                # Handle both VtlMappingScheme objects and References
                agency = (
                    udos.vtl_mapping_scheme.agency.id
                    if hasattr(udos.vtl_mapping_scheme.agency, "id")
                    else udos.vtl_mapping_scheme.agency
                )
                vtl_mapping_ref = (
                    f"urn:sdmx:org.sdmx.infomodel.transformation.VtlMappingScheme="
                    f"{agency}:{udos.vtl_mapping_scheme.id}"
                    f"({udos.vtl_mapping_scheme.version})"
                )

        return JsonUserDefinedOperatorScheme(
            agency=(
                udos.agency.id
                if isinstance(udos.agency, Agency)
                else udos.agency
            ),
            id=udos.id,
            name=udos.name,
            version=udos.version,
            isExternalReference=udos.is_external_reference,
            validFrom=udos.valid_from,
            validTo=udos.valid_to,
            description=udos.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in udos.annotations
            ],
            isPartial=udos.is_partial,
            vtlVersion=udos.vtl_version,  # type: ignore[arg-type]
            vtlMappingScheme=vtl_mapping_ref,
            rulesetSchemes=udos.ruleset_schemes,
            userDefinedOperators=[
                JsonUserDefinedOperator.from_model(i) for i in udos.items
            ],
        )


class JsonRuleset(Struct, frozen=True):
    """SDMX-JSON payload for rulesets."""

    id: str
    name: str
    rulesetDefinition: str
    rulesetType: Literal["datapoint", "hierarchical"]
    rulesetScope: Literal["variable", "valuedomain"]
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()

    def to_model(self) -> Ruleset:
        """Converts deserialized class to pysdmx model class."""
        return Ruleset(
            id=self.id,
            name=self.name,
            description=self.description,
            ruleset_definition=self.rulesetDefinition,
            ruleset_type=self.rulesetType,
            ruleset_scope=self.rulesetScope,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(cls, ruleset: Ruleset) -> "JsonRuleset":
        """Converts a pysdmx ruleset to an SDMX-JSON one."""
        if not ruleset.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON rulesets must have a name",
                {"ruleset": ruleset.id},
            )
        return JsonRuleset(
            id=ruleset.id,
            name=ruleset.name,
            description=ruleset.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in ruleset.annotations
            ],
            rulesetDefinition=ruleset.ruleset_definition,
            rulesetType=ruleset.ruleset_type,
            rulesetScope=ruleset.ruleset_scope,
        )


class JsonRulesetScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for ruleset schemes."""

    vtlVersion: str = ""
    rulesets: Sequence[JsonRuleset] = ()
    vtlMappingScheme: Optional[str] = None

    def to_model(self) -> RulesetScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.rulesets]
        return RulesetScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=self.vtlMappingScheme,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(cls, rss: RulesetScheme) -> "JsonRulesetScheme":
        """Converts a pysdmx ruleset scheme to an SDMX-JSON one."""
        if not rss.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON ruleset schemes must have a name",
                {"ruleset_scheme": rss.id},
            )
        return JsonRulesetScheme(
            agency=(
                rss.agency.id if isinstance(rss.agency, Agency) else rss.agency
            ),
            id=rss.id,
            name=rss.name,
            version=rss.version,
            isExternalReference=rss.is_external_reference,
            validFrom=rss.valid_from,
            validTo=rss.valid_to,
            description=rss.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in rss.annotations
            ],
            isPartial=rss.is_partial,
            vtlVersion=rss.vtl_version,  # type: ignore[arg-type]
            vtlMappingScheme=rss.vtl_mapping_scheme,
            rulesets=[JsonRuleset.from_model(i) for i in rss.items],
        )


class JsonToVtlMapping(Struct, frozen=True):
    """SDMX-JSON payload for To VTL mappings."""

    toVtlSubSpace: Sequence[str]
    type: Optional[str] = None

    def to_model(self) -> ToVtlMapping:
        """Converts deserialized class to pysdmx model class."""
        return ToVtlMapping(self.toVtlSubSpace, self.type)

    @classmethod
    def from_model(cls, mapping: ToVtlMapping) -> "JsonToVtlMapping":
        """Converts a pysdmx "to VTL" mapping to an SDMX-JSON one."""
        return JsonToVtlMapping(mapping.to_vtl_sub_space, mapping.method)


class JsonFromVtlMapping(Struct, frozen=True):
    """SDMX-JSON payload for from VTL mappings."""

    fromVtlSuperSpace: Sequence[str]
    type: Optional[str] = None

    def to_model(self) -> FromVtlMapping:
        """Converts deserialized class to pysdmx model class."""
        return FromVtlMapping(self.fromVtlSuperSpace, self.type)

    @classmethod
    def from_model(cls, mapping: FromVtlMapping) -> "JsonFromVtlMapping":
        """Converts a pysdmx "from VTL" mapping to an SDMX-JSON one."""
        return JsonFromVtlMapping(mapping.from_vtl_sub_space, mapping.method)


class JsonVtlMapping(NameableType, frozen=True):
    """SDMX-JSON payload for VTL mappings."""

    alias: str = ""
    concept: Optional[str] = None
    codelist: Optional[str] = None
    dataflow: Optional[str] = None
    genericDataflow: Optional[str] = None
    toVtlMapping: Optional[JsonToVtlMapping] = None
    fromVtlMapping: Optional[JsonFromVtlMapping] = None

    def to_model(self) -> VtlMapping:
        """Converts deserialized class to pysdmx model class."""
        if self.codelist:
            return VtlCodelistMapping(
                self.id,
                name=self.name,
                description=self.description,
                codelist=self.codelist,
                codelist_alias=self.alias,
            )
        elif self.concept:
            return VtlConceptMapping(
                self.id,
                name=self.name,
                description=self.description,
                concept=self.concept,
                concept_alias=self.alias,
            )
        else:
            reference = (
                parse_urn(self.dataflow)
                if self.dataflow
                else parse_urn(self.genericDataflow)  # type: ignore[arg-type]
            )
            dataflow = DataflowRef(
                id=reference.id,
                agency=reference.agency,
                version=reference.version,
            )
            return VtlDataflowMapping(
                self.id,
                name=self.name,
                description=self.description,
                dataflow=dataflow,
                dataflow_alias=self.alias,
                from_vtl_mapping_method=(
                    self.fromVtlMapping.to_model()
                    if self.fromVtlMapping
                    else None
                ),
                to_vtl_mapping_method=(
                    self.toVtlMapping.to_model() if self.toVtlMapping else None
                ),
                annotations=[a.to_model() for a in self.annotations],
            )

    @classmethod
    def from_model(cls, mapping: VtlMapping) -> "JsonVtlMapping":
        """Converts a pysdmx VTL mapping to an SDMX-JSON one."""
        if not mapping.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON VTL mappings must have a name",
                {"vtl_mapping": mapping.id},
            )

        if isinstance(mapping, VtlCodelistMapping):
            return JsonVtlMapping(
                id=mapping.id,
                name=mapping.name,
                description=mapping.description,
                annotations=[
                    JsonAnnotation.from_model(a) for a in mapping.annotations
                ],
                alias=mapping.codelist_alias,
                codelist=mapping.codelist,
            )
        elif isinstance(mapping, VtlConceptMapping):
            return JsonVtlMapping(
                id=mapping.id,
                name=mapping.name,
                description=mapping.description,
                annotations=[
                    JsonAnnotation.from_model(a) for a in mapping.annotations
                ],
                alias=mapping.concept_alias,
                concept=mapping.concept,
            )
        elif isinstance(mapping, VtlDataflowMapping):
            return JsonVtlMapping(
                id=mapping.id,
                name=mapping.name,
                description=mapping.description,
                annotations=[
                    JsonAnnotation.from_model(a) for a in mapping.annotations
                ],
                alias=mapping.dataflow_alias,
                dataflow=f"urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow={mapping.dataflow.agency}:{mapping.dataflow.id}({mapping.dataflow.version})",
                toVtlMapping=(
                    JsonToVtlMapping.from_model(mapping.to_vtl_mapping_method)
                    if mapping.to_vtl_mapping_method
                    else None
                ),
                fromVtlMapping=(
                    JsonFromVtlMapping.from_model(
                        mapping.from_vtl_mapping_method
                    )
                    if mapping.from_vtl_mapping_method
                    else None
                ),
            )
        else:
            raise errors.Invalid(
                "Invalid input",
                f"Unsupported VTL mapping type: {type(mapping)}",
                {"vtl_mapping": mapping.id},
            )


class JsonVtlMappingScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for VTL mapping schemes."""

    vtlMappings: Sequence[JsonVtlMapping] = ()
    vtlMappingScheme: Optional[str] = None

    def to_model(self) -> VtlMappingScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.vtlMappings]
        return VtlMappingScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(cls, vms: VtlMappingScheme) -> "JsonVtlMappingScheme":
        """Converts a pysdmx VTL mapping scheme to an SDMX-JSON one."""
        if not vms.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON VTL mapping schemes must have a name",
                {"vtl_mapping_scheme": vms.id},
            )
        return JsonVtlMappingScheme(
            agency=(
                vms.agency.id if isinstance(vms.agency, Agency) else vms.agency
            ),
            id=vms.id,
            name=vms.name,
            version=vms.version,
            isExternalReference=vms.is_external_reference,
            validFrom=vms.valid_from,
            validTo=vms.valid_to,
            description=vms.description,
            annotations=[
                JsonAnnotation.from_model(a) for a in vms.annotations
            ],
            isPartial=vms.is_partial,
            vtlMappings=[JsonVtlMapping.from_model(i) for i in vms.items],
        )


class JsonTransformation(Struct, frozen=True):
    """SDMX-JSON payload for VTL transformations."""

    id: str
    name: str
    expression: str
    result: str
    isPersistent: bool
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()

    def to_model(self) -> Transformation:
        """Converts deserialized class to pysdmx model class."""
        return Transformation(
            self.id,
            name=self.name,
            description=self.description,
            expression=self.expression,
            is_persistent=self.isPersistent,
            result=self.result,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(
        cls, transformation: Transformation
    ) -> "JsonTransformation":
        """Converts a pysdmx transformation to an SDMX-JSON one."""
        if not transformation.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON transformations must have a name",
                {"transformation": transformation.id},
            )
        return JsonTransformation(
            id=transformation.id,
            name=transformation.name,
            expression=transformation.expression,
            result=transformation.result,
            isPersistent=transformation.is_persistent,
            description=transformation.description,
            annotations=[
                JsonAnnotation.from_model(a)
                for a in transformation.annotations
            ],
        )


class JsonTransformationScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for VTL transformation schemes."""

    vtlVersion: str = ""
    transformations: Sequence[JsonTransformation] = ()
    vtlMappingScheme: Optional[str] = None
    namePersonalisationScheme: Optional[str] = None
    customTypeScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()
    userDefinedOperatorSchemes: Sequence[str] = ()

    def to_model(
        self,
        custom_type_schemes: Sequence[JsonCustomTypeScheme],
        vtl_mapping_schemes: Sequence[JsonVtlMappingScheme],
        name_personalisation_schemes: Sequence[JsonNamePersonalisationScheme],
        ruleset_schemes: Sequence[JsonRulesetScheme],
        user_defined_operator_schemes: Sequence[JsonUserDefinedOperatorScheme],
    ) -> TransformationScheme:
        """Converts deserialized class to pysdmx model class."""
        cts = [i.to_model() for i in custom_type_schemes]
        vms = [i.to_model() for i in vtl_mapping_schemes]
        nps = [i.to_model() for i in name_personalisation_schemes]
        rss = [i.to_model() for i in ruleset_schemes]
        dos = [i.to_model() for i in user_defined_operator_schemes]
        items = [i.to_model() for i in self.transformations]
        return TransformationScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=vms[0] if vms else None,
            custom_type_scheme=cts[0] if cts else None,
            name_personalisation_scheme=nps[0] if nps else None,
            ruleset_schemes=rss,
            user_defined_operator_schemes=dos,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(
        cls, ts: TransformationScheme
    ) -> "JsonTransformationScheme":
        """Converts a pysdmx transformation scheme to an SDMX-JSON one."""
        if not ts.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON transformation schemes must have a name",
                {"transformation_scheme": ts.id},
            )

        # Convert scheme references to strings
        mapping_ref = None
        if ts.vtl_mapping_scheme:
            mapping_ref = (
                f"urn:sdmx:org.sdmx.infomodel.vtl.VtlMappingScheme="
                f"{ts.vtl_mapping_scheme.agency}:{ts.vtl_mapping_scheme.id}"
                f"({ts.vtl_mapping_scheme.version})"
            )

        np_ref = None
        if ts.name_personalisation_scheme:
            np_ref = (
                f"urn:sdmx:org.sdmx.infomodel.vtl.NamePersonalisationScheme="
                f"{ts.name_personalisation_scheme.agency}:"
                f"{ts.name_personalisation_scheme.id}"
                f"({ts.name_personalisation_scheme.version})"
            )

        ct_ref = None
        if ts.custom_type_scheme:
            ct_ref = (
                f"urn:sdmx:org.sdmx.infomodel.vtl.CustomTypeScheme="
                f"{ts.custom_type_scheme.agency}:{ts.custom_type_scheme.id}"
                f"({ts.custom_type_scheme.version})"
            )

        rs_refs = [
            f"urn:sdmx:org.sdmx.infomodel.vtl.RulesetScheme="
            f"{rs.agency}:{rs.id}({rs.version})"
            for rs in ts.ruleset_schemes
        ]

        udo_refs = [
            f"urn:sdmx:org.sdmx.infomodel.vtl.UserDefinedOperatorScheme="
            f"{udos.agency}:{udos.id}({udos.version})"
            for udos in ts.user_defined_operator_schemes
        ]

        return JsonTransformationScheme(
            agency=(
                ts.agency.id if isinstance(ts.agency, Agency) else ts.agency
            ),
            id=ts.id,
            name=ts.name,
            version=ts.version,
            isExternalReference=ts.is_external_reference,
            validFrom=ts.valid_from,
            validTo=ts.valid_to,
            description=ts.description,
            annotations=[JsonAnnotation.from_model(a) for a in ts.annotations],
            isPartial=ts.is_partial,
            vtlVersion=ts.vtl_version,  # type: ignore[arg-type]
            vtlMappingScheme=mapping_ref,
            namePersonalisationScheme=np_ref,
            customTypeScheme=ct_ref,
            rulesetSchemes=rs_refs,
            userDefinedOperatorSchemes=udo_refs,
            transformations=[
                JsonTransformation.from_model(i) for i in ts.items
            ],
        )


class JsonVtlTransformations(Struct, frozen=True):
    """SDMX-JSON payload for VTL transformation schemes."""

    transformationSchemes: Sequence[JsonTransformationScheme]
    customTypeSchemes: Sequence[JsonCustomTypeScheme] = ()
    vtlMappingSchemes: Sequence[JsonVtlMappingScheme] = ()
    namePersonalisationSchemes: Sequence[JsonNamePersonalisationScheme] = ()
    rulesetSchemes: Sequence[JsonRulesetScheme] = ()
    userDefinedOperatorSchemes: Sequence[JsonUserDefinedOperatorScheme] = ()

    def to_model(self) -> TransformationScheme:
        """Converts deserialized class to pysdmx model class."""
        return self.transformationSchemes[0].to_model(
            self.customTypeSchemes,
            self.vtlMappingSchemes,
            self.namePersonalisationSchemes,
            self.rulesetSchemes,
            self.userDefinedOperatorSchemes,
        )


class JsonVtlTransformationsMessage(Struct, frozen=True):
    """SDMX-JSON payload for /transformationscheme queries."""

    data: JsonVtlTransformations

    def to_model(self) -> TransformationScheme:
        """Returns the requested transformation scheme."""
        return self.data.to_model()
