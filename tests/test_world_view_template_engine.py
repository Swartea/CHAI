"""Tests for WorldViewTemplateEngine."""

import pytest
from chai.models.world_view_template import (
    WorldViewTemplateType,
    GeographyImportance,
    PoliticsImportance,
    CultureImportance,
    HistoryImportance,
    MagicSystemImportance,
    SocialStructureImportance,
    GeographyConfig,
    PoliticsConfig,
    CultureConfig,
    HistoryConfig,
    MagicSystemConfig,
    SocialStructureConfig,
    WorldViewTemplate,
    WorldViewTemplateProfile,
    WorldViewTemplateLibrary,
    TemplateApplicationResult,
    TemplateCustomizationRequest,
)
from chai.engines.world_view_template_engine import WorldViewTemplateEngine


class TestWorldViewTemplateEngine:
    """Test suite for WorldViewTemplateEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = WorldViewTemplateEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine is not None
        assert len(self.engine._templates) > 0

    def test_get_builtin_templates(self):
        """Test getting built-in templates."""
        templates = self.engine.get_builtin_templates()
        assert len(templates) > 0
        for template in templates.values():
            assert template.is_builtin is True

    def test_get_custom_templates_empty(self):
        """Test getting custom templates when none exist."""
        templates = self.engine.get_custom_templates()
        assert len(templates) == 0

    def test_get_template_xianhua(self):
        """Test getting xianhua world view template."""
        template = self.engine.get_template("xianhua")
        assert template is not None
        assert template.template_type == WorldViewTemplateType.XIANHUA
        assert "仙侠" in template.template_description
        assert template.magic_system.has_magic is True
        assert template.magic_system.cultivation_system is True
        assert template.geography.importance == GeographyImportance.HIGH

    def test_get_template_dushi(self):
        """Test getting dushi (urban) world view template."""
        template = self.engine.get_template("dushi")
        assert template is not None
        assert template.template_type == WorldViewTemplateType.DUSHI
        assert template.magic_system.has_magic is False
        assert template.magic_system.technology_level == "modern"
        assert template.social_structure.importance == SocialStructureImportance.ESSENTIAL

    def test_get_template_kehuan(self):
        """Test getting kehuan (sci-fi) world view template."""
        template = self.engine.get_template("kehuan")
        assert template is not None
        assert template.template_type == WorldViewTemplateType.KEHAN
        assert template.magic_system.has_magic is False
        assert template.magic_system.technology_level == "futuristic"
        assert "星际" in template.tags or "太空" in template.tags

    def test_get_template_jianyu(self):
        """Test getting jianyu (wuxia) world view template."""
        template = self.engine.get_template("jianyu")
        assert template is not None
        assert template.template_type == WorldViewTemplateType.JIANYU
        assert template.magic_system.has_magic is True
        assert template.magic_system.magic_type == "martial_arts"
        assert "武侠" in template.tags

    def test_get_template_shenmo(self):
        """Test getting shenmo (divine) world view template."""
        template = self.engine.get_template("shenmo")
        assert template is not None
        assert template.template_type == WorldViewTemplateType.SHENMO
        assert template.magic_system.has_magic is True
        assert template.magic_system.magic_type == "divine"
        assert template.history.importance == HistoryImportance.ESSENTIAL

    def test_get_all_templates(self):
        """Test getting all templates."""
        templates = self.engine.get_all_templates()
        assert len(templates) >= 8  # At least 8 built-in templates
        assert "xianhua" in templates
        assert "yuanman" in templates
        assert "dushi" in templates
        assert "kehuan" in templates

    def test_create_custom_template(self):
        """Test creating a custom template."""
        template = self.engine.create_template(
            template_name="My Custom World",
            template_name_cn="我的自定义世界",
            template_description="A custom world template",
            template_type=WorldViewTemplateType.custom,
            tags=["custom", "test"],
        )
        assert template is not None
        assert template.is_custom is True
        assert template.is_builtin is False
        assert template.template_name == "My Custom World"
        assert template.template_name_cn == "我的自定义世界"
        assert "custom" in template.tags
        assert "test" in template.tags

    def test_create_profile(self):
        """Test creating a template profile."""
        profile = self.engine.create_profile(
            template_id="xianhua",
            genre_hint="xianxia",
            theme_hint="修仙",
        )
        assert profile is not None
        assert profile.template.template_id == "xianhua"
        assert profile.genre_hint == "xianxia"
        assert profile.theme_hint == "修仙"

    def test_create_profile_nonexistent(self):
        """Test creating profile for nonexistent template."""
        profile = self.engine.create_profile(template_id="nonexistent")
        assert profile is None

    def test_apply_template(self):
        """Test applying a template."""
        result = self.engine.apply_template("xianhua")
        assert result is not None
        assert result.template_id == "xianhua"
        assert "geography" in result.generation_hints
        assert "magic_system" in result.generation_hints
        assert result.generation_hints["magic_system"]["has_magic"] is True
        assert result.generation_hints["magic_system"]["cultivation_system"] is True

    def test_apply_template_with_customizations(self):
        """Test applying a template with customizations."""
        result = self.engine.apply_template(
            "dushi",
            customizations={"has_magic": True, "magic_type": "psychic"},
        )
        assert result is not None
        assert result.template_id == "dushi"
        assert any("has_magic" in m for m in result.modifications)
        assert result.generation_hints["magic_system"]["has_magic"] is True
        assert result.generation_hints["magic_system"]["magic_type"] == "psychic"

    def test_apply_nonexistent_template(self):
        """Test applying nonexistent template."""
        result = self.engine.apply_template("nonexistent")
        assert result is None

    def test_duplicate_template(self):
        """Test duplicating a template."""
        new_template = self.engine.duplicate_template(
            "xianhua",
            new_name="My Xianxia Variant",
            new_name_cn="我的仙侠变体",
        )
        assert new_template is not None
        assert new_template.is_custom is True
        assert new_template.is_builtin is False
        assert new_template.template_name == "My Xianxia Variant"
        assert new_template.magic_system.cultivation_system is True

    def test_update_template(self):
        """Test updating a custom template."""
        # First create a custom template
        template = self.engine.create_template(
            template_name="Update Test",
            template_name_cn="更新测试",
            template_description="Before update",
        )
        template_id = template.template_id

        # Update it
        updated = self.engine.update_template(
            template_id,
            {"template_description": "After update"},
        )
        assert updated is not None
        assert updated.template_description == "After update"

    def test_delete_custom_template(self):
        """Test deleting a custom template."""
        # First create a custom template
        template = self.engine.create_template(
            template_name="Delete Test",
            template_name_cn="删除测试",
            template_description="Will be deleted",
        )
        template_id = template.template_id

        # Delete it
        deleted = self.engine.delete_template(template_id)
        assert deleted is True
        assert self.engine.get_template(template_id) is None

    def test_delete_builtin_template_fails(self):
        """Test that deleting built-in template fails."""
        deleted = self.engine.delete_template("xianhua")
        assert deleted is False
        assert self.engine.get_template("xianhua") is not None

    def test_search_templates(self):
        """Test searching templates."""
        results = self.engine.search_templates("仙侠")
        assert len(results) > 0
        assert any(t.template_id == "xianhua" for t in results)

    def test_search_templates_by_description(self):
        """Test searching templates by description."""
        results = self.engine.search_templates("冒险")
        assert len(results) > 0

    def test_get_templates_by_tag(self):
        """Test getting templates by tag."""
        templates = self.engine.get_templates_by_tag("武侠")
        assert len(templates) > 0
        assert all("武侠" in t.tags for t in templates)

    def test_get_templates_by_type(self):
        """Test getting templates by type."""
        templates = self.engine.get_templates_by_type(WorldViewTemplateType.XIANHUA)
        assert len(templates) > 0
        assert all(t.template_type == WorldViewTemplateType.XIANHUA for t in templates)

    def test_get_all_tags(self):
        """Test getting all unique tags."""
        tags = self.engine.get_all_tags()
        assert len(tags) > 0
        assert "仙侠" in tags or "玄幻" in tags or "都市" in tags

    def test_export_template(self):
        """Test exporting a template."""
        exported = self.engine.export_template("xianhua")
        assert exported is not None
        assert exported["template_id"] == "xianhua"
        assert "template_name" in exported
        assert "geography" in exported

    def test_export_nonexistent_template(self):
        """Test exporting nonexistent template."""
        exported = self.engine.export_template("nonexistent")
        assert exported is None

    def test_import_template(self):
        """Test importing a template."""
        template_data = {
            "template_id": "imported_test",
            "template_name": "Imported Template",
            "template_name_cn": "导入的模板",
            "template_description": "Test import",
            "template_type": "custom",
            "is_builtin": False,
            "is_custom": True,
            "tags": ["imported"],
            "author": "test",
            "version": "1.0",
        }
        imported = self.engine.import_template(template_data)
        assert imported is not None
        assert imported.template_id == "imported_test"
        assert imported.is_custom is True

    def test_get_template_summary(self):
        """Test getting template summary."""
        summary = self.engine.get_template_summary("xianhua")
        assert summary is not None
        assert "仙侠" in summary or "xianhua" in summary.lower()
        assert "重要性配置" in summary

    def test_get_template_summary_nonexistent(self):
        """Test getting summary for nonexistent template."""
        summary = self.engine.get_template_summary("nonexistent")
        assert summary is None

    def test_geography_importance_levels(self):
        """Test all geography importance levels."""
        for level in GeographyImportance:
            config = GeographyConfig(importance=level)
            assert config.importance == level

    def test_world_view_template_type_enum(self):
        """Test WorldViewTemplateType enum values."""
        assert WorldViewTemplateType.XIANHUA.value == "xianhua"
        assert WorldViewTemplateType.YUANMAN.value == "yuanman"
        assert WorldViewTemplateType.DUSHI.value == "dushi"
        assert WorldViewTemplateType.KEHAN.value == "kehan"
        assert WorldViewTemplateType.XUANYI.value == "xuanyi"
        assert WorldViewTemplateType.YANQING.value == "yanqing"
        assert WorldViewTemplateType.JIANYU.value == "jianyu"
        assert WorldViewTemplateType.SHENMO.value == "shenmo"
        assert WorldViewTemplateType.custom.value == "custom"

    def test_world_view_template_get_importance_summary(self):
        """Test WorldViewTemplate importance summary."""
        template = self.engine.get_template("xianhua")
        assert template is not None
        summary = template.get_importance_summary()
        assert "geography" in summary
        assert "politics" in summary
        assert "culture" in summary
        assert "history" in summary
        assert "magic_system" in summary
        assert "social_structure" in summary

    def test_template_application_result_model(self):
        """Test TemplateApplicationResult model."""
        result = TemplateApplicationResult(
            template_id="test",
            applied_settings={"key": "value"},
            warnings=["warning1"],
            modifications=["change1"],
            generation_hints={"hint": "value"},
        )
        assert result.template_id == "test"
        assert result.applied_settings["key"] == "value"
        assert len(result.warnings) == 1
        assert len(result.modifications) == 1

    def test_world_view_template_library_model(self):
        """Test WorldViewTemplateLibrary model."""
        template = WorldViewTemplate(
            template_id="library_test",
            template_name="Library Test",
            template_name_cn="库测试",
            template_description="Test library",
            template_type=WorldViewTemplateType.custom,
        )
        library = WorldViewTemplateLibrary()
        library.add_template(template)
        assert "library_test" in library.templates
        retrieved = library.get_templates_by_tag("test")
        assert len(retrieved) == 0  # No tags set

    def test_world_view_template_library_remove(self):
        """Test removing from library."""
        template = WorldViewTemplate(
            template_id="remove_test",
            template_name="Remove Test",
            template_name_cn="移除测试",
            template_description="Test remove",
            template_type=WorldViewTemplateType.custom,
            tags=["removable"],
        )
        library = WorldViewTemplateLibrary()
        library.add_template(template)
        assert library.remove_template("remove_test") is True
        assert "remove_test" not in library.templates
        assert library.remove_template("nonexistent") is False
