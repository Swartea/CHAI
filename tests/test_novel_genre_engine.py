"""Tests for NovelGenreEngine."""

import pytest
from chai.models.novel_genre import (
    NovelGenreType,
    WorldSettingType,
    MagicTechnologyLevel,
    PlotStructureType,
    RomanceType,
    ConflictType,
    TargetAudience,
    GenreWorldConfig,
    GenreCharacterTemplate,
    GenrePlotConfig,
    GenreStyleConfig,
    GenreToneConfig,
    NovelGenreProfile,
    GenreAnalysisResult,
    GenreTemplate,
    GenreRecommendation,
)
from chai.engines.novel_genre_engine import NovelGenreEngine


class TestNovelGenreEngine:
    """Test suite for NovelGenreEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = NovelGenreEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine is not None
        assert len(self.engine._templates) > 0

    def test_get_template_xianhua(self):
        """Test getting xianhua genre template."""
        template = self.engine.get_template("xianhua")
        assert template is not None
        assert template.genre == NovelGenreType.XIANHUA
        assert "仙侠" in template.template_description
        assert template.world_config.magic_tech_level == MagicTechnologyLevel.HIGH
        assert template.world_config.requires_cultivation_system is True

    def test_get_template_dushi(self):
        """Test getting dushi (urban) genre template."""
        template = self.engine.get_template("dushi")
        assert template is not None
        assert template.genre == NovelGenreType.DUSHI
        assert "都市" in template.template_description
        assert template.world_config.world_setting_type == WorldSettingType.URBAN_MODERN
        assert template.character_template.romance_importance == RomanceType.PRIMARY_ROMANCE

    def test_get_template_xuanyi(self):
        """Test getting xuanyi (mystery) genre template."""
        template = self.engine.get_template("xuanyi")
        assert template is not None
        assert template.genre == NovelGenreType.XUANYI
        assert "悬疑" in template.template_description
        assert template.plot_config.recommended_structure == PlotStructureType.MYSTERY_STRUCTURE
        assert template.character_template.romance_importance == RomanceType.NONE

    def test_get_template_kehuan(self):
        """Test getting kehuan (sci-fi) genre template."""
        template = self.engine.get_template("kehuan")
        assert template is not None
        assert template.genre == NovelGenreType.KEHAN
        assert "科幻" in template.template_description
        assert template.world_config.world_setting_type == WorldSettingType.SCI_FI_WORLD

    def test_get_template_yuanman(self):
        """Test getting yuanman (fantasy) genre template."""
        template = self.engine.get_template("yuanman")
        assert template is not None
        assert template.genre == NovelGenreType.YUANMAN
        assert template.world_config.requires_cultivation_system is False

    def test_get_template_case_insensitive(self):
        """Test template lookup is case insensitive."""
        template1 = self.engine.get_template("XIANHUA")
        template2 = self.engine.get_template("xianhua")
        assert template1 is not None
        assert template2 is not None
        assert template1.genre == template2.genre

    def test_get_nonexistent_template(self):
        """Test getting non-existent template returns None."""
        template = self.engine.get_template("nonexistent_genre")
        assert template is None

    def test_get_all_templates(self):
        """Test getting all templates."""
        templates = self.engine.get_all_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "xianhua" in templates
        assert "dushi" in templates

    def test_create_genre_profile(self):
        """Test creating genre profile from genre type."""
        profile = self.engine.create_genre_profile(NovelGenreType.XIANHUA)
        assert profile is not None
        assert profile.genre == NovelGenreType.XIANHUA
        assert profile.world_config is not None
        assert profile.character_template is not None
        assert profile.plot_config is not None
        assert profile.style_config is not None
        assert profile.tone_config is not None

    def test_create_genre_profile_xianhua(self):
        """Test xianhua genre profile has correct settings."""
        profile = self.engine.create_genre_profile(NovelGenreType.XIANHUA)
        assert profile.world_config.magic_system_importance == 1.0
        assert profile.world_config.requires_cultivation_system is True
        assert "修仙" in profile.character_template.common_archetypes or len(profile.character_template.common_archetypes) > 0
        assert profile.plot_config.plot_complexity == "complex"
        assert "epic" in profile.style_config.typical_tones

    def test_create_genre_profile_dushi(self):
        """Test dushi genre profile has correct settings."""
        profile = self.engine.create_genre_profile(NovelGenreType.DUSHI)
        assert profile.world_config.world_setting_type == WorldSettingType.URBAN_MODERN
        assert profile.world_config.requires_modern_technology is True
        assert profile.character_template.romance_importance == RomanceType.PRIMARY_ROMANCE
        assert profile.target_audience == TargetAudience.NEW_ADULT

    def test_detect_genre_from_content_xianhua(self):
        """Test genre detection for xianhua content."""
        content = "主角修炼仙法，突破金丹境界，渡劫飞升。师傅说修仙之路需要机缘。"
        result = self.engine.detect_genre_from_content(content)
        assert result is not None
        assert result.detected_genre == NovelGenreType.XIANHUA
        assert result.confidence > 0
        assert NovelGenreType.XIANHUA.value in result.genre_evidence

    def test_detect_genre_from_content_dushi(self):
        """Test genre detection for dushi content."""
        content = "他在都市创业，与总裁谈判合同。同事们都在职场努力工作。"
        result = self.engine.detect_genre_from_content(content)
        assert result is not None
        assert result.confidence > 0

    def test_detect_genre_from_content_xuanyi(self):
        """Test genre detection for mystery content."""
        content = "侦探调查谋杀案，嫌疑人有不在场证明。证据指向一个秘密阴谋。"
        result = self.engine.detect_genre_from_content(content)
        assert result is not None
        assert result.confidence > 0

    def test_detect_genre_from_content_empty(self):
        """Test genre detection with empty content."""
        result = self.engine.detect_genre_from_content("")
        assert result is not None
        assert result.confidence == 0.0

    def test_detect_genre_from_title_xianhua(self):
        """Test genre detection from title for xianxia."""
        results = self.engine.detect_genre_from_title("凡人修仙传")
        assert len(results) > 0
        top_genre, confidence = results[0]
        assert top_genre == NovelGenreType.XIANHUA
        assert confidence > 0

    def test_detect_genre_from_title_dushi(self):
        """Test genre detection from title for urban novel."""
        results = self.engine.detect_genre_from_title("都市狂少")
        assert len(results) > 0
        top_genre, confidence = results[0]
        assert top_genre == NovelGenreType.DUSHI
        assert confidence > 0

    def test_detect_genre_from_title_xuanyi(self):
        """Test genre detection from title for mystery."""
        results = self.engine.detect_genre_from_title("悬疑推理集")
        assert len(results) > 0
        top_genre, confidence = results[0]
        assert top_genre == NovelGenreType.XUANYI
        assert confidence > 0

    def test_recommend_genre_for_plot(self):
        """Test genre recommendation from plot keywords."""
        keywords = ["修仙", "飞升", "宗门", "灵气"]
        recommendations = self.engine.recommend_genre_for_plot(keywords)
        assert len(recommendations) > 0
        assert recommendations[0].genre == NovelGenreType.XIANHUA
        assert recommendations[0].priority >= 20

    def test_recommend_genre_for_plot_dushi(self):
        """Test genre recommendation for urban plot."""
        keywords = ["都市", "创业", "商战", "职场"]
        recommendations = self.engine.recommend_genre_for_plot(keywords)
        assert len(recommendations) > 0
        assert recommendations[0].genre == NovelGenreType.DUSHI

    def test_get_genre_summary(self):
        """Test getting genre summary."""
        summary = self.engine.get_genre_summary(NovelGenreType.XIANHUA)
        assert summary is not None
        assert len(summary) > 0
        assert "仙侠" in summary or "修仙" in summary
        assert "世界观类型" in summary
        assert "推荐结构" in summary

    def test_get_all_genres(self):
        """Test getting all genre types."""
        genres = self.engine.get_all_genres()
        assert isinstance(genres, list)
        assert len(genres) > 0
        assert NovelGenreType.XIANHUA in genres
        assert NovelGenreType.DUSHI in genres
        assert NovelGenreType.XUANYI in genres
        assert NovelGenreType.KEHAN in genres

    def test_get_genres_by_category(self):
        """Test getting genres organized by category."""
        categories = self.engine.get_genres_by_category()
        assert "Chinese Web Novels" in categories
        assert "Western Genres" in categories
        assert NovelGenreType.XIANHUA in categories["Chinese Web Novels"]
        assert NovelGenreType.DUSHI in categories["Chinese Web Novels"]


class TestGenreModels:
    """Test suite for genre models."""

    def test_novel_genre_type_enum(self):
        """Test NovelGenreType enum values."""
        assert NovelGenreType.XIANHUA.value == "xianhua"
        assert NovelGenreType.YUANMAN.value == "yuanman"
        assert NovelGenreType.DUSHI.value == "dushi"
        assert NovelGenreType.XUANYI.value == "xuanyi"
        assert NovelGenreType.KEHAN.value == "kehuan"

    def test_world_setting_type_enum(self):
        """Test WorldSettingType enum values."""
        assert WorldSettingType.HIGH_FANTASY.value == "high_fantasy"
        assert WorldSettingType.URBAN_MODERN.value == "urban_modern"
        assert WorldSettingType.SCI_FI_WORLD.value == "sci_fi_world"

    def test_magic_technology_level_enum(self):
        """Test MagicTechnologyLevel enum values."""
        assert MagicTechnologyLevel.NONE.value == "none"
        assert MagicTechnologyLevel.LOW.value == "low"
        assert MagicTechnologyLevel.HIGH.value == "high"
        assert MagicTechnologyLevel.ULTRA.value == "ultra"

    def test_genre_world_config(self):
        """Test GenreWorldConfig model."""
        config = GenreWorldConfig(
            genre=NovelGenreType.XIANHUA,
            world_setting_type=WorldSettingType.HIGH_FANTASY,
            magic_tech_level=MagicTechnologyLevel.HIGH,
            geography_importance=0.8,
            magic_system_importance=1.0,
            requires_cultivation_system=True,
        )
        assert config.genre == NovelGenreType.XIANHUA
        assert config.geography_importance == 0.8
        assert config.requires_cultivation_system is True

    def test_genre_character_template(self):
        """Test GenreCharacterTemplate model."""
        template = GenreCharacterTemplate(
            genre=NovelGenreType.DUSHI,
            common_archetypes=["总裁", "职场新人", "富二代"],
            romance_importance=RomanceType.PRIMARY_ROMANCE,
            min_key_characters=5,
        )
        assert template.genre == NovelGenreType.DUSHI
        assert "总裁" in template.common_archetypes
        assert template.romance_importance == RomanceType.PRIMARY_ROMANCE

    def test_genre_plot_config(self):
        """Test GenrePlotConfig model."""
        config = GenrePlotConfig(
            genre=NovelGenreType.XUANYI,
            recommended_structure=PlotStructureType.MYSTERY_STRUCTURE,
            plot_complexity="complex",
            typical_pacing="slow",
            chapter_hook_style="cliffhanger",
            primary_conflict_type=ConflictType.EXTERNAL,
        )
        assert config.genre == NovelGenreType.XUANYI
        assert config.recommended_structure == PlotStructureType.MYSTERY_STRUCTURE
        assert config.plot_complexity == "complex"

    def test_genre_style_config(self):
        """Test GenreStyleConfig model."""
        config = GenreStyleConfig(
            genre=NovelGenreType.XIANHUA,
            typical_narrative_voice="third_limited",
            typical_tones=["epic", "dramatic"],
            typical_dialogue_ratio=0.25,
        )
        assert config.genre == NovelGenreType.XIANHUA
        assert config.typical_dialogue_ratio == 0.25
        assert "epic" in config.typical_tones

    def test_genre_tone_config(self):
        """Test GenreToneConfig model."""
        config = GenreToneConfig(
            genre=NovelGenreType.YANQING,
            primary_tone="romantic",
            secondary_tones=["lyrical", "intimate"],
            emotional_intensity="high",
            allows_tragedy=False,
        )
        assert config.genre == NovelGenreType.YANQING
        assert config.primary_tone == "romantic"
        assert config.allows_tragedy is False

    def test_novel_genre_profile(self):
        """Test NovelGenreProfile model."""
        profile = NovelGenreProfile(
            genre=NovelGenreType.XIANHUA,
            sub_genres=[NovelGenreType.YANQING],
            world_config=GenreWorldConfig(
                genre=NovelGenreType.XIANHUA,
                world_setting_type=WorldSettingType.HIGH_FANTASY,
                magic_tech_level=MagicTechnologyLevel.HIGH,
            ),
            character_template=GenreCharacterTemplate(
                genre=NovelGenreType.XIANHUA,
            ),
            plot_config=GenrePlotConfig(
                genre=NovelGenreType.XIANHUA,
                recommended_structure=PlotStructureType.THREE_ACT,
            ),
            style_config=GenreStyleConfig(
                genre=NovelGenreType.XIANHUA,
            ),
            tone_config=GenreToneConfig(
                genre=NovelGenreType.XIANHUA,
                primary_tone="epic",
            ),
            target_audience=TargetAudience.NEW_ADULT,
        )
        assert profile.genre == NovelGenreType.XIANHUA
        assert NovelGenreType.YANQING in profile.sub_genres
        assert profile.target_audience == TargetAudience.NEW_ADULT

    def test_genre_analysis_result(self):
        """Test GenreAnalysisResult model."""
        result = GenreAnalysisResult(
            detected_genre=NovelGenreType.XIANHUA,
            confidence=0.75,
            genre_evidence={
                NovelGenreType.XIANHUA.value: 0.75,
                NovelGenreType.DUSHI.value: 0.25,
            },
            recommendations=["Strong xianxia markers detected"],
        )
        assert result.detected_genre == NovelGenreType.XIANHUA
        assert result.confidence == 0.75
        assert len(result.recommendations) > 0

    def test_genre_template_to_profile(self):
        """Test GenreTemplate.to_genre_profile method."""
        template = GenreTemplate(
            template_name="xianhua",
            template_description="仙侠模板",
            genre=NovelGenreType.XIANHUA,
            world_config=GenreWorldConfig(
                genre=NovelGenreType.XIANHUA,
                world_setting_type=WorldSettingType.HIGH_FANTASY,
                magic_tech_level=MagicTechnologyLevel.HIGH,
            ),
            character_template=GenreCharacterTemplate(
                genre=NovelGenreType.XIANHUA,
            ),
            plot_config=GenrePlotConfig(
                genre=NovelGenreType.XIANHUA,
                recommended_structure=PlotStructureType.THREE_ACT,
            ),
            style_config=GenreStyleConfig(
                genre=NovelGenreType.XIANHUA,
            ),
            tone_config=GenreToneConfig(
                genre=NovelGenreType.XIANHUA,
                primary_tone="epic",
            ),
        )
        profile = template.to_genre_profile()
        assert isinstance(profile, NovelGenreProfile)
        assert profile.genre == NovelGenreType.XIANHUA

    def test_genre_recommendation(self):
        """Test GenreRecommendation model."""
        rec = GenreRecommendation(
            genre=NovelGenreType.XIANHUA,
            priority=80,
            reason="Matches cultivation plot keywords",
            expected_appeal="Fans of cultivation stories enjoy strong progression",
        )
        assert rec.genre == NovelGenreType.XIANHUA
        assert rec.priority == 80
        assert "cultivation" in rec.reason.lower()


class TestGenreIntegration:
    """Integration tests for genre system."""

    def test_full_genre_workflow(self):
        """Test complete genre workflow."""
        engine = NovelGenreEngine()

        # Get template
        template = engine.get_template("xianhua")
        assert template is not None

        # Create profile
        profile = engine.create_genre_profile(NovelGenreType.XIANHUA)
        assert profile is not None

        # Detect from content
        content = "主角修炼突破金丹境界，师傅说修仙需要经历天劫。"
        result = engine.detect_genre_from_content(content)
        assert result.detected_genre == NovelGenreType.XIANHUA

        # Get summary
        summary = engine.get_genre_summary(NovelGenreType.XIANHUA)
        assert len(summary) > 0

    def test_multiple_genre_detection(self):
        """Test detecting multiple genres."""
        engine = NovelGenreEngine()

        # Xianxia content
        xianxia_content = "修仙者突破金丹，渡劫飞升，师傅说修仙之路充满机缘。"
        result = engine.detect_genre_from_content(xianxia_content)
        assert result.detected_genre == NovelGenreType.XIANHUA
        assert result.confidence > 0

        # Urban content
        urban_content = "他在都市创业，与总裁谈判合同，努力在职场奋斗。"
        result = engine.detect_genre_from_content(urban_content)
        assert result.confidence > 0

    def test_genre_template_consistency(self):
        """Test that templates produce consistent profiles."""
        engine = NovelGenreEngine()

        for genre_name in ["xianhua", "dushi", "xuanyi", "kehuan", "yuanman"]:
            template = engine.get_template(genre_name)
            assert template is not None, f"Template {genre_name} not found"

            profile = engine.create_genre_profile(template.genre)
            assert profile.genre == template.genre, f"Genre mismatch for {genre_name}"

            # Verify all config sections exist
            assert profile.world_config is not None
            assert profile.character_template is not None
            assert profile.plot_config is not None
            assert profile.style_config is not None
            assert profile.tone_config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
