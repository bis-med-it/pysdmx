"""Your opinionated Python SDMX library."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pysdmx")
except PackageNotFoundError:
    __version__ = "0.0.0"
