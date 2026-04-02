"""Markdown manuscript export models and configuration."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ManuscriptTemplate(str, Enum):
    """Manuscript output template styles."""

    SIMPLE = "simple"  # Basic text with minimal formatting
    STANDARD = "standard"  # Standard manuscript with TOC and summaries
    DETAILED = "detailed"  # Full manuscript with all metadata


class ManuscriptExportConfig(BaseModel):
    """Configuration for manuscript export."""

    template: ManuscriptTemplate = Field(
        default=ManuscriptTemplate.STANDARD,
        description="Output template style"
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
        default=False,
        description="Indent first line of each paragraph"
    )


class ChapterManuscriptSection(BaseModel):
    """A section within a chapter manuscript."""

    section_type: str = Field(description="Section type: heading, content, scene, summary, etc.")
    content: str = Field(description="Section content")
    level: int = Field(default=1, description="Heading level (1-6)")


class ChapterManuscript(BaseModel):
    """Formatted chapter manuscript."""

    chapter_id: str
    chapter_number: int
    chapter_title: str
    is_prologue: bool = False
    is_epilogue: bool = False
    sections: list[ChapterManuscriptSection] = Field(default_factory=list)
    word_count: int = 0


class VolumeManuscript(BaseModel):
    """Formatted volume manuscript."""

    volume_id: str
    volume_number: int
    volume_title: str
    description: str = ""
    chapters: list[ChapterManuscript] = Field(default_factory=list)
    word_count: int = 0


class FrontMatter(BaseModel):
    """Front matter content for manuscript."""

    title: str = ""
    subtitle: str = ""
    author: str = "CHAI"
    genre: str = ""
    total_words: int = 0
    total_chapters: int = 0
    total_volumes: int = 0
    character_list: list[str] = Field(default_factory=list)
    world_summary: str = ""
    creation_date: str = ""


class BackMatter(BaseModel):
    """Back matter content for manuscript."""

    word_count_summary: str = ""
    chapter_word_counts: list[dict] = Field(default_factory=list)


class TableOfContentsEntry(BaseModel):
    """Table of contents entry."""

    title: str
    level: int  # 1 for volume, 2 for chapter
    chapter_number: Optional[int] = None
    volume_number: Optional[int] = None
    anchor: str = ""


class ManuscriptTOC(BaseModel):
    """Table of contents for manuscript."""

    entries: list[TableOfContentsEntry] = Field(default_factory=list)


class ManuscriptExportResult(BaseModel):
    """Result of manuscript export operation."""

    content: str = Field(default="", description="Generated manuscript content")
    config: ManuscriptExportConfig = Field(default_factory=ManuscriptExportConfig, description="Export configuration used")
    front_matter: Optional[FrontMatter] = None
    back_matter: Optional[BackMatter] = None
    toc: Optional[ManuscriptTOC] = None
    word_count: int = 0