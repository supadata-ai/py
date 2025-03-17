"""Type definitions for Supadata API responses."""

from typing import List, Optional, Union
from dataclasses import dataclass


@dataclass
class TranscriptChunk:
    """A chunk of a video transcript.
    
    Attributes:
        text: Transcript segment text
        offset: Start time in milliseconds
        duration: Duration in milliseconds
        lang: ISO 639-1 language code of chunk
    """
    text: str
    offset: int
    duration: int
    lang: str


@dataclass
class Transcript:
    """A complete video transcript.
    
    Attributes:
        content: List of transcript chunks or plain text when text=true
        lang: ISO 639-1 language code of transcript
        available_langs: List of available language codes
    """
    content: Union[List[TranscriptChunk], str]
    lang: str
    available_langs: List[str]


@dataclass
class TranslatedTranscript:
    """A translated video transcript.
    
    Attributes:
        content: List of transcript chunks or plain text when text=true
        lang: ISO 639-1 language code of translation
    """
    content: Union[List[TranscriptChunk], str]
    lang: str


@dataclass
class Scrape:
    """Scraped web content.
    
    Attributes:
        url: The URL that was scraped
        content: The Markdown content extracted from the URL
        name: The name of the webpage
        description: A description of the webpage
        og_url: Open Graph URL for the webpage
        count_characters: The number of characters in the content
        urls: List of URLs found on the webpage
    """
    url: str
    content: str
    name: str
    description: str
    og_url: Optional[str]
    count_characters: int
    urls: List[str]


@dataclass
class Map:
    """A site map containing URLs.
    
    Attributes:
        urls: List of URLs found on the webpage
    """
    urls: List[str]

@dataclass
class CrawlPage:
    """A page from a crawl job.
    
    Attributes:
        url: The URL that was scraped
        content: The markdown content extracted from the URL
        name: The title of the webpage
        description: A description of the webpage
    """
    url: str
    content: str
    name: str
    description: str


@dataclass
class CrawlResponse:
    """Response from a crawl job.
    
    Attributes:
        status: The status of the crawl job
        pages: List of crawled pages (only when completed)
        next: URL for the next page of results
    """
    status: str  # 'scraping', 'completed', 'failed' or 'cancelled'
    pages: Optional[List[CrawlPage]] = None
    next: Optional[str] = None


@dataclass
class CrawlJob:
    """A new crawl job.
    
    Attributes:
        job_id: The ID of the crawl job
    """
    job_id: str


@dataclass
class YoutubeVideo:
    """YouTube video details.
    
    Attributes:
        id: YouTube video ID
        title: Video title
        description: Video description
        published_at: Timestamp when the video was published
        channel_id: ID of the channel that uploaded the video
        channel_title: Title of the channel that uploaded the video
        thumbnail_url: URL of the video thumbnail
        duration: Duration of video in seconds
        view_count: Number of views
        like_count: Number of likes
        comment_count: Number of comments
        tags: List of video tags
    """
    id: str
    title: str
    description: str
    published_at: str
    channel_id: str
    channel_title: str
    thumbnail_url: str
    duration: int
    view_count: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    tags: Optional[List[str]] = None


@dataclass
class YoutubeChannel:
    """YouTube channel details.
    
    Attributes:
        id: YouTube channel ID
        title: Channel title
        description: Channel description
        custom_url: Custom URL of the channel
        published_at: Timestamp when the channel was created
        thumbnail_url: URL of the channel thumbnail
        subscriber_count: Number of subscribers
        video_count: Number of videos
        view_count: Number of views
    """
    id: str
    title: str
    description: str
    custom_url: Optional[str]
    published_at: str
    thumbnail_url: str
    subscriber_count: Optional[int] = None
    video_count: int = 0
    view_count: int = 0


@dataclass
class YoutubePlaylist:
    """YouTube playlist details.
    
    Attributes:
        id: YouTube playlist ID
        title: Playlist title
        description: Playlist description
        published_at: Timestamp when the playlist was created
        channel_id: ID of the channel that created the playlist
        channel_title: Title of the channel that created the playlist
        thumbnail_url: URL of the playlist thumbnail
        item_count: Number of videos in the playlist
    """
    id: str
    title: str
    description: str
    published_at: str
    channel_id: str
    channel_title: str
    thumbnail_url: str
    item_count: int


@dataclass
class YoutubeChannelVideos:
    """Videos from a YouTube channel.
    
    Attributes:
        channel_id: YouTube channel ID
        channel_title: Title of the channel
        videos: List of videos from the channel
    """
    channel_id: str
    channel_title: str
    videos: List[YoutubeVideo]


@dataclass
class YoutubePlaylistVideos:
    """Videos from a YouTube playlist.
    
    Attributes:
        playlist_id: YouTube playlist ID
        playlist_title: Title of the playlist
        videos: List of videos from the playlist
    """
    playlist_id: str
    playlist_title: str
    videos: List[YoutubeVideo]

