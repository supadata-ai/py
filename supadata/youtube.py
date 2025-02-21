"""YouTube-related operations for Supadata."""

from typing import Dict, Any
from .types import Transcript, TranslatedTranscript, TranscriptChunk


class YouTube:
    """YouTube namespace for Supadata operations."""

    def __init__(self, request_handler):
        """Initialize YouTube namespace.
        
        Args:
            request_handler: Internal request handler from main client
        """
        self._request = request_handler

    def transcript(self, video_id: str, lang: str = None, text: bool = False) -> Transcript:
        """Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
            lang: Language code for preferred transcript language (e.g., 'es' for Spanish)
            text: Whether to return plain text instead of segments

        Returns:
            Transcript object containing content, language and available languages

        Raises:
            SupadataError: If the API request fails
        """
        params = {
            "videoId": video_id,
            "text": str(text).lower()
        }
        
        if lang:
            params["lang"] = lang

        response = self._request("GET", "/youtube/transcript", params=params)

        # Convert chunks if present
        if not text and isinstance(response.get("content"), list):
            response["content"] = [
                TranscriptChunk(
                    text=chunk.get("text", ""),
                    offset=chunk.get("offset", 0),
                    duration=chunk.get("duration", 0),
                    lang=chunk.get("lang", "")
                ) for chunk in response["content"]
            ]

        return Transcript(**response)

    def translate(
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
            SupadataError: If the API request fails
        """
        response = self._request("GET", "/youtube/transcript/translate", params={
            "videoId": video_id,
            "lang": lang,
            "text": str(text).lower()
        })

        # Convert chunks if present
        if not text and isinstance(response.get("content"), list):
            response["content"] = [
                TranscriptChunk(
                    text=chunk.get("text", ""),
                    offset=chunk.get("offset", 0),
                    duration=chunk.get("duration", 0),
                    lang=chunk.get("lang", "")
                ) for chunk in response["content"]
            ]

        return TranslatedTranscript(**response) 