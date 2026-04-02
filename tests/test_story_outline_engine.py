"""Tests for StoryOutlineEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.story_outline import (
    StoryOutline,
    StoryOutlineType,
    OutlineStatus,
    VolumeOutline,
    ChapterOutline,
    SceneOutline,
    PlotThread,
    ForeshadowingElement,
    ForeshadowingType,
    ForeshadowingStatus,
    PlotThreadType,
    TensionLevel,
    ScenePurpose,
    StoryOutlineAnalysis,
)
from chai.engines.story_outline_engine import StoryOutlineEngine
from chai.services import AIService


class TestStoryOutlineModels:
    """Tests for story outline models."""

    def test_story_outline_type_enum(self):
        """Test StoryOutlineType enum values."""
        assert StoryOutlineType.THREE_ACT.value == "three_act"
        assert StoryOutlineType.HEROS_JOURNEY.value == "heros_journey"
        assert StoryOutlineType.SEVEN_POINT.value == "seven_point"
        assert StoryOutlineType.SAVE_THE_CAT.value == "save_the_cat"
        assert StoryOutlineType.FREYTAGS_PYRAMID.value == "freytags_pyramid"
        assert StoryOutlineType.KISHOTENKETSU.value == "kishotenketsu"

    def test_outline_status_enum(self):
        """Test OutlineStatus enum values."""
        assert OutlineStatus.PENDING.value == "pending"
        assert OutlineStatus.IN_PROGRESS.value == "in_progress"
        assert OutlineStatus.COMPLETE.value == "complete"
        assert OutlineStatus.REVISED.value == "revised"

    def test_tension_level_enum(self):
        """Test TensionLevel enum values."""
        assert TensionLevel.LOW.value == "low"
        assert TensionLevel.MODERATE.value == "moderate"
        assert TensionLevel.HIGH.value == "high"
        assert TensionLevel.CLIMAX.value == "climax"
        assert TensionLevel.RELEASE.value == "release"

    def test_foreshadowing_type_enum(self):
        """Test ForeshadowingType enum values."""
        assert ForeshadowingType.DIRECT.value == "direct"
        assert ForeshadowingType.INDIRECT.value == "indirect"
        assert ForeshadowingType.CHARACTER_BASED.value == "character_based"
        assert ForeshadowingType.ENVIRONMENTAL.value == "environmental"
        assert ForeshadowingType.DIALOGUE.value == "dialogue"
        assert ForeshadowingType.SYMBOLIC.value == "symbolic"

    def test_foreshadowing_status_enum(self):
        """Test ForeshadowingStatus enum values."""
        assert ForeshadowingStatus.PLANTED.value == "planted"
        assert ForeshadowingStatus.DEVELOPING.value == "developing"
        assert ForeshadowingStatus.PAYED_OFF.value == "payed_off"
        assert ForeshadowingStatus.REPURPOSED.value == "repurposed"

    def test_plot_thread_type_enum(self):
        """Test PlotThreadType enum values."""
        assert PlotThreadType.MAIN.value == "main"
        assert PlotThreadType.ROMANTIC.value == "romantic"
        assert PlotThreadType.CHARACTER.value == "character"
        assert PlotThreadType.SUBPLOT.value == "subplot"
        assert PlotThreadType.WORLD_BUILDING.value == "world_building"
        assert PlotThreadType.MYSTERY.value == "mystery"

    def test_scene_purpose_enum(self):
        """Test ScenePurpose enum values."""
        assert ScenePurpose.exposition.value == "exposition"
        assert ScenePurpose.rising_action.value == "rising_action"
        assert ScenePurpose.COMPLICATION.value == "complication"
        assert ScenePurpose.CLIMAX.value == "climax"
        assert ScenePurpose.RESOLUTION.value == "resolution"

    def test_volume_outline_model(self):
        """Test VolumeOutline model."""
        volume = VolumeOutline(
            id="vol_1",
            number=1,
            title="第一卷：觉醒",
            chapter_start=1,
            chapter_end=8,
            description="主角觉醒的篇章",
            theme="成长与觉醒",
            central_conflict="内心的挣扎",
            arc_summary="从迷茫到坚定",
            key_events=["事件1", "事件2"],
            status=OutlineStatus.PENDING,
        )
        assert volume.number == 1
        assert volume.chapter_start == 1
        assert volume.chapter_end == 8
        assert volume.status == OutlineStatus.PENDING

    def test_chapter_outline_model(self):
        """Test ChapterOutline model."""
        chapter = ChapterOutline(
            id="ch_1",
            number=1,
            title="第一章",
            summary="故事开始",
            pov_character="张三",
            characters_involved=["张三", "李四"],
            tension_level=TensionLevel.LOW,
            pacing_notes="建立世界观",
            plot_threads_advanced=["thread_main"],
            foreshadowing_planted=["fore_1"],
            foreshadowing_payoffs=[],
            status=OutlineStatus.PENDING,
            target_word_count=3000,
        )
        assert chapter.number == 1
        assert chapter.tension_level == TensionLevel.LOW
        assert "张三" in chapter.characters_involved

    def test_scene_outline_model(self):
        """Test SceneOutline model."""
        scene = SceneOutline(
            id="scene_1",
            number=1,
            chapter_id="ch_1",
            location="城镇广场",
            time_period="白天",
            setting_description="热闹的集市",
            characters=["张三", "李四"],
            pov_character="张三",
            scene_purpose=ScenePurpose.exposition,
            purpose_description="介绍世界观",
            scene_summary="主角出现在集市",
            key_dialogues=["对话1", "对话2"],
            character_actions=["动作1", "动作2"],
            mood="轻松",
            emotional_beat="好奇",
            plot_threads_advanced=["thread_main"],
            foreshadowing_planted=[],
            tension_level=TensionLevel.LOW,
            duration_words=1000,
        )
        assert scene.number == 1
        assert scene.location == "城镇广场"
        assert scene.scene_purpose == ScenePurpose.exposition

    def test_plot_thread_model(self):
        """Test PlotThread model."""
        thread = PlotThread(
            id="thread_1",
            name="主线剧情",
            thread_type=PlotThreadType.MAIN,
            description="主角的冒险之旅",
            chapters_active=[1, 2, 3, 4, 5],
            status=OutlineStatus.PENDING,
            current_state="初始状态",
            key_events=["事件1", "事件2"],
        )
        assert thread.name == "主线剧情"
        assert thread.thread_type == PlotThreadType.MAIN
        assert len(thread.chapters_active) == 5

    def test_foreshadowing_element_model(self):
        """Test ForeshadowingElement model."""
        foreshadowing = ForeshadowingElement(
            id="fore_1",
            element="神秘符号",
            foreshadowing_type=ForeshadowingType.SYMBOLIC,
            chapter_planted=3,
            scene_location="墙壁上",
            description="墙上出现的神秘符号",
            chapter_payoff=18,
            payoff_description="符号的含义揭晓",
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=0.7,
        )
        assert foreshadowing.element == "神秘符号"
        assert foreshadowing.chapter_planted == 3
        assert foreshadowing.chapter_payoff == 18
        assert foreshadowing.subtlety_level == 0.7

    def test_story_outline_model(self):
        """Test StoryOutline model."""
        volume = VolumeOutline(
            id="vol_1",
            number=1,
            title="第一卷",
            chapter_start=1,
            chapter_end=8,
            description="测试卷描述",
        )
        chapter = ChapterOutline(
            id="ch_1",
            number=1,
            title="第一章",
            summary="故事开始",
        )
        scene = SceneOutline(
            id="scene_1",
            number=1,
            chapter_id="ch_1",
            location="城镇",
        )
        thread = PlotThread(
            id="thread_1",
            name="主线",
            thread_type=PlotThreadType.MAIN,
            description="主线剧情",
            chapters_active=[1, 2, 3],
        )
        foreshadowing = ForeshadowingElement(
            id="fore_1",
            element="符号",
            foreshadowing_type=ForeshadowingType.SYMBOLIC,
            chapter_planted=1,
        )

        outline = StoryOutline(
            id="outline_1",
            title="我的小说",
            genre="奇幻",
            theme="成长",
            outline_type=StoryOutlineType.THREE_ACT,
            target_word_count=80000,
            target_chapter_count=24,
            volumes=[volume],
            chapters=[chapter],
            scenes=[scene],
            plot_threads=[thread],
            foreshadowing_elements=[foreshadowing],
            main_character_ids=["char_1"],
            supporting_character_ids=["char_2"],
            antagonist_ids=["char_3"],
            status=OutlineStatus.PENDING,
        )
        assert outline.title == "我的小说"
        assert outline.genre == "奇幻"
        assert len(outline.volumes) == 1
        assert len(outline.chapters) == 1
        assert len(outline.plot_threads) == 1

    def test_story_outline_analysis_model(self):
        """Test StoryOutlineAnalysis model."""
        analysis = StoryOutlineAnalysis(
            outline_id="outline_1",
            pacing_analysis={"has_climax": True},
            tension_curve=[{"chapter": 1, "tension": "low"}],
            thread_coverage={"total_threads": 3},
            unresolved_threads=[],
            foreshadowing_balance={"total_planted": 5, "total_paid_off": 3},
            orphaned_foreshadowing=[],
            character_screen_time={"char_1": 10, "char_2": 5},
            protagonist_dominance=0.6,
            timeline_consistency=[],
            plot_holes=[],
            coherence_score=0.85,
            completeness_score=0.9,
        )
        assert analysis.outline_id == "outline_1"
        assert analysis.coherence_score == 0.85
        assert analysis.completeness_score == 0.9


class TestStoryOutlineEngine:
    """Tests for StoryOutlineEngine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock(spec=AIService)
        service.generate = AsyncMock(return_value='{"title": "测试小说", "logline": "一句话故事", "synopsis": "故事梗概", "main_conflict": "核心冲突", "thematic_statements": ["主题1"], "plot_threads": [{"name": "主线", "type": "main", "description": "主线剧情", "key_events": ["事件1"]}], "foreshadowing_plan": [{"element": "伏笔1", "type": "indirect", "plant_chapter": 3, "payoff_chapter": 18, "description": "伏笔描述"}], "chapter_summaries": [], "volume_splits": [{"volume": 1, "start_chapter": 1, "end_chapter": 8, "theme": "第一卷主题"}], "character_arc_milestones": {}}')
        service._parse_json = lambda r: {
            "title": "测试小说",
            "logline": "一句话故事",
            "synopsis": "故事梗概",
            "main_conflict": "核心冲突",
            "thematic_statements": ["主题1"],
            "plot_threads": [{"name": "主线", "type": "main", "description": "主线剧情", "key_events": ["事件1"]}],
            "foreshadowing_plan": [{"element": "伏笔1", "type": "indirect", "plant_chapter": 3, "payoff_chapter": 18, "description": "伏笔描述"}],
            "chapter_summaries": [],
            "volume_splits": [{"volume": 1, "start_chapter": 1, "end_chapter": 8, "theme": "第一卷主题"}],
            "character_arc_milestones": {},
        }
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create a StoryOutlineEngine instance."""
        return StoryOutlineEngine(mock_ai_service)

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert hasattr(engine, "ai_service")

    def test_get_outline_summary(self, engine):
        """Test getting outline summary."""
        volume = VolumeOutline(
            id="vol_1",
            number=1,
            title="第一卷",
            chapter_start=1,
            chapter_end=8,
            description="测试卷",
        )
        chapter = ChapterOutline(
            id="ch_1",
            number=1,
            title="第一章",
            summary="测试章节内容摘要文字",
        )
        thread = PlotThread(
            id="thread_1",
            name="主线剧情",
            thread_type=PlotThreadType.MAIN,
            description="测试主线描述",
            chapters_active=[1, 2, 3],
        )
        foreshadowing = ForeshadowingElement(
            id="fore_1",
            element="伏笔",
            foreshadowing_type=ForeshadowingType.SYMBOLIC,
            chapter_planted=1,
            status=ForeshadowingStatus.PLANTED,
        )
        outline = StoryOutline(
            id="outline_1",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            volumes=[volume],
            chapters=[chapter],
            scenes=[],
            plot_threads=[thread],
            foreshadowing_elements=[foreshadowing],
            status=OutlineStatus.COMPLETE,
        )

        summary = engine.get_outline_summary(outline)

        assert "测试小说" in summary
        assert "奇幻" in summary
        assert "成长" in summary
        assert "第一卷" in summary
        assert "第一章" in summary
        assert "主线剧情" in summary
        assert "伏笔" in summary

    def test_export_outline(self, engine):
        """Test exporting outline to dict."""
        volume = VolumeOutline(
            id="vol_1",
            number=1,
            title="第一卷",
            chapter_start=1,
            chapter_end=8,
            description="测试卷",
        )
        chapter = ChapterOutline(
            id="ch_1",
            number=1,
            title="第一章",
            summary="测试章节",
            tension_level=TensionLevel.LOW,
            characters_involved=["char_1"],
        )
        outline = StoryOutline(
            id="outline_1",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            outline_type=StoryOutlineType.THREE_ACT,
            target_word_count=80000,
            target_chapter_count=24,
            volumes=[volume],
            chapters=[chapter],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.COMPLETE,
        )

        exported = engine.export_outline(outline)

        assert exported["id"] == "outline_1"
        assert exported["title"] == "测试小说"
        assert exported["genre"] == "奇幻"
        assert len(exported["volumes"]) == 1
        assert len(exported["chapters"]) == 1

    def test_add_subplot(self, engine):
        """Test adding a subplot to outline."""
        outline = StoryOutline(
            id="outline_1",
            title="测试",
            genre="奇幻",
            theme="成长",
            chapters=[
                ChapterOutline(
                    id="ch_1",
                    number=1,
                    title="第一章",
                    summary="测试",
                    plot_threads_advanced=[],
                ),
                ChapterOutline(
                    id="ch_5",
                    number=5,
                    title="第五章",
                    summary="测试",
                    plot_threads_advanced=[],
                ),
            ],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
        )

        updated = engine.add_subplot(
            outline=outline,
            subplot_name="感情线",
            subplot_type=PlotThreadType.ROMANTIC,
            involved_characters=["char_1", "char_2"],
            start_chapter=3,
            end_chapter=10,
            key_events=["相遇", "发展"],
        )

        assert len(updated.plot_threads) == 1
        assert updated.plot_threads[0].name == "感情线"
        assert updated.plot_threads[0].thread_type == PlotThreadType.ROMANTIC
        assert 3 in updated.plot_threads[0].chapters_active

    def test_plant_foreshadowing(self, engine):
        """Test planting foreshadowing in outline."""
        outline = StoryOutline(
            id="outline_1",
            title="测试",
            genre="奇幻",
            theme="成长",
            chapters=[
                ChapterOutline(
                    id="ch_3",
                    number=3,
                    title="第三章",
                    summary="测试",
                    foreshadowing_planted=[],
                    foreshadowing_payoffs=[],
                ),
                ChapterOutline(
                    id="ch_18",
                    number=18,
                    title="第十八章",
                    summary="测试",
                    foreshadowing_planted=[],
                    foreshadowing_payoffs=[],
                ),
            ],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
        )

        updated = engine.plant_foreshadowing(
            outline=outline,
            element="神秘符号",
            foreshadowing_type=ForeshadowingType.SYMBOLIC,
            plant_chapter=3,
            plant_location="墙上",
            payoff_chapter=18,
            payoff_description="符号的含义揭晓",
            subtlety_level=0.8,
        )

        assert len(updated.foreshadowing_elements) == 1
        assert updated.foreshadowing_elements[0].element == "神秘符号"
        assert updated.foreshadowing_elements[0].chapter_planted == 3
        assert updated.foreshadowing_elements[0].chapter_payoff == 18


class TestStoryOutlineTensionProgression:
    """Tests for tension progression checking."""

    def test_check_tension_progression_valid(self):
        """Test valid tension progression."""
        engine = StoryOutlineEngine(MagicMock())
        tensions = [
            TensionLevel.LOW,
            TensionLevel.MODERATE,
            TensionLevel.MODERATE,
            TensionLevel.HIGH,
            TensionLevel.HIGH,
            TensionLevel.CLIMAX,
        ]
        # Climax at index 5 of 6 chapters (83%) - valid
        result = engine._check_tension_progression(tensions)
        assert result is True

    def test_check_tension_progression_climax_too_early(self):
        """Test climax too early in story."""
        engine = StoryOutlineEngine(MagicMock())
        tensions = [
            TensionLevel.LOW,
            TensionLevel.MODERATE,
            TensionLevel.CLIMAX,
            TensionLevel.MODERATE,
            TensionLevel.LOW,
            TensionLevel.RELEASE,
        ]
        # Climax at index 2 of 6 (33%) - too early
        result = engine._check_tension_progression(tensions)
        assert result is False

    def test_check_tension_progression_no_variation(self):
        """Test no tension variation."""
        engine = StoryOutlineEngine(MagicMock())
        tensions = [
            TensionLevel.MODERATE,
            TensionLevel.MODERATE,
            TensionLevel.MODERATE,
            TensionLevel.MODERATE,
        ]
        # No tension variation
        result = engine._check_tension_progression(tensions)
        assert result is False


class TestStoryOutlineCoherence:
    """Tests for coherence calculation."""

    def test_calculate_coherence_with_issues(self):
        """Test coherence calculation with issues."""
        engine = StoryOutlineEngine(MagicMock())
        outline = StoryOutline(
            id="outline_1",
            title="测试",
            genre="奇幻",
            theme="成长",
            volumes=[],
            chapters=[],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
        )
        analysis = StoryOutlineAnalysis(
            outline_id="outline_1",
            unresolved_threads=["t1", "t2"],
            orphaned_foreshadowing=["f1"],
            timeline_consistency=["问题1"],
            coherence_score=0.0,
            completeness_score=0.0,
        )

        score = engine._calculate_coherence(outline, analysis)
        # Base 1.0 - 0.1*2 (unresolved) - 0.1*1 (orphaned) - 0.1*1 (timeline)
        # = 1.0 - 0.2 - 0.1 - 0.1 = 0.6
        assert score == pytest.approx(0.6, abs=0.001)

    def test_calculate_coherence_clean(self):
        """Test coherence calculation with no issues."""
        engine = StoryOutlineEngine(MagicMock())
        outline = StoryOutline(
            id="outline_1",
            title="测试",
            genre="奇幻",
            theme="成长",
            volumes=[],
            chapters=[],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
        )
        analysis = StoryOutlineAnalysis(
            outline_id="outline_1",
            unresolved_threads=[],
            orphaned_foreshadowing=[],
            timeline_consistency=[],
            coherence_score=0.0,
            completeness_score=0.0,
        )

        score = engine._calculate_coherence(outline, analysis)
        assert score == 1.0


class TestStoryOutlineCompleteness:
    """Tests for completeness calculation."""

    def test_calculate_completeness_full(self):
        """Test completeness with full outline."""
        engine = StoryOutlineEngine(MagicMock())
        outline = StoryOutline(
            id="outline_1",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            volumes=[
                VolumeOutline(id="v1", number=1, title="第一卷", chapter_start=1, chapter_end=8, description="第一卷描述")
            ],
            chapters=[
                ChapterOutline(id="c1", number=1, title="第一章", summary="测试", scene_summaries=["s1", "s2", "s3"]),
                ChapterOutline(id="c2", number=2, title="第二章", summary="测试", scene_summaries=["s4", "s5", "s6"]),
            ],
            scenes=[
                SceneOutline(id="s1", number=1, chapter_id="c1", location=""),
                SceneOutline(id="s2", number=2, chapter_id="c1", location=""),
                SceneOutline(id="s3", number=3, chapter_id="c1", location=""),
                SceneOutline(id="s4", number=1, chapter_id="c2", location=""),
            ],
            plot_threads=[
                PlotThread(id="t1", name="主线", thread_type=PlotThreadType.MAIN, description="", chapters_active=[1, 2]),
                PlotThread(id="t2", name="支线", thread_type=PlotThreadType.SUBPLOT, description="", chapters_active=[1]),
            ],
            foreshadowing_elements=[
                ForeshadowingElement(id="f1", element="伏笔1", foreshadowing_type=ForeshadowingType.SYMBOLIC, chapter_planted=1),
                ForeshadowingElement(id="f2", element="伏笔2", foreshadowing_type=ForeshadowingType.SYMBOLIC, chapter_planted=2),
                ForeshadowingElement(id="f3", element="伏笔3", foreshadowing_type=ForeshadowingType.SYMBOLIC, chapter_planted=3),
            ],
            status=OutlineStatus.PENDING,
            target_chapter_count=2,
        )

        score = engine._calculate_completeness(outline)
        # Should have title, chapters, threads, foreshadowing, volumes, scenes
        assert score > 0.8

    def test_calculate_completeness_minimal(self):
        """Test completeness with minimal outline."""
        engine = StoryOutlineEngine(MagicMock())
        outline = StoryOutline(
            id="outline_1",
            title="",
            genre="奇幻",
            theme="成长",
            volumes=[],
            chapters=[],
            scenes=[],
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
        )

        score = engine._calculate_completeness(outline)
        assert score < 0.3
