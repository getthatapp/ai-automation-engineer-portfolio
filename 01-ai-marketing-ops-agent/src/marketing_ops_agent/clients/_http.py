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
        resolved_config = config or load_config()
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds or resolved_config.request_timeout_seconds
        self._retry_config = retry_config or resolved_config.retry_config()
        self._http_client = http_client or httpx.AsyncClient()
        self._owns_http_client = http_client is None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
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
        """Send a request and return decoded JSON."""

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
        if path.startswith("http://") or path.startswith("https://"):
            return path
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}{normalized_path}"
