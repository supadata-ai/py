"""Main Supadata client implementation."""

from typing import Dict, Any
import requests

from .youtube import YouTube
from .web import Web
from .types import Error


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
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)

        try:
            response.raise_for_status()
            return self._camel_to_snake(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = self._camel_to_snake(e.response.json())
                    error = Error(**error_data)
                    raise requests.exceptions.HTTPError(error) from e
                except (ValueError, TypeError):
                    pass
            raise 