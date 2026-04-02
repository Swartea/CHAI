"""World view template models for custom world-building templates."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WorldViewTemplateType(str, Enum):
    """Pre-defined world view template types."""
    XIANHUA = "xianhua"           # 仙侠：修仙文明
    YUANMAN = "yuanman"          # 玄幻：异世界冒险
    DUSHI = "dushi"              # 都市：现代城市
    KEHAN = "kehan"              # 科幻：未来科技
    XUANYI = "xuanyi"            # 悬疑：神秘推理
    YANQING = "yanqing"          # 言情：爱情为主
    LISHI = "lishi"              # 历史：古代背景
    JUNSHI = "junshi"            # 军事：战争冲突
    SHENMO = "shenmo"            # 神话：上古神魔
    TONGREN = "tongren"          # 同人：改编创作
    DIYU = "diyu"                # 地域：末日废土
    JIANYU = "jianyu"            # 剑雨：武侠江湖
    custom = "custom"            # 自定义模板


class GeographyImportance(str, Enum):
    """Geography importance level."""
    NONE = "none"               # 不重要
    LOW = "low"                # 较低
    MEDIUM = "medium"           # 中等
    HIGH = "high"               # 重要
    ESSENTIAL = "essential"     # 核心


class PoliticsImportance(str, Enum):
    """Politics importance level."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESSENTIAL = "essential"


class CultureImportance(str, Enum):
    """Culture importance level."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESSENTIAL = "essential"


class HistoryImportance(str, Enum):
    """History importance level."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESSENTIAL = "essential"


class MagicSystemImportance(str, Enum):
    """Magic/technology system importance."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESSENTIAL = "essential"


class SocialStructureImportance(str, Enum):
    """Social structure importance."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESSENTIAL = "essential"


class GeographyConfig(BaseModel):
    """Geography configuration for a world view template."""
    importance: GeographyImportance = Field(default=GeographyImportance.MEDIUM)
    continents: int = Field(default=3, description="Number of major continents")
    countries_per_continent: int = Field(default=3, description="Average countries per continent")
    major_cities: int = Field(default=5, description="Major cities per country")
    landmarks: int = Field(default=10, description="Notable landmarks/attractions")
    terrain_variety: list[str] = Field(
        default_factory=lambda: ["平原", "山地", "森林", "河流", "海洋"],
        description="Types of terrain"
    )
    climate_types: list[str] = Field(
        default_factory=lambda: ["温带", "热带", "寒带"],
        description="Climate types"
    )
    natural_resources: list[str] = Field(
        default_factory=list,
        description="Key natural resources"
    )
    geographic_features: list[str] = Field(
        default_factory=list,
        description="Special geographic features like magic zones, qi concentration areas"
    )


class PoliticsConfig(BaseModel):
    """Politics configuration for a world view template."""
    importance: PoliticsImportance = Field(default=PoliticsImportance.MEDIUM)
    government_types: list[str] = Field(
        default_factory=list,
        description="Types of governments"
    )
    faction_count: int = Field(default=5, description="Number of major factions")
    conflict_potential: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Potential for political conflict (0-1)"
    )
    power_structure: str = Field(
        default="centralized",
        description="centralized, decentralized, theocratic, etc."
    )
    laws_enforcement: str = Field(
        default="standard",
        description="How laws are enforced"
    )
    war_frequency: str = Field(
        default="rare",
        description="How often wars occur: never, rare, occasional, frequent, constant"
    )


class CultureConfig(BaseModel):
    """Culture configuration for a world view template."""
    importance: CultureImportance = Field(default=CultureImportance.MEDIUM)
    religions: int = Field(default=2, description="Number of major religions/cults")
    language_count: int = Field(default=3, description="Number of major languages")
    cultural_festivals: int = Field(default=5, description="Important cultural festivals")
    taboos: list[str] = Field(default_factory=list, description="Cultural taboos")
    traditions: list[str] = Field(default_factory=list, description="Important traditions")
    arts_level: str = Field(
        default="moderate",
        description="Development level of arts and literature"
    )
    magical_culture: bool = Field(
        default=False,
        description="Whether culture incorporates magical elements"
    )


class HistoryConfig(BaseModel):
    """History configuration for a world view template."""
    importance: HistoryImportance = Field(default=HistoryImportance.MEDIUM)
    era_count: int = Field(default=3, description="Number of major historical eras")
    founding_myth: bool = Field(
        default=True,
        description="Whether there is a founding myth"
    )
    major_wars: int = Field(default=3, description="Number of major historical wars")
    historical_figures: int = Field(
        default=10,
        description="Number of notable historical figures"
    )
    ancient_ruins: bool = Field(
        default=True,
        description="Whether ancient ruins exist"
    )
    history_affects_present: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How much history affects current events"
    )


class MagicSystemConfig(BaseModel):
    """Magic/technology system configuration."""
    importance: MagicSystemImportance = Field(default=MagicSystemImportance.MEDIUM)
    has_magic: bool = Field(default=True, description="Whether magic exists")
    magic_type: str = Field(
        default="spiritual",
        description="spiritual, elemental, arcane, divine, demonic, etc."
    )
    cultivation_system: bool = Field(
        default=False,
        description="Whether a cultivation/leveling system exists"
    )
    technology_level: str = Field(
        default="medieval",
        description="medieval, renaissance, industrial, modern, futuristic"
    )
    magical_beings: list[str] = Field(
        default_factory=list,
        description="Types of magical beings"
    )
    power_source: str = Field(
        default="spiritual_energy",
        description="Source of magical/super power"
    )
    power_restrictions: list[str] = Field(
        default_factory=list,
        description="Common restrictions on power usage"
    )


class SocialStructureConfig(BaseModel):
    """Social structure configuration."""
    importance: SocialStructureImportance = Field(default=SocialStructureImportance.MEDIUM)
    class_system: str = Field(
        default="hierarchical",
        description="none, feudal, hierarchical, caste, egalitarian"
    )
    class_count: int = Field(default=3, description="Number of social classes")
    guilds_exist: bool = Field(default=True, description="Whether guilds exist")
    family_structure: str = Field(
        default="patriarchal",
        description="patriarchal, matriarchal, egalitarian"
    )
    social_mobility: str = Field(
        default="low",
        description="How easy it is to change social class"
    )


class WorldViewTemplate(BaseModel):
    """A world view template defining the structure and emphasis of a world."""
    template_id: str = Field(description="Unique template identifier")
    template_name: str = Field(description="Template name")
    template_name_cn: str = Field(description="Chinese name of template")
    template_description: str = Field(description="Template description")
    template_type: WorldViewTemplateType = Field(
        default=WorldViewTemplateType.custom,
        description="Template type category"
    )

    # Configuration for each world component
    geography: GeographyConfig = Field(
        default_factory=GeographyConfig,
        description="Geography configuration"
    )
    politics: PoliticsConfig = Field(
        default_factory=PoliticsConfig,
        description="Politics configuration"
    )
    culture: CultureConfig = Field(
        default_factory=CultureConfig,
        description="Culture configuration"
    )
    history: HistoryConfig = Field(
        default_factory=HistoryConfig,
        description="History configuration"
    )
    magic_system: MagicSystemConfig = Field(
        default_factory=MagicSystemConfig,
        description="Magic/technology system configuration"
    )
    social_structure: SocialStructureConfig = Field(
        default_factory=SocialStructureConfig,
        description="Social structure configuration"
    )

    # Metadata
    is_builtin: bool = Field(
        default=False,
        description="Whether this is a built-in template"
    )
    is_custom: bool = Field(
        default=True,
        description="Whether this is a user-created custom template"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
    author: str = Field(
        default="system",
        description="Template author"
    )
    version: str = Field(
        default="1.0",
        description="Template version"
    )

    def get_importance_summary(self) -> dict[str, str]:
        """Get a summary of component importance levels."""
        return {
            "geography": self.geography.importance.value,
            "politics": self.politics.importance.value,
            "culture": self.culture.importance.value,
            "history": self.history.importance.value,
            "magic_system": self.magic_system.importance.value,
            "social_structure": self.social_structure.importance.value,
        }


class WorldViewTemplateProfile(BaseModel):
    """Profile for applying a world view template to generation."""
    template: WorldViewTemplate = Field(description="The template to apply")
    customizations: dict = Field(
        default_factory=dict,
        description="User customizations to the template"
    )
    genre_hint: Optional[str] = Field(
        default=None,
        description="Optional genre hint for generation"
    )
    theme_hint: Optional[str] = Field(
        default=None,
        description="Optional theme hint for generation"
    )


class WorldViewTemplateLibrary(BaseModel):
    """A library of world view templates."""
    templates: dict[str, WorldViewTemplate] = Field(
        default_factory=dict,
        description="Templates by template_id"
    )
    categories: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Templates organized by category"
    )
    default_template_id: Optional[str] = Field(
        default=None,
        description="Default template ID"
    )

    def add_template(self, template: WorldViewTemplate) -> None:
        """Add a template to the library."""
        self.templates[template.template_id] = template
        for tag in template.tags:
            if tag not in self.categories:
                self.categories[tag] = []
            if template.template_id not in self.categories[tag]:
                self.categories[tag].append(template.template_id)

    def remove_template(self, template_id: str) -> bool:
        """Remove a template from the library."""
        if template_id not in self.templates:
            return False
        template = self.templates[template_id]
        del self.templates[template_id]
        for tag in template.tags:
            if tag in self.categories and template_id in self.categories[tag]:
                self.categories[tag].remove(template_id)
        return True

    def get_templates_by_tag(self, tag: str) -> list[WorldViewTemplate]:
        """Get all templates with a specific tag."""
        template_ids = self.categories.get(tag, [])
        return [self.templates[tid] for tid in template_ids if tid in self.templates]


class TemplateApplicationResult(BaseModel):
    """Result of applying a template to world generation."""
    template_id: str = Field(description="Template that was applied")
    applied_settings: dict = Field(
        default_factory=dict,
        description="Settings that were applied"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings during application"
    )
    modifications: list[str] = Field(
        default_factory=list,
        description="Modifications made to the template"
    )
    generation_hints: dict = Field(
        default_factory=dict,
        description="Hints to pass to the world generator"
    )


class TemplateCustomizationRequest(BaseModel):
    """Request to customize a template."""
    template_id: str = Field(description="Template to customize")
    changes: dict = Field(
        default_factory=dict,
        description="Changes to apply to the template"
    )
    new_template_name: Optional[str] = Field(
        default=None,
        description="Name for the customized template"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for the customized template"
    )
