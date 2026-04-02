"""Tests for PayoffCompletenessEngine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Novel, Chapter
from chai.models.payoff_completeness import (
    PayoffCompletenessType,
    PayoffCompletenessSeverity,
    PayoffSatisfactionLevel,
    PayoffCompletenessIssue,
    PlantedElementPayoff,
    ChapterPayoffProfile,
    PayoffCompletenessAnalysis,
    PayoffCompletenessRevision,
    PayoffCompletenessPlan,
    PayoffCompletenessReport,
)
from chai.engines.payoff_completeness_engine import PayoffCompletenessEngine


class MockAIService:
    """Mock AI service for testing."""
    pass


@pytest.fixture
def ai_service():
    """Create a mock AI service."""
    return MockAIService()


@pytest.fixture
def engine(ai_service):
    """Create a payoff completeness engine."""
    return PayoffCompletenessEngine(ai_service)


@pytest.fixture
def sample_chapters():
    """Create sample chapters with foreshadowing and payoffs."""
    chapters = [
        Chapter(
            id="ch_1",
            number=1,
            title="序章",
            content="这是一个关于命运的故事。古老的预言说，总有一天，英雄会崛起。那把被封印的剑在等待时机。"
        ),
        Chapter(
            id="ch_2",
            number=2,
            title="相遇",
            content="主角李明在森林中遇到了神秘老人。老人说：你身上有不一样的气质。"
        ),
        Chapter(
            id="ch_3",
            number=3,
            title="启程",
            content="李明踏上了旅程。他想起了老人的话，仿佛有什么在召唤他。"
        ),
        Chapter(
            id="ch_10",
            number=10,
            title="觉醒",
            content="原来如此！正如老人预言的那样，李明终于觉醒了力量。那把剑开始回应他的召唤。"
        ),
        Chapter(
            id="ch_20",
            number=20,
            title="决战",
            content="最终决战来临。李明握着那把剑，正如命运所安排的那样，他战胜了黑暗。全部的预言都应验了。"
        ),
    ]
    return chapters


@pytest.fixture
def sample_novel(sample_chapters):
    """Create a sample novel."""
    novel = MagicMock(spec=Novel)
    novel.chapters = {ch.number: ch for ch in sample_chapters}
    return novel


class TestPayoffCompletenessEngine:
    """Tests for PayoffCompletenessEngine."""

    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert engine.ai_service is not None

    def test_detect_plants_in_chapter(self, engine):
        """Test detecting foreshadowing plants in a chapter."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="序章",
            content="这是一个关于命运的故事。古老的预言说，总有一天，英雄会崛起。那把被封印的剑在等待时机。"
        )

        plants = engine._detect_plants_in_chapter(chapter)

        assert len(plants) > 0
        assert any("命运" in p.get("content", "") for p in plants)
        assert any("总有一天" in p.get("content", "") for p in plants)
        assert any("那把" in p.get("content", "") for p in plants)

    def test_detect_payoffs_in_chapter(self, engine):
        """Test detecting payoff moments in a chapter."""
        chapter = Chapter(
            id="ch_10",
            number=10,
            title="觉醒",
            content="原来如此！正如老人预言的那样，李明终于觉醒了力量。那把剑开始回应他的召唤。"
        )

        payoffs = engine._detect_payoffs_in_chapter(chapter)

        assert len(payoffs) > 0
        assert any("原来" in p.get("content", "") or "正如" in p.get("content", "") for p in payoffs)

    def test_detect_strong_payoff_markers(self, engine):
        """Test detecting strong payoff markers."""
        chapter = Chapter(
            id="ch_20",
            number=20,
            title="决战",
            content="最终决战来临。李明握着那把剑，正如命运所安排的那样，他战胜了黑暗。全部的预言都应验了。"
        )

        payoffs = engine._detect_payoffs_in_chapter(chapter)

        # Should have strong payoff markers
        assert len(payoffs) > 0

    def test_check_payoff_completeness_with_payoff(self, engine):
        """Test checking payoff completeness when payoff exists."""
        plant = {
            "id": "fs_1",
            "chapter": 1,
            "content": "古老的预言说，总有一天，英雄会崛起。",
            "context": "这是一个关于命运的故事。",
        }
        payoff = {
            "id": "po_1",
            "chapter": 10,
            "content": "原来如此！正如老人预言的那样，李明终于觉醒了力量。",
        }

        result = engine.check_payoff_completeness(plant, payoff)

        assert result.has_payoff is True
        assert result.payoff_chapter == 10
        assert result.completeness_type in [PayoffCompletenessType.FULL_PAYOFF, PayoffCompletenessType.PARTIAL_PAYOFF]
        assert result.completeness_score >= 0.0
        assert result.satisfaction_level in PayoffSatisfactionLevel

    def test_check_payoff_completeness_without_payoff(self, engine):
        """Test checking payoff completeness when no payoff exists."""
        plant = {
            "id": "fs_1",
            "chapter": 1,
            "content": "神秘的剑在等待时机。",
            "context": "那把被封印的剑在等待时机。",
        }

        result = engine.check_payoff_completeness(plant, None)

        assert result.has_payoff is False
        assert result.completeness_type == PayoffCompletenessType.NO_PAYOFF
        assert result.completeness_score == 0.0
        assert len(result.issues) > 0

    def test_assess_payoff_completeness_strong(self, engine):
        """Test assessing strong payoff completeness."""
        strong_payoff = "原来如此！正如命运所安排的那样，一切都圆满了。全部完成，彻底解决。"
        score = engine._assess_payoff_completeness(strong_payoff)
        assert score >= 0.5

    def test_assess_payoff_completeness_weak(self, engine):
        """Test assessing weak payoff completeness."""
        weak_payoff = "也许可能大概如此吧，似乎还没完全结束。"
        score = engine._assess_payoff_completeness(weak_payoff)
        assert score < 0.5

    def test_assess_payoff_satisfaction_excellent(self, engine):
        """Test assessing excellent payoff satisfaction."""
        excellent_payoff = "原来如此！正如命运所安排的那样，英雄终于觉醒了力量，他激动地热泪盈眶！"
        score = engine._assess_payoff_satisfaction(excellent_payoff)
        assert score >= 0.6

    def test_assess_resolution_clarity(self, engine):
        """Test assessing resolution clarity."""
        clear = "原来如此！这就是当年发生的一切，全部真相大白。"
        vague = "也许可能大概是这样吧。"
        clear_score = engine._assess_resolution_clarity(clear)
        vague_score = engine._assess_resolution_clarity(vague)
        assert clear_score > vague_score

    def test_assess_emotional_impact(self, engine):
        """Test assessing emotional impact."""
        high_impact = "他激动地热泪盈眶，心中充满欣喜若狂的感动。"
        low_impact = "他平静地接受了这一切。"
        high_score = engine._assess_emotional_impact(high_impact)
        low_score = engine._assess_emotional_impact(low_impact)
        assert high_score > low_score

    def test_assess_thematic_alignment(self, engine):
        """Test assessing thematic alignment."""
        plant = "这是一个关于命运的故事，轮回将再次开始。"
        payoff = "正如命运的安排，轮回再次完成。"
        score = engine._assess_thematic_alignment(plant, payoff)
        assert score >= 0.5

    def test_analyze_chapter_payoff_completeness(self, engine):
        """Test analyzing single chapter payoff completeness."""
        chapter = Chapter(
            id="ch_10",
            number=10,
            title="觉醒",
            content="原来如此！正如老人预言的那样，李明终于觉醒了力量。"
        )

        profile = engine.analyze_chapter_payoff_completeness(chapter)

        assert profile.chapter_number == 10
        assert isinstance(profile, ChapterPayoffProfile)
        assert profile.payoff_count >= 0
        assert profile.plant_count >= 0

    def test_analyze_novel_payoff_completeness(self, engine, sample_novel):
        """Test analyzing entire novel payoff completeness."""
        analysis = engine.analyze_novel_payoff_completeness(sample_novel)

        assert isinstance(analysis, PayoffCompletenessAnalysis)
        assert analysis.total_plants >= 0
        assert analysis.overall_completeness_score >= 0.0
        assert analysis.overall_satisfaction_score >= 0.0
        assert analysis.payoff_ratio >= 0.0
        assert analysis.full_payoff_ratio >= 0.0

    def test_create_revision_plan(self, engine, sample_novel):
        """Test creating revision plan."""
        analysis = engine.analyze_novel_payoff_completeness(sample_novel)
        plan = engine.create_revision_plan(analysis)

        assert isinstance(plan, PayoffCompletenessPlan)
        assert isinstance(plan.priority_order, list)
        assert plan.ai_generation is True

    def test_generate_report(self, engine, sample_novel):
        """Test generating complete report."""
        analysis = engine.analyze_novel_payoff_completeness(sample_novel)
        report = engine.generate_report(analysis)

        assert isinstance(report, PayoffCompletenessReport)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0

    def test_get_summary(self, engine, sample_novel):
        """Test getting human-readable summary."""
        analysis = engine.analyze_novel_payoff_completeness(sample_novel)
        summary = engine.get_summary(analysis)

        assert isinstance(summary, str)
        assert "伏笔回收完整性检查报告" in summary
        assert "总伏笔数" in summary

    def test_find_payoff_issues(self, engine):
        """Test finding payoff issues."""
        issues = engine._find_payoff_issues(
            completeness=0.2,
            satisfaction=0.2,
            clarity=0.3,
            emotional=0.2,
            thematic=0.3,
            payoff_content="也许可能大概是这样吧。"
        )

        assert len(issues) > 0
        assert any("回收不完整" in i or "令人失望" in i for i in issues)

    def test_generate_payoff_recommendations(self, engine):
        """Test generating payoff recommendations."""
        recs = engine._generate_payoff_recommendations(
            PayoffCompletenessType.NO_PAYOFF,
            PayoffSatisfactionLevel.DISAPPOINTING,
            ["伏笔未回收"]
        )

        assert len(recs) > 0
        assert any("回收" in r for r in recs)

    def test_calculate_overall_completeness(self, engine):
        """Test calculating overall completeness score."""
        results = [
            PlantedElementPayoff(
                foreshadowing_id="fs_1",
                plant_chapter=1,
                plant_content="test",
                plant_context="test context",
                completeness_score=0.8,
                satisfaction_level=PayoffSatisfactionLevel.GOOD,
            ),
            PlantedElementPayoff(
                foreshadowing_id="fs_2",
                plant_chapter=2,
                plant_content="test",
                plant_context="test context",
                completeness_score=0.6,
                satisfaction_level=PayoffSatisfactionLevel.ACCEPTABLE,
            ),
        ]

        score = engine._calculate_overall_completeness(results)
        assert score == 0.7

    def test_calculate_overall_satisfaction(self, engine):
        """Test calculating overall satisfaction score."""
        results = [
            PlantedElementPayoff(
                foreshadowing_id="fs_1",
                plant_chapter=1,
                plant_content="test",
                plant_context="test context",
                completeness_score=0.8,
                satisfaction_level=PayoffSatisfactionLevel.GOOD,
            ),
            PlantedElementPayoff(
                foreshadowing_id="fs_2",
                plant_chapter=2,
                plant_content="test",
                plant_context="test context",
                completeness_score=0.6,
                satisfaction_level=PayoffSatisfactionLevel.WEAK,
            ),
        ]

        score = engine._calculate_overall_satisfaction(results)
        # GOOD=0.75, WEAK=0.25, avg=0.5
        assert score == 0.5

    def test_build_chapter_profiles(self, engine, sample_chapters):
        """Test building chapter profiles."""
        plants = [
            {"id": "fs_1", "chapter": 1, "content": "test"},
        ]
        payoffs = [
            {"id": "po_1", "chapter": 10, "content": "test"},
        ]
        results = [
            PlantedElementPayoff(
                foreshadowing_id="fs_1",
                plant_chapter=1,
                plant_content="test",
                plant_context="test context",
                completeness_score=0.8,
                satisfaction_level=PayoffSatisfactionLevel.GOOD,
            ),
        ]

        profiles = engine._build_chapter_profiles(
            sample_chapters, plants, payoffs, results
        )

        assert len(profiles) == len(sample_chapters)
        assert all(isinstance(p, ChapterPayoffProfile) for p in profiles)

    def test_identify_issues(self, engine):
        """Test identifying issues from results."""
        results = [
            PlantedElementPayoff(
                foreshadowing_id="fs_1",
                plant_chapter=1,
                plant_content="test",
                plant_context="test context",
                has_payoff=False,
                completeness_score=0.0,
                satisfaction_level=PayoffSatisfactionLevel.DISAPPOINTING,
            ),
            PlantedElementPayoff(
                foreshadowing_id="fs_2",
                plant_chapter=2,
                plant_content="test",
                plant_context="test context",
                has_payoff=True,
                payoff_chapter=10,
                completeness_score=0.4,
                satisfaction_level=PayoffSatisfactionLevel.WEAK,
            ),
        ]

        issues = engine._identify_issues(results)

        assert len(issues) > 0
        assert any(i.severity == PayoffCompletenessSeverity.CRITICAL for i in issues)

    def test_auto_detect_plants(self, engine, sample_chapters):
        """Test auto-detecting plants in chapters."""
        plants = engine._auto_detect_plants(sample_chapters)
        assert len(plants) > 0

    def test_auto_detect_payoffs(self, engine, sample_chapters):
        """Test auto-detecting payoffs in chapters."""
        payoffs = engine._auto_detect_payoffs(sample_chapters)
        assert len(payoffs) > 0

    def test_empty_novel(self, engine):
        """Test handling empty novel."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {}

        analysis = engine.analyze_novel_payoff_completeness(novel)

        assert analysis.total_plants == 0
        assert analysis.overall_completeness_score == 0.0

    def test_chapter_with_no_foreshadowing(self, engine):
        """Test chapter with no foreshadowing elements."""
        chapter = Chapter(
            id="ch_5",
            number=5,
            title="普通章节",
            content="这是一个普通的章节，描述了主角在街上散步的情景。"
        )

        profile = engine.analyze_chapter_payoff_completeness(chapter)

        assert profile.plant_count == 0
        assert profile.payoff_count == 0

    def test_payoff_satisfaction_level_enum(self, engine):
        """Test payoff satisfaction level enum values."""
        assert PayoffSatisfactionLevel.EXCELLENT.value == "excellent"
        assert PayoffSatisfactionLevel.GOOD.value == "good"
        assert PayoffSatisfactionLevel.ACCEPTABLE.value == "acceptable"
        assert PayoffSatisfactionLevel.WEAK.value == "weak"
        assert PayoffSatisfactionLevel.DISAPPOINTING.value == "disappointing"

    def test_payoff_completeness_type_enum(self, engine):
        """Test payoff completeness type enum values."""
        assert PayoffCompletenessType.FULL_PAYOFF.value == "full_payoff"
        assert PayoffCompletenessType.PARTIAL_PAYOFF.value == "partial_payoff"
        assert PayoffCompletenessType.NO_PAYOFF.value == "no_payoff"

    def test_payoff_completeness_severity_enum(self, engine):
        """Test payoff completeness severity enum values."""
        assert PayoffCompletenessSeverity.CRITICAL.value == "critical"
        assert PayoffCompletenessSeverity.SEVERE.value == "severe"
        assert PayoffCompletenessSeverity.MODERATE.value == "moderate"
        assert PayoffCompletenessSeverity.MINOR.value == "minor"
        assert PayoffCompletenessSeverity.NONE.value == "none"
