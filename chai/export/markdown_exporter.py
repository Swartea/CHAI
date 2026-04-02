"""Markdown export functionality."""

from pathlib import Path
from chai.models import Novel, Volume, Chapter


class MarkdownExporter:
    """Export novel to Markdown format."""

    def export_chapter(self, chapter: Chapter) -> str:
        """Export single chapter to Markdown."""
        md = f"# {chapter.title}\n\n"

        if chapter.is_prologue:
            md = f"# 序章：{chapter.title.replace('序章：', '')}\n\n"
        elif chapter.is_epilogue:
            md = f"# 尾声：{chapter.title.replace('尾声：', '')}\n\n"

        md += chapter.content
        md += "\n\n"

        return md

    def export_volume(self, volume: Volume) -> str:
        """Export single volume to Markdown."""
        md = f"# {volume.title}\n\n"
        md += f"*{volume.description}*\n\n"
        md += "---\n\n"

        for chapter in volume.chapters:
            md += self.export_chapter(chapter)
            md += "---\n\n"

        return md

    def export_novel(self, novel: Novel) -> str:
        """Export entire novel to Markdown."""
        md = f"# {novel.title}\n\n"
        md += f"**类型**: {novel.genre}\n\n"
        md += f"**字数**: {sum(c.word_count for v in novel.volumes for c in v.chapters)}\n\n"
        md += "---\n\n"

        for volume in novel.volumes:
            md += self.export_volume(volume)

        return md

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export novel to a Markdown file."""
        path = Path(output_path)
        content = self.export_novel(novel)
        path.write_text(content, encoding="utf-8")
        return path

    def export_chapters_to_files(self, novel: Novel, output_dir: str | Path) -> list[Path]:
        """Export each chapter as a separate Markdown file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                filename = f"chapter_{chapter.number:03d}_{chapter.title}.md"
                path = output_dir / filename
                path.write_text(self.export_chapter(chapter), encoding="utf-8")
                paths.append(path)

        return paths
