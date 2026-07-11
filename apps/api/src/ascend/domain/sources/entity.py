from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class SourceType(str, Enum):
    WEB_ARTICLE = "WEB_ARTICLE"
    YOUTUBE = "YOUTUBE"
    PDF = "PDF"
    BOOK = "BOOK"
    MARKDOWN = "MARKDOWN"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    TWEET = "TWEET"
    LOCAL_FILE = "LOCAL_FILE"
    MANUAL = "MANUAL"


@dataclass
class Source:
    id: UUID
    title: str
    source_type: SourceType
    created_at: datetime
    updated_at: datetime
    uri: str | None = None
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    metadata_json: str = "{}"
