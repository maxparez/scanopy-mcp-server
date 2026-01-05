"""Tests for scanopy_mcp.openapi_loader fixes."""

from unittest.mock import Mock

from scanopy_mcp.openapi_loader import OpenAPILoader


def test_cache_returns_empty_dict(mocker):
    """Loader should cache empty dict correctly (truthiness bug fix)."""
    url = "http://scanopy.local/openapi.json"
    mock_response = Mock()
    mock_response.json.return_value = {}  # Empty dict - falsy in Python
    mock_response.raise_for_status = Mock()
    httpx_mock = mocker.patch("httpx.get", return_value=mock_response)

    loader = OpenAPILoader(url=url)

    # First call - fetches
    spec1 = loader.load()
    assert spec1 == {}
    assert httpx_mock.call_count == 1

    # Second call - should use cache, not fetch again
    spec2 = loader.load()
    assert spec2 == {}
    assert httpx_mock.call_count == 1  # Still 1, not 2
