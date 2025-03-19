"""Tests for the Supadata client."""

from datetime import datetime

import pytest

from supadata import (
    CrawlJob,
    CrawlPage,
    Map,
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
    """Test getting YouTube transcript with chunks."""
    video_id = "test123"
    mock_response = {
        "content": [{"text": "Hello", "offset": 0, "duration": 1000, "lang": "en"}],
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/youtube/transcript", json=mock_response)

    transcript = client.youtube.transcript(video_id=video_id)
    assert isinstance(transcript, Transcript)
    assert isinstance(transcript.content[0], TranscriptChunk)
    assert transcript.content[0].text == "Hello"
    assert transcript.lang == "en"
    assert transcript.available_langs == ["en", "es"]


def test_get_transcript_text(client: Supadata, requests_mock) -> None:
    """Test getting YouTube transcript as plain text."""
    video_id = "test123"
    mock_response = {
        "content": "Hello, this is a test transcript",
        "lang": "en",
        "availableLangs": ["en", "es"],
    }
    requests_mock.get(f"{client.base_url}/youtube/transcript", json=mock_response)

    transcript = client.youtube.transcript(video_id=video_id, text=True)
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
    video_id = "invalid"
    error_response = {
        "error": "video-not-found",
        "message": "Video Not Found",
        "details": "The specified video was not found",
        "documentationUrl": "https://docs.test.com/errors#video-not-found",
    }
    requests_mock.get(
        f"{client.base_url}/youtube/transcript",
        status_code=400,  # Changed from 404 to 400 since 404 is handled as gateway error
        json=error_response,
        headers={"content-type": "application/json"},
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.transcript(video_id=video_id)

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


def test_gateway_error_403(client: Supadata, requests_mock) -> None:
    """Test handling of 403 gateway error."""
    requests_mock.get(
        f"{client.base_url}/youtube/transcript",
        status_code=403,
        text="Please ensure you have provided a valid API key",
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.transcript(video_id="test123")

    error = exc_info.value
    assert error.error == "invalid-request"
    assert error.message == "Invalid or missing API key"
    assert error.details == "Please ensure you have provided a valid API key"


def test_gateway_error_404(client: Supadata, requests_mock) -> None:
    """Test handling of 404 gateway error."""
    requests_mock.get(
        f"{client.base_url}/invalid/endpoint",
        status_code=404,
        text="The API endpoint you are trying to access does not exist",
    )

    with pytest.raises(SupadataError) as exc_info:
        client._request("GET", "/invalid/endpoint")

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The API endpoint you are trying to access does not exist"


def test_gateway_error_429(client: Supadata, requests_mock) -> None:
    """Test handling of 429 gateway error."""
    requests_mock.get(
        f"{client.base_url}/youtube/transcript",
        status_code=429,
        text="You have exceeded the allowed request rate or quota limits",
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.transcript(video_id="test123")

    error = exc_info.value
    assert error.error == "limit-exceeded"
    assert error.message == "Limit exceeded"
    assert error.details == "You have exceeded the allowed request rate or quota limits"


def test_youtube_video(client: Supadata, requests_mock) -> None:
    video_id = "pEfrdAtAmqk"
    mock_response = {
        "id": video_id,
        "duration": 1002,
        "description": "The programming iceberg is complete roadmap to the loved, ...",
        "title": "God-Tier Developer Roadmap",
        "channel": {"id": "UCsBjURrPoezykLs9EqgamOA", "name": "Fireship"},
        "tags": ["#iceberg", "#learntocode", "#programming"],
        "thumbnail": "https://i.ytimg.com/vi/pEfrdAtAmqk/maxresdefault.jpg",
        "uploadDate": "2022-08-24T00:00:00.000Z",
        "viewCount": 7388353,
        "likeCount": 262086,
        "transcriptLanguages": ["en"],
    }

    requests_mock.get(
        f"{client.base_url}/youtube/video?id={video_id}", json=mock_response
    )

    video = client.youtube.video(video_id)
    assert isinstance(video, YoutubeVideo)
    assert video.id == mock_response["id"]
    assert video.duration == mock_response["duration"]
    assert video.description == mock_response["description"]
    assert video.title == mock_response["title"]
    assert video.channel == mock_response["channel"]
    assert video.tags == mock_response["tags"]
    assert video.uploaded_date == datetime.fromisoformat(mock_response["uploadDate"])
    assert video.view_count == mock_response["viewCount"]
    assert video.like_count == mock_response["likeCount"]


def test_youtube_video_invalid_id(client: Supadata, requests_mock) -> None:
    video_id = "pEfrdAtmqk"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
    }
    requests_mock.get(
        f"{client.base_url}/youtube/video?id={video_id}",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.video(video_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The requested item could not be found"


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
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The requested item could not be found"


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
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The requested item could not be found"


def test_youtube_channel_videos(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "videoIds": [
            "PQ2WjtaPfXU",
            "UIVADiGfwWc",
        ]
    }

    requests_mock.get(
        f"{client.base_url}/youtube/channel/videos?id={channel_id}", json=mock_response
    )
    channel_videos = client.youtube.channel.videos(channel_id)
    assert isinstance(channel_videos, list)
    assert len(channel_videos) == len(mock_response["videoIds"])
    for i in channel_videos:
        assert i in mock_response["videoIds"]


def test_youtube_channel_videos_invalid_id(client: Supadata, requests_mock) -> None:
    channel_id = "UCsBjURrPoezyLs9EqgamOA"
    mock_response = {
        "error": "not-found",
        "message": "The requested item could not be found",
        "details": "The requested item could not be found.",
    }
    requests_mock.get(
        f"{client.base_url}/youtube/channel/videos?id={channel_id}",
        status_code=404,
        json=mock_response,
    )

    with pytest.raises(SupadataError) as exc_info:
        client.youtube.channel.videos(channel_id)

    error = exc_info.value
    assert error.error == "not-found"
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The requested item could not be found"


def test_youtube_playlist_videos(client: Supadata, requests_mock) -> None:
    playlist_id = "PL0vfts4VzfNjQOM9VClyL5R0LeuTxlAR3"
    mock_response = {
        "videoIds": [
            "zDNaUi2cjv4",
            "B1t4Fjlomi8",
        ]
    }
    requests_mock.get(
        f"{client.base_url}/youtube/playlist/videos?id={playlist_id}",
        json=mock_response,
    )

    playlist_videos = client.youtube.playlist.videos(playlist_id)
    assert isinstance(playlist_videos, list)
    assert len(playlist_videos) == len(mock_response["videoIds"])
    for i in playlist_videos:
        assert i in mock_response["videoIds"]


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
    assert error.message == "Endpoint does not exist or resource not found"
    assert error.details == "The requested item could not be found"
