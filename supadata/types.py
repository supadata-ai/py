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
class Error:
    """Standard error response format.
    
    Attributes:
        code: Error code identifying the type of error
        title: Human readable error title
        description: Detailed error description
        documentation_url: URL to error documentation
    """
    code: str
    title: str
    description: str
    documentation_url: Optional[str]

