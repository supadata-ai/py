"""Tests for the Supadata client."""

from datetime import datetime

import pytest

from supadata import (
    CrawlJob,
    CrawlPage,
    Map,
    Metadata,
    MetadataAuthor,
    MetadataStats,
    MetadataMedia,
    Scrape,
    Supadata,
    Transcript,
    TranscriptChunk,
    TranslatedTranscript,
    YoutubeChannel,
    YoutubePlaylist,
    YoutubeVideo,
)
from supadata.errors import SupadataError
from supadata.types import (
    BatchJob,
    BatchResultItem,
    BatchResults,
    BatchStats,
    YoutubeSearchResponse,
    YoutubeSearchResult,
)


@pytest.fixture
def api_key() -> str:
    """Return a dummy API key for testing."""
    return "test_api_key"


@pytest.fixture
def base_url() -> str:
    """Return a dummy base URL for testing."""
    return "https://api.test.com/v1"


@pytest.fixture
def client(api_key: str, base_url: str) -> Supadata:
    """Return a configured Supadata client."""
    return Supadata(api_key=api_key, base_url=base_url)


def test_client_initialization(api_key: str, base_url: str) -> None:
    """Test client initialization."""
    client = Supadata(api_key=api_key, base_url=base_url)
    assert client.base_url == base_url
    assert client.session.headers["x-api-key"] == api_key
    assert client.session.headers["Accept"] == "application/json"


def test_get_transcript_chunks(client: Supadata, requests_mock) -> None:
    """Test getting transcript with chunks using universal endpoint."""
    url = "https://www.youtube.com/watch?v=test123"
    mock_response = {
        "content": [{"text": "Hello", "offset": 0, "duration": 1000, "lang": "en"}],
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url)
    assert isinstance(transcript, Transcript)
    assert isinstance(transcript.content[0], TranscriptChunk)
    assert transcript.content[0].text == "Hello"
    assert transcript.lang == "en"
    assert transcript.available_langs == ["en", "es"]


def test_get_transcript_text(client: Supadata, requests_mock) -> None:
    """Test getting transcript as plain text using universal endpoint."""
    url = "https://www.youtube.com/watch?v=test123"
    mock_response = {
        "content": "Hello, this is a test transcript",
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url, text=True)
    assert isinstance(transcript, Transcript)
    assert isinstance(transcript.content, str)
    assert transcript.content == "Hello, this is a test transcript"


def test_translate_transcript(client: Supadata, requests_mock) -> None:
    """Test translating YouTube transcript."""
    video_id = "test123"
    mock_response = {"content": "Hola, esto es una prueba", "lang": "es"}
    requests_mock.get(
        f"{client.base_url}/youtube/transcript/translate", json=mock_response
    )

    transcript = client.youtube.translate(video_id=video_id, lang="es", text=True)
    assert isinstance(transcript, TranslatedTranscript)
    assert transcript.content == "Hola, esto es una prueba"
    assert transcript.lang == "es"


def test_scrape(client: Supadata, requests_mock) -> None:
    """Test web scraping."""
    url = "https://test.com"
    mock_response = {
        "url": url,
        "content": "# Test\nThis is a test page",
        "name": "Test Page",
        "description": "A test page",
        "ogUrl": "https://test.com/og.png",
        "countCharacters": 100,
        "urls": ["https://test.com/about"],
    }
    requests_mock.get(f"{client.base_url}/web/scrape", json=mock_response)

    content = client.web.scrape(url=url)
    assert isinstance(content, Scrape)
    assert content.url == url
    assert content.name == "Test Page"
    assert content.og_url == "https://test.com/og.png"
    assert content.count_characters == 100


def test_map(client: Supadata, requests_mock) -> None:
    """Test site mapping."""
    url = "https://test.com"
    mock_response = {"urls": ["https://test.com", "https://test.com/about"]}
    requests_mock.get(f"{client.base_url}/web/map", json=mock_response)

    site_map = client.web.map(url=url)
    assert isinstance(site_map, Map)
    assert len(site_map.urls) == 2


def test_error_handling(client: Supadata, requests_mock) -> None:
    """Test error handling for JSON API errors."""
    url = "https://www.youtube.com/watch?v=invalid"
    error_response = {
        "error": "video-not-found",
        "message": "Video Not Found",
        "details": "The specified video was not found",
        "documentationUrl": "https://docs.test.com/errors#video-not-found",
    }
    requests_mock.get(
        f"{client.base_url}/transcript",
        status_code=400,
        json=error_response,
        headers={"content-type": "application/json"},
    )

    with pytest.raises(SupadataError) as exc_info:
        client.transcript(url=url)

    error = exc_info.value
    assert error.error == error_response["error"]
    assert error.message == error_response["message"]
    assert error.details == error_response["details"]
    assert error.documentation_url == error_response["documentationUrl"]


def test_start_crawl(client: Supadata, requests_mock) -> None:
    """Test starting a crawl job."""
    url = "https://test.com"
    mock_response = {"jobId": "test-job-123"}
    requests_mock.post(f"{client.base_url}/web/crawl", json=mock_response)

    job = client.web.crawl(url=url, limit=100)
    assert isinstance(job, CrawlJob)
    assert job.job_id == "test-job-123"


def test_get_crawl_results(client: Supadata, requests_mock) -> None:
    """Test getting crawl results with pagination."""
    job_id = "test-job-123"

    # First page response
    mock_response1 = {
        "status": "completed",
        "pages": [
            {
                "url": "https://test.com",
                "content": "# Page 1",
                "name": "Test Page 1",
                "description": "First test page",
            }
        ],
        "next": "page2",
    }

    # Second page response
    mock_response2 = {
        "status": "completed",
        "pages": [
            {
                "url": "https://test.com/2",
                "content": "# Page 2",
                "name": "Test Page 2",
                "description": "Second test page",
            }
        ],
        "next": None,
    }

    requests_mock.get(
        f"{client.base_url}/web/crawl/{job_id}",
        [{"json": mock_response1}, {"json": mock_response2}],
    )

    pages = client.web.get_crawl_results(job_id=job_id)
    assert len(pages) == 2
    assert isinstance(pages[0], CrawlPage)
    assert pages[0].name == "Test Page 1"
    assert pages[1].name == "Test Page 2"


def test_get_crawl_results_failed(client: Supadata, requests_mock) -> None:
    """Test getting crawl results for a failed job."""
    job_id = "test-job-123"
    mock_response = {"status": "failed", "pages": None, "next": None}
    requests_mock.get(f"{client.base_url}/web/crawl/{job_id}", json=mock_response)

    with pytest.raises(Exception, match="Crawl job failed"):
        client.web.get_crawl_results(job_id=job_id)


def test_youtube_video_metadata(client: Supadata, requests_mock) -> None:
    """Test getting YouTube video metadata via metadata endpoint."""
    url = "https://www.youtube.com/watch?v=pEfrdAtAmqk"
    mock_response = {
        "platform": "youtube",
        "type": "video",
        "id": "pEfrdAtAmqk",
        "url": url,
        "title": "God-Tier Developer Roadmap",
        "description": "The programming iceberg is complete roadmap to the loved, ...",
        "author": {
            "username": "@Fireship",
            "displayName": "Fireship",
            "avatarUrl": "https://yt3.googleusercontent.com/avatar.jpg",
            "verified": True
        },
        "stats": {
            "views": 7388353,
            "likes": 262086,
            "comments": None,
            "shares": None
        },
        "media": {
            "video": {
                "url": "https://video.url",
                "duration": 1002,
                "width": 1920,
                "height": 1080,
                "thumbnail": "https://i.ytimg.com/vi/pEfrdAtAmqk/maxresdefault.jpg"
            }
        },
        "tags": ["#iceberg", "#learntocode", "#programming"],
        "createdAt": "2022-08-24T00:00:00.000Z"
    }

    requests_mock.get(f"{client.base_url}/metadata", json=mock_response)

    metadata = client.metadata(url=url)
    assert isinstance(metadata, Metadata)
    assert metadata.platform == "youtube"
    assert metadata.id == "pEfrdAtAmqk"
    assert metadata.title == "God-Tier Developer Roadmap"
    assert metadata.description == "The programming iceberg is complete roadmap to the loved, ..."
    assert metadata.author.display_name == "Fireship"
    assert metadata.stats.views == 7388353
    assert metadata.stats.likes == 262086
    assert metadata.media.video.duration == 1002
    assert metadata.tags == ["#iceberg", "#learntocode", "#programming"]


def test_youtube_video_invalid_url(client: Supadata, requests_mock) -> None:
    """Test error handling for invalid YouTube video URL."""
    url = "https://www.youtube.com/watch?v=invalid"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }
    requests_mock.get(
        f"{client.base_url}/metadata",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.metadata(url=url)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "The requested item could not be found"
    assert error.details == "The requested item could not be found."


def test_youtube_channel(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezykLs9EqgamOA"
    mock_response = {
        "id": channel_id,
        "name": "Fireship",
        "handle": "@Fireship",
        "description": "High-intensity ⚡ code tutorials and tech news to help you ship your app faster. New videos every week covering the topics every programmer should know. ",
        "videoCount": 719,
        "subscriberCount": 3770000,
        "thumbnail": "https://yt3.googleusercontent.com/ytc/AIdro_mKzklyPPhghBJQH5H3HpZ108YcE618DBRLAvRUD1AjKNw=s160-c-k-c0x00ffffff-no-rj",
        "banner": "https://yt3.googleusercontent.com/62Kw34f1ysmycFceeNIFGsWpRDyqgDUSn2mAn29gwv7axMjN4NUVkJWqwEi4XKBE0016l7C4=w2560-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
    }

    requests_mock.get(
        f"{client.base_url}/youtube/channel?id={channel_id}", json=mock_response
    )

    channel = client.youtube.channel(channel_id)
    assert isinstance(channel, YoutubeChannel)
    assert channel.id == mock_response["id"]
    assert channel.name == mock_response["name"]
    assert channel.handle == mock_response["handle"]
    assert channel.description == mock_response["description"]
    assert channel.video_count == mock_response["videoCount"]
    assert channel.subscriber_count == mock_response["subscriberCount"]
    assert channel.thumbnail == mock_response["thumbnail"]
    assert channel.banner == mock_response["banner"]


def test_youtube_channel_invalid_id(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }
    requests_mock.get(
        f"{client.base_url}/youtube/channel?id={channel_id}",
        status_code=404,
        json=mock_response,
    )
    with pytest.raises(SupadataError) as exc_info:
        client.youtube.channel(channel_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "The requested item could not be found"
    assert error.details == "The requested item could not be found."


def test_youtube_playlist(client: Supadata, requests_mock) -> None:
    playlist_id = "PL0vfts4VzfNjQOM9VClyL5R0LeuTxlAR3"
    mock_response = {
        "id": playlist_id,
        "title": "CS101",
        "videoCount": 17,
        "viewCount": 440901,
        "lastUpdated": "2024-07-06T00:00:00.000Z",
        "channel": {"id": "UCsBjURrPoezykLs9EqgamOA", "name": "Fireship"},
    }

    requests_mock.get(
        f"{client.base_url}/youtube/playlist?id={playlist_id}", json=mock_response
    )

    playlist = client.youtube.playlist(playlist_id)
    assert isinstance(playlist, YoutubePlaylist)
    assert playlist.id == mock_response["id"]
    assert playlist.title == mock_response["title"]
    assert playlist.video_count == mock_response["videoCount"]
    assert playlist.view_count == mock_response["viewCount"]
    assert playlist.last_updated == datetime.fromisoformat(mock_response["lastUpdated"])
    assert playlist.channel == mock_response["channel"]


def test_youtube_playlist_invalid_id(client: Supadata, requests_mock) -> None:
    playlist_id = "PL0vfts4VzfNjQOM9VClyL50LeuTxlAR3"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }

    requests_mock.get(
        f"{client.base_url}/youtube/playlist?id={playlist_id}",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.playlist(playlist_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "The requested item could not be found"
    assert error.details == "The requested item could not be found."


def test_youtube_channel_videos(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "videoIds": [
            "PQ2WjtaPfXU",
            "UIVADiGfwWc",
        ],
        "shortIds": [
            "abc123",
            "def456",
        ],
        "liveIds": [
            "ghi789",
            "jkl012",
        ]
    }

    requests_mock.get(
        f"{client.base_url}/youtube/channel/videos?id={channel_id}&type=all", json=mock_response
    )
    channel_videos = client.youtube.channel.videos(channel_id)
    assert hasattr(channel_videos, "video_ids")
    assert hasattr(channel_videos, "short_ids")
    assert hasattr(channel_videos, "live_ids")
    assert isinstance(channel_videos.video_ids, list)
    assert isinstance(channel_videos.short_ids, list)
    assert isinstance(channel_videos.live_ids, list)
    assert len(channel_videos.video_ids) == len(mock_response["videoIds"])
    assert len(channel_videos.short_ids) == len(mock_response["shortIds"])
    assert len(channel_videos.live_ids) == len(mock_response["liveIds"])
    for i in channel_videos.video_ids:
        assert i in mock_response["videoIds"]
    for i in channel_videos.short_ids:
        assert i in mock_response["shortIds"]
    for i in channel_videos.live_ids:
        assert i in mock_response["liveIds"]


def test_youtube_channel_videos_with_type(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "videoIds": [
            "PQ2WjtaPfXU",
            "UIVADiGfwWc",
        ],
        "shortIds": [],
        "liveIds": []
    }

    requests_mock.get(
        f"{client.base_url}/youtube/channel/videos?id={channel_id}&type=video", json=mock_response
    )
    channel_videos = client.youtube.channel.videos(channel_id, type="video")
    assert hasattr(channel_videos, "video_ids")
    assert hasattr(channel_videos, "short_ids")
    assert hasattr(channel_videos, "live_ids")
    assert isinstance(channel_videos.video_ids, list)
    assert isinstance(channel_videos.short_ids, list)
    assert isinstance(channel_videos.live_ids, list)
    assert len(channel_videos.video_ids) == len(mock_response["videoIds"])
    assert len(channel_videos.short_ids) == 0
    assert len(channel_videos.live_ids) == 0
    for i in channel_videos.video_ids:
        assert i in mock_response["videoIds"]
    for i in channel_videos.short_ids:
        assert i in mock_response["shortIds"]
    for i in channel_videos.live_ids:
        assert i in mock_response["liveIds"]


def test_youtube_channel_videos_invalid_id(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }
    requests_mock.get(
        f"{client.base_url}/youtube/channel/videos?id={channel_id}&type=all",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.channel.videos(channel_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "The requested item could not be found"
    assert error.details == "The requested item could not be found."


def test_youtube_playlist_videos(client: Supadata, requests_mock) -> None:
    playlist_id = "PL0vfts4VzfNjQOM9VClyL5R0LeuTxlAR3"
    mock_response = {
        "videoIds": [
            "zDNaUi2cjv4",
            "B1t4Fjlomi8",
        ],
        "shortIds": [
            "short1",
            "short2"
        ],
        "liveIds": [
            "live1",
            "live2"
        ]
    }
    requests_mock.get(
        f"{client.base_url}/youtube/playlist/videos?id={playlist_id}",
        json=mock_response,
    )

    playlist_videos = client.youtube.playlist.videos(playlist_id)
    assert hasattr(playlist_videos, "video_ids")
    assert hasattr(playlist_videos, "short_ids")
    assert hasattr(playlist_videos, "live_ids")
    assert isinstance(playlist_videos.video_ids, list)
    assert isinstance(playlist_videos.short_ids, list)
    assert isinstance(playlist_videos.live_ids, list)
    assert len(playlist_videos.video_ids) == len(mock_response["videoIds"])
    assert len(playlist_videos.short_ids) == len(mock_response["shortIds"])
    assert len(playlist_videos.live_ids) == len(mock_response["liveIds"])
    for i in playlist_videos.video_ids:
        assert i in mock_response["videoIds"]
    for i in playlist_videos.short_ids:
        assert i in mock_response["shortIds"]
    for i in playlist_videos.live_ids:
        assert i in mock_response["liveIds"]


def test_youtube_playlist_videos_invalid_id(client: Supadata, requests_mock) -> None:
    playlist_id = "PL0vfts4VzfNjQOM9VClyL50LeuTxlAR3"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }

    requests_mock.get(
        f"{client.base_url}/youtube/playlist/videos?id={playlist_id}",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.playlist.videos(playlist_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "The requested item could not be found"
    assert error.details == "The requested item could not be found."


# --- Batch Tests ---

def test_youtube_batch_transcript(client: Supadata, requests_mock) -> None:
    """Test creating a YouTube transcript batch job."""
    mock_response = {"jobId": "batch-transcript-job-123"}
    requests_mock.post(
        f"{client.base_url}/youtube/transcript/batch", json=mock_response
    )

    job = client.youtube.transcript.batch(video_ids=["vid1", "vid2"], lang="en", text=True)
    assert isinstance(job, BatchJob)
    assert job.job_id == "batch-transcript-job-123"


def test_youtube_batch_transcript_validation_no_source(client: Supadata) -> None:
    """Test validation for transcript batch without source."""
    with pytest.raises(SupadataError, match="Missing source"):
        client.youtube.transcript.batch()


def test_youtube_batch_transcript_validation_multiple_sources(client: Supadata) -> None:
    """Test validation for transcript batch with multiple sources."""
    with pytest.raises(SupadataError, match="Multiple sources"):
        client.youtube.transcript.batch(video_ids=["vid1"], playlist_id="pl1")


def test_youtube_batch_video(client: Supadata, requests_mock) -> None:
    """Test creating a YouTube video metadata batch job."""
    mock_response = {"jobId": "batch-video-job-456"}
    requests_mock.post(f"{client.base_url}/youtube/video/batch", json=mock_response)

    job = client.youtube.video.batch(playlist_id="pl123", limit=50)
    assert isinstance(job, BatchJob)
    assert job.job_id == "batch-video-job-456"


def test_youtube_batch_video_validation_no_source(client: Supadata) -> None:
    """Test validation for video batch without source."""
    with pytest.raises(SupadataError, match="Missing source"):
        client.youtube.video.batch()


def test_youtube_batch_video_validation_multiple_sources(client: Supadata) -> None:
    """Test validation for video batch with multiple sources."""
    with pytest.raises(SupadataError, match="Multiple sources"):
        client.youtube.video.batch(video_ids=["vid1"], channel_id="ch1")


def test_youtube_get_batch_results_completed(client: Supadata, requests_mock) -> None:
    """Test getting completed YouTube batch results."""
    job_id = "batch-job-789"
    mock_response = {
        "status": "completed",
        "results": [
            {
                "videoId": "vid1",
                "transcript": {
                    "content": "Transcript 1",
                    "lang": "en",
                    "availableLangs": ["en", "de"],
                },
            },
            {"videoId": "vid2", "errorCode": "transcript-unavailable"},
        ],
        "stats": {"total": 2, "succeeded": 1, "failed": 1},
        "completedAt": "2025-04-03T06:59:53.428Z",
    }
    requests_mock.get(f"{client.base_url}/youtube/batch/{job_id}", json=mock_response)

    results = client.youtube.batch.get_batch_results(job_id=job_id)
    assert isinstance(results, BatchResults)
    assert results.status == "completed"
    assert isinstance(results.stats, BatchStats)
    assert results.stats.total == 2
    assert results.stats.succeeded == 1
    assert results.stats.failed == 1
    assert isinstance(results.completed_at, datetime)
    assert len(results.results) == 2
    assert isinstance(results.results[0], BatchResultItem)
    assert results.results[0].video_id == "vid1"
    assert isinstance(results.results[0].transcript, Transcript)
    assert results.results[0].transcript.content == "Transcript 1"
    assert results.results[0].error_code is None
    assert results.results[1].video_id == "vid2"
    assert results.results[1].transcript is None
    assert results.results[1].error_code == "transcript-unavailable"


def test_youtube_get_batch_results_active(client: Supadata, requests_mock) -> None:
    """Test getting active YouTube batch results."""
    job_id = "batch-job-active"
    mock_response = {"status": "active"}
    requests_mock.get(f"{client.base_url}/youtube/batch/{job_id}", json=mock_response)

    results = client.youtube.batch.get_batch_results(job_id=job_id)
    assert isinstance(results, BatchResults)
    assert results.status == "active"
    assert results.results == []
    assert results.stats is None
    assert results.completed_at is None


def test_youtube_get_batch_results_failed(client: Supadata, requests_mock) -> None:
    """Test getting failed YouTube batch results."""
    job_id = "batch-job-failed"
    mock_response = {"status": "failed"}
    requests_mock.get(f"{client.base_url}/youtube/batch/{job_id}", json=mock_response)

    results = client.youtube.batch.get_batch_results(job_id=job_id)
    assert isinstance(results, BatchResults)
    assert results.status == "failed"


# --- Universal Transcript Tests ---

def test_transcript_immediate_chunks(client: Supadata, requests_mock) -> None:
    """Test getting transcript with immediate response as chunks."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "content": [{"text": "Never gonna give you up", "offset": 0, "duration": 2000, "lang": "en"}],
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url)
    assert isinstance(transcript, Transcript)
    assert isinstance(transcript.content[0], TranscriptChunk)
    assert transcript.content[0].text == "Never gonna give you up"
    assert transcript.lang == "en"
    assert transcript.available_langs == ["en", "es"]


def test_transcript_immediate_text(client: Supadata, requests_mock) -> None:
    """Test getting transcript with immediate response as plain text."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "content": "Never gonna give you up, never gonna let you down",
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url, text=True)
    assert isinstance(transcript, Transcript)
    assert isinstance(transcript.content, str)
    assert transcript.content == "Never gonna give you up, never gonna let you down"
    assert transcript.lang == "en"


def test_transcript_async_job(client: Supadata, requests_mock) -> None:
    """Test getting transcript that returns a job ID for async processing."""
    url = "https://www.tiktok.com/@user/video/123456789"
    mock_response = {"jobId": "transcript-job-456"}
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    result = client.transcript(url=url)
    assert isinstance(result, BatchJob)
    assert result.job_id == "transcript-job-456"


def test_transcript_with_language(client: Supadata, requests_mock) -> None:
    """Test transcript with specific language preference."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "content": "Nunca te voy a abandonar",
        "lang": "es",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url, lang="es", text=True)
    assert isinstance(transcript, Transcript)
    assert transcript.content == "Nunca te voy a abandonar"
    assert transcript.lang == "es"


def test_transcript_with_chunk_size(client: Supadata, requests_mock) -> None:
    """Test transcript with chunk size parameter."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "content": [
            {"text": "Never gonna", "offset": 0, "duration": 1000, "lang": "en"},
            {"text": "give you up", "offset": 1000, "duration": 1000, "lang": "en"}
        ],
        "lang": "en",
        "availableLangs": ["en"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url, chunk_size=100)
    assert isinstance(transcript, Transcript)
    assert len(transcript.content) == 2
    assert transcript.content[0].text == "Never gonna"
    assert transcript.content[1].text == "give you up"


def test_transcript_with_mode(client: Supadata, requests_mock) -> None:
    """Test transcript with different mode parameter."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "content": "Generated transcript content",
        "lang": "en",
        "availableLangs": ["en"],
    }
    requests_mock.get(f"{client.base_url}/transcript", json=mock_response)

    transcript = client.transcript(url=url, mode="generate", text=True)
    assert isinstance(transcript, Transcript)
    assert transcript.content == "Generated transcript content"


def test_transcript_error_handling(client: Supadata, requests_mock) -> None:
    """Test transcript error handling."""
    url = "https://invalid-url.com"
    error_response = {
        "error": "unsupported-platform",
        "message": "Unsupported Platform", 
        "details": "The specified platform is not supported",
    }
    requests_mock.get(
        f"{client.base_url}/transcript",
        status_code=400,
        json=error_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.transcript(url=url)

    error = exc_info.value
    assert error.error == "unsupported-platform"
    assert error.message == "Unsupported Platform"
    assert error.details == "The specified platform is not supported"


def test_youtube_transcript_206_error_handling(client: Supadata, requests_mock) -> None:
    """Test transcript 206 response error handling."""
    url = "https://www.youtube.com/watch?v=6ciqyBnXIKQ"
    error_response = {
        "error": "transcript-unavailable",
        "message": "Transcript Unavailable",
        "details": "No transcript is available for this video",
        "documentationUrl": "https://supadata.ai/documentation/errors/transcript-unavailable"
    }
    requests_mock.get(
        f"{client.base_url}/transcript",
        status_code=206,
        json=error_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.transcript(url=url)

    error = exc_info.value
    assert error.error == "transcript-unavailable"
    assert error.message == "Transcript Unavailable"
    assert error.details == "No transcript is available for this video"
    assert error.documentation_url == "https://supadata.ai/documentation/errors/transcript-unavailable"


# --- YouTube Search Tests ---

def test_youtube_search_basic(client: Supadata, requests_mock) -> None:
    """Test basic YouTube search functionality."""
    query = "Never Gonna Give You Up"
    mock_response = {
        "query": query,
        "results": [
            {
                "id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
                "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "duration": 212,
                "viewCount": 1500000000,
                "uploadDate": "2009-10-25T00:00:00.000Z",
                "channel": {"id": "UCuAXFkgsw1L7xaCfnd5JJOw", "name": "Rick Astley"},
                "description": "The official video for \"Never Gonna Give You Up\" by Rick Astley"
            }
        ],
        "totalResults": 1000000
    }
    requests_mock.get(f"{client.base_url}/youtube/search", json=mock_response)

    search_response = client.youtube.search(query=query)
    assert isinstance(search_response, YoutubeSearchResponse)
    assert search_response.query == query
    assert search_response.total_results == 1000000
    assert len(search_response.results) == 1
    
    result = search_response.results[0]
    assert isinstance(result, YoutubeSearchResult)
    assert result.id == "dQw4w9WgXcQ"
    assert result.title == "Rick Astley - Never Gonna Give You Up (Official Video)"
    assert result.duration == 212
    assert result.view_count == 1500000000
    assert result.channel["name"] == "Rick Astley"


def test_youtube_search_with_filters(client: Supadata, requests_mock) -> None:
    """Test YouTube search with various filters."""
    query = "Python tutorial"
    mock_response = {
        "query": query,
        "results": [
            {
                "id": "abc123def",
                "title": "Python Tutorial for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/abc123def/maxresdefault.jpg",
                "duration": 3600,
                "viewCount": 500000,
                "uploadDate": "2024-01-15T00:00:00.000Z",
                "channel": {"id": "UCchannel123", "name": "Python Academy"},
                "description": "Complete Python tutorial for beginners"
            }
        ],
        "totalResults": 50000
    }
    requests_mock.get(f"{client.base_url}/youtube/search", json=mock_response)

    search_response = client.youtube.search(
        query=query,
        upload_date="week",
        type="video", 
        duration="long",
        sort_by="views",
        features=["hd", "subtitles"],
        limit=10
    )
    
    assert isinstance(search_response, YoutubeSearchResponse)
    assert search_response.query == query
    assert search_response.total_results == 50000
    assert len(search_response.results) == 1



def test_youtube_search_empty_query_error(client: Supadata) -> None:
    """Test YouTube search with empty query raises error."""
    with pytest.raises(SupadataError) as exc_info:
        client.youtube.search(query="")
    
    error = exc_info.value
    assert error.error == "invalid-request"
    assert "Query is required" in error.message


def test_youtube_search_invalid_limit_error(client: Supadata) -> None:
    """Test YouTube search with invalid limit raises error."""
    with pytest.raises(SupadataError) as exc_info:
        client.youtube.search(query="test", limit=6000)
    
    error = exc_info.value
    assert error.error == "invalid-request"
    assert "Invalid limit" in error.message


def test_youtube_search_api_error(client: Supadata, requests_mock) -> None:
    """Test YouTube search API error handling."""
    query = "test query"
    error_response = {
        "error": "rate-limit-exceeded",
        "message": "Rate limit exceeded",
        "details": "Too many requests per minute"
    }
    requests_mock.get(
        f"{client.base_url}/youtube/search",
        status_code=429,
        json=error_response
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.search(query=query)

    error = exc_info.value
    assert error.error == "rate-limit-exceeded"
    assert error.message == "Rate limit exceeded"
    assert error.details == "Too many requests per minute"


# --- Metadata Tests ---

def test_metadata_youtube_video(client: Supadata, requests_mock) -> None:
    """Test getting metadata for a YouTube video."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_response = {
        "platform": "youtube",
        "type": "video",
        "id": "dQw4w9WgXcQ",
        "url": url,
        "title": "Rick Astley - Never Gonna Give You Up",
        "description": "The official video for Never Gonna Give You Up",
        "author": {
            "username": "@RickAstley",
            "displayName": "Rick Astley",
            "avatarUrl": "https://yt3.googleusercontent.com/avatar.jpg",
            "verified": True
        },
        "stats": {
            "views": 1500000000,
            "likes": 15000000,
            "comments": 500000,
            "shares": None
        },
        "media": {
            "type": "video",
            "duration": 213,
            "thumbnailUrl": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp",
            "video": {
                "url": "https://video.url",
                "duration": 212,
                "width": 1920,
                "height": 1080,
                "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
            }
        },
        "tags": ["music", "80s", "rickroll"],
        "createdAt": "2009-10-25T00:00:00.000Z"
    }
    requests_mock.get(f"{client.base_url}/metadata", json=mock_response)

    metadata = client.metadata(url=url)
    assert isinstance(metadata, Metadata)
    assert metadata.platform == "youtube"
    assert metadata.type == "video"
    assert metadata.id == "dQw4w9WgXcQ"
    assert metadata.url == url
    assert metadata.title == "Rick Astley - Never Gonna Give You Up"
    assert metadata.description == "The official video for Never Gonna Give You Up"

    assert isinstance(metadata.author, MetadataAuthor)
    assert metadata.author.username == "@RickAstley"
    assert metadata.author.display_name == "Rick Astley"
    assert metadata.author.verified is True

    assert isinstance(metadata.stats, MetadataStats)
    assert metadata.stats.views == 1500000000
    assert metadata.stats.likes == 15000000
    assert metadata.stats.comments == 500000

    assert isinstance(metadata.media, MetadataMedia)
    assert metadata.media.type == "video"
    assert metadata.media.duration == 213
    assert metadata.media.thumbnail_url == "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp"
    assert metadata.media.video is not None
    assert metadata.media.video.duration == 212
    assert metadata.media.video.width == 1920
    assert metadata.media.video.height == 1080

    assert metadata.tags == ["music", "80s", "rickroll"]
    assert metadata.created_at is not None


def test_metadata_tiktok_video(client: Supadata, requests_mock) -> None:
    """Test getting metadata for a TikTok video."""
    url = "https://www.tiktok.com/@user/video/1234567890"
    mock_response = {
        "platform": "tiktok",
        "type": "video",
        "id": "1234567890",
        "url": url,
        "title": None,
        "description": "Check out this cool video! #fyp #trending",
        "author": {
            "username": "@cooluser",
            "displayName": "Cool User",
            "avatarUrl": "https://tiktok.com/avatar.jpg",
            "verified": False
        },
        "stats": {
            "views": 1000000,
            "likes": 50000,
            "comments": 2500,
            "shares": 10000
        },
        "media": {
            "video": {
                "url": "https://video.url",
                "duration": 30,
                "width": 720,
                "height": 1280,
                "thumbnail": "https://tiktok.com/thumb.jpg"
            }
        },
        "tags": ["fyp", "trending"],
        "createdAt": "2025-01-15T12:00:00.000Z"
    }
    requests_mock.get(f"{client.base_url}/metadata", json=mock_response)

    metadata = client.metadata(url=url)
    assert isinstance(metadata, Metadata)
    assert metadata.platform == "tiktok"
    assert metadata.type == "video"
    assert metadata.id == "1234567890"
    assert metadata.title is None
    assert metadata.description == "Check out this cool video! #fyp #trending"
    assert metadata.author.username == "@cooluser"
    assert metadata.author.verified is False
    assert metadata.stats.shares == 10000
    assert metadata.tags == ["fyp", "trending"]


def test_metadata_instagram_carousel(client: Supadata, requests_mock) -> None:
    """Test getting metadata for an Instagram carousel."""
    url = "https://www.instagram.com/p/ABC123/"
    mock_response = {
        "platform": "instagram",
        "type": "carousel",
        "id": "ABC123",
        "url": url,
        "title": None,
        "description": "Beautiful sunset photos from the beach",
        "author": {
            "username": "@photographer",
            "displayName": "Photographer",
            "avatarUrl": "https://instagram.com/avatar.jpg",
            "verified": True
        },
        "stats": {
            "views": None,
            "likes": 25000,
            "comments": 350,
            "shares": None
        },
        "media": {
            "carousel": [
                {
                    "type": "image",
                    "image": {
                        "url": "https://instagram.com/photo1.jpg",
                        "width": 1080,
                        "height": 1080
                    }
                },
                {
                    "type": "image",
                    "image": {
                        "url": "https://instagram.com/photo2.jpg",
                        "width": 1080,
                        "height": 1080
                    }
                }
            ]
        },
        "tags": ["sunset", "beach", "photography"],
        "createdAt": "2025-01-10T18:30:00.000Z"
    }
    requests_mock.get(f"{client.base_url}/metadata", json=mock_response)

    metadata = client.metadata(url=url)
    assert isinstance(metadata, Metadata)
    assert metadata.platform == "instagram"
    assert metadata.type == "carousel"
    assert metadata.media.carousel is not None
    assert len(metadata.media.carousel) == 2
    assert metadata.media.carousel[0].type == "image"
    assert metadata.media.carousel[0].image is not None
    assert metadata.media.carousel[0].image.url == "https://instagram.com/photo1.jpg"


def test_metadata_error_handling(client: Supadata, requests_mock) -> None:
    """Test metadata error handling."""
    url = "https://invalid-url.com"
    error_response = {
        "error": "unsupported-platform",
        "message": "Unsupported Platform",
        "details": "The specified platform is not supported"
    }
    requests_mock.get(
        f"{client.base_url}/metadata",
        status_code=400,
        json=error_response
    )

    with pytest.raises(SupadataError) as exc_info:
        client.metadata(url=url)

    error = exc_info.value
    assert error.error == "unsupported-platform"
    assert error.message == "Unsupported Platform"
    assert error.details == "The specified platform is not supported"


def test_youtube_video_deprecation_warning(client: Supadata, requests_mock) -> None:
    """Test that youtube.video() raises deprecation warning."""
    video_id = "test123"
    mock_response = {
        "id": video_id,
        "title": "Test Video",
        "description": "Test",
        "duration": 100,
        "channel": {"id": "ch1", "name": "Channel 1"},
        "tags": [],
        "thumbnail": "https://test.com/thumb.jpg",
        "uploadDate": "2024-01-01T00:00:00.000Z",
        "viewCount": 1000,
        "likeCount": 100,
        "transcriptLanguages": []
    }
    requests_mock.get(f"{client.base_url}/youtube/video", json=mock_response)

    with pytest.warns(DeprecationWarning, match="youtube.video\\(\\) is deprecated"):
        client.youtube.video(video_id)


def test_youtube_transcript_deprecation_warning(client: Supadata, requests_mock) -> None:
    """Test that youtube.transcript() raises deprecation warning."""
    video_id = "test123"
    mock_response = {
        "content": [{"text": "Hello", "offset": 0, "duration": 1000, "lang": "en"}],
        "lang": "en",
        "availableLangs": ["en"]
    }
    requests_mock.get(f"{client.base_url}/youtube/transcript", json=mock_response)

    with pytest.warns(DeprecationWarning, match="youtube.transcript\\(\\) is deprecated"):
        client.youtube.transcript(video_id)
