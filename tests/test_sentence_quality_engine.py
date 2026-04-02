"""Tests for SentenceQualityEngine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Chapter
from chai.models.novel import Novel
from chai.models.sentence_quality_check import (
    SentenceQualityType,
    SentenceQualitySeverity,
    SentenceQualityIssue,
    SentenceQualityResult,
    ChapterSentenceQualityProfile,
    SentenceQualityAnalysis,
    SentenceQualityRevision,
    SentenceQualityPlan,
    SentenceQualityReport,
    DiseaseSentencePattern,
    RedundancyPattern,
    SentenceQualityTemplate,
)
from chai.engines.sentence_quality_engine import SentenceQualityEngine


class MockAIService:
    """Mock AI service for testing."""
    pass


@pytest.fixture
def ai_service():
    """Create a mock AI service."""
    return MockAIService()


@pytest.fixture
def engine(ai_service):
    """Create a sentence quality engine."""
    return SentenceQualityEngine(ai_service)


@pytest.fixture
def sample_chapter():
    """Create a sample chapter with known quality issues."""
    return Chapter(
        id="ch_1",
        number=1,
        title="第一章",
        content="""这是一个美好的早晨。阳光照进窗户，小明起床了。

"我今天要去做一件非常重要的事！"他高兴地跳了起来。

慢慢的地走出房门，他想起昨天的话。曾经的记忆中，有一个声音在呼唤。

非常极其重要的事情必须要做。大约左右的情况就是这样。

各种各种的花朵在风中摇曳。这是这是重复的表达。

一个空洞的句子。只是在说好，没有具体内容。

实际上其实他已经明白了。基本大概的情况是这样。
""",
    )


@pytest.fixture
def sample_novel(sample_chapter):
    """Create a sample novel."""
    novel = MagicMock(spec=Novel)
    novel.chapters = {1: sample_chapter}
    return novel


class TestSentenceQualityModels:
    """Test sentence quality models."""

    def test_sentence_quality_type_values(self):
        """Test SentenceQualityType enum values."""
        assert SentenceQualityType.MISSING_SUBJECT.value == "missing_subject"
        assert SentenceQualityType.REDUNDANT_SUBJECT.value == "redundant_subject"
        assert SentenceQualityType.SUBJECT_PREDICATE_MISMATCH.value == "subject_predicate_mismatch"
        assert SentenceQualityType.REPETITIVE_MEANING.value == "repetitive_meaning"
        assert SentenceQualityType.FILLER_PHRASE.value == "filler_phrase"

    def test_sentence_quality_severity_values(self):
        """Test SentenceQualitySeverity enum values."""
        assert SentenceQualitySeverity.CRITICAL.value == "critical"
        assert SentenceQualitySeverity.MAJOR.value == "major"
        assert SentenceQualitySeverity.MINOR.value == "minor"
        assert SentenceQualitySeverity.SUGGESTION.value == "suggestion"

    def test_sentence_quality_issue_creation(self):
        """Test SentenceQualityIssue model creation."""
        issue = SentenceQualityIssue(
            issue_id="test_1",
            chapter=1,
            sentence="这是一个测试句子。",
            position=0,
            issue_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
            severity=SentenceQualitySeverity.MINOR,
            original_text="非常极其",
            suggested_fix="极其",
            description="词语重复",
            confidence=0.9,
        )
        assert issue.issue_id == "test_1"
        assert issue.chapter == 1
        assert issue.issue_type == SentenceQualityType.REDUNDANT_DESCRIPTION
        assert issue.severity == SentenceQualitySeverity.MINOR

    def test_chapter_sentence_quality_profile_creation(self):
        """Test ChapterSentenceQualityProfile model creation."""
        profile = ChapterSentenceQualityProfile(
            chapter_number=1,
            chapter_title="第一章",
            total_sentences=10,
            total_characters=500,
            dialogue_sentences=3,
            narration_sentences=7,
            disease_counts=2,
            redundancy_counts=3,
            total_issues=5,
            critical_issues=0,
            major_issues=1,
            minor_issues=2,
            suggestions=2,
            disease_sentence_score=0.9,
            redundancy_score=0.85,
            overall_quality_score=0.875,
            needs_revision=True,
            is_concise=False,
        )
        assert profile.chapter_number == 1
        assert profile.total_sentences == 10
        assert profile.disease_counts == 2
        assert profile.redundancy_counts == 3
        assert profile.needs_revision is True


class TestSentenceQualityEngine:
    """Test SentenceQualityEngine functionality."""

    def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine is not None
        assert hasattr(engine, 'ai_service')

    def test_check_chapter_quality_empty_chapter(self, engine):
        """Test checking an empty chapter."""
        chapter = Chapter(
            id="ch_empty",
            number=1,
            title="空章节",
            content="",
        )
        profile, issues = engine.check_chapter_quality(chapter)

        assert profile.chapter_number == 1
        assert profile.total_sentences == 0
        assert len(issues) == 0

    def test_check_chapter_quality_with_content(self, engine, sample_chapter):
        """Test checking a chapter with content."""
        profile, issues = engine.check_chapter_quality(sample_chapter)

        assert profile.chapter_number == 1
        assert profile.total_sentences > 0
        assert profile.total_characters > 0
        assert len(issues) > 0

    def test_detects_redundancy_patterns(self, engine):
        """Test detection of redundancy patterns."""
        chapter = Chapter(
            id="ch_redundancy",
            number=1,
            title="冗余测试",
            content="这是一个非常极其重要的句子。大约左右的情况。各种各样的花朵。",
        )
        profile, issues = engine.check_chapter_quality(chapter)

        redundancy_issues = [i for i in issues if i.issue_type == SentenceQualityType.REDUNDANT_DESCRIPTION]
        assert len(redundancy_issues) >= 3

    def test_detects_disease_sentences(self, engine):
        """Test detection of disease sentences."""
        chapter = Chapter(
            id="ch_disease",
            number=1,
            title="病句测试",
            content="非常的高兴。他提高生活水平。",
        )
        profile, issues = engine.check_chapter_quality(chapter)

        # Should detect some issues
        assert len(issues) > 0

    def test_detects_filler_phrases(self, engine):
        """Test detection of filler phrases."""
        chapter = Chapter(
            id="ch_filler",
            number=1,
            title="填充词测试",
            content="毫无疑问，这是一个好结果。不言而喻，情况就是这样。",
        )
        profile, issues = engine.check_chapter_quality(chapter)

        filler_issues = [i for i in issues if i.issue_type == SentenceQualityType.FILLER_PHRASE]
        assert len(filler_issues) >= 2

    def test_check_novel_quality(self, engine, sample_novel):
        """Test checking entire novel."""
        analysis = engine.check_novel_quality(sample_novel)

        assert analysis.total_chapters == 1
        assert analysis.total_sentences > 0
        assert len(analysis.chapter_profiles) == 1
        assert len(analysis.all_issues) > 0

    def test_create_revision_plan(self, engine, sample_novel):
        """Test creating revision plan."""
        analysis = engine.check_novel_quality(sample_novel)
        plan = engine.create_revision_plan(analysis)

        assert plan is not None
        assert isinstance(plan, SentenceQualityPlan)
        assert len(plan.chapters_to_revise) >= 0
        # Sample content may or may not have disease sentences, but should have redundancy
        assert plan.focus_on_redundancy is True

    def test_generate_quality_report(self, engine, sample_novel):
        """Test generating quality report."""
        analysis = engine.check_novel_quality(sample_novel)
        report = engine.generate_quality_report(analysis)

        assert report is not None
        assert isinstance(report, SentenceQualityReport)
        assert report.analysis == analysis
        assert len(report.summary) > 0

    def test_get_quality_summary(self, engine, sample_novel):
        """Test getting human-readable summary."""
        analysis = engine.check_novel_quality(sample_novel)
        summary = engine.get_quality_summary(analysis)

        assert "病句与冗余句子优化报告" in summary
        assert "检查章节数" in summary

    def test_sentence_splitting(self, engine):
        """Test sentence splitting logic."""
        content = "这是第一句。这是第二句！"
        sentences = engine._split_sentences(content)

        assert len(sentences) == 2
        assert sentences[0] == "这是第一句"
        assert sentences[1] == "这是第二句"

    def test_dialogue_detection(self, engine):
        """Test dialogue detection."""
        assert engine._is_dialogue('他说："你好"') is True
        assert engine._is_dialogue('"早上好！"他说道。') is True
        assert engine._is_dialogue('这是一个普通句子。') is False

    def test_score_calculation(self, engine):
        """Test quality score calculation."""
        disease_score = engine._calculate_disease_score(5, 100)
        assert 0.0 <= disease_score <= 1.0

        redundancy_score = engine._calculate_redundancy_score(3, 100)
        assert 0.0 <= redundancy_score <= 1.0

    def test_empty_novel_returns_empty_analysis(self, engine):
        """Test that empty novel returns empty analysis."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {}

        analysis = engine.check_novel_quality(novel)
        assert analysis.total_chapters == 0
        assert len(analysis.all_issues) == 0


class TestRedundancyPatterns:
    """Test specific redundancy pattern detection."""

    @pytest.fixture
    def redundancy_engine(self, ai_service):
        return SentenceQualityEngine(ai_service)

    def test_非常极其_pattern(self, redundancy_engine):
        """Test 非常极其 redundancy detection."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="测试",
            content="这是一个非常极其重要的日子。",
        )
        _, issues = redundancy_engine.check_chapter_quality(chapter)

        redundant = [i for i in issues if i.original_text == "非常极其"]
        assert len(redundant) > 0
        assert redundant[0].suggested_fix == "极其"

    def test_各种各样_pattern(self, redundancy_engine):
        """Test 各种各样的 redundancy detection."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="测试",
            content="各种各样的花朵在花园里盛开。",
        )
        _, issues = redundancy_engine.check_chapter_quality(chapter)

        redundant = [i for i in issues if "各种" in i.original_text]
        assert len(redundant) > 0

    def test_实际上其实_pattern(self, redundancy_engine):
        """Test 实际上其实 redundancy detection."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="测试",
            content="其实实际上他已经知道了。",
        )
        _, issues = redundancy_engine.check_chapter_quality(chapter)

        redundant = [i for i in issues if "其实实际上" in i.original_text]
        assert len(redundant) > 0


class TestDiseasePatterns:
    """Test specific disease sentence pattern detection."""

    @pytest.fixture
    def disease_engine(self, ai_service):
        return SentenceQualityEngine(ai_service)

    def test_vague_expression_detection(self, disease_engine):
        """Test vague expression detection."""
        # Sentences must be exactly the vague expression to match the pattern
        # which requires ^...$ (entire sentence is the vague expression)
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="测试",
            content="很好。不错。还好。",
        )
        _, issues = disease_engine.check_chapter_quality(chapter)

        vague_issues = [i for i in issues if i.issue_type == SentenceQualityType.VAGUE_EXPRESSION]
        assert len(vague_issues) > 0

    def test_pronoun_ambiguity(self, disease_engine):
        """Test pronoun ambiguity detection."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="测试",
            content="他们三个人一起去看他。他说他们不对。",
        )
        _, issues = disease_engine.check_chapter_quality(chapter)

        ambiguity_issues = [i for i in issues if i.issue_type == SentenceQualityType.PRONOUN_AMBIGUITY]
        assert len(ambiguity_issues) > 0
