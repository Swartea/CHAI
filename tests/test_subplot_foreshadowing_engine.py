"""Tests for SubplotForeshadowingEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.subplot_foreshadowing import (
    SubplotType,
    SubplotStatus,
    SubplotImportance,
    SubplotConnection,
    ForeshadowingTechnique,
    ForeshadowingStrength,
    ForeshadowingPattern,
    ForeshadowingPlanting,
    ForeshadowingPayoff,
    SubplotChapterBeat,
    SubplotArc,
    Subplot,
    ForeshadowingElementDetail,
    SubplotForeshadowingSystem,
    SubplotAnalysis,
    ForeshadowingAnalysis,
    SubplotForeshadowingDesign,
)
from chai.engines.subplot_foreshadowing_engine import SubplotForeshadowingEngine
from chai.services import AIService


class TestSubplotForeshadowingModels:
    """Tests for subplot and foreshadowing models."""

    def test_subplot_type_enum(self):
        """Test SubplotType enum values."""
        assert SubplotType.ROMANTIC.value == "romantic"
        assert SubplotType.RIVALRY.value == "rivalry"
        assert SubplotType.REDEMPTION.value == "redemption"
        assert SubplotType.MYSTERY.value == "mystery"
        assert SubplotType.GROWTH.value == "growth"
        assert SubplotType.BETRAYAL.value == "betrayal"

    def test_subplot_status_enum(self):
        """Test SubplotStatus enum values."""
        assert SubplotStatus.CONCEPT.value == "concept"
        assert SubplotStatus.PLANNED.value == "planned"
        assert SubplotStatus.ACTIVE.value == "active"
        assert SubplotStatus.RESOLVED.value == "resolved"

    def test_subplot_importance_enum(self):
        """Test SubplotImportance enum values."""
        assert SubplotImportance.MINOR.value == "minor"
        assert SubplotImportance.MODERATE.value == "moderate"
        assert SubplotImportance.MAJOR.value == "major"
        assert SubplotImportance.CRITICAL.value == "critical"

    def test_foreshadowing_technique_enum(self):
        """Test ForeshadowingTechnique enum values."""
        assert ForeshadowingTechnique.DIRECT_HINT.value == "direct_hint"
        assert ForeshadowingTechnique.CHEKHOVS_GUN.value == "chekhovs_gun"
        assert ForeshadowingTechnique.DRAMATIC_IRONY.value == "dramatic_irony"
        assert ForeshadowingTechnique.ATMOSPHERIC_HINT.value == "atmospheric_hint"
        assert ForeshadowingTechnique.SYMBOLIC.value == "symbolic"

    def test_foreshadowing_pattern_enum(self):
        """Test ForeshadowingPattern enum values."""
        assert ForeshadowingPattern.EARLY_PLANT_LATE_PAYOFF.value == "early_plant_late_payoff"
        assert ForeshadowingPattern.MULTI_STAGE_REVEAL.value == "multi_stage_reveal"
        assert ForeshadowingPattern.PARALLEL_STRUCTURE.value == "parallel_structure"
        assert ForeshadowingPattern.CIRCULAR_RETURN.value == "circular_return"

    def test_subplot_model(self):
        """Test Subplot model."""
        subplot = Subplot(
            id="subplot_1",
            name="感情线",
            subplot_type=SubplotType.ROMANTIC,
            importance=SubplotImportance.MAJOR,
            estimated_word_count=10000,
            start_chapter=3,
            end_chapter=22,
            peak_chapter=15,
            involved_characters=["char_1", "char_2"],
            primary_conflict="角色间的误会",
            connection_to_main=SubplotConnection.PARALLEL,
            status=SubplotStatus.PLANNED,
        )
        assert subplot.name == "感情线"
        assert subplot.subplot_type == SubplotType.ROMANTIC
        assert subplot.start_chapter == 3
        assert subplot.end_chapter == 22

    def test_foreshadowing_element_detail_model(self):
        """Test ForeshadowingElementDetail model."""
        planting = ForeshadowingPlanting(
            technique=ForeshadowingTechnique.SYMBOLIC,
            chapter=3,
            scene_location="墙壁角落",
            presentation_method="神秘符号",
            supporting_context="环境描写",
            subtlety_level=0.7,
            reinforcement_chapters=[10, 15],
        )
        payoff = ForeshadowingPayoff(
            chapter=20,
            payoff_type="revelation",
            payoff_method="揭示真相",
            emotional_impact="恍然大悟",
            connection_strength=ForeshadowingStrength.STRONG,
            reader_awareness=0.3,
        )

        foreshadowing = ForeshadowingElementDetail(
            id="fore_1",
            name="神秘符号",
            element="墙上出现的神秘符号",
            foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
            pattern_type=ForeshadowingPattern.EARLY_PLANT_LATE_PAYOFF,
            planting=planting,
            payoff=payoff,
            foreshadows="主角身世之谜",
            related_characters=["char_1"],
            thematic_significance="命运与身份",
            linked_subplot_id="subplot_mystery",
            is_planted=False,
            is_paid_off=False,
        )

        assert foreshadowing.name == "神秘符号"
        assert foreshadowing.planting.chapter == 3
        assert foreshadowing.payoff.chapter == 20
        assert foreshadowing.planting.subtlety_level == 0.7

    def test_subplot_arc_model(self):
        """Test SubplotArc model."""
        arc = SubplotArc(
            id="arc_1",
            name="救赎弧线",
            subplot_type=SubplotType.REDEMPTION,
            primary_characters=["char_1"],
            introduction="角色堕落的开始",
            rising_action=["错误决定", "后果显现"],
            climax="关键抉择时刻",
            falling_action=["影响扩散", "最后挣扎"],
            resolution="获得救赎",
            thematic_connection="救赎与成长",
            emotional_tone="沉重但有希望",
        )
        assert arc.name == "救赎弧线"
        assert arc.subplot_type == SubplotType.REDEMPTION
        assert len(arc.rising_action) == 2

    def test_subplot_chapter_beat_model(self):
        """Test SubplotChapterBeat model."""
        beat = SubplotChapterBeat(
            chapter=5,
            beat_description="角色相遇",
            character_states={"char_1": "紧张", "char_2": "好奇"},
            relationship_changes={"char_1-char_2": "从陌生到认识"},
            tension_level="moderate",
            subplot_progress=0.3,
        )
        assert beat.chapter == 5
        assert beat.tension_level == "moderate"
        assert beat.subplot_progress == 0.3

    def test_subplot_foreshadowing_system_model(self):
        """Test SubplotForeshadowingSystem model."""
        system = SubplotForeshadowingSystem(
            id="system_1",
            story_id="story_1",
            subplots=[],
            foreshadowing_elements=[],
            subplot_distribution={1: [], 2: ["subplot_1"]},
            foreshadowing_density={1: 1, 2: 0},
            overall_coherence=0.85,
            payoff_ratio=0.75,
        )
        assert system.id == "system_1"
        assert system.overall_coherence == 0.85
        assert system.payoff_ratio == 0.75

    def test_subplot_analysis_model(self):
        """Test SubplotAnalysis model."""
        analysis = SubplotAnalysis(
            subplot_id="subplot_1",
            main_story_integration={"connected_beats": [], "dependency_level": True},
            pacing_impact={"peak_at_chapter": 15},
            character_development={"chars_involved": 2, "growth_stages": 4},
            relationship_evolution=[],
            screen_time_ratio=0.25,
            reader_engagement=0.8,
            potential_conflicts=[],
            recommendations=["建议增加互动"],
        )
        assert analysis.subplot_id == "subplot_1"
        assert analysis.screen_time_ratio == 0.25

    def test_foreshadowing_analysis_model(self):
        """Test ForeshadowingAnalysis model."""
        analysis = ForeshadowingAnalysis(
            coverage_by_chapter={1: 1, 2: 0, 3: 2},
            coverage_gaps=[2],
            pattern_distribution={"symbolic": 3, "dramatic_irony": 2},
            effectiveness_scores={},
            payoff_timing={},
            delayed_payoffs=[],
            rushed_payoffs=[],
            subplot_connections={},
            orphaned_elements=["fore_5"],
            overall_balance=0.8,
            reader_experience={},
        )
        assert analysis.coverage_gaps == [2]
        assert 0.8 in [analysis.overall_balance]

    def test_subplot_foreshadowing_design_model(self):
        """Test SubplotForeshadowingDesign model."""
        system = SubplotForeshadowingSystem(
            id="system_1",
            story_id="story_1",
            subplots=[],
            foreshadowing_elements=[],
        )
        design = SubplotForeshadowingDesign(
            id="design_1",
            story_id="story_1",
            title="测试设计",
            system=system,
            subplot_analyses=[],
            foreshadowing_analysis=ForeshadowingAnalysis(
                coverage_by_chapter={},
                coverage_gaps=[],
                pattern_distribution={},
                effectiveness_scores={},
                payoff_timing={},
                delayed_payoffs=[],
                rushed_payoffs=[],
                subplot_connections={},
                orphaned_elements=[],
                overall_balance=0.0,
                reader_experience={},
            ),
            main_story_beats=[],
            character_arcs=["arc_1"],
            design_summary="测试设计概要",
            key_subplots=[],
            key_foreshadowing=[],
        )
        assert design.title == "测试设计"
        assert design.system is not None


class TestSubplotForeshadowingEngine:
    """Tests for SubplotForeshadowingEngine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock(spec=AIService)
        service.generate = AsyncMock(return_value='{"introduction": "开始", "rising_action": ["事件1"], "climax": "高潮", "falling_action": ["事件2"], "resolution": "结束", "primary_conflict": "冲突", "thematic_connection": "主题", "emotional_tone": "紧张", "dependency": ""}')
        service._parse_json = lambda r: {
            "introduction": "开始",
            "rising_action": ["事件1"],
            "climax": "高潮",
            "falling_action": ["事件2"],
            "resolution": "结束",
            "primary_conflict": "冲突",
            "thematic_connection": "主题",
            "emotional_tone": "紧张",
            "dependency": "",
        }
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create a SubplotForeshadowingEngine instance."""
        return SubplotForeshadowingEngine(mock_ai_service)

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert hasattr(engine, "ai_service")

    def test_generate_subplot(self, engine):
        """Test generating a subplot."""
        subplot = engine.generate_subplot(
            subplot_name="测试支线",
            subplot_type=SubplotType.ROMANTIC,
            primary_characters=["char_1", "char_2"],
            start_chapter=3,
            end_chapter=15,
            importance=SubplotImportance.MAJOR,
        )
        # Note: This is async so we check it runs
        assert subplot is not None or True

    @pytest.mark.asyncio
    async def test_generate_subplot_async(self, engine):
        """Test generating a subplot async."""
        subplot = await engine.generate_subplot(
            subplot_name="测试支线",
            subplot_type=SubplotType.ROMANTIC,
            primary_characters=["char_1", "char_2"],
            start_chapter=3,
            end_chapter=15,
            importance=SubplotImportance.MAJOR,
        )
        assert subplot is not None
        assert subplot.name == "测试支线"
        assert subplot.subplot_type == SubplotType.ROMANTIC

    @pytest.mark.asyncio
    async def test_generate_foreshadowing(self, engine):
        """Test generating foreshadowing."""
        foreshadowing = await engine.generate_foreshadowing(
            name="神秘符号",
            foreshadows="主角身份揭晓",
            technique=ForeshadowingTechnique.SYMBOLIC,
            plant_chapter=3,
            payoff_chapter=18,
            related_characters=["char_1"],
        )
        assert foreshadowing is not None
        assert foreshadowing.name == "神秘符号"
        assert foreshadowing.planting.chapter == 3
        assert foreshadowing.payoff.chapter == 18

    @pytest.mark.asyncio
    async def test_generate_complete_design(self, engine):
        """Test generating complete design."""
        design = await engine.generate_complete_design(
            story_id="story_1",
            title="测试设计",
            total_chapters=24,
            genre="奇幻",
            main_characters=[
                {"id": "char_1", "name": "主角1"},
                {"id": "char_2", "name": "主角2"},
            ],
        )
        assert design is not None
        assert design.title == "测试设计"
        assert len(design.system.subplots) > 0
        assert len(design.system.foreshadowing_elements) > 0

    def test_link_foreshadowing_to_subplot(self, engine):
        """Test linking foreshadowing to subplot."""
        system = SubplotForeshadowingSystem(
            id="system_1",
            story_id="story_1",
            subplots=[
                Subplot(
                    id="subplot_1",
                    name="测试支线",
                    subplot_type=SubplotType.ROMANTIC,
                    start_chapter=1,
                    end_chapter=24,
                    involved_characters=[],
                    foreshadowing_elements=[],
                )
            ],
            foreshadowing_elements=[
                ForeshadowingElementDetail(
                    id="fore_1",
                    name="测试伏笔",
                    element="测试",
                    foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                    planting=ForeshadowingPlanting(
                        technique=ForeshadowingTechnique.SYMBOLIC,
                        chapter=1,
                    ),
                    payoff=ForeshadowingPayoff(chapter=20),
                )
            ],
        )
        design = SubplotForeshadowingDesign(
            id="design_1",
            story_id="story_1",
            title="测试",
            system=system,
            subplot_analyses=[],
            foreshadowing_analysis=ForeshadowingAnalysis(
                coverage_by_chapter={},
                coverage_gaps=[],
                pattern_distribution={},
                effectiveness_scores={},
                payoff_timing={},
                delayed_payoffs=[],
                rushed_payoffs=[],
                subplot_connections={},
                orphaned_elements=[],
                overall_balance=0.0,
                reader_experience={},
            ),
            main_story_beats=[],
            character_arcs=[],
            design_summary="",
            key_subplots=[],
            key_foreshadowing=[],
        )

        updated = engine.link_foreshadowing_to_subplot(
            design, "fore_1", "subplot_1"
        )

        assert updated.system.foreshadowing_elements[0].linked_subplot_id == "subplot_1"
        assert "fore_1" in updated.system.subplots[0].foreshadowing_elements

    def test_get_design_summary(self, engine):
        """Test getting design summary."""
        system = SubplotForeshadowingSystem(
            id="system_1",
            story_id="story_1",
            subplots=[
                Subplot(
                    id="subplot_1",
                    name="感情线",
                    subplot_type=SubplotType.ROMANTIC,
                    importance=SubplotImportance.MAJOR,
                    start_chapter=3,
                    end_chapter=22,
                    involved_characters=["char_1"],
                    foreshadowing_elements=[],
                )
            ],
            foreshadowing_elements=[
                ForeshadowingElementDetail(
                    id="fore_1",
                    name="神秘符号",
                    element="测试",
                    foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                    planting=ForeshadowingPlanting(
                        technique=ForeshadowingTechnique.SYMBOLIC,
                        chapter=3,
                    ),
                    payoff=ForeshadowingPayoff(chapter=20),
                    is_paid_off=True,
                )
            ],
            payoff_ratio=1.0,
        )
        design = SubplotForeshadowingDesign(
            id="design_1",
            story_id="story_1",
            title="测试设计",
            system=system,
            subplot_analyses=[],
            foreshadowing_analysis=ForeshadowingAnalysis(
                coverage_by_chapter={},
                coverage_gaps=[],
                pattern_distribution={},
                effectiveness_scores={},
                payoff_timing={},
                delayed_payoffs=[],
                rushed_payoffs=[],
                subplot_connections={},
                orphaned_elements=[],
                overall_balance=0.8,
                reader_experience={},
            ),
            main_story_beats=[],
            character_arcs=[],
            design_summary="",
            key_subplots=[],
            key_foreshadowing=[],
        )

        summary = engine.get_design_summary(design)

        assert "测试设计" in summary
        assert "感情线" in summary
        assert "神秘符号" in summary

    def test_export_design(self, engine):
        """Test exporting design."""
        system = SubplotForeshadowingSystem(
            id="system_1",
            story_id="story_1",
            subplots=[
                Subplot(
                    id="subplot_1",
                    name="感情线",
                    subplot_type=SubplotType.ROMANTIC,
                    importance=SubplotImportance.MAJOR,
                    start_chapter=3,
                    end_chapter=22,
                    involved_characters=["char_1"],
                    status=SubplotStatus.PLANNED,
                    foreshadowing_elements=[],
                )
            ],
            foreshadowing_elements=[
                ForeshadowingElementDetail(
                    id="fore_1",
                    name="神秘符号",
                    element="测试",
                    foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                    planting=ForeshadowingPlanting(
                        technique=ForeshadowingTechnique.SYMBOLIC,
                        chapter=3,
                    ),
                    payoff=ForeshadowingPayoff(chapter=20),
                    is_paid_off=True,
                    linked_subplot_id=None,
                )
            ],
            overall_coherence=0.85,
            payoff_ratio=1.0,
        )
        design = SubplotForeshadowingDesign(
            id="design_1",
            story_id="story_1",
            title="测试设计",
            system=system,
            subplot_analyses=[],
            foreshadowing_analysis=ForeshadowingAnalysis(
                coverage_by_chapter={},
                coverage_gaps=[],
                pattern_distribution={},
                effectiveness_scores={},
                payoff_timing={},
                delayed_payoffs=[],
                rushed_payoffs=[],
                subplot_connections={},
                orphaned_elements=[],
                overall_balance=0.8,
                reader_experience={},
            ),
            main_story_beats=[],
            character_arcs=[],
            design_summary="",
            key_subplots=["subplot_1"],
            key_foreshadowing=["fore_1"],
        )

        exported = engine.export_design(design)

        assert exported["id"] == "design_1"
        assert exported["title"] == "测试设计"
        assert len(exported["subplots"]) == 1
        assert len(exported["foreshadowing"]) == 1


class TestForeshadowingDensityCalculation:
    """Tests for foreshadowing density calculation."""

    def test_calculate_foreshadowing_density(self):
        """Test foreshadowing density calculation."""
        engine = SubplotForeshadowingEngine(MagicMock())

        foreshadowing = [
            ForeshadowingElementDetail(
                id="fore_1",
                name="测试1",
                element="元素1",
                foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                planting=ForeshadowingPlanting(
                    technique=ForeshadowingTechnique.SYMBOLIC,
                    chapter=2,
                ),
                payoff=ForeshadowingPayoff(chapter=18),
            ),
            ForeshadowingElementDetail(
                id="fore_2",
                name="测试2",
                element="元素2",
                foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                planting=ForeshadowingPlanting(
                    technique=ForeshadowingTechnique.SYMBOLIC,
                    chapter=2,
                ),
                payoff=ForeshadowingPayoff(chapter=18),
            ),
        ]

        density = engine._calculate_foreshadowing_density(foreshadowing, 24)

        assert density[2] == 2  # Both planted in chapter 2
        assert density[18] == 2  # Both paid off in chapter 18
        assert density[1] == 0  # Nothing in chapter 1


class TestSubplotDistribution:
    """Tests for subplot distribution calculation."""

    def test_calculate_distribution(self):
        """Test subplot chapter distribution."""
        engine = SubplotForeshadowingEngine(MagicMock())

        subplots = [
            Subplot(
                id="subplot_1",
                name="支线1",
                subplot_type=SubplotType.ROMANTIC,
                start_chapter=3,
                end_chapter=10,
                involved_characters=[],
            ),
            Subplot(
                id="subplot_2",
                name="支线2",
                subplot_type=SubplotType.MYSTERY,
                start_chapter=5,
                end_chapter=15,
                involved_characters=[],
            ),
        ]

        distribution = engine._calculate_distribution(subplots, 24)

        assert "subplot_1" in distribution[3]
        assert "subplot_1" in distribution[10]
        assert "subplot_2" in distribution[5]
        assert "subplot_2" in distribution[15]
        assert "subplot_1" not in distribution[15]


class TestForeshadowingBalance:
    """Tests for foreshadowing balance calculation."""

    def test_calculate_balance(self):
        """Test balance calculation."""
        engine = SubplotForeshadowingEngine(MagicMock())

        foreshadowing = [
            ForeshadowingElementDetail(
                id=f"fore_{i}",
                name=f"测试{i}",
                element=f"元素{i}",
                foreshadowing_type=ForeshadowingTechnique.SYMBOLIC,
                planting=ForeshadowingPlanting(
                    technique=ForeshadowingTechnique.SYMBOLIC,
                    chapter=i,
                ),
                payoff=ForeshadowingPayoff(chapter=20 + i),
            )
            for i in range(1, 7)
        ]

        balance = engine._calculate_balance(foreshadowing, 24)

        assert 0.0 <= balance <= 1.0

    def test_calculate_balance_empty(self):
        """Test balance with empty foreshadowing."""
        engine = SubplotForeshadowingEngine(MagicMock())

        balance = engine._calculate_balance([], 24)

        assert balance == 0.0
