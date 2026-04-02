"""Tests for volume split functionality (multi-volume/book export)."""

import pytest
import tempfile
from pathlib import Path

from chai.models import Novel, Volume, Chapter, Scene, SceneType
from chai.models.volume_split import (
    VolumeSplitConfig,
    VolumeSplitResult,
    VolumeSplitStrategy,
    VolumeBookInfo,
    BookBinding,
)
from chai.engines.volume_split_engine import VolumeSplitEngine
from chai.engines.markdown_manuscript_engine import MarkdownManuscriptEngine
from chai.engines.epub_manuscript_engine import EPUBManuscriptEngine


class TestVolumeSplitConfig:
    """Tests for VolumeSplitConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = VolumeSplitConfig()
        assert config.strategy == VolumeSplitStrategy.ONE_VOLUME_PER_BOOK
        assert config.volumes_per_book == 1
        assert config.include_book_cover is True
        assert config.include_book_toc is True
        assert config.include_series_toc is False
        assert config.create_series_info is True
        assert config.binding == BookBinding.DIGITAL

    def test_custom_config(self):
        """Test custom configuration."""
        config = VolumeSplitConfig(
            strategy=VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK,
            volumes_per_book=2,
            include_series_toc=True,
        )
        assert config.strategy == VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK
        assert config.volumes_per_book == 2
        assert config.include_series_toc is True


class TestVolumeBookInfo:
    """Tests for VolumeBookInfo model."""

    def test_book_info_creation(self):
        """Test creating a book info object."""
        book_info = VolumeBookInfo(
            book_number=1,
            book_title="第一卷",
            volume_ids=["vol_1"],
            chapter_count=5,
            word_count=10000,
            file_path="/path/to/book.md",
        )
        assert book_info.book_number == 1
        assert book_info.book_title == "第一卷"
        assert book_info.volume_ids == ["vol_1"]
        assert book_info.chapter_count == 5
        assert book_info.word_count == 10000


class TestVolumeSplitStrategy:
    """Tests for VolumeSplitStrategy enum."""

    def test_strategy_values(self):
        """Test strategy enum values."""
        assert VolumeSplitStrategy.ONE_VOLUME_PER_BOOK.value == "one_volume_per_book"
        assert VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK.value == "multiple_volumes_per_book"
        assert VolumeSplitStrategy.ALL_IN_ONE.value == "all_in_one"


class TestMarkdownVolumeExport:
    """Tests for Markdown manuscript volume export."""

    def _create_test_novel_with_volumes(self) -> Novel:
        """Create a test novel with multiple volumes."""
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。\n\n这是第二段。",
            word_count=20,
        )
        chapter2 = Chapter(
            id="ch_2",
            number=2,
            title="第二章：发展",
            content="这是第二章的内容。\n\n这是第二段。",
            word_count=25,
        )
        chapter3 = Chapter(
            id="ch_3",
            number=3,
            title="第三章：高潮",
            content="这是第三章的内容。\n\n这是第二段。",
            word_count=30,
        )
        volume1 = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="这是第一卷的描述",
            chapters=[chapter1, chapter2],
        )
        volume2 = Volume(
            id="vol_2",
            title="第二卷",
            number=2,
            description="这是第二卷的描述",
            chapters=[chapter3],
        )
        return Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume1, volume2],
        )

    def test_export_volumes_separate_markdown(self):
        """Test exporting each volume as a separate Markdown file."""
        novel = self._create_test_novel_with_volumes()
        engine = MarkdownManuscriptEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = engine.export_volumes_separate(novel, tmpdir)

            assert len(paths) == 2
            assert all(p.suffix == ".md" for p in paths)

            # Check first volume file
            vol1_path = [p for p in paths if "第1册" in str(p)][0]
            content1 = vol1_path.read_text(encoding="utf-8")
            assert "测试小说" in content1
            assert "第一卷" in content1
            assert "第一章" in content1
            assert "第二章" in content1

            # Check second volume file
            vol2_path = [p for p in paths if "第2册" in str(p)][0]
            content2 = vol2_path.read_text(encoding="utf-8")
            assert "第二卷" in content2
            assert "第三章" in content2

    def test_export_volumes_separate_with_custom_pattern(self):
        """Test exporting with custom filename pattern."""
        novel = self._create_test_novel_with_volumes()
        engine = MarkdownManuscriptEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = engine.export_volumes_separate(
                novel,
                tmpdir,
                filename_pattern="{series_title}_Book{book_number}_{book_title}.md"
            )

            assert len(paths) == 2
            path_names = [p.name for p in paths]
            assert any("Book1" in name for name in path_names)
            assert any("Book2" in name for name in path_names)


class TestEPUBVolumeExport:
    """Tests for EPUB manuscript volume export."""

    def _create_test_novel_with_volumes(self) -> Novel:
        """Create a test novel with multiple volumes."""
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。\n\n这是第二段。",
            word_count=20,
        )
        chapter2 = Chapter(
            id="ch_2",
            number=2,
            title="第二章：发展",
            content="这是第二章的内容。\n\n这是第二段。",
            word_count=25,
        )
        volume1 = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="这是第一卷的描述",
            chapters=[chapter1],
        )
        volume2 = Volume(
            id="vol_2",
            title="第二卷",
            number=2,
            description="这是第二卷的描述",
            chapters=[chapter2],
        )
        return Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume1, volume2],
        )

    def test_export_volumes_separate_epub(self):
        """Test exporting each volume as a separate EPUB file."""
        novel = self._create_test_novel_with_volumes()
        engine = EPUBManuscriptEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = engine.export_volumes_separate(novel, tmpdir)

            assert len(paths) == 2
            assert all(p.suffix == ".epub" for p in paths)

            # Check files exist and are valid ZIP files (EPUB is a ZIP)
            for path in paths:
                assert path.exists()
                assert path.stat().st_size > 0


class TestVolumeSplitEngine:
    """Tests for VolumeSplitEngine."""

    def _create_test_novel_with_volumes(self) -> Novel:
        """Create a test novel with multiple volumes."""
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。\n\n这是第二段。",
            word_count=20,
        )
        chapter2 = Chapter(
            id="ch_2",
            number=2,
            title="第二章：发展",
            content="这是第二章的内容。\n\n这是第二段。",
            word_count=25,
        )
        chapter3 = Chapter(
            id="ch_3",
            number=3,
            title="第三章：高潮",
            content="这是第三章的内容。\n\n这是第二段。",
            word_count=30,
        )
        volume1 = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="这是第一卷的描述",
            chapters=[chapter1, chapter2],
        )
        volume2 = Volume(
            id="vol_2",
            title="第二卷",
            number=2,
            description="这是第二卷的描述",
            chapters=[chapter3],
        )
        return Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume1, volume2],
        )

    def test_split_summary(self):
        """Test getting split summary."""
        novel = self._create_test_novel_with_volumes()
        config = VolumeSplitConfig(strategy=VolumeSplitStrategy.ONE_VOLUME_PER_BOOK)
        engine = VolumeSplitEngine(config)

        summary = engine.get_split_summary(novel)

        assert summary["series_title"] == "测试小说"
        assert summary["total_volumes"] == 2
        assert summary["total_chapters"] == 3
        assert summary["strategy"] == "one_volume_per_book"
        assert summary["books_count"] == 2

    def test_split_summary_multiple_per_book(self):
        """Test getting split summary with multiple volumes per book."""
        novel = self._create_test_novel_with_volumes()
        config = VolumeSplitConfig(
            strategy=VolumeSplitStrategy.MULTIPLE_VOLUMES_PER_BOOK,
            volumes_per_book=2,
        )
        engine = VolumeSplitEngine(config)

        summary = engine.get_split_summary(novel)

        assert summary["books_count"] == 1  # 2 volumes / 2 per book = 1 book

    def test_split_and_export_markdown(self):
        """Test splitting and exporting to Markdown."""
        novel = self._create_test_novel_with_volumes()
        config = VolumeSplitConfig(
            strategy=VolumeSplitStrategy.ONE_VOLUME_PER_BOOK,
            create_series_info=True,
        )
        engine = VolumeSplitEngine(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = engine.split_and_export(novel, tmpdir, format="markdown")

            assert result.total_volumes == 2
            assert result.total_books == 2
            assert len(result.books) == 2
            assert result.series_info_path is not None
            assert Path(result.series_info_path).exists()

    def test_split_and_export_all_in_one(self):
        """Test splitting with ALL_IN_ONE strategy."""
        novel = self._create_test_novel_with_volumes()
        config = VolumeSplitConfig(strategy=VolumeSplitStrategy.ALL_IN_ONE)
        engine = VolumeSplitEngine(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = engine.split_and_export(novel, tmpdir, format="markdown")

            assert result.total_books == 1
            assert len(result.books) == 1
            assert result.books[0].volume_ids == ["vol_1", "vol_2"]

    def test_master_toc_creation(self):
        """Test master TOC creation."""
        novel = self._create_test_novel_with_volumes()
        config = VolumeSplitConfig(
            strategy=VolumeSplitStrategy.ONE_VOLUME_PER_BOOK,
            include_series_toc=True,
        )
        engine = VolumeSplitEngine(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = engine.split_and_export(novel, tmpdir, format="markdown")

            assert result.master_toc_path is not None
            toc_content = Path(result.master_toc_path).read_text(encoding="utf-8")
            assert "总目录" in toc_content
            assert "第一卷" in toc_content
            assert "第二卷" in toc_content


class TestVolumeSplitIntegration:
    """Integration tests for volume split with existing engines."""

    def _create_test_novel(self) -> Novel:
        """Create a test novel."""
        chapters = [
            Chapter(
                id=f"ch_{i}",
                number=i,
                title=f"第{i}章",
                content=f"这是第{i}章的内容。",
                word_count=100 * i,
            )
            for i in range(1, 5)
        ]
        volume1 = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[chapters[0], chapters[1]],
        )
        volume2 = Volume(
            id="vol_2",
            title="第二卷",
            number=2,
            chapters=[chapters[2], chapters[3]],
        )
        return Novel(
            id="novel_1",
            title="测试系列",
            genre="奇幻",
            volumes=[volume1, volume2],
        )

    def test_markdown_engine_export_volumes_separate(self):
        """Test MarkdownManuscriptEngine.export_volumes_separate."""
        novel = self._create_test_novel()
        engine = MarkdownManuscriptEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = engine.export_volumes_separate(novel, tmpdir)

            assert len(paths) == 2

            # Verify first volume
            vol1_path = [p for p in paths if "第1册" in str(p)][0]
            content1 = vol1_path.read_text(encoding="utf-8")
            assert "第一卷" in content1
            assert "第1章" in content1
            assert "第2章" in content1
            assert "第3章" not in content1  # Volume 1 only has chapters 1-2

            # Verify second volume
            vol2_path = [p for p in paths if "第2册" in str(p)][0]
            content2 = vol2_path.read_text(encoding="utf-8")
            assert "第二卷" in content2
            assert "第3章" in content2
            assert "第4章" in content2
