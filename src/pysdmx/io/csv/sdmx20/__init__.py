"""SDMX 2.0 CSV reader and writer."""

from pysdmx.model.message import ActionType

SDMX_CSV_ACTION_MAPPER = {
    ActionType.Append: "A",
    ActionType.Replace: "R",
    ActionType.Information: "I",
    ActionType.Delete: "D",
}
