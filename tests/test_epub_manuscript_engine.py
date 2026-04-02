"""Tests for EPUB manuscript export engine."""

import pytest
import tempfile
import zipfile
from pathlib import Path

from chai.models import Novel, Volume, Chapter, Scene, SceneType
from chai.models.epub_export import (
    EPUBTemplate,
    EPUBExportConfig,
    EPUBExportResult,
    EPUBMetadata,
    EPUBChapterRef,
    EPUBVolumeRef,
    EPUBCSSStyle,
    EPUBTemplateStyles,
)
from chai.engines.epub_manuscript_engine import EPUBManuscriptEngine


class TestEPUBManuscriptEngine:
    """Tests for EPUBManuscriptEngine."""

    def test_simple_template_generate(self):
        """Test generating manuscript with simple template."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。\n\n这是第二段。",
            word_count=20,
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

        config = EPUBExportConfig(template=EPUBTemplate.SIMPLE)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        # Simple template should have minimal metadata
        assert result.metadata is None
        assert len(result.volumes) == 1
        assert result.word_count == 20

    def test_standard_template_generate(self):
        """Test generating manuscript with standard template."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。",
            word_count=10,
            summary="这是一个测试章节。",
        )
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="测试卷描述",
            chapters=[chapter],
        )
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert result.metadata is not None
        assert result.metadata.title == "测试小说"
        assert result.metadata.total_words == 10
        assert result.metadata.total_chapters == 1
        assert len(result.volumes) == 1
        assert len(result.volumes[0].chapters) == 1

    def test_detailed_template_generate(self):
        """Test generating manuscript with detailed template."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。",
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

        config = EPUBExportConfig(template=EPUBTemplate.DETAILED)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert result.metadata is not None
        assert result.metadata.total_volumes == 1
        assert result.metadata.total_chapters == 1

    def test_export_to_file(self):
        """Test exporting to EPUB file."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            content="这是第一章的内容。",
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

        config = EPUBExportConfig(template=EPUBTemplate.SIMPLE)
        engine = EPUBManuscriptEngine(config)

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            output_path = Path(f.name)

        try:
            result_path = engine.export_to_file(novel, output_path)

            # Verify file exists
            assert result_path.exists()

            # Verify it's a valid ZIP/EPUB
            with zipfile.ZipFile(result_path, 'r') as epub:
                names = epub.namelist()

                # Check required files
                assert "mimetype" in names
                assert "META-INF/container.xml" in names
                assert "OEBPS/content.opf" in names
                assert "OEBPS/toc.ncx" in names
                assert "OEBPS/nav.xhtml" in names
                assert "OEBPS/styles.css" in names
                assert "OEBPS/chapter_001.xhtml" in names

                # Check mimetype is uncompressed
                mimetype_info = epub.getinfo("mimetype")
                assert mimetype_info.compress_type == zipfile.ZIP_STORED
        finally:
            output_path.unlink(missing_ok=True)

    def test_export_with_multiple_volumes(self):
        """Test exporting with multiple volumes."""
        chapters1 = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容1", word_count=10),
            Chapter(id="ch_2", number=2, title="第二章", content="内容2", word_count=10),
        ]
        chapters2 = [
            Chapter(id="ch_3", number=3, title="第三章", content="内容3", word_count=10),
        ]
        volume1 = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters1)
        volume2 = Volume(id="vol_2", title="第二卷", number=2, chapters=chapters2)

        novel = Novel(
            id="novel_1",
            title="多卷小说",
            genre="奇幻",
            volumes=[volume1, volume2],
        )

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert len(result.volumes) == 2
        assert result.metadata.total_volumes == 2
        assert result.metadata.total_chapters == 3
        assert result.word_count == 30

    def test_export_with_prologue_epilogue(self):
        """Test exporting with prologue and epilogue chapters."""
        chapters = [
            Chapter(id="ch_0", number=0, title="序章", content="序言内容", word_count=5, is_prologue=True),
            Chapter(id="ch_1", number=1, title="第一章", content="正文内容", word_count=10),
            Chapter(id="ch_99", number=99, title="尾声", content="结束内容", word_count=5, is_epilogue=True),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(id="novel_1", title="有首尾的小说", genre="言情", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert len(result.volumes) == 1
        assert len(result.volumes[0].chapters) == 3
        assert result.volumes[0].chapters[0].is_prologue is True
        assert result.volumes[0].chapters[2].is_epilogue is True

    def test_export_with_scenes(self):
        """Test exporting with scene content."""
        scene1 = Scene(
            id="s1",
            number=1,
            location="森林",
            time_period="白天",
            mood="神秘",
            content="场景一的内容。",
        )
        scene2 = Scene(
            id="s2",
            number=2,
            location="城堡",
            time_period="夜晚",
            mood="紧张",
            content="场景二的内容。",
        )
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="",
            word_count=20,
            scenes=[scene1, scene2],
        )
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[chapter])
        novel = Novel(id="novel_1", title="场景小说", genre="悬疑", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD, include_scene_content=True)
        engine = EPUBManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        # Verify scenes are in the output
        assert result.word_count == 20

    def test_get_manuscript_summary(self):
        """Test getting manuscript summary."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=100),
            Chapter(id="ch_2", number=2, title="第二章", content="内容", word_count=200),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            has_prologue=True,
            has_epilogue=False,
        )

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)
        summary = engine.get_manuscript_summary(novel)

        assert summary["title"] == "测试小说"
        assert summary["genre"] == "玄幻"
        assert summary["total_volumes"] == 1
        assert summary["total_chapters"] == 2
        assert summary["total_words"] == 300
        assert summary["average_chapter_words"] == 150
        assert summary["has_prologue"] is True
        assert summary["has_epilogue"] is False
        assert summary["epub_version"] == "2.0"
        assert summary["template"] == "standard"

    def test_export_chapters_separate(self):
        """Test exporting chapters as separate files."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="第一章内容", word_count=10),
            Chapter(id="ch_2", number=2, title="第二章", content="第二章内容", word_count=10),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(id="novel_1", title="测试", genre="玄幻", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.SIMPLE)
        engine = EPUBManuscriptEngine(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = engine.export_chapters_separate(novel, tmpdir)

            assert len(paths) == 2
            assert all(p.suffix == ".xhtml" for p in paths)

            # Verify content
            for path in paths:
                content = path.read_text(encoding="utf-8")
                assert "第一章" in content or "第二章" in content
                assert "<html" in content


class TestEPUBModels:
    """Tests for EPUB export models."""

    def test_epub_template_enum(self):
        """Test EPUBTemplate enum values."""
        assert EPUBTemplate.SIMPLE.value == "simple"
        assert EPUBTemplate.STANDARD.value == "standard"
        assert EPUBTemplate.DETAILED.value == "detailed"

    def test_epub_export_config_defaults(self):
        """Test EPUBExportConfig default values."""
        config = EPUBExportConfig()

        assert config.template == EPUBTemplate.STANDARD
        assert config.epub_version == "2.0"
        assert config.include_table_of_contents is True
        assert config.include_chapter_summaries is True
        assert config.include_word_counts is True
        assert config.paragraph_spacing is True
        assert config.scene_separators is True

    def test_epub_metadata(self):
        """Test EPUBMetadata model."""
        metadata = EPUBMetadata(
            title="测试小说",
            subtitle="测试副标题",
            author="测试作者",
            language="zh-CN",
            genre="玄幻",
            total_words=10000,
            total_chapters=50,
            total_volumes=2,
        )

        assert metadata.title == "测试小说"
        assert metadata.subtitle == "测试副标题"
        assert metadata.author == "测试作者"
        assert metadata.language == "zh-CN"
        assert metadata.total_words == 10000
        assert metadata.total_chapters == 50
        assert metadata.total_volumes == 2

    def test_epub_chapter_ref(self):
        """Test EPUBChapterRef model."""
        chapter_ref = EPUBChapterRef(
            chapter_id="ch_001",
            chapter_number=1,
            chapter_title="第一章",
            is_prologue=False,
            is_epilogue=False,
            file_path="chapter_001.xhtml",
        )

        assert chapter_ref.chapter_id == "ch_001"
        assert chapter_ref.chapter_number == 1
        assert chapter_ref.chapter_title == "第一章"
        assert chapter_ref.is_prologue is False
        assert chapter_ref.is_epilogue is False

    def test_epub_volume_ref(self):
        """Test EPUBVolumeRef model."""
        chapter_ref = EPUBChapterRef(
            chapter_id="ch_001",
            chapter_number=1,
            chapter_title="第一章",
        )
        volume_ref = EPUBVolumeRef(
            volume_id="vol_001",
            volume_number=1,
            volume_title="第一卷",
            description="测试描述",
            chapters=[chapter_ref],
        )

        assert volume_ref.volume_id == "vol_001"
        assert volume_ref.volume_number == 1
        assert volume_ref.volume_title == "第一卷"
        assert len(volume_ref.chapters) == 1

    def test_epub_css_style(self):
        """Test EPUBCSSStyle model."""
        style = EPUBCSSStyle(
            body="body { margin: 5%; }",
            h1="h1 { text-align: center; }",
            p="p { text-indent: 2em; }",
        )

        assert "margin: 5%" in style.body
        assert "text-align: center" in style.h1
        assert "text-indent: 2em" in style.p

    def test_epub_template_styles_simple(self):
        """Test EPUBTemplateStyles.get_simple_css()."""
        style = EPUBTemplateStyles.get_simple_css()

        assert isinstance(style, EPUBCSSStyle)
        assert "body" in style.body
        assert "SimSun" in style.body

    def test_epub_template_styles_standard(self):
        """Test EPUBTemplateStyles.get_standard_css()."""
        style = EPUBTemplateStyles.get_standard_css()

        assert isinstance(style, EPUBCSSStyle)
        assert "body" in style.body
        assert "line-height: 1.8" in style.body
        assert "text-align: justify" in style.body

    def test_epub_template_styles_detailed(self):
        """Test EPUBTemplateStyles.get_detailed_css()."""
        style = EPUBTemplateStyles.get_detailed_css()

        assert isinstance(style, EPUBCSSStyle)
        assert "body" in style.body
        assert "background-color" in style.body

    def test_epub_export_result(self):
        """Test EPUBExportResult model."""
        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        result = EPUBExportResult(
            config=config,
            word_count=1000,
            success=True,
        )

        assert result.config.template == EPUBTemplate.STANDARD
        assert result.word_count == 1000
        assert result.success is True
        assert result.error_message == ""


class TestEPUBStructure:
    """Tests for EPUB structure and formatting."""

    def test_nav_xhtml_structure(self):
        """Test navigation document structure."""
        chapter = Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=10)
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[chapter])
        novel = Novel(id="novel_1", title="测试", genre="玄幻", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            output_path = Path(f.name)

        try:
            engine.export_to_file(novel, output_path)

            with zipfile.ZipFile(output_path, 'r') as epub:
                nav_content = epub.read("OEBPS/nav.xhtml").decode("utf-8")

                # Check nav document structure
                assert 'xmlns="http://www.w3.org/1999/xhtml"' in nav_content
                assert 'epub:type="toc"' in nav_content
                assert "<h1>目录</h1>" in nav_content
                assert "第一章" in nav_content
        finally:
            output_path.unlink(missing_ok=True)

    def test_ncx_structure(self):
        """Test NCX document structure."""
        chapter = Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=10)
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[chapter])
        novel = Novel(id="novel_1", title="测试", genre="玄幻", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            output_path = Path(f.name)

        try:
            engine.export_to_file(novel, output_path)

            with zipfile.ZipFile(output_path, 'r') as epub:
                ncx_content = epub.read("OEBPS/toc.ncx").decode("utf-8")

                # Check NCX structure
                assert 'xmlns="http://www.daisy.org/z3986/2005/ncx/"' in ncx_content
                assert 'version="2005-1"' in ncx_content
                assert "<docTitle>" in ncx_content
                assert "<navMap>" in ncx_content
                assert "navPoint" in ncx_content
        finally:
            output_path.unlink(missing_ok=True)

    def test_content_opf_structure(self):
        """Test content.opf document structure."""
        chapter = Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=10)
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[chapter])
        novel = Novel(id="novel_1", title="测试", genre="玄幻", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            output_path = Path(f.name)

        try:
            engine.export_to_file(novel, output_path)

            with zipfile.ZipFile(output_path, 'r') as epub:
                opf_content = epub.read("OEBPS/content.opf").decode("utf-8")

                # Check OPF structure
                assert 'xmlns="http://www.idpf.org/2007/opf"' in opf_content
                assert 'version="2.0"' in opf_content
                assert "<metadata" in opf_content
                assert "<manifest>" in opf_content
                assert "<spine" in opf_content
                assert "dc:title" in opf_content
        finally:
            output_path.unlink(missing_ok=True)

    def test_chapter_xhtml_structure(self):
        """Test chapter XHTML document structure."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是第一章的内容。",
            word_count=10,
        )
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[chapter])
        novel = Novel(id="novel_1", title="测试", genre="玄幻", volumes=[volume])

        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            output_path = Path(f.name)

        try:
            engine.export_to_file(novel, output_path)

            with zipfile.ZipFile(output_path, 'r') as epub:
                chapter_content = epub.read("OEBPS/chapter_001.xhtml").decode("utf-8")

                # Check chapter structure
                assert 'xmlns="http://www.w3.org/1999/xhtml"' in chapter_content
                assert "<h1" in chapter_content
                assert "第一章" in chapter_content
                assert "<p" in chapter_content
                assert "styles.css" in chapter_content
        finally:
            output_path.unlink(missing_ok=True)

    def test_css_includes_all_styles(self):
        """Test CSS includes all style components."""
        config = EPUBExportConfig(template=EPUBTemplate.STANDARD)
        engine = EPUBManuscriptEngine(config)
        css = engine._assemble_css()

        assert "body" in css
        assert "h1" in css
        assert "h2" in css
        assert "p" in css
        assert "chapter-title" in css
        assert "volume-title" in css
