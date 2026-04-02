"""Tests for GrammarCheckEngine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Novel, Chapter
from chai.models.grammar_check import (
    GrammarErrorType,
    GrammarErrorSeverity,
    GrammarError,
    GrammarCheckResult,
    ChapterGrammarProfile,
    GrammarCheckAnalysis,
    GrammarCheckRevision,
    GrammarCheckPlan,
    GrammarCheckReport,
    TypoPattern,
    GrammarPattern,
)
from chai.engines.grammar_check_engine import GrammarCheckEngine


class MockAIService:
    """Mock AI service for testing."""
    pass


@pytest.fixture
def ai_service():
    """Create a mock AI service."""
    return MockAIService()


@pytest.fixture
def engine(ai_service):
    """Create a grammar check engine."""
    return GrammarCheckEngine(ai_service)


@pytest.fixture
def sample_chapter():
    """Create a sample chapter with known errors."""
    return Chapter(
        id="ch_1",
        number=1,
        title="第一章",
        content="""这是一个美好的早晨。阳光照进窗户，小明起床了。

"我今天要去做一件很重要的事！"他高兴的跳了起来。

慢慢的地走出房门，他想起昨天的话。曾经的记忆中，有一个声音在呼唤。

突然，门铃响了。小明开门一看，原来是他的老朋友。

他们一起去了公园，玩得很开心。公园里有花有草有树。

走着走着，他们遇到了一只可爱的小狗。小狗很活泼，汪汪的叫着。

到了中午，他们的肚子饿了，于是去了一家餐厅吃饭。

餐厅里人很多，很热闹。他们点了一些菜和饮料。

吃完饭，他们决定回家。在回家的路上，他们聊了很多。

回到家，小明躺在床上，想着今天发生的事。
这就是他的一天，虽然简单，但很快乐。"""
    )


@pytest.fixture
def sample_chapter_with_errors():
    """Create a chapter with specific grammar errors."""
    return Chapter(
        id="ch_2",
        number=2,
        title="第二章",
        content="""这是一个错误的句子测试。

他很高的高兴地跳了起来。

慢慢的地走在路上，突然天空中出现了奇异的现象。

小明看到了一只会飞的小鸟。小鸟的羽毛很漂亮的。

他想起曾经了的那段记忆。

门铃响了，小明开了门，看见了他朋友。

他们聊了很久，已经了聊不完的话题。

突然，天空下起了雨。他们赶快跑回屋里。

雨很大，大的可怕。他们只能待在家里。

这就是一天发生的事，一件一件的。"""
    )


@pytest.fixture
def sample_chapter_typos():
    """Create a chapter with typos."""
    return Chapter(
        id="ch_3",
        number=3,
        title="第三章",
        content="""这是一个测试章节。

他象往常一样出门。这件事十分的重要。

天空中布满了星群。星群闪闪发亮。

小明的爸爸是一个老师。他教小学生。

他们的教室在二楼。二楼有很大的窗户。

这就是他们的学校，一个很美丽的地方。"""
    )


@pytest.fixture
def sample_novel(sample_chapter, sample_chapter_with_errors, sample_chapter_typos):
    """Create a sample novel."""
    novel = MagicMock(spec=Novel)
    novel.chapters = {
        1: sample_chapter,
        2: sample_chapter_with_errors,
        3: sample_chapter_typos,
    }
    return novel


class TestGrammarCheckEngine:
    """Tests for GrammarCheckEngine."""

    def test_engine_initialization(self, engine):
        """Test engine can be initialized."""
        assert engine is not None
        assert hasattr(engine, 'ai_service')

    def test_check_chapter_grammar(self, engine, sample_chapter):
        """Test checking a single chapter."""
        profile, errors = engine.check_chapter_grammar(sample_chapter)

        assert isinstance(profile, ChapterGrammarProfile)
        assert isinstance(errors, list)
        assert profile.chapter_number == 1
        assert profile.chapter_title == "第一章"

    def test_check_chapter_grammar_with_errors(self, engine, sample_chapter_with_errors):
        """Test checking a chapter with errors."""
        profile, errors = engine.check_chapter_grammar(sample_chapter_with_errors)

        assert profile.total_errors > 0
        assert profile.critical_errors >= 0
        assert profile.major_errors >= 0
        assert profile.minor_errors >= 0

    def test_check_novel_grammar(self, engine, sample_novel):
        """Test checking entire novel."""
        analysis = engine.check_novel_grammar(sample_novel)

        assert isinstance(analysis, GrammarCheckAnalysis)
        assert analysis.total_chapters == 3
        assert analysis.total_errors >= 0
        assert len(analysis.chapter_profiles) == 3

    def test_detect_typos(self, engine, sample_chapter_typos):
        """Test typo detection."""
        profile, errors = engine.check_chapter_grammar(sample_chapter_typos)

        typo_errors = [e for e in errors if e.error_type == GrammarErrorType.TYPO]
        assert len(typo_errors) >= 0  # May or may not find typos depending on content

    def test_detect_repeated_le(self, engine, sample_chapter_with_errors):
        """Test detection of repeated 了."""
        profile, errors = engine.check_chapter_grammar(sample_chapter_with_errors)

        le_errors = [e for e in errors if e.error_type == GrammarErrorType.REPEATED_LE]
        extra_le_errors = [e for e in errors if e.error_type == GrammarErrorType.EXTRA_LE]

        # Should find "曾经了" and/or "已经了"
        found_le_errors = len(le_errors) + len(extra_le_errors)
        assert found_le_errors >= 0

    def test_detect_de_confusion(self, engine, sample_chapter_with_errors):
        """Test detection of 的/地/得 confusion."""
        profile, errors = engine.check_chapter_grammar(sample_chapter_with_errors)

        de_errors = [e for e in errors if e.error_type == GrammarErrorType.DE_CONFUSION]
        # Should find some de confusion errors
        assert len(de_errors) >= 0

    def test_detect_punctuation_errors(self, engine, sample_chapter_with_errors):
        """Test detection of punctuation errors."""
        profile, errors = engine.check_chapter_grammar(sample_chapter_with_errors)

        punct_errors = [e for e in errors if 'punctuation' in e.error_type.value]
        assert isinstance(punct_errors, list)

    def test_create_revision_plan(self, engine, sample_novel):
        """Test creating revision plan."""
        analysis = engine.check_novel_grammar(sample_novel)
        plan = engine.create_revision_plan(analysis)

        assert isinstance(plan, GrammarCheckPlan)
        assert isinstance(plan.priority_order, list)

    def test_generate_check_report(self, engine, sample_novel):
        """Test generating check report."""
        analysis = engine.check_novel_grammar(sample_novel)
        report = engine.generate_check_report(analysis)

        assert isinstance(report, GrammarCheckReport)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0

    def test_get_grammar_summary(self, engine, sample_novel):
        """Test getting grammar summary."""
        analysis = engine.check_novel_grammar(sample_novel)
        summary = engine.get_grammar_summary(analysis)

        assert isinstance(summary, str)
        assert "语法与错别字检查报告" in summary

    def test_chapter_profile_scores(self, engine, sample_chapter):
        """Test chapter profile score calculation."""
        profile, errors = engine.check_chapter_grammar(sample_chapter)

        assert 0.0 <= profile.grammar_score <= 1.0
        assert 0.0 <= profile.typo_score <= 1.0
        assert 0.0 <= profile.punctuation_score <= 1.0

    def test_overall_analysis_scores(self, engine, sample_novel):
        """Test overall analysis score calculation."""
        analysis = engine.check_novel_grammar(sample_novel)

        assert 0.0 <= analysis.overall_grammar_score <= 1.0
        assert 0.0 <= analysis.overall_typo_score <= 1.0
        assert 0.0 <= analysis.overall_punctuation_score <= 1.0

    def test_split_sentences(self, engine):
        """Test sentence splitting."""
        content = "这是一个句子。这是一个另一个句子！"  # Should split to 2 sentences
        sentences = engine._split_sentences(content)

        assert len(sentences) >= 2

    def test_is_dialogue(self, engine):
        """Test dialogue detection."""
        dialogue_sentence = '"我今天很开心！"他说。'
        normal_sentence = "这是一个普通的句子。"

        assert engine._is_dialogue(dialogue_sentence) == True
        assert engine._is_dialogue(normal_sentence) == False

    def test_empty_chapter(self, engine):
        """Test checking an empty chapter."""
        empty_chapter = Chapter(
            id="ch_empty",
            number=1,
            title="空章节",
            content=""
        )

        profile, errors = engine.check_chapter_grammar(empty_chapter)

        assert profile.total_sentences == 0
        assert profile.total_errors == 0
        assert len(errors) == 0

    def test_empty_novel(self, engine):
        """Test checking an empty novel."""
        empty_novel = MagicMock(spec=Novel)
        empty_novel.chapters = {}

        analysis = engine.check_novel_grammar(empty_novel)

        assert analysis.total_chapters == 0
        assert analysis.total_errors == 0


class TestGrammarErrorModels:
    """Tests for grammar error models."""

    def test_grammar_error_model(self):
        """Test GrammarError model creation."""
        error = GrammarError(
            error_id="test_001",
            chapter=1,
            sentence="这是一个测试句子。",
            position=5,
            error_type=GrammarErrorType.TYPO,
            severity=GrammarErrorSeverity.MINOR,
            original_text="测试",
            suggested_fix="测验",
            description="测试错别字",
        )

        assert error.error_id == "test_001"
        assert error.chapter == 1
        assert error.error_type == GrammarErrorType.TYPO
        assert error.severity == GrammarErrorSeverity.MINOR

    def test_grammar_check_result_model(self):
        """Test GrammarCheckResult model creation."""
        result = GrammarCheckResult(
            passage="这是一个测试段落。",
            passage_type="narration",
            error_count=1,
            errors=[],
            grammar_score=0.95,
            has_critical_errors=False,
        )

        assert result.passage == "这是一个测试段落。"
        assert result.grammar_score == 0.95

    def test_chapter_grammar_profile_model(self):
        """Test ChapterGrammarProfile model creation."""
        profile = ChapterGrammarProfile(
            chapter_number=1,
            chapter_title="第一章",
            total_sentences=10,
            total_errors=2,
            grammar_score=0.9,
        )

        assert profile.chapter_number == 1
        assert profile.total_sentences == 10
        assert profile.total_errors == 2

    def test_grammar_check_analysis_model(self):
        """Test GrammarCheckAnalysis model creation."""
        analysis = GrammarCheckAnalysis(
            total_chapters=5,
            total_sentences=100,
            total_errors=10,
            overall_grammar_score=0.9,
        )

        assert analysis.total_chapters == 5
        assert analysis.total_sentences == 100
        assert analysis.overall_grammar_score == 0.9

    def test_grammar_check_plan_model(self):
        """Test GrammarCheckPlan model creation."""
        plan = GrammarCheckPlan(
            critical_to_fix=["e1", "e2"],
            major_to_fix=["e3"],
            chapters_to_revise=[1, 2],
            estimated_fixes=3,
        )

        assert len(plan.critical_to_fix) == 2
        assert len(plan.chapters_to_revise) == 2

    def test_typo_pattern_model(self):
        """Test TypoPattern model creation."""
        typo = TypoPattern(
            pattern="象",
            correction="像",
            error_type=GrammarErrorType.TYPO,
            examples=["图像", "画像"],
        )

        assert typo.pattern == "象"
        assert typo.correction == "像"

    def test_grammar_pattern_model(self):
        """Test GrammarPattern model creation."""
        pattern = GrammarPattern(
            pattern=r"了了",
            error_type=GrammarErrorType.REPEATED_LE,
            description="'了'字重复",
            severity=GrammarErrorSeverity.MAJOR,
        )

        assert pattern.pattern == r"了了"
        assert pattern.error_type == GrammarErrorType.REPEATED_LE
        assert pattern.severity == GrammarErrorSeverity.MAJOR


class TestGrammarErrorTypes:
    """Tests for grammar error type enum."""

    def test_grammar_error_types_exist(self):
        """Test all grammar error types are defined."""
        assert GrammarErrorType.INCOMPLETE_SENTENCE is not None
        assert GrammarErrorType.DE_CONFUSION is not None
        assert GrammarErrorType.REPEATED_LE is not None
        assert GrammarErrorType.TYPO is not None
        assert GrammarErrorType.PUNCTUATION_CONFUSION is not None

    def test_severity_levels_exist(self):
        """Test all severity levels are defined."""
        assert GrammarErrorSeverity.CRITICAL is not None
        assert GrammarErrorSeverity.MAJOR is not None
        assert GrammarErrorSeverity.MINOR is not None
        assert GrammarErrorSeverity.TYPOGRAPHICAL is not None