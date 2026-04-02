"""Novel genre models for supporting multiple novel types."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class NovelGenreType(str, Enum):
    """Supported novel genre types."""
    # Chinese web novel genres
    XIANHUA = "xianhua"           # 仙侠 - Fantasy/Xianxia
    YUANMAN = "yuanman"           # 玄幻 - Urban Fantasy/High Fantasy
    DUSHI = "dushi"               # 都市 - Urban Modern
    YANQING = "yanqing"           # 言情 - Romance
    XUANYI = "xuanyi"             # 悬疑 - Mystery/Thriller
    KEHAN = "kehuan"              # 科幻 - Science Fiction
    LISHI = "lishi"               # 历史 - Historical
    JUNSHI = "junshi"             # 军事 - Military
    YOUXI = "youxi"               # 游戏 - Game-related
    JINGJI = "jingji"             # 竞技 - Sports/Competition
    QINGXIAOSHUO = "qingxiaoshuo"  # 轻小说 - Light Novel
    TONGREN = "tongren"           # 同人 - Fan Fiction
    DANMEI = "danmei"             # 耽美 - Boys' Love
    BAIHE = "baihe"              # 百合 - Girls' Love
    NVZUN = "nvzun"               # 女尊 - Female Lead in Authority
    ZHICHANG = "zhichang"         # 职场 - Workplace

    # Western genres (aliases)
    FANTASY = "fantasy"            # Fantasy
    SCI_FI = "sci_fi"             # Science Fiction
    URBAN_FANTASY = "urban_fantasy" # Urban Fantasy
    ROMANCE = "romance"           # Romance
    MYSTERY = "mystery"           # Mystery
    THRILLER = "thriller"         # Thriller
    HORROR = "horror"             # Horror
    LITERARY = "literary"         # Literary Fiction
    ACTION = "action"             # Action/Adventure
    HISTORICAL_FICTION = "historical_fiction"  # Historical Fiction


class WorldSettingType(str, Enum):
    """Type of world setting for a genre."""
    REALISTIC = "realistic"               # Real-world modern/historical
    LOW_FANTASY = "low_fantasy"           # Magic exists but rare
    HIGH_FANTASY = "high_fantasy"         # Full fantasy world
    SCI_FI_WORLD = "sci_fi_world"         # Science fiction setting
    URBAN_MODERN = "urban_modern"         # Modern city setting
    POST_APOCALYPTIC = "post_apocalyptic" # After civilization collapse
    ALTERNATE_HISTORY = "alternate_history" # Historical with fictional elements


class MagicTechnologyLevel(str, Enum):
    """Level of magic/technology in the world."""
    NONE = "none"                         # No magic or advanced tech
    LOW = "low"                           # Limited magic/primitive tech
    MEDIUM = "medium"                     # Moderate magic/standard tech
    HIGH = "high"                         # Advanced magic/modern tech
    ULTRA = "ultra"                       # Highly advanced magic/tech


class PlotStructureType(str, Enum):
    """Plot structure types common in specific genres."""
    THREE_ACT = "three_act"               # Classic three-act structure
    HEROS_JOURNEY = "heros_journey"       # Hero's journey/monomyth
    SEVEN_POINT = "seven_point"            # Seven-point story structure
    SAVE_THE_CAT = "save_the_cat"          # Save the Cat structure
    MYSTERY_STRUCTURE = "mystery_structure" # Mystery genre structure (setup/clue/reveal)
    ROMANCE_STRUCTURE = "romance_structure" # Romance structure (meet/struggle/commit)
    SERIAL_ARC = "serial_arc"             # Episodic/arc-based structure


class RomanceType(str, Enum):
    """Types of romance subplots."""
    NONE = "none"                         # No romance
    PRIMARY_ROMANCE = "primary_romance"    # Romance is main plot
    SUBPLOT_ROMANCE = "subplot_romance"   # Romance as subplot
    WILL_THEY_WONT_THEY = "wont_they"      # Slow-burn tension
    FRIENDS_TO_LOVERS = "friends_to_lovers"
    ENEMIES_TO_LOVERS = "enemies_to_lovers"
    RELUCTANT_INTEREST = "reluctant_interest"
    LOVE_TRIANGLE = "love_triangle"
    POLYAMORY = "polyamory"


class ConflictType(str, Enum):
    """Primary conflict types for a genre."""
    EXTERNAL = "external"                 # Outside forces (villain, environment)
    INTERNAL = "internal"                 # Character's inner struggle
    SOCIAL = "social"                     # Society/community conflict
    RELATIONSHIP = "relationship"         # Interpersonal conflict
    SURVIVAL = "survival"                # Survival stakes
    IDEOLOGICAL = "ideological"           # Belief/idea conflict


class TargetAudience(str, Enum):
    """Target audience classification."""
    YOUNG_ADULT = "young_adult"          # YA (13-18)
    NEW_ADULT = "new_adult"              # NA (18-25)
    ADULT = "adult"                       # Adult (25+)
    ALL_AGES = "all_ages"                # All ages


class GenreWorldConfig(BaseModel):
    """Genre-specific world building configuration."""
    genre: NovelGenreType = Field(description="The novel genre")
    world_setting_type: WorldSettingType = Field(
        description="Type of world setting"
    )
    magic_tech_level: MagicTechnologyLevel = Field(
        description="Level of magic/technology"
    )

    # World building priorities (higher = more focus)
    geography_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of geography in world building"
    )
    politics_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of politics in world building"
    )
    culture_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of culture in world building"
    )
    history_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of history in world building"
    )
    magic_system_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of magic system"
    )
    social_structure_importance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Importance of social structure"
    )

    # Special elements
    requires_cultivation_system: bool = Field(
        default=False,
        description="Requires cultivation/leveling system (for xianxia)"
    )
    requires_system_mechanics: bool = Field(
        default=False,
        description="Requires game system mechanics (for game/infinite flow)"
    )
    requires_modern_technology: bool = Field(
        default=False,
        description="Requires modern technology level"
    )


class GenreCharacterTemplate(BaseModel):
    """Genre-specific character template configuration."""
    genre: NovelGenreType = Field(description="The novel genre")

    # Character archetype preferences
    common_archetypes: list[str] = Field(
        default_factory=list,
        description="Common character archetypes for this genre"
    )

    # Character complexity
    allows_gray_characters: bool = Field(
        default=True,
        description="Allow morally ambiguous characters"
    )
    requires_strong_protagonist: bool = Field(
        default=True,
        description="Require a strong/competent protagonist"
    )
    allows_weak_to_strong: bool = Field(
        default=True,
        description="Allow weak-to-strong character progression"
    )

    # Relationship dynamics
    common_relationship_patterns: list[str] = Field(
        default_factory=list,
        description="Common relationship patterns"
    )
    romance_importance: RomanceType = Field(
        default=RomanceType.NONE,
        description="Importance of romance"
    )

    # Character count ranges
    min_key_characters: int = Field(
        default=5,
        description="Minimum number of key characters"
    )
    max_key_characters: int = Field(
        default=20,
        description="Maximum number of key characters"
    )


class GenrePlotConfig(BaseModel):
    """Genre-specific plot structure configuration."""
    genre: NovelGenreType = Field(description="The novel genre")

    # Plot structure
    recommended_structure: PlotStructureType = Field(
        description="Recommended plot structure"
    )
    allows_multiple_plots: bool = Field(
        default=True,
        description="Allow multiple plot threads"
    )
    plot_complexity: str = Field(
        default="moderate",
        description="Plot complexity level: simple, moderate, complex"
    )

    # Pacing
    typical_pacing: str = Field(
        default="moderate",
        description="Typical pacing: slow, moderate, fast"
    )
    chapter_hook_style: str = Field(
        default="cliffhanger",
        description="Chapter ending style: cliffhanger, reveal, transition"
    )

    # Genre-specific plot elements
    common_plot_tropes: list[str] = Field(
        default_factory=list,
        description="Common plot tropes for this genre"
    )
    required_themes: list[str] = Field(
        default_factory=list,
        description="Themes that should be explored"
    )
    taboo_themes: list[str] = Field(
        default_factory=list,
        description="Themes to avoid"
    )

    # Conflict
    primary_conflict_type: ConflictType = Field(
        default=ConflictType.EXTERNAL,
        description="Primary conflict type"
    )


class GenreStyleConfig(BaseModel):
    """Genre-specific style configuration."""
    genre: NovelGenreType = Field(description="The novel genre")

    # Narrative style
    typical_narrative_voice: str = Field(
        default="third_limited",
        description="Typical narrative voice"
    )
    allows_multiple_pov: bool = Field(
        default=False,
        description="Allow multiple POV characters"
    )

    # Tone
    typical_tones: list[str] = Field(
        default_factory=list,
        description="Typical narrative tones"
    )
    tone_flexibility: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="How much tone can vary"
    )

    # Description density
    typical_description_density: str = Field(
        default="moderate",
        description="Typical description density: sparse, moderate, rich"
    )

    # Dialogue
    typical_dialogue_ratio: float = Field(
        default=0.3, ge=0.0, le=1.0,
        description="Typical dialogue ratio"
    )
    internal_thought_typical: float = Field(
        default=0.1, ge=0.0, le=1.0,
        description="Typical internal thought amount"
    )

    # Genre-specific style markers
    common_style_elements: list[str] = Field(
        default_factory=list,
        description="Common style elements"
    )
    genre_specific_vocabulary: list[str] = Field(
        default_factory=list,
        description="Genre-specific vocabulary to use"
    )


class GenreToneConfig(BaseModel):
    """Genre-specific tone configuration."""
    genre: NovelGenreType = Field(description="The novel genre")

    # Overall tone
    primary_tone: str = Field(description="Primary narrative tone")
    secondary_tones: list[str] = Field(
        default_factory=list,
        description="Secondary tones"
    )

    # Emotional range
    emotional_intensity: str = Field(
        default="moderate",
        description="Emotional intensity: low, moderate, high"
    )
    allows_humor: bool = Field(
        default=True,
        description="Allow humorous elements"
    )
    allows_tragedy: bool = Field(
        default=True,
        description="Allow tragic elements"
    )

    # Seriousness
    typical_severity: str = Field(
        default="moderate",
        description="Typical severity: light, moderate, serious"
    )


class NovelGenreProfile(BaseModel):
    """Complete genre profile for a novel."""
    genre: NovelGenreType = Field(description="Primary genre")
    sub_genres: list[NovelGenreType] = Field(
        default_factory=list,
        description="Secondary/sub genres"
    )

    # Components
    world_config: GenreWorldConfig = Field(
        description="World building configuration"
    )
    character_template: GenreCharacterTemplate = Field(
        description="Character template configuration"
    )
    plot_config: GenrePlotConfig = Field(
        description="Plot structure configuration"
    )
    style_config: GenreStyleConfig = Field(
        description="Style configuration"
    )
    tone_config: GenreToneConfig = Field(
        description="Tone configuration"
    )

    # Audience
    target_audience: TargetAudience = Field(
        default=TargetAudience.NEW_ADULT,
        description="Target audience"
    )

    # Additional
    genre_tags: list[str] = Field(
        default_factory=list,
        description="Genre-specific tags for categorization"
    )
    comparable_works: list[str] = Field(
        default_factory=list,
        description="Comparable published works"
    )
    notes: str = Field(
        default="",
        description="Additional notes about this genre profile"
    )


class GenreAnalysisResult(BaseModel):
    """Result of genre analysis."""
    detected_genre: NovelGenreType = Field(
        description="Detected primary genre"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Detection confidence"
    )
    genre_evidence: dict[str, float] = Field(
        default_factory=dict,
        description="Evidence scores for each genre"
    )
    sub_genres: list[NovelGenreType] = Field(
        default_factory=list,
        description="Detected sub-genres"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for genre adaptation"
    )


class GenreTemplate(BaseModel):
    """Pre-built genre template."""
    template_name: str = Field(description="Template name")
    template_description: str = Field(description="Template description")
    genre: NovelGenreType = Field(description="Genre type")

    world_config: GenreWorldConfig = Field(
        description="World configuration"
    )
    character_template: GenreCharacterTemplate = Field(
        description="Character template"
    )
    plot_config: GenrePlotConfig = Field(
        description="Plot configuration"
    )
    style_config: GenreStyleConfig = Field(
        description="Style configuration"
    )
    tone_config: GenreToneConfig = Field(
        description="Tone configuration"
    )

    target_audience: TargetAudience = Field(
        default=TargetAudience.NEW_ADULT
    )

    def to_genre_profile(self) -> NovelGenreProfile:
        """Convert template to NovelGenreProfile."""
        return NovelGenreProfile(
            genre=self.genre,
            world_config=self.world_config,
            character_template=self.character_template,
            plot_config=self.plot_config,
            style_config=self.style_config,
            tone_config=self.tone_config,
            target_audience=self.target_audience,
        )


class GenreRecommendation(BaseModel):
    """Recommendation for a specific genre feature."""
    genre: NovelGenreType = Field(description="Recommended genre")
    priority: int = Field(
        default=50,
        description="Priority (1-100)"
    )
    reason: str = Field(
        description="Why this genre is recommended"
    )
    expected_appeal: str = Field(
        description="Expected reader appeal"
    )
