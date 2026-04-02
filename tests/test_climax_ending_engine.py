"""Tests for ClimaxEndingEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.climax_ending import (
    ClimaxType,
    ClimaxIntensity,
    ClimaxStatus,
    ClimaxElement,
    ClimaxStructure,
    ClimaxDesign,
    EndingType,
    EndingStatus,
    EndingElement,
    EndingStructure,
    EndingDesign,
    ClimaxEndingConnection,
    ClimaxEndingSystem,
    ClimaxAnalysis,
    EndingAnalysis,
    ClimaxEndingAnalysis,
)
from chai.engines.climax_ending_engine import ClimaxEndingEngine
from chai.services import AIService


class TestClimaxEndingModels:
    """Tests for climax and ending models."""

    def test_climax_type_enum(self):
        """Test ClimaxType enum values."""
        assert ClimaxType.FINAL_CLIMAX.value == "final_climax"
        assert ClimaxType.SUB_CLIMAX.value == "sub_climax"
        assert ClimaxType.EMOTIONAL_CLIMAX.value == "emotional_climax"
        assert ClimaxType.COMBAT_CLIMAX.value == "combat_climax"
        assert ClimaxType.SACRIFICE_CLIMAX.value == "sacrifice_climax"
        assert ClimaxType.REVELATION_CLIMAX.value == "revelation_climax"
        assert ClimaxType.DECISION_CLIMAX.value == "decision_climax"
        assert ClimaxType.TRANSFORMATION_CLIMAX.value == "transformation_climax"

    def test_climax_intensity_enum(self):
        """Test ClimaxIntensity enum values."""
        assert ClimaxIntensity.MODERATE.value == "moderate"
        assert ClimaxIntensity.HIGH.value == "high"
        assert ClimaxIntensity.EXTREME.value == "extreme"
        assert ClimaxIntensity.CATASTROPHIC.value == "catastrophic"

    def test_climax_status_enum(self):
        """Test ClimaxStatus enum values."""
        assert ClimaxStatus.CONCEPT.value == "concept"
        assert ClimaxStatus.PLANNED.value == "planned"
        assert ClimaxStatus.DEVELOPED.value == "developed"
        assert ClimaxStatus.INTEGRATED.value == "integrated"

    def test_ending_type_enum(self):
        """Test EndingType enum values."""
        assert EndingType.CLEAN_RESOLUTION.value == "clean_resolution"
        assert EndingType.BITTERSWEET.value == "bittersweet"
        assert EndingType.TRAGIC.value == "tragic"
        assert EndingType.OPEN_ENDED.value == "open_ended"
        assert EndingType.CIRCULAR.value == "circular"
        assert EndingType.TWIST_ENDING.value == "twist_ending"
        assert EndingType.TRIUMPHANT.value == "triumphant"
        assert EndingType.PYRRHIC_VICTORY.value == "pyrrhic_victory"
        assert EndingType.REDEMPTIVE.value == "redemptive"
        assert EndingType.CLEANSED.value == "cleansed"

    def test_ending_status_enum(self):
        """Test EndingStatus enum values."""
        assert EndingStatus.CONCEPT.value == "concept"
        assert EndingStatus.PLANNED.value == "planned"
        assert EndingStatus.DEVELOPED.value == "developed"
        assert EndingStatus.REFINED.value == "refined"

    def test_climax_element_model(self):
        """Test ClimaxElement model."""
        element = ClimaxElement(
            id="elem_1",
            name="正面对决",
            description="主角与反派的终极对决",
            element_type="confrontation",
            chapter=20,
            sequence_order=1,
            character_ids=["protagonist_1", "antagonist_1"],
            protagonist_central=True,
            stakes="世界的命运",
            tension_level=ClimaxIntensity.EXTREME,
            plot_thread_ids=["main_thread"],
            foreshadowing_ids=["foreshadow_1"],
        )
        assert element.id == "elem_1"
        assert element.name == "正面对决"
        assert element.tension_level == ClimaxIntensity.EXTREME
        assert element.protagonist_central is True

    def test_climax_structure_model(self):
        """Test ClimaxStructure model."""
        element = ClimaxElement(
            id="elem_1",
            name="高潮",
            description="高潮时刻",
            element_type="peak",
            chapter=20,
            sequence_order=1,
            tension_level=ClimaxIntensity.EXTREME,
        )
        structure = ClimaxStructure(
            id="climax_1",
            climax_type=ClimaxType.FINAL_CLIMAX,
            name="终极对决",
            buildup_chapters=[17, 18, 19],
            trigger_event="魔王觉醒",
            elements=[element],
            peak_moment="正面对决",
            peak_chapter=20,
            immediate_resolution="魔王被击败",
            consequences=["和平降临", "主角成长"],
            world_changes=["旧世界毁灭", "新世界诞生"],
            emotional_impact="强烈的情感冲击",
            catharsis_level=0.9,
        )
        assert structure.id == "climax_1"
        assert structure.climax_type == ClimaxType.FINAL_CLIMAX
        assert len(structure.elements) == 1
        assert structure.catharsis_level == 0.9

    def test_ending_element_model(self):
        """Test EndingElement model."""
        element = EndingElement(
            id="end_elem_1",
            name="新开始",
            description="新的冒险开始",
            element_type="new_beginning",
            chapter=24,
            sequence_order=0,
            character_ids=["protagonist_1"],
            purpose="传达希望",
            emotional_effect="温暖与期待",
        )
        assert element.id == "end_elem_1"
        assert element.element_type == "new_beginning"
        assert element.emotional_effect == "温暖与期待"

    def test_ending_structure_model(self):
        """Test EndingStructure model."""
        element = EndingElement(
            id="end_elem_1",
            name="结局",
            description="故事结束",
            element_type="conclusion",
            chapter=24,
            sequence_order=0,
            purpose="完整收尾",
            emotional_effect="满足与回味",
        )
        structure = EndingStructure(
            id="ending_1",
            ending_type=EndingType.CLEAN_RESOLUTION,
            name="完美结局",
            resolved_threads=["main_thread", "subplot_1"],
            unresolved_threads=[],
            elements=[element],
            final_image="朝阳下的新世界",
            final_line="故事至此结束，但生活仍在继续。",
            closing_symbol="首尾呼应的象征",
            emotional_tone="所有冲突得到解决",
            reader_emotional_journey=["期待", "紧张", "满足", "回味"],
            character_fates={"protagonist_1": "成为英雄", "antagonist_1": "改过自新"},
            world_state="世界恢复到新的平衡状态",
        )
        assert structure.id == "ending_1"
        assert structure.ending_type == EndingType.CLEAN_RESOLUTION
        assert len(structure.resolved_threads) == 2
        assert len(structure.character_fates) == 2

    def test_climax_design_model(self):
        """Test ClimaxDesign model."""
        element = ClimaxElement(
            id="elem_1",
            name="高潮",
            description="高潮时刻",
            element_type="peak",
            chapter=20,
            sequence_order=0,
            tension_level=ClimaxIntensity.EXTREME,
        )
        climax = ClimaxStructure(
            id="climax_1",
            climax_type=ClimaxType.FINAL_CLIMAX,
            name="终极对决",
            elements=[element],
            peak_moment="高潮",
            peak_chapter=20,
        )
        design = ClimaxDesign(
            id="design_1",
            story_id="story_1",
            main_climax=climax,
            sub_climaxes=[],
            climax_chapter=20,
            climax_duration_chapters=2,
            story_beat_ids=["beat_1"],
            character_arc_ids=["arc_1"],
            plot_thread_ids=["thread_1"],
            status=ClimaxStatus.DEVELOPED,
        )
        assert design.id == "design_1"
        assert design.climax_chapter == 20
        assert design.status == ClimaxStatus.DEVELOPED

    def test_ending_design_model(self):
        """Test EndingDesign model."""
        ending = EndingStructure(
            id="ending_1",
            ending_type=EndingType.CLEAN_RESOLUTION,
            name="完美结局",
            elements=[],
            final_image="朝阳下的新世界",
        )
        design = EndingDesign(
            id="end_design_1",
            story_id="story_1",
            ending=ending,
            ending_chapter=24,
            epilogue_chapters=1,
            climax_id="climax_1",
            character_arc_ids=["arc_1"],
            theme_resolution="主题在结局得到升华",
            thematic_statement="关于勇气与牺牲的思考",
            main_question_answered="故事核心问题得到回答",
            closure_level=0.95,
            status=EndingStatus.DEVELOPED,
        )
        assert design.id == "end_design_1"
        assert design.ending_chapter == 24
        assert design.closure_level == 0.95

    def test_climax_ending_connection_model(self):
        """Test ClimaxEndingConnection model."""
        conn = ClimaxEndingConnection(
            id="conn_1",
            climax_id="climax_1",
            ending_id="ending_1",
            transition_chapters=2,
            transition_nature="从高潮到结局的平稳过渡",
            emotional_flow="从激昂到平静的情感流动",
            plot_continuity="情节连贯，逻辑自洽",
            climax_weight=0.6,
        )
        assert conn.id == "conn_1"
        assert conn.transition_chapters == 2
        assert conn.climax_weight == 0.6

    def test_climax_ending_system_model(self):
        """Test ClimaxEndingSystem model."""
        element = ClimaxElement(
            id="elem_1",
            name="高潮",
            description="高潮时刻",
            element_type="peak",
            chapter=20,
            sequence_order=0,
            tension_level=ClimaxIntensity.EXTREME,
        )
        climax = ClimaxStructure(
            id="climax_1",
            climax_type=ClimaxType.FINAL_CLIMAX,
            name="终极对决",
            elements=[element],
            peak_moment="高潮",
            peak_chapter=20,
        )
        climax_design = ClimaxDesign(
            id="climax_design_1",
            story_id="story_1",
            main_climax=climax,
            climax_chapter=20,
        )
        ending = EndingStructure(
            id="ending_1",
            ending_type=EndingType.CLEAN_RESOLUTION,
            name="完美结局",
            elements=[],
            final_image="朝阳下的新世界",
        )
        ending_design = EndingDesign(
            id="ending_design_1",
            story_id="story_1",
            ending=ending,
            ending_chapter=24,
            climax_id="climax_design_1",
        )
        conn = ClimaxEndingConnection(
            id="conn_1",
            climax_id="climax_design_1",
            ending_id="ending_design_1",
            transition_chapters=2,
        )
        system = ClimaxEndingSystem(
            id="system_1",
            story_id="story_1",
            climax_design=climax_design,
            ending_design=ending_design,
            connection=conn,
            emotional_impact_score=0.85,
            thematic_coherence_score=0.9,
            satisfaction_score=0.88,
        )
        assert system.id == "system_1"
        assert system.emotional_impact_score == 0.85

    def test_climax_analysis_model(self):
        """Test ClimaxAnalysis model."""
        analysis = ClimaxAnalysis(
            design_id="design_1",
            structural_integrity=0.85,
            element_balance=0.8,
            emotional_peak_effectiveness=0.9,
            tension_curve_quality=0.85,
            plot_thread_resolution=0.8,
            character_arc_resolution=0.85,
            identified_issues=["高潮可以更激烈"],
            recommendations=["增加情感冲击"],
        )
        assert analysis.design_id == "design_1"
        assert analysis.emotional_peak_effectiveness == 0.9
        assert len(analysis.recommendations) == 1

    def test_ending_analysis_model(self):
        """Test EndingAnalysis model."""
        analysis = EndingAnalysis(
            design_id="end_design_1",
            closure_quality=0.9,
            thread_resolution_quality=0.85,
            emotional_satisfaction=0.88,
            thematic_resolution_quality=0.9,
            character_fate_satisfaction=0.85,
            identified_issues=[],
            recommendations=["补充更多细节"],
        )
        assert analysis.design_id == "end_design_1"
        assert analysis.closure_quality == 0.9

    def test_climax_ending_analysis_model(self):
        """Test ClimaxEndingAnalysis model."""
        climax_analysis = ClimaxAnalysis(
            design_id="design_1",
            structural_integrity=0.85,
        )
        ending_analysis = EndingAnalysis(
            design_id="end_design_1",
            closure_quality=0.9,
        )
        analysis = ClimaxEndingAnalysis(
            system_id="system_1",
            climax_analysis=climax_analysis,
            ending_analysis=ending_analysis,
            transition_quality=0.8,
            emotional_flow_quality=0.85,
            narrative_coherence=0.88,
            overall_quality_score=0.86,
            identified_issues=["过渡可以更平滑"],
            recommendations=["增加过渡细节"],
        )
        assert analysis.system_id == "system_1"
        assert analysis.overall_quality_score == 0.86


class TestClimaxEndingEngine:
    """Tests for ClimaxEndingEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ai_service = MagicMock(spec=AIService)
        self.engine = ClimaxEndingEngine(self.ai_service)

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine.ai_service is not None

    def test_calculate_climax_chapter_final(self):
        """Test climax chapter calculation for final climax."""
        chapter = self.engine._calculate_climax_chapter(24, ClimaxType.FINAL_CLIMAX)
        assert chapter == 21  # 24 * 0.88 = 21.12

    def test_calculate_climax_chapter_sub(self):
        """Test climax chapter calculation for sub climax."""
        chapter = self.engine._calculate_climax_chapter(24, ClimaxType.SUB_CLIMAX)
        assert chapter == 16  # int(24 * 0.7) = int(16.8) = 16

    def test_calculate_climax_duration_final(self):
        """Test climax duration calculation for final climax."""
        duration = self.engine._calculate_climax_duration(ClimaxType.FINAL_CLIMAX)
        assert duration == 2

    def test_calculate_climax_duration_combat(self):
        """Test climax duration calculation for combat climax."""
        duration = self.engine._calculate_climax_duration(ClimaxType.COMBAT_CLIMAX)
        assert duration == 2

    def test_calculate_climax_duration_emotional(self):
        """Test climax duration calculation for emotional climax."""
        duration = self.engine._calculate_climax_duration(ClimaxType.EMOTIONAL_CLIMAX)
        assert duration == 1

    def test_get_element_name(self):
        """Test element name localization."""
        assert self.engine._get_element_name("buildup") == "张力积累"
        assert self.engine._get_element_name("peak") == "巅峰时刻"
        assert self.engine._get_element_name("resolution") == "结果揭晓"

    def test_get_ending_element_name(self):
        """Test ending element name localization."""
        assert self.engine._get_ending_element_name("victory") == "胜利宣告"
        assert self.engine._get_ending_element_name("conclusion") == "尾声"
        assert self.engine._get_ending_element_name("hope") == "希望"

    def test_get_emotional_effect(self):
        """Test emotional effect descriptions."""
        assert self.engine._get_emotional_effect("victory") == "喜悦与满足"
        assert self.engine._get_emotional_effect("loss") == "悲伤与感慨"

    def test_get_final_image(self):
        """Test final image selection."""
        assert "朝阳" in self.engine._get_final_image(EndingType.CLEAN_RESOLUTION)
        assert "夕阳" in self.engine._get_final_image(EndingType.BITTERSWEET)

    def test_get_final_line(self):
        """Test final line selection."""
        assert "结束" in self.engine._get_final_line(EndingType.CLEAN_RESOLUTION)
        assert "未完待续" in self.engine._get_final_line(EndingType.OPEN_ENDED)

    def test_calculate_closure_level_clean(self):
        """Test closure level for clean resolution."""
        level = self.engine._calculate_closure_level(EndingType.CLEAN_RESOLUTION)
        assert level == 1.0

    def test_calculate_closure_level_open(self):
        """Test closure level for open ended."""
        level = self.engine._calculate_closure_level(EndingType.OPEN_ENDED)
        assert level == 0.4

    def test_extract_story_beat_ids_empty(self):
        """Test extracting beat IDs from None."""
        ids = self.engine._extract_story_beat_ids(None)
        assert ids == []

    def test_extract_arc_ids_empty(self):
        """Test extracting arc IDs from None."""
        ids = self.engine._extract_arc_ids(None)
        assert ids == []

    def test_extract_thread_ids_empty(self):
        """Test extracting thread IDs from None."""
        ids = self.engine._extract_thread_ids(None)
        assert ids == []

    @pytest.mark.asyncio
    async def test_generate_climax_design(self):
        """Test climax design generation."""
        design = await self.engine.generate_climax_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            climax_type=ClimaxType.FINAL_CLIMAX,
            target_chapters=24,
        )
        assert design.id.startswith("climax_")
        assert design.story_id == "story_1"
        assert design.climax_chapter > 0
        assert design.status == ClimaxStatus.DEVELOPED

    @pytest.mark.asyncio
    async def test_generate_ending_design(self):
        """Test ending design generation."""
        design = await self.engine.generate_ending_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            ending_type=EndingType.CLEAN_RESOLUTION,
            target_chapters=24,
        )
        assert design.id.startswith("ending_")
        assert design.story_id == "story_1"
        assert design.ending_chapter > 0
        assert design.status == EndingStatus.DEVELOPED

    @pytest.mark.asyncio
    async def test_generate_complete_design(self):
        """Test complete climax and ending system generation."""
        system = await self.engine.generate_complete_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            climax_type=ClimaxType.FINAL_CLIMAX,
            ending_type=EndingType.CLEAN_RESOLUTION,
            target_chapters=24,
        )
        assert system.id.startswith("climax_ending_")
        assert system.story_id == "story_1"
        assert system.climax_design is not None
        assert system.ending_design is not None
        assert system.connection is not None

    @pytest.mark.asyncio
    async def test_analyze_climax(self):
        """Test climax analysis."""
        design = await self.engine.generate_climax_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            climax_type=ClimaxType.FINAL_CLIMAX,
            target_chapters=24,
        )
        analysis = await self.engine.analyze_climax(design)
        assert analysis.design_id == design.id
        assert 0 <= analysis.structural_integrity <= 1

    @pytest.mark.asyncio
    async def test_analyze_ending(self):
        """Test ending analysis."""
        design = await self.engine.generate_ending_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            ending_type=EndingType.CLEAN_RESOLUTION,
            target_chapters=24,
        )
        analysis = await self.engine.analyze_ending(design)
        assert analysis.design_id == design.id
        assert 0 <= analysis.closure_quality <= 1

    @pytest.mark.asyncio
    async def test_analyze_climax_ending_system(self):
        """Test climax and ending system analysis."""
        system = await self.engine.generate_complete_design(
            story_id="story_1",
            genre="玄幻",
            theme="成长",
            climax_type=ClimaxType.FINAL_CLIMAX,
            ending_type=EndingType.CLEAN_RESOLUTION,
            target_chapters=24,
        )
        analysis = await self.engine.analyze_climax_ending_system(system)
        assert analysis.system_id == system.id
        assert 0 <= analysis.overall_quality_score <= 1

    def test_get_system_summary(self):
        """Test system summary generation."""
        element = ClimaxElement(
            id="elem_1",
            name="高潮",
            description="高潮时刻",
            element_type="peak",
            chapter=20,
            sequence_order=0,
            tension_level=ClimaxIntensity.EXTREME,
        )
        climax = ClimaxStructure(
            id="climax_1",
            climax_type=ClimaxType.FINAL_CLIMAX,
            name="终极对决",
            elements=[element],
            peak_moment="高潮",
            peak_chapter=20,
        )
        climax_design = ClimaxDesign(
            id="climax_design_1",
            story_id="story_1",
            main_climax=climax,
            climax_chapter=20,
        )
        ending = EndingStructure(
            id="ending_1",
            ending_type=EndingType.CLEAN_RESOLUTION,
            name="完美结局",
            elements=[],
            final_image="朝阳下的新世界",
        )
        ending_design = EndingDesign(
            id="ending_design_1",
            story_id="story_1",
            ending=ending,
            ending_chapter=24,
            climax_id="climax_design_1",
        )
        conn = ClimaxEndingConnection(
            id="conn_1",
            climax_id="climax_design_1",
            ending_id="ending_design_1",
            transition_chapters=2,
        )
        system = ClimaxEndingSystem(
            id="system_1",
            story_id="story_1",
            climax_design=climax_design,
            ending_design=ending_design,
            connection=conn,
            emotional_impact_score=0.85,
            thematic_coherence_score=0.9,
            satisfaction_score=0.88,
        )

        summary = self.engine.get_system_summary(system)
        assert "高潮与结局设计" in summary
        assert "终极对决" in summary
        assert "完美结局" in summary

    def test_export_system(self):
        """Test system export."""
        element = ClimaxElement(
            id="elem_1",
            name="高潮",
            description="高潮时刻",
            element_type="peak",
            chapter=20,
            sequence_order=0,
            tension_level=ClimaxIntensity.EXTREME,
        )
        climax = ClimaxStructure(
            id="climax_1",
            climax_type=ClimaxType.FINAL_CLIMAX,
            name="终极对决",
            elements=[element],
            peak_moment="高潮",
            peak_chapter=20,
        )
        climax_design = ClimaxDesign(
            id="climax_design_1",
            story_id="story_1",
            main_climax=climax,
            climax_chapter=20,
        )
        ending = EndingStructure(
            id="ending_1",
            ending_type=EndingType.CLEAN_RESOLUTION,
            name="完美结局",
            elements=[],
            final_image="朝阳下的新世界",
        )
        ending_design = EndingDesign(
            id="ending_design_1",
            story_id="story_1",
            ending=ending,
            ending_chapter=24,
            climax_id="climax_design_1",
        )
        conn = ClimaxEndingConnection(
            id="conn_1",
            climax_id="climax_design_1",
            ending_id="ending_design_1",
            transition_chapters=2,
        )
        system = ClimaxEndingSystem(
            id="system_1",
            story_id="story_1",
            climax_design=climax_design,
            ending_design=ending_design,
            connection=conn,
            emotional_impact_score=0.85,
            thematic_coherence_score=0.9,
            satisfaction_score=0.88,
        )

        exported = self.engine.export_system(system)
        assert exported["id"] == "system_1"
        assert exported["climax"]["type"] == "final_climax"
        assert exported["ending"]["type"] == "clean_resolution"
        assert exported["quality"]["emotional_impact"] == 0.85
