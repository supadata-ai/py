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
from supadata import Supadata

# Initialize the client
supadata = Supadata(api_key="YOUR_API_KEY")

# Get YouTube transcript
transcript = supadata.youtube.transcript(video_id="VIDEO_ID")
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

# Map website URLs
site_map = supadata.web.map("https://supadata.ai")
print(f"Found {len(site_map.urls)} URLs")
```

## Error Handling

The SDK uses the standard `requests` library and will raise `requests.exceptions.HTTPError` for API-related errors. The error object contains structured error information:

```python
from requests.exceptions import HTTPError

try:
    transcript = supadata.youtube.transcript(video_id="INVALID_ID")
except HTTPError as error:
    error_data = error.args[0]  # This is an Error object
    print(f"Error code: {error_data.code}")
    print(f"Error title: {error_data.title}")
    print(f"Error description: {error_data.description}")
    if error_data.documentation_url:
        print(f"Documentation: {error_data.documentation_url}")
```

## API Reference

See the [Documentation](https://supadata.ai/documentation) for more details on all possible parameters and options.

## License

MIT
