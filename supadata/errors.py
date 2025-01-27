"""Custom exceptions for Supadata SDK."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SupadataError(Exception):
    """Base exception for all Supadata errors.
    
    Attributes:
        code: Error code identifying the type of error (e.g., 'video-not-found')
        title: Human readable error title
        description: Detailed error description
        documentation_url: URL to error documentation
    """
    code: str
    title: str
    description: str
    documentation_url: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.description]
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.documentation_url:
            parts.append(f"Documentation: {self.documentation_url}")
        return " | ".join(parts) 