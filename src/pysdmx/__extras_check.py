EXTRAS_DOCS = "https://py.sdmx.io/start.html#how-can-i-get-it"
ERROR_MESSAGE = (
    "The '{extra_name}' extra is required to run {extra_desc}. "
    "Please install it using 'pip install pysdmx[{extra_name}]' or "
    "install all extras with 'pip install pysdmx[all]'. "
    f"Check the documentation at: {EXTRAS_DOCS}"
)


def __check_dc_extra() -> None:
    try:
        import dateutil  # noqa: F401
    except ImportError:
        raise ImportError(
            ERROR_MESSAGE.format(
                extra_name="dc", extra_desc="the python parser for dates"
            )
        ) from None


def __check_data_extra() -> None:
    try:
        import pandas  # noqa: F401
    except ImportError:
        raise ImportError(
            ERROR_MESSAGE.format(
                extra_name="data",
                extra_desc="the reading and writing of Data Messages",
            )
        ) from None


def __check_xml_extra() -> None:
    try:
        import lxml  # noqa: F401
        import sdmxschemas  # noqa: F401
        import xmltodict  # noqa: F401
    except ImportError:
        raise ImportError(
            ERROR_MESSAGE.format(
                extra_name="xml",
                extra_desc="the reading and writing of SDMX-ML Messages",
            )
        ) from None


def __check_vtl_extra() -> None:
    try:
        import vtlengine  # type: ignore[import-untyped]  # noqa: F401
    except ImportError:
        raise ImportError(
            ERROR_MESSAGE.format(
                extra_name="vtl",
                extra_desc="VTL Scripts, SDMX-VTL model validations"
                " and prettify",
            )
        ) from None
