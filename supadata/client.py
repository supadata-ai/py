"""Main Supadata client implementation."""

from typing import Any, Dict

import requests

from supadata.errors import SupadataError

from .web import Web
from .youtube import YouTube


class Supadata:
    """Main Supadata client."""

    def __init__(self, api_key: str, base_url: str = "https://api.supadata.ai/v1"):
        """Initialize Supadata client.

        Args:
            api_key: Your Supadata API key
            base_url: Optional custom API base URL
        """

        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Accept": "application/json"
        })

        # Initialize namespaces
        self.youtube = YouTube(self._request)
        self.web = Web(self._request)

    def _handle_gateway_error(self, status_code: int, error_text: str) -> None:
        """Handle gateway-specific error responses.
        
        Args:
            status_code: HTTP status code
            error_text: Error message from the gateway
            
        Raises:
            SupadataError: With appropriate error details
        """

        try:
            import json
            error_json = json.loads(error_text)
            error_message = error_json.get('message', '')
        except (ValueError, AttributeError):
            error_message = ''

        if status_code == 403:
            raise SupadataError(
                error="invalid-request",
                message="Invalid or missing API key",
                details=error_message or "Please ensure you have provided a valid API key"
            )
        elif status_code == 404:
            raise SupadataError(
                error="not-found",
                message="Endpoint does not exist or resource not found",
                details=error_message or "The API endpoint you are trying to access does not exist"
            )
        elif status_code == 429:
            raise SupadataError(
                error="limit-exceeded",
                message="Limit exceeded",
                details=error_message or "You have exceeded the allowed request rate or quota limits"
            )

    def _camel_to_snake(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dictionary keys from camelCase to snake_case."""
        import re
        def convert(name: str) -> str:
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        if isinstance(d, dict):
            return {convert(k): self._camel_to_snake(v) for k, v in d.items()}
        if isinstance(d, list):
            return [self._camel_to_snake(i) for i in d]
        return d

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make an HTTP request to the Supadata API.

        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            dict: Parsed JSON response

        Raises:
            SupadataError: If a gateway error occurs
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)

        # Handle gateway-specific status codes
        if response.status_code in (403, 404, 429):
            self._handle_gateway_error(response.status_code, response.text)

        # Treat 206 Partial Content as an error for transcript endpoints
        if response.status_code == 206 and ('/transcript' in path):
            error_data = self._camel_to_snake(response.json())
            if 'error' in error_data:
                raise SupadataError(**error_data['error'])
            raise SupadataError(error="transcript-unavailable", message="No Transcript", details="No transcript available")

        try:
            response.raise_for_status()
            return self._camel_to_snake(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = self._camel_to_snake(e.response.json())
                    raise SupadataError(**error_data) from e
                except (ValueError, KeyError):
                    raise e
            raise e 