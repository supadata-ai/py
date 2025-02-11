"""Main Supadata client implementation."""

from typing import Dict, Any
import requests

from .youtube import YouTube
from .web import Web
from .types import Error
from .errors import SupadataError, map_gateway_error


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

    def _request(self, method: str, path: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Make an HTTP request to the Supadata API.

        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            dict: Parsed JSON response

        Raises:
            SupadataError: If the API request fails with a gateway error
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)

        # Treat 206 Partial Content as an error for transcript endpoints
        if response.status_code == 206 and ('/transcript' in path):
            error_data = self._camel_to_snake(response.json())
            if 'error' in error_data:
                raise SupadataError(
                    code=error_data['error'].get('code', 'unknown'),
                    title=error_data['error'].get('title', 'Unknown Error'),
                    description=error_data['error'].get('description', str(error_data['error'])),
                    documentation_url=error_data['error'].get('documentation_url')
                )
            raise SupadataError(
                code='transcript-unavailable',
                title='Transcript Unavailable',
                description='No transcript available for this video'
            )

        # Handle error responses
        if 400 <= response.status_code < 600:
            try:
                # Try to parse as JSON first
                error_data = self._camel_to_snake(response.json())
                if isinstance(error_data, dict):
                    if 'error' in error_data:
                        error = error_data['error']
                        raise SupadataError(
                            code=error.get('code', 'unknown'),
                            title=error.get('title', 'Unknown Error'),
                            description=error.get('description', str(error)),
                            documentation_url=error.get('documentation_url')
                        )
                    raise SupadataError(
                        code='unknown',
                        title='Unknown Error',
                        description=str(error_data)
                    )
            except ValueError:
                # If not JSON, treat as gateway error
                if response.status_code in (403, 404, 429):
                    raise map_gateway_error(response.status_code, response.text)
                response.raise_for_status()

        return self._camel_to_snake(response.json()) 