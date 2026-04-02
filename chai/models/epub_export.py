"""EPUB export models and configuration.

This module provides comprehensive EPUB export models with support for
metadata, chapter formatting, navigation, and multiple output templates
following the EPUB 2.0/3.0 specifications.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EPUBTemplate(str, Enum):
    """EPUB output template styles."""

    SIMPLE = "simple"  # Basic text with minimal formatting
    STANDARD = "standard"  # Standard EPUB with TOC and summaries
    DETAILED = "detailed"  # Full EPUB with all metadata and styling


class EPUBExportConfig(BaseModel):
    """Configuration for EPUB export."""

    template: EPUBTemplate = Field(
        default=EPUBTemplate.STANDARD,
        description="Output template style"
    )
    epub_version: str = Field(
        default="2.0",
        description="EPUB version (2.0 or 3.0)"
    )
    include_table_of_contents: bool = Field(
        default=True,
        description="Include navigation document"
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
    font_family: str = Field(
        default="serif",
        description="Font family for body text (serif, sans-serif, monospace)"
    )
    font_size: int = Field(
        default=16,
        description="Base font size in points"
    )
    line_height: float = Field(
        default=1.8,
        description="Line height multiplier"
    )
    text_align: str = Field(
        default="justify",
        description="Text alignment (justify, left, center)"
    )
    chapter_title_align: str = Field(
        default="center",
        description="Chapter title alignment (center, left)"
    )


class EPUBMetadata(BaseModel):
    """EPUB metadata information."""

    title: str = ""
    subtitle: str = ""
    author: str = "CHAI"
    language: str = "zh-CN"
    publisher: str = ""
    publish_date: str = ""
    genre: str = ""
    description: str = ""
    isbn: str = ""
    rights: str = ""
    total_words: int = 0
    total_chapters: int = 0
    total_volumes: int = 0
    creation_date: str = ""


class EPUBChapterRef(BaseModel):
    """Reference to a chapter in the EPUB."""

    chapter_id: str
    chapter_number: int
    chapter_title: str
    is_prologue: bool = False
    is_epilogue: bool = False
    file_path: str = ""


class EPUBVolumeRef(BaseModel):
    """Reference to a volume in the EPUB."""

    volume_id: str
    volume_number: int
    volume_title: str
    description: str = ""
    chapters: list[EPUBChapterRef] = Field(default_factory=list)


class EPUBNavPoint(BaseModel):
    """Navigation point for EPUB NCX/NAV."""

    id: str
    play_order: int
    title: str
    content_src: str
    children: list["EPUBNavPoint"] = Field(default_factory=list)


class EPUBSpineItem(BaseModel):
    """Spine item reference."""

    idref: str
    linear: bool = True


class EPUBManifestItem(BaseModel):
    """Manifest item for EPUB content."""

    id: str
    href: str
    media_type: str


class EPUBExportResult(BaseModel):
    """Result of EPUB export operation."""

    config: EPUBExportConfig = Field(
        default_factory=EPUBExportConfig,
        description="Export configuration used"
    )
    metadata: Optional[EPUBMetadata] = None
    volumes: list[EPUBVolumeRef] = Field(default_factory=list)
    word_count: int = 0
    file_size: int = 0
    output_path: Optional[str] = None
    success: bool = False
    error_message: str = ""


class EPUBCSSStyle(BaseModel):
    """CSS styling for EPUB."""

    body: str = ""
    h1: str = ""
    h2: str = ""
    h3: str = ""
    p: str = ""
    p_first: str = ""
    scene_break: str = ""
    chapter_title: str = ""
    volume_title: str = ""
    front_matter: str = ""
    back_matter: str = ""
    toc: str = ""


class EPUBTemplateStyles:
    """Pre-built CSS templates for EPUB exports."""

    @staticmethod
    def get_simple_css() -> EPUBCSSStyle:
        """Get simple CSS template."""
        return EPUBCSSStyle(
            body="""
                body {
                    font-family: "SimSun", serif;
                    margin: 5%;
                    line-height: 1.6;
                }
            """,
            h1="""
                h1 {
                    text-align: center;
                    margin-top: 1em;
                    margin-bottom: 0.5em;
                }
            """,
            h2="""
                h2 {
                    text-align: center;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }
            """,
            p="""
                p {
                    text-indent: 2em;
                    margin-top: 0;
                    margin-bottom: 0.5em;
                }
            """,
            p_first="""
                p.first {
                    text-indent: 0;
                }
            """,
            scene_break="""
                .scene-break {
                    text-align: center;
                    margin: 1em 0;
                    color: #666;
                }
            """,
            chapter_title="""
                .chapter-title {
                    text-align: center;
                    font-size: 1.5em;
                    margin: 1.5em 0 1em;
                }
            """,
            volume_title="""
                .volume-title {
                    text-align: center;
                    font-size: 1.8em;
                    margin: 2em 0 1em;
                }
            """,
        )

    @staticmethod
    def get_standard_css() -> EPUBCSSStyle:
        """Get standard CSS template with better typography."""
        return EPUBCSSStyle(
            body="""
                body {
                    font-family: "SimSun", "Noto Serif CJK SC", serif;
                    margin: 5%;
                    line-height: 1.8;
                    font-size: 1em;
                    text-align: justify;
                }
            """,
            h1="""
                h1 {
                    text-align: center;
                    margin-top: 2em;
                    margin-bottom: 1em;
                    font-size: 1.8em;
                }
            """,
            h2="""
                h2 {
                    text-align: center;
                    margin-top: 2em;
                    margin-bottom: 0.8em;
                    font-size: 1.4em;
                }
            """,
            h3="""
                h3 {
                    text-align: left;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }
            """,
            p="""
                p {
                    text-indent: 2em;
                    margin-top: 0;
                    margin-bottom: 0.5em;
                }
            """,
            p_first="""
                p.first, p.scene-header {
                    text-indent: 0;
                }
            """,
            scene_break="""
                .scene-break {
                    text-align: center;
                    margin: 1.5em 0;
                    color: #888;
                    font-size: 1.2em;
                }
            """,
            chapter_title="""
                .chapter-title {
                    text-align: center;
                    font-size: 1.6em;
                    font-weight: bold;
                    margin: 2em 0 1.5em;
                }
                .chapter-summary {
                    text-align: left;
                    font-style: italic;
                    color: #555;
                    margin: 0 5% 1em;
                    font-size: 0.9em;
                }
                .chapter-meta {
                    text-align: center;
                    color: #666;
                    font-size: 0.85em;
                    margin-bottom: 1em;
                }
            """,
            volume_title="""
                .volume-title {
                    text-align: center;
                    font-size: 2em;
                    font-weight: bold;
                    margin: 2.5em 0 1em;
                }
                .volume-description {
                    text-align: center;
                    font-style: italic;
                    color: #666;
                    margin: 0 10% 1.5em;
                }
                .volume-meta {
                    text-align: center;
                    color: #888;
                    font-size: 0.9em;
                    margin-bottom: 2em;
                }
            """,
            front_matter="""
                .front-matter {
                    text-align: center;
                    margin: 20% 0;
                }
                .front-matter h1 {
                    font-size: 2em;
                    margin-bottom: 0.5em;
                }
                .front-matter h2 {
                    font-size: 1.2em;
                    font-weight: normal;
                    margin-bottom: 2em;
                }
                .front-matter .meta {
                    text-align: left;
                    font-size: 0.9em;
                    color: #555;
                    margin-top: 3em;
                }
            """,
            back_matter="""
                .back-matter {
                    margin: 5% 0;
                    padding-top: 2em;
                    border-top: 1px solid #ccc;
                }
                .back-matter h2 {
                    text-align: left;
                    font-size: 1.2em;
                }
                .word-count-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9em;
                }
                .word-count-table th, .word-count-table td {
                    text-align: left;
                    padding: 0.3em 0.5em;
                    border-bottom: 1px solid #eee;
                }
                .word-count-table th {
                    border-bottom: 1px solid #ccc;
                }
            """,
            toc="""
                .toc {
                    margin: 5% 10%;
                }
                .toc h1 {
                    text-align: center;
                    margin-bottom: 1em;
                }
                .toc-volume {
                    font-weight: bold;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }
                .toc-chapter {
                    margin-left: 1.5em;
                    margin-bottom: 0.3em;
                }
            """,
        )

    @staticmethod
    def get_detailed_css() -> EPUBCSSStyle:
        """Get detailed CSS template with full styling."""
        base = EPUBTemplateStyles.get_standard_css()
        base.body = """
            body {
                font-family: "SimSun", "Noto Serif CJK SC", "Source Han Serif CN", serif;
                margin: 6%;
                line-height: 2;
                font-size: 1.05em;
                text-align: justify;
                background-color: #fafafa;
            }
        """
        base.h1 = """
            h1 {
                text-align: center;
                margin-top: 2.5em;
                margin-bottom: 1em;
                font-size: 2em;
                letter-spacing: 0.1em;
            }
        """
        base.h2 = """
            h2 {
                text-align: center;
                margin-top: 2em;
                margin-bottom: 1em;
                font-size: 1.5em;
                letter-spacing: 0.05em;
            }
        """
        base.p = """
            p {
                text-indent: 2em;
                margin-top: 0;
                margin-bottom: 0.6em;
                line-height: 2;
            }
        """
        base.scene_break = """
            .scene-break {
                text-align: center;
                margin: 2em 0;
                color: #999;
                font-size: 1.4em;
                letter-spacing: 0.5em;
            }
        """
        base.chapter_title = """
            .chapter-title {
                text-align: center;
                font-size: 1.8em;
                font-weight: bold;
                margin: 2.5em 0 1.5em;
                letter-spacing: 0.08em;
            }
            .chapter-number {
                font-size: 0.7em;
                display: block;
                margin-bottom: 0.5em;
                color: #888;
                letter-spacing: 0.15em;
            }
            .chapter-summary {
                text-align: left;
                font-style: italic;
                color: #666;
                margin: 0 8% 1.5em;
                font-size: 0.95em;
                line-height: 1.8;
                padding: 1em;
                background-color: #f5f5f5;
                border-left: 3px solid #ccc;
            }
            .chapter-meta {
                text-align: center;
                color: #888;
                font-size: 0.85em;
                margin-bottom: 2em;
            }
        """
        base.volume_title = """
            .volume-title {
                text-align: center;
                font-size: 2.2em;
                font-weight: bold;
                margin: 3em 0 1.5em;
                letter-spacing: 0.12em;
            }
            .volume-description {
                text-align: center;
                font-style: italic;
                color: #777;
                margin: 0 15% 2em;
                font-size: 1em;
                line-height: 1.8;
            }
            .volume-meta {
                text-align: center;
                color: #999;
                font-size: 0.9em;
                margin-bottom: 3em;
            }
        """
        base.front_matter = """
            .front-matter {
                text-align: center;
                margin: 25% 0;
                padding: 2em;
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
            }
            .front-matter h1 {
                font-size: 2.2em;
                margin-bottom: 0.3em;
                letter-spacing: 0.15em;
            }
            .front-matter h2 {
                font-size: 1.2em;
                font-weight: normal;
                margin-bottom: 3em;
                color: #666;
            }
            .front-matter .meta {
                text-align: left;
                font-size: 0.9em;
                color: #555;
                margin-top: 4em;
                padding-top: 2em;
                border-top: 1px solid #ddd;
            }
            .front-matter .meta p {
                margin-bottom: 0.5em;
            }
        """
        base.back_matter = """
            .back-matter {
                margin: 8% 0;
                padding-top: 3em;
                border-top: 2px solid #ddd;
            }
            .back-matter h2 {
                text-align: left;
                font-size: 1.3em;
                margin-bottom: 1.5em;
                padding-bottom: 0.5em;
                border-bottom: 1px solid #eee;
            }
            .word-count-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9em;
                margin-top: 1em;
            }
            .word-count-table th, .word-count-table td {
                text-align: left;
                padding: 0.5em 0.8em;
                border-bottom: 1px solid #eee;
            }
            .word-count-table th {
                border-bottom: 2px solid #ddd;
                background-color: #f8f8f8;
            }
            .word-count-table tr:nth-child(even) {
                background-color: #fafafa;
            }
        """
        return base
