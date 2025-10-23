"""Collection of SDMX-JSON schemas for categories and category schemes."""

from collections import defaultdict
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
    MaintainableType,
    NameableType,
)
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.model import (
    Agency,
    Categorisation,
    Category,
    CategoryScheme,
    Dataflow,
    DataflowRef,
)
from pysdmx.util import find_by_urn


class JsonCategorisation(
    MaintainableType,
    frozen=True,
    rename={"agency": "agencyID"},
    omit_defaults=True,
):
    """SDMX-JSON payload for a categorisation."""

    source: str = ""
    target: str = ""

    def to_model(self) -> Categorisation:
        """Converts a JsonCategorisation to a standard categorisation."""
        return Categorisation(
            id=self.id,
            agency=self.agency,
            version=self.version,
            source=self.source,
            target=self.target,
            name=self.name,
            description=self.description,
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(self, cat: Categorisation) -> "JsonCategorisation":
        """Converts a pysdmx categorisation to an SDMX-JSON one."""
        if not cat.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON categorisations must have a name",
                {"categorisation": cat.id},
            )
        return JsonCategorisation(
            agency=(
                cat.agency.id if isinstance(cat.agency, Agency) else cat.agency
            ),
            id=cat.id,
            name=cat.name,
            version=cat.version,
            isExternalReference=cat.is_external_reference,
            validFrom=cat.valid_from,
            validTo=cat.valid_to,
            description=cat.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cat.annotations]
            ),
            source=cat.source,
            target=cat.target,
        )


class JsonCategory(NameableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a category."""

    categories: Sequence["JsonCategory"] = ()

    def __add_flows(
        self, cni: str, cf: Dict[str, list[Dataflow]]
    ) -> Sequence[DataflowRef]:
        if cni in cf:
            return [
                DataflowRef(
                    (
                        df.agency.id
                        if isinstance(df.agency, Agency)
                        else df.agency
                    ),
                    df.id,
                    df.version,
                    df.name,
                )
                for df in cf[cni]
            ]
        else:
            return ()

    def to_model(
        self,
        cat_flows: dict[str, list[Dataflow]],
        parent_id: Optional[str] = None,
    ) -> Category:
        """Converts a FusionCode to a standard code."""
        cni = f"{parent_id}.{self.id}" if parent_id else self.id
        dataflows = self.__add_flows(cni, cat_flows)
        return Category(
            id=self.id,
            name=self.name,
            description=self.description,
            categories=[c.to_model(cat_flows, cni) for c in self.categories],
            annotations=[a.to_model() for a in self.annotations],
            dataflows=dataflows,
        )

    @classmethod
    def from_model(self, cat: Category) -> "JsonCategory":
        """Converts a pysdmx category to an SDMX-JSON one."""
        if not cat.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON category must have a name",
                {"category": cat.id},
            )
        return JsonCategory(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cat.annotations]
            ),
            categories=tuple(
                [JsonCategory.from_model(c) for c in cat.categories]
            ),
        )


class JsonCategoryScheme(
    ItemSchemeType,
    frozen=True,
    rename={"agency": "agencyID"},
    omit_defaults=True,
):
    """SDMX-JSON payload for a category scheme."""

    categories: Sequence[JsonCategory] = ()

    def to_model(self, cat_flows: dict[str, list[Dataflow]]) -> CategoryScheme:
        """Converts a JsonCodelist to a standard codelist."""
        return CategoryScheme(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=[c.to_model(cat_flows) for c in self.categories],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            annotations=[a.to_model() for a in self.annotations],
        )

    @classmethod
    def from_model(self, cs: CategoryScheme) -> "JsonCategoryScheme":
        """Converts a pysdmx category scheme to an SDMX-JSON one."""
        if not cs.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON category schemes must have a name",
                {"category_scheme": cs.id},
            )
        return JsonCategoryScheme(
            agency=(
                cs.agency.id if isinstance(cs.agency, Agency) else cs.agency
            ),
            id=cs.id,
            name=cs.name,
            version=cs.version,
            isExternalReference=cs.is_external_reference,
            validFrom=cs.valid_from,
            validTo=cs.valid_to,
            description=cs.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cs.annotations]
            ),
            isPartial=cs.is_partial,
            categories=tuple(
                [JsonCategory.from_model(c) for c in cs.categories]
            ),
        )


class JsonCategorySchemes(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of category schemes."""

    categorySchemes: Sequence[JsonCategoryScheme]
    categorisations: Sequence[JsonCategorisation] = ()
    dataflows: Sequence[JsonDataflow] = ()

    def __group_flows(self) -> defaultdict[str, list[Dataflow]]:
        out: defaultdict[str, list[Dataflow]] = defaultdict(list)
        for c in self.categorisations:
            d = find_by_urn(self.dataflows, c.source)
            src = c.target[c.target.find(")") + 2 :]
            out[src].append(d.to_model())
        return out

    def to_model(self) -> CategoryScheme:
        """Returns the requested codelist."""
        cf = self.__group_flows()
        return self.categorySchemes[0].to_model(cf)


class JsonCategorySchemeMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /categoryscheme queries."""

    data: JsonCategorySchemes

    def to_model(self) -> CategoryScheme:
        """Returns the requested category scheme."""
        return self.data.to_model()


class JsonCategorisations(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of categorisations."""

    categorisations: Sequence[JsonCategorisation]


class JsonCategorisationMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /categorisation queries."""

    data: JsonCategorisations

    def to_model(self) -> Sequence[Categorisation]:
        """Returns the requested categorisations."""
        return [cat.to_model() for cat in self.data.categorisations]
