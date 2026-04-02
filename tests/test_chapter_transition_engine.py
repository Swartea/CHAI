"""Tests for chapter transition engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chai.models import Novel, Volume, Chapter
from chai.models.chapter_transition import (
    TransitionType,
    TransitionQuality,
    TransitionSmoothness,
    ChapterEndingType,
    ChapterOpeningType,
    TransitionElement,
    ChapterTransitionProfile,
    TransitionIssue,
    TransitionConnection,
    TransitionAnalysis,
    TransitionRevision,
    TransitionPlan,
    TransitionReport,
)
from chai.engines.chapter_transition_engine import ChapterTransitionEngine
from chai.services import AIService


class TestChapterTransitionEngine:
    """Tests for ChapterTransitionEngine."""

    def test_analyze_chapter_ending_basic(self):
        """Test basic chapter ending analysis."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个紧张的场景。英雄面对着危机，必须做出关键决定。就在此时，敌人突然出现。",
            word_count=200,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        ending_type, tension, emotion = engine.analyze_chapter_ending(chapter)

        assert ending_type is not None
        assert isinstance(ending_type, ChapterEndingType)
        assert 0 <= tension <= 1
        assert emotion in ["positive", "negative", "neutral"]

    def test_analyze_chapter_ending_cliffhanger(self):
        """Test detecting cliffhanger ending."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="悬念",
            content="就在此时，突然一声巨响。他转头看去，刹那间一切都变了。命悬一线的时刻来临。紧张危机四伏，心跳加速，屏息以待。",
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        ending_type, tension, emotion = engine.analyze_chapter_ending(chapter)

        # Should detect high tension markers
        assert tension > 0.3

    def test_analyze_chapter_ending_quiet(self):
        """Test detecting quiet ending."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="平静",
            content="一切归于平静。夕阳渐渐落下，村庄恢复了往日的宁静。人们安然入睡，期待着明天的到来。",
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        ending_type, tension, emotion = engine.analyze_chapter_ending(chapter)

        assert ending_type == ChapterEndingType.QUIET_ENDING
        assert tension < 0.5

    def test_analyze_chapter_opening_basic(self):
        """Test basic chapter opening analysis."""
        chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="第二天清晨，阳光洒在窗台上。他睁开眼，回想起昨天发生的一切。",
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        opening_type, tension, emotion = engine.analyze_chapter_opening(chapter)

        assert opening_type is not None
        assert isinstance(opening_type, ChapterOpeningType)
        assert 0 <= tension <= 1

    def test_analyze_chapter_opening_time_marker(self):
        """Test detecting time marker in opening."""
        chapter = Chapter(
            id="ch_2",
            number=2,
            title="数日后",
            content="数日后，他变得更强了。敌人依然环伺。",
            word_count=50,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        opening_type, tension, emotion = engine.analyze_chapter_opening(chapter)

        # Should detect time marker
        assert opening_type == ChapterOpeningType.TIME_MARKER

    def test_analyze_chapter_opening_direct_continuation(self):
        """Test detecting direct continuation."""
        chapter = Chapter(
            id="ch_2",
            number=2,
            title="继续",
            content="接着昨天的经历，他继续前行。然而，事情并没有想象中那么简单。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        opening_type, tension, emotion = engine.analyze_chapter_opening(chapter)

        assert opening_type == ChapterOpeningType.DIRECT_CONTINUATION

    def test_detect_time_jump(self):
        """Test time jump detection."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="夜幕降临，战斗终于结束。",
            word_count=50,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="第二天清晨，阳光洒在战场上。废墟中，他站了起来。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        has_jump = engine.detect_time_jump(from_chapter, to_chapter)
        assert has_jump is True

    def test_detect_no_time_jump(self):
        """Test when there's no time jump."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="他走出房间，来到了走廊。",
            word_count=50,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="接着，他推开了走廊尽头的门。",
            word_count=50,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        has_jump = engine.detect_time_jump(from_chapter, to_chapter)
        assert has_jump is False

    def test_detect_location_change(self):
        """Test location change detection."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="他在森林中迷了路。",
            word_count=50,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="来到城堡门口，他看到了那扇巨大的门。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        has_change = engine.detect_location_change(from_chapter, to_chapter)
        assert has_change is True

    def test_analyze_transition_elements(self):
        """Test analyzing transition elements."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="夜幕降临，战斗终于结束。他疲惫地靠在废墟上。",
            word_count=80,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="来到城堡门口，他看到了那扇巨大的门。门缓缓打开。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        elements = engine.analyze_transition_elements(from_chapter, to_chapter)

        assert elements is not None
        assert isinstance(elements, TransitionElement)
        # Scene continuity should be low since there's a location change

    def test_analyze_transition_quality_good(self):
        """Test good transition quality assessment."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="他走在路上，心情愉快。",
            word_count=50,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="接着，他继续向前走去。",
            word_count=50,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        elements = engine.analyze_transition_elements(from_chapter, to_chapter)
        quality, smoothness, consistency = engine.assess_transition_quality(
            from_chapter, to_chapter, elements
        )

        assert quality in [TransitionQuality.EXCELLENT, TransitionQuality.GOOD, TransitionQuality.ACCEPTABLE]
        assert 0 <= consistency <= 1

    def test_analyze_transition_single_chapters(self):
        """Test analyzing transition between two chapters."""
        from_chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个紧张而充满悬念的结尾。紧张危机四伏，刹那之间。",
            word_count=100,
        )
        to_chapter = Chapter(
            id="ch_2",
            number=2,
            title="第二章",
            content="第二天清晨，阳光洒在战场上。来到城堡门前，危险从未远去。",
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        profile = engine.analyze_transition(from_chapter, to_chapter)

        assert profile is not None
        assert isinstance(profile, ChapterTransitionProfile)
        assert profile.from_chapter_number == 1
        assert profile.to_chapter_number == 2
        assert profile.transition_type in TransitionType
        assert profile.quality in TransitionQuality
        assert 0 <= profile.consistency_score <= 1

    def test_analyze_all_transitions(self):
        """Test analyzing all transitions in a list of chapters."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="第一天，他出发了。", word_count=50),
            Chapter(id="ch_2", number=2, title="第二章", content="第二天，他继续前行。", word_count=50),
            Chapter(id="ch_3", number=3, title="第三章", content="第三天，他到达了目的地。", word_count=50),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        analysis = engine.analyze_all_transitions(chapters)

        assert analysis is not None
        assert isinstance(analysis, TransitionAnalysis)
        assert analysis.total_transitions == 2
        assert len(analysis.transition_profiles) == 2
        assert len(analysis.connections) == 2
        assert 0 <= analysis.overall_transition_score <= 1

    def test_analyze_all_transitions_single_chapter(self):
        """Test analyzing transitions with single chapter."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", content="唯一的一章。", word_count=20),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        analysis = engine.analyze_all_transitions(chapters)

        assert analysis.total_transitions == 0

    def test_analyze_novel_transitions(self):
        """Test analyzing all transitions in a novel."""
        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[
                Volume(
                    id="vol_1",
                    number=1,
                    title="第一卷",
                    chapters=[
                        Chapter(id="ch_1", number=1, title="第一章", content="他开始了旅程。", word_count=30),
                        Chapter(id="ch_2", number=2, title="第二章", content="数日后，他来到了边境。", word_count=30),
                        Chapter(id="ch_3", number=3, title="第三章", content="夜幕降临，他进入了城堡。", word_count=30),
                    ],
                ),
            ],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        analysis = engine.analyze_novel_transitions(novel)

        assert analysis is not None
        assert analysis.total_transitions == 2
        assert len(analysis.transition_profiles) == 2

    def test_create_revision_plan(self):
        """Test creating revision plan."""
        analysis = TransitionAnalysis(
            total_transitions=3,
            overall_transition_score=0.75,
            transition_profiles=[
                ChapterTransitionProfile(
                    from_chapter_number=1,
                    to_chapter_number=2,
                    from_ending_type=ChapterEndingType.CLIFFHANGER,
                    from_tension_level=0.8,
                    from_emotional_tone="negative",
                    to_opening_type=ChapterOpeningType.TIME_MARKER,
                    to_tension_level=0.3,
                    to_emotional_tone="neutral",
                    transition_type=TransitionType.TIME_JUMP,
                    transition_elements=TransitionElement(
                        time_continuity=0.3,
                        scene_continuity=0.8,
                    ),
                    quality=TransitionQuality.ROUGH,
                    smoothness=TransitionSmoothness.ABRUPT,
                    consistency_score=0.5,
                    issues=["时间跳跃未被明确说明"],
                    recommendations=["添加时间过渡说明"],
                ),
                ChapterTransitionProfile(
                    from_chapter_number=2,
                    to_chapter_number=3,
                    from_ending_type=ChapterEndingType.RESOLUTION,
                    from_tension_level=0.3,
                    from_emotional_tone="neutral",
                    to_opening_type=ChapterOpeningType.DIRECT_CONTINUATION,
                    to_tension_level=0.3,
                    to_emotional_tone="neutral",
                    transition_type=TransitionType.SCENE_CONTINUATION,
                    transition_elements=TransitionElement(),
                    quality=TransitionQuality.GOOD,
                    smoothness=TransitionSmoothness.GRADUAL,
                    consistency_score=0.9,
                    issues=[],
                    recommendations=["过渡质量良好"],
                ),
            ],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        plan = engine.create_revision_plan(analysis, target_score=0.85)

        assert plan is not None
        assert isinstance(plan, TransitionPlan)
        assert len(plan.transitions_to_revise) == 1
        assert plan.transitions_to_revise[0] == (1, 2)
        assert plan.estimated_revisions == 1

    def test_generate_transition_report(self):
        """Test generating transition report."""
        analysis = TransitionAnalysis(
            total_transitions=2,
            overall_transition_score=0.8,
            excellent_transitions=1,
            good_transitions=1,
            acceptable_transitions=0,
            rough_transitions=0,
            jarring_transitions=0,
            average_consistency=0.85,
            weakest_transitions=[],
            critical_issues=[],
            recommendations=["章节过渡整体流畅"],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        report = engine.generate_transition_report(analysis)

        assert report is not None
        assert isinstance(report, TransitionReport)
        assert report.summary is not None
        assert len(report.summary) > 0
        assert report.revision_plan is not None

    def test_get_transition_summary(self):
        """Test getting human-readable transition summary."""
        profile = ChapterTransitionProfile(
            from_chapter_number=1,
            from_chapter_title="第一章",
            to_chapter_number=2,
            to_chapter_title="第二章",
            from_ending_type=ChapterEndingType.CLIFFHANGER,
            from_tension_level=0.8,
            from_emotional_tone="negative",
            to_opening_type=ChapterOpeningType.TIME_MARKER,
            to_tension_level=0.3,
            to_emotional_tone="neutral",
            transition_type=TransitionType.TIME_JUMP,
            transition_elements=TransitionElement(),
            quality=TransitionQuality.GOOD,
            smoothness=TransitionSmoothness.GRADUAL,
            consistency_score=0.85,
            issues=[],
            recommendations=[],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        summary = engine.get_transition_summary(profile)

        assert summary is not None
        assert isinstance(summary, str)
        assert "第1章→第2章" in summary
        assert "0.85" in summary

    def test_determine_transition_type(self):
        """Test determining transition type."""
        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        # Test time jump
        elements_time = TransitionElement(time_continuity=0.2, scene_continuity=0.8)
        from_ch = Chapter(id="ch1", number=1, title="ch1", content="content", word_count=50)
        to_ch = Chapter(id="ch2", number=2, title="ch2", content="content", word_count=50)
        transition_type = engine.determine_transition_type(from_ch, to_ch, elements_time)
        assert transition_type == TransitionType.TIME_JUMP

        # Test scene switch
        elements_scene = TransitionElement(time_continuity=1.0, scene_continuity=0.3)
        transition_type = engine.determine_transition_type(from_ch, to_ch, elements_scene)
        assert transition_type == TransitionType.SCENE_SWITCH

        # Test emotional shift
        elements_emotion = TransitionElement(
            time_continuity=1.0,
            scene_continuity=1.0,
            emotional_continuity=0.3,
            tension_flow=0.35,
        )
        transition_type = engine.determine_transition_type(from_ch, to_ch, elements_emotion)
        assert transition_type == TransitionType.EMOTIONAL_SHIFT

    def test_identify_issues(self):
        """Test identifying transition issues."""
        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        from_ch = Chapter(id="ch1", number=1, title="ch1", content="content", word_count=50)
        to_ch = Chapter(id="ch2", number=2, title="ch2", content="content", word_count=50)

        elements_bad = TransitionElement(
            time_continuity=0.2,
            time_gap_acknowledged=False,
            scene_continuity=0.3,
            location_clear=False,
            character_continuity=0.3,
            emotional_continuity=0.3,
            tension_flow=0.3,
        )

        issues = engine._identify_issues(
            from_ch, to_ch, elements_bad, TransitionQuality.JARRING
        )

        assert len(issues) > 0

    def test_generate_recommendations(self):
        """Test generating recommendations."""
        mock_ai = MagicMock(spec=AIService)
        engine = ChapterTransitionEngine(mock_ai)

        elements = TransitionElement(
            time_continuity=0.3,
            scene_continuity=0.3,
        )

        recommendations = engine._generate_recommendations(
            elements, TransitionQuality.ROUGH, TransitionType.TIME_JUMP
        )

        assert len(recommendations) > 0
        assert any("时间" in rec for rec in recommendations)

    def test_model_enums(self):
        """Test that all model enums are properly defined."""
        # Test TransitionType
        assert len(TransitionType) == 10
        assert TransitionType.SCENE_CONTINUATION is not None
        assert TransitionType.TIME_JUMP is not None

        # Test TransitionQuality
        assert len(TransitionQuality) == 5
        assert TransitionQuality.EXCELLENT is not None
        assert TransitionQuality.JARRING is not None

        # Test TransitionSmoothness
        assert len(TransitionSmoothness) == 4
        assert TransitionSmoothness.SEAMLESS is not None
        assert TransitionSmoothness.CONFUSING is not None

        # Test ChapterEndingType
        assert len(ChapterEndingType) == 8
        assert ChapterEndingType.CLIFFHANGER is not None
        assert ChapterEndingType.RESOLUTION is not None

        # Test ChapterOpeningType
        assert len(ChapterOpeningType) == 8
        assert ChapterOpeningType.DIRECT_CONTINUATION is not None
        assert ChapterOpeningType.TIME_MARKER is not None

    def test_model_fields(self):
        """Test that model fields are properly defined."""
        profile = ChapterTransitionProfile(
            from_chapter_number=1,
            from_chapter_title="第一章",
            to_chapter_number=2,
            to_chapter_title="第二章",
            transition_type=TransitionType.SCENE_CONTINUATION,
            quality=TransitionQuality.GOOD,
            smoothness=TransitionSmoothness.GRADUAL,
            consistency_score=0.85,
        )

        assert profile.from_chapter_number == 1
        assert profile.to_chapter_number == 2
        assert profile.consistency_score == 0.85

        revision = TransitionRevision(
            from_chapter=1,
            to_chapter=2,
            before_score=0.6,
            after_score=0.85,
        )

        assert revision.from_chapter == 1
        assert revision.before_score == 0.6
        assert revision.after_score == 0.85
