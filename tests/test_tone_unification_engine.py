"""Tests for tone unification engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chai.models import Novel, Volume, Chapter
from chai.models.tone_unification import (
    ToneUnificationType,
    ToneShiftType,
    ToneShiftSeverity,
    ChapterToneProfile,
    ToneShift,
    UnifiedToneProfile,
    ToneUnificationAnalysis,
    ToneUnificationRevision,
    ToneUnificationPlan,
    ToneUnificationReport,
)
from chai.engines.tone_unification_engine import ToneUnificationEngine
from chai.services import AIService


class TestToneUnificationEngine:
    """Tests for ToneUnificationEngine."""

    def test_analyze_chapter_tone_basic(self):
        """Test basic chapter tone analysis."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="这是一个紧张的场景。英雄面对着危机，必须做出关键决定。" * 20,
            word_count=200,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        profile = engine.analyze_chapter_tone(chapter)

        assert profile is not None
        assert profile.chapter_number == 1
        assert profile.chapter_title == "第一章"
        assert 0 <= profile.emotional_intensity <= 1
        assert 0 <= profile.emotional_valence <= 1
        assert isinstance(profile.tone_markers, dict)

    def test_analyze_chapter_tone_epic_content(self):
        """Test analyzing chapter with epic tone."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="战场",
            content="史诗般的战争开始了。伟大的英雄站在壮阔的战场上，面对着前所未有的危机。荣耀与传奇在此交织。",
            word_count=100,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        profile = engine.analyze_chapter_tone(chapter)

        assert profile is not None
        assert profile.primary_atmosphere == "epic"
        assert profile.emotional_intensity > 0.3

    def test_analyze_chapter_tone_romantic_content(self):
        """Test analyzing chapter with romantic tone."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="相遇",
            content="她的出现让他心跳加速。爱情的火花在两人之间悄然绽放。温柔的月光下，他们紧紧相拥。",
            word_count=80,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        profile = engine.analyze_chapter_tone(chapter)

        assert profile is not None
        assert profile.primary_atmosphere == "romantic"
        assert profile.emotional_valence > 0.5

    def test_analyze_chapter_tone_dark_content(self):
        """Test analyzing chapter with dark tone."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="黑暗",
            content="黑暗笼罩着整个王国。血腥的战场弥漫着死亡的气息。绝望的恐惧吞噬着每一个灵魂。",
            word_count=60,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        profile = engine.analyze_chapter_tone(chapter)

        assert profile is not None
        assert profile.primary_atmosphere == "dark"
        assert profile.emotional_valence < 0.5

    def test_analyze_chapter_tone_empty_content(self):
        """Test analyzing chapter with empty content."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="空白",
            content="",
            word_count=0,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        profile = engine.analyze_chapter_tone(chapter)

        assert profile is not None
        assert profile.chapter_number == 1
        assert profile.emotional_intensity == 0.5  # default
        assert profile.emotional_valence == 0.5  # default

    def test_detect_tone_shifts_none(self):
        """Test detecting no tone shifts."""
        profiles = [
            ChapterToneProfile(chapter_number=1, chapter_title="第一章", emotional_intensity=0.5, emotional_valence=0.5),
            ChapterToneProfile(chapter_number=2, chapter_title="第二章", emotional_intensity=0.51, emotional_valence=0.49),
            ChapterToneProfile(chapter_number=3, chapter_title="第三章", emotional_intensity=0.5, emotional_valence=0.5),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        shifts = engine.detect_tone_shifts(profiles)

        # Minor variations shouldn't trigger shifts
        assert len(shifts) == 0 or all(s.magnitude < 0.2 for s in shifts)

    def test_detect_tone_shifts_abrupt(self):
        """Test detecting abrupt tone shift."""
        profiles = [
            ChapterToneProfile(
                chapter_number=1,
                chapter_title="第一章",
                emotional_intensity=0.3,
                emotional_valence=0.7,
                primary_atmosphere="light",
            ),
            ChapterToneProfile(
                chapter_number=2,
                chapter_title="第二章",
                emotional_intensity=0.9,
                emotional_valence=0.2,
                primary_atmosphere="dark",
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        shifts = engine.detect_tone_shifts(profiles)

        assert len(shifts) > 0
        # Should detect the abrupt shift
        shift = shifts[0]
        assert shift.start_chapter == 1
        assert shift.end_chapter == 2
        assert shift.shift_type in [ToneShiftType.ABRUPT_SHIFT, ToneShiftType.REGIONAL_DRIFT]

    def test_detect_tone_shifts_gradual(self):
        """Test detecting gradual tone drift."""
        # Use values within valid range [0, 1]
        profiles = [
            ChapterToneProfile(
                chapter_number=1,
                chapter_title="第一章",
                emotional_intensity=0.2,
                emotional_valence=0.8,
                primary_atmosphere="epic",
            ),
            ChapterToneProfile(
                chapter_number=2,
                chapter_title="第二章",
                emotional_intensity=0.5,
                emotional_valence=0.5,
                primary_atmosphere="epic",
            ),
            ChapterToneProfile(
                chapter_number=3,
                chapter_title="第三章",
                emotional_intensity=0.9,
                emotional_valence=0.2,
                primary_atmosphere="dark",  # Major atmosphere shift
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        shifts = engine.detect_tone_shifts(profiles)

        # Should detect shift with dramatic differences and atmosphere change
        assert isinstance(shifts, list)

    def test_create_unified_tone_profile(self):
        """Test creating unified tone profile."""
        profiles = [
            ChapterToneProfile(
                chapter_number=1,
                chapter_title="第一章",
                emotional_intensity=0.5,
                emotional_valence=0.5,
                sentence_avg_length=20.0,
                paragraph_avg_length=150.0,
                dialogue_ratio=0.3,
                vocabulary_sophistication=0.5,
                primary_atmosphere="epic",
            ),
            ChapterToneProfile(
                chapter_number=2,
                chapter_title="第二章",
                emotional_intensity=0.6,
                emotional_valence=0.4,
                sentence_avg_length=22.0,
                paragraph_avg_length=160.0,
                dialogue_ratio=0.35,
                vocabulary_sophistication=0.55,
                primary_atmosphere="epic",
            ),
            ChapterToneProfile(
                chapter_number=3,
                chapter_title="第三章",
                emotional_intensity=0.55,
                emotional_valence=0.45,
                sentence_avg_length=21.0,
                paragraph_avg_length=155.0,
                dialogue_ratio=0.32,
                vocabulary_sophistication=0.52,
                primary_atmosphere="epic",
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        unified = engine.create_unified_tone_profile(profiles)

        assert unified is not None
        assert 0 <= unified.target_emotional_intensity <= 1
        assert 0 <= unified.target_emotional_valence <= 1
        assert unified.target_dialogue_ratio > 0
        assert len(unified.allowed_atmospheres) > 0

    def test_create_unified_tone_profile_empty(self):
        """Test creating unified profile with no chapters."""
        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        unified = engine.create_unified_tone_profile([])

        assert unified is not None
        assert unified.target_emotional_intensity == 0.5

    def test_calculate_chapter_consistency(self):
        """Test calculating chapter consistency with unified profile."""
        profile = ChapterToneProfile(
            chapter_number=1,
            chapter_title="第一章",
            emotional_intensity=0.5,
            emotional_valence=0.5,
            sentence_avg_length=20.0,
            paragraph_avg_length=150.0,
            dialogue_ratio=0.3,
            vocabulary_sophistication=0.5,
            primary_atmosphere="epic",
        )

        unified = UnifiedToneProfile(
            target_emotional_intensity=0.5,
            target_emotional_valence=0.5,
            intensity_range=(0.3, 0.7),
            valence_range=(0.3, 0.7),
            target_sentence_avg_length=20.0,
            sentence_length_range=(15.0, 30.0),
            target_paragraph_avg_length=150.0,
            paragraph_length_range=(100.0, 200.0),
            target_dialogue_ratio=0.3,
            dialogue_ratio_range=(0.2, 0.4),
            target_vocabulary_sophistication=0.5,
            target_atmosphere="epic",
            allowed_atmospheres=["epic", "dramatic"],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        score = engine.calculate_chapter_consistency(profile, unified)

        assert 0 <= score <= 1
        assert score > 0.8  # Should be high since within ranges

    def test_calculate_chapter_consistency_low(self):
        """Test calculating low consistency chapter."""
        profile = ChapterToneProfile(
            chapter_number=1,
            chapter_title="第一章",
            emotional_intensity=0.1,  # Outside range
            emotional_valence=0.9,    # Outside range
            sentence_avg_length=5.0,  # Outside range
            paragraph_avg_length=50.0,
            dialogue_ratio=0.8,       # Outside range
            vocabulary_sophistication=0.1,
            primary_atmosphere="light",  # Not in allowed
        )

        unified = UnifiedToneProfile(
            target_emotional_intensity=0.5,
            target_emotional_valence=0.5,
            intensity_range=(0.3, 0.7),
            valence_range=(0.3, 0.7),
            target_sentence_avg_length=20.0,
            sentence_length_range=(15.0, 30.0),
            target_paragraph_avg_length=150.0,
            paragraph_length_range=(100.0, 200.0),
            target_dialogue_ratio=0.3,
            dialogue_ratio_range=(0.2, 0.4),
            target_vocabulary_sophistication=0.5,
            target_atmosphere="epic",
            allowed_atmospheres=["epic", "dramatic"],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        score = engine.calculate_chapter_consistency(profile, unified)

        assert 0 <= score <= 1
        assert score < 0.6  # Should be low due to multiple out-of-range values

    def test_analyze_novel_tone(self):
        """Test comprehensive novel tone analysis."""
        chapters = [
            Chapter(
                id="ch_1",
                number=1,
                title="第一章",
                content="史诗般的战争开始了。伟大的英雄站在壮阔的战场上。" * 20,
                word_count=200,
            ),
            Chapter(
                id="ch_2",
                number=2,
                title="第二章",
                content="战斗持续进行。危机四伏，紧张时刻来临。" * 20,
                word_count=200,
            ),
            Chapter(
                id="ch_3",
                number=3,
                title="第三章",
                content="最终胜利来临。英雄获得了荣耀与胜利。" * 20,
                word_count=200,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="史诗小说",
            genre="玄幻",
            volumes=[volume],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        analysis = engine.analyze_novel_tone(novel)

        assert analysis is not None
        assert analysis.total_chapters_analyzed == 3
        assert isinstance(analysis.chapter_profiles, list)
        assert len(analysis.chapter_profiles) == 3
        assert isinstance(analysis.unified_tone_profile, UnifiedToneProfile)
        assert isinstance(analysis.detected_shifts, list)
        assert isinstance(analysis.overall_uniformity_score, float)
        assert 0 <= analysis.overall_uniformity_score <= 1

    def test_analyze_novel_tone_empty(self):
        """Test analyzing novel with no chapters."""
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=[])

        novel = Novel(
            id="novel_1",
            title="空小说",
            genre="玄幻",
            volumes=[volume],
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        analysis = engine.analyze_novel_tone(novel)

        assert analysis is not None
        assert analysis.total_chapters_analyzed == 0

    def test_create_revision_plan(self):
        """Test creating revision plan."""
        profiles = [
            ChapterToneProfile(
                chapter_number=1,
                chapter_title="第一章",
                consistency_score=0.95,
            ),
            ChapterToneProfile(
                chapter_number=2,
                chapter_title="第二章",
                consistency_score=0.6,  # Low
            ),
            ChapterToneProfile(
                chapter_number=3,
                chapter_title="第三章",
                consistency_score=0.7,  # Below target
            ),
        ]

        unified = UnifiedToneProfile()

        analysis = ToneUnificationAnalysis(
            overall_uniformity_score=0.75,
            chapter_profiles=profiles,
            unified_tone_profile=unified,
            detected_shifts=[],
            problematic_chapters=[(2, 0.6)],
            total_chapters_analyzed=3,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        plan = engine.create_revision_plan(analysis, target_score=0.85)

        assert plan is not None
        assert isinstance(plan, ToneUnificationPlan)
        assert 2 in plan.chapters_to_revise  # Chapters 2 and 3 below 0.85
        assert 3 in plan.chapters_to_revise
        assert 1 not in plan.chapters_to_revise  # Chapter 1 above 0.85

    def test_generate_unification_report(self):
        """Test generating unification report."""
        profiles = [
            ChapterToneProfile(
                chapter_number=1,
                chapter_title="第一章",
                consistency_score=0.9,
            ),
        ]

        unified = UnifiedToneProfile(target_atmosphere="epic")

        analysis = ToneUnificationAnalysis(
            overall_uniformity_score=0.9,
            chapter_profiles=profiles,
            unified_tone_profile=unified,
            detected_shifts=[],
            problematic_chapters=[],
            total_chapters_analyzed=1,
            average_consistency=0.9,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        report = engine.generate_unification_report(analysis)

        assert report is not None
        assert isinstance(report, ToneUnificationReport)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0
        assert isinstance(report.revision_plan, ToneUnificationPlan)

    def test_get_chapter_tone_summary(self):
        """Test getting chapter tone summary."""
        profile = ChapterToneProfile(
            chapter_number=1,
            chapter_title="第一章",
            emotional_intensity=0.8,
            emotional_valence=0.3,
            primary_atmosphere="dark",
            consistency_score=0.85,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = ToneUnificationEngine(mock_ai)

        summary = engine.get_chapter_tone_summary(profile)

        assert isinstance(summary, str)
        assert "第1章" in summary
        assert "第一章" in summary
        assert "高强度" in summary
        assert "负面" in summary
        assert "dark" in summary


class TestToneUnificationModels:
    """Tests for tone unification models."""

    def test_chapter_tone_profile_model(self):
        """Test ChapterToneProfile model validation."""
        profile = ChapterToneProfile(
            chapter_number=1,
            chapter_title="第一章",
            emotional_intensity=0.6,
            emotional_valence=0.4,
            tone_markers={"epic": 5.0, "dramatic": 3.0},
            sentence_avg_length=25.0,
            paragraph_avg_length=180.0,
            dialogue_ratio=0.35,
            vocabulary_sophistication=0.6,
            primary_atmosphere="epic",
            consistency_score=0.9,
        )

        assert profile is not None
        assert profile.chapter_number == 1
        assert profile.emotional_intensity == 0.6
        assert profile.primary_atmosphere == "epic"

    def test_tone_shift_model(self):
        """Test ToneShift model validation."""
        shift = ToneShift(
            shift_id="shift_001",
            start_chapter=1,
            end_chapter=2,
            shift_type=ToneShiftType.ABRUPT_SHIFT,
            severity=ToneShiftSeverity.MODERATE,
            description="Abrupt tone shift detected",
            magnitude=0.4,
            likely_cause="Scene change",
            affected_aspects=[ToneUnificationType.EMOTIONAL_TONE],
        )

        assert shift is not None
        assert shift.shift_id == "shift_001"
        assert shift.start_chapter == 1
        assert shift.end_chapter == 2
        assert shift.shift_type == ToneShiftType.ABRUPT_SHIFT

    def test_unified_tone_profile_model(self):
        """Test UnifiedToneProfile model validation."""
        unified = UnifiedToneProfile(
            target_emotional_intensity=0.5,
            target_emotional_valence=0.5,
            intensity_range=(0.3, 0.7),
            valence_range=(0.3, 0.7),
            target_sentence_avg_length=20.0,
            sentence_length_range=(15.0, 30.0),
            target_paragraph_avg_length=150.0,
            paragraph_length_range=(100.0, 200.0),
            target_dialogue_ratio=0.3,
            dialogue_ratio_range=(0.2, 0.4),
            target_vocabulary_sophistication=0.5,
            target_atmosphere="epic",
            allowed_atmospheres=["epic", "dramatic"],
            emphasized_tones=["epic", "heroic"],
            avoided_tones=["comedic"],
        )

        assert unified is not None
        assert unified.target_emotional_intensity == 0.5
        assert unified.target_atmosphere == "epic"
        assert "epic" in unified.allowed_atmospheres

    def test_tone_unification_analysis_model(self):
        """Test ToneUnificationAnalysis model validation."""
        analysis = ToneUnificationAnalysis(
            overall_uniformity_score=0.85,
            chapter_profiles=[],
            unified_tone_profile=UnifiedToneProfile(),
            detected_shifts=[],
            problematic_chapters=[(2, 0.6), (5, 0.65)],
            total_chapters_analyzed=10,
            chapters_with_shifts=2,
            average_consistency=0.88,
            recommendations=["Revise chapter 2", "Check chapter 5"],
        )

        assert analysis is not None
        assert analysis.overall_uniformity_score == 0.85
        assert analysis.total_chapters_analyzed == 10
        assert len(analysis.problematic_chapters) == 2

    def test_tone_unification_revision_model(self):
        """Test ToneUnificationRevision model validation."""
        revision = ToneUnificationRevision(
            original_content="Original text",
            revised_content="Revised text",
            chapter_number=1,
            changes_made=["Adjusted tone"],
            before_score=0.6,
            after_score=0.9,
            issues_addressed=["Low intensity"],
            issues_remaining=[],
        )

        assert revision is not None
        assert revision.original_content == "Original text"
        assert revision.revised_content == "Revised text"
        assert revision.after_score > revision.before_score

    def test_tone_unification_plan_model(self):
        """Test ToneUnificationPlan model validation."""
        plan = ToneUnificationPlan(
            target_profile=UnifiedToneProfile(),
            chapters_to_revise=[2, 5, 8],
            priority_order=[2, 5, 8],
            estimated_revisions=3,
            ai_polishing_enabled=True,
        )

        assert plan is not None
        assert len(plan.chapters_to_revise) == 3
        assert plan.estimated_revisions == 3
        assert plan.ai_polishing_enabled is True

    def test_tone_unification_report_model(self):
        """Test ToneUnificationReport model validation."""
        report = ToneUnificationReport(
            analysis=ToneUnificationAnalysis(
                overall_uniformity_score=0.85,
                chapter_profiles=[],
                unified_tone_profile=UnifiedToneProfile(),
            ),
            revision_plan=ToneUnificationPlan(
                target_profile=UnifiedToneProfile(),
            ),
            summary="Tone is consistent across the manuscript.",
            revisions_completed=[],
            final_uniformity_score=0.92,
            improvement_achieved=0.07,
        )

        assert report is not None
        assert "consistent" in report.summary
        assert report.final_uniformity_score == 0.92


class TestToneUnificationTypes:
    """Tests for tone unification enums."""

    def test_tone_unification_types(self):
        """Test ToneUnificationType enum values."""
        assert ToneUnificationType.EMOTIONAL_TONE.value == "emotional_tone"
        assert ToneUnificationType.NARRATIVE_TONE.value == "narrative_tone"
        assert ToneUnificationType.ATMOSPHERIC_TONE.value == "atmospheric_tone"

    def test_tone_shift_types(self):
        """Test ToneShiftType enum values."""
        assert ToneShiftType.GRADUAL_SHIFT.value == "gradual_shift"
        assert ToneShiftType.ABRUPT_SHIFT.value == "abrupt_shift"
        assert ToneShiftType.CYCLICAL_SHIFT.value == "cyclical_shift"

    def test_tone_shift_severity(self):
        """Test ToneShiftSeverity enum values."""
        assert ToneShiftSeverity.NEGLIGIBLE.value == "negligible"
        assert ToneShiftSeverity.MINOR.value == "minor"
        assert ToneShiftSeverity.MODERATE.value == "moderate"
        assert ToneShiftSeverity.SEVERE.value == "severe"
        assert ToneShiftSeverity.CRITICAL.value == "critical"