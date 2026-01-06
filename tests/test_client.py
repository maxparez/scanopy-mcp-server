"""Tests for scanopy_mcp.client."""

from scanopy_mcp.client import ScanopyClient


def test_auth_header_is_bearer():
    """Client should use Bearer token authentication."""
    client = ScanopyClient(base_url="http://x", api_key="scp_u_test")
    assert client._headers()["Authorization"].startswith("Bearer ")


def test_request_includes_base_url(mocker):
    """Client should prepend base URL to request path."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status = mocker.Mock()
    httpx_mock = mocker.patch("httpx.Client.request", return_value=mock_response)

    client = ScanopyClient(base_url="http://test", api_key="key123")
    client.request("GET", "/api/v1/hosts")

    # Verify full URL was called
    call_args = httpx_mock.call_args
    assert call_args[0][1] == "http://test/api/v1/hosts"


def test_request_passes_json_body(mocker):
    """Client should pass JSON body in requests."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": 1}
    mock_response.raise_for_status = mocker.Mock()
    httpx_mock = mocker.patch("httpx.Client.request", return_value=mock_response)

    client = ScanopyClient(base_url="http://test", api_key="key123")
    client.request("POST", "/api/v1/hosts", json={"name": "test"})

    # Verify JSON was passed
    call_kwargs = httpx_mock.call_args[1]
    assert call_kwargs["json"] == {"name": "test"}


def test_request_substitutes_path_params(mocker):
    """Client should substitute {id} placeholders in path."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": 123}
    mock_response.raise_for_status = mocker.Mock()
    httpx_mock = mocker.patch("httpx.Client.request", return_value=mock_response)

    client = ScanopyClient(base_url="http://test", api_key="key123")
    client.request("GET", "/api/v1/hosts/{id}", params={"id": 123})

    # Verify path substitution
    call_args = httpx_mock.call_args
    assert call_args[0][1] == "http://test/api/v1/hosts/123"


def test_request_sends_query_params_for_get(mocker):
    """Client should send query params for GET requests."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"hosts": []}
    mock_response.raise_for_status = mocker.Mock()
    httpx_mock = mocker.patch("httpx.Client.request", return_value=mock_response)

    client = ScanopyClient(base_url="http://test", api_key="key123")
    client.request("GET", "/api/v1/hosts", json={"limit": 10, "offset": 0})

    # Verify params were passed for GET
    call_kwargs = httpx_mock.call_args[1]
    assert call_kwargs["params"] == {"limit": 10, "offset": 0}
