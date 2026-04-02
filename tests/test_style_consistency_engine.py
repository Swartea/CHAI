"""Tests for style consistency engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import Novel, Volume, Chapter, Character
from chai.models.style_consistency import (
    StyleConsistencyType,
    NarrativeTone,
    NarrativeVoice,
    PacingLevel,
    DescriptiveDensity,
    SentenceComplexity,
    VocabularyLevel,
    StyleConsistencyStatus,
    StyleConsistencyCheck,
    StyleProfile,
    StyleConsistencyAnalysis,
    StyleConsistencyTemplate,
    StyleConsistencyDraft,
    CharacterVoiceProfile,
)
from chai.engines.style_engine import StyleEngine, STYLE_TEMPLATES
from chai.services import AIService


class TestStyleEngine:
    """Tests for StyleEngine."""

    def test_analyze_novel_style(self):
        """Test style profile analysis."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content='这是一个史诗般的场景。他说道："这是一个壮阔的故事。"紧张的时刻来临。',
                word_count=50,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            target_chapter_word_count=(2000, 4000),
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        profile = engine.analyze_novel_style(novel)

        assert profile is not None
        assert isinstance(profile.tones, list)
        assert hasattr(profile, 'dialogue_ratio')
        assert 0 <= profile.dialogue_ratio <= 1

    def test_analyze_novel_style_epic_fantasy(self):
        """Test analyzing epic fantasy style."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content='史诗般的战争开始了。伟大的英雄站在壮阔的战场上，面临着前所未有的危机。',
                word_count=100,
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
        engine = StyleEngine(mock_ai)

        profile = engine.analyze_novel_style(novel)

        assert profile is not None
        assert profile.pacing in [PacingLevel.FAST, PacingLevel.MODERATE, PacingLevel.SLOW]

    def test_check_character_voice_consistency(self):
        """Test character voice consistency checking."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content="张三：这是一个测试。" "李四：当然没问题。",
            word_count=50,
        )

        characters = [
            Character(
                id="char_1",
                name="张三",
                role="protagonist",
                speech_pattern="简洁直接",
            ),
            Character(
                id="char_2",
                name="李四",
                role="supporting",
                speech_pattern="礼貌客气",
            ),
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        issues = engine.check_character_voice_consistency(chapter, characters)

        assert isinstance(issues, list)

    def test_check_descriptive_consistency(self):
        """Test descriptive density consistency checking."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content="这是一个非常长的描述性段落，描述了房间里的一切陈设和细节。" * 20,
            word_count=500,
        )

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.DRAMATIC,
            descriptive_density=DescriptiveDensity.HIGH,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        issues = engine.check_descriptive_consistency(chapter, profile)

        assert isinstance(issues, list)

    def test_check_tone_consistency(self):
        """Test tone consistency checking."""
        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content="这是一个紧张的场景，危机四伏。英雄必须做出关键决定。",
            word_count=50,
        )

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC, NarrativeTone.EPIC],
            dominant_tone=NarrativeTone.DRAMATIC,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        check = engine.check_tone_consistency(chapter, profile)

        assert check is not None
        assert check.check_type == StyleConsistencyType.TONE
        assert check.chapter_number == 1

    def test_check_pacing_consistency(self):
        """Test pacing consistency checking."""
        # Create chapter with varied paragraph lengths
        content = ""
        for i in range(10):
            if i % 2 == 0:
                content += "短段落。" * 3 + "\n\n"
            else:
                content += "这是一个非常长的段落，描述了场景中的许多细节和发生的事情。" * 5 + "\n\n"

        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content=content,
            word_count=len(content),
        )

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.DRAMATIC,
            pacing=PacingLevel.MODERATE,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        check = engine.check_pacing_consistency(chapter, profile)

        assert check is not None
        assert check.check_type == StyleConsistencyType.PACING
        assert 0 <= check.score <= 1

    def test_check_dialogue_ratio_consistency(self):
        """Test dialogue ratio consistency checking."""
        # Create chapter with known dialogue ratio
        content = '"对话内容。" ' * 20  # 20 dialogue lines
        content += "这是叙述内容。" * 50  # 50 narration lines

        chapter = Chapter(
            id="ch_1", number=1, title="第一章",
            content=content,
            word_count=len(content),
        )

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.DRAMATIC,
            dialogue_ratio=0.3,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        check = engine.check_dialogue_ratio_consistency(chapter, profile)

        assert check is not None
        assert check.check_type == StyleConsistencyType.DIALOGUE_RATIO

    def test_analyze_consistency(self):
        """Test comprehensive consistency analysis."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content='这是一个紧张的场景。"对话。" 英雄面对危机。',
                word_count=50,
            ),
            Chapter(
                id="ch_2", number=2, title="第二章",
                content='另一个史诗般的场景。"更多对话。" 战斗开始了。',
                word_count=50,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC, NarrativeTone.EPIC],
            dominant_tone=NarrativeTone.DRAMATIC,
            pacing=PacingLevel.MODERATE,
            descriptive_density=DescriptiveDensity.MEDIUM,
            dialogue_ratio=0.3,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)
        engine.set_style_profile(profile)

        analysis = engine.analyze_consistency(novel, profile)

        assert analysis is not None
        assert isinstance(analysis.overall_score, float)
        assert 0 <= analysis.overall_score <= 1
        assert analysis.overall_status in [
            StyleConsistencyStatus.CONSISTENT,
            StyleConsistencyStatus.MINOR_ISSUES,
            StyleConsistencyStatus.MAJOR_ISSUES,
            StyleConsistencyStatus.INCONSISTENT,
        ]

    def test_generate_style_guide(self):
        """Test style guide generation."""
        chapters = [
            Chapter(
                id="ch_1", number=1, title="第一章",
                content="内容" * 1000,
                word_count=1000,
            ),
        ]
        volume = Volume(id="vol_1", title="第一卷", number=1, chapters=chapters)

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
            characters=[
                Character(
                    id="char_1",
                    name="主角",
                    role="protagonist",
                    speech_pattern="沉稳有力",
                ),
            ],
        )

        profile = StyleProfile(
            tones=[NarrativeTone.EPIC, NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.EPIC,
            descriptive_density=DescriptiveDensity.HIGH,
            dialogue_ratio=0.3,
            pacing=PacingLevel.MODERATE,
            sentence_structure=SentenceComplexity.MIXED,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        guide = engine.generate_style_guide(novel, profile)

        assert "测试小说" in guide
        assert "文风指南" in guide
        assert "主角" in guide

    def test_get_template(self):
        """Test getting a style template."""
        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        template = engine.get_template("epic_fantasy")

        assert template is not None
        assert isinstance(template, StyleConsistencyTemplate)
        assert template.template_name == "epic_fantasy"

    def test_get_all_templates(self):
        """Test getting all style templates."""
        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        templates = engine.get_all_templates()

        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "epic_fantasy" in templates
        assert "mystery" in templates
        assert "romance" in templates

    def test_apply_template(self):
        """Test applying a style template."""
        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        profile = engine.apply_template("epic_fantasy")

        assert profile is not None
        assert isinstance(profile, StyleProfile)
        assert NarrativeTone.EPIC in profile.tones or profile.dominant_tone == NarrativeTone.EPIC

    def test_apply_invalid_template(self):
        """Test applying an invalid template returns None."""
        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        profile = engine.apply_template("nonexistent_template")

        assert profile is None

    def test_create_character_voice_profile(self):
        """Test creating a character voice profile."""
        character = Character(
            id="char_1",
            name="张三",
            role="protagonist",
            speech_pattern="简洁有力",
            catchphrase="一切都会好的",
        )

        sample_dialogue = [
            "这是第一句对话。",
            "这是第二句对话。",
            "这是第三句对话。",
        ]

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        voice_profile = engine.create_character_voice_profile(character, sample_dialogue)

        assert voice_profile is not None
        assert isinstance(voice_profile, CharacterVoiceProfile)
        assert voice_profile.character_name == "张三"
        assert voice_profile.character_id == "char_1"

    def test_create_character_voice_profile_empty_dialogue(self):
        """Test creating voice profile with empty dialogue."""
        character = Character(
            id="char_1",
            name="张三",
            role="protagonist",
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        voice_profile = engine.create_character_voice_profile(character, [])

        assert voice_profile is not None
        assert voice_profile.character_name == "张三"

    def test_set_and_get_style_profile(self):
        """Test setting and getting style profile."""
        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        profile = StyleProfile(
            tones=[NarrativeTone.ROMANTIC],
            dominant_tone=NarrativeTone.ROMANTIC,
        )

        engine.set_style_profile(profile)
        retrieved = engine.get_style_profile()

        assert retrieved is profile
        assert retrieved is not None

    def test_export_draft(self):
        """Test exporting a style consistency draft."""
        content = "这是一些小说内容。"

        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC],
            dominant_tone=NarrativeTone.DRAMATIC,
        )

        mock_ai = MagicMock(spec=AIService)
        engine = StyleEngine(mock_ai)

        draft = engine.export_draft(content, profile, "epic_fantasy")

        assert draft is not None
        assert isinstance(draft, StyleConsistencyDraft)
        assert draft.content == content
        assert "epic_fantasy" in draft.applied_templates


class TestStyleTemplates:
    """Tests for style consistency templates."""

    def test_epic_fantasy_template(self):
        """Test epic fantasy template has correct values."""
        template = STYLE_TEMPLATES["epic_fantasy"]

        assert template is not None
        assert NarrativeTone.EPIC in template.tones
        assert template.narrative_voice == NarrativeVoice.THIRD_OMNISCIENT
        assert template.dialogue_ratio == 0.25
        assert template.descriptive_density == DescriptiveDensity.HIGH

    def test_romance_template(self):
        """Test romance template has correct values."""
        template = STYLE_TEMPLATES["romance"]

        assert template is not None
        assert NarrativeTone.ROMANTIC in template.tones
        assert template.narrative_voice == NarrativeVoice.THIRD_LIMITED
        assert template.dialogue_ratio == 0.45
        assert template.pacing == PacingLevel.SLOW

    def test_mystery_template(self):
        """Test mystery template has correct values."""
        template = STYLE_TEMPLATES["mystery"]

        assert template is not None
        assert NarrativeTone.MYSTERIOUS in template.tones
        assert template.sentence_structure == SentenceComplexity.COMPLEX
        assert template.strict_tone_matching is True

    def test_template_to_style_profile(self):
        """Test converting template to style profile."""
        template = STYLE_TEMPLATES["epic_fantasy"]
        profile = template.to_style_profile()

        assert profile is not None
        assert isinstance(profile, StyleProfile)
        assert NarrativeTone.EPIC in profile.tones
        assert profile.narrative_voice == NarrativeVoice.THIRD_OMNISCIENT


class TestStyleConsistencyModels:
    """Tests for style consistency models."""

    def test_style_profile_model(self):
        """Test StyleProfile model validation."""
        profile = StyleProfile(
            tones=[NarrativeTone.DRAMATIC, NarrativeTone.EPIC],
            dominant_tone=NarrativeTone.DRAMATIC,
            narrative_voice=NarrativeVoice.THIRD_OMNISCIENT,
            pacing=PacingLevel.MODERATE,
            descriptive_density=DescriptiveDensity.MEDIUM,
            dialogue_ratio=0.35,
            sentence_structure=SentenceComplexity.MIXED,
            vocabulary_level=VocabularyLevel.MODERATE,
        )

        assert profile is not None
        assert len(profile.tones) == 2
        assert profile.dialogue_ratio == 0.35

    def test_style_consistency_check_model(self):
        """Test StyleConsistencyCheck model validation."""
        check = StyleConsistencyCheck(
            check_type=StyleConsistencyType.TONE,
            status=StyleConsistencyStatus.MINOR_ISSUES,
            score=0.85,
            issues=["Minor tone shift detected"],
            chapter_number=5,
            recommendations=["Maintain consistent tone"],
        )

        assert check is not None
        assert check.score == 0.85
        assert len(check.issues) == 1

    def test_style_consistency_analysis_model(self):
        """Test StyleConsistencyAnalysis model validation."""
        analysis = StyleConsistencyAnalysis(
            overall_status=StyleConsistencyStatus.CONSISTENT,
            overall_score=0.92,
            all_issues=[],
            all_recommendations=[],
            chapter_issues={},
        )

        assert analysis is not None
        assert analysis.overall_score == 0.92
        assert analysis.overall_status == StyleConsistencyStatus.CONSISTENT

    def test_character_voice_profile_model(self):
        """Test CharacterVoiceProfile model validation."""
        voice_profile = CharacterVoiceProfile(
            character_id="char_1",
            character_name="张三",
            speech_pattern="简洁有力",
            vocabulary_level=VocabularyLevel.MODERATE,
            sentence_structure=SentenceComplexity.MIXED,
            catchphrases=["一切都会好的"],
            consistency_score=0.9,
        )

        assert voice_profile is not None
        assert voice_profile.character_name == "张三"
        assert len(voice_profile.catchphrases) == 1
