"""Tests for the package version exposed by pysdmx."""

import importlib
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import pysdmx


def test_version_is_read_from_distribution_metadata() -> None:
    """Expose the version reported by installed distribution metadata."""
    with patch("importlib.metadata.version", return_value="1.22.0rc1"):
        importlib.reload(pysdmx)

    assert pysdmx.__version__ == "1.22.0rc1"


def test_version_has_a_fallback_when_distribution_is_unavailable() -> None:
    """Expose a fallback version when the package is not installed."""
    with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
        importlib.reload(pysdmx)

    assert pysdmx.__version__ == "0.0.0"
