"""Main character (protagonist) models for enhanced protagonist representation."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class MotivationType(str, Enum):
    """Types of character motivations."""
    REVENGE = "revenge"  # 复仇型
    PROTECTION = "protection"  # 守护型
    POWER = "power"  # 力量型
    LOVE = "love"  # 爱情型
    JUSTICE = "justice"  # 正义型
    SURVIVAL = "survival"  # 生存型
    REDEMPTION = "redemption"  # 救赎型
    DISCOVERY = "discovery"  # 探索型
    BELONGING = "belonging"  # 归属型
    GROWTH = "growth"  # 成长型


class PersonalityDimension(BaseModel):
    """Detailed personality dimension analysis."""
    openness: int = Field(default=5, description="开放度 1-10")
    conscientiousness: int = Field(default=5, description="尽责性 1-10")
    extraversion: int = Field(default=5, description="外向性 1-10")
    agreeableness: int = Field(default=5, description="宜人性 1-10")
    neuroticism: int = Field(default=5, description="神经质 1-10")


class AppearanceDetail(BaseModel):
    """Detailed physical appearance of the character."""
    face: str = Field(default="", description="面部特征")
    eyes: str = Field(default="", description="眼睛描写")
    hair: str = Field(default="", description="发型发色")
    body: str = Field(default="", description="体型身材")
    skin: str = Field(default="", description="肤色肤质")
    dressing: str = Field(default="", description="着装风格")
    accessories: list[str] = Field(default_factory=list, description="配饰")
    overall: str = Field(default="", description="整体形象")


class BackgroundDetail(BaseModel):
    """Detailed background information."""
    birth_place: str = Field(default="", description="出生地点")
    birth_era: str = Field(default="", description="出生时代")
    childhood: str = Field(default="", description="童年经历")
    adolescence: str = Field(default="", description="青少年时期")
    early_adulthood: str = Field(default="", description="成年早期")
    family_members: list[dict] = Field(default_factory=list, description="家庭成员")
    socioeconomic_status: str = Field(default="", description="社会经济地位")
    education_background: str = Field(default="", description="教育背景")
    career_path: list[str] = Field(default_factory=list, description="职业经历")
    key_events: list[str] = Field(default_factory=list, description="关键事件")
    turning_points: list[str] = Field(default_factory=list, description="转折点")


class MotivationDetail(BaseModel):
    """Detailed motivation analysis."""
    surface_motivation: str = Field(default="", description="表面动机")
    deep_motivation: str = Field(default="", description="深层动机")
    motivation_type: str = Field(default="", description="动机类型")
    motivation_source: str = Field(default="", description="动机来源")
    motivation_conflict: str = Field(default="", description="动机冲突")
    driving_force: str = Field(default="", description="驱动力")
    obstacles: list[str] = Field(default_factory=list, description="阻碍因素")
    internal_conflict: str = Field(default="", description="内心冲突")
    fear_core: str = Field(default="", description="核心恐惧")
    desire_core: str = Field(default="", description="核心欲望")


class MainCharacter(BaseModel):
    """Enhanced main character (protagonist) model.

    This model extends the base Character model with specialized
    depth for the 4 core aspects: appearance, personality, background, motivation.
    """

    id: str = Field(description="Unique character identifier")
    name: str = Field(description="Character name")

    # Enhanced appearance (外貌)
    age: Optional[str] = Field(default=None, description="Age description")
    age_numeric: Optional[int] = Field(default=None, description="Numeric age")
    appearance_detail: AppearanceDetail = Field(
        default_factory=AppearanceDetail,
        description="Detailed physical appearance"
    )
    distinguishing_features: list[str] = Field(
        default_factory=list,
        description="Distinguishing physical features"
    )
    presence: str = Field(
        default="",
        description="How the character presents themselves"
    )
    first_impression: str = Field(
        default="",
        description="First impression others have of this character"
    )

    # Enhanced personality (性格)
    personality_dimension: PersonalityDimension = Field(
        default_factory=PersonalityDimension,
        description="Big Five personality dimensions"
    )
    personality_description: str = Field(
        default="",
        description="Detailed personality description"
    )
    mbti: str = Field(default="", description="MBTI personality type")
    values: list[str] = Field(default_factory=list, description="Core values")
    fears: list[str] = Field(default_factory=list, description="Character fears")
    desires: list[str] = Field(default_factory=list, description="Character desires")
    strengths: list[str] = Field(default_factory=list, description="Character strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Character weaknesses")
    habits: list[str] = Field(default_factory=list, description="Habits and mannerisms")
    emotional_pattern: str = Field(
        default="",
        description="Typical emotional response pattern"
    )

    # Enhanced background (背景)
    background_detail: BackgroundDetail = Field(
        default_factory=BackgroundDetail,
        description="Detailed background information"
    )
    backstory: str = Field(default="", description="Character backstory summary")
    origin: str = Field(default="", description="Where the character comes from")
    family_background: str = Field(default="", description="Family background")
    formative_experiences: list[str] = Field(
        default_factory=list,
        description="Key experiences that shaped them"
    )

    # Enhanced motivation (动机)
    motivation_detail: MotivationDetail = Field(
        default_factory=MotivationDetail,
        description="Detailed motivation analysis"
    )
    motivation: str = Field(default="", description="Character motivation summary")
    goal: str = Field(default="", description="Character's main goal")
    internal_conflict: str = Field(default="", description="Internal conflict")

    # Character arc
    archetype: str = Field(default="", description="Character archetype")
    growth_arc: str = Field(
        default="",
        description="Character growth and development arc"
    )
    starting_state: str = Field(default="", description="Starting state")
    ending_state: str = Field(default="", description="Ending state after growth")

    # Dialogue
    speech_pattern: str = Field(
        default="",
        description="Speech patterns and catchphrases"
    )
    catchphrases: list[str] = Field(
        default_factory=list,
        description="Character's catchphrases"
    )
    communication_style: str = Field(
        default="",
        description="How the character communicates"
    )

    # Story function
    narrative_function: str = Field(
        default="",
        description="Narrative function in the story"
    )
    thematic_significance: str = Field(
        default="",
        description="Thematic significance"
    )
    character_arc_summary: str = Field(
        default="",
        description="One-sentence arc summary"
    )

    # Story progression
    first_appearance: str = Field(
        default="",
        description="When the character first appears"
    )
    status: str = Field(
        default="active",
        description="Current status (active, deceased, missing, etc.)"
    )


class MainCharacterProfile(BaseModel):
    """Complete main character profile with all details."""

    # Basic identity
    basic_info: dict = Field(
        default_factory=dict,
        description="Basic character information"
    )

    # Four core aspects
    appearance: AppearanceDetail = Field(
        default_factory=AppearanceDetail,
        description="Physical appearance"
    )
    personality: PersonalityDimension = Field(
        default_factory=PersonalityDimension,
        description="Personality dimensions"
    )
    background: BackgroundDetail = Field(
        default_factory=BackgroundDetail,
        description="Background details"
    )
    motivation: MotivationDetail = Field(
        default_factory=MotivationDetail,
        description="Motivation details"
    )

    # Character development
    values: list[str] = Field(default_factory=list, description="Core values")
    fears: list[str] = Field(default_factory=list, description="Fears")
    desires: list[str] = Field(default_factory=list, description="Desires")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses")

    # Arc
    archetype: str = Field(default="", description="Character archetype")
    growth_arc: str = Field(default="", description="Growth arc description")
    starting_state: str = Field(default="", description="Starting state")
    ending_state: str = Field(default="", description="Ending state")

    # Dialogue
    speech_pattern: str = Field(default="", description="Speech pattern")
    catchphrases: list[str] = Field(default_factory=list, description="Catchphrases")

    # Story
    narrative_function: str = Field(default="", description="Narrative function")
    thematic_significance: str = Field(default="", description="Thematic significance")
