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
            params: Optional all parameters (will be split into path/query/body).

        Returns:
            Parsed JSON response.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        params = params or {}

        # Extract path params (those with {placeholder} in path)
        path_params = {}
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in path:
                path_params[key] = value
                path = path.replace(placeholder, str(value))

        # Remaining params go to query (GET) or body (POST/PUT/PATCH/DELETE)
        other_params = {k: v for k, v in params.items() if k not in path_params}

        url = f"{self.base_url}{path}"

        with httpx.Client(timeout=self.timeout_s) as client:
            if method.upper() == "GET":
                # GET: use query params, no body
                resp = client.request(
                    method, url, headers=self._headers(), params=other_params or None
                )
            else:
                # POST/PUT/PATCH/DELETE: use JSON body (prefer explicit json)
                body = json if json is not None else (other_params or None)
                resp = client.request(
                    method, url, headers=self._headers(), json=body
                )

            resp.raise_for_status()
            return resp.json()
