"""Conservative redaction helpers for local ingestion payloads."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "[REDACTED]"

_SECRET_KEY_PATTERN = re.compile(
    r"(?i)(password|passwd|pwd|token|secret|api[_-]?key|authorization|credential)"
)
_KEYED_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|authorization|credential)"
    r"(\s*[=:]\s*)"
    r"([^,\s;]+)"
)
_AUTHORIZATION_BEARER_PATTERN = re.compile(
    r"(?i)\b(authorization)(\s*[=:]\s*)bearer\s+[A-Za-z0-9._~+/=-]+"
)
_BEARER_SECRET_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")


def is_secret_key(value: str) -> bool:
    """Return whether a key name looks credential-related.

    Args:
        value: Mapping key text to inspect.

    Returns:
        `True` when the key name is obviously secret-like.
    """
    return bool(_SECRET_KEY_PATTERN.search(value))


def redact_text(value: str) -> str:
    """Redact obvious inline credential values from text.

    Args:
        value: Raw text.

    Returns:
        Text with common credential shapes replaced.
    """
    redacted = _AUTHORIZATION_BEARER_PATTERN.sub(r"\1\2Bearer [REDACTED]", value)
    redacted = _KEYED_SECRET_PATTERN.sub(r"\1\2[REDACTED]", redacted)
    return _BEARER_SECRET_PATTERN.sub("Bearer [REDACTED]", redacted)


def sanitize_value(value: Any) -> Any:
    """Recursively redact secret-like keys and values.

    Args:
        value: Arbitrary JSON-compatible value.

    Returns:
        Sanitized value with conservative redaction applied.
    """
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for raw_key, raw_item in value.items():
            key = redact_text(str(raw_key))
            sanitized[key] = REDACTED if is_secret_key(str(raw_key)) else sanitize_value(raw_item)
        return sanitized
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [sanitize_value(item) for item in value]
    return value


def sanitize_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    """Sanitize a string-keyed mapping.

    Args:
        value: Mapping to sanitize.

    Returns:
        Sanitized dictionary.
    """
    sanitized = sanitize_value(value)
    if isinstance(sanitized, dict):
        return sanitized
    return {}
