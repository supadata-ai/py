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
        self._video_instance = None
        self._transcript_instance = None
        self._batch_instance = None

    def _validate_batch_sources(
        self,
        video_ids: Optional[List[str]] = None,
        playlist_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate batch source parameters and construct the payload.

        Args:
            video_ids: Array of YouTube video IDs or URLs.
            playlist_id: YouTube playlist URL or ID.
            channel_id: YouTube channel URL, handle or ID.
            limit: Maximum number of videos to process.

        Returns:
            Dict containing the validated payload.

        Raises:
            SupadataError: If validation fails.
        """
        payload = {}
        if video_ids:
            payload["videoIds"] = video_ids
        if playlist_id:
            payload["playlistId"] = playlist_id
        if channel_id:
            payload["channelId"] = channel_id

        if not payload:
            raise SupadataError(
                error="invalid-request",
                message="Missing source",
                details="One of video_ids, playlist_id, or channel_id must be provided.",
            )

        if len(payload) > 1:
            raise SupadataError(
                error="invalid-request",
                message="Multiple sources",
                details="Only one of video_ids, playlist_id, or channel_id can be provided.",
            )

        if limit is not None:
            self._validate_limit(limit)
            payload["limit"] = limit

        return payload

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
        # Delegate to _Transcript.__call__
        if self._transcript_instance is None:
            self._transcript_instance = self._Transcript(self)
        return self._transcript_instance(video_id, lang, text)

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
        # Delegate to _Transcript.translate
        if self._transcript_instance is None:
            self._transcript_instance = self._Transcript(self)
        return self._transcript_instance.translate(video_id, lang, text)

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
    def channel(self) -> "_Channel":
        """Channel namespace for YouTube operations.
        
        Returns:
            Channel handler that can be called with an ID to get channel metadata.
            
        Example:
            ```python
            channel = supadata.youtube.channel("UC_9-kyTW8ZkZNDHQJ6FgpwQ")
            ```
        """
        if self._channel_instance is None:
            self._channel_instance = self._Channel(self)
        return self._channel_instance

    @property
    def playlist(self) -> "_Playlist":
        """Playlist namespace for YouTube operations.
        
        Returns:
            Playlist handler that can be called with an ID to get playlist metadata.
            
        Example:
            ```python
            playlist = supadata.youtube.playlist("PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc")
            ```
        """
        if self._playlist_instance is None:
            self._playlist_instance = self._Playlist(self)
        return self._playlist_instance

    @property
    def video(self) -> "_Video":
        """Video namespace for YouTube operations.
        
        Returns:
            Video handler that can be called with an ID to get video metadata.
            
        Example:
            ```python
            video = supadata.youtube.video("dQw4w9WgXcQ")
            ```
        """
        if self._video_instance is None:
            self._video_instance = self._Video(self)
        return self._video_instance

    @property
    def transcript(self) -> "_Transcript":
        """Transcript namespace for YouTube operations.
        
        Returns:
            Transcript handler that can be called with a video ID to get transcript.
            
        Example:
            ```python
            transcript = supadata.youtube.transcript("dQw4w9WgXcQ")
            ```
        """
        if self._transcript_instance is None:
            self._transcript_instance = self._Transcript(self)
        return self._transcript_instance

    @property
    def batch(self) -> "_Batch":
        """Batch namespace for YouTube operations.
        
        Returns:
            Batch handler for working with batch operations.
            
        Example:
            ```python
            batch_results = supadata.youtube.batch.get_batch_results("job_id_here")
            ```
        """
        if self._batch_instance is None:
            self._batch_instance = self._Batch(self)
        return self._batch_instance

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
                id: YouTube Channel ID, URL, or handle (@username)

            Returns:
                YoutubeChannel object containing the metadata:
                - id: Channel ID
                - name: Channel name
                - handle: Channel handle (if available)
                - description: Channel description
                - subscriber_count: Number of subscribers
                - video_count: Number of videos
                - thumbnail: URL to channel thumbnail
                - banner: URL to channel banner

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

        def videos(
            self, 
            id: str, 
            limit: Optional[int] = None,
            type: Literal["all", "video", "short"] = "all"
        ) -> VideoIds:
            """Get video IDs from a YouTube channel.

            Args:
                id: YouTube Channel ID
                limit: The limit of videos to be returned. None will
                    return the default (30 videos)
                type: The type of videos to fetch.
                    'all': Both regular videos and shorts (default)
                    'video': Only regular videos
                    'short': Only shorts

            Returns:
                VideoIds object containing lists of video IDs and short IDs

            Raises:
                SupadataError: If the API request fails
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
                short_ids=response.get("short_ids", [])
            )

        def batch(
            self,
            video_ids: Optional[List[str]] = None,
            playlist_id: Optional[str] = None,
            channel_id: Optional[str] = None,
            limit: Optional[int] = None,
            lang: Optional[str] = None,
        ) -> BatchJob:
            """Create a batch job to get transcripts from multiple YouTube videos.

            One of video_ids, playlist_id, or channel_id must be provided.

            Args:
                video_ids: Array of YouTube video IDs or URLs.
                playlist_id: YouTube playlist URL or ID.
                channel_id: YouTube channel URL, handle or ID.
                limit: Maximum number of videos to process (when using playlistId or channelId). Default: 10, Max: 5000.
                lang: Preferred language code for transcripts (ISO 639-1).

            Returns:
                BatchJob object containing the job ID.

            Raises:
                SupadataError: If the API request fails or input validation fails.
            """
            payload = self._youtube._validate_batch_sources(video_ids, playlist_id, channel_id, limit)
            if lang:
                payload["lang"] = lang

            response = self._youtube._request("POST", "/youtube/transcript/batch", json=payload)
            return BatchJob(**response)

    class _Playlist:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def __call__(self, id: str) -> YoutubePlaylist:
            """Gets the playlist metadata for a YouTube public playlist.

            Args:
                id: YouTube playlist ID or URL

            Returns:
                YoutubePlaylist object containing the metadata:
                - id: Playlist ID
                - title: Playlist title
                - description: Playlist description (if available)
                - video_count: Number of videos in the playlist
                - view_count: Number of views
                - channel: Dict containing channel id and name
                - last_updated: Datetime when the playlist was last updated

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

        def videos(
            self, 
            id: str, 
            limit: Optional[int] = None
        ) -> VideoIds:
            """Get video IDs from a YouTube playlist.

            Args:
                id: YouTube Playlist ID
                limit: The limit of videos to be returned. None will
                    return the default (30 videos)

            Returns:
                VideoIds object containing lists of video IDs and short IDs

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
            
            return VideoIds(
                video_ids=response.get("video_ids", []),
                short_ids=response.get("short_ids", [])
            )

    class _Video:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def __call__(self, id: str) -> YoutubeVideo:
            """Get the video metadata for a YouTube video.

            Args:
                id: YouTube video ID or URL

            Returns:
                YoutubeVideo object containing the metadata:
                - id: Video ID
                - title: Video title
                - description: Video description
                - duration: Video duration in seconds
                - channel: Dict containing channel id and name
                - tags: List of video tags
                - thumbnail: URL to video thumbnail
                - view_count: Number of views
                - like_count: Number of likes
                - transcript_languages: List of available transcript languages
                - uploaded_date: Datetime when the video was uploaded

            Raises:
                SupadataError: If the API request fails
            """
            response: dict = self._youtube._request("GET", "/youtube/video", params={"id": id})
            
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
                limit: Maximum number of videos to process (when using playlistId or channelId). Default: 10, Max: 5000.

            Returns:
                BatchJob object containing the job ID.

            Raises:
                SupadataError: If the API request fails or input validation fails.
            """
            payload = self._youtube._validate_batch_sources(video_ids, playlist_id, channel_id, limit)
            response = self._youtube._request("POST", "/youtube/video/batch", json=payload)
            return BatchJob(**response)

    class _Transcript:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def __call__(self, video_id: str, lang: str = None, text: bool = False) -> Transcript:
            """Get transcript for a YouTube video.

            Args:
                video_id: YouTube video ID or URL
                lang: Language code for preferred transcript language (e.g., 'es' for Spanish)
                text: Whether to return plain text instead of segments

            Returns:
                Transcript object containing:
                - content: List of TranscriptChunk objects or plain text if text=True
                - lang: Language code of the transcript
                - available_langs: List of available language codes

            Raises:
                SupadataError: If the API request fails
            """
            params = {"videoId": video_id, "text": str(text).lower()}

            if lang:
                params["lang"] = lang

            response = self._youtube._request("GET", "/youtube/transcript", params=params)

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

        def batch(
            self,
            video_ids: Optional[List[str]] = None,
            playlist_id: Optional[str] = None,
            channel_id: Optional[str] = None,
            limit: Optional[int] = None,
            lang: Optional[str] = None,
        ) -> BatchJob:
            """Create a batch job to get transcripts from multiple YouTube videos.

            One of video_ids, playlist_id, or channel_id must be provided.

            Args:
                video_ids: Array of YouTube video IDs or URLs.
                playlist_id: YouTube playlist URL or ID.
                channel_id: YouTube channel URL, handle or ID.
                limit: Maximum number of videos to process (when using playlistId or channelId). Default: 10, Max: 5000.
                lang: Preferred language code for transcripts (ISO 639-1).

            Returns:
                BatchJob object containing the job ID.

            Raises:
                SupadataError: If the API request fails or input validation fails.
            """
            payload = self._youtube._validate_batch_sources(video_ids, playlist_id, channel_id, limit)
            if lang:
                payload["lang"] = lang

            response = self._youtube._request("POST", "/youtube/transcript/batch", json=payload)
            return BatchJob(**response)

        def translate(self, video_id: str, lang: str, text: bool = False) -> TranslatedTranscript:
            """Get translated transcript for a YouTube video.

            Args:
                video_id: YouTube video ID or URL
                lang: Target language code (e.g., 'es' for Spanish)
                text: Whether to return plain text instead of segments

            Returns:
                TranslatedTranscript object containing:
                - content: List of TranscriptChunk objects or plain text if text=True
                - lang: Language code of the translated transcript

            Raises:
                SupadataError: If the API request fails
            """
            response = self._youtube._request(
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

    class _Batch:
        def __init__(self, youtube: "YouTube"):
            self._youtube = youtube

        def get_batch_results(self, job_id: str) -> BatchResults:
            """Get the status and results of a batch job.

            Args:
                job_id: The ID of the batch job.

            Returns:
                BatchResults object containing:
                - status: Current job status ('pending', 'processing', 'completed', 'failed')
                - results: List of processed items (videos or transcripts)
                - stats: Statistics about the job (total items, processed, errors)

            Raises:
                SupadataError: If the API request fails.
            """
            response = self._youtube._request("GET", f"/youtube/batch/{job_id}")
            return BatchResults(**response)
