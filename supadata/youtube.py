"""YouTube-related operations for Supadata."""

from typing import Dict, Any, Optional, List, Union
from .types import Transcript, TranslatedTranscript, TranscriptChunk, YoutubeVideo, YoutubeChannel, YoutubePlaylist, YoutubeChannelVideos, YoutubePlaylistVideos


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

    def video(self, video_id: str) -> YoutubeVideo:
        """Get details about a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            YoutubeVideo object containing video details

        Raises:
            SupadataError: If the API request fails
        """
        response = self._request("GET", "/youtube/video", params={
            "videoId": video_id
        })
        return YoutubeVideo(**response)

    def channel(self, channel_id: str) -> YoutubeChannel:
        """Get details about a YouTube channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            YoutubeChannel object containing channel details

        Raises:
            SupadataError: If the API request fails
        """
        response = self._request("GET", "/youtube/channel", params={
            "channelId": channel_id
        })
        return YoutubeChannel(**response)

    def playlist(self, playlist_id: str) -> YoutubePlaylist:
        """Get details about a YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            YoutubePlaylist object containing playlist details

        Raises:
            SupadataError: If the API request fails
        """
        response = self._request("GET", "/youtube/playlist", params={
            "playlistId": playlist_id
        })
        return YoutubePlaylist(**response)

    def channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        published_after: str = None,
        published_before: str = None
    ) -> YoutubeChannelVideos:
        """Get videos from a YouTube channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return (default: 50, max: 100)
            published_after: Filter videos published after this date (ISO 8601, e.g., '2023-01-01T00:00:00Z')
            published_before: Filter videos published before this date (ISO 8601, e.g., '2023-12-31T23:59:59Z')

        Returns:
            YoutubeChannelVideos object containing channel information and list of videos

        Raises:
            SupadataError: If the API request fails
        """
        params = {
            "channelId": channel_id,
            "maxResults": max_results
        }

        if published_after:
            params["publishedAfter"] = published_after
        
        if published_before:
            params["publishedBefore"] = published_before

        response = self._request("GET", "/youtube/channel/videos", params=params)
        
        # Convert video list to YoutubeVideo objects
        videos = [YoutubeVideo(**video) for video in response.get("videos", [])]
        
        return YoutubeChannelVideos(
            channel_id=response.get("channel_id", ""),
            channel_title=response.get("channel_title", ""),
            videos=videos
        )

    def playlist_videos(
        self,
        playlist_id: str,
        max_results: int = 50
    ) -> YoutubePlaylistVideos:
        """Get videos from a YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to return (default: 50, max: 100)

        Returns:
            YoutubePlaylistVideos object containing playlist information and list of videos

        Raises:
            SupadataError: If the API request fails
        """
        params = {
            "playlistId": playlist_id,
            "maxResults": max_results
        }

        response = self._request("GET", "/youtube/playlist/videos", params=params)
        
        # Convert video list to YoutubeVideo objects
        videos = [YoutubeVideo(**video) for video in response.get("videos", [])]
        
        return YoutubePlaylistVideos(
            playlist_id=response.get("playlist_id", ""),
            playlist_title=response.get("playlist_title", ""),
            videos=videos
        ) 