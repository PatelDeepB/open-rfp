"""Domain exceptions for OpenRFP.

Provides explicit, typed hierarchy for parser, retrieval, drafting, and storage errors.
"""

from typing import Optional


class OpenRfpError(Exception):
    """Base exception for all OpenRFP errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ParseError(OpenRfpError):
    """Raised when an RFP document fails to parse or extract requirements."""


class DocumentNotFoundError(OpenRfpError):
    """Raised when a specified document or file cannot be located."""


class KnowledgeBaseError(OpenRfpError):
    """Raised when knowledge indexing or retrieval fails."""


class DraftingError(OpenRfpError):
    """Raised when proposal synthesis fails."""


class ValidationError(OpenRfpError):
    """Raised when input parameters fail domain validation rules."""


class StorageError(OpenRfpError):
    """Raised when persisting or loading records fails."""
