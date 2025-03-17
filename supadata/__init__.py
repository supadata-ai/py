"""
Supadata Python SDK

The official Python SDK for Supadata - scrape web and YouTube content with ease.
"""
from importlib.metadata import version
from supadata.client import Supadata
from supadata.errors import SupadataError
from supadata.types import (
    Transcript,
    TranslatedTranscript,
    TranscriptChunk,
    Scrape,
    Map,
    CrawlJob,
    CrawlPage,
    CrawlResponse,
    YoutubeVideo,
    YoutubeChannel,
    YoutubePlaylist,
    YoutubeChannelVideos,
    YoutubePlaylistVideos
)

__version__ = version("supadata")
__all__ = [
    "Supadata",
    "Transcript",
    "TranslatedTranscript",
    "TranscriptChunk",
    "Scrape",
    "Map",
    "SupadataError",
    "CrawlJob",
    "CrawlPage",
    "CrawlResponse",
    "YoutubeVideo",
    "YoutubeChannel",
    "YoutubePlaylist",
    "YoutubeChannelVideos",
    "YoutubePlaylistVideos"
] 