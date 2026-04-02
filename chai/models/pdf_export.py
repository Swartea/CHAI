"""PDF export models and configuration.

This module provides comprehensive PDF export models with support for
page layout, fonts, margins, headers/footers, and multiple output templates
suitable for print publishing.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PDFTemplate(str, Enum):
    """PDF output template styles."""

    SIMPLE = "simple"  # Basic text with minimal formatting
    STANDARD = "standard"  # Standard PDF with TOC and page headers
    DETAILED = "detailed"  # Full PDF with all metadata, TOC, and print-ready formatting


class PDFPageSize(str, Enum):
    """Standard page sizes for PDF output."""

    A4 = "A4"
    A5 = "A5"
    B5 = "B5"
    LETTER = "letter"
    LEGAL = "legal"


class PDFFont(str, Enum):
    """Font options for PDF export."""

    SIMSUN = "simsun"  # 宋体
    TIMES = "times"
    SERIF = "serif"
    SANS_SERIF = "sans-serif"


class PDFExportConfig(BaseModel):
    """Configuration for PDF export."""

    template: PDFTemplate = Field(
        default=PDFTemplate.STANDARD,
        description="Output template style"
    )
    page_size: PDFPageSize = Field(
        default=PDFPageSize.A5,
        description="Page size for PDF"
    )
    include_table_of_contents: bool = Field(
        default=True,
        description="Include table of contents"
    )
    include_chapter_summaries: bool = Field(
        default=True,
        description="Include chapter summaries"
    )
    include_character_list: bool = Field(
        default=False,
        description="Include character listing in front matter"
    )
    include_world_setting: bool = Field(
        default=False,
        description="Include world setting summary in front matter"
    )
    include_scene_content: bool = Field(
        default=False,
        description="Include scene-level content and separators"
    )
    include_word_counts: bool = Field(
        default=True,
        description="Include word count statistics"
    )
    paragraph_spacing: bool = Field(
        default=True,
        description="Add spacing between paragraphs"
    )
    scene_separators: bool = Field(
        default=True,
        description="Use separators between scenes"
    )
    indent_first_line: bool = Field(
        default=True,
        description="Indent first line of each paragraph"
    )

    # Page layout
    left_margin: float = Field(
        default=2.0,
        description="Left margin in cm"
    )
    right_margin: float = Field(
        default=2.0,
        description="Right margin in cm"
    )
    top_margin: float = Field(
        default=2.0,
        description="Top margin in cm"
    )
    bottom_margin: float = Field(
        default=2.0,
        description="Bottom margin in cm"
    )

    # Fonts
    body_font: PDFFont = Field(
        default=PDFFont.SIMSUN,
        description="Font for body text"
    )
    title_font: PDFFont = Field(
        default=PDFFont.SIMSUN,
        description="Font for title"
    )
    body_font_size: int = Field(
        default=11,
        description="Body font size in points"
    )
    title_font_size: int = Field(
        default=24,
        description="Title font size in points"
    )
    chapter_title_font_size: int = Field(
        default=16,
        description="Chapter title font size in points"
    )

    # Line spacing
    line_spacing: float = Field(
        default=1.8,
        description="Line spacing multiplier"
    )

    # Headers and footers
    include_page_numbers: bool = Field(
        default=True,
        description="Include page numbers"
    )
    include_chapter_headers: bool = Field(
        default=True,
        description="Include chapter title in page header"
    )


class PDFMetadata(BaseModel):
    """PDF metadata information."""

    title: str = ""
    subtitle: str = ""
    author: str = "CHAI"
    language: str = "zh-CN"
    publisher: str = ""
    publish_date: str = ""
    genre: str = ""
    description: str = ""
    isbn: str = ""
    total_words: int = 0
    total_pages: int = 0


class PDFChapterRef(BaseModel):
    """Reference to a chapter in the PDF."""

    chapter_id: str
    chapter_number: int
    chapter_title: str
    is_prologue: bool = False
    is_epilogue: bool = False
    start_page: int = 0
    word_count: int = 0


class PDFVolumeRef(BaseModel):
    """Reference to a volume in the PDF."""

    volume_id: str
    volume_number: int
    volume_title: str
    description: str = ""
    chapters: list[PDFChapterRef] = Field(default_factory=list)
    start_page: int = 0
    word_count: int = 0


class PDFTableOfContentsEntry(BaseModel):
    """Entry in the table of contents."""

    title: str
    page_number: int
    level: int = Field(default=1, description="TOC level (1=volume, 2=chapter)")
    volume_number: Optional[int] = None
    chapter_number: Optional[int] = None


class PDFExportResult(BaseModel):
    """Result of PDF manuscript generation."""

    config: PDFExportConfig
    metadata: Optional[PDFMetadata] = None
    volumes: list[PDFVolumeRef] = Field(default_factory=list)
    toc: list[PDFTableOfContentsEntry] = Field(default_factory=list)
    word_count: int = 0
    total_pages: int = 0

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
