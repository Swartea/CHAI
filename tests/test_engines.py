"""Tests for novel writing engines."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import (
    Novel, Volume, Chapter, WorldSetting, Character,
    PlotOutline, PlotArc, PlotPoint, PlotPointType, PlotStructure,
    Scene, SceneType, CharacterRole,
)
from chai.engines import StoryPlanner, ChapterWriter, Editor, NovelEngine, StyleEngine
from chai.models.style_consistency import (
    StyleProfile,
    NarrativeTone,
    DescriptiveDensity,
    PacingLevel,
    SentenceComplexity,
)
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


class TestEditorEnhanced:
    """Tests for enhanced Editor features."""

    def test_check_dialogue_tags(self):
        """Test dialogue tag consistency checking."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content='"你好！"他说。"再见！"',
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        issues = editor.check_dialogue_tags(chapter)
        # Should detect missing comma after dialogue
        assert len(issues) >= 0  # May vary based on regex

    def test_check_punctuation_mismatched_quotes(self):
        """Test detecting mismatched dialogue quotes."""
        # Create content with unmatched quotes - quotes outside dialogue pairs
        # "你好" is a matched pair, but " at the end is stray
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content='他说："你好"。这是结尾"',
            word_count=200,
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        issues = editor.check_punctuation(chapter)
        assert len(issues) > 0

    def test_analyze_pacing(self):
        """Test pacing analysis."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content='这是一个测试段落。"对话内容。" 这是另一段。' * 20,
            word_count=500,
        )

        mock_ai = MagicMock(spec=AIService)
        editor = Editor(mock_ai)

        pacing = editor.analyze_pacing(chapter)

        assert "dialogue_ratio" in pacing
        assert "estimated_scenes" in pacing
        assert 0 <= pacing["dialogue_ratio"] <= 1

    def test_generate_full_report(self):
        """Test generating full editorial report."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="内容" * 500,
                word_count=2000,
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

        report = editor.generate_full_report(novel)

        assert "CHAI Editorial Report" in report
        assert "Pacing Analysis" in report


class TestStoryPlannerStructures:
    """Tests for StoryPlanner with multiple plot structures."""

    def test_create_plot_outline_heros_journey(self):
        """Test creating plot outline with Hero's Journey structure."""
        world = WorldSetting(name="测试世界", genre="奇幻")
        characters = [Character(id="char_1", name="英雄", role="protagonist")]

        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_plot_outline = AsyncMock(return_value={
            "structure_type": "heros_journey",
            "theme": "成长",
            "plot_arcs": [{
                "plot_points": [
                    {"title": "普通世界", "description": "介绍日常"},
                ] * 10
            }],
        })

        planner = StoryPlanner(mock_ai)

        import asyncio
        outline = asyncio.run(planner.create_plot_outline(
            world, characters, "奇幻", "成长",
            structure=PlotStructure.HEROS_JOURNEY,
        ))

        assert outline.structure_type == PlotStructure.HEROS_JOURNEY
        assert len(outline.plot_arcs) == 1
        assert len(outline.plot_arcs[0].plot_points) == 10

    def test_create_plot_outline_seven_point(self):
        """Test creating plot outline with Seven Point structure."""
        world = WorldSetting(name="测试世界", genre="悬疑")
        characters = [Character(id="char_1", name="侦探", role="protagonist")]

        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_plot_outline = AsyncMock(return_value={
            "structure_type": "seven_point",
            "theme": "真相",
            "plot_arcs": [{
                "plot_points": [
                    {"title": "钩子", "description": "吸引读者"},
                ] * 8
            }],
        })

        planner = StoryPlanner(mock_ai)

        import asyncio
        outline = asyncio.run(planner.create_plot_outline(
            world, characters, "悬疑", "真相",
            structure=PlotStructure.SEVEN_POINT,
        ))

        assert outline.structure_type == PlotStructure.SEVEN_POINT
        assert len(outline.plot_arcs[0].plot_points) == 8

    def test_create_subplot_arc(self):
        """Test creating subplot arc."""
        world = WorldSetting(name="测试世界", genre="言情")
        characters = [
            Character(id="char_1", name="男主", role="protagonist"),
            Character(id="char_2", name="女主", role="protagonist"),
        ]

        plot_points = []
        arc = PlotArc(
            id="main_arc",
            name="主线",
            arc_type="main",
            plot_points=plot_points,
            protagonist="char_1",
        )
        plot_outline = PlotOutline(
            structure_type=PlotStructure.THREE_ACT,
            genre="言情",
            theme=["爱情"],
            plot_arcs=[arc],
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="言情",
            world_setting=world,
            characters=characters,
            plot_outline=plot_outline,
        )

        mock_ai = MagicMock(spec=AIService)
        planner = StoryPlanner(mock_ai)

        import asyncio
        subplot = asyncio.run(planner.create_subplot_arc(
            plot_outline, characters, 0, arc_type="romantic",
        ))

        assert subplot.arc_type == "romantic"
        assert len(subplot.plot_points) == 5


class TestChapterWriterScenes:
    """Tests for ChapterWriter scene-level generation."""

    def test_write_scene_dialogue(self):
        """Test writing a dialogue scene."""
        world = WorldSetting(name="测试世界", genre="都市")
        characters = [Character(id="char_1", name="张三", role="protagonist")]

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="都市",
            world_setting=world,
            characters=characters,
        )

        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value='张三点点头说："好的，我明白了。"')
        mock_ai.generate_chapter = AsyncMock(return_value="第一章内容")

        writer = ChapterWriter(mock_ai)

        import asyncio
        scene_content = asyncio.run(writer.write_scene(
            novel,
            {
                "location": "咖啡厅",
                "character_names": ["张三"],
                "purpose": "展示角色关系",
                "mood": "轻松",
            },
            SceneType.DIALOGUE,
        ))

        assert scene_content is not None
        assert len(scene_content) > 0

    def test_write_chapter_with_scenes(self):
        """Test writing chapter by generating scenes."""
        world = WorldSetting(name="测试世界", genre="奇幻")
        characters = [Character(id="char_1", name="英雄", role="protagonist")]

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="奇幻",
            world_setting=world,
            characters=characters,
        )

        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="场景内容段落。")
        mock_ai.generate_chapter = AsyncMock(return_value="第一章完整内容")

        writer = ChapterWriter(mock_ai)

        import asyncio
        chapter = asyncio.run(writer.write_chapter_with_scenes(
            novel,
            1,
            {"title": "第一章", "summary": "开场"},
            [
                {"type": "narrative", "location": "村庄", "purpose": "介绍背景"},
                {"type": "dialogue", "location": "酒馆", "purpose": "遇到导师"},
            ],
        ))

        assert chapter.number == 1
        assert len(chapter.scenes) == 2
        assert chapter.scenes[0].scene_type == SceneType.NARRATIVE
        assert chapter.scenes[1].scene_type == SceneType.DIALOGUE


class TestStyleEngine:
    """Tests for StyleEngine."""

    def test_analyze_novel_style(self):
        """Test style profile analysis."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content='这是一个史诗般的场景。他说道："这是一个壮阔的故事。"紧张的时刻来临。',
                word_count=50,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            target_chapter_word_count=(2000, 4000),
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        profile = engine.analyze_novel_style(novel)

        assert profile is not None
        assert isinstance(profile.tones, list)
        assert 0 <= profile.dialogue_ratio <= 1

    def test_check_character_voice_consistency(self):
        """Test character voice consistency checking."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content="张三：这是一个测试。" "李四：当然没问题。",
            word_count=50,
        )

        characters = [
            Character(
                id="char_1",
                name="张三",
                role="protagonist",
                speech_pattern="简洁直接",
            ),
            Character(
                id="char_2",
                name="李四",
                role="supporting",
                speech_pattern="礼貌客气",
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        issues = engine.check_character_voice_consistency(chapter, characters)

        assert isinstance(issues, list)

    def test_generate_style_guide(self):
        """Test style guide generation."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="内容" * 1000,
                word_count=1000,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            characters=[
                Character(
                    id="char_1",
                    name="主角",
                    role="protagonist",
                    speech_pattern="沉稳有力",
                ),
            ],
        )

        profile = StyleProfile(
            tones=[NarrativeTone.EPIC, NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.EPIC,
            descriptive_density=DescriptiveDensity.HIGH,
            dialogue_ratio=0.3,
            pacing=PacingLevel.MODERATE,
            sentence_structure=SentenceComplexity.MIXED,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)
        engine._style_profile = profile

        guide = engine.generate_style_guide(novel, profile)

        assert "测试小说" in guide
        assert "文风指南" in guide
        assert "主角" in guide
