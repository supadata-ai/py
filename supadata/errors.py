"""Custom exceptions for Supadata SDK."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SupadataError(Exception):
    """Base exception for all Supadata errors.
    
    Attributes:
        error: Error code identifying the type of error (e.g., 'video-not-found')
        message: Human readable error title
        details: Detailed error description
        documentation_url: URL to error documentation
    """
    error: str
    message: str
    details: str
    documentation_url: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.error:
            parts.append(f"error: {self.error}")
        if self.details:
            parts.append(f"details: {self.details}")
        if self.documentation_url:
            parts.append(f"documentationUrl: {self.documentation_url}")
        return " | ".join(parts) 