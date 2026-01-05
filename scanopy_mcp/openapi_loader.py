"""OpenAPI spec loader with TTL cache."""

import time

import httpx


class OpenAPILoader:
    """Load and cache OpenAPI specification from a URL."""

    def __init__(self, url: str, ttl_seconds: int = 600):
        """Initialize the loader.

        Args:
            url: URL to fetch OpenAPI spec from.
            ttl_seconds: Cache time-to-live in seconds.
        """
        self.url = url
        self.ttl_seconds = ttl_seconds
        self._cache = None
        self._loaded_at = 0.0

    def load(self) -> dict:
        """Load OpenAPI spec, using cache if fresh.

        Returns:
            OpenAPI specification as a dictionary.
        """
        now = time.time()
        if self._cache and (now - self._loaded_at) < self.ttl_seconds:
            return self._cache

        resp = httpx.get(self.url, timeout=5)
        resp.raise_for_status()
        self._cache = resp.json()
        self._loaded_at = now
        return self._cache
