from pydantic import BaseModel
from enum import Enum
from typing import Optional


class TranslationStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    TRANSLATING = "translating"
    REBUILDING = "rebuilding"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranslationRequest(BaseModel):
    file_id: str
    source_language: str
    target_language: str
    model: str


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    chapter_count: int


class JobStatusResponse(BaseModel):
    job_id: str
    status: TranslationStatus
    current_chapter: int = 0
    total_chapters: int = 0
    current_chunk: int = 0
    total_chunks: int = 0
    percentage: float = 0.0
    error_message: Optional[str] = None
    download_url: Optional[str] = None


class ProgressMessage(BaseModel):
    type: str
    job_id: str
    status: TranslationStatus
    chapter_current: int = 0
    chapter_total: int = 0
    chapter_title: str = ""
    chunk_current: int = 0
    chunk_total: int = 0
    percentage: float = 0.0
    estimated_time_remaining: float = 0.0
    preview_original: str = ""
    preview_translated: str = ""
    error_message: Optional[str] = None
    download_url: Optional[str] = None
