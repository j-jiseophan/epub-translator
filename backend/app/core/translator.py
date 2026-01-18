import asyncio
import os
import time
from typing import Callable, Awaitable
from dataclasses import dataclass

from .epub_parser import EPUBParser
from .chunker import TextChunker
from .ollama_client import OllamaClient
from ..models.schemas import TranslationStatus


@dataclass
class TranslationJob:
    job_id: str
    file_id: str
    source_lang: str
    target_lang: str
    model: str
    status: TranslationStatus = TranslationStatus.PENDING
    current_chapter: int = 0
    total_chapters: int = 0
    current_chunk: int = 0
    total_chunks: int = 0  # chunks in current chapter
    completed_chunks: int = 0  # total completed chunks across all chapters
    total_chunks_all: int = 0  # total chunks across all chapters
    start_time: float | None = None
    error_message: str | None = None
    output_path: str | None = None


ProgressCallback = Callable[[dict], Awaitable[None]]


class TranslationOrchestrator:
    def __init__(
        self,
        job: TranslationJob,
        upload_dir: str,
        output_dir: str,
        progress_callback: ProgressCallback,
    ):
        self.job = job
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.is_cancelled = False

        self.ollama = OllamaClient()
        self.chunker = TextChunker(max_chars=2000)

    async def run(self) -> str:
        """Run the full translation pipeline. Returns output path."""
        file_path = os.path.join(self.upload_dir, f"{self.job.file_id}.epub")
        self.job.start_time = time.time()

        try:
            self.job.status = TranslationStatus.PARSING
            await self._notify_progress()

            parser = EPUBParser(file_path)
            chapters = parser.get_chapters()
            self.job.total_chapters = len(chapters)

            # Pre-calculate total chunks across all chapters
            all_chapter_chunks = []
            for chapter in chapters:
                chunks = self.chunker.chunk_elements(chapter.elements)
                all_chapter_chunks.append((chapter, chunks))
                self.job.total_chunks_all += len(chunks)

            self.job.status = TranslationStatus.TRANSLATING
            await self._notify_progress()

            for chapter, chunks in all_chapter_chunks:
                self._check_cancelled()

                self.job.current_chapter = chapter.index + 1
                self.job.total_chunks = len(chunks)

                all_translations = {}

                for chunk in chunks:
                    self._check_cancelled()

                    self.job.current_chunk = chunk.chunk_id + 1
                    await self._notify_progress(
                        chapter_title=chapter.name,
                        preview_original=chunk.combined_text[:100],
                    )

                    translated = await self._translate_with_retry(chunk.combined_text)

                    translations = self.chunker.parse_translated_chunk(
                        chunk, translated
                    )
                    all_translations.update(translations)
                    self.job.completed_chunks += 1

                    await self._notify_progress(
                        chapter_title=chapter.name,
                        preview_original=chunk.combined_text[:100],
                        preview_translated=translated[:100],
                    )

                parser.apply_translations(chapter.item, all_translations)

            self.job.status = TranslationStatus.REBUILDING
            await self._notify_progress()

            output_filename = f"translated_{self.job.job_id}.epub"
            output_path = os.path.join(self.output_dir, output_filename)
            parser.save(output_path)

            self.job.status = TranslationStatus.COMPLETED
            self.job.output_path = output_path
            await self._notify_progress()

            return output_path

        except asyncio.CancelledError:
            self.job.status = TranslationStatus.CANCELLED
            await self.ollama.unload_model(self.job.model)
            await self._notify_progress()
            raise

        except Exception as e:
            self.job.status = TranslationStatus.FAILED
            self.job.error_message = str(e)
            await self._notify_progress()
            raise

        finally:
            await self.ollama.close()

    def _check_cancelled(self):
        """Check if cancelled and raise CancelledError if so."""
        if self.is_cancelled:
            raise asyncio.CancelledError("Translation cancelled by user")

    async def _translate_with_retry(self, text: str, max_retries: int = 3) -> str:
        """Translate with retry on failure."""
        last_error: Exception | None = None

        for attempt in range(max_retries):
            self._check_cancelled()
            try:
                return await self.ollama.translate(
                    text=text,
                    source_lang=self.job.source_lang,
                    target_lang=self.job.target_lang,
                    model=self.job.model,
                )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)

        raise last_error or Exception("Translation failed")

    async def _notify_progress(
        self,
        chapter_title: str = "",
        preview_original: str = "",
        preview_translated: str = "",
    ) -> None:
        """Send progress update via callback."""
        percentage = 0.0
        estimated_time = 0.0
        if self.job.total_chunks_all > 0:
            percentage = (self.job.completed_chunks / self.job.total_chunks_all) * 100
            percentage = min(percentage, 100.0)  # Clamp to 100%

            if self.job.start_time and self.job.completed_chunks > 0:
                elapsed = time.time() - self.job.start_time
                avg_time_per_chunk = elapsed / self.job.completed_chunks
                remaining_chunks = self.job.total_chunks_all - self.job.completed_chunks
                estimated_time = avg_time_per_chunk * remaining_chunks

        message = {
            "type": "progress",
            "job_id": self.job.job_id,
            "status": self.job.status.value,
            "chapter_current": self.job.current_chapter,
            "chapter_total": self.job.total_chapters,
            "chapter_title": chapter_title,
            "chunk_current": self.job.current_chunk,
            "chunk_total": self.job.total_chunks,
            "percentage": round(percentage, 1),
            "estimated_time_remaining": round(estimated_time, 1),
            "preview_original": preview_original,
            "preview_translated": preview_translated,
            "error_message": self.job.error_message,
            "download_url": f"/api/download/{self.job.job_id}"
            if self.job.status == TranslationStatus.COMPLETED
            else None,
        }

        await self.progress_callback(message)

    def cancel(self):
        """Mark the job as cancelled."""
        self.is_cancelled = True
