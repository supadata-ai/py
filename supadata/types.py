"""Type definitions for Supadata API responses."""

from dataclasses import dataclass, field
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
        # Convert list of dictionaries to TranscriptChunk objects
        if isinstance(self.content, list):
            self.content = [
                chunk if isinstance(chunk, TranscriptChunk) else TranscriptChunk(**chunk)
                for chunk in self.content
            ]


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


@dataclass
class VideoIds:
    """Container for YouTube video IDs.
    
    Attributes:
        video_ids: List of regular YouTube video IDs
        short_ids: List of YouTube Shorts IDs
        live_ids: List of YouTube Live IDs
    """
    
    video_ids: List[str] = None
    short_ids: List[str] = None
    live_ids: List[str] = None
    
    def __post_init__(self):
        if self.video_ids is None:
            self.video_ids = []
        if self.short_ids is None:
            self.short_ids = []
        if self.live_ids is None:
            self.live_ids = []


@dataclass
class BatchJob:
    """Response containing the ID of a newly created batch job.

    Attributes:
        job_id: The unique identifier for the batch job.
    """

    job_id: str


@dataclass
class BatchResultItem:
    """Represents a single result item within a batch job.

    Attributes:
        video_id: The ID of the YouTube video processed.
        transcript: The transcript object (present if successful and type is transcript).
        video: The video metadata object (present if successful and type is video).
        error_code: An error code if processing this specific video failed.
    """

    video_id: str
    transcript: Optional[Transcript] = None
    video: Optional[YoutubeVideo] = None
    error_code: Optional[str] = None


@dataclass
class BatchStats:
    """Statistics for a completed batch job.

    Attributes:
        total: The total number of videos processed.
        succeeded: The number of videos processed successfully.
        failed: The number of videos that failed processing.
    """

    total: int = 0
    succeeded: int = 0
    failed: int = 0


@dataclass
class BatchResults:
    """Represents the complete results of a batch job.

    Attributes:
        status: The current status of the batch job ('queued', 'active', 'completed', 'failed').
        results: A list of individual results for each video.
        stats: Statistics about the processed videos.
        completed_at: Timestamp when the job completed (ISO 8601 format).
    """

    status: str
    results: List[BatchResultItem] = field(default_factory=list)
    stats: Optional[BatchStats] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        # Attempt to parse completed_at if it's a string
        if isinstance(self.completed_at, str):
            try:
                self.completed_at = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
            except ValueError:
                self.completed_at = None # Handle potential parsing errors
        
        # Process results into BatchResultItem objects
        processed_results = []
        if isinstance(self.results, list):
            for item in self.results:
                 if isinstance(item, dict):
                    # Determine if it's a transcript or video result based on keys
                    transcript_data = item.get('transcript')
                    video_data = item.get('video')
                    
                    transcript_obj = None
                    if transcript_data and isinstance(transcript_data, dict):
                       transcript_obj = Transcript(**transcript_data)

                    video_obj = None
                    if video_data and isinstance(video_data, dict):
                        # Handle potential date parsing issues for video upload_date
                        try:
                            uploaded_time = datetime.fromisoformat(video_data.pop("upload_date", datetime.now().isoformat()))
                        except (ValueError, TypeError):
                            uploaded_time = datetime.now()
                        video_obj = YoutubeVideo(**video_data, uploaded_date=uploaded_time)

                    # Explicitly get values before creating the object
                    # Use 'video_id' (snake_case) as the key might be auto-converted by dataclass init
                    current_video_id = item.get('video_id', '')
                    current_error_code = item.get('error_code') # Assuming this might also be converted

                    processed_results.append(
                        BatchResultItem(
                            video_id=current_video_id,
                            transcript=transcript_obj,
                            video=video_obj,
                            error_code=current_error_code
                        )
                    )
        self.results = processed_results

        # Process stats into BatchStats object
        if isinstance(self.stats, dict):
            self.stats = BatchStats(**self.stats)
