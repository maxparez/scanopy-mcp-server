"""Tests for scanopy_mcp.openapi_loader."""

from unittest.mock import Mock

from scanopy_mcp.openapi_loader import OpenAPILoader


def test_loads_openapi_and_paths(mocker):
    """Loader should fetch OpenAPI spec and return paths."""
    url = "http://scanopy.local/openapi.json"
    mock_response = Mock()
    mock_response.json.return_value = {"openapi": "3.0.0", "paths": {"/api/v1/x": {"get": {}}}}
    mock_response.raise_for_status = Mock()
    mocker.patch("httpx.get", return_value=mock_response)

    loader = OpenAPILoader(url=url)
    spec = loader.load()

    assert "/api/v1/x" in spec["paths"]
