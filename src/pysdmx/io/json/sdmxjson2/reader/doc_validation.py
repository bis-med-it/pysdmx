"""SDMX-JSON document validation against JSON schemas.

The validation uses jsonschema-rs when it is installed, and jsonschema
otherwise. The failures found by either library are converted to the same
representation, so that the outcome (error, warning and their messages)
does not depend on the library in use.
"""

import ast
import json
import re
import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Sequence,
    Tuple,
    Union,
)

from sdmxschemas import SDMX_JSON_20_DATA_PATH as SCHEMA_PATH_JSON20_DATA
from sdmxschemas import (
    SDMX_JSON_20_METADATA_PATH as SCHEMA_PATH_JSON20_METADATA,
)
from sdmxschemas import (
    SDMX_JSON_20_STRUCTURE_PATH as SCHEMA_PATH_JSON20_STRUCTURE,
)
from sdmxschemas import SDMX_JSON_21_DATA_PATH as SCHEMA_PATH_JSON21_DATA
from sdmxschemas import (
    SDMX_JSON_21_METADATA_PATH as SCHEMA_PATH_JSON21_METADATA,
)
from sdmxschemas import (
    SDMX_JSON_21_STRUCTURE_PATH as SCHEMA_PATH_JSON21_STRUCTURE,
)

from pysdmx import errors
from pysdmx.__extras_check import __check_json_extra as _json_library

if TYPE_CHECKING:  # pragma: no cover
    import jsonschema.exceptions
    import jsonschema_rs

# SDMX-JSON schema files by message version then message type. The 2.0 and 2.1
# schema files share the same file name (only the directory differs), so the
# version must be selected before matching the type against the schema URL.
_SCHEMA_FILES: Mapping[str, Mapping[str, Path]] = {
    "2.0": {
        "structure": SCHEMA_PATH_JSON20_STRUCTURE,
        "metadata": SCHEMA_PATH_JSON20_METADATA,
        "data": SCHEMA_PATH_JSON20_DATA,
    },
    "2.1": {
        "structure": SCHEMA_PATH_JSON21_STRUCTURE,
        "metadata": SCHEMA_PATH_JSON21_METADATA,
        "data": SCHEMA_PATH_JSON21_DATA,
    },
}

_Path = Tuple[Union[str, int], ...]


@dataclass(frozen=True)
class _Failure:
    """A schema validation failure, whichever library found it.

    Attributes:
        path: The location of the failing value in the message.
        keyword: The JSON Schema keyword that failed (e.g. ``required``).
        instance: The failing value.
        detail: The keyword-specific detail, such as the missing property
            for ``required``, or the expected types for ``type``.
        context: For ``anyOf`` and ``oneOf``, the failures of their
            subschemas.
    """

    path: _Path
    keyword: str
    instance: Any
    detail: Any
    context: Tuple["_Failure", ...]


def _schema_for(instance: Mapping[str, Any]) -> Path:
    # ``meta.schema`` is optional: SDMX-JSON 2.1 messages may declare their
    # schema in the top-level ``$schema`` instead.
    schema_url = instance.get("meta", {}).get("schema") or instance.get(
        "$schema", ""
    )
    version = "2.1" if "2.1" in schema_url else "2.0"
    p = next(
        (p for p in _SCHEMA_FILES[version].values() if p.name in schema_url),
        None,
    )
    if p is None:
        raise errors.Invalid(
            "Validation Error",
            "The message does not declare a supported SDMX-JSON schema, "
            "neither in meta.schema nor in $schema.",
        )
    return p


@lru_cache(maxsize=None)
def _load_schema(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# jsonschema does not check the ``uri`` and ``uri-reference`` formats
# without further dependencies, and only checks that an ``email`` contains
# an ``@``. jsonschema-rs is given the same checks, so that a message is
# valid or invalid whichever library validates it.
def _any_value(value: str) -> bool:
    return True


def _has_at_sign(value: str) -> bool:
    return "@" in value


@lru_cache(maxsize=None)
def _rs_validator(path: Path) -> "jsonschema_rs.Draft202012Validator":
    import jsonschema_rs

    return jsonschema_rs.Draft202012Validator(
        _load_schema(path),
        validate_formats=True,
        formats={
            "uri": _any_value,
            "uri-reference": _any_value,
            "email": _has_at_sign,
        },
    )


def _from_rs(e: "jsonschema_rs.ValidationError") -> _Failure:
    kind = e.kind
    detail = next(
        (
            getattr(kind, attribute)
            for attribute in (
                "unexpected",
                "property",
                "types",
                "options",
                "pattern",
                "limit",
                "format",
                "expected_value",
            )
            if hasattr(kind, attribute)
        ),
        None,
    )
    # Like jsonschema, keep the subschema failures of an ``anyOf`` or
    # ``oneOf`` that no subschema matches, but not of a ``oneOf`` that
    # several subschemas match.
    branches = (
        getattr(kind, "context", ())
        if type(kind).__name__ != "OneOfMultipleValid"
        else ()
    )
    context = tuple(_from_rs(c) for branch in branches for c in branch)
    return _Failure(
        tuple(e.instance_path), kind.name, e.instance, detail, context
    )


def _rs_failures(path: Path, instance: Any) -> Iterator[_Failure]:
    return (_from_rs(e) for e in _rs_validator(path).iter_errors(instance))


@lru_cache(maxsize=None)
def _jsonschema_validator(
    path: Path,
) -> "jsonschema.Draft202012Validator":
    from jsonschema import Draft202012Validator

    return Draft202012Validator(
        _load_schema(path),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def _unexpected_properties(message: str) -> List[str]:
    # jsonschema only names the unexpected properties in its messages, e.g.
    # "Additional properties are not allowed ('a', 'b' were unexpected)" or,
    # next to patternProperties, "'a' does not match any of the regexes: ...".
    m = re.search(r"\((.*) (?:was|were) un", message) or re.match(
        r"(.*) (?:does|do) not match any of the regexes", message
    )
    return list(ast.literal_eval(f"[{m.group(1)}]")) if m else []


def _jsonschema_detail(
    keyword: str, e: "jsonschema.exceptions.ValidationError"
) -> Any:
    if keyword in ("additionalProperties", "unevaluatedProperties"):
        return _unexpected_properties(e.message)
    if keyword == "required":
        # The message is "<property repr> is a required property".
        return ast.literal_eval(e.message.rsplit(" is a required", 1)[0])
    if keyword == "type" and isinstance(e.validator_value, str):
        return [e.validator_value]
    return e.validator_value


def _from_jsonschema(e: "jsonschema.exceptions.ValidationError") -> _Failure:
    # A false subschema has no keyword (``validator`` is None).
    keyword = str(e.validator or "falseSchema")
    return _Failure(
        tuple(e.absolute_path),
        keyword,
        e.instance,
        _jsonschema_detail(keyword, e),
        tuple(_from_jsonschema(c) for c in e.context or ()),
    )


def _jsonschema_failures(path: Path, instance: Any) -> Iterator[_Failure]:
    validator = _jsonschema_validator(path)
    return (_from_jsonschema(e) for e in validator.iter_errors(instance))


_FAILURES: Mapping[str, Callable[[Path, Any], Iterator[_Failure]]] = {
    "jsonschema_rs": _rs_failures,
    "jsonschema": _jsonschema_failures,
}


def _path_key(path: _Path) -> Tuple[Tuple[int, int, str], ...]:
    # Paths mix property names and array indexes, which do not compare.
    return tuple((0, p, "") if isinstance(p, int) else (1, 0, p) for p in path)


def _format_path(path: _Path) -> str:
    return "$" if not path else "$." + ".".join(map(str, path))


def _unexpected(f: _Failure) -> str:
    names = ", ".join(repr(n) for n in sorted(f.detail))
    return f"unexpected propert{'y' if len(f.detail) == 1 else 'ies'} {names}"


# The descriptions of the failures of the keywords used by the SDMX-JSON
# schemas. ``anyOf`` and ``oneOf`` failures are described by the failure
# of one of their subschemas (see ``_compact``), except for a ``oneOf``
# failing because several of its subschemas match.
_DESCRIPTIONS: Mapping[str, Callable[[_Failure], str]] = {
    "additionalProperties": _unexpected,
    "unevaluatedProperties": _unexpected,
    "type": lambda f: (
        f"invalid type (expected {' or '.join(sorted(f.detail))})"
    ),
    "enum": lambda f: "invalid value {!r} (expected one of: {})".format(
        f.instance, ", ".join(map(str, f.detail))
    ),
    "const": lambda f: f"invalid value {f.instance!r} (expected {f.detail!r})",
    "required": lambda f: f"missing property {f.detail!r}",
    "pattern": lambda f: f"does not match required pattern {f.detail!r}",
    # The SDMX-JSON schemas only require non-empty arrays.
    "minItems": lambda f: f"{f.instance!r} should be non-empty",
    "maxItems": lambda f: f"should have at most {f.detail} items",
    "maxProperties": lambda f: f"should have at most {f.detail} properties",
    "uniqueItems": lambda f: "should not have duplicate items",
    "minimum": lambda f: f"{f.instance!r} is less than {f.detail}",
    "maximum": lambda f: f"{f.instance!r} is greater than {f.detail}",
    "format": lambda f: f"{f.instance!r} is not a valid {f.detail}",
    "not": lambda f: "matches a definition that is not allowed",
    "oneOf": lambda f: "matches more than one allowed definition",
}

# The subschema failure reported for an ``anyOf`` or ``oneOf`` failure is
# the first kind of failure in this list, if any.
_SUBSCHEMA_PRIORITY = (
    "additionalProperties",
    "unevaluatedProperties",
    "type",
    "enum",
    "required",
    "pattern",
    "minItems",
)


def _describe(f: _Failure) -> str:
    describe = _DESCRIPTIONS.get(f.keyword)
    return describe(f) if describe else f"fails the '{f.keyword}' check"


def _priority(f: _Failure) -> int:
    if f.keyword in _SUBSCHEMA_PRIORITY:
        return _SUBSCHEMA_PRIORITY.index(f.keyword)
    return len(_SUBSCHEMA_PRIORITY)


def _compact(f: _Failure) -> str:
    if f.context:
        # An ``anyOf`` or ``oneOf`` failure, described by the failure of
        # one of its subschemas, chosen whatever their order.
        reported = min(
            f.context,
            key=lambda c: (_priority(c), _path_key(c.path), _compact(c)),
        )
        return _compact(reported)
    return f"{_format_path(f.path)}: {_describe(f)}"


def _is_datetime(f: _Failure) -> bool:
    return f.keyword == "format" and f.detail == "date-time"


def _involves_datetime(f: _Failure) -> bool:
    """Whether the failure is caused by a strict ``date-time`` check."""
    return _is_datetime(f) or any(_involves_datetime(c) for c in f.context)


def _datetime_failures(f: _Failure) -> Iterator[_Failure]:
    """Yields the strict ``date-time`` failures behind a failure.

    The failure is either the strict ``date-time`` format failure itself,
    or a ``oneOf``/``anyOf`` failure holding such failures, possibly
    nested, which point at the offending values.
    """
    if _is_datetime(f):
        yield f
    for c in f.context:
        yield from _datetime_failures(c)


def _describe_datetimes(failures: Sequence[_Failure]) -> List[str]:
    offending = {
        dt.path: dt.instance for f in failures for dt in _datetime_failures(f)
    }
    return [
        f"{_format_path(p)}: {offending[p]!r} is not an RFC 3339 date-time"
        for p in sorted(offending, key=_path_key)
    ]


def _summarize(messages: Sequence[str]) -> str:
    summary = "; ".join(messages[:3])
    more = f" (+{len(messages) - 3} more errors)" if len(messages) > 3 else ""
    return f"{summary}{more}"


def validate_sdmx_json(input_str: str) -> None:
    """Validates an SDMX-JSON message against the appropriate JSON schema.

    The validation uses jsonschema-rs when it is installed, and jsonschema
    otherwise, with the same outcome.

    Datetimes without timezone information are allowed by SDMX, but the
    SDMX-JSON schemas require RFC 3339 compliant datetimes (i.e. with
    timezone information). Failures caused by the strict ``date-time``
    format check are therefore reported as a ``UserWarning`` instead of
    an error.

    Args: input_str: The SDMX-JSON message to validate.
    Raises:
        invalid: If the SDMX-JSON message does not validate against the
            schema.

    Warns:
        UserWarning: If the only issues found are datetimes that are not
            RFC 3339 compliant (e.g. without timezone information).
    """
    instance = json.loads(input_str)
    schema_path = _schema_for(instance)
    find_failures = _FAILURES[_json_library()]

    failures = sorted(
        find_failures(schema_path, instance),
        key=lambda f: (_path_key(f.path), _compact(f)),
    )
    dt_failures = [f for f in failures if _involves_datetime(f)]
    other_failures = [f for f in failures if not _involves_datetime(f)]

    if dt_failures:
        summary = _summarize(_describe_datetimes(dt_failures))
        warnings.warn(
            f"The message contains SDMX datetimes that are not RFC 3339 "
            f"compliant (e.g. the timezone is missing): {summary}. SDMX "
            "allows such datetimes, so the message is processed anyway, "
            "but it does not fully validate against the SDMX-JSON schema.",
            UserWarning,
            stacklevel=2,
        )
    if other_failures:
        summary = _summarize([_compact(f) for f in other_failures])
        raise errors.Invalid("Validation Error", summary)
