"""PDF manuscript export engine.

This module provides comprehensive PDF export functionality with support for
page layout, fonts, margins, headers/footers, table of contents, and
multiple output templates suitable for print publishing.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from chai.models import Novel, Volume, Chapter, Scene
from chai.models.pdf_export import (
    PDFTemplate,
    PDFExportConfig,
    PDFExportResult,
    PDFMetadata,
    PDFChapterRef,
    PDFVolumeRef,
    PDFTableOfContentsEntry,
    PDFPageSize,
)


class PDFManuscriptEngine:
    """Engine for generating formatted PDF manuscripts for print."""

    def __init__(self, config: Optional[PDFExportConfig] = None):
        """Initialize the PDF manuscript engine.

        Args:
            config: Export configuration. Uses defaults if not provided.
        """
        self.config = config or PDFExportConfig()
        self._page_counter = 0
        self._current_chapter = None

    def generate_manuscript(self, novel: Novel) -> PDFExportResult:
        """Generate a complete PDF manuscript structure.

        Args:
            novel: The novel to export.

        Returns:
            PDFExportResult with the generated PDF metadata and structure.
        """
        result = PDFExportResult(config=self.config)

        # Generate metadata
        if self.config.template != PDFTemplate.SIMPLE:
            result.metadata = self._create_metadata(novel)

        # Generate volume and chapter references
        result.volumes = self._create_volume_refs(novel)

        # Generate table of contents
        if self.config.include_table_of_contents and self.config.template != PDFTemplate.SIMPLE:
            result.toc = self._create_toc(novel, result.volumes)

        # Calculate total word count
        result.word_count = sum(c.word_count for v in novel.volumes for c in v.chapters)

        return result

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export manuscript to a PDF file.

        Args:
            novel: The novel to export.
            output_path: Path to write the PDF file.

        Returns:
            Path to the created PDF file.
        """
        path = Path(output_path)
        result = self.generate_manuscript(novel)

        try:
            from reportlab.lib.pagesizes import A4, A5, B5, letter, legal
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                TableOfContents, KeepTogether
            )
            from reportlab.pdfgen import canvas
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install it with: pip install reportlab"
            )

        # Map page size enum to reportlab pagesizes
        page_size_map = {
            PDFPageSize.A4: A4,
            PDFPageSize.A5: A5,
            PDFPageSize.B5: B5,
            PDFPageSize.LETTER: letter,
            PDFPageSize.LEGAL: legal,
        }
        page_size = page_size_map.get(self.config.page_size, A5)

        # Create the document
        doc = SimpleDocTemplate(
            str(path),
            pagesize=page_size,
            leftMargin=self.config.left_margin * cm,
            rightMargin=self.config.right_margin * cm,
            topMargin=self.config.top_margin * cm,
            bottomMargin=self.config.bottom_margin * cm,
        )

        # Build the story
        story = []

        # Add front matter
        if result.metadata:
            story.extend(self._build_front_matter(novel, result.metadata))

        # Add table of contents
        if result.toc:
            story.extend(self._build_toc(result.toc))

        # Add chapters
        for volume in novel.volumes:
            for chapter in volume.chapters:
                story.extend(self._build_chapter(chapter))

        # Build the PDF
        doc.build(story)
        return path

    def export_chapters_separate(self, novel: Novel, output_dir: str | Path) -> dict[str, Path]:
        """Export each chapter as a separate PDF file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write the PDF files.

        Returns:
            Dictionary mapping chapter IDs to their PDF file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = {}
        for volume in novel.volumes:
            for chapter in volume.chapters:
                filename = f"chapter_{chapter.number:03d}_{chapter.title}.pdf"
                filepath = output_dir / filename
                self._export_single_chapter(chapter, filepath)
                paths[chapter.id] = filepath

        return paths

    def _export_single_chapter(self, chapter: Chapter, output_path: Path) -> Path:
        """Export a single chapter to PDF."""
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install it with: pip install reportlab"
            )

        path = Path(output_path)
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A5,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []
        story.append(Paragraph(chapter.title, self._get_chapter_style()))
        story.append(Spacer(1, 20))

        for para in chapter.content.split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, self._get_body_style()))

        doc.build(story)
        return path

    def _create_metadata(self, novel: Novel) -> PDFMetadata:
        """Create PDF metadata."""
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)

        return PDFMetadata(
            title=novel.title,
            author="CHAI",
            genre=novel.genre,
            total_words=total_words,
            total_pages=0,  # Calculated during export
        )

    def _create_volume_refs(self, novel: Novel) -> list[PDFVolumeRef]:
        """Create volume and chapter references."""
        volumes = []

        for volume in novel.volumes:
            chapters = []
            volume_word_count = 0

            for chapter in volume.chapters:
                chapter_ref = PDFChapterRef(
                    chapter_id=chapter.id,
                    chapter_number=chapter.number,
                    chapter_title=chapter.title,
                    is_prologue=chapter.is_prologue,
                    is_epilogue=chapter.is_epilogue,
                    word_count=chapter.word_count,
                )
                chapters.append(chapter_ref)
                volume_word_count += chapter.word_count

            volume_ref = PDFVolumeRef(
                volume_id=volume.id,
                volume_number=volume.number,
                volume_title=volume.title,
                description=volume.description,
                chapters=chapters,
                word_count=volume_word_count,
            )
            volumes.append(volume_ref)

        return volumes

    def _create_toc(self, novel: Novel, volumes: list[PDFVolumeRef]) -> list[PDFTableOfContentsEntry]:
        """Create table of contents entries."""
        toc = []

        for volume_ref in volumes:
            # Add volume entry
            toc.append(PDFTableOfContentsEntry(
                title=volume_ref.volume_title,
                page_number=0,  # Calculated during export
                level=1,
                volume_number=volume_ref.volume_number,
            ))

            # Add chapter entries
            for chapter_ref in volume_ref.chapters:
                toc.append(PDFTableOfContentsEntry(
                    title=chapter_ref.chapter_title,
                    page_number=0,
                    level=2,
                    volume_number=volume_ref.volume_number,
                    chapter_number=chapter_ref.chapter_number,
                ))

        return toc

    def _build_front_matter(self, novel: Novel, metadata: PDFMetadata) -> list:
        """Build front matter content."""
        from reportlab.platypus import Paragraph, Spacer

        story = []
        story.append(Paragraph(novel.title, self._get_title_style()))
        story.append(Spacer(1, 20))

        if metadata.subtitle:
            story.append(Paragraph(metadata.subtitle, self._get_subtitle_style()))
            story.append(Spacer(1, 10))

        story.append(Paragraph(f"作者：{metadata.author}", self._get_meta_style()))
        story.append(Paragraph(f"类型：{metadata.genre}", self._get_meta_style()))
        story.append(Paragraph(f"字数：{metadata.total_words}", self._get_meta_style()))
        story.append(Paragraph(f"日期：{datetime.now().strftime('%Y-%m-%d')}", self._get_meta_style()))
        story.append(Spacer(1, 30))
        story.append(Paragraph("—— 目录 ——", self._get_toc_header_style()))
        story.append(Spacer(1, 20))

        return story

    def _build_toc(self, toc: list[PDFTableOfContentsEntry]) -> list:
        """Build table of contents."""
        from reportlab.platypus import Paragraph, Spacer

        story = []

        for entry in toc:
            indent = "　" * (entry.level - 1) * 2
            style = self._get_toc_volume_style() if entry.level == 1 else self._get_toc_chapter_style()
            story.append(Paragraph(f"{indent}{entry.title}", style))

        story.append(Spacer(1, 30))
        story.append(Paragraph("—— 正文 ——", self._get_toc_header_style()))
        story.append(Spacer(1, 20))

        return story

    def _build_chapter(self, chapter: Chapter) -> list:
        """Build chapter content."""
        from reportlab.platypus import Paragraph, Spacer, PageBreak

        story = []
        story.append(PageBreak())
        story.append(Paragraph(chapter.title, self._get_chapter_style()))
        story.append(Spacer(1, 20))

        # Add chapter summary if configured
        if self.config.include_chapter_summaries and chapter.summary:
            story.append(Paragraph(f"本章概要：{chapter.summary}", self._get_summary_style()))
            story.append(Spacer(1, 15))

        # Add content
        for para in chapter.content.split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, self._get_body_style()))
                if self.config.paragraph_spacing:
                    story.append(Spacer(1, 6))

        return story

    def _get_title_style(self):
        """Get title paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        return ParagraphStyle(
            'Title',
            fontName='SimSun',
            fontSize=self.config.title_font_size,
            alignment=TA_CENTER,
            spaceAfter=30,
        )

    def _get_subtitle_style(self):
        """Get subtitle paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        return ParagraphStyle(
            'Subtitle',
            fontName='SimSun',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

    def _get_meta_style(self):
        """Get metadata paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        return ParagraphStyle(
            'Meta',
            fontName='SimSun',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=5,
        )

    def _get_chapter_style(self):
        """Get chapter title paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        return ParagraphStyle(
            'ChapterTitle',
            fontName='SimSun',
            fontSize=self.config.chapter_title_font_size,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=20,
        )

    def _get_body_style(self):
        """Get body paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_JUSTIFY

        style = ParagraphStyle(
            'Body',
            fontName='SimSun',
            fontSize=self.config.body_font_size,
            leading=self.config.body_font_size * self.config.line_spacing,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
        )

        if self.config.indent_first_line:
            style.firstLineIndent = self.config.body_font_size * 2

        return style

    def _get_summary_style(self):
        """Get chapter summary paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        return ParagraphStyle(
            'Summary',
            fontName='SimSun',
            fontSize=9,
            leading=14,
            alignment=TA_LEFT,
            textColor='gray',
            spaceAfter=10,
        )

    def _get_toc_header_style(self):
        """Get TOC header paragraph style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        return ParagraphStyle(
            'TOCHHeader',
            fontName='SimSun',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10,
        )

    def _get_toc_volume_style(self):
        """Get TOC volume entry style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        return ParagraphStyle(
            'TOCVolume',
            fontName='SimSun',
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=8,
        )

    def _get_toc_chapter_style(self):
        """Get TOC chapter entry style."""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        return ParagraphStyle(
            'TOCChapter',
            fontName='SimSun',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=4,
        )

    def get_manuscript_summary(self, result: PDFExportResult) -> str:
        """Get a human-readable summary of the PDF manuscript.

        Args:
            result: The PDF export result.

        Returns:
            Summary string describing the generated PDF.
        """
        total_chapters = sum(len(v.chapters) for v in result.volumes)

        summary_parts = [
            f"PDF Manuscript Summary:",
            f"- Template: {result.config.template.value}",
            f"- Page Size: {result.config.page_size.value}",
            f"- Total Volumes: {len(result.volumes)}",
            f"- Total Chapters: {total_chapters}",
            f"- Total Words: {result.word_count}",
            f"- Table of Contents: {'Yes' if result.toc else 'No'}",
            f"- Page Numbers: {'Yes' if result.config.include_page_numbers else 'No'}",
        ]

        return "\n".join(summary_parts)

    def export_volumes_separate(
        self,
        novel: Novel,
        output_dir: str | Path,
        filename_pattern: str = "{series_title}_第{book_number}册_{book_title}.pdf"
    ) -> list[Path]:
        """Export each volume as a separate PDF book file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write PDF files.
            filename_pattern: Pattern for filenames with {series_title}, {book_number}, {book_title} placeholders.

        Returns:
            List of created PDF file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []

        for book_num, volume in enumerate(novel.volumes, start=1):
            # Format filename
            book_title = volume.title.replace(" ", "_").replace("/", "-")
            series_title = novel.title.replace(" ", "_").replace("/", "-")
            filename = filename_pattern.format(
                series_title=series_title,
                book_number=book_num,
                book_title=book_title
            )
            path = output_dir / filename

            # Export single volume as PDF
            self._export_single_volume_pdf(novel, volume, book_num, path)
            paths.append(path)

        return paths

    def _export_single_volume_pdf(
        self,
        novel: Novel,
        volume: Volume,
        book_number: int,
        output_path: Path
    ) -> Path:
        """Export a single volume as a complete PDF file.

        Args:
            novel: The original novel.
            volume: The volume to export.
            book_number: Book number in series (1-indexed).
            output_path: Path for the output PDF file.

        Returns:
            Path to the created PDF file.
        """
        try:
            from reportlab.lib.pagesizes import A4, A5, B5, letter, legal
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                TableOfContents, KeepTogether
            )
            from reportlab.pdfgen import canvas
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install it with: pip install reportlab"
            )

        path = Path(output_path)

        # Map page size enum to reportlab pagesizes
        page_size_map = {
            PDFPageSize.A4: A4,
            PDFPageSize.A5: A5,
            PDFPageSize.B5: B5,
            PDFPageSize.LETTER: letter,
            PDFPageSize.LEGAL: legal,
        }
        page_size = page_size_map.get(self.config.page_size, A5)

        # Create the document
        doc = SimpleDocTemplate(
            str(path),
            pagesize=page_size,
            leftMargin=self.config.left_margin * cm,
            rightMargin=self.config.right_margin * cm,
            topMargin=self.config.top_margin * cm,
            bottomMargin=self.config.bottom_margin * cm,
        )

        # Build the story
        story = []

        # Add book front matter
        if self.config.template != PDFTemplate.SIMPLE:
            story.extend(self._build_volume_front_matter(novel, volume, book_number))

        # Add table of contents for this volume
        if self.config.include_table_of_contents and self.config.template != PDFTemplate.SIMPLE:
            story.extend(self._build_volume_toc(volume))

        # Add chapter content
        for chapter in volume.chapters:
            story.extend(self._build_chapter(chapter))

        # Build the PDF
        doc.build(story)
        return path

    def _build_volume_front_matter(
        self,
        novel: Novel,
        volume: Volume,
        book_number: int
    ) -> list:
        """Build front matter for a single volume PDF."""
        from reportlab.platypus import Paragraph, Spacer

        story = []
        total_words = sum(c.word_count for c in volume.chapters)

        # Book title page
        story.append(Paragraph(novel.title, self._get_title_style()))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"第{book_number}册：{volume.title}", self._get_subtitle_style()))
        story.append(Spacer(1, 30))

        # Metadata
        story.append(Paragraph(f"作者：{getattr(novel, 'author', 'CHAI')}", self._get_meta_style()))
        story.append(Paragraph(f"类型：{novel.genre}", self._get_meta_style()))
        story.append(Paragraph(f"本册字数：{total_words:,} 字", self._get_meta_style()))
        story.append(Paragraph(f"本册章节：{len(volume.chapters)} 章", self._get_meta_style()))
        story.append(Paragraph(f"日期：{datetime.now().strftime('%Y-%m-%d')}", self._get_meta_style()))
        story.append(Spacer(1, 30))

        if self.config.include_table_of_contents:
            story.append(Paragraph("—— 目录 ——", self._get_toc_header_style()))
            story.append(Spacer(1, 20))

        return story

    def _build_volume_toc(self, volume: Volume) -> list:
        """Build table of contents for a single volume PDF."""
        from reportlab.platypus import Paragraph, Spacer

        story = []

        for chapter in volume.chapters:
            indent = "　　"
            story.append(Paragraph(f"{indent}{chapter.title}", self._get_toc_chapter_style()))

        story.append(Spacer(1, 20))
        story.append(Paragraph("—— 正文 ——", self._get_toc_header_style()))
        story.append(Spacer(1, 15))

        return story
