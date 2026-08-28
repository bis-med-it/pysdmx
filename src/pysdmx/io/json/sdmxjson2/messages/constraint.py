"""Collection of SDMX-JSON schemas for content constraints."""

from datetime import datetime
from typing import Optional, Sequence, Union, cast

from msgspec import Struct

from pysdmx import errors
from pysdmx.errors import Invalid
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import (
    Agency,
    Annotation,
    AvailabilityConstraint,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeTimeRange,
    CubeValue,
    DataConstraint,
    DataKey,
    DataKeyValue,
    KeySet,
    TimePeriodBoundary,
)
from pysdmx.util import Reference, is_final, parse_urn


class JsonValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube value."""

    value: str
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None

    def to_model(self) -> CubeValue:
        """Converts a JsonValue to a CubeValue."""
        return CubeValue(self.value, self.validFrom, self.validTo)

    @classmethod
    def from_model(self, cv: CubeValue) -> "JsonValue":
        """Converts a pysdmx cube value to an SDMX-JSON one."""
        return JsonValue(cv.value, cv.valid_from, cv.valid_to)


class JsonTimePeriod(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for one end of a time range."""

    period: str
    isInclusive: bool = True

    def to_model(self) -> TimePeriodBoundary:
        """Converts a JsonTimePeriod to a TimePeriodBoundary."""
        return TimePeriodBoundary(self.period, self.isInclusive)

    @classmethod
    def from_model(cls, b: TimePeriodBoundary) -> "JsonTimePeriod":
        """Converts a pysdmx time period boundary to an SDMX-JSON one."""
        return JsonTimePeriod(b.period, b.is_inclusive)


class JsonTimeRange(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube-region time range."""

    beforePeriod: Optional[JsonTimePeriod] = None
    afterPeriod: Optional[JsonTimePeriod] = None
    startPeriod: Optional[JsonTimePeriod] = None
    endPeriod: Optional[JsonTimePeriod] = None

    def to_model(self) -> CubeTimeRange:
        """Converts a JsonTimeRange to a CubeTimeRange."""

        def conv(
            p: Optional[JsonTimePeriod],
        ) -> Optional[TimePeriodBoundary]:
            return p.to_model() if p else None

        return CubeTimeRange(
            conv(self.beforePeriod),
            conv(self.afterPeriod),
            conv(self.startPeriod),
            conv(self.endPeriod),
        )

    @classmethod
    def from_model(cls, tr: CubeTimeRange) -> "JsonTimeRange":
        """Converts a pysdmx cube time range to an SDMX-JSON one."""

        def conv(
            b: Optional[TimePeriodBoundary],
        ) -> Optional[JsonTimePeriod]:
            return JsonTimePeriod.from_model(b) if b else None

        return JsonTimeRange(
            conv(tr.before_period),
            conv(tr.after_period),
            conv(tr.start_period),
            conv(tr.end_period),
        )


class JsonKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of allowed values per component."""

    id: str
    values: Sequence[JsonValue] = ()
    timeRange: Optional[JsonTimeRange] = None
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    # `include` and `removePrefix` are supported by the SDMX-JSON schema
    # but not by the FMR. Therefore, they are ignored for now.

    def to_model(self) -> CubeKeyValue:
        """Converts a JsonKeyValue to a CubeKeyValue."""
        return CubeKeyValue(
            self.id,
            tuple([v.to_model() for v in self.values]),
            self.timeRange.to_model() if self.timeRange else None,
            self.validFrom,
            self.validTo,
        )

    @classmethod
    def from_model(self, key_value: CubeKeyValue) -> "JsonKeyValue":
        """Converts a pysdmx cube key value to an SDMX-JSON one."""
        values = tuple([JsonValue.from_model(v) for v in key_value.values])
        # values and time_range are mutually exclusive (enforced by
        # CubeKeyValue), so there is no precedence to resolve here.
        time_range = (
            JsonTimeRange.from_model(key_value.time_range)
            if key_value.time_range
            else None
        )
        return JsonKeyValue(
            key_value.id,
            values,
            time_range,
            key_value.valid_from,
            key_value.valid_to,
        )


class JsonCubeRegion(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube region."""

    # The property `components` is ignored as it's not used in the FMR`
    keyValues: Sequence[JsonKeyValue]
    include: bool = True

    def to_model(self) -> CubeRegion:
        """Converts a JsonCubeRegion to a CubeRegion."""
        return CubeRegion(
            tuple([kv.to_model() for kv in self.keyValues]), self.include
        )

    @classmethod
    def from_model(self, region: CubeRegion) -> "JsonCubeRegion":
        """Converts a pysdmx cube region to an SDMX-JSON one."""
        return JsonCubeRegion(
            [JsonKeyValue.from_model(kv) for kv in region.key_values],
            region.is_included,
        )


class JsonConstraintAttachment(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a constraint attachment."""

    dataProvider: Optional[str] = None
    dataStructures: Sequence[str] = ()
    dataflows: Sequence[str] = ()
    provisionAgreements: Sequence[str] = ()

    def to_model(self) -> ConstraintAttachment:
        """Converts a JsonConstraintAttachment to a ConstraintAttachment."""
        return ConstraintAttachment(
            self.dataProvider,
            tuple(self.dataStructures),
            tuple(self.dataflows),
            tuple(self.provisionAgreements),
        )

    @classmethod
    def from_model(
        self, attachment: ConstraintAttachment
    ) -> "JsonConstraintAttachment":
        """Converts a pysdmx constraint attachment to an SDMX-JSON one."""
        ds = attachment.data_structures or ()
        df = attachment.dataflows or ()
        pa = attachment.provision_agreements or ()
        return JsonConstraintAttachment(attachment.data_provider, ds, df, pa)


class JsonDataKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key value."""

    id: str
    value: str

    def to_model(self) -> DataKeyValue:
        """Converts a JsonDataKeyValue to a DataKeyValue."""
        return DataKeyValue(self.id, self.value)

    @classmethod
    def from_model(self, kv: DataKeyValue) -> "JsonDataKeyValue":
        """Converts a pysdmx key value to an SDMX-JSON one."""
        return JsonDataKeyValue(kv.id, kv.value)


class JsonDataKey(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key."""

    keyValues: Sequence[JsonDataKeyValue]
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None

    def to_model(self) -> DataKey:
        """Converts a JsonDataKey to a DataKey."""
        return DataKey(
            tuple([kv.to_model() for kv in self.keyValues]),
            self.validFrom,
            self.validTo,
        )

    @classmethod
    def from_model(self, kv: DataKey) -> "JsonDataKey":
        """Converts a pysdmx key constraint to an SDMX-JSON one."""
        return JsonDataKey(
            [JsonDataKeyValue.from_model(val) for val in kv.keys_values],
            kv.valid_from,
            kv.valid_to,
        )


class JsonKeySet(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a keyset."""

    keys: Sequence[JsonDataKey]
    isIncluded: bool

    def to_model(self) -> KeySet:
        """Converts a JsonKeySet to a KeySet."""
        return KeySet(
            tuple([k.to_model() for k in self.keys]), self.isIncluded
        )

    @classmethod
    def from_model(self, ks: KeySet) -> "JsonKeySet":
        """Converts a pysdmx key set constraint to an SDMX-JSON one."""
        return JsonKeySet(
            [JsonDataKey.from_model(k) for k in ks.keys], ks.is_included
        )


_METRIC_ANNOTATION_IDS = ("series_count", "obs_count")


def _metric_annotations(
    cons: AvailabilityConstraint,
) -> "tuple[JsonAnnotation, ...]":
    """Builds FMR-style ``sdmx_metrics`` annotations for the counts.

    The legacy ``dataConstraint`` payload has no dedicated field for
    the series/observation counts, so they are carried as
    annotations, mirroring what the FMR emits: an annotation with
    ``type="sdmx_metrics"``, ``id`` set to ``"series_count"`` or
    ``"obs_count"`` and the count as a string in ``title``.
    """
    metrics = []
    if cons.series_count is not None:
        metrics.append(
            JsonAnnotation(
                id="series_count",
                title=str(cons.series_count),
                type="sdmx_metrics",
            )
        )
    if cons.obs_count is not None:
        metrics.append(
            JsonAnnotation(
                id="obs_count",
                title=str(cons.obs_count),
                type="sdmx_metrics",
            )
        )
    return tuple(metrics)


def _lift_metric_annotations(
    annotations: Sequence[JsonAnnotation],
) -> "tuple[Optional[int], Optional[int], tuple[Annotation, ...]]":
    """Splits FMR-style ``sdmx_metrics`` annotations from the rest.

    Mirrors ``__parse_annotation_metrics`` in the SDMX-JSON dataflow
    reader: an annotation with ``type="sdmx_metrics"``, ``id`` in
    ``{"series_count", "obs_count"}`` and the count as a string in
    ``title`` is lifted into the matching return value instead of
    being kept as a plain annotation (it is dropped from the returned
    sequence so it is not written back out as a duplicate).

    A ``title`` that is not a plain non-negative integer is left as a
    regular annotation instead of being lifted.
    """
    series_count: Optional[int] = None
    obs_count: Optional[int] = None
    kept = []
    for a in annotations:
        if (
            a.type == "sdmx_metrics"
            and a.id in _METRIC_ANNOTATION_IDS
            and a.title is not None
            and a.title.isdecimal()
        ):
            if a.id == "series_count":
                series_count = int(a.title)
            else:
                obs_count = int(a.title)
        else:
            kept.append(a.to_model())
    return series_count, obs_count, tuple(kept)


class JsonDataConstraint(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a content constraint."""

    role: Optional[str] = None
    constraintAttachment: Optional[JsonConstraintAttachment] = None
    cubeRegions: Optional[Sequence[JsonCubeRegion]] = None
    dataKeySets: Optional[Sequence[JsonKeySet]] = None

    def to_model(self) -> Union[DataConstraint, AvailabilityConstraint]:
        """Converts a JsonDataConstraint to a pysdmx constraint.

        A constraint with role "Actual" is mapped to an
        AvailabilityConstraint; any other role (or its absence) is
        mapped to a DataConstraint.

        Raises:
            Invalid: If a constraint with role "Actual" has key sets,
                or does not have exactly one cube region and one
                attached artefact.
        """
        at = (
            self.constraintAttachment.to_model()
            if self.constraintAttachment
            else None
        )
        if self.role == "Actual":
            regions = [r.to_model() for r in (self.cubeRegions or ())]
            if self.dataKeySets:
                raise Invalid(
                    "Invalid availability constraint",
                    "An Actual constraint with key sets cannot be "
                    "represented as an availability constraint.",
                )
            if len(regions) != 1 or at is None:
                raise Invalid(
                    "Invalid availability constraint",
                    "An Actual constraint must have exactly one cube "
                    "region and one attached artefact.",
                )
            series_count, obs_count, annotations = _lift_metric_annotations(
                self.annotations
            )
            return AvailabilityConstraint(
                annotations=annotations,
                constraint_attachment=at,
                cube_region=regions[0],
                series_count=series_count,
                obs_count=obs_count,
            )
        return DataConstraint(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
            is_final=is_final(self.version),
            valid_from=self.validFrom,
            valid_to=self.validTo,
            constraint_attachment=at,
            cube_regions=(
                tuple([r.to_model() for r in self.cubeRegions])
                if self.cubeRegions
                else ()
            ),
            key_sets=(
                tuple([s.to_model() for s in self.dataKeySets])
                if self.dataKeySets
                else ()
            ),
        )

    @classmethod
    def from_model(
        self, cons: DataConstraint, with_role: bool = True
    ) -> "JsonDataConstraint":
        """Converts a pysdmx constraint to an SDMX-JSON one.

        Args:
            cons: The data constraint to be converted.
            with_role: Whether to write the legacy SDMX-JSON 2.0
                ``role`` field (always ``"Allowed"``, as constraints
                with role ``"Actual"`` are represented as
                AvailabilityConstraint instead). SDMX-JSON 2.1 removed
                the field, so pass ``False`` when writing 2.1.
        """
        crs = (
            [JsonCubeRegion.from_model(r) for r in cons.cube_regions]
            if cons.cube_regions
            else None
        )
        dks = (
            [JsonKeySet.from_model(s) for s in cons.key_sets]
            if cons.key_sets
            else None
        )
        if not cons.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON data constraints must have a name",
                {"data_constraint": cons.id},
            )
        if not cons.constraint_attachment:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON data constraints must have a constraint attachment",
                {"data_constraint": cons.id},
            )
        return JsonDataConstraint(
            id=cons.id,
            name=cons.name,
            agency=(
                cons.agency.id
                if isinstance(cons.agency, Agency)
                else cons.agency
            ),
            description=cons.description,
            version=cons.version,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cons.annotations]
            ),
            isExternalReference=cons.is_external_reference,
            validFrom=cons.valid_from,
            validTo=cons.valid_to,
            role="Allowed" if with_role else None,
            constraintAttachment=JsonConstraintAttachment.from_model(
                cons.constraint_attachment
            ),
            cubeRegions=crs,
            dataKeySets=dks,
        )

    @classmethod
    def from_availability(
        cls, cons: AvailabilityConstraint
    ) -> "JsonDataConstraint":
        """Creates a legacy Actual payload for an availability constraint.

        SDMX-JSON 2.0 has no availability collection, so the constraint
        is written as a dataConstraint with role "Actual" and an
        identification synthesised from the attached artefact. The
        series/observation counts have no field to live in either, so
        they are appended as ``sdmx_metrics`` annotations (see
        ``_metric_annotations``).
        """
        ref = cast(Reference, parse_urn(cons.reference))
        return JsonDataConstraint(
            id=ref.id,
            name=f"Availability for {ref.id}",
            agency=ref.agency,
            version=ref.version,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cons.annotations]
                + list(_metric_annotations(cons))
            ),
            role="Actual",
            constraintAttachment=JsonConstraintAttachment.from_model(
                cons.constraint_attachment
            ),
            cubeRegions=[JsonCubeRegion.from_model(cons.cube_region)],
        )


class JsonAvailabilityConstraintAttachment(
    Struct, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for an availability constraint attachment."""

    dataStructure: Optional[str] = None
    dataflow: Optional[str] = None
    provisionAgreement: Optional[str] = None

    def to_model(self) -> ConstraintAttachment:
        """Converts the payload to a pysdmx constraint attachment."""
        return ConstraintAttachment(
            data_provider=None,
            data_structures=(
                (self.dataStructure,) if self.dataStructure else None
            ),
            dataflows=(self.dataflow,) if self.dataflow else None,
            provision_agreements=(
                (self.provisionAgreement,) if self.provisionAgreement else None
            ),
        )

    @classmethod
    def from_model(
        cls, at: ConstraintAttachment
    ) -> "JsonAvailabilityConstraintAttachment":
        """Converts a pysdmx constraint attachment to the payload."""
        return JsonAvailabilityConstraintAttachment(
            dataStructure=(
                at.data_structures[0] if at.data_structures else None
            ),
            dataflow=at.dataflows[0] if at.dataflows else None,
            provisionAgreement=(
                at.provision_agreements[0] if at.provision_agreements else None
            ),
        )


class JsonAvailabilityConstraint(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON 2.1 payload for an availability constraint."""

    constraintAttachment: Optional[JsonAvailabilityConstraintAttachment] = None
    cubeRegion: Optional[JsonCubeRegion] = None
    seriesCount: Optional[int] = None
    obsCount: Optional[int] = None
    annotations: Sequence[JsonAnnotation] = ()

    def to_model(self) -> AvailabilityConstraint:
        """Converts the payload to a pysdmx availability constraint."""
        if self.constraintAttachment is None or self.cubeRegion is None:
            raise Invalid(
                "Invalid availability constraint",
                "An availability constraint requires a constraint "
                "attachment and a cube region.",
            )
        return AvailabilityConstraint(
            annotations=tuple([a.to_model() for a in self.annotations]),
            constraint_attachment=self.constraintAttachment.to_model(),
            cube_region=self.cubeRegion.to_model(),
            series_count=self.seriesCount,
            obs_count=self.obsCount,
        )

    @classmethod
    def from_model(
        cls, cons: AvailabilityConstraint
    ) -> "JsonAvailabilityConstraint":
        """Converts a pysdmx availability constraint to the payload."""
        return JsonAvailabilityConstraint(
            constraintAttachment=(
                JsonAvailabilityConstraintAttachment.from_model(
                    cons.constraint_attachment
                )
            ),
            cubeRegion=JsonCubeRegion.from_model(cons.cube_region),
            seriesCount=cons.series_count,
            obsCount=cons.obs_count,
            # tuple([...]) rather than a generator: on Python 3.10 an
            # empty tuple built from a generator is not interned, so
            # msgspec's omit_defaults would emit [] (which the 2.1
            # schema rejects as empty).
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cons.annotations]
            ),
        )


class JsonDataConstraints(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for data constraints."""

    dataConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(
        self,
    ) -> Sequence[Union[DataConstraint, AvailabilityConstraint]]:
        """Returns the requested data constraints."""
        return [cc.to_model() for cc in self.dataConstraints]


class JsonDataConstraintMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataconstraint queries."""

    data: JsonDataConstraints

    def to_model(
        self,
    ) -> Sequence[Union[DataConstraint, AvailabilityConstraint]]:
        """Returns the requested data constraints."""
        return self.data.to_model()
