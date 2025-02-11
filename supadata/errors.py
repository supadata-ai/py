"""Custom exceptions for Supadata SDK."""

from typing import Optional, Dict, TypedDict
from dataclasses import dataclass


class GatewayErrorInfo(TypedDict):
    error: str
    message: str
    details: str


GATEWAY_STATUS_ERRORS: Dict[int, GatewayErrorInfo] = {
    403: {
        'error': 'invalid-request',
        'message': 'Invalid or missing API key',
        'details': 'Please ensure you have provided a valid API key'
    },
    404: {
        'error': 'invalid-request',
        'message': 'Endpoint does not exist',
        'details': 'The API endpoint you are trying to access does not exist'
    },
    429: {
        'error': 'limit-exceeded',
        'message': 'Limit exceeded',
        'details': 'You have exceeded the allowed request rate or quota limits'
    }
}


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


def map_gateway_error(status_code: int, error_text: str) -> SupadataError:
    """Map gateway errors to SupadataError instances.

    Args:
        status_code: HTTP status code from the gateway
        error_text: Error text from the response

    Returns:
        SupadataError: Mapped error with appropriate details
    """
    if status_code in GATEWAY_STATUS_ERRORS:
        error_info = GATEWAY_STATUS_ERRORS[status_code]
        return SupadataError(
            code=error_info['error'],
            title=error_info['message'],
            description=error_text or error_info['details']
        )

    # Default error if status code is not recognized
    return SupadataError(
        code='internal-error',
        title='An unexpected error occurred',
        description=error_text
    ) 