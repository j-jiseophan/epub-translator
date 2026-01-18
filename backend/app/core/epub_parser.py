import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TranslatableElement:
    element_id: str
    text: str
    tag_name: str


@dataclass
class Chapter:
    index: int
    name: str
    item: epub.EpubHtml
    elements: List[TranslatableElement]


class EPUBParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        # ignore_ncx=False to avoid lxml parsing issues with HTML comments in nav
        self.book = epub.read_epub(file_path, options={"ignore_ncx": False})

    def get_chapters(self) -> List[Chapter]:
        """Extract all document items (chapters) from EPUB."""
        chapters = []
        items = list(self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

        chapter_index = 0
        for item in items:
            elements = self._extract_translatable_elements(item)
            if elements:
                chapter = Chapter(
                    index=chapter_index,
                    name=item.get_name() or f"Chapter {chapter_index + 1}",
                    item=item,
                    elements=elements,
                )
                chapters.append(chapter)
                chapter_index += 1

        return chapters

    def _extract_translatable_elements(
        self, item: epub.EpubHtml
    ) -> List[TranslatableElement]:
        """Extract text elements that need translation."""
        content = item.get_content()
        soup = BeautifulSoup(content, "lxml")

        translatable_tags = [
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "td",
            "th",
            "figcaption",
            "blockquote",
            "title",
        ]

        elements = []
        element_counter = 0

        for tag in soup.find_all(translatable_tags):
            text = tag.get_text(strip=True)
            if text and len(text) > 1:
                element_id = f"elem_{element_counter}"
                tag["data-translate-id"] = element_id
                elements.append(
                    TranslatableElement(
                        element_id=element_id,
                        text=text,
                        tag_name=tag.name,
                    )
                )
                element_counter += 1

        item.set_content(str(soup).encode("utf-8"))
        return elements

    def apply_translations(
        self, item: epub.EpubHtml, translations: dict[str, str]
    ) -> None:
        """Apply translations to a chapter item."""
        content = item.get_content()
        soup = BeautifulSoup(content, "lxml")

        for element_id, translated_text in translations.items():
            tag = soup.find(attrs={"data-translate-id": element_id})
            if tag:
                self._replace_text_content(tag, translated_text)
                del tag["data-translate-id"]

        item.set_content(str(soup).encode("utf-8"))

    def _replace_text_content(self, tag, new_text: str) -> None:
        """Replace text content while preserving inline tags as much as possible."""
        if tag.string:
            tag.string.replace_with(new_text)
        else:
            tag.clear()
            tag.append(new_text)

    def save(self, output_path: str) -> None:
        """Save the translated EPUB."""
        epub.write_epub(output_path, self.book)
