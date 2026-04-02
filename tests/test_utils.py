"""Tests for utility functions."""

import pytest
import tempfile
from pathlib import Path

from chai.utils import create_sample_novel, save_novel, load_novel


class TestHelpers:
    """Tests for helper utilities."""

    def test_create_sample_novel(self):
        """Test creating a sample novel."""
        novel = create_sample_novel()

        assert novel.title == "测试小说"
        assert novel.genre == "玄幻"
        assert len(novel.characters) == 1
        assert len(novel.volumes) == 1
        assert novel.volumes[0].chapters[0].title == "第一章：开始"

    def test_save_and_load_novel(self):
        """Test saving and loading a novel."""
        original = create_sample_novel()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "novel.json"

            saved_path = save_novel(original, path)
            assert saved_path.exists()

            loaded = load_novel(path)
            assert loaded.title == original.title
            assert loaded.genre == original.genre
            assert len(loaded.volumes) == len(original.volumes)

    def test_load_novel_nonexistent(self):
        """Test loading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            load_novel("/nonexistent/path/novel.json")
