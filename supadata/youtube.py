"""YouTube-related operations for Supadata."""

from datetime import datetime
from typing import Any, Callable, Dict, List

from .errors import SupadataError
from .types import (
    Transcript,
    TranscriptChunk,
    TranslatedTranscript,
    YoutubeChannel,
    YoutubePlaylist,
    YoutubeVideo,
)


class YouTube:
    """YouTube namespace for Supadata operations."""

    def __init__(self, request_handler: Callable[[str, str, Any], Dict[str, Any]]):
        """Initialize YouTube namespace.

        Args:
            request_handler: Internal request handler from main client
        """
        self._request = request_handler
        self._channel_instance = None
        self._playlist_instance = None

    def transcript(
        self, video_id: str, lang: str = None, text: bool = False
    ) -> Transcript:
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
        params = {"videoId": video_id, "text": str(text).lower()}

        if lang:
            params["lang"] = lang

        response = self._request("GET", "/youtube/transcript", params=params)

        # Convert chunks if present
        content = response.get("content")
        if not text:
            if isinstance(content, list):
                processed_content = []
                for chunk in content:
                    chunk_obj = TranscriptChunk(
                        text=chunk.get("text", ""),
                        offset=chunk.get("offset", 0),
                        duration=chunk.get("duration", 0),
                        lang=chunk.get("lang", ""),
                    )
                    processed_content.append(chunk_obj)
            else:
                processed_content = []
        else:
            processed_content = content if isinstance(content, str) else ""

        response["content"] = processed_content
        
        if "lang" not in response:
            response["lang"] = ""
        if "available_langs" not in response:
            response["available_langs"] = []

        return Transcript(**response)

    def translate(
        self, video_id: str, lang: str, text: bool = False
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
        response = self._request(
            "GET",
            "/youtube/transcript/translate",
            params={"videoId": video_id, "lang": lang, "text": str(text).lower()},
        )

        # Convert chunks if present
        content = response.get("content")
        if not text:
            if isinstance(content, list):
                processed_content = []
                for chunk in content:
                    chunk_obj = TranscriptChunk(
                        text=chunk.get("text", ""),
                        offset=chunk.get("offset", 0),
                        duration=chunk.get("duration", 0),
                        lang=chunk.get("lang", ""),
                    )
                    processed_content.append(chunk_obj)
            else:
                processed_content = []
        else:
            processed_content = content if isinstance(content, str) else ""

        response["content"] = processed_content
        
        # Add default value for missing lang field
        if "lang" not in response:
            response["lang"] = lang

        return TranslatedTranscript(**response)

    def video(self, id: str) -> YoutubeVideo:
        """Get the video metadata for a YouTube video.

        Args:
            id: YouTube video ID

        Returns:
            YoutubeVideo object containing the metadata

        Raises:
            SupadataError: If the API request fails
        """
        response: dict = self._request("GET", "/youtube/video", params={"id": id})
        
        # Safely convert upload_date with fallback
        try:
            uploaded_time = datetime.fromisoformat(response.pop("upload_date", datetime.now().isoformat()))
        except (ValueError, TypeError):
            uploaded_time = datetime.now()
        
        # Ensure all required fields have defaults
        defaults = {
            "id": id,
            "title": "",
            "description": "",
            "duration": 0,
            "channel": {"id": "", "name": ""},
            "tags": [],
            "thumbnail": "",
            "view_count": 0,
            "like_count": 0,
            "transcript_languages": [],
        }
        
        # Apply defaults for any missing fields
        for key, default_value in defaults.items():
            if key not in response:
                response[key] = default_value
            elif key == "channel" and not isinstance(response[key], dict):
                response[key] = defaults[key]

        return YoutubeVideo(**response, uploaded_date=uploaded_time)

    @property
    def channel(self):
        """Channel namespace for YouTube operations."""
        if self._channel_instance is None:
            self._channel_instance = self._Channel(self)
        return self._channel_instance

    @property
    def playlist(self):
        """Playlist namespace for YouTube operations."""
        if self._playlist_instance is None:
            self._playlist_instance = self._Playlist(self)
        return self._playlist_instance

    def _validate_limit(self, limit: int | None = None) -> None:
        if limit is None:
            return
        elif not isinstance(limit, int) or limit <= 0 or limit > 5000:
            raise SupadataError(
                error="invalid-request",
                message="Invalid limit provided",
                details="You provided a limit in an invalid format or amount.",
            )

    class _Channel:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def __call__(self, id: str) -> YoutubeChannel:
            """Get the channel metadata for a YouTube Channel.

            Args:
                id: YouTube Channel ID

            Returns:
                YoutubeChannel object containing the metadata

            Raises:
                SupadataError: If the API request fails
            """
            response: dict = self._youtube._request(
                "GET", "/youtube/channel", params={"id": id}
            )
            
            # Ensure all required fields exist with defaults
            defaults = {
                "id": id,
                "name": "",
                "handle": "",
                "description": "",
                "subscriber_count": 0,
                "video_count": 0,
                "thumbnail": "",
                "banner": "",
            }
            
            # Apply defaults for any missing fields
            for key, default_value in defaults.items():
                if key not in response:
                    response[key] = default_value

            return YoutubeChannel(**response)

        def videos(self, id: str, limit: int | None = None) -> List[str]:
            """Get a list of video IDs from a YouTube channel.

            Args:
                id: YouTube Channel ID
                limit: The limit of videos to be returned. None will
                    return the default (30 videos)

            Returns:
                A list of video IDs.

            Raises:
                SupadataError: If the API request fails
            """
            self._youtube._validate_limit(limit)
            query_params = {"id": id}
            if limit:
                query_params["limit"] = limit

            response: dict = self._youtube._request(
                "GET", "/youtube/channel/videos", params=query_params
            )
            return response.get("video_ids", [])

    class _Playlist:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def __call__(self, id: str) -> YoutubePlaylist:
            """Gets the playlist metadata for a YouTube public playlist.

            Args:
                id: YouTube playlist id

            Returns:
                YoutubePlaylist object containing the metadata

            Raises:
                SupadataError: If the API request fails
            """
            response: dict = self._youtube._request(
                "GET", "/youtube/playlist", params={"id": id}
            )
            
            # Safely convert last_updated with fallback
            try:
                last_updated = datetime.fromisoformat(response.pop("last_updated", datetime.now().isoformat()))
            except (ValueError, TypeError):
                last_updated = datetime.now()
            
            # Ensure all required fields exist with defaults
            defaults = {
                "id": id,
                "title": "",
                "video_count": 0,
                "view_count": 0,
                "channel": {"id": "", "name": ""},
                "description": None
            }
            
            # Apply defaults for any missing fields
            for key, default_value in defaults.items():
                if key not in response:
                    response[key] = default_value
                elif key == "channel" and not isinstance(response[key], dict):
                    response[key] = defaults[key]

            return YoutubePlaylist(**response, last_updated=last_updated)

        def videos(self, id: str, limit: int | None = None) -> List[str]:
            """Get a list of the IDs of the list of video IDs from a YouTube playlist.

            Args:
                id: YouTube Playlist ID
                limit: The limit of videos to be returned. None will
                    return the default (30 videos)

            Returns:
                A list of video IDs.

            Raises:
                SupadataError: If the API request fails
            """
            self._youtube._validate_limit(limit)
            query_params = {"id": id}
            if limit:
                query_params["limit"] = limit
                
            response: dict = self._youtube._request(
                "GET", "/youtube/playlist/videos", params=query_params
            )
            return response.get("video_ids", [])
