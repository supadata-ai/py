"""Main Supadata client implementation."""

from typing import Any, Dict, Union
import importlib.metadata

import requests

from supadata.errors import SupadataError

from .web import Web
from .youtube import YouTube
from .types import Transcript, BatchJob


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
            "Accept": "application/json",
            "User-Agent": f"Supadata-Python-SDK/{importlib.metadata.version('supadata')}"
        })

        # Initialize namespaces
        self.youtube = YouTube(self._request)
        self.web = Web(self._request)

    def transcript(
        self,
        url: str,
        lang: str = None,
        text: bool = False,
        chunk_size: int = None,
        mode: str = "auto"
    ) -> Union[Transcript, BatchJob]:
        """Get transcript from a video URL.

        Args:
            url: Video URL from supported platforms (YouTube, TikTok, Twitter) or file URL
            lang: Optional preferred language code (ISO 639-1)
            text: Return plain text transcript instead of timestamped chunks
            chunk_size: Maximum characters per transcript chunk
            mode: Transcript retrieval mode - "native", "auto", or "generate"

        Returns:
            Transcript object if transcript is available immediately,
            or BatchJob with job_id for asynchronous processing

        Raises:
            SupadataError: If the transcript request fails
        """
        params = {"url": url, "mode": mode}
        
        if lang is not None:
            params["lang"] = lang
        if text:
            params["text"] = str(text).lower()
        if chunk_size is not None:
            params["chunkSize"] = chunk_size

        response = self._request("GET", "/transcript", params=params)
        
        # Check if response contains a job_id (async processing)
        if "job_id" in response:
            return BatchJob(job_id=response["job_id"])
        
        # Otherwise, return the transcript directly
        return Transcript(**response)

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

        # Treat 206 Partial Content as an error for transcript endpoints
        if response.status_code == 206 and ('/transcript' in path):
            error_data = self._camel_to_snake(response.json())
            if 'error' in error_data:
                raise SupadataError(**error_data)
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