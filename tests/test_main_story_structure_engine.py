"""Tests for MainStoryStructureEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.services import AIService
from chai.models.main_story_structure import (
    MainStoryStructure,
    MainStoryStructureType,
    StoryBeat,
    StoryBeatType,
    StoryBeatStatus,
    ActStructure,
    StructureAnalysis,
)
from chai.engines.main_story_structure_engine import (
    MainStoryStructureEngine,
    STRUCTURE_TEMPLATES,
    THREE_ACT_TEMPLATE,
    HEROS_JOURNEY_TEMPLATE,
    SEVEN_POINT_TEMPLATE,
    SAVE_THE_CAT_TEMPLATE,
    FREYTAGS_PYRAMID_TEMPLATE,
    KISHOTENKETSU_TEMPLATE,
)


class TestMainStoryStructureModels:
    """Tests for main story structure models."""

    def test_main_story_structure_type_enum(self):
        """Test MainStoryStructureType enum values."""
        assert MainStoryStructureType.THREE_ACT.value == "three_act"
        assert MainStoryStructureType.HEROS_JOURNEY.value == "heros_journey"
        assert MainStoryStructureType.SEVEN_POINT.value == "seven_point"
        assert MainStoryStructureType.SAVE_THE_CAT.value == "save_the_cat"
        assert MainStoryStructureType.FREYTAGS_PYRAMID.value == "freytags_pyramid"
        assert MainStoryStructureType.KISHOTENKETSU.value == "kishotenketsu"

    def test_story_beat_type_enum(self):
        """Test StoryBeatType enum values."""
        assert StoryBeatType.EXPOSITION.value == "exposition"
        assert StoryBeatType.INCITING_INCIDENT.value == "inciting_incident"
        assert StoryBeatType.RISING_ACTION.value == "rising_action"
        assert StoryBeatType.MIDPOINT.value == "midpoint"
        assert StoryBeatType.CLIMAX.value == "climax"
        assert StoryBeatType.FALLING_ACTION.value == "falling_action"
        assert StoryBeatType.RESOLUTION.value == "resolution"

    def test_story_beat_status_enum(self):
        """Test StoryBeatStatus enum values."""
        assert StoryBeatStatus.PENDING.value == "pending"
        assert StoryBeatStatus.IN_PROGRESS.value == "in_progress"
        assert StoryBeatStatus.COMPLETE.value == "complete"
        assert StoryBeatStatus.REVISED.value == "revised"

    def test_story_beat_model(self):
        """Test StoryBeat model."""
        beat = StoryBeat(
            id="beat_1",
            beat_type=StoryBeatType.EXPOSITION,
            name="建置",
            description="介绍世界和角色",
            order=1,
            act_number=1,
            start_chapter=1,
            end_chapter=3,
            purpose="建立故事基础",
            key_events=["事件1", "事件2"],
            character_involvement=["char_1", "char_2"],
            themes_explored=["成长", "勇气"],
            tension_level="low",
            status=StoryBeatStatus.PENDING,
        )
        assert beat.id == "beat_1"
        assert beat.beat_type == StoryBeatType.EXPOSITION
        assert beat.order == 1
        assert beat.start_chapter == 1
        assert beat.end_chapter == 3

    def test_act_structure_model(self):
        """Test ActStructure model."""
        act = ActStructure(
            id="act_1",
            number=1,
            name="第一幕",
            description="建置阶段",
            start_chapter=1,
            end_chapter=6,
            beats=[],
            purpose="建立故事基础",
            key_conflict="日常冲突",
            thematic_focus="现状",
        )
        assert act.id == "act_1"
        assert act.number == 1
        assert act.start_chapter == 1
        assert act.end_chapter == 6

    def test_main_story_structure_model(self):
        """Test MainStoryStructure model."""
        act = ActStructure(
            id="act_1",
            number=1,
            name="第一幕",
            description="测试",
            start_chapter=1,
            end_chapter=6,
            beats=[],
            purpose="测试",
            key_conflict="测试冲突",
        )
        beat = StoryBeat(
            id="beat_1",
            beat_type=StoryBeatType.EXPOSITION,
            name="测试",
            description="测试",
            order=1,
            start_chapter=1,
            end_chapter=3,
            purpose="测试",
        )
        structure = MainStoryStructure(
            id="structure_1",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            target_word_count=80000,
            acts=[act],
            beats=[beat],
            main_character_ids=["char_1"],
            core_conflict="测试冲突",
            central_question="测试问题",
            thematic_statement="测试主题",
            status=StoryBeatStatus.PENDING,
        )
        assert structure.title == "测试小说"
        assert structure.genre == "奇幻"
        assert structure.structure_type == MainStoryStructureType.THREE_ACT
        assert len(structure.acts) == 1
        assert len(structure.beats) == 1

    def test_structure_analysis_model(self):
        """Test StructureAnalysis model."""
        analysis = StructureAnalysis(
            structure_id="structure_1",
            beat_coverage={"required": 8, "present": 6, "coverage": 0.75},
            missing_beats=["beat_1", "beat_2"],
            pacing_score=0.8,
            chapter_distribution={"act_1": {"chapters": 6, "percentage": 0.25}},
            tension_curve=[{"beat": "beat_1", "tension": "low"}],
            thematic_coherence=0.75,
            thematic_progression=["主题1", "主题2"],
            character_arc_alignment={},
            coherence_score=0.85,
            completeness_score=0.9,
            structural_issues=["缺少情节点"],
            recommendations=["建议1"],
        )
        assert analysis.structure_id == "structure_1"
        assert analysis.coherence_score == 0.85
        assert analysis.completeness_score == 0.9


class TestStructureTemplates:
    """Tests for structure templates."""

    def test_three_act_template(self):
        """Test Three-Act template structure."""
        template = THREE_ACT_TEMPLATE
        assert template["name"] == "三幕式结构"
        assert len(template["acts"]) == 3
        assert len(template["beats"]) > 0

    def test_heros_journey_template(self):
        """Test Hero's Journey template structure."""
        template = HEROS_JOURNEY_TEMPLATE
        assert template["name"] == "英雄之旅"
        assert len(template["acts"]) == 3
        assert len(template["beats"]) > 0

    def test_seven_point_template(self):
        """Test Seven-Point template structure."""
        template = SEVEN_POINT_TEMPLATE
        assert template["name"] == "七点结构"
        assert len(template["acts"]) == 3
        assert len(template["beats"]) > 0

    def test_save_the_cat_template(self):
        """Test Save the Cat template structure."""
        template = SAVE_THE_CAT_TEMPLATE
        assert template["name"] == "救猫咪"
        assert len(template["acts"]) == 4
        assert len(template["beats"]) == 15

    def test_freytags_pyramid_template(self):
        """Test Freytag's Pyramid template structure."""
        template = FREYTAGS_PYRAMID_TEMPLATE
        assert template["name"] == "弗莱塔格金字塔"
        assert len(template["acts"]) == 3
        assert len(template["beats"]) > 0

    def test_kishotenketsu_template(self):
        """Test Kishotenketsu template structure."""
        template = KISHOTENKETSU_TEMPLATE
        assert template["name"] == "起承转合"
        assert len(template["acts"]) == 4
        assert len(template["beats"]) > 0

    def test_all_templates_in_structure_templates(self):
        """Test all templates are in STRUCTURE_TEMPLATES dict."""
        assert MainStoryStructureType.THREE_ACT in STRUCTURE_TEMPLATES
        assert MainStoryStructureType.HEROS_JOURNEY in STRUCTURE_TEMPLATES
        assert MainStoryStructureType.SEVEN_POINT in STRUCTURE_TEMPLATES
        assert MainStoryStructureType.SAVE_THE_CAT in STRUCTURE_TEMPLATES
        assert MainStoryStructureType.FREYTAGS_PYRAMID in STRUCTURE_TEMPLATES
        assert MainStoryStructureType.KISHOTENKETSU in STRUCTURE_TEMPLATES


class TestMainStoryStructureEngine:
    """Tests for MainStoryStructureEngine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock(spec=AIService)
        service.generate = AsyncMock(return_value='{"title": "测试小说", "core_conflict": "核心冲突", "central_question": "核心问题", "thematic_statement": "主题陈述", "beat_details": {"转折": ["转折1", "转折2"]}, "character_involvement": {"角色1": ["事件1"]}}')
        service._parse_json = lambda r: {
            "title": "测试小说",
            "core_conflict": "核心冲突",
            "central_question": "核心问题",
            "thematic_statement": "主题陈述",
            "beat_details": {"转折": ["转折1", "转折2"]},
            "character_involvement": {"角色1": ["事件1"]},
        }
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create a MainStoryStructureEngine instance."""
        return MainStoryStructureEngine(mock_ai_service)

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert hasattr(engine, "ai_service")

    def test_get_required_beats_three_act(self, engine):
        """Test getting required beats for Three-Act structure."""
        beats = engine._get_required_beats(MainStoryStructureType.THREE_ACT)
        assert StoryBeatType.EXPOSITION.value in beats
        assert StoryBeatType.CLIMAX.value in beats
        assert StoryBeatType.RESOLUTION.value in beats

    def test_get_required_beats_heros_journey(self, engine):
        """Test getting required beats for Hero's Journey structure."""
        beats = engine._get_required_beats(MainStoryStructureType.HEROS_JOURNEY)
        assert StoryBeatType.ORDINARY_WORLD.value in beats
        assert StoryBeatType.CALL_TO_ADVENTURE.value in beats
        assert StoryBeatType.ORDEAL.value in beats

    def test_get_required_beats_seven_point(self, engine):
        """Test getting required beats for Seven-Point structure."""
        beats = engine._get_required_beats(MainStoryStructureType.SEVEN_POINT)
        assert StoryBeatType.HOOK.value in beats
        assert StoryBeatType.MIDPOINT.value in beats
        assert StoryBeatType.DARK_MOMENT.value in beats

    def test_get_required_beats_save_the_cat(self, engine):
        """Test getting required beats for Save the Cat structure."""
        beats = engine._get_required_beats(MainStoryStructureType.SAVE_THE_CAT)
        assert StoryBeatType.OPENING_IMAGE.value in beats
        assert StoryBeatType.CATALYST.value in beats
        assert StoryBeatType.ALL_IS_LOST.value in beats

    def test_calculate_pacing_score_full(self, engine):
        """Test pacing score calculation with full structure."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose=""),
                StoryBeat(id="b2", beat_type=StoryBeatType.EXPOSITION, name="2", description="", order=2, start_chapter=4, end_chapter=6, purpose=""),
                StoryBeat(id="b3", beat_type=StoryBeatType.RISING_ACTION, name="3", description="", order=3, start_chapter=7, end_chapter=10, purpose=""),
            ],
            acts=[],
            main_character_ids=[],
            core_conflict="",
        )
        score = engine._calculate_pacing_score(structure)
        assert score >= 0.0

    def test_calculate_pacing_score_empty(self, engine):
        """Test pacing score calculation with empty structure."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            beats=[],
            acts=[],
            main_character_ids=[],
            core_conflict="",
        )
        score = engine._calculate_pacing_score(structure)
        assert score == 0.0

    def test_analyze_chapter_distribution(self, engine):
        """Test chapter distribution analysis."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[
                ActStructure(id="a1", number=1, name="第一幕", description="", start_chapter=1, end_chapter=8, beats=[], purpose="", key_conflict=""),
                ActStructure(id="a2", number=2, name="第二幕", description="", start_chapter=9, end_chapter=18, beats=[], purpose="", key_conflict=""),
                ActStructure(id="a3", number=3, name="第三幕", description="", start_chapter=19, end_chapter=24, beats=[], purpose="", key_conflict=""),
            ],
            beats=[],
            main_character_ids=[],
            core_conflict="",
        )
        distribution = engine._analyze_chapter_distribution(structure)
        assert "act_1" in distribution
        assert distribution["act_1"]["chapters"] == 8
        assert distribution["act_1"]["percentage"] == pytest.approx(8/24, abs=0.01)

    def test_analyze_tension_curve(self, engine):
        """Test tension curve analysis."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose="", tension_level="low"),
                StoryBeat(id="b2", beat_type=StoryBeatType.RISING_ACTION, name="2", description="", order=2, start_chapter=4, end_chapter=6, purpose="", tension_level="moderate"),
                StoryBeat(id="b3", beat_type=StoryBeatType.CLIMAX, name="3", description="", order=3, start_chapter=7, end_chapter=8, purpose="", tension_level="climax"),
            ],
            main_character_ids=[],
            core_conflict="",
        )
        curve = engine._analyze_tension_curve(structure)
        assert len(curve) == 3
        assert curve[0]["tension"] == "low"
        assert curve[2]["tension"] == "climax"

    def test_calculate_thematic_coherence_with_themes(self, engine):
        """Test thematic coherence with themes present."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose="", themes_explored=["成长"]),
                StoryBeat(id="b2", beat_type=StoryBeatType.RISING_ACTION, name="2", description="", order=2, start_chapter=4, end_chapter=6, purpose="", themes_explored=["勇气"]),
            ],
            main_character_ids=[],
            core_conflict="",
            thematic_statement="成长与勇气",
        )
        score = engine._calculate_thematic_coherence(structure)
        assert score == 1.0

    def test_calculate_thematic_coherence_without_themes(self, engine):
        """Test thematic coherence without themes."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose=""),
            ],
            main_character_ids=[],
            core_conflict="",
        )
        score = engine._calculate_thematic_coherence(structure)
        assert score == 0.3  # Base score without thematic statement

    def test_identify_issues_missing_beats(self, engine):
        """Test issue identification with missing beats."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[],  # Empty beats
            main_character_ids=["char_1"],
            core_conflict="",
        )
        analysis = StructureAnalysis(
            structure_id="test",
            missing_beats=["beat_1", "beat_2"],
            pacing_score=0.5,
        )
        issues = engine._identify_issues(structure, analysis)
        assert len(issues) > 0

    def test_identify_issues_early_climax(self, engine):
        """Test issue identification with early climax."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose="", tension_level="low"),
                StoryBeat(id="b2", beat_type=StoryBeatType.RISING_ACTION, name="2", description="", order=2, start_chapter=4, end_chapter=6, purpose="", tension_level="moderate"),
                StoryBeat(id="b3", beat_type=StoryBeatType.CLIMAX, name="3", description="", order=3, start_chapter=7, end_chapter=8, purpose="", tension_level="climax"),
                StoryBeat(id="b4", beat_type=StoryBeatType.FALLING_ACTION, name="4", description="", order=4, start_chapter=9, end_chapter=15, purpose="", tension_level="moderate"),
                StoryBeat(id="b5", beat_type=StoryBeatType.RESOLUTION, name="5", description="", order=5, start_chapter=16, end_chapter=24, purpose="", tension_level="low"),
            ],
            main_character_ids=[],
            core_conflict="",
        )
        analysis = StructureAnalysis(
            structure_id="test",
            pacing_score=0.5,
        )
        issues = engine._identify_issues(structure, analysis)
        # Climax ends at chapter 8, last chapter is 24, 8 < 24*0.7 = 16.8 is True
        assert any("过早" in issue for issue in issues)

    def test_generate_recommendations(self, engine):
        """Test recommendation generation."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[],
            main_character_ids=["char_1"],
            core_conflict="",
        )
        analysis = StructureAnalysis(
            structure_id="test",
            missing_beats=["beat_1"],
            pacing_score=0.4,
            thematic_coherence=0.5,
        )
        recommendations = engine._generate_recommendations(structure, analysis)
        assert len(recommendations) > 0

    def test_get_structure_summary(self, engine):
        """Test getting structure summary."""
        structure = MainStoryStructure(
            id="test",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[
                ActStructure(id="a1", number=1, name="第一幕", description="", start_chapter=1, end_chapter=8, beats=[], purpose="建立基础", key_conflict=""),
            ],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="建置", description="", order=1, start_chapter=1, end_chapter=3, purpose="建立基础"),
            ],
            main_character_ids=[],
            core_conflict="测试冲突",
            central_question="测试问题",
            thematic_statement="成长主题",
        )
        summary = engine.get_structure_summary(structure)
        assert "测试小说" in summary
        assert "奇幻" in summary
        assert "成长" in summary
        assert "第一幕" in summary

    def test_export_structure(self, engine):
        """Test exporting structure to dict."""
        structure = MainStoryStructure(
            id="test",
            title="测试小说",
            genre="奇幻",
            theme="成长",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            target_word_count=80000,
            acts=[
                ActStructure(id="a1", number=1, name="第一幕", description="", start_chapter=1, end_chapter=8, beats=[], purpose="建立基础", key_conflict=""),
            ],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="建置", description="", order=1, start_chapter=1, end_chapter=3, purpose="建立基础", tension_level="low"),
            ],
            main_character_ids=["char_1"],
            antagonist_id="ant_1",
            core_conflict="测试冲突",
            central_question="测试问题",
            thematic_statement="成长主题",
            status=StoryBeatStatus.PENDING,
        )
        exported = engine.export_structure(structure)
        assert exported["id"] == "test"
        assert exported["title"] == "测试小说"
        assert exported["genre"] == "奇幻"
        assert exported["structure_type"] == "three_act"
        assert len(exported["acts"]) == 1
        assert len(exported["beats"]) == 1


class TestStructureAnalysis:
    """Tests for structure analysis."""

    @pytest.fixture
    def engine(self):
        """Create engine with mock AI service."""
        return MainStoryStructureEngine(MagicMock(spec=AIService))

    def test_analyze_structure_three_act_sync(self, engine):
        """Test analyzing a Three-Act structure (sync test for non-async analyze)."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[
                ActStructure(id="a1", number=1, name="第一幕", description="", start_chapter=1, end_chapter=8, beats=[], purpose="", key_conflict=""),
                ActStructure(id="a2", number=2, name="第二幕", description="", start_chapter=9, end_chapter=18, beats=[], purpose="", key_conflict=""),
                ActStructure(id="a3", number=3, name="第三幕", description="", start_chapter=19, end_chapter=24, beats=[], purpose="", key_conflict=""),
            ],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose="", tension_level="low"),
                StoryBeat(id="b2", beat_type=StoryBeatType.INCITING_INCIDENT, name="2", description="", order=2, start_chapter=4, end_chapter=5, purpose="", tension_level="moderate"),
                StoryBeat(id="b3", beat_type=StoryBeatType.RISING_ACTION, name="3", description="", order=3, start_chapter=6, end_chapter=8, purpose="", tension_level="high"),
            ],
            main_character_ids=["char_1"],
            core_conflict="测试冲突",
            thematic_statement="成长",
        )
        # Test the sync parts of analyze_structure
        pacing = engine._calculate_pacing_score(structure)
        assert pacing >= 0.0

        dist = engine._analyze_chapter_distribution(structure)
        assert "act_1" in dist

    def test_analyze_structure_heros_journey_sync(self, engine):
        """Test analyzing a Hero's Journey structure (sync test)."""
        structure = MainStoryStructure(
            id="test",
            title="测试",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.HEROS_JOURNEY,
            target_chapters=24,
            acts=[],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.ORDINARY_WORLD, name="1", description="", order=1, start_chapter=1, end_chapter=2, purpose="", tension_level="low"),
                StoryBeat(id="b2", beat_type=StoryBeatType.CALL_TO_ADVENTURE, name="2", description="", order=2, start_chapter=3, end_chapter=4, purpose="", tension_level="moderate"),
                StoryBeat(id="b3", beat_type=StoryBeatType.MEETING_THE_MENTOR, name="3", description="", order=3, start_chapter=5, end_chapter=6, purpose="", tension_level="moderate"),
            ],
            main_character_ids=["char_1"],
            core_conflict="测试冲突",
        )
        # Test the sync parts
        tension = engine._analyze_tension_curve(structure)
        assert len(tension) == 3

    def test_calculate_coherence_with_issues(self, engine):
        """Test coherence calculation with issues."""
        analysis = StructureAnalysis(
            structure_id="test",
            missing_beats=["beat_1", "beat_2"],
            structural_issues=["issue1", "issue2", "issue3"],
        )
        score = engine._calculate_coherence_score(analysis)
        # Base 1.0 - 0.1*2 (missing) - 0.05*3 (issues) = 1.0 - 0.2 - 0.15 = 0.65
        assert score == pytest.approx(0.65, abs=0.001)

    def test_calculate_coherence_clean(self, engine):
        """Test coherence calculation with no issues."""
        analysis = StructureAnalysis(
            structure_id="test",
            missing_beats=[],
            structural_issues=[],
        )
        score = engine._calculate_coherence_score(analysis)
        assert score == 1.0

    def test_calculate_completeness_full(self, engine):
        """Test completeness with full structure."""
        structure = MainStoryStructure(
            id="test",
            title="测试小说",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[
                ActStructure(id="a1", number=1, name="第一幕", description="", start_chapter=1, end_chapter=8, beats=[], purpose="", key_conflict=""),
                ActStructure(id="a2", number=2, name="第二幕", description="", start_chapter=9, end_chapter=18, beats=[], purpose="", key_conflict=""),
            ],
            beats=[
                StoryBeat(id="b1", beat_type=StoryBeatType.EXPOSITION, name="1", description="", order=1, start_chapter=1, end_chapter=3, purpose="", themes_explored=["主题"]),
                StoryBeat(id="b2", beat_type=StoryBeatType.RISING_ACTION, name="2", description="", order=2, start_chapter=4, end_chapter=6, purpose="", themes_explored=["主题"]),
                StoryBeat(id="b3", beat_type=StoryBeatType.MIDPOINT, name="3", description="", order=3, start_chapter=7, end_chapter=9, purpose="", themes_explored=["主题"]),
                StoryBeat(id="b4", beat_type=StoryBeatType.RISING_ACTION, name="4", description="", order=4, start_chapter=10, end_chapter=12, purpose="", themes_explored=["主题"]),
                StoryBeat(id="b5", beat_type=StoryBeatType.CLIMAX, name="5", description="", order=5, start_chapter=13, end_chapter=15, purpose="", themes_explored=["主题"]),
            ],
            main_character_ids=["char_1"],
            core_conflict="测试冲突",
            thematic_statement="成长主题",
        )
        analysis = StructureAnalysis(
            structure_id="test",
            beat_coverage={"coverage": 0.8},
        )
        score = engine._calculate_completeness_score(structure, analysis)
        assert score > 0.8

    def test_calculate_completeness_minimal(self, engine):
        """Test completeness with minimal structure."""
        structure = MainStoryStructure(
            id="test",
            title="",
            genre="奇幻",
            theme="测试",
            structure_type=MainStoryStructureType.THREE_ACT,
            target_chapters=24,
            acts=[],
            beats=[],
            main_character_ids=[],
            core_conflict="",
        )
        analysis = StructureAnalysis(
            structure_id="test",
            beat_coverage={"coverage": 0},
        )
        score = engine._calculate_completeness_score(structure, analysis)
        assert score < 0.3