"""Tests for scene description engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from chai.engines.scene_description_engine import SceneDescriptionEngine
from chai.models.scene_description import (
    EnvironmentType, AtmosphereType, LightingCondition, TimeOfDay,
    SceneDescriptionPlan, SceneDescriptionDraft, SceneDescriptionAnalysis,
    SceneDescriptionTemplate, EnvironmentDetail, LightingDetail,
    AtmosphereDetail, VisualDetail, SensoryDetail, SpatialLayout,
    WeatherCondition, VisualDetailType, SensoryDetailType
)
from chai.services import AIService


class TestSceneDescriptionModels:
    """Test scene description models."""

    def test_environment_detail_creation(self):
        """Test creating an environment detail."""
        env = EnvironmentDetail(
            environment_type=EnvironmentType.NATURAL,
            location_name="魔法森林",
            architecture_style="fantasy",
            main_features=["古树", "藤蔓", "蘑菇"],
            spatial_layout=SpatialLayout.COMPLEX,
        )
        assert env.environment_type == EnvironmentType.NATURAL
        assert env.location_name == "魔法森林"
        assert "古树" in env.main_features

    def test_lighting_detail_creation(self):
        """Test creating a lighting detail."""
        light = LightingDetail(
            condition=LightingCondition.MOONLIGHT,
            light_source="月亮",
            light_color="银白色",
            shadow_intensity="high",
        )
        assert light.condition == LightingCondition.MOONLIGHT
        assert light.shadow_intensity == "high"

    def test_atmosphere_detail_creation(self):
        """Test creating an atmosphere detail."""
        atmos = AtmosphereDetail(
            atmosphere_type=AtmosphereType.MYSTERIOUS,
            atmosphere_intensity="strong",
            emotional_tone=["神秘", "好奇"],
            tension_level="moderate",
        )
        assert atmos.atmosphere_type == AtmosphereType.MYSTERIOUS
        assert "神秘" in atmos.emotional_tone

    def test_visual_detail_creation(self):
        """Test creating a visual detail."""
        visual = VisualDetail(
            detail_types=["color", "texture", "shadow"],
            color_palette=["暗红", "黑色", "金色"],
            focal_point="王座",
        )
        assert len(visual.detail_types) == 3
        assert "暗红" in visual.color_palette

    def test_sensory_detail_creation(self):
        """Test creating a sensory detail."""
        sensory = SensoryDetail(
            detail_types=["sound", "smell", "touch"],
            sound_descriptions=["风声", "远处狼嚎"],
            smell_descriptions=["泥土", "腐叶"],
            temperature_sensation="阴冷",
        )
        assert len(sensory.detail_types) == 3
        assert "风声" in sensory.sound_descriptions

    def test_scene_description_plan_creation(self):
        """Test creating a scene description plan."""
        plan = SceneDescriptionPlan(
            scene_id="scene_1",
            scene_location="古老城堡",
            time_setting=TimeOfDay.NIGHT,
            environment=EnvironmentDetail(
                environment_type=EnvironmentType.INDOOR,
                location_name="城堡大厅",
            ),
            lighting=LightingDetail(
                condition=LightingCondition.DIM,
                light_source="火把",
            ),
            atmosphere=AtmosphereDetail(
                atmosphere_type=AtmosphereType.OMINOUS,
                atmosphere_intensity="strong",
            ),
            description_length="long",
        )
        assert plan.scene_id == "scene_1"
        assert plan.time_setting == TimeOfDay.NIGHT
        assert plan.description_length == "long"

    def test_scene_description_draft_creation(self):
        """Test creating a scene description draft."""
        plan = SceneDescriptionPlan(
            scene_id="scene_1",
            scene_location="测试地点",
            time_setting=TimeOfDay.AFTERNOON,
        )
        draft = SceneDescriptionDraft(
            plan=plan,
            environment_description="一片广阔的平原",
            atmosphere_description="微风吹拂",
            combined_description="广阔的平原上，微风吹拂",
            word_count=12,
        )
        assert draft.word_count == 12
        assert draft.status == "draft"

    def test_scene_description_analysis_creation(self):
        """Test creating a scene description analysis."""
        analysis = SceneDescriptionAnalysis(
            scene_id="scene_1",
            atmosphere_consistency=0.85,
            visual_immersion=0.75,
            sensory_balance=0.65,
            descriptive_density="medium",
            issues=["光线描写不足"],
            suggestions=["增加阴影细节"],
        )
        assert analysis.atmosphere_consistency == 0.85
        assert "光线描写不足" in analysis.issues


class TestSceneDescriptionEngine:
    """Test scene description engine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock(spec=AIService)
        service.generate = AsyncMock(return_value="测试描述文字")
        return service

    @pytest.fixture
    def engine(self, mock_ai_service):
        """Create a scene description engine."""
        return SceneDescriptionEngine(mock_ai_service)

    def test_engine_creation(self, engine):
        """Test engine can be created."""
        assert engine is not None

    def test_get_all_templates(self, engine):
        """Test getting all templates."""
        templates = engine.get_all_templates()
        assert len(templates) == 10
        assert "dark_forest" in templates
        assert "grand_hall" in templates
        assert "peaceful_meadow" in templates

    def test_get_template(self, engine):
        """Test getting a specific template."""
        template = engine.get_template("dark_forest")
        assert template is not None
        assert template.name == "黑暗森林"
        assert template.environment_type == EnvironmentType.NATURAL
        assert template.atmosphere_type == AtmosphereType.OMINOUS

    def test_get_template_not_found(self, engine):
        """Test getting a non-existent template."""
        template = engine.get_template("nonexistent")
        assert template is None

    @pytest.mark.asyncio
    async def test_generate_description(self, engine, mock_ai_service):
        """Test generating a scene description."""
        draft = await engine.generate_description(
            scene_id="scene_test",
            scene_location="神秘森林",
            time_setting=TimeOfDay.NIGHT,
            environment_type=EnvironmentType.NATURAL,
            atmosphere_type=AtmosphereType.MYSTERIOUS,
            lighting_condition=LightingCondition.DARK,
            description_length="medium",
        )
        # AI service returns mock text
        mock_ai_service.generate.assert_called()
        assert draft.plan.scene_id == "scene_test"
        assert draft.plan.scene_location == "神秘森林"

    @pytest.mark.asyncio
    async def test_generate_from_template(self, engine, mock_ai_service):
        """Test generating from a template."""
        draft = await engine.generate_from_template(
            template_name="dark_forest",
            scene_id="scene_forest",
            scene_location="黑暗森林深处",
        )
        mock_ai_service.generate.assert_called()
        assert draft.plan.scene_id == "scene_forest"

    def test_analyze_description(self, engine):
        """Test analyzing a scene description."""
        plan = SceneDescriptionPlan(
            scene_id="scene_1",
            scene_location="测试",
            time_setting=TimeOfDay.AFTERNOON,
            description_length="medium",
        )
        draft = SceneDescriptionDraft(
            plan=plan,
            combined_description="这是一段中等长度的测试描述文字内容。",
            word_count=20,
        )

        analysis = engine.analyze_description(draft)
        assert analysis.scene_id == "scene_1"
        assert analysis.descriptive_density in ["too_sparse", "sparse", "medium", "rich", "too_rich"]

    def test_export_draft(self, engine):
        """Test exporting a draft."""
        plan = SceneDescriptionPlan(
            scene_id="scene_export",
            scene_location="导出测试地点",
            time_setting=TimeOfDay.EVENING,
            environment=EnvironmentDetail(
                environment_type=EnvironmentType.URBAN,
            ),
            lighting=LightingDetail(
                condition=LightingCondition.ARTIFICIAL,
            ),
            atmosphere=AtmosphereDetail(
                atmosphere_type=AtmosphereType.JOYFUL,
            ),
        )
        draft = SceneDescriptionDraft(
            plan=plan,
            combined_description="导出测试内容",
            word_count=6,
        )

        exported = engine.export_draft(draft)
        assert exported["scene_id"] == "scene_export"
        assert exported["scene_location"] == "导出测试地点"
        assert exported["word_count"] == 6
        assert exported["status"] == "draft"


class TestTemplateTypes:
    """Test scene description template types."""

    def test_all_templates_have_required_fields(self):
        """Test all templates have required fields."""
        engine = SceneDescriptionEngine(MagicMock(spec=AIService))
        for name, template in engine.TEMPLATES.items():
            assert template.name is not None
            assert template.environment_type is not None
            assert template.atmosphere_type is not None
            assert template.description_length in ["brief", "short", "medium", "long"]

    def test_template_dark_forest(self):
        """Test dark_forest template details."""
        engine = SceneDescriptionEngine(MagicMock(spec=AIService))
        template = engine.get_template("dark_forest")
        assert template.environment_type == EnvironmentType.NATURAL
        assert template.atmosphere_type == AtmosphereType.OMINOUS
        assert template.lighting_condition == LightingCondition.DARK

    def test_template_grand_hall(self):
        """Test grand_hall template details."""
        engine = SceneDescriptionEngine(MagicMock(spec=AIService))
        template = engine.get_template("grand_hall")
        assert template.environment_type == EnvironmentType.INDOOR
        assert template.atmosphere_type == AtmosphereType.EPIC
        assert template.lighting_condition == LightingCondition.DRAMATIC

    def test_template_stormy_sea(self):
        """Test stormy_sea template details."""
        engine = SceneDescriptionEngine(MagicMock(spec=AIService))
        template = engine.get_template("stormy_sea")
        assert template.environment_type == EnvironmentType.OUTDOOR
        assert template.atmosphere_type == AtmosphereType.TENSE
        assert VisualDetailType.MOVEMENT in template.visual_detail_types


class TestSceneDescriptionEnums:
    """Test scene description enum values."""

    def test_environment_types(self):
        """Test EnvironmentType enum."""
        assert len(EnvironmentType) == 8
        assert EnvironmentType.INDOOR == "indoor"
        assert EnvironmentType.NATURAL == "natural"
        assert EnvironmentType.FANTASY == "fantasy"

    def test_lighting_conditions(self):
        """Test LightingCondition enum."""
        assert len(LightingCondition) == 10
        assert LightingCondition.BRIGHT == "bright"
        assert LightingCondition.DARK == "dark"
        assert LightingCondition.MOONLIGHT == "moonlight"

    def test_atmosphere_types(self):
        """Test AtmosphereType enum."""
        assert len(AtmosphereType) == 17
        assert AtmosphereType.NEUTRAL == "neutral"
        assert AtmosphereType.TENSE == "tense"
        assert AtmosphereType.PEACEFUL == "peaceful"
        assert AtmosphereType.MYSTERIOUS == "mysterious"
        assert AtmosphereType.ROMANTIC == "romantic"
        assert AtmosphereType.EPIC == "epic"

    def test_time_of_day(self):
        """Test TimeOfDay enum."""
        assert len(TimeOfDay) == 7
        assert TimeOfDay.DAWN == "dawn"
        assert TimeOfDay.NIGHT == "night"
        assert TimeOfDay.MIDNIGHT == "midnight"

    def test_weather_conditions(self):
        """Test WeatherCondition enum."""
        assert len(WeatherCondition) == 11
        assert WeatherCondition.CLEAR == "clear"
        assert WeatherCondition.RAINY == "rainy"
        assert WeatherCondition.STORMY == "stormy"

    def test_visual_detail_types(self):
        """Test VisualDetailType enum."""
        assert len(VisualDetailType) == 9
        assert VisualDetailType.COLOR == "color"
        assert VisualDetailType.TEXTURE == "texture"
        assert VisualDetailType.SHADOW == "shadow"

    def test_sensory_detail_types(self):
        """Test SensoryDetailType enum."""
        assert len(SensoryDetailType) == 5
        assert SensoryDetailType.SOUND == "sound"
        assert SensoryDetailType.SMELL == "smell"
        assert SensoryDetailType.TOUCH == "touch"

    def test_spatial_layout(self):
        """Test SpatialLayout enum."""
        assert len(SpatialLayout) == 8
        assert SpatialLayout.CRAMPED == "cramped"
        assert SpatialLayout.SPACIOUS == "spacious"
        assert SpatialLayout.CHAOTIC == "chaotic"
