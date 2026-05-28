"""Errors for the optional LLM interpretation layer."""


class LLMInterpretationError(Exception):
    """Base error for LLM interpretation failures."""


class LLMProviderUnavailableError(LLMInterpretationError):
    """Raised when an LLM provider cannot serve an interpretation request."""


class LLMProviderResponseError(LLMInterpretationError):
    """Raised when an LLM provider returns invalid structured output."""
