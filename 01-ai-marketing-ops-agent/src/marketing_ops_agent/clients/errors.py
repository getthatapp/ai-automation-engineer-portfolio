"""Typed service client exceptions."""

import httpx


class ServiceClientError(Exception):
    """Base error for external service client failures."""


class ServiceTimeoutError(ServiceClientError):
    """Raised when an external service call times out."""


class ServiceConnectionError(ServiceClientError):
    """Raised when a request cannot reach the external service."""


class ServiceDecodeError(ServiceClientError):
    """Raised when a service response cannot be decoded into the expected shape."""


class ServiceResponseError(ServiceClientError):
    """Raised for non-successful HTTP responses."""

    def __init__(self, *, status_code: int, response_text: str) -> None:
        """Initialize the HTTP response error with response context.

        Args:
            status_code: HTTP status code.
            response_text: Response body text, truncated in the error message.
        """
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Service returned HTTP {status_code}: {response_text[:300]}")

    @classmethod
    def from_response(cls, response: httpx.Response) -> "ServiceResponseError":
        """Create an error from an `httpx.Response`.

        Args:
            response: Non-successful HTTP response.

        Returns:
            Service response error containing status and body text.
        """
        return cls(status_code=response.status_code, response_text=response.text)


class RetryableServiceResponseError(ServiceResponseError):
    """Raised for HTTP responses that should be retried."""


class GraphQLResponseError(ServiceClientError):
    """Raised when a GraphQL response contains an `errors` field."""

    def __init__(self, errors: object) -> None:
        """Initialize the GraphQL response error with raw error content.

        Args:
            errors: Raw GraphQL `errors` payload.
        """
        self.errors = errors
        super().__init__(f"GraphQL response contained errors: {_format_errors(errors)}")


def _format_errors(errors: object) -> str:
    """Format GraphQL errors into compact text.

    Args:
        errors: Raw GraphQL error payload.

    Returns:
        Semicolon-separated messages when available, otherwise `str(errors)`.
    """
    if isinstance(errors, list):
        messages: list[str] = []
        for error in errors:
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str):
                    messages.append(message)
        if messages:
            return "; ".join(messages)
    return str(errors)
