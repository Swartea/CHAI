"""Unit tests for ChapterSelfCheckEngine."""

import pytest
from chai.models.chapter_self_check import (
    SelfCheckStatus,
    SelfCheckType,
    ChapterSelfCheckConfig,
    ChapterSelfCheckRequest,
)
from chai.engines.chapter_self_check_engine import ChapterSelfCheckEngine


class TestChapterSelfCheckEngine:
    """Test suite for ChapterSelfCheckEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ChapterSelfCheckEngine()

    def test_engine_initialization(self):
        """Test engine can be initialized."""
        assert self.engine is not None
        assert self.engine.config is not None
        assert isinstance(self.engine.config, ChapterSelfCheckConfig)

    def test_config_defaults(self):
        """Test default configuration values."""
        config = ChapterSelfCheckConfig()
        assert config.enable_grammar is True
        assert config.enable_sentence_quality is True
        assert config.enable_dialogue_tag is True
        assert config.enable_punctuation is True
        assert config.enable_word_count is True
        assert config.enable_foreshadowing is True
        assert config.enable_transition is True
        assert config.enable_style is True
        assert config.enable_tone is True
        assert config.enable_description_density is True
        assert config.enable_dialogue_naturalness is True
        assert config.enable_scene_vividness is True
        assert config.enable_plot_logic is True
        assert config.enable_payoff_completeness is True
        assert config.min_word_count == 2000
        assert config.max_word_count == 4000
        assert config.min_acceptable_score == 0.7

    def test_check_chapter_basic(self):
        """Test basic chapter self-check."""
        request = ChapterSelfCheckRequest(
            chapter_id="ch_001",
            chapter_number=1,
            title="第一章：开端",
            content="这是一个测试章节的内容。" * 300,  # ~3300 chars
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        assert result.chapter_id == "ch_001"
        assert result.chapter_number == 1
        assert result.status in [SelfCheckStatus.PASSED, SelfCheckStatus.WARNING, SelfCheckStatus.FAILED]
        assert result.profile is not None
        assert result.report is not None
        assert result.report.summary is not None

    def test_check_chapter_word_count_pass(self):
        """Test chapter with acceptable word count passes word count check."""
        # Create content with ~3000 characters (within 2000-4000 range)
        content = "这是第一章的内容。" * 250  # ~3000 chars

        request = ChapterSelfCheckRequest(
            chapter_id="ch_002",
            chapter_number=2,
            title="第二章：发展",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        # Find word count check result
        word_count_result = next(
            (r for r in result.profile.check_results if r.check_type == SelfCheckType.WORD_COUNT),
            None
        )
        assert word_count_result is not None
        assert word_count_result.status == SelfCheckStatus.PASSED

    def test_check_chapter_word_count_fail_short(self):
        """Test chapter with too few words fails word count check."""
        # Create content with only ~500 characters (below 2000 minimum)
        # 450 chars is far below 2000, so severity is SEVERE -> FAILED
        content = "这是很短的章节内容。" * 50  # ~450 chars

        request = ChapterSelfCheckRequest(
            chapter_id="ch_003",
            chapter_number=3,
            title="第三章：过短",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        # Find word count check result
        word_count_result = next(
            (r for r in result.profile.check_results if r.check_type == SelfCheckType.WORD_COUNT),
            None
        )
        assert word_count_result is not None
        # 450 chars is far below 2000, severity is SEVERE -> FAILED
        assert word_count_result.status == SelfCheckStatus.FAILED

    def test_check_chapter_word_count_fail_long(self):
        """Test chapter with too many words fails word count check."""
        # Create content with ~5000 characters (above 4000 maximum)
        # 5250 chars is above 4000, so severity is SEVERE -> FAILED
        content = "这是很长的章节内容需要大量填充。" * 350  # ~5250 chars

        request = ChapterSelfCheckRequest(
            chapter_id="ch_004",
            chapter_number=4,
            title="第四章：过长",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        # Find word count check result
        word_count_result = next(
            (r for r in result.profile.check_results if r.check_type == SelfCheckType.WORD_COUNT),
            None
        )
        assert word_count_result is not None
        # 5250 chars is above 4000, severity is SEVERE -> FAILED
        assert word_count_result.status == SelfCheckStatus.FAILED

    def test_check_chapter_with_context(self):
        """Test chapter with previous/next chapter context for word count check."""
        # 1600 chars is below 2000 minimum, deviation = 400/2000 = 0.2, MODERATE -> WARNING
        content = "这是主要章节内容。" * 200  # ~1600 chars - below range
        prev_content = "这是前一章的结尾内容。" * 100
        next_content = "这是后一章的开头内容。" * 100

        request = ChapterSelfCheckRequest(
            chapter_id="ch_005",
            chapter_number=5,
            title="第五章：过渡",
            content=content,
            previous_chapter_content=prev_content,
            next_chapter_content=next_content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_word_count=True,  # Only test word count
                enable_foreshadowing=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        # Find word count check result
        word_count_result = next(
            (r for r in result.profile.check_results if r.check_type == SelfCheckType.WORD_COUNT),
            None
        )
        assert word_count_result is not None
        # 1600 chars is below 2000, deviation ratio = 0.2 -> MODERATE severity -> WARNING
        assert word_count_result.status == SelfCheckStatus.WARNING

    def test_check_chapter_revision_plan_created_on_failure(self):
        """Test revision plan is created when chapter fails checks."""
        # Very short content should trigger warnings
        content = "短。" * 10  # Very short

        request = ChapterSelfCheckRequest(
            chapter_id="ch_006",
            chapter_number=6,
            title="第六章：需修订",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        # If there are warnings or failures, revision plan should be created
        if result.status in [SelfCheckStatus.FAILED, SelfCheckStatus.WARNING]:
            assert result.revision_plan is not None

    def test_check_chapter_profile_details(self):
        """Test chapter self-check profile contains correct details."""
        content = "测试章节内容。" * 150  # ~1650 chars

        request = ChapterSelfCheckRequest(
            chapter_id="ch_007",
            chapter_number=7,
            title="第七章：Profile",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        assert result.success is True
        profile = result.profile
        assert profile.chapter_id == "ch_007"
        assert profile.chapter_number == 7
        assert profile.title == "第七章：Profile"
        assert profile.checked_at is not None
        assert len(profile.check_results) >= 1  # At least word count check

    def test_self_check_types_all_defined(self):
        """Test all self-check types are properly defined."""
        expected_types = [
            SelfCheckType.GRAMMAR,
            SelfCheckType.SENTENCE_QUALITY,
            SelfCheckType.DIALOGUE_TAG,
            SelfCheckType.PUNCTUATION,
            SelfCheckType.WORD_COUNT,
            SelfCheckType.FORESHADOWING,
            SelfCheckType.TRANSITION,
            SelfCheckType.STYLE,
            SelfCheckType.TONE,
            SelfCheckType.DESCRIPTION_DENSITY,
            SelfCheckType.DIALOGUE_NATURALNESS,
            SelfCheckType.SCENE_VIVIDNESS,
            SelfCheckType.PLOT_LOGIC,
            SelfCheckType.PAYOFF_COMPLETENESS,
        ]

        for check_type in expected_types:
            assert check_type is not None

    def test_self_check_status_values(self):
        """Test self-check status enum values."""
        assert SelfCheckStatus.PENDING.value == "pending"
        assert SelfCheckStatus.IN_PROGRESS.value == "in_progress"
        assert SelfCheckStatus.PASSED.value == "passed"
        assert SelfCheckStatus.FAILED.value == "failed"
        assert SelfCheckStatus.WARNING.value == "warning"

    def test_engine_with_custom_config(self):
        """Test engine initialization with custom configuration."""
        config = ChapterSelfCheckConfig(
            enable_word_count=True,
            enable_grammar=False,
            enable_sentence_quality=False,
            min_word_count=3000,
            max_word_count=5000,
        )

        engine = ChapterSelfCheckEngine(config=config)

        assert engine.config.min_word_count == 3000
        assert engine.config.max_word_count == 5000
        assert engine.config.enable_word_count is True
        assert engine.config.enable_grammar is False

    def test_get_summary(self):
        """Test getting summary from check result."""
        content = "测试章节内容。" * 150

        request = ChapterSelfCheckRequest(
            chapter_id="ch_008",
            chapter_number=8,
            title="第八章：摘要",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)
        summary = self.engine.get_summary(result)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_overall_score_calculation(self):
        """Test overall score is calculated correctly."""
        content = "测试内容。" * 200

        request = ChapterSelfCheckRequest(
            chapter_id="ch_009",
            chapter_number=9,
            title="第九章：评分",
            content=content,
            config=ChapterSelfCheckConfig(
                enable_grammar=False,
                enable_sentence_quality=False,
                enable_dialogue_tag=False,
                enable_punctuation=False,
                enable_foreshadowing=False,
                enable_transition=False,
                enable_style=False,
                enable_tone=False,
                enable_description_density=False,
                enable_dialogue_naturalness=False,
                enable_scene_vividness=False,
                enable_plot_logic=False,
                enable_payoff_completeness=False,
            ),
        )

        result = self.engine.check_chapter(request)

        # Calculate expected average
        scores = [r.score for r in result.profile.check_results]
        expected_avg = sum(scores) / len(scores) if scores else 1.0

        assert result.profile.overall_score == pytest.approx(expected_avg, rel=0.01)
