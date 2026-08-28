"""Collection of SDMX-JSON schemas for organisations."""

from typing import Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
)
from pysdmx.model import Agency, DataConsumer, DataConsumerScheme
from pysdmx.util import is_final


class JsonDataConsumerScheme(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data consumer scheme."""

    dataConsumers: Sequence[DataConsumer] = ()

    def to_model(self) -> DataConsumerScheme:
        """Converts a JsonDataConsumerScheme to a list of organisations."""
        consumers = [
            DataConsumer(
                id=p.id,
                name=p.name,
                description=p.description,
                contacts=p.contacts,
                annotations=tuple([a.to_model() for a in self.annotations]),
            )
            for p in self.dataConsumers
        ]
        return DataConsumerScheme(
            agency=self.agency,
            description=self.description,
            items=consumers,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
            is_final=is_final(self.version),
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )

    @classmethod
    def from_model(self, dps: DataConsumerScheme) -> "JsonDataConsumerScheme":
        """Converts a pysdmx data consumer scheme to an SDMX-JSON one."""
        return JsonDataConsumerScheme(
            id="DATA_CONSUMERS",
            name="DATA_CONSUMERS",
            agency=(
                dps.agency.id if isinstance(dps.agency, Agency) else dps.agency
            ),
            description=dps.description,
            version="1.0",
            dataConsumers=dps.items,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in dps.annotations]
            ),
            isExternalReference=dps.is_external_reference,
            isPartial=dps.is_partial,
            validFrom=dps.valid_from,
            validTo=dps.valid_to,
        )


class JsonDataConsumerSchemes(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of data consumer schemes."""

    dataConsumerSchemes: Sequence[JsonDataConsumerScheme]

    def to_model(self) -> Sequence[DataConsumerScheme]:
        """Converts JsonDataConsumerSchemes to a list of organisations."""
        return [s.to_model() for s in self.dataConsumerSchemes]


class JsonConsumerMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataconsumerscheme queries."""

    data: JsonDataConsumerSchemes

    def to_model(self) -> Sequence[DataConsumerScheme]:
        """Returns the requested list of data consumer schemes."""
        return self.data.to_model()
