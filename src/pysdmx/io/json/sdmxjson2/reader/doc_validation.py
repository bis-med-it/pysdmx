"""SDMX-JSON document validation against JSON schemas."""

import json
import re
import warnings
from pathlib import Path
from typing import Any, Callable, List, Mapping, Match, Optional, Sequence

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
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

# SDMX-JSON schema files by message version then message type. The 2.0 and 2.1
# schema files share the same file name (only the directory differs), so the
# version must be selected before matching the type against ``meta.schema``.
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


def _schema_for(instance: Mapping[str, Any]) -> dict[str, Any]:
    schema_url = instance.get("meta", {}).get("schema", "")
    version = "2.1" if "2.1" in schema_url else "2.0"
    p = next(
        p for p in _SCHEMA_FILES[version].values() if p.name in schema_url
    )
    with p.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def _involves_datetime(e: ValidationError) -> bool:
    """Whether the error is caused by a strict ``date-time`` format check."""
    if e.validator == "format" and e.validator_value == "date-time":
        return True
    return any(_involves_datetime(c) for c in e.context or ())


def _describe_datetime(e: ValidationError) -> str:
    """Describes a ``date-time`` failure, pointing at the offending value.

    The error is either the strict ``date-time`` format failure itself,
    or a ``oneOf``/``anyOf`` failure holding it, possibly nested. In the
    latter case, the failing subschema errors are walked down to the
    ``date-time`` failure, to point at the offending value.
    """
    parts = list(e.absolute_path)
    cur = e
    while cur.validator != "format":
        nxt = next(c for c in cur.context or () if _involves_datetime(c))
        parts.extend(nxt.path)
        cur = nxt
    path = "$" if not parts else "$." + ".".join(map(str, parts))
    return f"{path}: {cur.instance!r} is not an RFC 3339 date-time"


def _compact(e: ValidationError) -> str:
    path = "$" if not e.path else "$." + ".".join(map(str, e.path))
    sub = " | ".join(
        getattr(e, "context", []) and [c.message for c in e.context] or []
    )
    raw = f"{e.message} | {sub}"

    patterns: list[tuple[str, Callable[[Match[str]], str]]] = [
        (
            r"Additional properties are not allowed.*'([^']+)'",
            lambda m: f"unexpected property '{m.group(1)}'",
        ),
        (
            r"is not of type '([^']+)'",
            lambda m: f"invalid type (expected {m.group(1)})",
        ),
        (
            r"""['"]?([^'"\n]+)['"]?\s+is not one of\s+\[([^\]]+)\]""",
            lambda m: "invalid value {!r} (expected one of: {})".format(
                m.group(1),
                ", ".join(
                    s.strip().strip("'\"") for s in m.group(2).split(",")
                ),
            ),
        ),
        (
            r"'([^']+)' is a required property",
            lambda m: f"missing property '{m.group(1)}'",
        ),
        (
            r"""does not match ['"]([^'"]+)['"]""",
            lambda m: f"does not match required pattern {m.group(1)!r}",
        ),
        (
            r"\[\]\s+is\s+too\s+short",
            lambda _m: "[] should be non-empty",
        ),
    ]

    msg: Optional[str] = next(
        (
            fmt(re.search(rx, raw))  # type: ignore[arg-type]
            for rx, fmt in patterns
            if re.search(rx, raw)
        ),
        None,
    )
    msg = msg or e.message
    return f"{path}: {msg}"


def _summarize(messages: Sequence[str]) -> str:
    summary = "; ".join(messages[:3])
    more = f" (+{len(messages) - 3} more errors)" if len(messages) > 3 else ""
    return f"{summary}{more}"


def validate_sdmx_json(input_str: str) -> None:
    """Validates an SDMX-JSON message against the appropriate JSON schema.

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
    schema = _schema_for(instance)
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )

    failures = sorted(
        validator.iter_errors(instance),
        key=lambda e: (list(e.path), e.message),
    )
    dt_failures: List[ValidationError] = []
    other_failures: List[ValidationError] = []
    for e in failures:
        if _involves_datetime(e):
            dt_failures.append(e)
        else:
            other_failures.append(e)

    if dt_failures:
        summary = _summarize([_describe_datetime(e) for e in dt_failures])
        warnings.warn(
            f"The message contains SDMX datetimes that are not RFC 3339 "
            f"compliant (e.g. the timezone is missing): {summary}. SDMX "
            "allows such datetimes, so the message is processed anyway, "
            "but it does not fully validate against the SDMX-JSON schema.",
            UserWarning,
            stacklevel=2,
        )
    if other_failures:
        summary = _summarize([_compact(e) for e in other_failures])
        raise errors.Invalid("Validation Error", summary)
