"""Shared HTTP behavior for typed service clients."""

from types import TracebackType
from typing import Self, cast

import httpx

from marketing_ops_agent.clients.errors import (
    RetryableServiceResponseError,
    ServiceConnectionError,
    ServiceDecodeError,
    ServiceResponseError,
    ServiceTimeoutError,
)
from marketing_ops_agent.config import AppConfig, load_config
from marketing_ops_agent.utils.retry import RetryConfig, retry_async


class AsyncHttpServiceClient:
    """Small `httpx` wrapper with timeout, retry and error translation."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float | None = None,
        retry_config: RetryConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize shared HTTP client behavior.

        Args:
            base_url: Base URL used for relative request paths.
            timeout_seconds: Per-call timeout override.
            retry_config: Retry policy for timeout, transport and 5xx failures.
            http_client: Optional injected `httpx.AsyncClient` for tests.
            config: Optional application configuration.
        """
        resolved_config = config or load_config()
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds or resolved_config.request_timeout_seconds
        self._retry_config = retry_config or resolved_config.retry_config()
        self._http_client = http_client or httpx.AsyncClient()
        self._owns_http_client = http_client is None

    async def __aenter__(self) -> Self:
        """Enter the async client context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the async client context and close owned HTTP resources."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client when this instance owns it."""

        if self._owns_http_client:
            await self._http_client.aclose()

    async def request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: object | None = None,
    ) -> object:
        """Send an HTTP request with retry and return decoded JSON.

        Args:
            method: HTTP method.
            path: Relative or absolute request path.
            json_body: Optional JSON request body.

        Returns:
            Decoded JSON response body.

        Raises:
            ServiceDecodeError: If the response body is not valid JSON.
            ServiceClientError: If the request fails after retries.
        """

        response = await retry_async(
            lambda: self._send(method, path, json_body=json_body),
            config=self._retry_config,
            retry_on=(
                ServiceTimeoutError,
                ServiceConnectionError,
                RetryableServiceResponseError,
            ),
        )

        try:
            return cast(object, response.json())
        except ValueError as exc:
            raise ServiceDecodeError("Service returned invalid JSON") from exc

    async def _send(self, method: str, path: str, *, json_body: object | None) -> httpx.Response:
        """Send one HTTP request and translate transport/HTTP failures.

        Args:
            method: HTTP method.
            path: Relative or absolute request path.
            json_body: Optional JSON request body.

        Returns:
            Successful HTTP response.

        Raises:
            ServiceTimeoutError: If the call times out.
            ServiceConnectionError: If transport fails.
            RetryableServiceResponseError: If a 5xx response is returned.
            ServiceResponseError: If a 4xx response is returned.
        """
        url = self._build_url(path)
        try:
            response = await self._http_client.request(
                method,
                url,
                json=json_body,
                timeout=self._timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise ServiceTimeoutError(f"{method} {url} timed out") from exc
        except httpx.TransportError as exc:
            raise ServiceConnectionError(f"{method} {url} failed: {exc}") from exc

        if response.status_code >= 500:
            raise RetryableServiceResponseError.from_response(response)
        if response.status_code >= 400:
            raise ServiceResponseError.from_response(response)
        return response

    def _build_url(self, path: str) -> str:
        """Build a request URL from a relative or absolute path.

        Args:
            path: Relative path or absolute URL.

        Returns:
            Absolute request URL.
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}{normalized_path}"
