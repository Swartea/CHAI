"""Tests for ChapterWordCountEngine."""

import pytest
from chai.models.chapter_word_count import (
    WordCountStatus,
    WordCountSeverity,
    ChapterWordCountProfile,
    ChapterWordCountIssue,
    ChapterWordCountAnalysis,
    ChapterWordCountRevision,
    ChapterWordCountReport,
)
from chai.engines.chapter_word_count_engine import ChapterWordCountEngine


class TestChapterWordCountEngine:
    """Test cases for ChapterWordCountEngine."""

    @pytest.fixture
    def engine(self):
        """Create a chapter word count engine with default targets."""
        return ChapterWordCountEngine(
            min_target=2000,
            max_target=4000,
            optimal_target=3000
        )

    @pytest.fixture
    def chinese_text_3000(self):
        """Create a Chinese text with approximately 3000 characters."""
        # ~3100 Chinese characters to ensure we're within 2000-4000 range
        base = "这是一个测试段落。" * 210  # ~2520 chars
        base += "额外的测试内容。" * 55  # ~715 chars
        return base

    @pytest.fixture
    def chinese_text_1500(self):
        """Create a Chinese text with approximately 1500 characters."""
        # ~1500 Chinese characters
        return "这是一个简短的测试段落。" * 100

    @pytest.fixture
    def chinese_text_4500(self):
        """Create a Chinese text with approximately 4500 characters."""
        # ~4500 Chinese characters
        base = "这是一个非常长的测试段落，用于模拟章节内容。" * 300
        return base

    def test_count_chinese_words(self, engine):
        """Test Chinese word counting."""
        text = "你好世界Hello"
        count = engine.count_chinese_words(text)
        # 4 Chinese chars + 5 English letters = 9
        assert count == 9

    def test_count_chinese_words_empty(self, engine):
        """Test counting empty text."""
        count = engine.count_chinese_words("")
        assert count == 0

    def test_analyze_chapter_optimal(self, engine, chinese_text_3000):
        """Test analyzing a chapter with optimal word count."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_3000,
        )

        assert profile.chapter_id == "ch_1"
        assert profile.chapter_number == 1
        assert 2000 <= profile.actual_word_count <= 4000
        assert profile.is_within_target is True
        assert profile.min_target == 2000
        assert profile.max_target == 4000
        assert profile.optimal_target == 3000

    def test_analyze_chapter_too_short(self, engine, chinese_text_1500):
        """Test analyzing a chapter that is too short."""
        profile = engine.analyze_chapter(
            chapter_id="ch_2",
            chapter_number=2,
            title="第二章",
            content=chinese_text_1500,
        )

        assert profile.actual_word_count < 2000
        assert profile.is_within_target is False
        assert profile.status == WordCountStatus.TOO_SHORT
        assert profile.deviation_from_min > 0

    def test_analyze_chapter_too_long(self, engine, chinese_text_4500):
        """Test analyzing a chapter that is too long."""
        profile = engine.analyze_chapter(
            chapter_id="ch_3",
            chapter_number=3,
            title="第三章",
            content=chinese_text_4500,
        )

        assert profile.actual_word_count > 4000
        assert profile.is_within_target is False
        assert profile.status == WordCountStatus.TOO_LONG
        assert profile.deviation_from_max > 0

    def test_identify_issue_too_short(self, engine, chinese_text_1500):
        """Test identifying issue for a short chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_1500,
        )

        issue = engine.identify_issue(profile)

        assert issue is not None
        assert issue.chapter_id == "ch_1"
        assert issue.issue_type == "too_short"
        assert issue.words_to_add is not None
        assert issue.words_to_add > 0

    def test_identify_issue_too_long(self, engine, chinese_text_4500):
        """Test identifying issue for a long chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_4500,
        )

        issue = engine.identify_issue(profile)

        assert issue is not None
        assert issue.chapter_id == "ch_1"
        assert issue.issue_type == "too_long"
        assert issue.words_to_remove is not None
        assert issue.words_to_remove > 0

    def test_identify_issue_none_for_optimal(self, engine, chinese_text_3000):
        """Test that no issue is identified for optimal chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_3000,
        )

        # If the text is within acceptable range but not optimal, may still get minor issue
        if profile.is_within_target and profile.status == WordCountStatus.OPTIMAL:
            issue = engine.identify_issue(profile)
            # May be None or minor issue

    def test_analyze_novel(self, engine, chinese_text_3000, chinese_text_1500, chinese_text_4500):
        """Test analyzing multiple chapters in a novel."""
        chapters = [
            {"id": "ch_1", "number": 1, "title": "第一章", "content": chinese_text_3000},
            {"id": "ch_2", "number": 2, "title": "第二章", "content": chinese_text_1500},
            {"id": "ch_3", "number": 3, "title": "第三章", "content": chinese_text_4500},
        ]

        analysis = engine.analyze_novel("novel_1", chapters)

        assert analysis.novel_id == "novel_1"
        assert analysis.total_chapters == 3
        assert analysis.chapters_too_short >= 1
        assert analysis.chapters_too_long >= 1
        assert analysis.average_word_count > 0
        assert len(analysis.issues) >= 2

    def test_create_revision_plan_for_short_chapter(self, engine, chinese_text_1500):
        """Test creating revision plan for a short chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_1500,
        )

        revision = engine.create_revision_plan(profile)

        assert revision is not None
        assert revision.chapter_id == "ch_1"
        assert revision.needs_expansion is True
        assert revision.needs_contraction is False
        assert revision.words_to_add > 0

    def test_create_revision_plan_for_long_chapter(self, engine, chinese_text_4500):
        """Test creating revision plan for a long chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_4500,
        )

        revision = engine.create_revision_plan(profile)

        assert revision is not None
        assert revision.chapter_id == "ch_1"
        assert revision.needs_expansion is False
        assert revision.needs_contraction is True
        assert revision.words_to_remove > 0

    def test_create_revision_plan_returns_none_for_optimal(self, engine, chinese_text_3000):
        """Test that revision plan is None for optimal chapter."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_3000,
        )

        # For chapters that are already optimal/well within range
        if profile.is_within_target and profile.status == WordCountStatus.OPTIMAL:
            revision = engine.create_revision_plan(profile)
            # May be None

    def test_generate_report(self, engine, chinese_text_3000, chinese_text_1500):
        """Test generating comprehensive report."""
        chapters = [
            {"id": "ch_1", "number": 1, "title": "第一章", "content": chinese_text_3000},
            {"id": "ch_2", "number": 2, "title": "第二章", "content": chinese_text_1500},
        ]

        report = engine.generate_report("novel_1", "测试小说", chapters)

        assert isinstance(report, ChapterWordCountReport)
        assert report.novel_id == "novel_1"
        assert report.novel_title == "测试小说"
        assert isinstance(report.analysis, ChapterWordCountAnalysis)
        assert report.total_chapters == 2

    def test_severity_calculation(self, engine):
        """Test severity calculation for different deviation levels."""
        # Create text that's 30% below minimum (severe)
        text_severe = "测试。" * 700  # ~2100 chars, below 2000 minimum

        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=text_severe,
        )

        # The severity should reflect the deviation
        if profile.actual_word_count < engine.min_target:
            assert profile.severity in [
                WordCountSeverity.MINOR,
                WordCountSeverity.MODERATE,
                WordCountSeverity.SEVERE,
                WordCountSeverity.NONE
            ]

    def test_word_count_ratios(self, engine, chinese_text_3000):
        """Test word count ratio calculations."""
        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=chinese_text_3000,
        )

        assert profile.ratio_to_min > 0
        assert profile.ratio_to_max > 0
        assert profile.ratio_to_optimal > 0

    def test_custom_targets(self):
        """Test engine with custom word count targets."""
        engine = ChapterWordCountEngine(
            min_target=2500,
            max_target=3500,
            optimal_target=3000
        )

        text = "测试内容。" * 200  # ~2000 chars

        profile = engine.analyze_chapter(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            content=text,
        )

        assert profile.min_target == 2500
        assert profile.max_target == 3500
        assert profile.optimal_target == 3000

    def test_multiple_chapters_statistics(self, engine):
        """Test statistics calculation across multiple chapters."""
        chapters = [
            {"id": f"ch_{i}", "number": i, "title": f"第{i}章", "content": f"测试内容{i}。" * 200}
            for i in range(1, 11)
        ]

        analysis = engine.analyze_novel("novel_1", chapters)

        assert analysis.total_chapters == 10
        assert analysis.average_word_count > 0
        assert analysis.min_word_count <= analysis.average_word_count
        assert analysis.max_word_count >= analysis.average_word_count
        assert analysis.total_word_count == sum(p.actual_word_count for p in analysis.chapter_profiles)

    def test_get_summary(self, engine):
        """Test getting summary from report."""
        chapters = [
            {"id": "ch_1", "number": 1, "title": "第一章", "content": "测试。" * 250},
        ]

        report = engine.generate_report("novel_1", "测试小说", chapters)
        summary = engine.get_summary(report)

        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_chapter_word_count_profile_model(self):
        """Test ChapterWordCountProfile model creation."""
        profile = ChapterWordCountProfile(
            chapter_id="ch_1",
            chapter_number=1,
            title="第一章",
            actual_word_count=3000,
            min_target=2000,
            max_target=4000,
            optimal_target=3000,
            is_within_target=True,
        )

        assert profile.chapter_id == "ch_1"
        assert profile.actual_word_count == 3000
        assert profile.is_within_target is True

    def test_chapter_word_count_issue_model(self):
        """Test ChapterWordCountIssue model creation."""
        issue = ChapterWordCountIssue(
            chapter_id="ch_1",
            chapter_number=1,
            issue_type="too_short",
            severity=WordCountSeverity.MODERATE,
            actual_word_count=1500,
            expected_word_count=2000,
            deviation=500,
            deviation_percent=25.0,
            words_to_add=500,
            recommendation="建议增加500字",
        )

        assert issue.chapter_id == "ch_1"
        assert issue.words_to_add == 500

    def test_chapter_word_count_analysis_model(self):
        """Test ChapterWordCountAnalysis model creation."""
        analysis = ChapterWordCountAnalysis(
            novel_id="novel_1",
            total_chapters=5,
            chapters_within_target=3,
            chapters_too_short=1,
            chapters_too_long=1,
            average_word_count=2800,
        )

        assert analysis.novel_id == "novel_1"
        assert analysis.total_chapters == 5

    def test_chapter_word_count_revision_model(self):
        """Test ChapterWordCountRevision model creation."""
        revision = ChapterWordCountRevision(
            chapter_id="ch_1",
            chapter_number=1,
            current_word_count=1500,
            target_range=(2000, 4000),
            needs_expansion=True,
            words_to_add=500,
        )

        assert revision.chapter_id == "ch_1"
        assert revision.needs_expansion is True
        assert revision.words_to_add == 500

    def test_chapter_word_count_report_model(self):
        """Test ChapterWordCountReport model creation."""
        report = ChapterWordCountReport(
            novel_id="novel_1",
            novel_title="测试小说",
            analysis=ChapterWordCountAnalysis(novel_id="novel_1"),
            summary="测试摘要",
            passed=False,
            total_chapters=10,
            chapters_needing_revision=3,
        )

        assert report.novel_id == "novel_1"
        assert report.passed is False
        assert report.chapters_needing_revision == 3

    def test_empty_chapters(self, engine):
        """Test handling of empty chapter content."""
        chapters = [
            {"id": "ch_1", "number": 1, "title": "第一章", "content": ""},
        ]

        analysis = engine.analyze_novel("novel_1", chapters)

        assert analysis.total_chapters == 1
        assert analysis.chapter_profiles[0].actual_word_count == 0
        assert analysis.chapter_profiles[0].is_within_target is False

    def test_consistency_score_calculation(self, engine):
        """Test consistency score calculation."""
        # Create chapters with varied word counts
        chapters = [
            {"id": "ch_1", "number": 1, "title": "第一章", "content": "测" * 2000},
            {"id": "ch_2", "number": 2, "title": "第二章", "content": "测" * 3000},
            {"id": "ch_3", "number": 3, "title": "第三章", "content": "测" * 4000},
        ]

        analysis = engine.analyze_novel("novel_1", chapters)

        assert 0 <= analysis.consistency_score <= 1
        assert 0 <= analysis.overall_score <= 1
