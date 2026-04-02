"""Tests for PDF manuscript export engine."""

import pytest
from pathlib import Path
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
    PDFFont,
)
from chai.engines.pdf_manuscript_engine import PDFManuscriptEngine


class TestPDFExportModels:
    """Test PDF export model definitions."""

    def test_pdf_template_values(self):
        """Test PDFTemplate enum values."""
        assert PDFTemplate.SIMPLE.value == "simple"
        assert PDFTemplate.STANDARD.value == "standard"
        assert PDFTemplate.DETAILED.value == "detailed"

    def test_pdf_page_size_values(self):
        """Test PDFPageSize enum values."""
        assert PDFPageSize.A4.value == "A4"
        assert PDFPageSize.A5.value == "A5"
        assert PDFPageSize.B5.value == "B5"
        assert PDFPageSize.LETTER.value == "letter"
        assert PDFPageSize.LEGAL.value == "legal"

    def test_pdf_font_values(self):
        """Test PDFFont enum values."""
        assert PDFFont.SIMSUN.value == "simsun"
        assert PDFFont.TIMES.value == "times"
        assert PDFFont.SERIF.value == "serif"
        assert PDFFont.SANS_SERIF.value == "sans-serif"

    def test_pdf_export_config_defaults(self):
        """Test PDFExportConfig default values."""
        config = PDFExportConfig()
        assert config.template == PDFTemplate.STANDARD
        assert config.page_size == PDFPageSize.A5
        assert config.include_table_of_contents is True
        assert config.include_chapter_summaries is True
        assert config.include_word_counts is True
        assert config.paragraph_spacing is True
        assert config.scene_separators is True
        assert config.indent_first_line is True
        assert config.left_margin == 2.0
        assert config.right_margin == 2.0
        assert config.top_margin == 2.0
        assert config.bottom_margin == 2.0
        assert config.body_font == PDFFont.SIMSUN
        assert config.body_font_size == 11
        assert config.title_font_size == 24
        assert config.chapter_title_font_size == 16
        assert config.line_spacing == 1.8
        assert config.include_page_numbers is True
        assert config.include_chapter_headers is True

    def test_pdf_export_config_custom(self):
        """Test PDFExportConfig with custom values."""
        config = PDFExportConfig(
            template=PDFTemplate.DETAILED,
            page_size=PDFPageSize.A4,
            include_table_of_contents=False,
            body_font_size=12,
        )
        assert config.template == PDFTemplate.DETAILED
        assert config.page_size == PDFPageSize.A4
        assert config.include_table_of_contents is False
        assert config.body_font_size == 12

    def test_pdf_metadata(self):
        """Test PDFMetadata model."""
        metadata = PDFMetadata(
            title="Test Novel",
            author="Test Author",
            genre="Fantasy",
            total_words=50000,
            total_pages=200,
        )
        assert metadata.title == "Test Novel"
        assert metadata.author == "Test Author"
        assert metadata.genre == "Fantasy"
        assert metadata.total_words == 50000
        assert metadata.total_pages == 200

    def test_pdf_chapter_ref(self):
        """Test PDFChapterRef model."""
        chapter_ref = PDFChapterRef(
            chapter_id="ch_1",
            chapter_number=1,
            chapter_title="Chapter 1",
            is_prologue=False,
            is_epilogue=False,
            start_page=5,
            word_count=3000,
        )
        assert chapter_ref.chapter_id == "ch_1"
        assert chapter_ref.chapter_number == 1
        assert chapter_ref.chapter_title == "Chapter 1"
        assert chapter_ref.start_page == 5
        assert chapter_ref.word_count == 3000

    def test_pdf_volume_ref(self):
        """Test PDFVolumeRef model."""
        chapters = [
            PDFChapterRef(
                chapter_id="ch_1",
                chapter_number=1,
                chapter_title="Chapter 1",
                word_count=3000,
            ),
        ]
        volume_ref = PDFVolumeRef(
            volume_id="vol_1",
            volume_number=1,
            volume_title="Volume 1",
            description="First volume",
            chapters=chapters,
            start_page=1,
            word_count=3000,
        )
        assert volume_ref.volume_id == "vol_1"
        assert volume_ref.volume_number == 1
        assert volume_ref.volume_title == "Volume 1"
        assert len(volume_ref.chapters) == 1
        assert volume_ref.word_count == 3000

    def test_pdf_toc_entry(self):
        """Test PDFTableOfContentsEntry model."""
        toc_entry = PDFTableOfContentsEntry(
            title="Chapter 1",
            page_number=5,
            level=2,
            volume_number=1,
            chapter_number=1,
        )
        assert toc_entry.title == "Chapter 1"
        assert toc_entry.page_number == 5
        assert toc_entry.level == 2
        assert toc_entry.volume_number == 1
        assert toc_entry.chapter_number == 1

    def test_pdf_export_result(self):
        """Test PDFExportResult model."""
        config = PDFExportConfig()
        result = PDFExportResult(config=config)
        assert result.config == config
        assert result.metadata is None
        assert result.volumes == []
        assert result.toc == []
        assert result.word_count == 0


class TestPDFManuscriptEngine:
    """Test PDFManuscriptEngine functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PDFManuscriptEngine()

    def _create_sample_novel(self) -> Novel:
        """Create a sample novel for testing."""
        chapters = [
            Chapter(
                id="ch_1",
                number=1,
                title="第一章：开始",
                summary="故事从这里开始",
                content="这是第一章的内容。这是一个测试段落。",
                word_count=50,
                status="complete",
            ),
            Chapter(
                id="ch_2",
                number=2,
                title="第二章：发展",
                summary="故事继续发展",
                content="这是第二章的内容。故事在继续发展。",
                word_count=60,
                status="complete",
            ),
        ]

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="测试卷",
            chapters=chapters,
        )

        novel = Novel(
            id="test_novel",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            has_prologue=False,
            has_epilogue=False,
        )

        return novel

    def test_engine_initialization(self):
        """Test engine initialization with default config."""
        engine = PDFManuscriptEngine()
        assert engine.config.template == PDFTemplate.STANDARD
        assert engine.config.page_size == PDFPageSize.A5

    def test_engine_initialization_with_config(self):
        """Test engine initialization with custom config."""
        config = PDFExportConfig(
            template=PDFTemplate.SIMPLE,
            page_size=PDFPageSize.A4,
        )
        engine = PDFManuscriptEngine(config=config)
        assert engine.config.template == PDFTemplate.SIMPLE
        assert engine.config.page_size == PDFPageSize.A4

    def test_generate_manuscript_simple_template(self):
        """Test manuscript generation with simple template."""
        novel = self._create_sample_novel()
        engine = PDFManuscriptEngine(
            PDFExportConfig(template=PDFTemplate.SIMPLE)
        )
        result = engine.generate_manuscript(novel)

        assert result.config.template == PDFTemplate.SIMPLE
        assert result.metadata is None  # Simple template doesn't include metadata
        assert len(result.volumes) == 1
        assert len(result.volumes[0].chapters) == 2
        assert result.word_count == 110  # 50 + 60

    def test_generate_manuscript_standard_template(self):
        """Test manuscript generation with standard template."""
        novel = self._create_sample_novel()
        engine = PDFManuscriptEngine(
            PDFExportConfig(template=PDFTemplate.STANDARD)
        )
        result = engine.generate_manuscript(novel)

        assert result.config.template == PDFTemplate.STANDARD
        assert result.metadata is not None  # Standard template includes metadata
        assert len(result.volumes) == 1
        assert result.metadata.title == "测试小说"
        assert result.metadata.genre == "玄幻"

    def test_generate_manuscript_detailed_template(self):
        """Test manuscript generation with detailed template."""
        novel = self._create_sample_novel()
        engine = PDFManuscriptEngine(
            PDFExportConfig(template=PDFTemplate.DETAILED)
        )
        result = engine.generate_manuscript(novel)

        assert result.config.template == PDFTemplate.DETAILED
        assert result.metadata is not None
        assert len(result.toc) > 0  # Detailed template includes TOC

    def test_generate_manuscript_volume_refs(self):
        """Test volume and chapter references are created correctly."""
        novel = self._create_sample_novel()
        result = self.engine.generate_manuscript(novel)

        assert len(result.volumes) == 1
        volume = result.volumes[0]
        assert volume.volume_id == "vol_1"
        assert volume.volume_number == 1
        assert volume.volume_title == "第一卷"
        assert len(volume.chapters) == 2

        chapter = volume.chapters[0]
        assert chapter.chapter_id == "ch_1"
        assert chapter.chapter_number == 1
        assert chapter.chapter_title == "第一章：开始"
        assert chapter.word_count == 50

    def test_generate_manuscript_toc(self):
        """Test table of contents generation."""
        novel = self._create_sample_novel()
        config = PDFExportConfig(
            include_table_of_contents=True,
            template=PDFTemplate.DETAILED,
        )
        engine = PDFManuscriptEngine(config=config)
        result = engine.generate_manuscript(novel)

        # TOC should have volume entry + 2 chapter entries
        assert len(result.toc) == 3

        # First entry should be volume
        assert result.toc[0].level == 1
        assert result.toc[0].title == "第一卷"

        # Subsequent entries should be chapters
        assert result.toc[1].level == 2
        assert result.toc[1].chapter_number == 1
        assert result.toc[2].level == 2
        assert result.toc[2].chapter_number == 2

    def test_generate_manuscript_without_toc(self):
        """Test manuscript generation without TOC."""
        novel = self._create_sample_novel()
        config = PDFExportConfig(
            include_table_of_contents=False,
            template=PDFTemplate.DETAILED,
        )
        engine = PDFManuscriptEngine(config=config)
        result = engine.generate_manuscript(novel)

        assert result.toc == []

    def test_generate_manuscript_word_count(self):
        """Test word count calculation."""
        novel = self._create_sample_novel()
        result = self.engine.generate_manuscript(novel)

        assert result.word_count == 110  # 50 + 60

    def test_get_manuscript_summary(self):
        """Test manuscript summary generation."""
        novel = self._create_sample_novel()
        result = self.engine.generate_manuscript(novel)
        summary = self.engine.get_manuscript_summary(result)

        assert "PDF Manuscript Summary" in summary
        assert "Total Volumes: 1" in summary
        assert "Total Chapters: 2" in summary
        assert "Total Words: 110" in summary

    def test_get_manuscript_summary_with_toc(self):
        """Test manuscript summary includes TOC info."""
        config = PDFExportConfig(template=PDFTemplate.DETAILED)
        engine = PDFManuscriptEngine(config=config)
        novel = self._create_sample_novel()
        result = engine.generate_manuscript(novel)
        summary = engine.get_manuscript_summary(result)

        assert "Table of Contents: Yes" in summary

    def test_multivolume_novel(self):
        """Test manuscript generation with multiple volumes."""
        chapters1 = [
            Chapter(id="ch_1", number=1, title="Chapter 1", content="Content 1", word_count=100),
        ]
        chapters2 = [
            Chapter(id="ch_2", number=2, title="Chapter 2", content="Content 2", word_count=200),
        ]

        volume1 = Volume(id="vol_1", title="Volume 1", number=1, chapters=chapters1)
        volume2 = Volume(id="vol_2", title="Volume 2", number=2, chapters=chapters2)

        novel = Novel(
            id="test_novel",
            title="Multi-Volume Novel",
            genre="Fantasy",
            volumes=[volume1, volume2],
        )

        result = self.engine.generate_manuscript(novel)

        assert len(result.volumes) == 2
        assert result.volumes[0].volume_title == "Volume 1"
        assert result.volumes[1].volume_title == "Volume 2"
        assert result.word_count == 300

    def test_novel_with_prologue_epilogue(self):
        """Test manuscript generation with prologue and epilogue."""
        chapters = [
            Chapter(
                id="ch_0",
                number=0,
                title="序章",
                is_prologue=True,
                content="序章内容",
                word_count=100,
            ),
            Chapter(
                id="ch_1",
                number=1,
                title="第一章",
                content="第一章内容",
                word_count=200,
            ),
            Chapter(
                id="ch_n",
                number=99,
                title="尾声",
                is_epilogue=True,
                content="尾声内容",
                word_count=100,
            ),
        ]

        volume = Volume(id="vol_1", title="Volume 1", number=1, chapters=chapters)
        novel = Novel(
            id="test_novel",
            title="Novel with Prologue",
            genre="Fantasy",
            volumes=[volume],
            has_prologue=True,
            has_epilogue=True,
        )

        result = self.engine.generate_manuscript(novel)

        assert len(result.volumes[0].chapters) == 3
        prologue = result.volumes[0].chapters[0]
        assert prologue.is_prologue is True
        epilogue = result.volumes[0].chapters[2]
        assert epilogue.is_epilogue is True


class TestPDFManuscriptEngineIntegration:
    """Integration tests for PDF export that require reportlab."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PDFManuscriptEngine()

    def _create_sample_novel(self) -> Novel:
        """Create a sample novel for testing."""
        chapters = [
            Chapter(
                id="ch_1",
                number=1,
                title="第一章：开始",
                summary="测试概要",
                content="这是第一章的测试内容。",
                word_count=50,
                status="complete",
            ),
        ]
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=chapters,
        )
        return Novel(
            id="test_novel",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

    def test_export_to_file_creates_pdf(self, tmp_path):
        """Test that export_to_file creates a PDF file."""
        novel = self._create_sample_novel()
        output_path = tmp_path / "test_novel.pdf"

        try:
            path = self.engine.export_to_file(novel, output_path)
            assert path.exists()
            assert path.suffix == ".pdf"
            assert path.stat().st_size > 0
        except ImportError:
            pytest.skip("reportlab not installed")
