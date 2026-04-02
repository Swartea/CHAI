"""Tests for dialogue engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from chai.engines.dialogue_engine import DialogueEngine
from chai.models.dialogue import (
    DialoguePurpose, DialogueType, DialogueTone, CharacterDialogueStyle,
    DialogueLine, DialogueExchange, DialoguePlan, DialogueDraft,
    DialogueRevision, DialogueAnalysis, DialogueTemplate
)
from chai.models.character import Character, CharacterRole
from chai.services import AIService


class TestDialogueModels:
    """Test dialogue models."""

    def test_character_dialogue_style_creation(self):
        """Test creating a character dialogue style."""
        style = CharacterDialogueStyle(
            speech_pattern="简洁直接",
            vocabulary_level="sophisticated",
            sentence_structure="mixed",
            formal_or_informal="formal",
            catchphrases=["吾之所见", "诚如所言"],
            filler_words=["嗯", "这个"],
            verbal_tics=["习惯性停顿"],
            emotional_restraint="suppressed",
            directness="direct",
        )
        assert style.speech_pattern == "简洁直接"
        assert "吾之所见" in style.catchphrases
        assert style.vocabulary_level == "sophisticated"

    def test_dialogue_line_creation(self):
        """Test creating a dialogue line."""
        line = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="今天的天气真是不错啊。",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.EMOTIONAL,
            emotional_state="joyful",
            is_catchphrase=False,
            is_important=True,
            word_count=10,
        )
        assert line.speaker_name == "小明"
        assert line.content == "今天的天气真是不错啊。"
        assert line.tone == DialogueTone.CASUAL

    def test_dialogue_exchange_creation(self):
        """Test creating a dialogue exchange."""
        line1 = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="你好啊！",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
        )
        line2 = DialogueLine(
            id="line_2",
            speaker_id="char_2",
            speaker_name="小红",
            content="你好！见到你很高兴。",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
        )
        exchange = DialogueExchange(
            id="exchange_1",
            scene_id="scene_1",
            participants=["char_1", "char_2"],
            participant_names=["小明", "小红"],
            lines=[line1, line2],
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
            topic="初次见面",
            power_dynamic="equal",
            emotional_tone=DialogueTone.CASUAL,
        )
        assert len(exchange.lines) == 2
        assert exchange.participants == ["char_1", "char_2"]

    def test_dialogue_plan_creation(self):
        """Test creating a dialogue plan."""
        plan = DialoguePlan(
            id="plan_1",
            scene_id="scene_1",
            characters=[
                {'name': '小明', 'personality_description': '开朗', 'speech_pattern': '活泼'},
                {'name': '小红', 'personality_description': '内向', 'speech_pattern': '沉稳'},
            ],
            speaker_count=2,
            purpose=DialoguePurpose.CONFLICT,
            topic="争论",
            situation="两人在讨论一个问题",
            target_line_count=10,
            target_word_count=500,
            dialogue_type=DialogueType.DIRECT,
            target_tone=DialogueTone.HOSTILE,
            tension_level="high",
            pacing="fast",
            relationship_type="rival",
            starting_emotion="neutral",
            ending_emotion="angry",
            include_subtext=True,
            include_gestures=True,
        )
        assert plan.purpose == DialoguePurpose.CONFLICT
        assert plan.target_tone == DialogueTone.HOSTILE
        assert plan.tension_level == "high"
        assert len(plan.characters) == 2

    def test_dialogue_draft_creation(self):
        """Test creating a dialogue draft."""
        line = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="测试对话",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
        )
        exchange = DialogueExchange(
            id="exchange_1",
            scene_id="scene_1",
            participants=["char_1"],
            participant_names=["小明"],
            lines=[line],
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
            topic="测试",
            total_word_count=4,
        )
        draft = DialogueDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            exchanges=[exchange],
            combined_text="小明：测试对话",
            total_line_count=1,
            total_word_count=4,
            naturalness_score=0.8,
            character_voice_score=0.85,
            purpose_fulfillment_score=0.75,
            status="draft",
        )
        assert draft.total_line_count == 1
        assert draft.naturalness_score == 0.8

    def test_dialogue_revision_creation(self):
        """Test creating a dialogue revision."""
        line = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="原对话",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
        )
        exchange = DialogueExchange(
            id="exchange_1",
            scene_id="scene_1",
            participants=["char_1"],
            participant_names=["小明"],
            lines=[line],
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
            topic="测试",
            total_word_count=3,
        )
        draft = DialogueDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            exchanges=[exchange],
            combined_text="小明：原对话",
            total_line_count=1,
            total_word_count=3,
        )
        revision = DialogueRevision(
            original_draft=draft,
            revision_notes=["需要更自然的对话", "增加情感表达"],
            revised_exchanges=[exchange],
            quality_score=0.9,
        )
        assert len(revision.revision_notes) == 2
        assert revision.quality_score == 0.9

    def test_dialogue_analysis_creation(self):
        """Test creating a dialogue analysis."""
        analysis = DialogueAnalysis(
            draft_id="draft_1",
            character_voice_consistency={"小明": 0.9, "小红": 0.85},
            speech_pattern_adherence=0.88,
            naturalness_score=0.85,
            dialogue_flow_score=0.8,
            purpose_clarity=0.9,
            information_transfer=0.75,
            emotional_authenticity=0.82,
            subtext_effectiveness=0.7,
            situation_appropriateness=0.88,
            relationship_consistency=0.85,
            overall_quality_score=0.83,
            critical_issues=["角色语气不够一致"],
            minor_issues=["可以增加更多潜台词"],
            recommendations=["加强角色语言特色"],
        )
        assert analysis.character_voice_consistency["小明"] == 0.9
        assert "角色语气不够一致" in analysis.critical_issues

    def test_dialogue_template_creation(self):
        """Test creating a dialogue template."""
        template = DialogueTemplate(
            id="confrontation",
            name="对峙",
            applicable_purposes=[DialoguePurpose.CONFLICT, DialoguePurpose.TENSION_BUILDING],
            applicable_tones=[DialogueTone.HOSTILE, DialogueTone.TENSE],
            typical_line_count=12,
            typical_participants=2,
            pacing_pattern="fast",
            tension_curve=["moderate", "high", "critical"],
            opening_pattern="直接挑战",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="deep",
            typical_opening_phrases=["你以为你可以..."],
            transition_phrases=["别打断我"],
            closing_phrases=["你会后悔的"],
        )
        assert template.name == "对峙"
        assert DialoguePurpose.CONFLICT in template.applicable_purposes
        assert template.typical_line_count == 12


class TestDialogueEngine:
    """Test dialogue engine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock(spec=AIService)
        service.generate = AsyncMock(return_value="小明：今天天气真好。\n小红：是啊，很适合出门。")
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create a dialogue engine."""
        return DialogueEngine(mock_ai_service)

    @pytest.fixture
    def sample_characters(self):
        """Create sample characters for testing."""
        char1 = Character(
            id="char_1",
            name="小明",
            role=CharacterRole.PROTAGONIST,
            personality_description="开朗活泼，喜欢交朋友",
            speech_pattern="说话直接，热情洋溢",
            speech_characteristics=["常用感叹词", "语速较快"],
            catchphrases=["太棒了！"],
        )
        char2 = Character(
            id="char_2",
            name="小红",
            role=CharacterRole.SUPPORTING,
            personality_description="温柔体贴，细心周到",
            speech_pattern="说话柔和，常用安慰语",
            speech_characteristics=["语气温和", "善于倾听"],
            catchphrases=["别担心"],
        )
        return [char1, char2]

    def test_engine_creation(self, engine):
        """Test engine can be created."""
        assert engine is not None

    def test_get_all_templates(self, engine):
        """Test getting all templates."""
        templates = engine.get_all_templates()
        assert len(templates) == 8
        assert "confrontation" in templates
        assert "romantic" in templates
        assert "negotiation" in templates
        assert "revelation" in templates

    def test_get_template(self, engine):
        """Test getting a specific template."""
        template = engine.get_template("confrontation")
        assert template is not None
        assert template.name == "对峙/冲突"
        assert DialoguePurpose.CONFLICT in template.applicable_purposes
        assert template.typical_line_count == 12

    def test_get_template_not_found(self, engine):
        """Test getting a non-existent template."""
        template = engine.get_template("nonexistent")
        assert template is None

    def test_build_character_dialogue_style(self, engine, sample_characters):
        """Test building character dialogue style."""
        char = sample_characters[0]
        style = engine._build_character_dialogue_style(char)
        assert style.speech_pattern == "说话直接，热情洋溢"
        assert "常用感叹词" in style.speech_quirks
        assert "太棒了！" in style.catchphrases

    @pytest.mark.asyncio
    async def test_generate_dialogue(self, engine, mock_ai_service, sample_characters):
        """Test generating dialogue."""
        draft = await engine.generate_dialogue(
            scene_id="scene_test",
            characters=sample_characters,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
            topic="天气讨论",
            situation="两人在公园散步",
            target_line_count=6,
            target_word_count=200,
            target_tone=DialogueTone.CASUAL,
        )
        assert draft is not None
        assert draft.scene_id == "scene_test"
        assert draft.total_line_count >= 0

    @pytest.mark.asyncio
    async def test_generate_dialogue_with_template(self, engine, mock_ai_service, sample_characters):
        """Test generating dialogue from template."""
        draft = await engine.generate_from_template(
            template_name="confrontation",
            scene_id="scene_confrontation",
            characters=sample_characters,
            situation="两人发生争执",
            topic="责任归属",
        )
        assert draft is not None
        assert draft.scene_id == "scene_confrontation"

    def test_analyze_dialogue(self, engine):
        """Test analyzing dialogue quality."""
        line = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="这个计划有问题。",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.SUSPICIOUS,
            purpose=DialoguePurpose.REVELATION,
            word_count=7,
        )
        line2 = DialogueLine(
            id="line_2",
            speaker_id="char_2",
            speaker_name="小红",
            content="什么问题？你说说看。",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.SUSPICIOUS,
            purpose=DialoguePurpose.INFORMATION_GATHERING,
            word_count=8,
        )
        exchange = DialogueExchange(
            id="exchange_1",
            scene_id="scene_1",
            participants=["char_1", "char_2"],
            participant_names=["小明", "小红"],
            lines=[line, line2],
            purpose=DialoguePurpose.REVELATION,
            topic="计划讨论",
            total_word_count=15,
        )
        draft = DialogueDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            exchanges=[exchange],
            combined_text="小明：这个计划有问题。\n小红：什么问题？你说说看。",
            total_line_count=2,
            total_word_count=15,
            naturalness_score=0.8,
            character_voice_score=0.75,
            purpose_fulfillment_score=0.7,
        )
        analysis = engine.analyze_dialogue(draft)
        assert analysis is not None
        assert analysis.draft_id == "draft_1"
        assert analysis.overall_quality_score >= 0

    def test_export_draft(self, engine):
        """Test exporting draft to dict."""
        line = DialogueLine(
            id="line_1",
            speaker_id="char_1",
            speaker_name="小明",
            content="测试对话",
            dialogue_type=DialogueType.DIRECT,
            tone=DialogueTone.CASUAL,
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
        )
        exchange = DialogueExchange(
            id="exchange_1",
            scene_id="scene_1",
            participants=["char_1"],
            participant_names=["小明"],
            lines=[line],
            purpose=DialoguePurpose.PLOT_ADVANCEMENT,
            topic="测试",
            total_word_count=4,
        )
        draft = DialogueDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            exchanges=[exchange],
            combined_text="小明：测试对话",
            total_line_count=1,
            total_word_count=4,
            naturalness_score=0.8,
            character_voice_score=0.85,
        )
        exported = engine.export_draft(draft)
        assert exported["draft_id"] == "draft_1"
        assert exported["total_line_count"] == 1
        assert len(exported["exchanges"]) == 1


class TestDialoguePurposeEnums:
    """Test dialogue purpose and type enums."""

    def test_dialogue_purpose_values(self):
        """Test all dialogue purpose values exist."""
        assert DialoguePurpose.INFORMATION_GATHERING.value == "information_gathering"
        assert DialoguePurpose.CONFLICT.value == "conflict"
        assert DialoguePurpose.ALLIANCE_BUILDING.value == "alliance_building"
        assert DialoguePurpose.REVELATION.value == "revelation"
        assert DialoguePurpose.EMOTIONAL.value == "emotional"
        assert DialoguePurpose.MANIPULATION.value == "manipulation"
        assert DialoguePurpose.TENSION_BUILDING.value == "tension_building"
        assert DialoguePurpose.COMIC_RELIEF.value == "comic_relief"
        assert DialoguePurpose.PLOT_ADVANCEMENT.value == "plot_advancement"
        assert DialoguePurpose.CHARACTER_REVELATION.value == "character_revelation"

    def test_dialogue_type_values(self):
        """Test all dialogue type values exist."""
        assert DialogueType.DIRECT.value == "direct"
        assert DialogueType.INDIRECT.value == "indirect"
        assert DialogueType.INTERNAL.value == "internal"
        assert DialogueType.WHISPERED.value == "whispered"
        assert DialogueType.SHOUTED.value == "shouted"
        assert DialogueType.SILENT.value == "silent"

    def test_dialogue_tone_values(self):
        """Test all dialogue tone values exist."""
        assert DialogueTone.FORMAL.value == "formal"
        assert DialogueTone.CASUAL.value == "casual"
        assert DialogueTone.INTIMATE.value == "intimate"
        assert DialogueTone.HOSTILE.value == "hostile"
        assert DialogueTone.SUSPICIOUS.value == "suspicious"
        assert DialogueTone.JOYFUL.value == "joyful"
        assert DialogueTone.SAD.value == "sad"
        assert DialogueTone.TENSE.value == "tense"
        assert DialogueTone.ROMANTIC.value == "romantic"
        assert DialogueTone.IRONIC.value == "ironic"
