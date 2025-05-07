"""YouTube-related operations for Supadata."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Literal

from .errors import SupadataError
from .types import (
    Transcript,
    TranscriptChunk,
    TranslatedTranscript,
    YoutubeChannel,
    YoutubePlaylist,
    YoutubeVideo,
    VideoIds,
    BatchJob,
    BatchResults,
)

# Forward declare YouTube for type hints in private classes
class YouTube:
    pass

# --------------------------------------------------------------------------
# Private Classes for API Namespaces
# --------------------------------------------------------------------------

class _Channel:
    def __init__(self, youtube: "YouTube"):
        self._youtube = youtube

    def __call__(self, id: str) -> YoutubeChannel:
        """Get the channel metadata for a YouTube Channel.

        Args:
            id: YouTube Channel ID, URL, or handle (@username)

        Returns:
            YoutubeChannel object containing the metadata.

        Raises:
            SupadataError: If the API request fails.
        """
        response: dict = self._youtube._request(
            "GET", "/youtube/channel", params={"id": id}
        )

        defaults = {
            "id": id, "name": "", "handle": "", "description": "",
            "subscriber_count": 0, "video_count": 0, "thumbnail": "", "banner": ""
        }
        for key, default_value in defaults.items():
            if key not in response:
                response[key] = default_value
        return YoutubeChannel(**response)

    def videos(
        self, id: str, limit: Optional[int] = None, type: Literal["all", "video", "short", "live"] = "all"
    ) -> VideoIds:
        """Get video IDs from a YouTube channel.

        Args:
            id: YouTube Channel ID.
            limit: Max videos to return (default 30, max 5000).
            type: Type of videos ('all', 'video', 'short', 'live'). Default 'all'.

        Returns:
            VideoIds object containing lists of video IDs, short IDs, and live IDs.

        Raises:
            SupadataError: If the API request fails or limit is invalid.
        """
        self._youtube._validate_limit(limit)
        query_params = {"id": id, "type": type}
        if limit:
            query_params["limit"] = limit

        response: dict = self._youtube._request(
            "GET", "/youtube/channel/videos", params=query_params
        )
        return VideoIds(
            video_ids=response.get("video_ids", []),
            short_ids=response.get("short_ids", []),
            live_ids=response.get("live_ids", [])
        )



class _Playlist:
    def __init__(self, youtube: "YouTube"):
        self._youtube = youtube

    def __call__(self, id: str) -> YoutubePlaylist:
        """Gets the playlist metadata for a YouTube public playlist.

        Args:
            id: YouTube playlist ID or URL.

        Returns:
            YoutubePlaylist object containing the metadata.

        Raises:
            SupadataError: If the API request fails.
        """
        response: dict = self._youtube._request(
            "GET", "/youtube/playlist", params={"id": id}
        )

        try:
            last_updated = datetime.fromisoformat(response.pop("last_updated", datetime.now().isoformat()))
        except (ValueError, TypeError):
            last_updated = datetime.now()

        defaults = {
            "id": id, "title": "", "video_count": 0, "view_count": 0,
            "channel": {"id": "", "name": ""}, "description": None
        }
        for key, default_value in defaults.items():
            if key not in response:
                response[key] = default_value
            elif key == "channel" and not isinstance(response[key], dict):
                response[key] = defaults[key]

        return YoutubePlaylist(**response, last_updated=last_updated)

    def videos(self, id: str, limit: Optional[int] = None) -> VideoIds:
        """Get video IDs from a YouTube playlist.

        Args:
            id: YouTube Playlist ID.
            limit: Max videos to return (default 30, max 5000).

        Returns:
            VideoIds object containing lists of video IDs.

        Raises:
            SupadataError: If the API request fails or limit is invalid.
        """
        self._youtube._validate_limit(limit)
        query_params = {"id": id}
        if limit:
            query_params["limit"] = limit
        if type:
            query_params["type"] = type

        response: dict = self._youtube._request(
            "GET", "/youtube/playlist/videos", params=query_params
        )
        return VideoIds(
            video_ids=response.get("video_ids", []),
            short_ids=response.get("short_ids", []),
            live_ids=response.get("live_ids", [])
        )


class _Video:
    def __init__(self, youtube: "YouTube"):
        self._youtube = youtube

    def __call__(self, id: str) -> YoutubeVideo:
        """Get the video metadata for a YouTube video.

        Args:
            id: YouTube video ID or URL.

        Returns:
            YoutubeVideo object containing the metadata.

        Raises:
            SupadataError: If the API request fails.
        """
        response: dict = self._youtube._request("GET", "/youtube/video", params={"id": id})

        try:
            uploaded_time = datetime.fromisoformat(response.pop("upload_date", datetime.now().isoformat()))
        except (ValueError, TypeError):
            uploaded_time = datetime.now()

        defaults = {
            "id": id, "title": "", "description": "", "duration": 0,
            "channel": {"id": "", "name": ""}, "tags": [], "thumbnail": "",
            "view_count": 0, "like_count": 0, "transcript_languages": []
        }
        for key, default_value in defaults.items():
            if key not in response:
                response[key] = default_value
            elif key == "channel" and not isinstance(response[key], dict):
                response[key] = defaults[key]

        return YoutubeVideo(**response, uploaded_date=uploaded_time)

    def batch(
        self,
        video_ids: Optional[List[str]] = None,
        playlist_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> BatchJob:
        """Create a batch job to get metadata from multiple YouTube videos.

        One of video_ids, playlist_id, or channel_id must be provided.

        Args:
            video_ids: Array of YouTube video IDs or URLs.
            playlist_id: YouTube playlist URL or ID.
            channel_id: YouTube channel URL, handle or ID.
            limit: Maximum number of videos to process (default 10, max 5000).

        Returns:
            BatchJob object containing the job ID.

        Raises:
            SupadataError: If the API request fails or input validation fails.
        """
        return self._youtube._create_video_batch(
            video_ids=video_ids,
            playlist_id=playlist_id,
            channel_id=channel_id,
            limit=limit
        )


class _Transcript:
    def __init__(self, youtube: "YouTube"):
        self._youtube = youtube

    def __call__(self, video_id: str, lang: str = None, text: bool = False) -> Transcript:
        """Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID or URL.
            lang: Language code for preferred transcript (e.g., 'es'). Optional.
            text: Return plain text instead of segments. Default False.

        Returns:
            Transcript object containing content, language, and available languages.

        Raises:
            SupadataError: If the API request fails.
        """
        params = {"videoId": video_id, "text": str(text).lower()}
        if lang:
            params["lang"] = lang

        response = self._youtube._request("GET", "/youtube/transcript", params=params)

        content = response.get("content")
        if not text:
            processed_content = [
                TranscriptChunk(**chunk) for chunk in content
            ] if isinstance(content, list) else []
        else:
            processed_content = content if isinstance(content, str) else ""

        # Ensure defaults for optional return fields
        response_lang = response.get("lang", "")
        response_available = response.get("available_langs", [])

        return Transcript(
            content=processed_content,
            lang=response_lang,
            available_langs=response_available
        )

    def translate(self, video_id: str, lang: str, text: bool = False) -> TranslatedTranscript:
        """Get translated transcript for a YouTube video.

        Args:
            video_id: YouTube video ID or URL.
            lang: Target language code (e.g., 'es').
            text: Return plain text instead of segments. Default False.

        Returns:
            TranslatedTranscript object containing the translated content and language.

        Raises:
            SupadataError: If the API request fails.
        """
        response = self._youtube._request(
            "GET",
            "/youtube/transcript/translate",
            params={"videoId": video_id, "lang": lang, "text": str(text).lower()},
        )

        content = response.get("content")
        if not text:
             processed_content = [
                TranscriptChunk(**chunk) for chunk in content
            ] if isinstance(content, list) else []
        else:
            processed_content = content if isinstance(content, str) else ""

        # Ensure target language is set even if API omits it
        response_lang = response.get("lang", lang)

        return TranslatedTranscript(content=processed_content, lang=response_lang)

    def batch(
        self,
        video_ids: Optional[List[str]] = None,
        playlist_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: Optional[int] = None,
        lang: Optional[str] = None,
        text: Optional[bool] = None,
    ) -> BatchJob:
        """Create a batch job to get transcripts from multiple YouTube videos.

        One of video_ids, playlist_id, or channel_id must be provided.

        Args:
            video_ids: Array of YouTube video IDs or URLs.
            playlist_id: YouTube playlist URL or ID.
            channel_id: YouTube channel URL, handle or ID.
            limit: Maximum number of videos to process (default 10, max 5000).
            lang: Preferred language code for transcripts (ISO 639-1).
            text: Return plain text instead of segments. Default False.
        Returns:
            BatchJob object containing the job ID.

        Raises:
            SupadataError: If the API request fails or input validation fails.
        """
        return self._youtube._create_transcript_batch(
            video_ids=video_ids,
            playlist_id=playlist_id,
            channel_id=channel_id,
            limit=limit,
            lang=lang,
            text=text
        )

class _Batch:
    def __init__(self, youtube: "YouTube"):
        self._youtube = youtube

    def get_batch_results(self, job_id: str) -> BatchResults:
        """Get the status and results of a batch job.

        Args:
            job_id: The ID of the batch job.

        Returns:
            BatchResults object containing status, results, and stats.

        Raises:
            SupadataError: If the API request fails.
        """
        response = self._youtube._request("GET", f"/youtube/batch/{job_id}")
        
        # Reverted: Pass raw response directly to BatchResults constructor.
        # The BatchResults.__post_init__ method in types.py will handle parsing.
        return BatchResults(**response)


# --------------------------------------------------------------------------
# Main YouTube Class
# --------------------------------------------------------------------------

class YouTube:
    """Provides access to YouTube data retrieval and processing operations."""

    def __init__(self, request_handler: Callable[[str, str, Any], Dict[str, Any]]):
        """Initialize YouTube operations.

        Args:
            request_handler: Internal request handler from main client.
        """
        self._request = request_handler
        # No caching of private class instances

    # --- Validation and Core Helpers ---

    def _validate_limit(self, limit: int | None = None) -> None:
        """Validate the limit parameter."""
        if limit is None:
            return
        if not isinstance(limit, int) or limit <= 0 or limit > 5000:
            raise SupadataError(
                error="invalid-request",
                message="Invalid limit provided.",
                details="Limit must be a positive integer up to 5000.",
            )

    def _validate_batch_sources(
        self,
        video_ids: Optional[List[str]] = None,
        playlist_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate batch source parameters and construct the payload."""
        payload = {}
        sources = 0
        if video_ids:
            payload["videoIds"] = video_ids
            sources += 1
        if playlist_id:
            payload["playlistId"] = playlist_id
            sources += 1
        if channel_id:
            payload["channelId"] = channel_id
            sources += 1

        if sources == 0:
            raise SupadataError(
                error="invalid-request", message="Missing source.",
                details="One of video_ids, playlist_id, or channel_id must be provided."
            )
        if sources > 1:
            raise SupadataError(
                error="invalid-request", message="Multiple sources.",
                details="Only one of video_ids, playlist_id, or channel_id can be provided."
            )

        if limit is not None:
            self._validate_limit(limit)
            # Only add limit if source is playlist or channel
            if playlist_id or channel_id:
                 payload["limit"] = limit
            elif video_ids and limit is not None:
                 # Optionally warn or ignore limit if only video_ids are provided?
                 # Current behavior: limit is ignored by API if only video_ids are sent.
                 pass


        return payload

    def _create_batch_job(self, endpoint: str, payload: dict) -> BatchJob:
        """Internal helper to create any batch job."""
        response = self._request("POST", endpoint, json=payload)
        return BatchJob(**response)

    # --- Batch Creation Helpers (used by private classes) ---

    def _create_video_batch(
        self, video_ids=None, playlist_id=None, channel_id=None, limit=None
    ) -> BatchJob:
        """Create a batch job for video metadata."""
        payload = self._validate_batch_sources(video_ids, playlist_id, channel_id, limit)
        return self._create_batch_job("/youtube/video/batch", payload)

    def _create_transcript_batch(
        self, video_ids=None, playlist_id=None, channel_id=None, limit=None, lang=None, text=None
    ) -> BatchJob:
        """Create a batch job for transcripts."""
        payload = self._validate_batch_sources(video_ids, playlist_id, channel_id, limit)
        if lang:
            payload["lang"] = lang
        if text:
            payload["text"] = str(text).lower()
        return self._create_batch_job("/youtube/transcript/batch", payload)

    # --------------------------------------------------------------------------
    # Public API Methods (Direct Access)
    # --------------------------------------------------------------------------

    # Note: video() and transcript() direct calls are implicitly handled
    # by the __call__ methods of the objects returned by the properties.

    def translate(
        self, video_id: str, lang: str, text: bool = False
    ) -> TranslatedTranscript:
        """Get translated transcript for a YouTube video.

        This is a convenience method, equivalent to `youtube.transcript.translate(...)`.

        Args:
            video_id: YouTube video ID or URL.
            lang: Target language code (e.g., 'es').
            text: Return plain text instead of segments. Default False.

        Returns:
            TranslatedTranscript object containing translated content.

        Raises:
            SupadataError: If the API request fails.
        """
        # Creates a temporary _Transcript instance to perform the action
        return _Transcript(self).translate(video_id, lang, text)

    # --------------------------------------------------------------------------
    # Public API (Properties returning callable/namespace objects)
    # --------------------------------------------------------------------------

    @property
    def channel(self) -> _Channel:
        """Access YouTube channel operations.

        Call directly with a channel ID/URL/handle to get metadata,
        or access methods like `.videos()` or `.batch()`.

        Example:
            ```python
            channel_info = supadata.youtube.channel(id="UC_...")
            videos = supadata.youtube.channel.videos(id="UC_...")
            batch_job = supadata.youtube.channel.batch(channel_id="UC_...")
            ```
        Returns:
            An object for channel operations.
        """
        return _Channel(self) # Return a new instance each time

    @property
    def playlist(self) -> _Playlist:
        """Access YouTube playlist operations.

        Call directly with a playlist ID/URL to get metadata,
        or access methods like `.videos()`.

        Example:
            ```python
            playlist_info = supadata.youtube.playlist(id="PL_...")
            videos = supadata.youtube.playlist.videos(id="PL_...")
            ```
        Returns:
            An object for playlist operations.
        """
        return _Playlist(self) # Return a new instance each time

    @property
    def video(self) -> _Video:
        """Access YouTube video operations.

        Call directly with a video ID/URL to get metadata,
        or access methods like `.batch()`.

        Example:
            ```python
            video_info = supadata.youtube.video(id="dQw4w9WgXcQ")
            batch_job = supadata.youtube.video.batch(video_ids=["dQw..."])
            ```
        Returns:
            An object for video operations.
        """
        return _Video(self) # Return a new instance each time

    @property
    def transcript(self) -> _Transcript:
        """Access YouTube transcript operations.

        Call directly with a video ID/URL to get its transcript,
        or access methods like `.translate()` or `.batch()`.

        Example:
            ```python
            transcript = supadata.youtube.transcript(video_id="dQw4w9WgXcQ")
            translated = supadata.youtube.transcript.translate(video_id="dQw...", lang="es")
            batch_job = supadata.youtube.transcript.batch(video_ids=["dQw..."])
            ```
        Returns:
            An object for transcript operations.
        """
        return _Transcript(self) # Return a new instance each time

    @property
    def batch(self) -> _Batch:
        """Access YouTube batch result operations.

        Used to access methods like `.get_batch_results()`. Batch jobs themselves
        are created via `.video.batch(...)`, `.transcript.batch(...)`, etc.

        Example:
            ```python
            batch_results = supadata.youtube.batch.get_batch_results("job_id_here")
            ```
        Returns:
            An object for batch result operations.
        """
        return _Batch(self) # Return a new instance each time

