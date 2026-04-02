"""Tests for novel writing engines."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chai.models import (
    Novel, Volume, Chapter, WorldSetting, Character,
    PlotOutline, PlotArc, PlotPoint, PlotPointType, PlotStructure,
)
from chai.engines import StoryPlanner, ChapterWriter, Editor, NovelEngine
from chai.services import AIService


class TestNovelEngine:
    """Tests for NovelEngine orchestration."""

    def test_expand_outline_to_volumes(self):
        """Test expanding plot outline into volume/chapter structure."""
        world = WorldSetting(name="测试世界", genre="玄幻")
        characters = [Character(id="char_1", name="主角", role="protagonist")]

        plot_points = [
            PlotPoint(
                id=f"pp_{i}",
                point_type=PlotPointType.EXPOSITION if i == 0 else PlotPointType.RISING_ACTION,
                title=f"情节点{i + 1}",
                description=f"描述{i + 1}",
                chapter_range=(i * 3 + 1, (i + 1) * 3),
                characters_involved=["char_1"],
            )
            for i in range(4)
        ]

        arc = PlotArc(
            id="main_arc",
            name="主线",
            arc_type="main",
            plot_points=plot_points,
            protagonist="char_1",
        )

        plot_outline = PlotOutline(
            structure_type=PlotStructure.THREE_ACT,
            genre="玄幻",
            theme=["成长"],
            plot_arcs=[arc],
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            world_setting=world,
            characters=characters,
            plot_outline=plot_outline,
        )

        # Mock AI service (not actually used in _expand_outline_to_volumes)
        mock_ai = MagicMock(spec=AIService)
        engine = NovelEngine(mock_ai)

        engine._expand_outline_to_volumes(novel)

        assert len(novel.volumes) == 2  # 4 plot points / 2 = 2 volumes
        total_chapters = sum(len(v.chapters) for v in novel.volumes)
        assert total_chapters == 12  # 4 points * 3 chapters = 12

    def test_expand_outline_no_plot_points(self):
        """Test creating default structure when no plot points exist."""
        world = WorldSetting(name="测试世界", genre="玄幻")

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            world_setting=world,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = NovelEngine(mock_ai)

        engine._expand_outline_to_volumes(novel)

        assert len(novel.volumes) == 1
        assert len(novel.volumes[0].chapters) == 10  # default 10 chapters

    def test_get_novel_status(self):
        """Test getting novel status."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="内容", word_count=1000, status="complete"),
            Chapter(id="ch_2", number=2, title="第二章", content="", word_count=0, status="pending"),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = NovelEngine(mock_ai)

        status = engine.get_novel_status(novel)

        assert status["title"] == "测试小说"
        assert status["total_chapters"] == 2
        assert status["written_chapters"] == 1
        assert status["total_words"] == 1000
        assert status["progress"] == 0.5


class TestStoryPlanner:
    """Tests for StoryPlanner."""

    def test_plan_novel_mock(self):
        """Test planning a novel with mocked AI."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试世界",
            "geography": {"continents": ["大陆"]},
            "politics": {"government": "君主制"},
            "culture": {"religion": "多神教"},
            "history": {"events": []},
        })
        mock_ai.generate_characters = AsyncMock(return_value=[
            {"name": "主角", "backstory": "测试", "motivation": "成长", "goal": "变强"},
            {"name": "配角", "backstory": "测试", "motivation": "帮助", "goal": "支持"},
        ])
        mock_ai.generate_plot_outline = AsyncMock(return_value={
            "structure_type": "three_act",
            "theme": "成长",
            "plot_arcs": [{
                "plot_points": [
                    {"title": "开场", "description": "介绍主角"},
                    {"title": "转折", "description": "遇到挑战"},
                ]
            }],
        })

        planner = StoryPlanner(mock_ai)
        # Run the async planner in sync context via asyncio.run
        import asyncio
        novel = asyncio.run(planner.plan_novel("玄幻", "成长"))

        assert novel.title.startswith("成长")
        assert novel.genre == "玄幻"
        assert novel.world_setting is not None
        assert len(novel.characters) >= 1


class TestEditor:
    """Tests for Editor consistency checking."""

    def test_check_consistency_under_min(self):
        """Test detecting chapters under minimum word count."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="短", word_count=100,  # below 2000 minimum
                target_word_count=3000,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(
            id="novel_1", title="测试", genre="玄幻",
            volumes=[volume],
            target_chapter_word_count=(2000, 4000),
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        issues = editor.check_consistency(novel)

        assert len(issues) == 1
        assert "below minimum" in issues[0]

    def test_check_consistency_passing(self):
        """Test novel that passes consistency checks."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="内容" * 1000, word_count=3000,
                target_word_count=3000,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(
            id="novel_1", title="测试", genre="玄幻",
            volumes=[volume],
            target_chapter_word_count=(2000, 4000),
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        issues = editor.check_consistency(novel)

        assert len(issues) == 0

    def test_generate_consistency_report(self):
        """Test generating consistency report."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="短", word_count=100,
                target_word_count=3000,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)
        novel = Novel(
            id="novel_1", title="测试", genre="玄幻",
            volumes=[volume],
            target_chapter_word_count=(2000, 4000),
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        report = editor.generate_consistency_report(novel)

        assert "Consistency Report" in report
        assert "Chapter 1" in report
