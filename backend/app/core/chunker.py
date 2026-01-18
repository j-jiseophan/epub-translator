from typing import List
from dataclasses import dataclass

from .epub_parser import TranslatableElement


@dataclass
class TranslationChunk:
    chunk_id: int
    elements: List[TranslatableElement]
    combined_text: str


class TextChunker:
    def __init__(self, max_chars: int = 2000):
        """
        Initialize chunker with maximum characters per chunk.
        Using chars as a rough proxy for tokens (4 chars ≈ 1 token).
        """
        self.max_chars = max_chars

    def chunk_elements(
        self, elements: List[TranslatableElement]
    ) -> List[TranslationChunk]:
        """
        Group elements into chunks that fit within the character limit.
        Each element is kept intact - we don't split individual paragraphs.
        """
        chunks = []
        current_elements = []
        current_length = 0
        chunk_id = 0

        for element in elements:
            element_length = len(element.text)

            if element_length > self.max_chars:
                if current_elements:
                    chunks.append(self._create_chunk(chunk_id, current_elements))
                    chunk_id += 1
                    current_elements = []
                    current_length = 0

                chunks.append(self._create_chunk(chunk_id, [element]))
                chunk_id += 1
                continue

            if current_length + element_length > self.max_chars:
                if current_elements:
                    chunks.append(self._create_chunk(chunk_id, current_elements))
                    chunk_id += 1
                current_elements = [element]
                current_length = element_length
            else:
                current_elements.append(element)
                current_length += element_length

        if current_elements:
            chunks.append(self._create_chunk(chunk_id, current_elements))

        return chunks

    def _create_chunk(
        self, chunk_id: int, elements: List[TranslatableElement]
    ) -> TranslationChunk:
        """Create a chunk with combined text using delimiters."""
        texts = []
        for i, elem in enumerate(elements):
            texts.append(f"[{i}] {elem.text}")

        combined = "\n\n".join(texts)

        return TranslationChunk(
            chunk_id=chunk_id,
            elements=elements,
            combined_text=combined,
        )

    def parse_translated_chunk(
        self, chunk: TranslationChunk, translated_text: str
    ) -> dict[str, str]:
        """
        Parse translated text back into individual element translations.
        Returns a dict mapping element_id to translated text.
        """
        translations = {}
        parts = translated_text.split("\n\n")

        for i, elem in enumerate(chunk.elements):
            if i < len(parts):
                text = parts[i].strip()
                if text.startswith(f"[{i}]"):
                    text = text[len(f"[{i}]") :].strip()
                translations[elem.element_id] = text
            else:
                translations[elem.element_id] = elem.text

        return translations
