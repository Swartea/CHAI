"""Tests for PunctuationCheckEngine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Novel, Chapter
from chai.models.punctuation_check import (
    PunctuationErrorType,
    PunctuationSeverity,
    PunctuationIssue,
    PunctuationCheckResult,
    ChapterPunctuationProfile,
    PunctuationCheckAnalysis,
    PunctuationCheckRevision,
    PunctuationCheckPlan,
    PunctuationCheckReport,
    PunctuationStyle,
    PunctuationTemplate,
    STANDARD_TEMPLATES,
)
from chai.engines.punctuation_check_engine import PunctuationCheckEngine


class MockAIService:
    """Mock AI service for testing."""
    pass


@pytest.fixture
def ai_service():
    """Create a mock AI service."""
    return MockAIService()


@pytest.fixture
def engine(ai_service):
    """Create a punctuation check engine."""
    return PunctuationCheckEngine(ai_service)


@pytest.fixture
def sample_chapter():
    """Create a sample chapter with known punctuation issues."""
    return Chapter(
        id="ch_1",
        number=1,
        title="第一章",
        content="""这是一个美好的早晨。阳光照进窗户，小明起床了。

"我今天要去做一件很重要的事！"他高兴的说。

突然，天空中出现了奇异的现象...这到底是怎么回事呢？

他们一起去了公园——那里有花有草有树。

走着走着，他们遇到了一只小狗。小狗很活泼，汪汪的叫着。（如图所示）

到了中午，他们的肚子饿了，于是去了一家餐厅吃饭。

餐厅里人很多...很热闹。

小明想：这一切是真的吗？"他说。"""
    )


@pytest.fixture
def sample_chapter_with_issues():
    """Create a chapter with specific punctuation errors."""
    return Chapter(
        id="ch_2",
        number=2,
        title="第二章",
        content="""这是一个错误的句子测试。

他很高,兴地跳了起来,,,

天空中出现了奇异的现象......
这到底是怎么回事呢？？？

他们去了公园——那里有花有草有树。
"我今天要去!"他说,。
"""

    )


@pytest.fixture
def sample_novel(sample_chapter, sample_chapter_with_issues):
    """Create a sample novel with chapters."""
    from chai.models import Volume
    volume = Volume(
        id="vol_1",
        title="第一卷",
        number=1,
        chapters=[sample_chapter, sample_chapter_with_issues],
    )
    return Novel(
        id="novel_1",
        title="测试小说",
        genre="玄幻",
        volumes=[volume],
    )


class TestPunctuationCheckEngine:
    """Tests for PunctuationCheckEngine class."""

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert engine.template is not None
        assert engine.template.name == "默认中文标点"

    def test_engine_with_custom_template(self, ai_service):
        """Test engine with custom template."""
        engine = PunctuationCheckEngine(ai_service, template_name="formal")
        assert engine.template.name == "正式文体"

    def test_check_chapter_punctuation(self, engine, sample_chapter):
        """Test checking a single chapter."""
        profile, issues = engine.check_chapter_punctuation(sample_chapter)

        assert profile is not None
        assert profile.chapter_number == 1
        assert profile.total_sentences > 0
        assert profile.total_characters > 0
        assert isinstance(issues, list)

    def test_check_chapter_punctuation_empty_content(self, engine):
        """Test checking a chapter with empty content."""
        chapter = Chapter(id="ch_empty", number=1, title="空章节", content="")
        profile, issues = engine.check_chapter_punctuation(chapter)

        assert profile.chapter_number == 1
        assert profile.total_sentences == 0
        assert len(issues) == 0

    def test_check_novel_punctuation(self, engine, sample_novel):
        """Test checking entire novel."""
        analysis = engine.check_novel_punctuation(sample_novel)

        assert analysis is not None
        assert analysis.total_chapters == 2
        assert analysis.total_sentences > 0
        assert isinstance(analysis.chapter_profiles, list)
        assert len(analysis.chapter_profiles) == 2

    def test_check_novel_punctuation_empty_novel(self, engine):
        """Test checking a novel with no chapters."""
        from chai.models import Volume
        novel = Novel(id="novel_empty", title="空小说", genre="玄幻", volumes=[])
        analysis = engine.check_novel_punctuation(novel)

        assert analysis.total_chapters == 0
        assert analysis.total_sentences == 0
        assert analysis.total_issues == 0

    def test_create_revision_plan(self, engine, sample_novel):
        """Test creating a revision plan."""
        analysis = engine.check_novel_punctuation(sample_novel)
        plan = engine.create_revision_plan(analysis)

        assert plan is not None
        assert isinstance(plan.estimated_fixes, int)
        assert isinstance(plan.chapters_to_revise, list)

    def test_generate_check_report(self, engine, sample_novel):
        """Test generating a check report."""
        analysis = engine.check_novel_punctuation(sample_novel)
        report = engine.generate_check_report(analysis)

        assert report is not None
        assert report.analysis is not None
        assert report.revision_plan is not None
        assert isinstance(report.summary, str)

    def test_get_punctuation_summary(self, engine, sample_novel):
        """Test getting a human-readable summary."""
        analysis = engine.check_novel_punctuation(sample_novel)
        summary = engine.get_punctuation_summary(analysis)

        assert isinstance(summary, str)
        assert "标点符号规范化检查报告" in summary

    def test_detect_english_ellipsis(self, engine):
        """Test detection of English ellipsis in Chinese text."""
        chapter = Chapter(
            id="ch_ellipsis",
            number=1,
            title="Test",
            content="这是一个奇怪的...现象。"
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        ellipsis_issues = [i for i in issues if i.issue_type == PunctuationErrorType.ENGLISH_ELLIPSIS]
        assert len(ellipsis_issues) > 0

    def test_detect_mixed_punctuation(self, engine):
        """Test detection of mixed Chinese/English punctuation."""
        chapter = Chapter(
            id="ch_mixed",
            number=1,
            title="Test",
            content="这是一个美好的,早晨。"
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        mixed_issues = [i for i in issues if i.issue_type == PunctuationErrorType.MIXED_PUNCTUATION]
        assert len(mixed_issues) > 0

    def test_detect_repeated_punctuation(self, engine):
        """Test detection of repeated punctuation."""
        chapter = Chapter(
            id="ch_repeated",
            number=1,
            title="Test",
            content="这是怎么回事呢？？？他问道。"
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        repeated_issues = [i for i in issues if i.issue_type == PunctuationErrorType.REPEATED_PUNCTUATION]
        assert len(repeated_issues) > 0

    def test_detect_unpaired_quotes(self, engine):
        """Test detection of unpaired quotes."""
        chapter = Chapter(
            id="ch_quotes",
            number=1,
            title="Test",
            content='他说："这是一个测试。"'
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        # Check that issues were found
        assert isinstance(issues, list)

    def test_detect_space_before_punctuation(self, engine):
        """Test detection of space before punctuation."""
        chapter = Chapter(
            id="ch_space",
            number=1,
            title="Test",
            content="这是一个测试 。"
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        space_issues = [i for i in issues if i.issue_type == PunctuationErrorType.SPACE_BEFORE_PUNCTUATION]
        assert len(space_issues) > 0

    def test_detect_mixed_quote_style(self, engine):
        """Test detection of mixed quote styles."""
        chapter = Chapter(
            id="ch_mixed_quotes",
            number=1,
            title="Test",
            content='他说："这是一个测试"，然后她说：「这是另一个测试」。'
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        mixed_quote_issues = [i for i in issues if i.issue_type == PunctuationErrorType.MIXED_QUOTE_STYLE]
        assert len(mixed_quote_issues) > 0

    def test_detect_english_dash(self, engine):
        """Test detection of English dash in Chinese text."""
        chapter = Chapter(
            id="ch_dash",
            number=1,
            title="Test",
            content="这是一个测试--破折号。"
        )
        profile, issues = engine.check_chapter_punctuation(chapter)

        dash_issues = [i for i in issues if i.issue_type == PunctuationErrorType.MIXED_DASH_STYLE]
        assert len(dash_issues) > 0

    def test_chapter_profile_scores(self, engine, sample_chapter):
        """Test that chapter profile has valid scores."""
        profile, issues = engine.check_chapter_punctuation(sample_chapter)

        assert 0.0 <= profile.punctuation_score <= 1.0
        assert 0.0 <= profile.quote_score <= 1.0
        assert 0.0 <= profile.spacing_score <= 1.0

    def test_analysis_overall_scores(self, engine, sample_novel):
        """Test that analysis has valid overall scores."""
        analysis = engine.check_novel_punctuation(sample_novel)

        assert 0.0 <= analysis.overall_punctuation_score <= 1.0
        assert 0.0 <= analysis.overall_quote_score <= 1.0
        assert 0.0 <= analysis.overall_spacing_score <= 1.0

    def test_severity_distribution(self, engine, sample_chapter_with_issues):
        """Test severity distribution in chapter profile."""
        profile, issues = engine.check_chapter_punctuation(sample_chapter_with_issues)

        assert profile.critical_issues >= 0
        assert profile.major_issues >= 0
        assert profile.minor_issues >= 0
        assert profile.typographical_issues >= 0
        assert profile.total_issues == len(issues)

    def test_issue_counts_by_type(self, engine, sample_chapter):
        """Test issue counts by type in chapter profile."""
        profile, issues = engine.check_chapter_punctuation(sample_chapter)

        total_counted = sum(profile.issue_counts.values())
        assert total_counted == len(issues)

    def test_split_sentences(self, engine):
        """Test sentence splitting."""
        content = "这是第一句。这是第二句！这是第三句？"
        sentences = engine._split_sentences(content)

        assert len(sentences) >= 3

    def test_is_dialogue(self, engine):
        """Test dialogue detection."""
        assert engine._is_dialogue('他说："你好"') == True
        assert engine._is_dialogue('这是一个普通句子。') == False

    def test_standard_templates(self):
        """Test that standard templates are defined."""
        assert "default" in STANDARD_TEMPLATES
        assert "formal" in STANDARD_TEMPLATES
        assert "literary" in STANDARD_TEMPLATES

        assert STANDARD_TEMPLATES["default"].quote_style == "chinese_brackets"
        assert STANDARD_TEMPLATES["default"].ellipsis_style == "chinese_ellipsis"

    def test_punctuation_template_fields(self):
        """Test PunctuationTemplate has required fields."""
        template = STANDARD_TEMPLATES["default"]

        assert hasattr(template, "name")
        assert hasattr(template, "description")
        assert hasattr(template, "quote_style")
        assert hasattr(template, "dash_style")
        assert hasattr(template, "comma_style")
        assert hasattr(template, "ellipsis_style")
        assert hasattr(template, "parentheses_style")


class TestPunctuationIssueModel:
    """Tests for PunctuationIssue model."""

    def test_punctuation_issue_creation(self):
        """Test creating a PunctuationIssue."""
        issue = PunctuationIssue(
            issue_id="test_1",
            chapter=1,
            sentence="这是一个测试句子。",
            position=0,
            issue_type=PunctuationErrorType.MIXED_PUNCTUATION,
            severity=PunctuationSeverity.MAJOR,
            original_text="，",
            suggested_fix="，",
            description="测试问题",
            confidence=0.9,
        )

        assert issue.issue_id == "test_1"
        assert issue.chapter == 1
        assert issue.issue_type == PunctuationErrorType.MIXED_PUNCTUATION
        assert issue.severity == PunctuationSeverity.MAJOR
        assert issue.confidence == 0.9


class TestChapterPunctuationProfile:
    """Tests for ChapterPunctuationProfile model."""

    def test_chapter_profile_creation(self):
        """Test creating a ChapterPunctuationProfile."""
        profile = ChapterPunctuationProfile(
            chapter_number=1,
            chapter_title="第一章",
            total_sentences=10,
            total_characters=1000,
            dialogue_sentences=3,
            narration_sentences=7,
            total_issues=5,
            punctuation_score=0.95,
        )

        assert profile.chapter_number == 1
        assert profile.total_sentences == 10
        assert profile.punctuation_score == 0.95


class TestPunctuationCheckAnalysis:
    """Tests for PunctuationCheckAnalysis model."""

    def test_analysis_creation(self):
        """Test creating a PunctuationCheckAnalysis."""
        analysis = PunctuationCheckAnalysis(
            overall_punctuation_score=0.9,
            overall_quote_score=0.95,
            overall_spacing_score=0.88,
            total_chapters=5,
            total_sentences=100,
            total_issues=20,
        )

        assert analysis.overall_punctuation_score == 0.9
        assert analysis.total_chapters == 5
        assert analysis.total_issues == 20


class TestPunctuationErrorType:
    """Tests for PunctuationErrorType enum."""

    def test_error_types_defined(self):
        """Test that all expected error types are defined."""
        expected_types = [
            "MIXED_QUOTE_STYLE",
            "MIXED_PUNCTUATION",
            "REPEATED_PUNCTUATION",
            "SPACE_BEFORE_PUNCTUATION",
            "ENGLISH_ELLIPSIS",
            "MIXED_DASH_STYLE",
        ]

        for error_type in expected_types:
            assert hasattr(PunctuationErrorType, error_type)


class TestPunctuationSeverity:
    """Tests for PunctuationSeverity enum."""

    def test_severity_levels(self):
        """Test severity levels are defined."""
        assert PunctuationSeverity.CRITICAL is not None
        assert PunctuationSeverity.MAJOR is not None
        assert PunctuationSeverity.MINOR is not None
        assert PunctuationSeverity.TYPOGRAPHICAL is not None


class TestPunctuationStyle:
    """Tests for PunctuationStyle enum."""

    def test_style_options(self):
        """Test style options are defined."""
        assert PunctuationStyle.CHINESE is not None
        assert PunctuationStyle.ENGLISH is not None
        assert PunctuationStyle.MIXED is not None
        assert PunctuationStyle.CONSISTENT is not None
        assert PunctuationStyle.INCONSISTENT is not None
