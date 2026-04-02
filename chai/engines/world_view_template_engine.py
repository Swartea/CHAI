"""World view template engine for custom world-building templates."""

import json
from pathlib import Path
from typing import Optional, Any

from chai.models.world_view_template import (
    WorldViewTemplateType,
    WorldViewTemplate,
    WorldViewTemplateProfile,
    WorldViewTemplateLibrary,
    TemplateApplicationResult,
    TemplateCustomizationRequest,
    GeographyConfig,
    PoliticsConfig,
    CultureConfig,
    HistoryConfig,
    MagicSystemConfig,
    SocialStructureConfig,
    GeographyImportance,
    PoliticsImportance,
    CultureImportance,
    HistoryImportance,
    MagicSystemImportance,
    SocialStructureImportance,
)


# Built-in world view templates
BUILTIN_TEMPLATES: dict[str, WorldViewTemplate] = {
    "xianhua": WorldViewTemplate(
        template_id="xianhua",
        template_name="Xianxia World",
        template_name_cn="仙侠世界",
        template_description="仙侠小说世界观：修仙文明，主角从凡人修炼成仙，追求长生不老",
        template_type=WorldViewTemplateType.XIANHUA,
        geography=GeographyConfig(
            importance=GeographyImportance.HIGH,
            continents=3,
            countries_per_continent=2,
            major_cities=8,
            landmarks=15,
            terrain_variety=["灵山", "秘境", "凡界", "仙界", "魔域"],
            climate_types=["灵气充沛", "天地元气"],
            geographic_features=["洞天福地", "小世界", "上古遗迹", "天材地宝产地"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.MEDIUM,
            government_types=["宗门统治", "王朝统治"],
            faction_count=8,
            conflict_potential=0.7,
            power_structure="decentralized",
            war_frequency="occasional",
        ),
        culture=CultureConfig(
            importance=CultureImportance.HIGH,
            religions=3,
            language_count=1,
            cultural_festivals=5,
            taboos=["欺师灭祖", "滥杀无辜"],
            traditions=["收徒传法", "历练修行", "炼丹炼器"],
            arts_level="spiritual",
            magical_culture=True,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.HIGH,
            era_count=5,
            founding_myth=True,
            major_wars=5,
            historical_figures=20,
            ancient_ruins=True,
            history_affects_present=0.8,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.ESSENTIAL,
            has_magic=True,
            magic_type="spiritual",
            cultivation_system=True,
            technology_level="ancient",
            magical_beings=["妖族", "魔族", "鬼族", "上古神兽"],
            power_source="天地灵气",
            power_restrictions=["心魔", "天劫", "寿元限制"],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.HIGH,
            class_system="hierarchical",
            class_count=4,
            guilds_exist=False,
            family_structure="patriarchal",
            social_mobility="high",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["仙侠", "修炼", "东方玄幻", "飞升"],
        author="system",
    ),
    "yuanman": WorldViewTemplate(
        template_id="yuanman",
        template_name="Fantasy World",
        template_name_cn="玄幻世界",
        template_description="玄幻小说世界观：异世界冒险，充满魔法与奇幻元素",
        template_type=WorldViewTemplateType.YUANMAN,
        geography=GeographyConfig(
            importance=GeographyImportance.HIGH,
            continents=5,
            countries_per_continent=4,
            major_cities=10,
            landmarks=20,
            terrain_variety=["平原", "森林", "山地", "沙漠", "海洋", "火山"],
            climate_types=["多样"],
            geographic_features=["魔法森林", "龙之峡谷", "精灵领地", "矮人山脉"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.MEDIUM,
            government_types=["王国", "帝国", "公会联盟"],
            faction_count=10,
            conflict_potential=0.8,
            power_structure="feudal",
            war_frequency="occasional",
        ),
        culture=CultureConfig(
            importance=CultureImportance.MEDIUM,
            religions=4,
            language_count=5,
            cultural_festivals=8,
            taboos=["杀害龙族", "盗取圣物"],
            traditions=["骑士精神", "魔法契约", "勇者的试炼"],
            arts_level="moderate",
            magical_culture=True,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.MEDIUM,
            era_count=4,
            founding_myth=True,
            major_wars=8,
            historical_figures=15,
            ancient_ruins=True,
            history_affects_present=0.6,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.ESSENTIAL,
            has_magic=True,
            magic_type="arcane",
            cultivation_system=False,
            technology_level="medieval",
            magical_beings=["龙族", "精灵", "矮人", "兽人", "天使", "恶魔"],
            power_source="魔力/斗气",
            power_restrictions=["魔力耗尽", "魔法反噬"],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.MEDIUM,
            class_system="feudal",
            class_count=5,
            guilds_exist=True,
            family_structure="patriarchal",
            social_mobility="medium",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["玄幻", "异世界", "魔法", "冒险"],
        author="system",
    ),
    "dushi": WorldViewTemplate(
        template_id="dushi",
        template_name="Urban Modern World",
        template_name_cn="都市世界",
        template_description="都市小说世界观：现代城市背景，贴近现实生活",
        template_type=WorldViewTemplateType.DUSHI,
        geography=GeographyConfig(
            importance=GeographyImportance.LOW,
            continents=1,
            countries_per_continent=1,
            major_cities=10,
            landmarks=20,
            terrain_variety=["平原", "丘陵", "河流"],
            climate_types=["温带季风", "亚热带"],
            geographic_features=["CBD", "高新技术园区", "老城区"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.HIGH,
            government_types=["现代政府体制"],
            faction_count=15,
            conflict_potential=0.6,
            power_structure="centralized",
            war_frequency="never",
        ),
        culture=CultureConfig(
            importance=CultureImportance.HIGH,
            religions=5,
            language_count=1,
            cultural_festivals=10,
            taboos=["违法乱纪"],
            traditions=["节日庆典", "商业习俗"],
            arts_level="high",
            magical_culture=False,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.LOW,
            era_count=2,
            founding_myth=False,
            major_wars=1,
            historical_figures=5,
            ancient_ruins=False,
            history_affects_present=0.3,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.NONE,
            has_magic=False,
            magic_type="none",
            cultivation_system=False,
            technology_level="modern",
            magical_beings=[],
            power_source="无",
            power_restrictions=[],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.ESSENTIAL,
            class_system="hierarchical",
            class_count=5,
            guilds_exist=False,
            family_structure="modern",
            social_mobility="high",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["都市", "现代", "职场", "商战"],
        author="system",
    ),
    "kehuan": WorldViewTemplate(
        template_id="kehuan",
        template_name="Sci-Fi World",
        template_name_cn="科幻世界",
        template_description="科幻小说世界观：未来科技，太空探索与星际文明",
        template_type=WorldViewTemplateType.KEHAN,
        geography=GeographyConfig(
            importance=GeographyImportance.HIGH,
            continents=1,
            countries_per_continent=1,
            major_cities=50,
            landmarks=100,
            terrain_variety=["行星表面", "太空站", "星际飞船"],
            climate_types=["人工控制", "多样星球"],
            geographic_features=["戴森球", "星际航道", "外星基地", "虫洞"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.HIGH,
            government_types=["星际联邦", "星际帝国", "独立星区"],
            faction_count=12,
            conflict_potential=0.8,
            power_structure="centralized",
            war_frequency="frequent",
        ),
        culture=CultureConfig(
            importance=CultureImportance.MEDIUM,
            religions=3,
            language_count=1,
            cultural_festivals=5,
            taboos=["AI叛变", "基因编辑人类"],
            traditions=["星际探索精神", "科技崇拜"],
            arts_level="technological",
            magical_culture=False,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.MEDIUM,
            era_count=3,
            founding_myth=False,
            major_wars=3,
            historical_figures=10,
            ancient_ruins=True,
            history_affects_present=0.7,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.ESSENTIAL,
            has_magic=False,
            magic_type="technology",
            cultivation_system=False,
            technology_level="futuristic",
            magical_beings=["AI生命体", "外星种族", "改造人"],
            power_source="能量核心/暗物质",
            power_restrictions=["能量限制", "技术门槛"],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.HIGH,
            class_system="hierarchical",
            class_count=4,
            guilds_exist=False,
            family_structure="modern",
            social_mobility="medium",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["科幻", "太空", "未来", "星际"],
        author="system",
    ),
    "xuanyi": WorldViewTemplate(
        template_id="xuanyi",
        template_name="Mystery World",
        template_name_cn="悬疑世界",
        template_description="悬疑小说世界观：充满谜团和反转，神秘事件频发",
        template_type=WorldViewTemplateType.XUANYI,
        geography=GeographyConfig(
            importance=GeographyImportance.MEDIUM,
            continents=1,
            countries_per_continent=1,
            major_cities=5,
            landmarks=10,
            terrain_variety=["城市", "郊区", "山区"],
            climate_types=["多变"],
            geographic_features=["神秘区域", "禁地", "古老建筑"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.MEDIUM,
            government_types=["现代政府"],
            faction_count=8,
            conflict_potential=0.5,
            power_structure="centralized",
            war_frequency="never",
        ),
        culture=CultureConfig(
            importance=CultureImportance.MEDIUM,
            religions=2,
            language_count=1,
            cultural_festivals=3,
            taboos=["禁忌实验", "神秘仪式"],
            traditions=["保密文化"],
            arts_level="moderate",
            magical_culture=False,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.HIGH,
            era_count=4,
            founding_myth=True,
            major_wars=2,
            historical_figures=8,
            ancient_ruins=True,
            history_affects_present=0.9,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.NONE,
            has_magic=False,
            magic_type="none",
            cultivation_system=False,
            technology_level="modern",
            magical_beings=[],
            power_source="无",
            power_restrictions=[],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.MEDIUM,
            class_system="hierarchical",
            class_count=3,
            guilds_exist=False,
            family_structure="modern",
            social_mobility="medium",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["悬疑", "推理", "神秘", "惊悚"],
        author="system",
    ),
    "yanqing": WorldViewTemplate(
        template_id="yanqing",
        template_name="Romance World",
        template_name_cn="言情世界",
        template_description="言情小说世界观：以爱情为主线，情感描写细腻",
        template_type=WorldViewTemplateType.YANQING,
        geography=GeographyConfig(
            importance=GeographyImportance.LOW,
            continents=1,
            countries_per_continent=1,
            major_cities=3,
            landmarks=5,
            terrain_variety=["城市", "海边", "乡村"],
            climate_types=["温带"],
            geographic_features=["浪漫场景"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.LOW,
            government_types=["现代政府"],
            faction_count=2,
            conflict_potential=0.2,
            power_structure="centralized",
            war_frequency="never",
        ),
        culture=CultureConfig(
            importance=CultureImportance.HIGH,
            religions=1,
            language_count=1,
            cultural_festivals=5,
            taboos=["不忠"],
            traditions=["浪漫约会", "节日惊喜"],
            arts_level="high",
            magical_culture=False,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.LOW,
            era_count=1,
            founding_myth=False,
            major_wars=0,
            historical_figures=2,
            ancient_ruins=False,
            history_affects_present=0.1,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.NONE,
            has_magic=False,
            magic_type="none",
            cultivation_system=False,
            technology_level="modern",
            magical_beings=[],
            power_source="无",
            power_restrictions=[],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.MEDIUM,
            class_system="hierarchical",
            class_count=3,
            guilds_exist=False,
            family_structure="modern",
            social_mobility="medium",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["言情", "爱情", "浪漫", "情感"],
        author="system",
    ),
    "jianyu": WorldViewTemplate(
        template_id="jianyu",
        template_name="Wuxia World",
        template_name_cn="剑雨江湖",
        template_description="武侠小说世界观：江湖恩怨，武功秘籍，侠客义举",
        template_type=WorldViewTemplateType.JIANYU,
        geography=GeographyConfig(
            importance=GeographyImportance.HIGH,
            continents=1,
            countries_per_continent=1,
            major_cities=15,
            landmarks=25,
            terrain_variety=["中原", "江南", "塞北", "西域", "海外"],
            climate_types=["多样"],
            geographic_features=["名山大川", "古道", "关隘", "秘境"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.HIGH,
            government_types=["王朝统治", "江湖门派"],
            faction_count=20,
            conflict_potential=0.9,
            power_structure="decentralized",
            war_frequency="occasional",
        ),
        culture=CultureConfig(
            importance=CultureImportance.HIGH,
            religions=3,
            language_count=1,
            cultural_festivals=6,
            taboos=["欺师灭祖", "勾结外敌", "滥杀无辜"],
            traditions=["武林大会", "江湖规矩", "侠义精神"],
            arts_level="high",
            magical_culture=False,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.HIGH,
            era_count=3,
            founding_myth=True,
            major_wars=5,
            historical_figures=30,
            ancient_ruins=True,
            history_affects_present=0.8,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.ESSENTIAL,
            has_magic=True,
            magic_type="martial_arts",
            cultivation_system=False,
            technology_level="ancient",
            magical_beings=["神兵利器", "珍禽异兽"],
            power_source="内力/真气",
            power_restrictions=["走火入魔", "内伤"],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.HIGH,
            class_system="hierarchical",
            class_count=4,
            guilds_exist=True,
            family_structure="patriarchal",
            social_mobility="high",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["武侠", "江湖", "武功", "侠义"],
        author="system",
    ),
    "shenmo": WorldViewTemplate(
        template_id="shenmo",
        template_name="Shenmo World",
        template_name_cn="神魔世界",
        template_description="神魔小说世界观：上古神魔大战，天道轮回，宏大叙事",
        template_type=WorldViewTemplateType.SHENMO,
        geography=GeographyConfig(
            importance=GeographyImportance.HIGH,
            continents=9,
            countries_per_continent=9,
            major_cities=81,
            landmarks=100,
            terrain_variety=["天界", "人界", "魔界", "妖界", "冥界"],
            climate_types=["天地元气充沛"],
            geographic_features=["神山", "魔域", "古战场", "天道遗迹"],
        ),
        politics=PoliticsConfig(
            importance=PoliticsImportance.HIGH,
            government_types=["天庭", "魔宫", "妖族部落"],
            faction_count=15,
            conflict_potential=1.0,
            power_structure="theocratic",
            war_frequency="frequent",
        ),
        culture=CultureConfig(
            importance=CultureImportance.HIGH,
            religions=5,
            language_count=3,
            cultural_festivals=10,
            taboos=["亵渎神明", "堕入魔道"],
            traditions=["祭祀大典", "天道法则", "天命论"],
            arts_level="divine",
            magical_culture=True,
        ),
        history=HistoryConfig(
            importance=HistoryImportance.ESSENTIAL,
            era_count=7,
            founding_myth=True,
            major_wars=10,
            historical_figures=50,
            ancient_ruins=True,
            history_affects_present=1.0,
        ),
        magic_system=MagicSystemConfig(
            importance=MagicSystemImportance.ESSENTIAL,
            has_magic=True,
            magic_type="divine",
            cultivation_system=True,
            technology_level="ancient",
            magical_beings=["神族", "魔族", "妖族", "冥族", "上古神兽"],
            power_source="天道法则/神力魔力",
            power_restrictions=["天道约束", "因果报应", "神魔制约"],
        ),
        social_structure=SocialStructureConfig(
            importance=SocialStructureImportance.HIGH,
            class_system="caste",
            class_count=6,
            guilds_exist=False,
            family_structure="divine_order",
            social_mobility="none",
        ),
        is_builtin=True,
        is_custom=False,
        tags=["神魔", "上古", "天道", "神话"],
        author="system",
    ),
}


class WorldViewTemplateEngine:
    """Engine for managing custom world view templates."""

    def __init__(self, library_path: Optional[str] = None):
        """Initialize the world view template engine.

        Args:
            library_path: Optional path to load/save custom templates
        """
        self._library_path = library_path
        self._templates: dict[str, WorldViewTemplate] = dict(BUILTIN_TEMPLATES)
        self._load_custom_templates()

    def _load_custom_templates(self) -> None:
        """Load custom templates from file if library_path is set."""
        if self._library_path:
            path = Path(self._library_path)
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if "templates" in data:
                        for template_data in data["templates"]:
                            template = WorldViewTemplate(**template_data)
                            if template.is_custom:
                                self._templates[template.template_id] = template
                except (json.JSONDecodeError, Exception):
                    pass  # Ignore errors, use built-in templates only

    def _save_custom_templates(self) -> None:
        """Save custom templates to file."""
        if self._library_path:
            custom_templates = [
                t.model_dump() for t in self._templates.values() if t.is_custom
            ]
            if custom_templates:
                data = {"templates": custom_templates}
                path = Path(self._library_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

    def get_template(self, template_id: str) -> Optional[WorldViewTemplate]:
        """Get a template by ID.

        Args:
            template_id: Template identifier

        Returns:
            WorldViewTemplate if found, None otherwise
        """
        return self._templates.get(template_id)

    def get_all_templates(self) -> dict[str, WorldViewTemplate]:
        """Get all available templates."""
        return self._templates.copy()

    def get_builtin_templates(self) -> dict[str, WorldViewTemplate]:
        """Get all built-in templates."""
        return {k: v for k, v in self._templates.items() if v.is_builtin}

    def get_custom_templates(self) -> dict[str, WorldViewTemplate]:
        """Get all user-created custom templates."""
        return {k: v for k, v in self._templates.items() if v.is_custom}

    def create_template(
        self,
        template_name: str,
        template_name_cn: str,
        template_description: str,
        template_type: WorldViewTemplateType = WorldViewTemplateType.custom,
        **kwargs,
    ) -> WorldViewTemplate:
        """Create a new custom template.

        Args:
            template_name: Template name in English
            template_name_cn: Template name in Chinese
            template_description: Template description
            template_type: Template type
            **kwargs: Additional configuration overrides

        Returns:
            The created WorldViewTemplate
        """
        template_id = f"custom_{template_name.lower().replace(' ', '_')}_{len(self._templates)}"

        template = WorldViewTemplate(
            template_id=template_id,
            template_name=template_name,
            template_name_cn=template_name_cn,
            template_description=template_description,
            template_type=template_type,
            is_builtin=False,
            is_custom=True,
            author="user",
            **kwargs,
        )

        self._templates[template_id] = template
        self._save_custom_templates()
        return template

    def update_template(
        self,
        template_id: str,
        changes: dict,
    ) -> Optional[WorldViewTemplate]:
        """Update an existing template.

        Args:
            template_id: Template to update
            changes: Dictionary of changes to apply

        Returns:
            Updated template or None if not found
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        if template.is_builtin and not template.is_custom:
            # Cannot modify built-in templates directly, create a copy
            template_id = f"custom_{template_id}_{len(self._templates)}"
            changes["template_id"] = template_id
            changes["is_custom"] = True
            changes["is_builtin"] = False

        for key, value in changes.items():
            if hasattr(template, key):
                setattr(template, key, value)

        self._templates[template_id] = template
        self._save_custom_templates()
        return template

    def delete_template(self, template_id: str) -> bool:
        """Delete a custom template.

        Args:
            template_id: Template to delete

        Returns:
            True if deleted, False if not found or is built-in
        """
        template = self._templates.get(template_id)
        if not template or (template.is_builtin and not template.is_custom):
            return False

        del self._templates[template_id]
        self._save_custom_templates()
        return True

    def duplicate_template(
        self,
        template_id: str,
        new_name: str,
        new_name_cn: str,
    ) -> Optional[WorldViewTemplate]:
        """Duplicate an existing template as a new custom template.

        Args:
            template_id: Template to duplicate
            new_name: Name for the new template
            new_name_cn: Chinese name for the new template

        Returns:
            New template or None if source not found
        """
        source = self._templates.get(template_id)
        if not source:
            return None

        new_id = f"custom_{new_name.lower().replace(' ', '_')}_{len(self._templates)}"
        new_template = WorldViewTemplate(
            template_id=new_id,
            template_name=new_name,
            template_name_cn=new_name_cn,
            template_description=source.template_description,
            template_type=source.template_type,
            geography=source.geography,
            politics=source.politics,
            culture=source.culture,
            history=source.history,
            magic_system=source.magic_system,
            social_structure=source.social_structure,
            is_builtin=False,
            is_custom=True,
            tags=source.tags.copy(),
            author="user",
            version="1.0",
        )

        self._templates[new_id] = new_template
        self._save_custom_templates()
        return new_template

    def apply_template(
        self,
        template_id: str,
        customizations: Optional[dict] = None,
    ) -> Optional[TemplateApplicationResult]:
        """Apply a template and get generation hints.

        Args:
            template_id: Template to apply
            customizations: Optional customizations to override template settings

        Returns:
            TemplateApplicationResult with hints for world generation
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        customizations = customizations or {}

        # Build applied settings from template
        applied_settings = {
            "geography_importance": template.geography.importance.value,
            "politics_importance": template.politics.importance.value,
            "culture_importance": template.culture.importance.value,
            "history_importance": template.history.importance.value,
            "magic_system_importance": template.magic_system.importance.value,
            "social_structure_importance": template.social_structure.importance.value,
            "has_magic": template.magic_system.has_magic,
            "magic_type": template.magic_system.magic_type,
            "technology_level": template.magic_system.technology_level,
        }

        warnings = []
        modifications = []

        # Apply customizations
        for key, value in customizations.items():
            if key in applied_settings:
                if applied_settings[key] != value:
                    modifications.append(f"Changed {key}: {applied_settings[key]} -> {value}")
                    applied_settings[key] = value
            else:
                applied_settings[key] = value

        # Generate hints based on template settings
        generation_hints = self._build_generation_hints(template, customizations)

        return TemplateApplicationResult(
            template_id=template_id,
            applied_settings=applied_settings,
            warnings=warnings,
            modifications=modifications,
            generation_hints=generation_hints,
        )

    def _build_generation_hints(
        self,
        template: WorldViewTemplate,
        customizations: dict,
    ) -> dict[str, Any]:
        """Build generation hints from template.

        Args:
            template: Template to build hints from
            customizations: User customizations

        Returns:
            Dictionary of generation hints
        """
        hints = {
            "template_type": template.template_type.value,
            "geography": {
                "importance": template.geography.importance.value,
                "continent_count": template.geography.continents,
                "countries_per_continent": template.geography.countries_per_continent,
                "major_cities": template.geography.major_cities,
                "landmarks": template.geography.landmarks,
                "terrain_variety": template.geography.terrain_variety,
                "climate_types": template.geography.climate_types,
                "natural_resources": template.geography.natural_resources,
                "geographic_features": template.geography.geographic_features,
            },
            "politics": {
                "importance": template.politics.importance.value,
                "government_types": template.politics.government_types,
                "faction_count": template.politics.faction_count,
                "conflict_potential": template.politics.conflict_potential,
                "power_structure": template.politics.power_structure,
                "war_frequency": template.politics.war_frequency,
            },
            "culture": {
                "importance": template.culture.importance.value,
                "religions": template.culture.religions,
                "language_count": template.culture.language_count,
                "cultural_festivals": template.culture.cultural_festivals,
                "taboos": template.culture.taboos,
                "traditions": template.culture.traditions,
                "magical_culture": template.culture.magical_culture,
            },
            "history": {
                "importance": template.history.importance.value,
                "era_count": template.history.era_count,
                "founding_myth": template.history.founding_myth,
                "major_wars": template.history.major_wars,
                "historical_figures": template.history.historical_figures,
                "ancient_ruins": template.history.ancient_ruins,
                "history_affects_present": template.history.history_affects_present,
            },
            "magic_system": {
                "importance": template.magic_system.importance.value,
                "has_magic": template.magic_system.has_magic,
                "magic_type": template.magic_system.magic_type,
                "cultivation_system": template.magic_system.cultivation_system,
                "technology_level": template.magic_system.technology_level,
                "magical_beings": template.magic_system.magical_beings,
                "power_source": template.magic_system.power_source,
                "power_restrictions": template.magic_system.power_restrictions,
            },
            "social_structure": {
                "importance": template.social_structure.importance.value,
                "class_system": template.social_structure.class_system,
                "class_count": template.social_structure.class_count,
                "guilds_exist": template.social_structure.guilds_exist,
                "family_structure": template.social_structure.family_structure,
                "social_mobility": template.social_structure.social_mobility,
            },
            "tags": template.tags,
        }

        # Apply customizations to hints
        for key, value in customizations.items():
            if key in hints:
                hints[key] = value
            elif "." in key:
                # Handle nested keys like "magic_system.has_magic"
                parts = key.split(".")
                if parts[0] in hints and isinstance(hints[parts[0]], dict):
                    hints[parts[0]][parts[1]] = value
            elif key in ("has_magic", "magic_type", "technology_level",
                         "cultivation_system", "power_source", "power_restrictions",
                         "magical_beings"):
                # Map top-level magic system keys to magic_system section
                if "magic_system" in hints:
                    hints["magic_system"][key] = value
            else:
                hints[key] = value

        return hints

    def create_profile(
        self,
        template_id: str,
        customizations: Optional[dict] = None,
        genre_hint: Optional[str] = None,
        theme_hint: Optional[str] = None,
    ) -> Optional[WorldViewTemplateProfile]:
        """Create a template profile for world generation.

        Args:
            template_id: Template to use
            customizations: Optional customizations
            genre_hint: Optional genre hint
            theme_hint: Optional theme hint

        Returns:
            WorldViewTemplateProfile or None if template not found
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        return WorldViewTemplateProfile(
            template=template,
            customizations=customizations or {},
            genre_hint=genre_hint,
            theme_hint=theme_hint,
        )

    def get_templates_by_tag(self, tag: str) -> list[WorldViewTemplate]:
        """Get templates filtered by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if tag in t.tags]

    def get_templates_by_type(
        self,
        template_type: WorldViewTemplateType,
    ) -> list[WorldViewTemplate]:
        """Get templates filtered by type.

        Args:
            template_type: Template type to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.template_type == template_type]

    def search_templates(
        self,
        query: str,
    ) -> list[WorldViewTemplate]:
        """Search templates by name or description.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        results = []
        for template in self._templates.values():
            if (query_lower in template.template_name.lower() or
                query_lower in template.template_name_cn or
                query_lower in template.template_description.lower()):
                results.append(template)
        return results

    def export_template(self, template_id: str) -> Optional[dict]:
        """Export a template as a dictionary.

        Args:
            template_id: Template to export

        Returns:
            Template as dict or None if not found
        """
        template = self._templates.get(template_id)
        if not template:
            return None
        return template.model_dump()

    def import_template(self, template_data: dict) -> WorldViewTemplate:
        """Import a template from a dictionary.

        Args:
            template_data: Template data dictionary

        Returns:
            Imported WorldViewTemplate
        """
        template = WorldViewTemplate(**template_data)
        # Ensure it's marked as custom
        template.is_builtin = False
        template.is_custom = True
        self._templates[template.template_id] = template
        self._save_custom_templates()
        return template

    def get_template_summary(self, template_id: str) -> Optional[str]:
        """Get a human-readable summary of a template.

        Args:
            template_id: Template to summarize

        Returns:
            Summary string or None if not found
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        parts = [
            f"【{template.template_name_cn}】{template.template_name}",
            f"类型: {template.template_type.value}",
            "",
            f"描述: {template.template_description}",
            "",
            "重要性配置:",
            f"  地理: {template.geography.importance.value}",
            f"  政治: {template.politics.importance.value}",
            f"  文化: {template.culture.importance.value}",
            f"  历史: {template.history.importance.value}",
            f"  魔法/科技: {template.magic_system.importance.value}",
            f"  社会结构: {template.social_structure.importance.value}",
            "",
            f"标签: {', '.join(template.tags) if template.tags else '无'}",
        ]

        return "\n".join(parts)

    def get_all_tags(self) -> list[str]:
        """Get all unique tags across templates."""
        tags = set()
        for template in self._templates.values():
            tags.update(template.tags)
        return sorted(list(tags))
