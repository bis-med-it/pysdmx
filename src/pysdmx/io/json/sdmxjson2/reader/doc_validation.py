"""SDMX-JSON document validation against JSON schemas."""

import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping, Match, Optional

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import (  # type: ignore[import-untyped]
    ValidationError,
)
from sdmxschemas import SDMX_JSON_20_DATA_PATH as SCHEMA_PATH_JSON20_DATA
from sdmxschemas import (
    SDMX_JSON_20_METADATA_PATH as SCHEMA_PATH_JSON20_METADATA,
)
from sdmxschemas import (
    SDMX_JSON_20_STRUCTURE_PATH as SCHEMA_PATH_JSON20_STRUCTURE,
)

from pysdmx import errors

_SCHEMA_FILES: Mapping[str, Path] = {
    "structure": SCHEMA_PATH_JSON20_STRUCTURE,
    "metadata": SCHEMA_PATH_JSON20_METADATA,
    "data": SCHEMA_PATH_JSON20_DATA,
}


def _schema_for(instance: Mapping[str, Any]) -> dict[str, Any]:
    schema_url = instance.get("meta", {}).get("schema")
    p = next(p for p in _SCHEMA_FILES.values() if p.name in schema_url)
    with p.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def validate_sdmx_json(input_str: str) -> None:
    """Validates an SDMX-JSON message against the appropriate JSON schema.

    Args: input_str: The SDMX-JSON message to validate.
    Raises:
        invalid: If the SDMX-JSON message does not validate against the schema.

    """
    instance = json.loads(input_str)
    schema = _schema_for(instance)
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
