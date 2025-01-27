"""Web-related operations for Supadata."""

from .types import Scrape, Map


class Web:
    """Web namespace for Supadata operations."""

    def __init__(self, request_handler):
        """Initialize Web namespace.
        
        Args:
            request_handler: Internal request handler from main client
        """
        self._request = request_handler

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