"""Markdown manuscript export engine.

This module provides comprehensive Markdown manuscript export functionality
with support for table of contents, front/back matter, scene-level content,
and multiple output templates.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from chai.models import Novel, Volume, Chapter, Scene
from chai.models.manuscript_export import (
    ManuscriptTemplate,
    ManuscriptExportConfig,
    ManuscriptExportResult,
    FrontMatter,
    BackMatter,
    TableOfContentsEntry,
    ManuscriptTOC,
    ChapterManuscript,
    VolumeManuscript,
    ChapterManuscriptSection,
)


class MarkdownManuscriptEngine:
    """Engine for generating formatted Markdown manuscripts."""

    def __init__(self, config: Optional[ManuscriptExportConfig] = None):
        """Initialize the manuscript engine.

        Args:
            config: Export configuration. Uses defaults if not provided.
        """
        self.config = config or ManuscriptExportConfig()

    def generate_manuscript(self, novel: Novel) -> ManuscriptExportResult:
        """Generate a complete Markdown manuscript.

        Args:
            novel: The novel to export.

        Returns:
            ManuscriptExportResult with the generated content and metadata.
        """
        result = ManuscriptExportResult(config=self.config)

        # Generate front matter
        if self.config.template != ManuscriptTemplate.SIMPLE:
            result.front_matter = self._create_front_matter(novel)

        # Generate table of contents
        if self.config.include_table_of_contents and self.config.template != ManuscriptTemplate.SIMPLE:
            result.toc = self._create_toc(novel)

        # Generate body content
        body = self._generate_body(novel)
        result.word_count = sum(c.word_count for v in novel.volumes for c in v.chapters)

        # Generate back matter
        if self.config.template == ManuscriptTemplate.DETAILED:
            result.back_matter = self._create_back_matter(novel)

        # Assemble final manuscript
        result.content = self._assemble_manuscript(result, body)

        return result

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export manuscript to a file.

        Args:
            novel: The novel to export.
            output_path: Path to write the file.

        Returns:
            Path to the created file.
        """
        result = self.generate_manuscript(novel)
        path = Path(output_path)
        path.write_text(result.content, encoding="utf-8")
        return path

    def _create_front_matter(self, novel: Novel) -> FrontMatter:
        """Create front matter for the manuscript."""
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)

        front = FrontMatter(
            title=novel.title,
            author="CHAI",
            genre=novel.genre,
            total_words=total_words,
            total_chapters=total_chapters,
            total_volumes=len(novel.volumes),
            creation_date=datetime.now().strftime("%Y-%m-%d"),
        )

        # Add character names if configured
        if self.config.include_character_list and novel.characters:
            front.character_list = [char.name for char in novel.characters]

        # Add world setting summary if configured
        if self.config.include_world_setting and novel.world_setting:
            front.world_summary = novel.world_setting.description or novel.world_setting.name

        return front

    def _create_toc(self, novel: Novel) -> ManuscriptTOC:
        """Create table of contents."""
        entries = []
        anchor_count = {}

        for volume in novel.volumes:
            vol_anchor = self._create_anchor(volume.title)
            anchor_count[vol_anchor] = anchor_count.get(vol_anchor, 0) + 1
            if anchor_count[vol_anchor] > 1:
                vol_anchor = f"{vol_anchor}-{anchor_count[vol_anchor]}"

            entries.append(TableOfContentsEntry(
                title=volume.title,
                level=1,
                volume_number=volume.number,
                anchor=vol_anchor,
            ))

            for chapter in volume.chapters:
                ch_anchor = self._create_anchor(f"{volume.title}-{chapter.title}")
                anchor_count[ch_anchor] = anchor_count.get(ch_anchor, 0) + 1
                if anchor_count[ch_anchor] > 1:
                    ch_anchor = f"{ch_anchor}-{anchor_count[ch_anchor]}"

                entries.append(TableOfContentsEntry(
                    title=chapter.title,
                    level=2,
                    chapter_number=chapter.number,
                    volume_number=volume.number,
                    anchor=ch_anchor,
                    is_prologue=chapter.is_prologue,
                    is_epilogue=chapter.is_epilogue,
                ))

        return ManuscriptTOC(entries=entries)

    def _create_back_matter(self, novel: Novel) -> BackMatter:
        """Create back matter for the manuscript."""
        back = BackMatter()

        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        back.word_count_summary = f"总字数: {total_words:,} 字"

        back.chapter_word_counts = [
            {
                "chapter": chapter.title,
                "number": chapter.number,
                "word_count": chapter.word_count,
            }
            for volume in novel.volumes
            for chapter in volume.chapters
        ]

        return back

    def _generate_body(self, novel: Novel) -> str:
        """Generate the main body content."""
        parts = []

        for volume in novel.volumes:
            vol_content = self._generate_volume(volume)
            parts.append(vol_content)

        return "\n\n".join(parts)

    def _generate_volume(self, volume: Volume) -> str:
        """Generate a single volume."""
        sections = []

        # Volume heading
        vol_title = f"# {volume.title}"
        if self.config.template != ManuscriptTemplate.SIMPLE:
            vol_anchor = self._create_anchor(volume.title)
            vol_title = f"# {volume.title} {{#{vol_anchor}}}"

        sections.append(vol_title)

        if volume.description and self.config.template != ManuscriptTemplate.SIMPLE:
            sections.append(f"*{volume.description}*")

        if self.config.include_word_counts and self.config.template != ManuscriptTemplate.SIMPLE:
            vol_words = sum(c.word_count for c in volume.chapters)
            sections.append(f"*{vol_words:,} 字*")

        sections.append("")

        # Chapters
        for chapter in volume.chapters:
            ch_content = self._generate_chapter(chapter, volume.number)
            sections.append(ch_content)

            if volume.chapters.index(chapter) < len(volume.chapters) - 1:
                sections.append("")

        return "\n".join(sections)

    def _generate_chapter(self, chapter: Chapter, volume_number: int) -> str:
        """Generate a single chapter."""
        sections = []

        # Chapter heading
        if chapter.is_prologue:
            title = f"## 序章：{chapter.title.replace('序章：', '')}"
        elif chapter.is_epilogue:
            title = f"## 尾声：{chapter.title.replace('尾声：', '')}"
        else:
            title = f"## 第{chapter.number}章 {chapter.title.replace(f'第{chapter.number}章 ', '')}"

        if self.config.template != ManuscriptTemplate.SIMPLE:
            ch_anchor = self._create_anchor(f"v{volume_number}-ch{chapter.number}")
            title = f"## {chapter.title} {{#{ch_anchor}}}"

        sections.append(title)

        # Chapter summary
        if self.config.include_chapter_summaries and chapter.summary and self.config.template != ManuscriptTemplate.SIMPLE:
            sections.append(f"**本章概要**: {chapter.summary}")

        # Word count
        if self.config.include_word_counts and self.config.template != ManuscriptTemplate.SIMPLE:
            sections.append(f"*{chapter.word_count:,} 字*")

        sections.append("")

        # Chapter content
        if self.config.include_scene_content and chapter.scenes:
            sections.append(self._generate_scened_content(chapter))
        else:
            sections.append(self._format_paragraphs(chapter.content))

        return "\n".join(sections)

    def _generate_scened_content(self, chapter: Chapter) -> str:
        """Generate content with scene separators."""
        parts = []

        for i, scene in enumerate(chapter.scenes):
            # Scene header
            if self.config.scene_separators:
                parts.append("───")

            # Scene info
            scene_info = []
            if scene.location:
                scene_info.append(f"**场景 {i + 1}** | {scene.location}")
            elif self.config.template != ManuscriptTemplate.SIMPLE:
                scene_info.append(f"**场景 {i + 1}**")

            if scene.time_period:
                scene_info.append(f"时间: {scene.time_period}")
            if scene.mood:
                scene_info.append(f"氛围: {scene.mood}")

            if scene_info:
                parts.append(" ".join(scene_info))
                parts.append("")

            # Scene content
            parts.append(self._format_paragraphs(scene.content))

            if self.config.scene_separators and i < len(chapter.scenes) - 1:
                parts.append("")
                parts.append("───")
                parts.append("")

        return "\n".join(parts)

    def _format_paragraphs(self, content: str) -> str:
        """Format paragraph content with proper spacing."""
        if not content:
            return ""

        paragraphs = content.split("\n\n")
        formatted = []

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            if self.config.paragraph_spacing:
                formatted.append(f"{p}\n")
            else:
                if self.config.indent_first_line:
                    formatted.append(f"　　{p}")
                else:
                    formatted.append(p)

        if self.config.paragraph_spacing:
            return "\n".join(formatted)
        else:
            return "\n\n".join(formatted)

    def _assemble_manuscript(self, result: ManuscriptExportResult, body: str) -> str:
        """Assemble the complete manuscript from components."""
        parts = []

        # Front matter
        if result.front_matter:
            parts.append(self._render_front_matter(result.front_matter))

        # Table of contents
        if result.toc:
            parts.append(self._render_toc(result.toc))

        # Body
        parts.append(body)

        # Back matter
        if result.back_matter:
            parts.append(self._render_back_matter(result.back_matter))

        return "\n\n".join(parts)

    def _render_front_matter(self, front: FrontMatter) -> str:
        """Render front matter as Markdown."""
        lines = [
            "---",
            "",
            f"# {front.title}",
            "",
        ]

        if front.subtitle:
            lines.append(f"## {front.subtitle}")
            lines.append("")

        lines.extend([
            f"**作者**: {front.author}",
            f"**类型**: {front.genre}",
            f"**总字数**: {front.total_words:,} 字",
            f"**章节数**: {front.total_chapters} 章",
            f"**卷数**: {front.total_volumes} 卷",
            f"**创作日期**: {front.creation_date}",
            "",
            "---",
            "",
        ])

        if front.character_list:
            lines.append("## 人物列表")
            lines.append("")
            for char_name in front.character_list:
                lines.append(f"- {char_name}")
            lines.append("")

        if front.world_summary:
            lines.append("## 世界观设定")
            lines.append("")
            lines.append(front.world_summary)
            lines.append("")

        return "\n".join(lines)

    def _render_toc(self, toc: ManuscriptTOC) -> str:
        """Render table of contents as Markdown."""
        lines = [
            "# 目录",
            "",
        ]

        for entry in toc.entries:
            indent = "  " * (entry.level - 1)
            if entry.level == 1:
                lines.append(f"{indent}**{entry.title}**")
            else:
                if entry.is_prologue:
                    ch_prefix = "序章："
                elif entry.is_epilogue:
                    ch_prefix = "尾声："
                else:
                    ch_prefix = f"第{entry.chapter_number}章 " if entry.chapter_number else ""
                lines.append(f"{indent}- {ch_prefix}{entry.title}")

            if entry.level == 1:
                lines.append("")

        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _render_back_matter(self, back: BackMatter) -> str:
        """Render back matter as Markdown."""
        lines = [
            "---",
            "",
            "# 附录",
            "",
        ]

        if back.word_count_summary:
            lines.append(f"**{back.word_count_summary}**")
            lines.append("")

        if back.chapter_word_counts:
            lines.append("## 章节字数统计")
            lines.append("")
            lines.append("| 章节 | 字数 |")
            lines.append("|------|------:|")
            for item in back.chapter_word_counts:
                lines.append(f"| {item['chapter']} | {item['word_count']:,} |")

        return "\n".join(lines)

    def _create_anchor(self, text: str) -> str:
        """Create a valid Markdown anchor from text."""
        anchor = text.lower()
        anchor = anchor.replace(" ", "-")
        anchor = anchor.replace("：", "-")
        anchor = anchor.replace(":", "-")
        anchor = anchor.replace(".", "-")
        anchor = anchor.replace(",", "-")
        anchor = anchor.replace("！", "")
        anchor = anchor.replace("?", "")
        anchor = anchor.replace("'", "")
        anchor = anchor.replace('"', "")
        anchor = anchor.replace("(", "")
        anchor = anchor.replace(")", "")
        anchor = anchor.replace("[", "")
        anchor = anchor.replace("]", "")

        # Remove multiple hyphens
        while "--" in anchor:
            anchor = anchor.replace("--", "-")

        # Remove leading/trailing hyphens
        anchor = anchor.strip("-")

        return anchor

    def export_chapters_separate(
        self,
        novel: Novel,
        output_dir: str | Path,
        filename_pattern: str = "{volume:03d}_{chapter:03d}_{title}.md"
    ) -> list[Path]:
        """Export each chapter as a separate Markdown file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write chapter files.
            filename_pattern: Pattern for filenames with {volume}, {chapter}, {title} placeholders.

        Returns:
            List of created file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                # Generate chapter manuscript
                content = self._generate_chapter(chapter, volume.number)

                # Format filename
                title_clean = chapter.title.replace(" ", "_").replace("/", "-")
                filename = filename_pattern.format(
                    volume=volume.number,
                    chapter=chapter.number,
                    title=title_clean
                )
                path = output_dir / filename
                path.write_text(content, encoding="utf-8")
                paths.append(path)

        return paths

    def export_volumes_separate(
        self,
        novel: Novel,
        output_dir: str | Path,
        filename_pattern: str = "{series_title}_第{book_number}册_{book_title}.md"
    ) -> list[Path]:
        """Export each volume as a separate Markdown book file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write book files.
            filename_pattern: Pattern for filenames with {series_title}, {book_number}, {book_title} placeholders.

        Returns:
            List of created file paths.
        """
        from chai.models.volume_split import VolumeSplitConfig, VolumeBookInfo

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        book_info_list = []

        for book_num, volume in enumerate(novel.volumes, start=1):
            # Generate volume content with its own front/back matter
            content = self._generate_single_volume_book(novel, volume, book_num)

            # Format filename
            book_title = volume.title.replace(" ", "_").replace("/", "-")
            series_title = novel.title.replace(" ", "_").replace("/", "-")
            filename = filename_pattern.format(
                series_title=series_title,
                book_number=book_num,
                book_title=book_title
            )
            path = output_dir / filename
            path.write_text(content, encoding="utf-8")
            paths.append(path)

            # Track book info
            book_info = VolumeBookInfo(
                book_number=book_num,
                book_title=volume.title,
                volume_ids=[volume.id],
                chapter_count=len(volume.chapters),
                word_count=sum(c.word_count for c in volume.chapters),
                file_path=str(path)
            )
            book_info_list.append(book_info)

        return paths

    def _generate_single_volume_book(
        self,
        novel: Novel,
        volume: Volume,
        book_number: int
    ) -> str:
        """Generate a single volume book with its own front/back matter.

        Args:
            novel: The original novel.
            volume: The volume to export.
            book_number: Book number in series (1-indexed).

        Returns:
            Complete book content as a string.
        """
        parts = []

        # Book-level front matter (if not simple template)
        if self.config.template != ManuscriptTemplate.SIMPLE:
            parts.append(self._render_book_front_matter(novel, volume, book_number))

        # Volume title page
        if self.config.template != ManuscriptTemplate.SIMPLE:
            parts.append(f"# {volume.title}")
            if volume.description:
                parts.append(f"*{volume.description}*")
            parts.append("")

        # Table of contents for this volume
        if self.config.include_table_of_contents and self.config.template != ManuscriptTemplate.SIMPLE:
            parts.append(self._render_book_toc(volume, book_number))

        # Chapter content
        for chapter in volume.chapters:
            ch_content = self._generate_chapter(chapter, volume.number)
            parts.append(ch_content)
            if volume.chapters.index(chapter) < len(volume.chapters) - 1:
                parts.append("")

        # Book-level back matter
        if self.config.template == ManuscriptTemplate.DETAILED:
            parts.append(self._render_book_back_matter(novel, volume))

        return "\n\n".join(parts)

    def _render_book_front_matter(
        self,
        novel: Novel,
        volume: Volume,
        book_number: int
    ) -> str:
        """Render front matter for a single volume book."""
        total_words = sum(c.word_count for c in volume.chapters)
        total_chapters = len(volume.chapters)

        lines = [
            "---",
            "",
            f"# {novel.title}",
            f"## 第{book_number}册：{volume.title}",
            "",
            f"**作者**: {getattr(novel, 'author', 'CHAI')}",
            f"**类型**: {novel.genre}",
            f"**本册字数**: {total_words:,} 字",
            f"**本册章节**: {total_chapters} 章",
            f"**创作日期**: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
        ]

        return "\n".join(lines)

    def _render_book_toc(self, volume: Volume, book_number: int) -> str:
        """Render table of contents for a single volume book."""
        lines = [
            "# 目录",
            "",
        ]

        for chapter in volume.chapters:
            if chapter.is_prologue:
                title = f"序章：{chapter.title.replace('序章：', '')}"
            elif chapter.is_epilogue:
                title = f"尾声：{chapter.title.replace('尾声：', '')}"
            else:
                title = f"第{chapter.number}章 {chapter.title.replace(f'第{chapter.number}章 ', '')}"
            lines.append(f"- {title}")

        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _render_book_back_matter(
        self,
        novel: Novel,
        volume: Volume
    ) -> str:
        """Render back matter for a single volume book."""
        lines = [
            "---",
            "",
            "# 附录",
            "",
        ]

        total_words = sum(c.word_count for c in volume.chapters)
        lines.append(f"**本册总字数**: {total_words:,} 字")
        lines.append("")

        lines.append("## 本册章节字数统计")
        lines.append("")
        lines.append("| 章节 | 字数 |")
        lines.append("|------|------:|")
        for chapter in volume.chapters:
            lines.append(f"| {chapter.title} | {chapter.word_count:,} |")

        return "\n".join(lines)

    def get_manuscript_summary(self, novel: Novel) -> dict:
        """Get a summary of the manuscript that would be generated.

        Args:
            novel: The novel to summarize.

        Returns:
            Dictionary with manuscript statistics.
        """
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)
        total_scenes = sum(len(c.scenes) for v in novel.volumes for c in v.chapters)

        return {
            "title": novel.title,
            "genre": novel.genre,
            "total_volumes": len(novel.volumes),
            "total_chapters": total_chapters,
            "total_scenes": total_scenes,
            "total_words": total_words,
            "average_chapter_words": total_words // total_chapters if total_chapters else 0,
            "has_prologue": novel.has_prologue,
            "has_epilogue": novel.has_epilogue,
        }