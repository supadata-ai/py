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

### Initialization

```python
from supadata import Supadata, SupadataError

# Initialize the client
supadata = Supadata(api_key="YOUR_API_KEY")
```

### Transcripts

```python
# Get transcript from any supported platform (YouTube, TikTok, Twitter, file URLs)
transcript = supadata.transcript(
    url="https://x.com/SpaceX/status/1481651037291225113",
    lang="en",  # Optional: preferred language
    text=True,  # Optional: return plain text instead of timestamped chunks
    mode="auto"  # Optional: "native", "auto", or "generate"
)

# For immediate results
if hasattr(transcript, 'content'):
    print(f"Transcript: {transcript.content}")
    print(f"Language: {transcript.lang}")
else:
    # For async processing (large files)
    print(f"Processing started with job ID: {transcript.job_id}")
    # Poll for results using existing batch.get_batch_results method
```

### YouTube

```python
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

# Get Video Metadata
video = supadata.youtube.video(id="https://youtu.be/dQw4w9WgXcQ") # can be url or video id
print(f"Video: {video}")

# Get Channel Metadata
channel = supadata.youtube.channel(id="https://youtube.com/@RickAstleyVEVO") # can be url, channel id, handle
print(f"Channel: {channel}")

# Get video IDs from a YouTube channel
channel_videos = supadata.youtube.channel.videos(
    id="RickAstleyVEVO",  # can be url, channel id, or handle
    type="all",  # 'all', 'video', 'short', or 'live'
    limit=50
)
print(f"Regular videos: {channel_videos.video_ids}")
print(f"Shorts: {channel_videos.short_ids}")
print(f"Live: {channel_videos.live_ids}")

# Get Playlist metadata
playlist = supadata.youtube.playlist(id="PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc") # can be url or playlist id
print(f"Playlist: {playlist}")

# Get video IDs from a YouTube playlist
playlist_videos = supadata.youtube.playlist.videos(
    id="https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",  # can be url or playlist id
    limit=50
)
print(f"Regular videos: {playlist_videos.video_ids}")
print(f"Shorts: {playlist_videos.short_ids}")
print(f"Live: {playlist_videos.live_ids}")

# Batch Operations
transcript_batch_job = supadata.youtube.transcript.batch(
    video_ids=["dQw4w9WgXcQ", "xvFZjo5PgG0"],
    # playlist_id="PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc", # alternatively
    # channel_id="UC_9-kyTW8ZkZNDHQJ6FgpwQ", # alternatively
    lang="en",  # Optional: specify preferred transcript language
    limit=100   # Optional: limit for playlist/channel
)
print(f"Started transcript batch job: {transcript_batch_job.job_id}")

# Start a batch job to get video metadata for a playlist
video_batch_job = supadata.youtube.video.batch(
    playlist_id="PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
    limit=50
)
print(f"Started video metadata batch job: {video_batch_job.job_id}")

# Get the results of a batch job (poll until status is 'completed' or 'failed')
batch_results = supadata.youtube.batch.get_batch_results(job_id=transcript_batch_job.job_id)
print(f"Job status: {batch_results.status}")
print(f"Stats: {batch_results.stats.succeeded}/{batch_results.stats.total} videos processed")
print(f"First result: {batch_results.results[0].video_id if batch_results.results else 'No results yet'}")
```

### Web

```python
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
