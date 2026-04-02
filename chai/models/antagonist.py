"""Antagonist models for villain and opposing character representation."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class AntagonistType(str, Enum):
    """Types of antagonist roles."""
    VILLAIN = "villain"  # 恶棍型 - pure evil
    DARK_HERO = "dark_hero"  # 黑暗英雄型 - morally grey
    TEMPORARY_ANTAGONIST = "temporary_antagonist"  # 临时反派 - former ally
    ETERNAL_RIVAL = "eternal_rival"  # 终身对手 - persistent adversary
    TYRANT = "tyrant"  # 暴君型 - oppressive ruler
    MANIPULATOR = "manipulator"  # 操控者型 - uses others
    REVENGE_SEEKER = "revenge_seeker"  # 复仇者型 - driven by revenge
    CORRUPTED = "corrupted"  # 堕落型 - was good, became evil
    IDEOLOGICAL = "ideological"  # 意识形态型 - believes in opposing cause
    TRAGIC_ANTAGONIST = "tragic_antagonist"  # 悲剧反派 - sympathetic villain
    MINION = "minion"  # 爪牙型 - works for真正的敌人
    BIG_BAD = "big_bad"  # 大反派 - main villain
    TEMPTER = "tempter"  # 诱惑者型 - tempts protagonist
    SHADOW = "shadow"  # 影子型 - dark reflection of protagonist
    NEMESIS = "nemesis"  # 死敌型 - ultimate adversary


class AntagonistAppearance(BaseModel):
    """Physical appearance details for antagonists."""
    face: str = Field(default="", description="Facial features")
    eyes: str = Field(default="", description="Eye description (often intimidating)")
    hair: str = Field(default="", description="Hair style and color")
    body: str = Field(default="", description="Build and physique")
    skin: str = Field(default="", description="Skin description")
    dressing: str = Field(default="", description="Dressing style (often imposing)")
    accessories: list[str] = Field(default_factory=list, description="Accessories/symbols")
    overall: str = Field(default="", description="Overall impression (often menacing)")


class AntagonistPersonality(BaseModel):
    """Personality details for antagonists."""
    core_traits: list[str] = Field(default_factory=list, description="Core personality traits")
    personality_description: str = Field(default="", description="Detailed personality description")
    mbti: str = Field(default="", description="MBTI type")
    values: list[str] = Field(default_factory=list, description="Their twisted values")
    moral_alignment: str = Field(default="", description="Moral alignment description")
    fears: list[str] = Field(default_factory=list, description="What they fear")
    desires: list[str] = Field(default_factory=list, description="Deepest desires")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses")
    habits: list[str] = Field(default_factory=list, description="Habits and mannerisms")
    emotional_pattern: str = Field(default="", description="Typical emotional responses")


class AntagonistBackground(BaseModel):
    """Background details for antagonists."""
    origin: str = Field(default="", description="Where they come from")
    family_background: str = Field(default="", description="Family background")
    education: str = Field(default="", description="Education and training")
    previous_occupations: list[str] = Field(default_factory=list, description="Previous roles")
    key_experiences: list[str] = Field(default_factory=list, description="Key life experiences")
    downfall_moments: list[str] = Field(default_factory=list, description="Moments of moral decline")
    socioeconomic_status: str = Field(default="", description="Social and economic status")


class AntagonistMotivation(BaseModel):
    """Motivation details for antagonists."""
    surface_motivation: str = Field(default="", description="Surface-level goal")
    deep_motivation: str = Field(default="", description="Deep psychological motivation")
    motivation_type: str = Field(default="", description="Motivation category")
    motivation_origin: str = Field(default="", description="What created this motivation")
    justification: str = Field(default="", description="How they justify their actions")
    twisted_logic: str = Field(default="", description="Their flawed reasoning")
    personal_goals: list[str] = Field(default_factory=list, description="Their own goals beyond opposing protagonist")
    what_they_lost: str = Field(default="", description="What they lost that drove them")


class AntagonistRelationship(BaseModel):
    """Relationship between antagonist and protagonist."""
    protagonist_id: str = Field(default="", description="Protagonist's character ID")
    protagonist_name: str = Field(default="", description="Protagonist's name")
    relationship_type: str = Field(default="", description="Type of rivalry/opposition")
    relationship_dynamics: str = Field(default="", description="How the opposition works")
    history: str = Field(default="", description="How this rivalry formed")
    current_status: str = Field(default="", description="Current relationship status")
    key_conflicts: list[str] = Field(default_factory=list, description="Key conflict points")
    mirrors_protagonist: bool = Field(default=False, description="Whether antagonist mirrors protagonist")
    symmetry_points: list[str] = Field(default_factory=list, description="Symmetry with protagonist")


class AntagonistPower(BaseModel):
    """Power and abilities of antagonist."""
    power_source: str = Field(default="", description="Where their power comes from")
    power_type: str = Field(default="", description="Type of power (magical, political, etc.)")
    combat_abilities: list[str] = Field(default_factory=list, description="Combat capabilities")
    social_abilities: list[str] = Field(default_factory=list, description="Social/political power")
    intellectual_abilities: list[str] = Field(default_factory=list, description="Intellectual capabilities")
    special_abilities: list[str] = Field(default_factory=list, description="Special/unique abilities")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses that can be exploited")
    power_limitations: str = Field(default="", description="Limits on their power")


class AntagonistOrganization(BaseModel):
    """Organization or forces the antagonist controls."""
    organization_name: str = Field(default="", description="Name of their organization")
    organization_type: str = Field(default="", description="Type of organization")
    size: str = Field(default="", description="Size of organization")
    structure: str = Field(default="", description="Organizational structure")
    key_members: list[str] = Field(default_factory=list, description="Key members")
    resources: list[str] = Field(default_factory=list, description="Resources controlled")
    territories: list[str] = Field(default_factory=list, description="Territories controlled")
    power_base: str = Field(default="", description="Where their power is based")


class AntagonistArc(BaseModel):
    """Character arc details for antagonists."""
    archetype: str = Field(default="", description="Antagonist archetype")
    arc_type: str = Field(default="", description="Type of arc (fall, rise, cycle)")
    starting_state: str = Field(default="", description="Initial state")
    ending_state: str = Field(default="", description="Final state")
    corruption_arc: str = Field(default="", description="How they became antagonist")
    redemption_potential: str = Field(default="", description="Potential for redemption")
    transformation: str = Field(default="", description="What transformation occurs")
    impact_on_protagonist: str = Field(default="", description="How they affect protagonist's arc")


class AntagonistConflict(BaseModel):
    """Conflict involving antagonist."""
    conflict_type: str = Field(description="Type: internal, external")
    description: str = Field(description="Conflict description")
    against_protagonist: list[str] = Field(default_factory=list, description="Points of conflict with protagonist")
    internal_conflict: str = Field(default="", description="Internal struggles")
    external_conflicts: list[str] = Field(default_factory=list, description="Other external conflicts")
    stakes: str = Field(default="", description="What's at stake")
    potential_resolution: str = Field(default="", description="How conflict might be resolved")


class AntagonistTactics(BaseModel):
    """Tactics and methods used by antagonist."""
    preferred_methods: list[str] = Field(default_factory=list, description="Preferred methods")
    manipulation_tactics: list[str] = Field(default_factory=list, description="Manipulation techniques")
    combat_style: str = Field(default="", description="Combat approach")
    social_strategy: str = Field(default="", description="Social/political strategy")
    deception_patterns: list[str] = Field(default_factory=list, description="How they deceive")
    response_to_defeat: str = Field(default="", description="How they respond when losing")


class Antagonist(BaseModel):
    """Antagonist model for villain characters.

    Antagonists are characters who oppose the protagonist.
    They can range from pure evil villains to sympathetic adversaries.
    Each has their own motivations, methods, and relationship with the protagonist.
    """

    id: str = Field(description="Unique character identifier")
    name: str = Field(description="Character name")

    # Role classification
    antagonist_type: AntagonistType = Field(
        description="Type of antagonist"
    )
    description: str = Field(default="", description="Brief description")

    # Physical appearance
    age: Optional[str] = Field(default=None, description="Age description")
    age_numeric: Optional[int] = Field(default=None, description="Numeric age")
    appearance: AntagonistAppearance = Field(
        default_factory=AntagonistAppearance,
        description="Physical appearance details"
    )
    distinguishing_features: list[str] = Field(
        default_factory=list,
        description="Distinguishing physical features"
    )
    presence: str = Field(
        default="",
        description="How they present themselves (often menacing)"
    )
    first_impression: str = Field(
        default="",
        description="First impression on others"
    )

    # Personality
    personality: AntagonistPersonality = Field(
        default_factory=AntagonistPersonality,
        description="Personality details"
    )

    # Background
    background: AntagonistBackground = Field(
        default_factory=AntagonistBackground,
        description="Background details"
    )
    backstory: str = Field(default="", description="Character backstory")
    origin_story: str = Field(default="", description="How they became antagonist")

    # Motivation
    motivation: AntagonistMotivation = Field(
        default_factory=AntagonistMotivation,
        description="Motivation details"
    )

    # Relationship with protagonist
    relationship_to_protagonist: AntagonistRelationship = Field(
        default_factory=AntagonistRelationship,
        description="Relationship details with protagonist"
    )

    # Power and abilities
    power: AntagonistPower = Field(
        default_factory=AntagonistPower,
        description="Power and abilities"
    )

    # Organization
    organization: AntagonistOrganization = Field(
        default_factory=AntagonistOrganization,
        description="Their organization or forces"
    )

    # Tactics
    tactics: AntagonistTactics = Field(
        default_factory=AntagonistTactics,
        description="Their methods and tactics"
    )

    # Character arc
    character_arc: AntagonistArc = Field(
        default_factory=AntagonistArc,
        description="Character development arc"
    )

    # Psychological profile
    psychological_profile: dict = Field(
        default_factory=dict,
        description="Psychological details"
    )
    attachment_style: str = Field(default="", description="Attachment style")
    defense_mechanisms: list[str] = Field(
        default_factory=list,
        description="Defense mechanisms"
    )
    emotional_wounds: list[str] = Field(
        default_factory=list,
        description="Emotional wounds")
    vulnerability: str = Field(
        default="",
        description="Key vulnerability"
    )

    # Speech and dialogue
    speech_pattern: str = Field(
        default="",
        description="Speech patterns and style"
    )
    catchphrases: list[str] = Field(
        default_factory=list,
        description="Character's catchphrases"
    )
    communication_style: str = Field(
        default="",
        description="How they communicate"
    )

    # Narrative function
    narrative_function: str = Field(
        default="",
        description="Narrative function in story"
    )
    thematic_significance: str = Field(
        default="",
        description="Thematic significance"
    )
    threat_level: str = Field(
        default="",
        description="Threat level (low/medium/high/catastrophic)"
    )

    # Conflicts
    conflicts: list[AntagonistConflict] = Field(
        default_factory=list,
        description="Character's conflicts"
    )

    # Story progression
    first_appearance: str = Field(
        default="",
        description="When they first appear"
    )
    death: Optional[str] = Field(
        default=None,
        description="Death information if applicable"
    )
    status: str = Field(
        default="active",
        description="Current status (active, defeated, deceased, reformed)"
    )
    defeat_conditions: list[str] = Field(
        default_factory=list,
        description="Conditions for their defeat"
    )


class AntagonistProfile(BaseModel):
    """Complete antagonist profile with all details."""

    basic_info: dict = Field(
        default_factory=dict,
        description="Basic character information"
    )
    appearance: AntagonistAppearance = Field(
        default_factory=AntagonistAppearance,
        description="Physical appearance"
    )
    personality: AntagonistPersonality = Field(
        default_factory=AntagonistPersonality,
        description="Personality"
    )
    background: AntagonistBackground = Field(
        default_factory=AntagonistBackground,
        description="Background"
    )
    motivation: AntagonistMotivation = Field(
        default_factory=AntagonistMotivation,
        description="Motivation"
    )
    relationship_to_protagonist: AntagonistRelationship = Field(
        default_factory=AntagonistRelationship,
        description="Relationship"
    )
    power: AntagonistPower = Field(
        default_factory=AntagonistPower,
        description="Power and abilities"
    )
    organization: AntagonistOrganization = Field(
        default_factory=AntagonistOrganization,
        description="Organization"
    )
    tactics: AntagonistTactics = Field(
        default_factory=AntagonistTactics,
        description="Tactics"
    )
    character_arc: AntagonistArc = Field(
        default_factory=AntagonistArc,
        description="Character arc"
    )
    speech_pattern: str = Field(default="", description="Speech pattern")
    catchphrases: list[str] = Field(default_factory=list, description="Catchphrases")
    narrative_function: str = Field(default="", description="Narrative function")
    thematic_significance: str = Field(default="", description="Thematic significance")
    threat_level: str = Field(default="", description="Threat level")


class AntagonistSystem(BaseModel):
    """System for managing multiple antagonists."""

    name: str = Field(default="", description="System name")
    protagonist_id: str = Field(default="", description="Associated protagonist ID")
    primary_antagonist: Optional[Antagonist] = Field(
        default=None,
        description="Main villain"
    )
    secondary_antagonists: list[Antagonist] = Field(
        default_factory=list,
        description="Secondary antagonists"
    )
    minion_types: list[str] = Field(
        default_factory=list,
        description="Types of minions"
    )
    organization_templates: list[dict] = Field(
        default_factory=list,
        description="Organization templates for antagonists"
    )
    conflict_potential: str = Field(
        default="",
        description="Potential for conflict escalation"
    )