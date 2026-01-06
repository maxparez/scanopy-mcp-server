"""HTTP client for Scanopy API."""

import httpx


class ScanopyClient:
    """HTTP client for making authenticated requests to Scanopy API."""

    def __init__(self, base_url: str, api_key: str, timeout_s: float = 10.0):
        """Initialize the client.

        Args:
            base_url: Base URL of the Scanopy API.
            api_key: API key for authentication (raw token, no "Bearer" prefix).
            timeout_s: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def _headers(self) -> dict:
        """Build request headers with authentication.

        Returns:
            Dictionary of HTTP headers.
        """
        return {"Authorization": f"Bearer {self.api_key}"}

    def request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Make an HTTP request to the Scanopy API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: Request path with {param} placeholders.
            json: Optional JSON body for request.
            params: Optional path parameters to substitute in {placeholders}.

        Returns:
            Parsed JSON response.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        # Substitute path parameters (e.g., {id} -> actual value)
        if params:
            for key, value in params.items():
                placeholder = f"{{{key}}}"
                if placeholder in path:
                    path = path.replace(placeholder, str(value))

        url = f"{self.base_url}{path}"

        with httpx.Client(timeout=self.timeout_s) as client:
            # For GET requests, send remaining args as query params
            if method.upper() == "GET" and json:
                resp = client.request(
                    method, url, headers=self._headers(), params=json
                )
            else:
                resp = client.request(method, url, headers=self._headers(), json=json)

            resp.raise_for_status()
            return resp.json()
