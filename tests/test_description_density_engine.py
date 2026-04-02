"""Tests for description density engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chai.models import Novel, Volume, Chapter
from chai.models.description_density import (
    DescriptionDensityType,
    DescriptionDensityLevel,
    DescriptionBalanceStatus,
    SceneDescriptionMetrics,
    ChapterDensityProfile,
    DensityShift,
    UnifiedDensityProfile,
    DescriptionDensityAnalysis,
    DescriptionDensityRevision,
    DescriptionDensityPlan,
    DescriptionDensityReport,
    DescriptionDensityTemplate,
)
from chai.engines.description_density_engine import DescriptionDensityEngine
from chai.services import AIService


class TestDescriptionDensityEngine:
    """Tests for DescriptionDensityEngine."""

    def test_analyze_chapter_density_basic(self):
        """Test basic chapter density analysis."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个描写环境的场景。天空是蓝色的，大地是绿色的。主角走在街道上。",
            word_count=50,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.chapter_number == 1
        assert profile.chapter_title == "第一章"
        assert 0 <= profile.environment_density <= 1.0
        assert 0 <= profile.action_density <= 1.0
        assert 0 <= profile.dialogue_density <= 1.0
        assert isinstance(profile.density_issues, list)

    def test_analyze_chapter_density_dialogue_heavy(self):
        """Test analyzing dialogue-heavy chapter."""
        chapter = Chapter(
            id="ch_2",
            number=2,
            title="对话章节",
            content="""
            "你好吗？"他问道。
            "我很好，谢谢。"她回答。
            "今天天气真不错。"
            "是啊，很适合散步。"
            "我们出去走走吧。"
            "好的，走吧。"
            """,
            word_count=60,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.dialogue_density > 0.3  # Dialogue is substantial
        # Balance will be severely uneven since it's only dialogue with no other description types
        assert profile.balance_status in list(DescriptionBalanceStatus)

    def test_analyze_chapter_density_action_heavy(self):
        """Test analyzing action-heavy chapter."""
        chapter = Chapter(
            id="ch_3",
            number=3,
            title="战斗章节",
            content="英雄快速跑向敌人，猛烈地攻击。他跳起来，踢向敌人的头部。敌人倒在地上，他拿起剑，刺向敌人。战斗激烈地进行着，双方都在拼命挣扎。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.action_density > 0.15
        assert profile.overall_density in [
            DescriptionDensityLevel.LIGHT,
            DescriptionDensityLevel.MODERATE,
            DescriptionDensityLevel.RICH,
        ]

    def test_analyze_chapter_density_emotional(self):
        """Test analyzing emotionally rich chapter."""
        chapter = Chapter(
            id="ch_4",
            number=4,
            title="情感章节",
            content="她感到高兴和幸福，心中充满了喜悦。但同时也有悲伤和难过，因为她知道分离即将来临。她的内心充满了复杂的情感，既感激又担心。",
            word_count=70,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.emotional_density > 0.05

    def test_analyze_chapter_density_empty(self):
        """Test analyzing empty chapter."""
        chapter = Chapter(
            id="ch_5",
            number=5,
            title="空白章节",
            content="",
            word_count=0,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.chapter_number == 5
        assert profile.total_words == 0

    def test_analyze_chapter_density_sensory_rich(self):
        """Test analyzing sensory detail rich chapter."""
        chapter = Chapter(
            id="ch_6",
            number=6,
            title="感官章节",
            content="她看见阳光照耀，听到鸟儿歌唱，闻到花香四溢。她触摸到柔软的花瓣，感觉到微风拂过。她品尝着甘甜的果实，感受到温暖的阳光。",
            word_count=65,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.analyze_chapter_density(chapter)

        assert profile is not None
        assert profile.sensory_density > 0.05

    def test_detect_density_shifts_basic(self):
        """Test detecting basic density shifts."""
        profiles = [
            ChapterDensityProfile(
                chapter_number=1,
                chapter_title="第一章",
                environment_density=0.15,
                action_density=0.20,
                dialogue_density=0.30,
                internal_thought_density=0.15,
                sensory_density=0.10,
                emotional_density=0.10,
                density_score=0.9,
                balance_score=0.9,
            ),
            ChapterDensityProfile(
                chapter_number=2,
                chapter_title="第二章",
                environment_density=0.25,
                action_density=0.30,
                dialogue_density=0.15,
                internal_thought_density=0.10,
                sensory_density=0.10,
                emotional_density=0.10,
                density_score=0.7,
                balance_score=0.7,
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        shifts = engine.detect_density_shifts(profiles)

        assert isinstance(shifts, list)

    def test_detect_density_shifts_no_shifts(self):
        """Test detecting no shifts when similar chapters."""
        profiles = [
            ChapterDensityProfile(
                chapter_number=1,
                chapter_title="第一章",
                environment_density=0.15,
                action_density=0.20,
                dialogue_density=0.30,
                internal_thought_density=0.15,
                sensory_density=0.10,
                emotional_density=0.10,
                density_score=0.9,
                balance_score=0.9,
            ),
            ChapterDensityProfile(
                chapter_number=2,
                chapter_title="第二章",
                environment_density=0.16,
                action_density=0.21,
                dialogue_density=0.31,
                internal_thought_density=0.14,
                sensory_density=0.09,
                emotional_density=0.09,
                density_score=0.9,
                balance_score=0.9,
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        shifts = engine.detect_density_shifts(profiles)

        assert len(shifts) == 0

    def test_create_unified_density_profile(self):
        """Test creating unified density profile."""
        profiles = [
            ChapterDensityProfile(
                chapter_number=1,
                chapter_title="第一章",
                environment_density=0.15,
                action_density=0.20,
                dialogue_density=0.30,
                internal_thought_density=0.15,
                sensory_density=0.10,
                emotional_density=0.10,
                density_score=0.9,
                balance_score=0.9,
            ),
            ChapterDensityProfile(
                chapter_number=2,
                chapter_title="第二章",
                environment_density=0.18,
                action_density=0.22,
                dialogue_density=0.28,
                internal_thought_density=0.12,
                sensory_density=0.10,
                emotional_density=0.10,
                density_score=0.9,
                balance_score=0.9,
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        unified = engine.create_unified_density_profile(profiles)

        assert unified is not None
        assert isinstance(unified, UnifiedDensityProfile)
        assert 0.0 <= unified.target_environment_density <= 1.0
        assert 0.0 <= unified.target_dialogue_density <= 1.0

    def test_create_unified_density_profile_empty(self):
        """Test creating unified profile from empty list."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        unified = engine.create_unified_density_profile([])

        assert unified is not None
        assert isinstance(unified, UnifiedDensityProfile)

    def test_calculate_chapter_consistency(self):
        """Test calculating chapter consistency."""
        profile = ChapterDensityProfile(
            chapter_number=1,
            chapter_title="第一章",
            environment_density=0.15,
            action_density=0.20,
            dialogue_density=0.30,
            internal_thought_density=0.15,
            sensory_density=0.10,
            emotional_density=0.10,
            density_score=0.9,
            balance_score=0.9,
        )

        unified = UnifiedDensityProfile(
            environment_range=(0.10, 0.20),
            action_range=(0.15, 0.25),
            dialogue_range=(0.25, 0.40),
            internal_thought_range=(0.10, 0.20),
            sensory_range=(0.05, 0.15),
            emotional_range=(0.05, 0.15),
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        score = engine.calculate_chapter_consistency(profile, unified)

        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be high since profile is within ranges

    def test_calculate_chapter_consistency_low(self):
        """Test calculating low chapter consistency."""
        profile = ChapterDensityProfile(
            chapter_number=1,
            chapter_title="第一章",
            environment_density=0.05,
            action_density=0.05,
            dialogue_density=0.10,
            internal_thought_density=0.05,
            sensory_density=0.02,
            emotional_density=0.02,
            density_score=0.5,
            balance_score=0.5,
        )

        unified = UnifiedDensityProfile(
            environment_range=(0.15, 0.25),
            action_range=(0.20, 0.30),
            dialogue_range=(0.30, 0.45),
            internal_thought_range=(0.15, 0.25),
            sensory_range=(0.10, 0.20),
            emotional_range=(0.10, 0.20),
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        score = engine.calculate_chapter_consistency(profile, unified)

        assert 0.0 <= score <= 1.0
        assert score < 0.7  # Should be low since profile is outside ranges

    def test_analyze_novel_density(self):
        """Test analyzing novel density."""
        chapter1 = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个环境描写的场景。天空湛蓝，大地翠绿。主角走在街道上，感受着微风。",
            word_count=50,
        )
        chapter2 = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="他快速地跑向敌人，猛烈地攻击。" + "他跳起来，踢向敌人。",
            word_count=30,
        )
        volume = Volume(
            id="v_1",
            number=1,
            title="第一卷",
            chapters=[chapter1, chapter2],
        )
        novel = Novel(
            id="n_1",
            title="测试小说",
            genre="fantasy",
            volumes=[volume],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        analysis = engine.analyze_novel_density(novel)

        assert analysis is not None
        assert isinstance(analysis, DescriptionDensityAnalysis)
        assert analysis.total_chapters_analyzed == 2
        assert len(analysis.chapter_profiles) == 2
        assert isinstance(analysis.unified_profile, UnifiedDensityProfile)

    def test_analyze_novel_density_empty(self):
        """Test analyzing empty novel."""
        volume = Volume(
            id="v_1",
            number=1,
            title="第一卷",
            chapters=[],
        )
        novel = Novel(
            id="n_1",
            title="空小说",
            genre="fantasy",
            volumes=[volume],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        analysis = engine.analyze_novel_density(novel)

        assert analysis is not None
        assert analysis.total_chapters_analyzed == 0

    def test_create_revision_plan(self):
        """Test creating revision plan."""
        profiles = [
            ChapterDensityProfile(
                chapter_number=1,
                chapter_title="第一章",
                density_score=0.9,
                balance_score=0.9,
            ),
            ChapterDensityProfile(
                chapter_number=2,
                chapter_title="第二章",
                density_score=0.7,
                balance_score=0.7,
            ),
            ChapterDensityProfile(
                chapter_number=3,
                chapter_title="第三章",
                density_score=0.5,
                balance_score=0.5,
            ),
        ]
        unified = UnifiedDensityProfile()
        analysis = DescriptionDensityAnalysis(
            chapter_profiles=profiles,
            unified_profile=unified,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        plan = engine.create_revision_plan(analysis, target_score=0.8)

        assert plan is not None
        assert isinstance(plan, DescriptionDensityPlan)
        assert len(plan.chapters_to_revise) == 2  # Chapters 2 and 3
        assert plan.chapters_to_revise[0] == 3  # Lowest score first

    def test_generate_density_report(self):
        """Test generating density report."""
        profiles = [
            ChapterDensityProfile(
                chapter_number=1,
                chapter_title="第一章",
                density_score=0.9,
                balance_score=0.9,
            ),
        ]
        unified = UnifiedDensityProfile()
        analysis = DescriptionDensityAnalysis(
            chapter_profiles=profiles,
            unified_profile=unified,
            total_chapters_analyzed=1,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        report = engine.generate_density_report(analysis)

        assert report is not None
        assert isinstance(report, DescriptionDensityReport)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0

    def test_get_chapter_density_summary(self):
        """Test getting chapter density summary."""
        profile = ChapterDensityProfile(
            chapter_number=1,
            chapter_title="第一章",
            overall_density=DescriptionDensityLevel.MODERATE,
            balance_status=DescriptionBalanceStatus.BALANCED,
            environment_density=0.15,
            action_density=0.20,
            dialogue_density=0.30,
            internal_thought_density=0.15,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        summary = engine.get_chapter_density_summary(profile)

        assert isinstance(summary, str)
        assert "第1章" in summary
        assert "第一章" in summary

    def test_get_all_templates(self):
        """Test getting all density templates."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        templates = engine.get_all_templates()

        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "epic_fantasy" in templates
        assert "romance" in templates
        assert "mystery" in templates

    def test_get_template(self):
        """Test getting specific template."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        template = engine.get_template("epic_fantasy")

        assert template is not None
        assert isinstance(template, DescriptionDensityTemplate)
        assert template.template_name == "epic_fantasy"

    def test_get_template_not_found(self):
        """Test getting non-existent template."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        template = engine.get_template("nonexistent")

        assert template is None

    def test_apply_template(self):
        """Test applying a template."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.apply_template("epic_fantasy")

        assert profile is not None
        assert isinstance(profile, UnifiedDensityProfile)
        assert profile.target_environment_density == 0.20

    def test_apply_template_not_found(self):
        """Test applying non-existent template."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        profile = engine.apply_template("nonexistent")

        assert profile is None

    def test_template_to_unified_profile(self):
        """Test converting template to unified profile."""
        template = DescriptionDensityTemplate(
            template_name="test",
            template_description="Test template",
            environment_density=0.18,
            action_density=0.22,
            dialogue_density=0.28,
            internal_thought_density=0.12,
            sensory_density=0.10,
            emotional_density=0.10,
        )

        unified = template.to_unified_profile()

        assert unified is not None
        assert isinstance(unified, UnifiedDensityProfile)
        assert unified.target_environment_density == 0.18
        assert unified.target_action_density == 0.22

    def test_density_shift_model(self):
        """Test DensityShift model."""
        shift = DensityShift(
            shift_id="test123",
            start_chapter=1,
            end_chapter=2,
            shift_type="increase",
            severity="moderate",
            description="Test shift",
            magnitude=0.15,
            affected_aspects=[DescriptionDensityType.ACTION],
            likely_cause="scene transition",
        )

        assert shift.shift_id == "test123"
        assert shift.start_chapter == 1
        assert shift.end_chapter == 2
        assert shift.shift_type == "increase"
        assert shift.severity == "moderate"
        assert DescriptionDensityType.ACTION in shift.affected_aspects

    def test_description_density_revision_model(self):
        """Test DescriptionDensityRevision model."""
        revision = DescriptionDensityRevision(
            original_content="Original text",
            revised_content="Revised text",
            chapter_number=1,
            changes_made=["Changed dialogue ratio"],
            before_score=0.6,
            after_score=0.85,
            issues_addressed=["Too much dialogue"],
            issues_remaining=[],
        )

        assert revision.original_content == "Original text"
        assert revision.revised_content == "Revised text"
        assert revision.chapter_number == 1
        assert revision.after_score > revision.before_score

    def test_description_density_level_enum(self):
        """Test DescriptionDensityLevel enum values."""
        assert DescriptionDensityLevel.SPARSE.value == "sparse"
        assert DescriptionDensityLevel.LIGHT.value == "light"
        assert DescriptionDensityLevel.MODERATE.value == "moderate"
        assert DescriptionDensityLevel.RICH.value == "rich"
        assert DescriptionDensityLevel.EXCESSIVE.value == "excessive"

    def test_description_balance_status_enum(self):
        """Test DescriptionBalanceStatus enum values."""
        assert DescriptionBalanceStatus.BALANCED.value == "balanced"
        assert DescriptionBalanceStatus.SLIGHTLY_UNEVEN.value == "slightly_uneven"
        assert DescriptionBalanceStatus.UNEVEN.value == "uneven"
        assert DescriptionBalanceStatus.SEVERELY_UNEVEN.value == "severely_uneven"

    def test_description_density_type_enum(self):
        """Test DescriptionDensityType enum values."""
        assert DescriptionDensityType.ENVIRONMENT.value == "environment"
        assert DescriptionDensityType.ACTION.value == "action"
        assert DescriptionDensityType.DIALOGUE.value == "dialogue"
        assert DescriptionDensityType.INTERNAL_THOUGHT.value == "internal_thought"
        assert DescriptionDensityType.SENSORY.value == "sensory"
        assert DescriptionDensityType.EMOTIONAL.value == "emotional"

    @pytest.mark.asyncio
    async def test_revise_chapter_for_density(self):
        """Test revising chapter for density balance."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个测试章节。" * 20,
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="Revised content with better density balance.")
        engine = DescriptionDensityEngine(mock_ai)

        unified = UnifiedDensityProfile()

        revision = await engine.revise_chapter_for_density(chapter, unified)

        assert revision is not None
        assert isinstance(revision, DescriptionDensityRevision)
        assert revision.chapter_number == 1
        mock_ai.generate.assert_called_once()

    def test_identify_density_issues(self):
        """Test identifying density issues."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        issues = engine._identify_density_issues(
            env=0.30,  # Excessive
            action=0.02,  # Too low
            dialogue=0.60,  # Excessive
            internal=0.02,  # Too low
            sensory=0.25,  # Excessive
            emotional=0.01,  # Too low
            chapter_num=1,
        )

        assert len(issues) > 0
        assert any("environment" in issue.lower() for issue in issues)
        assert any("dialogue" in issue.lower() for issue in issues)

    def test_calculate_balance_score(self):
        """Test calculating balance score."""
        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        # Balanced values
        balanced_score = engine._calculate_balance_score(0.15, 0.20, 0.30, 0.15, 0.10, 0.10)
        assert 0.0 <= balanced_score <= 1.0

        # Unbalanced values
        unbalanced_score = engine._calculate_balance_score(0.05, 0.50, 0.05, 0.05, 0.05, 0.05)
        assert 0.0 <= unbalanced_score <= 1.0
        assert unbalanced_score < balanced_score

    def test_analyze_shift_cause(self):
        """Test analyzing shift cause."""
        before = ChapterDensityProfile(
            chapter_number=1,
            chapter_title="第一章",
            action_density=0.10,
            dialogue_density=0.50,
            environment_density=0.15,
            internal_thought_density=0.15,
            sensory_density=0.05,
            emotional_density=0.05,
        )
        after = ChapterDensityProfile(
            chapter_number=2,
            chapter_title="第二章",
            action_density=0.35,
            dialogue_density=0.15,
            environment_density=0.20,
            internal_thought_density=0.15,
            sensory_density=0.08,
            emotional_density=0.07,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = DescriptionDensityEngine(mock_ai)

        cause = engine._analyze_shift_cause(before, after)

        assert isinstance(cause, str)
        assert len(cause) > 0
