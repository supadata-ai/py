# Supadata Python SDK

[![PyPI version](https://badge.fury.io/py/supadata.svg)](https://badge.fury.io/py/supadata)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](http://opensource.org/licenses/MIT)

The official Python SDK for Supadata.

Get your free API key at [supadata.ai](https://supadata.ai) and start scraping data in minutes.

## Installation

```bash
pip install supadata
```

## Usage

```python
from supadata import Supadata, SupadataError

# Initialize the client
supadata = Supadata(api_key="YOUR_API_KEY")

# Get YouTube transcript with Spanish language preference
transcript = supadata.youtube.transcript(video_id="VIDEO_ID", lang="es")
print(f"Got transcript {transcript.content}")

# Translate YouTube transcript to Spanish
translated = supadata.youtube.translate(
    video_id="VIDEO_ID",
    lang="es"
)
print(f"Got translated transcript in {translated.lang}")

# Get plain text transcript
text_transcript = supadata.youtube.transcript(
    video_id="VIDEO_ID",
    text=True
)
print(text_transcript.content)

# Scrape web content
web_content = supadata.web.scrape("https://supadata.ai")
print(f"Page title: {web_content.name}")
print(f"Page content: {web_content.content}")

# Get YouTube video details
video = supadata.youtube.video(video_id="VIDEO_ID")
print(f"Video title: {video.title}")
print(f"Channel: {video.channel_title}")
print(f"Views: {video.view_count}")

# Get YouTube channel details
channel = supadata.youtube.channel(channel_id="CHANNEL_ID")
print(f"Channel: {channel.title}")
print(f"Subscribers: {channel.subscriber_count}")
print(f"Videos: {channel.video_count}")

# Get YouTube playlist details
playlist = supadata.youtube.playlist(playlist_id="PLAYLIST_ID")
print(f"Playlist: {playlist.title}")
print(f"Videos count: {playlist.item_count}")

# Get videos from a YouTube channel
channel_videos = supadata.youtube.channel_videos(
    channel_id="CHANNEL_ID",
    max_results=10,  # Optional: limit the number of videos
    published_after="2023-01-01T00:00:00Z",  # Optional: filter by publish date
    published_before="2023-12-31T23:59:59Z"  # Optional: filter by publish date
)
print(f"Channel: {channel_videos.channel_title}")
for video in channel_videos.videos:
    print(f"Video: {video.title}, Views: {video.view_count}")

# Get videos from a YouTube playlist
playlist_videos = supadata.youtube.playlist_videos(
    playlist_id="PLAYLIST_ID",
    max_results=10  # Optional: limit the number of videos
)
print(f"Playlist: {playlist_videos.playlist_title}")
for video in playlist_videos.videos:
    print(f"Video: {video.title}, Views: {video.view_count}")

# Map website URLs
site_map = supadata.web.map("https://supadata.ai")
print(f"Found {len(site_map.urls)} URLs")

# Start a crawl job
crawl_job = supadata.web.crawl(
    url="https://supadata.ai",
    limit=100  # Optional: limit the number of pages to crawl
)
print(f"Started crawl job: {crawl_job.job_id}")

# Get crawl results
# This automatically handles pagination and returns all pages
try:
    pages = supadata.web.get_crawl_results(job_id=crawl_job.job_id)
    for page in pages:
        print(f"Crawled page: {page.url}")
        print(f"Page title: {page.name}")
        print(f"Content: {page.content}")
except SupadataError as e:
    print(f"Crawl job failed: {e}")
```

## Error Handling

The SDK uses custom `SupadataError` exceptions that provide structured error information:

```python
from supadata.errors import SupadataError

try:
    transcript = supadata.youtube.transcript(video_id="INVALID_ID")
except SupadataError as error:
    print(f"Error code: {error.error}")
    print(f"Error message: {error.message}")
    print(f"Error details: {error.details}")
    if error.documentation_url:
        print(f"Documentation: {error.documentation_url}")
```

## API Reference

See the [Documentation](https://supadata.ai/documentation) for more details on all possible parameters and options.

## License

MIT
