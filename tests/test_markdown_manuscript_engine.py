"""Tests for Markdown manuscript export engine."""

import pytest
import tempfile
from pathlib import Path

from chai.models import Novel, Volume, Chapter, Scene, SceneType
from chai.models.manuscript_export import (
    ManuscriptTemplate,
    ManuscriptExportConfig,
    ManuscriptExportResult,
)
from chai.engines.markdown_manuscript_engine import MarkdownManuscriptEngine


class TestMarkdownManuscriptEngine:
    """Tests for MarkdownManuscriptEngine."""

    def test_simple_template_export(self):
        """Test exporting with simple template."""
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

        config = ManuscriptExportConfig(template=ManuscriptTemplate.SIMPLE)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        # Simple template: no front matter, just volume and chapter headings
        assert "第一卷" in result.content
        assert "第一章" in result.content
        assert "这是第一章的内容" in result.content
        # Simple template should not have TOC, front matter with novel title, or extra formatting
        assert "目录" not in result.content
        assert "---" not in result.content
        assert "作者" not in result.content

    def test_standard_template_export(self):
        """Test exporting with standard template."""
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

        config = ManuscriptExportConfig(template=ManuscriptTemplate.STANDARD)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert "测试小说" in result.content
        assert "目录" in result.content
        assert "第一卷" in result.content
        assert "第一章" in result.content
        assert "测试卷描述" in result.content
        assert "10 字" in result.content

    def test_detailed_template_export(self):
        """Test exporting with detailed template."""
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

        config = ManuscriptExportConfig(template=ManuscriptTemplate.DETAILED)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert "测试小说" in result.content
        assert "目录" in result.content
        assert "附录" in result.content
        assert "总字数" in result.content
        assert "章节字数统计" in result.content

    def test_export_with_scenes(self):
        """Test exporting with scene content."""
        scene1 = Scene(
            id="scene_1",
            number=1,
            scene_type=SceneType.NARRATIVE,
            location="森林",
            time_period="夜晚",
            mood="神秘",
            content="场景一的内容。",
        )
        scene2 = Scene(
            id="scene_2",
            number=2,
            scene_type=SceneType.DIALOGUE,
            location="森林",
            time_period="夜晚",
            mood="紧张",
            content="场景二的内容。",
        )
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="章节内容",
            word_count=20,
            scenes=[scene1, scene2],
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

        config = ManuscriptExportConfig(
            template=ManuscriptTemplate.STANDARD,
            include_scene_content=True,
            scene_separators=True,
        )
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert "场景 1" in result.content
        assert "森林" in result.content
        assert "夜晚" in result.content
        assert "───" in result.content

    def test_export_with_prologue_epilogue(self):
        """Test exporting with prologue and epilogue."""
        prologue = Chapter(
            id="ch_0",
            number=0,
            title="序章",
            content="这是序章内容。",
            word_count=10,
            is_prologue=True,
        )
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是第一章内容。",
            word_count=10,
        )
        epilogue = Chapter(
            id="ch_99",
            number=99,
            title="尾声",
            content="这是尾声内容。",
            word_count=10,
            is_epilogue=True,
        )
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[prologue, chapter1, epilogue],
        )
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            has_prologue=True,
            has_epilogue=True,
        )

        config = ManuscriptExportConfig(template=ManuscriptTemplate.STANDARD)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert "序章" in result.content
        assert "尾声" in result.content

    def test_toc_prologue_epilogue_flags(self):
        """Test that TOC entries have correct prologue/epilogue flags."""
        prologue = Chapter(
            id="ch_0",
            number=0,
            title="序章",
            content="这是序章内容。",
            word_count=10,
            is_prologue=True,
        )
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是第一章内容。",
            word_count=10,
        )
        epilogue = Chapter(
            id="ch_99",
            number=99,
            title="尾声",
            content="这是尾声内容。",
            word_count=10,
            is_epilogue=True,
        )
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[prologue, chapter1, epilogue],
        )
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        config = ManuscriptExportConfig(template=ManuscriptTemplate.STANDARD)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        # Verify TOC entries have correct flags
        assert result.toc is not None
        entries = result.toc.entries

        # Volume entry
        vol_entry = entries[0]
        assert vol_entry.level == 1
        assert vol_entry.title == "第一卷"

        # Prologue entry
        prologue_entry = entries[1]
        assert prologue_entry.level == 2
        assert prologue_entry.is_prologue is True
        assert prologue_entry.is_epilogue is False

        # Chapter entry
        chapter_entry = entries[2]
        assert chapter_entry.level == 2
        assert chapter_entry.is_prologue is False
        assert chapter_entry.is_epilogue is False

        # Epilogue entry
        epilogue_entry = entries[3]
        assert epilogue_entry.level == 2
        assert epilogue_entry.is_prologue is False
        assert epilogue_entry.is_epilogue is True

    def test_toc_renders_prologue_epilogue_correctly(self):
        """Test that TOC renders prologue/epilogue with correct prefixes."""
        prologue = Chapter(
            id="ch_0",
            number=0,
            title="序章",
            content="这是序章内容。",
            word_count=10,
            is_prologue=True,
        )
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是第一章内容。",
            word_count=10,
        )
        epilogue = Chapter(
            id="ch_99",
            number=99,
            title="尾声",
            content="这是尾声内容。",
            word_count=10,
            is_epilogue=True,
        )
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[prologue, chapter1, epilogue],
        )
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        config = ManuscriptExportConfig(template=ManuscriptTemplate.STANDARD)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        # Verify rendered TOC contains prologue/epilogue with correct prefixes
        assert result.toc is not None
        toc_content = engine._render_toc(result.toc)

        # TOC should contain "序章：" prefix for prologue
        assert "序章：" in toc_content
        # TOC should contain "尾声：" prefix for epilogue
        assert "尾声：" in toc_content
        # TOC should NOT have "第0章" or "第99章" for prologue/epilogue
        assert "第0章" not in toc_content
        assert "第99章" not in toc_content
        # Regular chapters should have "第X章" prefix
        assert "第1章" in toc_content

    def test_export_to_file(self):
        """Test exporting to a file."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="测试内容",
            word_count=5,
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
            config = ManuscriptExportConfig()
            engine = MarkdownManuscriptEngine(config)
            path = engine.export_to_file(novel, Path(tmpdir) / "manuscript.md")

            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "测试小说" in content

    def test_export_chapters_separate(self):
        """Test exporting chapters as separate files."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容1", word_count=5),
            Chapter(id="ch_2", number=2, title="第二章", content="内容2", word_count=5),
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
            config = ManuscriptExportConfig()
            engine = MarkdownManuscriptEngine(config)
            paths = engine.export_chapters_separate(novel, tmpdir)

            assert len(paths) == 2
            assert all(p.exists() for p in paths)

    def test_manuscript_summary(self):
        """Test getting manuscript summary."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="测试内容",
            word_count=1000,
            scenes=[
                Scene(id="s1", number=1, content="场景1", word_count=500),
                Scene(id="s2", number=2, content="场景2", word_count=500),
            ],
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
            has_prologue=True,
            has_epilogue=True,
        )

        engine = MarkdownManuscriptEngine()
        summary = engine.get_manuscript_summary(novel)

        assert summary["title"] == "测试小说"
        assert summary["genre"] == "玄幻"
        assert summary["total_volumes"] == 1
        assert summary["total_chapters"] == 1
        assert summary["total_scenes"] == 2
        assert summary["total_words"] == 1000
        assert summary["has_prologue"] is True
        assert summary["has_epilogue"] is True

    def test_multiple_volumes(self):
        """Test exporting with multiple volumes."""
        vol1_chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容1", word_count=10),
        ]
        vol2_chapters = [
            Chapter(id="ch_2", number=2, title="第二章", content="内容2", word_count=10),
        ]
        volume1 = Volume(id="vol_1", title="第一卷", number=1, chapters=vol1_chapters)
        volume2 = Volume(id="vol_2", title="第二卷", number=2, chapters=vol2_chapters)
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume1, volume2],
        )

        config = ManuscriptExportConfig(template=ManuscriptTemplate.STANDARD)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)

        assert "第一卷" in result.content
        assert "第二卷" in result.content
        assert "第一章" in result.content
        assert "第二章" in result.content

    def test_config_options(self):
        """Test different configuration options."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="内容",
            word_count=10,
            summary="章节概要",
        )
        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            description="卷描述",
            chapters=[chapter],
        )
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        # Test without chapter summaries
        config = ManuscriptExportConfig(
            template=ManuscriptTemplate.STANDARD,
            include_chapter_summaries=False,
        )
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)
        assert "章节概要" not in result.content

        # Test without word counts - chapter word count should not appear
        config = ManuscriptExportConfig(
            template=ManuscriptTemplate.STANDARD,
            include_word_counts=False,
        )
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)
        # Chapter-specific word count should not appear (but total in front matter might)
        # Check that the chapter heading doesn't have *10 字*
        assert "*10 字*" not in result.content

    def test_anchor_creation(self):
        """Test anchor creation for links."""
        engine = MarkdownManuscriptEngine()

        anchor = engine._create_anchor("第一章：开始")
        assert anchor == "第一章-开始"

        anchor = engine._create_anchor("Test (Chapter 1)")
        assert anchor == "test-chapter-1"

        anchor = engine._create_anchor("第--一--章")
        assert anchor == "第-一-章"

    def test_paragraph_formatting(self):
        """Test paragraph formatting options."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="第一段。\n\n第二段。\n\n第三段。",
            word_count=15,
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

        # Test with paragraph spacing
        config = ManuscriptExportConfig(paragraph_spacing=True)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)
        # Should have newlines between paragraphs
        assert "第一段" in result.content

        # Test with first line indent
        config = ManuscriptExportConfig(indent_first_line=True)
        engine = MarkdownManuscriptEngine(config)
        result = engine.generate_manuscript(novel)
        assert "　　第一段" in result.content or "第一段" in result.content


class TestManuscriptExportConfig:
    """Tests for ManuscriptExportConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ManuscriptExportConfig()

        assert config.template == ManuscriptTemplate.STANDARD
        assert config.include_table_of_contents is True
        assert config.include_chapter_summaries is True
        assert config.include_character_list is False
        assert config.include_world_setting is False
        assert config.include_scene_content is False
        assert config.include_word_counts is True
        assert config.paragraph_spacing is True
        assert config.scene_separators is True
        assert config.indent_first_line is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = ManuscriptExportConfig(
            template=ManuscriptTemplate.DETAILED,
            include_table_of_contents=False,
            include_scene_content=True,
            scene_separators=False,
        )

        assert config.template == ManuscriptTemplate.DETAILED
        assert config.include_table_of_contents is False
        assert config.include_scene_content is True
        assert config.scene_separators is False
