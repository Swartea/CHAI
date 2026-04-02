"""Volume split engine for multi-volume/book export orchestration.

This module provides the VolumeSplitEngine class that orchestrates
splitting a novel into separate book files using the various manuscript
export engines.
"""

from pathlib import Path
from typing import Optional

from chai.models import Novel
from chai.models.volume_split import (
    VolumeSplitConfig,
    VolumeSplitResult,
    VolumeSplitStrategy,
    VolumeBookInfo,
)
from chai.engines.markdown_manuscript_engine import MarkdownManuscriptEngine
from chai.engines.epub_manuscript_engine import EPUBManuscriptEngine
from chai.engines.pdf_manuscript_engine import PDFManuscriptEngine


class VolumeSplitEngine:
    """Engine for splitting a novel into separate volume/book exports."""

    def __init__(
        self,
        config: Optional[VolumeSplitConfig] = None,
        markdown_config: Optional["MarkdownManuscriptEngine"] = None,
        epub_config: Optional["EPUBManuscriptEngine"] = None,
        pdf_config: Optional["PDFManuscriptEngine"] = None,
    ):
        """Initialize the volume split engine.

        Args:
            config: Volume split configuration.
            markdown_config: Markdown manuscript engine configuration.
            epub_config: EPUB manuscript engine configuration.
            pdf_config: PDF manuscript engine configuration.
        """
        self.config = config or VolumeSplitConfig()

    def split_and_export(
        self,
        novel: Novel,
        output_dir: str | Path,
        format: str = "markdown",
    ) -> VolumeSplitResult:
        """Split novel into separate books and export.

        Args:
            novel: The novel to split.
            output_dir: Directory to write book files.
            format: Export format ("markdown", "epub", or "pdf").

        Returns:
            VolumeSplitResult with information about created books.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = VolumeSplitResult(
            series_title=novel.title,
            total_volumes=len(novel.volumes),
            total_books=0,
            books=[],
        )

        if self.config.strategy == VolumeSplitStrategy.ONE_VOLUME_PER_BOOK:
            result = self._export_one_volume_per_book(novel, output_dir, format, result)
        elif self.config.strategy == VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK:
            result = self._export_multiple_volumes_per_book(novel, output_dir, format, result)
        elif self.config.strategy == VolumeSplitStrategy.ALL_IN_ONE:
            result = self._export_all_in_one(novel, output_dir, format, result)

        # Create series info if requested
        if self.config.create_series_info:
            result.series_info_path = str(self._create_series_info(novel, result, output_dir))

        # Create master TOC if requested
        if self.config.include_series_toc:
            result.master_toc_path = str(self._create_master_toc(novel, result, output_dir))

        return result

    def _export_one_volume_per_book(
        self,
        novel: Novel,
        output_dir: Path,
        format: str,
        result: VolumeSplitResult,
    ) -> VolumeSplitResult:
        """Export each volume as a separate book."""
        books = []

        for book_num, volume in enumerate(novel.volumes, start=1):
            book_info = VolumeBookInfo(
                book_number=book_num,
                book_title=volume.title,
                volume_ids=[volume.id],
                chapter_count=len(volume.chapters),
                word_count=sum(c.word_count for c in volume.chapters),
            )

            file_path = self._export_single_book(
                novel, volume, book_num, output_dir, format
            )
            book_info.file_path = file_path
            books.append(book_info)

        result.books = books
        result.total_books = len(books)
        return result

    def _export_multiple_volumes_per_book(
        self,
        novel: Novel,
        output_dir: Path,
        format: str,
        result: VolumeSplitResult,
    ) -> VolumeSplitResult:
        """Export multiple volumes per book."""
        books = []
        volumes_per = self.config.volumes_per_book
        volumes = list(novel.volumes)

        for i in range(0, len(volumes), volumes_per):
            book_volumes = volumes[i:i + volumes_per]
            book_num = (i // volumes_per) + 1

            # Create combined book title
            if len(book_volumes) == 1:
                book_title = book_volumes[0].title
            else:
                book_title = f"{book_volumes[0].title}至{book_volumes[-1].title}"

            # Collect volume IDs and word counts
            volume_ids = [v.id for v in book_volumes]
            chapter_count = sum(len(v.chapters) for v in book_volumes)
            word_count = sum(c.word_count for v in book_volumes for c in v.chapters)

            book_info = VolumeBookInfo(
                book_number=book_num,
                book_title=book_title,
                volume_ids=volume_ids,
                chapter_count=chapter_count,
                word_count=word_count,
            )

            # Export combined book
            file_path = self._export_combined_book(
                novel, book_volumes, book_num, output_dir, format
            )
            book_info.file_path = file_path
            books.append(book_info)

        result.books = books
        result.total_books = len(books)
        return result

    def _export_all_in_one(
        self,
        novel: Novel,
        output_dir: Path,
        format: str,
        result: VolumeSplitResult,
    ) -> VolumeSplitResult:
        """Export all volumes as a single book (no actual splitting)."""
        book_info = VolumeBookInfo(
            book_number=1,
            book_title=novel.title,
            volume_ids=[v.id for v in novel.volumes],
            chapter_count=sum(len(v.chapters) for v in novel.volumes),
            word_count=sum(c.word_count for v in novel.volumes for c in v.chapters),
        )

        file_path = self._export_combined_book(
            novel, list(novel.volumes), 1, output_dir, format
        )
        book_info.file_path = file_path

        result.books = [book_info]
        result.total_books = 1
        return result

    def _export_single_book(
        self,
        novel: Novel,
        volume,
        book_number: int,
        output_dir: Path,
        format: str,
    ) -> str:
        """Export a single volume as a book."""
        if format == "markdown":
            engine = MarkdownManuscriptEngine()
            paths = engine.export_volumes_separate(novel, output_dir)
            return paths[book_number - 1] if book_number <= len(paths) else None
        elif format == "epub":
            engine = EPUBManuscriptEngine()
            paths = engine.export_volumes_separate(novel, output_dir)
            return paths[book_number - 1] if book_number <= len(paths) else None
        elif format == "pdf":
            engine = PDFManuscriptEngine()
            paths = engine.export_volumes_separate(novel, output_dir)
            return paths[book_number - 1] if book_number <= len(paths) else None
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_combined_book(
        self,
        novel: Novel,
        volumes: list,
        book_number: int,
        output_dir: Path,
        format: str,
    ) -> str:
        """Export multiple volumes combined as a single book."""
        if format == "markdown":
            engine = MarkdownManuscriptEngine()
            return self._export_combined_markdown(novel, volumes, book_number, output_dir)
        elif format == "epub":
            engine = EPUBManuscriptEngine()
            return self._export_combined_epub(novel, volumes, book_number, output_dir)
        elif format == "pdf":
            engine = PDFManuscriptEngine()
            return self._export_combined_pdf(novel, volumes, book_number, output_dir)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_combined_markdown(
        self,
        novel: Novel,
        volumes: list,
        book_number: int,
        output_dir: Path,
    ) -> str:
        """Export combined volumes as a single Markdown file."""
        engine = MarkdownManuscriptEngine()

        series_title = novel.title.replace(" ", "_").replace("/", "-")
        book_title = f"{volumes[0].title}至{volumes[-1].title}" if len(volumes) > 1 else volumes[0].title
        filename = f"{series_title}_第{book_number}册_{book_title.replace(' ', '_').replace('/', '-')}.md"
        path = output_dir / filename

        content_parts = []
        for volume in volumes:
            vol_content = engine._generate_volume(volume)
            content_parts.append(vol_content)

        full_content = "\n\n".join(content_parts)
        path.write_text(full_content, encoding="utf-8")
        return str(path)

    def _export_combined_epub(
        self,
        novel: Novel,
        volumes: list,
        book_number: int,
        output_dir: Path,
    ) -> str:
        """Export combined volumes as a single EPUB file."""
        engine = EPUBManuscriptEngine()

        series_title = novel.title.replace(" ", "_").replace("/", "-")
        book_title = f"{volumes[0].title}至{volumes[-1].title}" if len(volumes) > 1 else volumes[0].title
        filename = f"{series_title}_第{book_number}册_{book_title.replace(' ', '_').replace('/', '-')}.epub"
        path = output_dir / filename

        # For combined EPUB, we create a temporary novel with only the selected volumes
        import copy
        temp_novel = copy.deepcopy(novel)
        temp_novel.volumes = volumes

        engine.export_to_file(temp_novel, path)
        return str(path)

    def _export_combined_pdf(
        self,
        novel: Novel,
        volumes: list,
        book_number: int,
        output_dir: Path,
    ) -> str:
        """Export combined volumes as a single PDF file."""
        engine = PDFManuscriptEngine()

        series_title = novel.title.replace(" ", "_").replace("/", "-")
        book_title = f"{volumes[0].title}至{volumes[-1].title}" if len(volumes) > 1 else volumes[0].title
        filename = f"{series_title}_第{book_number}册_{book_title.replace(' ', '_').replace('/', '-')}.pdf"
        path = output_dir / filename

        # For combined PDF, we create a temporary novel with only the selected volumes
        import copy
        temp_novel = copy.deepcopy(novel)
        temp_novel.volumes = volumes

        engine.export_to_file(temp_novel, path)
        return str(path)

    def _create_series_info(
        self,
        novel: Novel,
        result: VolumeSplitResult,
        output_dir: Path,
    ) -> Path:
        """Create a series information file."""
        filename = f"{novel.title.replace(' ', '_').replace('/', '-')}_series_info.md"
        path = output_dir / filename

        lines = [
            f"# {novel.title}",
            "",
            f"**类型**: {novel.genre}",
            f"**总卷数**: {result.total_volumes}",
            f"**总册数**: {result.total_books}",
            "",
            "## 册次信息",
            "",
        ]

        for book in result.books:
            lines.append(f"### 第{book.book_number}册：{book.book_title}")
            lines.append("")
            lines.append(f"- 章节数：{book.chapter_count}")
            lines.append(f"- 字数：{book.word_count:,}")
            if book.volume_ids:
                lines.append(f"- 包含卷数：{len(book.volume_ids)}")
            if book.file_path:
                lines.append(f"- 文件：{Path(book.file_path).name}")
            lines.append("")

        content = "\n".join(lines)
        path.write_text(content, encoding="utf-8")
        return path

    def _create_master_toc(
        self,
        novel: Novel,
        result: VolumeSplitResult,
        output_dir: Path,
    ) -> Path:
        """Create a master table of contents file."""
        filename = f"{novel.title.replace(' ', '_').replace('/', '-')}_master_toc.md"
        path = output_dir / filename

        lines = [
            "# 总目录",
            "",
            f"**{novel.title}**",
            "",
            "---",
            "",
        ]

        for book in result.books:
            lines.append(f"## 第{book.book_number}册：{book.book_title}")
            lines.append("")

            # Find volumes for this book
            book_volumes = [v for v in novel.volumes if v.id in book.volume_ids]
            for volume in book_volumes:
                if len(book_volumes) > 1:
                    lines.append(f"### {volume.title}")
                    lines.append("")

                for chapter in volume.chapters:
                    ch_num = f"第{chapter.number}章 " if not chapter.is_prologue and not chapter.is_epilogue else ""
                    if chapter.is_prologue:
                        ch_num = "序章 "
                    elif chapter.is_epilogue:
                        ch_num = "尾声 "
                    lines.append(f"- {ch_num}{chapter.title}")

            lines.append("")

        content = "\n".join(lines)
        path.write_text(content, encoding="utf-8")
        return path

    def get_split_summary(self, novel: Novel) -> dict:
        """Get a summary of how the novel would be split.

        Args:
            novel: The novel to analyze.

        Returns:
            Dictionary with split information.
        """
        total_volumes = len(novel.volumes)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)

        if self.config.strategy == VolumeSplitStrategy.ONE_VOLUME_PER_BOOK:
            num_books = total_volumes
        elif self.config.strategy == VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK:
            num_books = (total_volumes + self.config.volumes_per_book - 1) // self.config.volumes_per_book
        else:
            num_books = 1

        return {
            "series_title": novel.title,
            "total_volumes": total_volumes,
            "total_chapters": total_chapters,
            "total_words": total_words,
            "strategy": self.config.strategy.value,
            "books_count": num_books,
            "volumes_per_book": self.config.volumes_per_book,
        }
