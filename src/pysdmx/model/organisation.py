"""Model for SDMX Organisations (data providers, agencies, etc).

Organisations in SDMX can play different roles, such as:

- Maintenance agencies, i.e. organisations that maintain metadata.
- Data (or metadata) providers, i.e. organisations that provide data or
  metadata.
- Data (or metadata) consumers, i.e. organisations that collect data or
  metadata.

Contact details may be included with the information about an organisation.

Currently, only agencies and providers are supported in pysdmx (as consumers
seem to be underused in SDMX currently).

Furthermore, in pysdmx, an organisation may reference a list of dataflows
it maintains (if the organisation is an agency) or for which it provides
data (if the organisation is a data provider).
"""

from typing import Optional, Sequence

from msgspec import Struct


class Contact(Struct, frozen=True, omit_defaults=True):
    """Contact details such as the name of a contact and his email address.

    Attributes:
        id: An identifier for a contact. If the contact represents a person,
            this could be the person's username in the organisation.
        name: The contact name, which could be the name of a person, the name
            of a service ("e.g. Support"), etc.
        department: The department in which the contact is located (e.g.
            "Statistics").
        role: The contact's role, which could be his job title, or a role such
            as data owner, data steward, subject matter expert, etc.
        telephones: A list of telephone numbers.
        faxes: A list of fax numbers.
        uris: A list of URLs relevant for the contact (e.g. a link to an online
            form that can be used to send questions, a link to a support forum,
            etc.).
        emails: a list of email addresses.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    telephones: Optional[Sequence[str]] = None
    faxes: Optional[Sequence[str]] = None
    uris: Optional[Sequence[str]] = None
    emails: Optional[Sequence[str]] = None


class DataflowRef(Struct, frozen=True, omit_defaults=True):
    """Provide core information about a dataflow.

    Attributes:
        id: The dataflow identifier (e.g. BIS_MACRO).
        agency: The organisation (or unit) responsible for the dataflow.
        name: The dataflow name (e.g. MACRO dataflow).
        description: Additional descriptive information about the dataflow.
        version: The version of the dataflow (e.g. 1.0).
    """

    id: str
    agency: str
    name: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = self.id
        if self.name:
            out = f"{out} ({self.name})"
        return out


class Organisation(Struct, frozen=True, omit_defaults=True):
    """An organisation such as a provider of data or a metadata maintainer.

    Central Banks, International Organisations, statistical offices, market
    data vendors are typical examples of organisations participating in
    statistical data exchanges.

    Organisations may have one or more contact details.

    Attributes:
        id: The identifier of the organisation (e.g. BIS).
        name: The name of the organisation (e.g. Bank for
            International Settlements).
        description: Additional descriptive information about
            the organisation.
        contacts: Contact details (email address, support forum, etc).
        dataflows: The dataflows maintained by the organisation if it is
            a maintenance agency or for which the organisation provides data
            if it is a data provider.
    """

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    contacts: Sequence[Contact] = ()
    dataflows: Sequence[DataflowRef] = ()

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = self.id
        if self.name:
            out = f"{out} ({self.name})"
        return out

    def __hash__(self) -> int:
        """Returns the organisation's hash."""
        return hash(self.id)
