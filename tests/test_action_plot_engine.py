"""Tests for ActionPlotEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chai.models.action_plot import (
    ActionType, ActionIntensity, ActionPhase, PlotAdvancementType,
    PlotBeatType, PacingType, ActionPlotPlan, ActionPlotDraft,
    ActionPlotTemplate, ActionSequence, ActionBeat,
)
from chai.engines.action_plot_engine import ActionPlotEngine


class TestActionPlotEngine:
    """Test cases for ActionPlotEngine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create mock AI service."""
        service = MagicMock()
        service.generate = AsyncMock(return_value="测试生成的动作与情节内容")
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create engine with mock service."""
        return ActionPlotEngine(mock_ai_service)

    @pytest.fixture
    def sample_characters(self):
        """Create sample characters."""
        char1 = MagicMock()
        char1.name = "张三"
        char1.personality_description = "勇敢果断"
        char1.skills = ["剑术", "格斗"]

        char2 = MagicMock()
        char2.name = "李四"
        char2.personality_description = "冷静狡猾"
        char2.skills = ["阴谋", "策略"]

        return [char1, char2]

    def test_templates_exist(self, engine):
        """Test that templates are loaded."""
        templates = engine.get_all_templates()
        assert len(templates) > 0
        assert "combat_clash" in templates
        assert "chase_escape" in templates
        assert "revelation_climax" in templates

    def test_get_template(self, engine):
        """Test getting a specific template."""
        template = engine.get_template("combat_clash")
        assert template is not None
        assert template.name == "战斗冲突"
        assert ActionType.COMBAT in template.applicable_action_types

    def test_get_template_not_found(self, engine):
        """Test getting non-existent template."""
        template = engine.get_template("nonexistent")
        assert template is None

    def test_get_matching_template(self, engine):
        """Test template matching by action type."""
        template = engine._get_matching_template(
            ActionType.COMBAT,
            PlotAdvancementType.MAIN_PLOT
        )
        assert template is not None

    def test_build_action_sequence_prompt(self, engine, sample_characters):
        """Test action prompt building."""
        plan = ActionPlotPlan(
            id="test_plan",
            scene_id="scene_1",
            primary_action_type=ActionType.COMBAT,
            primary_plot_type=PlotAdvancementType.MAIN_PLOT,
            stakes_description="生死之战",
            target_intensity=ActionIntensity.HIGH,
            target_tension=0.7,
            target_action_count=5,
            balance_action_plot=0.6,
            pacing_type=PacingType.CRESCENDO,
        )

        prompt = engine._build_action_sequence_prompt(plan, sample_characters)

        assert "战斗冲突" in prompt or "combat" in prompt.lower()
        assert "生死之战" in prompt
        assert "角色1" in prompt or "张三" in prompt
        assert "角色2" in prompt or "李四" in prompt

    def test_build_plot_advancement_prompt(self, engine, sample_characters):
        """Test plot prompt building."""
        plan = ActionPlotPlan(
            id="test_plan",
            scene_id="scene_1",
            primary_action_type=ActionType.COMBAT,
            primary_plot_type=PlotAdvancementType.MAIN_PLOT,
            stakes_description="拯救世界",
            target_plot_count=3,
        )

        prompt = engine._build_plot_advancement_prompt(plan, sample_characters)

        assert "情节推进" in prompt or "plot" in prompt.lower()
        assert "拯救世界" in prompt

    def test_score_draft(self, engine):
        """Test draft scoring."""
        plan = ActionPlotPlan(
            id="test_plan",
            scene_id="scene_1",
            primary_action_type=ActionType.COMBAT,
            primary_plot_type=PlotAdvancementType.MAIN_PLOT,
            target_action_count=5,
            target_plot_count=3,
            target_tension=0.7,
            stakes_description="生死之战",
            balance_action_plot=0.5,
            pacing_type=PacingType.MODERATE,
        )

        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="test_plan",
            scene_id="scene_1",
            action_content="动作内容" * 50,
            plot_content="情节内容" * 30,
            combined_content="综合内容" * 80,
            action_word_count=500,
            plot_word_count=300,
            total_word_count=800,
            status="draft",
        )

        scored = engine._score_draft(draft, plan, None)

        assert scored.action_coherence_score > 0
        assert scored.plot_coherence_score > 0
        assert scored.tension_score > 0
        assert scored.excitement_score > 0
        assert scored.advances_plot is True
        assert scored.has_stakes_clarity is True

    def test_analyze(self, engine):
        """Test draft analysis."""
        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            action_content="动作内容",
            plot_content="情节内容",
            combined_content="综合内容",
            action_word_count=100,
            plot_word_count=50,
            total_word_count=150,
            action_coherence_score=0.5,
            plot_coherence_score=0.5,
            pacing_score=0.6,
            tension_score=0.4,
            status="draft",
        )

        analysis = engine.analyze(draft)

        assert analysis.draft_id == "draft_1"
        assert analysis.action_coherence > 0
        assert analysis.plot_coherence > 0
        assert len(analysis.critical_issues) > 0 or len(analysis.minor_issues) > 0

    def test_analyze_long_action(self, engine):
        """Test analysis of very long action content."""
        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            action_content="x" * 3000,
            plot_content="x" * 100,
            combined_content="x" * 3100,
            action_word_count=3000,
            plot_word_count=100,
            total_word_count=3100,
            action_coherence_score=0.9,
            plot_coherence_score=0.3,
            pacing_score=0.5,
            tension_score=0.6,
            status="draft",
        )

        analysis = engine.analyze(draft)

        # Should flag long action content
        assert len(analysis.critical_issues) > 0 or len(analysis.minor_issues) > 0

    def test_export_draft(self, engine):
        """Test draft export."""
        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            action_content="动作内容",
            plot_content="情节内容",
            combined_content="综合内容",
            action_word_count=100,
            plot_word_count=50,
            total_word_count=150,
            action_coherence_score=0.7,
            plot_coherence_score=0.6,
            tension_score=0.5,
            has_climactic_moment=True,
            advances_plot=True,
            status="draft",
        )

        exported = engine.export_draft(draft)

        assert exported["draft_id"] == "draft_1"
        assert exported["scene_id"] == "scene_1"
        assert exported["total_word_count"] == 150
        assert exported["has_climactic_moment"] is True
        assert "action_coherence_score" in exported

    @pytest.mark.asyncio
    async def test_generate_requires_ai(self, engine, sample_characters):
        """Test that generation requires AI service."""
        plan = ActionPlotPlan(
            id="test_plan",
            scene_id="scene_1",
            primary_action_type=ActionType.COMBAT,
            primary_plot_type=PlotAdvancementType.MAIN_PLOT,
        )

        # This would need async mock to fully test
        # Just verify the method exists and is async
        import inspect
        assert inspect.iscoroutinefunction(engine.generate)

    @pytest.mark.asyncio
    async def test_revise_requires_ai(self, engine):
        """Test that revision requires AI service."""
        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
            action_content="原始动作内容",
            plot_content="原始情节内容",
            combined_content="原始综合内容",
            status="draft",
        )

        revision_notes = ["增加更多动作细节"]

        # This would need async mock to fully test
        result = await engine.revise(draft, revision_notes)

        assert result.original_draft == draft
        assert result.revision_notes == revision_notes
        assert result.revised_content != ""

    def test_action_type_enum_values(self):
        """Test ActionType enum has expected values."""
        assert ActionType.COMBAT.value == "combat"
        assert ActionType.CHASE.value == "chase"
        assert ActionType.ESCAPE.value == "escape"
        assert ActionType.REVELATION.value == "revelation"
        assert ActionType.SACRIFICE.value == "sacrifice"

    def test_action_intensity_enum_values(self):
        """Test ActionIntensity enum has expected values."""
        assert ActionIntensity.LOW.value == "low"
        assert ActionIntensity.MODERATE.value == "moderate"
        assert ActionIntensity.HIGH.value == "high"
        assert ActionIntensity.EXTREME.value == "extreme"
        assert ActionIntensity.CLIMACTIC.value == "climactic"

    def test_plot_advancement_type_values(self):
        """Test PlotAdvancementType enum."""
        assert PlotAdvancementType.MAIN_PLOT.value == "main_plot"
        assert PlotAdvancementType.REVELATION.value == "revelation"
        assert PlotAdvancementType.TURNING_POINT.value == "turning_point"
        assert PlotAdvancementType.CHARACTER_DEVELOPMENT.value == "character_development"

    def test_pacing_type_values(self):
        """Test PacingType enum."""
        assert PacingType.SLOW.value == "slow"
        assert PacingType.MODERATE.value == "moderate"
        assert PacingType.FAST.value == "fast"
        assert PacingType.CRESCENDO.value == "crescendo"
        assert PacingType.DENouement.value == "denouement"

    def test_action_plot_template_structure(self):
        """Test ActionPlotTemplate has required fields."""
        template = ActionPlotTemplate(
            id="test",
            name="测试模板",
            applicable_action_types=[ActionType.COMBAT],
            applicable_plot_types=[PlotAdvancementType.MAIN_PLOT],
            typical_beat_count=5,
        )

        assert template.id == "test"
        assert template.name == "测试模板"
        assert ActionType.COMBAT in template.applicable_action_types
        assert template.typical_beat_count == 5

    def test_action_sequence_model(self):
        """Test ActionSequence model."""
        sequence = ActionSequence(
            id="seq_1",
            scene_id="scene_1",
            action_type=ActionType.COMBAT,
            title="战斗场景",
            starting_intensity=ActionIntensity.LOW,
            peak_intensity=ActionIntensity.EXTREME,
            ending_intensity=ActionIntensity.MODERATE,
        )

        assert sequence.id == "seq_1"
        assert sequence.action_type == ActionType.COMBAT
        assert sequence.peak_intensity == ActionIntensity.EXTREME

    def test_action_beat_model(self):
        """Test ActionBeat model."""
        beat = ActionBeat(
            id="beat_1",
            sequence_id="seq_1",
            description="主角出剑",
            action_type=ActionType.COMBAT,
            phase=ActionPhase.ESCALATION,
            intensity=ActionIntensity.HIGH,
            tension_level=0.8,
        )

        assert beat.id == "beat_1"
        assert beat.phase == ActionPhase.ESCALATION
        assert beat.tension_level == 0.8

    def test_action_plot_plan_defaults(self):
        """Test ActionPlotPlan default values."""
        plan = ActionPlotPlan(
            id="plan_1",
            scene_id="scene_1",
        )

        assert plan.primary_action_type == ActionType.CONFLICT
        assert plan.primary_plot_type == PlotAdvancementType.MAIN_PLOT
        assert plan.target_intensity == ActionIntensity.MODERATE
        assert plan.target_tension == 0.5
        assert plan.target_action_count == 5
        assert plan.target_plot_count == 3
        assert plan.balance_action_plot == 0.5

    def test_action_plot_draft_defaults(self):
        """Test ActionPlotDraft default values."""
        draft = ActionPlotDraft(
            id="draft_1",
            plan_id="plan_1",
            scene_id="scene_1",
        )

        assert draft.action_coherence_score == 0.0
        assert draft.plot_coherence_score == 0.0
        assert draft.has_climactic_moment is False
        assert draft.advances_plot is False
        assert draft.status == "draft"

    def test_get_all_templates_returns_copy(self, engine):
        """Test that get_all_templates returns a copy."""
        templates1 = engine.get_all_templates()
        templates2 = engine.get_all_templates()

        assert templates1 is not templates2
        assert templates1.keys() == templates2.keys()


class TestActionPlotTemplates:
    """Test specific templates."""

    @pytest.fixture
    def mock_ai_service(self):
        service = MagicMock()
        service.generate = AsyncMock(return_value="测试内容")
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        return ActionPlotEngine(mock_ai_service)

    def test_combat_clash_template(self, engine):
        """Test combat_clash template structure."""
        template = engine.get_template("combat_clash")

        assert template is not None
        assert ActionType.COMBAT in template.applicable_action_types
        assert len(template.intensity_curve) > 0
        assert template.peak_tension > template.starting_tension

    def test_chase_escape_template(self, engine):
        """Test chase_escape template."""
        template = engine.get_template("chase_escape")

        assert template is not None
        assert ActionType.CHASE in template.applicable_action_types
        assert template.pacing_pattern == PacingType.FAST

    def test_revelation_climax_template(self, engine):
        """Test revelation_climax template."""
        template = engine.get_template("revelation_climax")

        assert template is not None
        assert PlotAdvancementType.REVELATION in template.applicable_plot_types
        assert template.typical_action_ratio < 0.5  # More plot than action

    def test_rescue_mission_template(self, engine):
        """Test rescue_mission template."""
        template = engine.get_template("rescue_mission")

        assert template is not None
        assert ActionType.RESCUE in template.applicable_action_types
        assert template.action_detail_level == "detailed"

    def test_sacrifice_moment_template(self, engine):
        """Test sacrifice_moment template."""
        template = engine.get_template("sacrifice_moment")

        assert template is not None
        assert ActionType.SACRIFICE in template.applicable_action_types
        assert template.ending_tension < template.peak_tension

    def test_all_templates_have_required_fields(self, engine):
        """Test all templates have required fields."""
        templates = engine.get_all_templates()

        for name, template in templates.items():
            assert template.id, f"Template {name} missing id"
            assert template.name, f"Template {name} missing name"
            assert len(template.applicable_action_types) > 0, f"Template {name} missing action types"
            assert template.typical_beat_count > 0, f"Template {name} missing beat count"