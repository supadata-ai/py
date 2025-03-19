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
transcript = supadata.youtube.transcript(video_id="dQw4w9WgXcQ", lang="es")
print(f"Got transcript {transcript.content}")

# Translate YouTube transcript to Spanish
translated = supadata.youtube.translate(
    video_id="dQw4w9WgXcQ",
    lang="es"
)
print(f"Got translated transcript in {translated.lang}")

# Get plain text transcript
text_transcript = supadata.youtube.transcript(
    video_id="dQw4w9WgXcQ",
    text=True
)
print(text_transcript.content)

# Scrape web content
web_content = supadata.web.scrape("https://supadata.ai")
print(f"Page title: {web_content.name}")
print(f"Page content: {web_content.content}")

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

# Get Video Metadata
video = supadata.youtube.video(id="https://youtu.be/dQw4w9WgXcQ") # can be url or video id
print(f"Video: {video}")

# Get Channel Metadata
channel = supadata.youtube.channel(id="https://youtube.com/@RickAstleyVEVO") # can be url, channel id, handle
print(f"Channel: {channel}")

# Get a list of the channel video IDs
channel_videos = supadata.youtube.channel.videos(id="RickAstleyVEVO") # can be url, channel id, or handle
print(f"Channel Video IDs: {channel_videos}")

# Get Playlist metadata
playlist = supadata.youtube.playlist(id="PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc") # can be url or playlist id
print(f"Playlist: {playlist}")

# Get a list of the playlist video IDs
playlist_videos = supadata.youtube.playlist.videos(id="https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc") # can be url or playlist id
print(f"Playlist Videos IDs: {playlist_videos}")
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
