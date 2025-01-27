"""Main Supadata client implementation."""

from typing import Dict, Any
import requests
from dataclasses import asdict

from .types import (
    Transcript,
    TranslatedTranscript,
    TranscriptChunk,
    Scrape,
    Map,
    Error,
)


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

    def get_transcript(self, video_id: str, text: bool = False) -> Transcript:
        """Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
            text: Whether to return plain text instead of segments

        Returns:
            Transcript object containing content, language and available languages

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._request("GET", "/youtube/transcript", params={
            "videoId": video_id,
            "text": text
        })

        # Convert chunks if present
        if not text and isinstance(response["content"], list):
            response["content"] = [
                TranscriptChunk(**chunk) for chunk in response["content"]
            ]

        return Transcript(**response)

    def translate_transcript(
        self,
        video_id: str,
        lang: str,
        text: bool = False
    ) -> TranslatedTranscript:
        """Get translated transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
            lang: Target language code (e.g., 'es' for Spanish)
            text: Whether to return plain text instead of segments

        Returns:
            TranslatedTranscript object containing translated content

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._request("GET", "/youtube/transcript/translate", params={
            "videoId": video_id,
            "lang": lang,
            "text": text
        })

        # Convert chunks if present
        if not text and isinstance(response["content"], list):
            response["content"] = [
                TranscriptChunk(**chunk) for chunk in response["content"]
            ]

        return TranslatedTranscript(**response)

    def scrape(self, url: str) -> Scrape:
        """Scrape content from a web page.

        Args:
            url: URL to scrape

        Returns:
            Scrape object containing the extracted content

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._request("GET", "/web/scrape", params={"url": url})
        return Scrape(**response)

    def map(self, url: str) -> Map:
        """Generate a site map for a website.

        Args:
            url: Base URL to map

        Returns:
            Map object containing discovered URLs

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._request("GET", "/web/map", params={"url": url})
        return Map(**response)

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