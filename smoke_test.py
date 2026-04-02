#!/usr/bin/env python3
"""Smoke test for CHAI system."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chai.models import (
    WorldSetting,
    Character,
    CharacterRole,
    PlotOutline,
    Novel,
    Volume,
    Chapter,
)
from chai.export import MarkdownExporter, EPUBExporter
from chai.utils import create_sample_novel, save_novel, load_novel


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    from chai import (
        Novel,
        Chapter,
        Scene,
        Character,
        CharacterRelationship,
        WorldSetting,
        PlotOutline,
    )
    from chai.services import AIService, AIConfig
    from chai.engines import StoryPlanner, ChapterWriter, Editor, NovelEngine
    from chai.export import MarkdownExporter, EPUBExporter, PDFExporter
    print("  All imports successful")


def test_model_creation():
    """Test creating data models."""
    print("Testing model creation...")

    world = WorldSetting(name="测试世界", genre="玄幻")
    assert world.name == "测试世界"
    print("  WorldSetting created")

    char = Character(
        id="test_1",
        name="测试角色",
        role=CharacterRole.PROTAGONIST,
    )
    assert char.name == "测试角色"
    print("  Character created")

    chapter = Chapter(
        id="ch_1",
        number=1,
        title="第一章",
        content="测试内容",
        word_count=10,
    )
    assert chapter.number == 1
    print("  Chapter created")

    volume = Volume(
        id="vol_1",
        title="第一卷",
        number=1,
        chapters=[chapter],
    )
    assert len(volume.chapters) == 1
    print("  Volume created")

    novel = Novel(
        id="novel_1",
        title="测试小说",
        genre="玄幻",
        volumes=[volume],
    )
    assert novel.title == "测试小说"
    print("  Novel created")


def test_export():
    """Test export functionality."""
    print("Testing export...")

    novel = create_sample_novel()

    exporter = MarkdownExporter()
    md = exporter.export_novel(novel)
    assert "# 测试小说" in md
    print("  Markdown export successful")

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = exporter.export_to_file(novel, Path(tmpdir) / "test.md")
        assert md_path.exists()
        print("  Markdown file created")

        epub_exporter = EPUBExporter()
        epub_path = epub_exporter.export_to_file(novel, Path(tmpdir) / "test.epub")
        assert epub_path.exists()
        assert epub_path.stat().st_size > 0
        print("  EPUB file created")


def test_utils():
    """Test utility functions."""
    print("Testing utilities...")

    novel = create_sample_novel()
    assert novel.title == "测试小说"
    print("  Sample novel created")

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        path = save_novel(novel, Path(tmpdir) / "novel.json")
        assert path.exists()

        loaded = load_novel(path)
        assert loaded.title == novel.title
        print("  Save/load successful")


def run_smoke_tests():
    """Run all smoke tests."""
    print("=" * 50)
    print("CHAI Smoke Tests")
    print("=" * 50)

    try:
        test_imports()
        test_model_creation()
        test_export()
        test_utils()

        print("=" * 50)
        print("All smoke tests PASSED")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\nSMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_smoke_tests())
