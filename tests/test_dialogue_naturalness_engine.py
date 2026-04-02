"""Tests for dialogue naturalness engine."""

import pytest
from unittest.mock import MagicMock
from chai.models import Character, Novel, Volume, Chapter
from chai.models.character import CharacterRole
from chai.engines.dialogue_naturalness_engine import DialogueNaturalnessEngine
from chai.models.dialogue_naturalness import (
    DialogueNaturalnessType,
    DialogueNaturalnessSeverity,
    CharacterDialogueProfile,
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
    """Create dialogue naturalness engine."""
    return DialogueNaturalnessEngine(ai_service)


@pytest.fixture
def sample_character():
    """Create a sample character for testing."""
    return Character(
        id="char_001",
        name="张三",
        role=CharacterRole.PROTAGONIST,
        personality_description="性格直率，说话直接，不喜欢绕弯子",
        speech_pattern="说话简短有力，经常用短句",
        speech_characteristics=["直接", "简洁"],
        catchphrases=["说白了", "就这么回事"],
    )


@pytest.fixture
def formal_character():
    """Create a formal character for testing."""
    return Character(
        id="char_002",
        name="李四",
        role=CharacterRole.SUPPORTING,
        personality_description="文雅有礼，受过良好教育",
        speech_pattern="措辞正式，用语典雅",
        speech_characteristics=["文雅", "正式"],
        catchphrases=["承蒙关照", "甚是感激"],
    )


@pytest.fixture
def sample_chapter():
    """Create a sample chapter with dialogue."""
    chapter = Chapter(
        id="ch_001",
        number=1,
        title="第一章 初遇",
        content="""
小明：今天天气真好啊。
张三：说白了，就是太热了。
小明：你怎么这么直接啊？
张三：就这么回事，没必要绕弯子。
李四：承蒙二位夸奖，愧不敢当。
小明：李四你说话真文雅。
李四：甚是感激，这只是我的习惯罢了。
张三：行行行，你们继续聊，我先走了。
"""
    )
    return chapter


@pytest.fixture
def problematic_chapter():
    """Create a chapter with problematic dialogue."""
    chapter = Chapter(
        id="ch_002",
        number=2,
        title="第二章 问题对话",
        content="""
角色1：根据我的分析，我认为这个问题的解决方案需要我们从多个角度进行考虑。
角色2：好的，我理解你的意思。
角色1：首先，然后，最后，我们需要按步骤进行。
角色2：当然，我很乐意帮助你。作为一个专业人士，我建议你可以尝试这种方法。
小明：谢谢
张三：哈
"""
    )
    return chapter


class TestBuildCharacterProfile:
    """Tests for build_character_profile method."""

    def test_build_profile_basic(self, engine, sample_character):
        """Test building a basic character profile."""
        profile = engine.build_character_profile(sample_character)

        assert profile.character_id == "char_001"
        assert profile.character_name == "张三"
        assert profile.speech_pattern == "说话简短有力，经常用短句"
        assert "说白了" in profile.catchphrases
        assert "直接" in profile.speech_quirks

    def test_build_profile_formal(self, engine, formal_character):
        """Test building a formal character profile."""
        profile = engine.build_character_profile(formal_character)

        assert profile.character_name == "李四"
        assert profile.formality_level == "formal"
        assert "承蒙关照" in profile.catchphrases


class TestExtractDialogueLines:
    """Tests for _extract_dialogue_lines method."""

    def test_extract_simple_dialogue(self, engine):
        """Test extracting simple dialogue lines."""
        text = """
小明：今天天气真好。
张三：确实不错。
"""
        lines = engine._extract_dialogue_lines(text)

        assert len(lines) == 2
        assert lines[0] == ("小明", "今天天气真好。")
        assert lines[1] == ("张三", "确实不错。")

    def test_extract_dialogue_with_colon(self, engine):
        """Test extracting dialogue with English colon."""
        text = """
小明: Hello world
张三: Hi there
"""
        lines = engine._extract_dialogue_lines(text)

        assert len(lines) == 2
        assert lines[0] == ("小明", "Hello world")
        assert lines[1] == ("张三", "Hi there")


class TestCheckLineNaturalness:
    """Tests for _check_line_naturalness method."""

    def test_natural_dialogue_high_score(self, engine, sample_character):
        """Test that natural dialogue gets high score."""
        profile = engine.build_character_profile(sample_character)
        issues, nat_score, char_score = engine._check_line_naturalness(
            "说白了，这就是问题所在。",
            profile
        )

        assert nat_score >= 0.7
        assert char_score >= 0.7
        assert len(issues) == 0

    def test_robotic_speech_detected(self, engine, sample_character):
        """Test detection of robotic speech patterns."""
        profile = engine.build_character_profile(sample_character)
        issues, nat_score, char_score = engine._check_line_naturalness(
            "好的，我理解",
            profile
        )

        robotic_issues = [i for i in issues if i.issue_type == DialogueNaturalnessType.ROBOTIC_SPEECH]
        assert len(robotic_issues) > 0
        assert nat_score < 1.0

    def test_ai_generated_pattern_detected(self, engine, sample_character):
        """Test detection of AI-generated speech patterns."""
        profile = engine.build_character_profile(sample_character)
        issues, nat_score, char_score = engine._check_line_naturalness(
            "当然，我很乐意帮助你。",
            profile
        )

        assert nat_score < 1.0

    def test_formality_inconsistency_detected(self, engine, formal_character):
        """Test detection of formality inconsistency."""
        profile = engine.build_character_profile(formal_character)
        # Using casual speech on a formal character
        issues, nat_score, char_score = engine._check_line_naturalness(
            "哈，这事儿太搞笑了！",
            profile
        )

        formality_issues = [i for i in issues if i.issue_type == DialogueNaturalnessType.FORMALITY_INCONSISTENT]
        assert len(formality_issues) > 0

    def test_short_line_detected(self, engine, sample_character):
        """Test detection of too-short dialogue lines."""
        profile = engine.build_character_profile(sample_character)
        issues, nat_score, char_score = engine._check_line_naturalness(
            "哈",
            profile
        )

        assert nat_score < 1.0

    def test_long_line_without_punctuation(self, engine, sample_character):
        """Test detection of run-on dialogue lines."""
        profile = engine.build_character_profile(sample_character)
        issues, nat_score, char_score = engine._check_line_naturalness(
            "这是一个非常长的句子没有任何标点符号来分隔它所以读起来非常困难因为它一直在说话而且没有停顿因此很难理解而且读起来很累人这确实是一个问题需要被解决而且要尽快处理因为用户可能会抱怨所以我们应该立即修复这个问题并确保类似的问题不会再次发生",
            profile
        )

        assert nat_score < 1.0


class TestCheckConversationFlow:
    """Tests for _check_conversation_flow method."""

    def test_good_flow(self, engine):
        """Test that natural conversation gets good flow score."""
        lines = [
            ("小明", "今天有什么计划？"),
            ("张三", "打算去图书馆看书。"),
            ("小明", "那我可以一起去吗？"),
            ("张三", "当然可以。"),
        ]
        score, issues = engine._check_conversation_flow(lines)

        assert score >= 0.8
        assert len(issues) == 0

    def test_short_response_after_question(self, engine):
        """Test detection of short response after question."""
        lines = [
            ("小明", "今天有什么计划？"),
            ("张三", "图书馆。"),
        ]
        score, issues = engine._check_conversation_flow(lines)

        assert score < 1.0
        response_issues = [i for i in issues if i.issue_type == DialogueNaturalnessType.RESPONSE_MISMATCH]
        assert len(response_issues) > 0


class TestAnalyzeChapterDialogue:
    """Tests for analyze_chapter_dialogue method."""

    def test_analyze_natural_chapter(self, engine, sample_chapter, sample_character, formal_character):
        """Test analysis of chapter with natural dialogue."""
        characters = [sample_character, formal_character]
        analysis = engine.analyze_chapter_dialogue(sample_chapter, characters)

        assert analysis.total_lines > 0
        assert analysis.overall_score >= 0.0
        assert analysis.naturalness_score >= 0.0
        assert analysis.character_voice_score >= 0.0

    def test_analyze_problematic_chapter(self, engine, problematic_chapter, sample_character):
        """Test analysis of chapter with problematic dialogue."""
        characters = [sample_character]
        analysis = engine.analyze_chapter_dialogue(problematic_chapter, characters)

        assert analysis.total_lines > 0
        # Should find some issues
        assert analysis.total_issues > 0

        # Should detect robotic speech
        assert "robotic_speech" in analysis.issue_summary

    def test_analyze_empty_chapter(self, engine, sample_character):
        """Test analysis of chapter with no dialogue."""
        empty_chapter = Chapter(
            id="ch_empty",
            number=99,
            title="空章节",
            content="这是一段没有任何对话的叙述文字。"
        )
        characters = [sample_character]
        analysis = engine.analyze_chapter_dialogue(empty_chapter, characters)

        assert analysis.total_lines == 0
        assert analysis.overall_score == 1.0


class TestAnalyzeNovelDialogue:
    """Tests for analyze_novel_dialogue method."""

    def test_analyze_novel(self, engine, sample_chapter, problematic_chapter, sample_character, formal_character):
        """Test analysis of entire novel."""
        novel = MagicMock(spec=Novel)
        novel.chapters = {
            "ch_001": sample_chapter,
            "ch_002": problematic_chapter,
        }

        characters = [sample_character, formal_character]
        report = engine.analyze_novel_dialogue(novel, characters)

        assert report.total_chapters_analyzed == 2
        assert report.total_dialogue_lines > 0
        assert report.total_exchanges > 0
        assert report.total_issues >= 0
        assert report.overall_naturalness_score >= 0.0
        assert report.overall_character_consistency_score >= 0.0

    def test_analyze_empty_novel(self, engine, sample_character):
        """Test analysis of novel with no chapters."""
        empty_novel = MagicMock(spec=Novel)
        empty_novel.chapters = {}
        characters = [sample_character]
        report = engine.analyze_novel_dialogue(empty_novel, characters)

        assert report.total_chapters_analyzed == 0
        assert report.total_dialogue_lines == 0


class TestCreateRevisionPlan:
    """Tests for create_revision_plan method."""

    def test_create_revision_plan(self, engine, sample_chapter, sample_character):
        """Test creating revision plan from analysis."""
        characters = [sample_character]
        analysis = engine.analyze_chapter_dialogue(sample_chapter, characters)

        revision = engine.create_revision_plan(analysis)

        assert revision.analysis_id == analysis.analysis_id
        assert isinstance(revision.priority_fixes, list)
        assert isinstance(revision.suggested_fixes, list)
        assert isinstance(revision.optional_improvements, list)
        assert isinstance(revision.character_guidance, dict)
        assert isinstance(revision.revision_focus, list)


class TestGetSummary:
    """Tests for get_summary method."""

    def test_get_summary(self, engine, sample_chapter, sample_character):
        """Test getting human-readable summary."""
        characters = [sample_character]
        analysis = engine.analyze_chapter_dialogue(sample_chapter, characters)

        # Create a minimal report for summary
        from chai.models.dialogue_naturalness import DialogueNaturalnessReport

        # Build chapter profile for the analysis
        report = DialogueNaturalnessReport(
            report_id="report_001",
            analyses=[analysis],
            total_chapters_analyzed=1,
            total_dialogue_lines=analysis.total_lines,
            total_exchanges=1,
            total_issues=analysis.total_issues,
            severe_issues=analysis.severe_issues,
        )

        summary = engine.get_summary(report)

        assert "对话自然度检查报告" in summary
        assert "检查章节数" in summary
        assert "总体自然度评分" in summary


class TestDialogueNaturalnessModels:
    """Tests for dialogue naturalness model enums."""

    def test_naturalness_type_values(self):
        """Test DialogueNaturalnessType enum values."""
        assert DialogueNaturalnessType.ROBOTIC_SPEECH.value == "robotic_speech"
        assert DialogueNaturalnessType.FORMALITY_INCONSISTENT.value == "formality_inconsistent"
        assert DialogueNaturalnessType.CHARACTER_VOICE_BREAK.value == "character_voice_break"
        assert DialogueNaturalnessType.CONVERSATION_FLOW_POOR.value == "conversation_flow_poor"

    def test_severity_values(self):
        """Test DialogueNaturalnessSeverity enum values."""
        assert DialogueNaturalnessSeverity.MINOR.value == "minor"
        assert DialogueNaturalnessSeverity.MODERATE.value == "moderate"
        assert DialogueNaturalnessSeverity.SEVERE.value == "severe"


class TestCharacterDialogueProfile:
    """Tests for CharacterDialogueProfile model."""

    def test_profile_creation(self):
        """Test creating a character dialogue profile."""
        profile = CharacterDialogueProfile(
            character_id="test_001",
            character_name="测试角色",
            speech_pattern="说话直接",
            vocabulary_level="simple",
            formality_level="casual",
            catchphrases=["就这样", "明白"],
        )

        assert profile.character_id == "test_001"
        assert profile.character_name == "测试角色"
        assert profile.catchphrases == ["就这样", "明白"]

    def test_profile_defaults(self):
        """Test profile default values."""
        profile = CharacterDialogueProfile(
            character_id="test_002",
            character_name="默认角色",
        )

        assert profile.vocabulary_level == "moderate"
        assert profile.formality_level == "neutral"
        assert profile.sentence_structure == "mixed"
        assert profile.emotional_restraint == "moderate"
        assert profile.directness == "moderate"
