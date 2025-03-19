"""Type definitions for Supadata API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TypedDict, Union


@dataclass
class TranscriptChunk:
    """A chunk of a video transcript.

    Attributes:
        text: Transcript segment text
        offset: Start time in milliseconds
        duration: Duration in milliseconds
        lang: ISO 639-1 language code of chunk
    """

    text: str = ""
    offset: int = 0
    duration: int = 0
    lang: str = ""


@dataclass
class Transcript:
    """A complete video transcript.

    Attributes:
        content: List of transcript chunks or plain text when text=true
        lang: ISO 639-1 language code of transcript
        available_langs: List of available language codes
    """

    content: Union[List[TranscriptChunk], str] = None
    lang: str = ""
    available_langs: List[str] = None

    def __post_init__(self):
        if self.content is None:
            self.content = []
        if self.available_langs is None:
            self.available_langs = []


@dataclass
class TranslatedTranscript:
    """A translated video transcript.

    Attributes:
        content: List of transcript chunks or plain text when text=true
        lang: ISO 639-1 language code of translation
    """

    content: Union[List[TranscriptChunk], str] = None
    lang: str = ""

    def __post_init__(self):
        if self.content is None:
            self.content = []


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
    content: str = ""
    name: str = ""
    description: str = ""
    og_url: Optional[str] = None
    count_characters: int = 0
    urls: List[str] = None

    def __post_init__(self):
        if self.urls is None:
            self.urls = []


@dataclass
class Map:
    """A site map containing URLs.

    Attributes:
        urls: List of URLs found on the webpage
    """

    urls: List[str] = None

    def __post_init__(self):
        if self.urls is None:
            self.urls = []


@dataclass
class CrawlPage:
    """A page from a crawl job.

    Attributes:
        url: The URL that was scraped
        content: The Markdown content extracted from the URL
        name: The name of the webpage
        description: A description of the webpage
        og_url: Open Graph URL for the webpage
        count_characters: The number of characters in the content
    """

    url: str
    content: str = ""
    name: str = ""
    description: str = ""
    og_url: Optional[str] = None
    count_characters: int = 0


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
class YoutubeChannelBaseDict(TypedDict):
    """YouTube Channel dict

    Attribute:
        id: The channel id
        name: The channel name

    """

    id: str
    name: str


@dataclass
class YoutubeVideo:
    """YouTube video details.

    Attributes:
        id: YouTube video ID
        title: Video title
        description: Video description
        duration: Duration of video in seconds
        channel: A dict containing the channel ID and channel name
        thumbnail: The URL of the video thumbnail
        view_count: Number of views
        like_count: Number of likes
        tags: List of video tags
    """

    id: str
    title: str = ""
    description: str = ""
    duration: int = 0
    channel: YoutubeChannelBaseDict = None
    tags: List[str] = None
    thumbnail: str = ""
    uploaded_date: datetime = None
    view_count: int = 0
    like_count: int = 0
    transcript_languages: List[str] = None

    def __post_init__(self):
        if self.channel is None:
            self.channel = YoutubeChannelBaseDict(id="", name="")
        if self.tags is None:
            self.tags = []
        if self.uploaded_date is None:
            self.uploaded_date = datetime.now()
        if self.transcript_languages is None:
            self.transcript_languages = []


@dataclass
class YoutubeChannel:
    """YouTube Channel Details

    Attributes:
        id: Channel ID
        name: Channel name
        handle: The YouTube Channel Handle
        description: Channel description
        subscriber_count: Number of subscribers
        video_count: Number of videos
        thumbnail: The URL of the channel Thumbnail
        banner: The URL of the Channel banner
    """

    id: str
    name: str = ""
    handle: str = ""
    description: str = ""
    subscriber_count: int = 0
    video_count: int = 0
    thumbnail: str = ""
    banner: str = ""


@dataclass
class YoutubePlaylist:
    """Youtube Playlist Details

    Attributes:
        id: Playlist ID
        title: Playlist Title
        description: Playlist Description
        video_count: Number of videos in the playlist
        view_count: Number of views in the playlist
        last_updated: Playlist last update date
        channel: A dict containing the channel ID and channel name
    """

    id: str
    title: str = ""
    video_count: int = 0
    view_count: int = 0
    last_updated: datetime = None
    channel: YoutubeChannelBaseDict = None
    description: Optional[str] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.channel is None:
            self.channel = YoutubeChannelBaseDict(id="", name="")
