"""Tests for export functionality."""

import pytest
import tempfile
from pathlib import Path

from chai.models import Novel, Volume, Chapter
from chai.export import MarkdownExporter, EPUBExporter


class TestMarkdownExporter:
    """Tests for MarkdownExporter."""

    def test_export_chapter(self):
        """Test exporting a single chapter."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。\n\n段落二。",
            word_count=20,
        )

        exporter = MarkdownExporter()
        md = exporter.export_chapter(chapter)

        assert "# 第一章：开始" in md
        assert "这是第一章的内容。" in md

    def test_export_volume(self):
        """Test exporting a volume."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容1", word_count=10),
            Chapter(id="ch_2", number=2, title="第二章", content="内容2", word_count=10),
        ]

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="测试卷",
            chapters=chapters,
        )

        exporter = MarkdownExporter()
        md = exporter.export_volume(volume)

        assert "# 第一卷" in md
        assert "第一章" in md
        assert "第二章" in md

    def test_export_novel(self):
        """Test exporting entire novel."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=10),
        ]

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=chapters,
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        exporter = MarkdownExporter()
        md = exporter.export_novel(novel)

        assert "# 测试小说" in md
        assert "**类型**: 玄幻" in md
        assert "第一章" in md

    def test_export_to_file(self):
        """Test exporting to a file."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="测试内容",
            word_count=10,
        )

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[chapter],
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = MarkdownExporter()
            path = exporter.export_to_file(novel, Path(tmpdir) / "novel.md")

            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "测试小说" in content


class TestEPUBExporter:
    """Tests for EPUBExporter."""

    def test_epub_creation(self):
        """Test creating an EPUB file."""
        chapters = [
            Chapter(
                id="ch_1",
                number=1,
                title="第一章",
                content="这是第一章的内容。",
                word_count=15,
            ),
        ]

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=chapters,
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = EPUBExporter()
            path = exporter.export_to_file(novel, Path(tmpdir) / "novel.epub")

            assert path.exists()
            assert path.stat().st_size > 0
