"""SDMX-JSON document validation against JSON schemas."""


import json
import re
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Mapping, Match, Optional

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import (  # type: ignore[import-untyped]
    ValidationError,
)
from sdmxschemas.json import sdmx20

from pysdmx import errors

_SCHEMA_FILES = {
    "structure": "sdmx-json-structure-schema.json",
    "metadata": "sdmx-json-metadata-schema.json",
    "data": "sdmx-json-data-schema.json",
}


def _infer_message_type(instance: dict[str, Any]) -> str:
    schema_url: Optional[str] = (
        instance.get("meta", {}).get("schema")
        if isinstance(instance.get("meta"), dict)
        else None
    )
    return next(m for m, f in _SCHEMA_FILES.items()
                if schema_url and f in schema_url)


def _load_schema(message_type: str) -> Mapping[str, Any]:
    schema_filename = _SCHEMA_FILES[message_type]
    schema_trav = resources.files(sdmx20).joinpath(schema_filename)
    with resources.as_file(schema_trav) as schema_path:
        schema_path = Path(schema_path)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        base_uri = schema_path.parent.as_uri() + "/"
    schema.setdefault("$id", base_uri + schema_filename)
    return schema


def validate_sdmx_json(input_str: str) -> None:
    """Validates an SDMX-JSON message against the appropriate JSON schema.

    Args: input_str: The SDMX-JSON message to validate.
    Raises:
        invalid: If the SDMX-JSON message does not validate against the schema.

    """
    instance = json.loads(input_str)
    message_type = _infer_message_type(instance)

    schema = _load_schema(message_type)
    validator = Draft202012Validator(schema)

    failures = sorted(
        validator.iter_errors(instance),
        key=lambda e: (list(e.path), e.message),
    )
    if failures:

        def compact(e: ValidationError) -> str:
            path = "$" if not e.path else "$." + ".".join(map(str, e.path))
            sub = " | ".join(
                getattr(e, "context", [])
                and [c.message for c in e.context]
                or []
            )
            raw = f"{e.message} | {sub}"

            patterns: list[tuple[str, Callable[[Match[str]], str]]] = [
                (
                    r"'([^']+)' is a required property",
                    lambda m: f"missing property '{m.group(1)}'",
                ),
                (
                    r"Additional properties are not allowed.*'([^']+)'",
                    lambda m: f"unexpected property '{m.group(1)}'",
                ),
                (
                    r"is not of type '([^']+)'",
                    lambda m: f"invalid type (expected {m.group(1)})",
                ),
                (
                    r"is not one of",
                    lambda m: "invalid value (not in enumeration)",
                ),
                (
                    r"does not match",
                    lambda m: "does not match required pattern",
                ),
                (
                    r"is not valid under any of the"
                    r" given schemas|does not satisfy any allowed schema",
                    lambda m: "does not satisfy any allowed schema",
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
            msg = msg or (
                e.message.replace("\n", " ")[:77] + "…"
                if len(e.message) > 80
                else e.message
            )
            return f"{path}: {msg}"

        summary = "; ".join(compact(e) for e in failures[:3])
        more = (
            f" (+{len(failures) - 3} more errors)" if len(failures) > 3 else ""
        )
        raise errors.Invalid("Validation Error", f"{summary}{more}")
