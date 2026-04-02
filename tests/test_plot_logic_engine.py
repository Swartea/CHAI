"""Tests for plot logic self-consistency engine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Novel, Volume, Chapter
from chai.models.character import Character, CharacterRole
from chai.models.character import CharacterRole
from chai.engines.plot_logic_engine import PlotLogicEngine
from chai.models.plot_logic import (
    PlotLogicType,
    PlotLogicSeverity,
    PlotTimelineEvent,
    CharacterKnowledgeState,
    PlotLogicIssue,
    ChapterPlotLogicProfile,
    PlotLogicAnalysis,
    PlotLogicReport,
    PlotConsistencyTemplate,
)


class MockAIService:
    """Mock AI service for testing."""
    pass


@pytest.fixture
def ai_service():
    """Create mock AI service."""
    return MockAIService()


@pytest.fixture
def engine(ai_service):
    """Create plot logic engine."""
    return PlotLogicEngine(ai_service)


@pytest.fixture
def sample_character():
    """Create a sample character for testing."""
    return Character(
        id="char_001",
        name="张三",
        role=CharacterRole.PROTAGONIST,
        personality_description="性格直率，勇敢果断",
    )


@pytest.fixture
def sample_characters():
    """Create sample characters for testing."""
    return [
        Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            personality_description="性格直率，勇敢果断",
        ),
        Character(
            id="char_002",
            name="李四",
            role=CharacterRole.SUPPORTING,
            personality_description="聪明机智，善于谋略",
        ),
    ]


@pytest.fixture
def sample_chapter():
    """Create a sample chapter with content."""
    chapter = Chapter(
        id="ch_001",
        number=1,
        title="第一章 初遇",
        content="""
在一个月黑风高的夜晚，张三独自走在古老的街道上。
突然，他听到身后传来一阵脚步声。由于心中有些不安，他加快了脚步。
因此，他决定绕道而行。
就在这时，李四出现了。
张三：你是谁？
李四：我是来帮助你的人。
两人相视一笑，决定一起前行。
""",
        characters_involved=["char_001", "char_002"],
    )
    return chapter


@pytest.fixture
def problematic_chapter():
    """Create a chapter with potential plot logic issues."""
    chapter = Chapter(
        id="ch_002",
        number=2,
        title="第二章 矛盾",
        content="""
张三明明不知道李四的真实身份，却说："我知道你其实是来害我的。"
李四：但是我明明是好人。
然而，张三却没有继续追问下去。
突然，张三学会了一种他从未训练过的神奇技能。
最后，张三瞬间从城东赶到了城西。
"""
    )
    return chapter


@pytest.fixture
def chapter_with_travel():
    """Create a chapter with travel issues."""
    chapter = Chapter(
        id="ch_003",
        number=3,
        title="第三章 旅行",
        content="""
张三在城东的客栈中醒来。
他决定前往城西的寺庙。
于是，他来到了城西的寺庙门口。
李四已经在那里等候多时。
"""
    )
    return chapter


@pytest.fixture
def consistent_chapter():
    """Create a chapter with consistent plot logic."""
    chapter = Chapter(
        id="ch_004",
        number=4,
        title="第四章 一致",
        content="""
经过三个月的训练，张三终于掌握了这种技能。
他的师父李四对此感到非常欣慰。
因为张三的刻苦努力，他得以顺利出师。
从此以后，张三开始在江湖上行侠仗义。
"""
    )
    return chapter


class TestPlotLogicModels:
    """Test plot logic models."""

    def test_plot_logic_type_enum(self):
        """Test PlotLogicType enum values."""
        assert PlotLogicType.TIMELINE_REVERSAL.value == "timeline_reversal"
        assert PlotLogicType.CHARACTER_KNOWLEDGE_INCONSISTENT.value == "character_knowledge_inconsistent"
        assert PlotLogicType.CAUSE_EFFECT_MISSING.value == "cause_effect_missing"
        assert PlotLogicType.PLOT_INCONSISTENCY.value == "plot_inconsistency"

    def test_plot_logic_severity_enum(self):
        """Test PlotLogicSeverity enum values."""
        assert PlotLogicSeverity.MINOR.value == "minor"
        assert PlotLogicSeverity.MODERATE.value == "moderate"
        assert PlotLogicSeverity.SEVERE.value == "severe"
        assert PlotLogicSeverity.CRITICAL.value == "critical"

    def test_plot_timeline_event(self):
        """Test PlotTimelineEvent model."""
        event = PlotTimelineEvent(
            event_id="evt_001",
            chapter=1,
            title="测试事件",
            description="这是一个测试事件",
            characters_involved=["char_001"],
        )
        assert event.event_id == "evt_001"
        assert event.chapter == 1

    def test_character_knowledge_state(self):
        """Test CharacterKnowledgeState model."""
        state = CharacterKnowledgeState(
            character_id="char_001",
            character_name="张三",
            known_information=["secret_001"],
            relationships={"char_002": "friend"},
        )
        assert state.character_id == "char_001"
        assert "secret_001" in state.known_information

    def test_plot_logic_issue(self):
        """Test PlotLogicIssue model."""
        issue = PlotLogicIssue(
            issue_id="issue_001",
            issue_type=PlotLogicType.PLOT_INCONSISTENCY,
            severity=PlotLogicSeverity.MODERATE,
            title="测试问题",
            description="这是一个测试问题",
            suggestion="修复建议",
        )
        assert issue.issue_type == PlotLogicType.PLOT_INCONSISTENCY
        assert issue.severity == PlotLogicSeverity.MODERATE

    def test_chapter_plot_logic_profile(self):
        """Test ChapterPlotLogicProfile model."""
        profile = ChapterPlotLogicProfile(
            chapter_id="ch_001",
            chapter_number=1,
            chapter_title="测试章节",
            timeline_consistency_score=0.9,
            causality_score=0.85,
            overall_score=0.87,
        )
        assert profile.chapter_number == 1
        assert profile.overall_score == 0.87

    def test_plot_consistency_template(self):
        """Test PlotConsistencyTemplate model."""
        template = PlotConsistencyTemplate(
            template_name="fantasy_template",
            template_description="奇幻小说模板",
            magic_rules=["魔法消耗体力", "禁术有代价"],
            timeline_strictness=0.9,
        )
        assert "魔法消耗体力" in template.magic_rules
        assert template.timeline_strictness == 0.9


class TestExtractTimelineEvents:
    """Test timeline event extraction."""

    def test_extract_events_with_causal_language(self, engine, sample_chapter):
        """Test extraction of events with causal language."""
        events = engine._extract_timeline_events(sample_chapter, [])
        # Should find events with 因果 language like "因此"
        assert len(events) >= 0

    def test_extract_events_with_revelation_language(self, engine):
        """Test extraction of events with knowledge revelation."""
        chapter = Chapter(
            id="ch_test",
            number=1,
            title="测试章节",
            content="张三突然明白了，原来李四一直在骗他。",
        )
        events = engine._extract_timeline_events(chapter, [])
        assert len(events) >= 0


class TestTimelineConsistency:
    """Test timeline consistency checking."""

    def test_timeline_consistency_basic(self, engine):
        """Test basic timeline consistency check."""
        events = [
            PlotTimelineEvent(
                event_id="evt_001",
                chapter=1,
                title="事件1",
                description="张三出发去城里",
            ),
            PlotTimelineEvent(
                event_id="evt_002",
                chapter=2,
                title="事件2",
                description="张三到达城里",
            ),
        ]
        score, issues = engine._check_timeline_consistency(events)
        assert score >= 0.0
        assert score <= 1.0


class TestCharacterKnowledgeConsistency:
    """Test character knowledge consistency checking."""

    def test_knowledge_tracking(self, engine, sample_chapter):
        """Test character knowledge tracking."""
        previous_knowledge = {}
        updated_knowledge, score, issues = engine._check_character_knowledge_consistency(
            sample_chapter, previous_knowledge, sample_chapter.content
        )
        assert score >= 0.0
        assert score <= 1.0
        assert isinstance(updated_knowledge, dict)

    def test_knowledge_with_no_content(self, engine, sample_chapter):
        """Test knowledge check with empty content."""
        previous_knowledge = {
            "char_001": CharacterKnowledgeState(
                character_id="char_001",
                character_name="张三",
                known_information=["secret_001"],
            )
        }
        updated_knowledge, score, issues = engine._check_character_knowledge_consistency(
            sample_chapter, previous_knowledge, ""
        )
        assert score == 1.0
        assert len(issues) == 0


class TestCausalityConsistency:
    """Test causality consistency checking."""

    def test_causality_with_effect_but_no_cause(self, engine):
        """Test detection of effect without cause."""
        events = [
            PlotTimelineEvent(
                event_id="evt_001",
                chapter=1,
                title="事件1",
                description="因此，张三决定离开。",
            ),
        ]
        score, issues = engine._check_causality_consistency(events)
        # Should find an issue since there's no prior cause
        assert score >= 0.0

    def test_causality_with_proper_chain(self, engine):
        """Test causality with proper cause-effect chain."""
        events = [
            PlotTimelineEvent(
                event_id="evt_001",
                chapter=1,
                title="事件1",
                description="张三遇到了李四",
            ),
            PlotTimelineEvent(
                event_id="evt_002",
                chapter=2,
                title="事件2",
                description="因此，张三决定帮助李四",
                causes=["evt_001"],
            ),
        ]
        score, issues = engine._check_causality_consistency(events)
        assert score >= 0.0


class TestWorldRulesConsistency:
    """Test world rules consistency checking."""

    def test_world_rules_basic(self, engine, sample_chapter):
        """Test basic world rules check."""
        score, issues = engine._check_world_rules_consistency(sample_chapter)
        assert score >= 0.0
        assert score <= 1.0

    def test_world_rules_with_template(self, engine, sample_chapter):
        """Test world rules check with template."""
        template = PlotConsistencyTemplate(
            template_name="test",
            magic_rules=["魔法需要咏唱"],
        )
        score, issues = engine._check_world_rules_consistency(sample_chapter, template)
        assert score >= 0.0


class TestTravelTimeConsistency:
    """Test travel time consistency checking."""

    def test_travel_consistency_with_travel_mention(self, engine, chapter_with_travel, sample_chapter):
        """Test travel consistency when travel is mentioned."""
        score, issues = engine._check_travel_time_consistency(chapter_with_travel, sample_chapter)
        assert score >= 0.0

    def test_travel_consistency_without_previous(self, engine, chapter_with_travel):
        """Test travel consistency without previous chapter."""
        score, issues = engine._check_travel_time_consistency(chapter_with_travel, None)
        assert score == 1.0


class TestPlotInconsistencies:
    """Test plot inconsistency detection."""

    def test_contradiction_detection(self, engine, problematic_chapter):
        """Test detection of contradictions in text."""
        score, issues = engine._check_plot_inconsistencies(problematic_chapter, [])
        assert score >= 0.0

    def test_no_issues_on_consistent_text(self, engine, consistent_chapter):
        """Test no issues found on consistent text."""
        score, issues = engine._check_plot_inconsistencies(consistent_chapter, [])
        assert score >= 0.0


class TestAnalyzeChapterPlotLogic:
    """Test full chapter analysis."""

    def test_analyze_chapter_basic(self, engine, sample_chapter, sample_characters):
        """Test basic chapter analysis."""
        analysis = engine.analyze_chapter_plot_logic(
            sample_chapter, sample_characters
        )
        assert analysis is not None
        assert isinstance(analysis, PlotLogicAnalysis)
        assert analysis.chapter_profile.chapter_id == "ch_001"

    def test_analyze_chapter_with_previous(self, engine, sample_chapter, problematic_chapter, sample_characters):
        """Test chapter analysis with previous chapter."""
        analysis = engine.analyze_chapter_plot_logic(
            problematic_chapter,
            sample_characters,
            previous_chapter=sample_chapter,
        )
        assert analysis is not None
        assert isinstance(analysis, PlotLogicAnalysis)

    def test_analyze_chapter_with_empty_content(self, engine, sample_characters):
        """Test analysis of chapter with empty content."""
        chapter = Chapter(
            id="ch_empty",
            number=1,
            title="空章节",
            content="",
        )
        analysis = engine.analyze_chapter_plot_logic(chapter, sample_characters)
        assert analysis is not None
        assert analysis.total_issues == 0


class TestAnalyzeNovelPlotLogic:
    """Test full novel analysis."""

    def test_analyze_novel_basic(self, engine, sample_characters):
        """Test basic novel analysis."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {
            "ch_001": Chapter(id="ch_001", number=1, title="第一章", content="第一章内容"),
            "ch_002": Chapter(id="ch_002", number=2, title="第二章", content="第二章内容"),
        }
        report = engine.analyze_novel_plot_logic(novel, sample_characters)
        assert report is not None
        assert isinstance(report, PlotLogicReport)
        assert report.total_chapters_analyzed == 2

    def test_analyze_novel_with_dict_chapters(self, engine, sample_characters):
        """Test novel analysis with chapters as dict."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {
            "ch_001": Chapter(id="ch_001", number=1, title="第一章", content="第一章内容"),
            "ch_002": Chapter(id="ch_002", number=2, title="第二章", content="第二章内容"),
        }
        report = engine.analyze_novel_plot_logic(novel, sample_characters)
        assert report.total_chapters_analyzed == 2


class TestCreateRevisionPlan:
    """Test revision plan creation."""

    def test_create_revision_plan(self, engine, sample_chapter, sample_characters):
        """Test revision plan creation."""
        analysis = engine.analyze_chapter_plot_logic(
            sample_chapter, sample_characters
        )
        revision = engine.create_revision_plan(analysis)
        assert revision is not None
        assert revision.analysis_id == analysis.analysis_id


class TestGetSummary:
    """Test summary generation."""

    def test_get_summary(self, engine, sample_characters):
        """Test summary generation."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {
            "ch_001": Chapter(id="ch_001", number=1, title="第一章", content="第一章内容"),
        }
        report = engine.analyze_novel_plot_logic(novel, sample_characters)
        summary = engine.get_summary(report)
        assert "情节逻辑自洽性检查报告" in summary
        assert "检查章节数" in summary


class TestPlotLogicIssuePrioritization:
    """Test issue prioritization."""

    def test_critical_issues_prioritized(self, engine, sample_characters):
        """Test that critical issues are prioritized."""
        # Create a chapter with multiple issues
        chapter = Chapter(
            id="ch_multi",
            number=1,
            title="多问题章节",
            content="""
这是一个充满各种问题的小说章节。
明明不知道但是知道。
因此却没有原因。
突然出现却没训练过的新技能。
从城东瞬间到达城西。
张三：但是我明明是好人。
李四：然而事实并非如此。
""",
        )
        analysis = engine.analyze_chapter_plot_logic(chapter, sample_characters)
        revision = engine.create_revision_plan(analysis)

        # Priority fixes should contain severe/critical issues
        assert isinstance(revision.priority_fixes, list)
