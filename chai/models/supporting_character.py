"""Supporting character models for secondary characters that support the protagonist."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class SupportingRoleType(str, Enum):
    """Types of supporting character roles."""
    MENTOR = "mentor"  # 导师型 - guides and teaches protagonist
    SIDEKICK = "sidekick"  # 助手型 - loyal companion
    BEST_FRIEND = "best_friend"  # 挚友型 - close friend
    LOVE_INTEREST = "love_interest"  # 爱人型 - romantic interest
    MENTEE = "mentee"  # 学徒型 - student of protagonist
    ALLY = "ally"  # 同盟型 - temporary or permanent ally
    CONTACT = "contact"  # 线人型 - provides information
    EXPERT = "expert"  # 专家型 - provides expertise
    COMIC_RELIEF = "comic_relief"  # 喜剧型 - humor provider
    WISDOM_KEEPER = "wisdom_keeper"  # 智者型 - ancient wisdom
    FOIL = "foil"  # 对照型 - contrasts with protagonist
    FALLEN_ALLY = "fallen_ally"  # 堕落同盟 - former ally turned enemy
    RETIRED_HERO = "retired_hero"  # 隐退英雄 - former protagonist
    INFORMANT = "informant"  # 情报员 - spy/info gatherer


class SupportingArchetype(BaseModel):
    """Supporting character archetype definition."""
    name: str = Field(description="Archetype name")
    description: str = Field(description="Archetype description")
    typical_traits: list[str] = Field(default_factory=list, description="Typical personality traits")
    typical_functions: list[str] = Field(default_factory=list, description="Narrative functions")
    relationship_to_protagonist: str = Field(default="", description="Typical relationship dynamic")
    growth_potential: str = Field(default="", description="Growth potential")
    common_arcs: list[str] = Field(default_factory=list, description="Typical character arcs")


class SupportingCharacterAppearance(BaseModel):
    """Physical appearance details for supporting characters."""
    face: str = Field(default="", description="Facial features")
    eyes: str = Field(default="", description="Eye description")
    hair: str = Field(default="", description="Hair style and color")
    body: str = Field(default="", description="Build and physique")
    skin: str = Field(default="", description="Skin description")
    dressing: str = Field(default="", description="Dressing style")
    accessories: list[str] = Field(default_factory=list, description="Accessories")
    overall: str = Field(default="", description="Overall impression")


class SupportingCharacterPersonality(BaseModel):
    """Personality details for supporting characters."""
    core_traits: list[str] = Field(default_factory=list, description="Core personality traits")
    personality_description: str = Field(default="", description="Detailed personality description")
    mbti: str = Field(default="", description="MBTI type")
    values: list[str] = Field(default_factory=list, description="Core values")
    fears: list[str] = Field(default_factory=list, description="Fears")
    desires: list[str] = Field(default_factory=list, description="Desires")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses")
    habits: list[str] = Field(default_factory=list, description="Habits and mannerisms")
    emotional_pattern: str = Field(default="", description="Typical emotional responses")


class SupportingCharacterBackground(BaseModel):
    """Background details for supporting characters."""
    origin: str = Field(default="", description="Where they come from")
    family_background: str = Field(default="", description="Family background")
    education: str = Field(default="", description="Education and training")
    previous_occupations: list[str] = Field(default_factory=list, description="Previous jobs")
    key_experiences: list[str] = Field(default_factory=list, description="Key life experiences")
    formative_events: list[str] = Field(default_factory=list, description="Events that shaped them")
    socioeconomic_status: str = Field(default="", description="Social and economic status")


class SupportingCharacterMotivation(BaseModel):
    """Motivation details for supporting characters."""
    surface_motivation: str = Field(default="", description="Surface-level motivation")
    deep_motivation: str = Field(default="", description="Deep underlying motivation")
    motivation_type: str = Field(default="", description="Motivation category")
    motivation_source: str = Field(default="", description="What created this motivation")
    motivation_for_allying: str = Field(default="", description="Why they support protagonist")
    personal_goals: list[str] = Field(default_factory=list, description="Their own goals")
    conflicts_with_protagonist: list[str] = Field(default_factory=list, description="Potential conflicts")


class SupportingCharacterRelationship(BaseModel):
    """Relationship between supporting character and protagonist."""
    protagonist_id: str = Field(default="", description="Protagonist's character ID")
    protagonist_name: str = Field(default="", description="Protagonist's name")
    relationship_type: str = Field(default="", description="Type of relationship")
    relationship_dynamics: str = Field(default="", description="How the relationship works")
    relationship_history: str = Field(default="", description="How the relationship formed")
    current_status: str = Field(default="", description="Current relationship status")
    key_events: list[str] = Field(default_factory=list, description="Key events in relationship")
    support_functions: list[str] = Field(default_factory=list, description="How they support protagonist")
    future_potential: str = Field(default="", description="Where the relationship might go")


class SupportingCharacterArc(BaseModel):
    """Character arc details for supporting characters."""
    archetype: str = Field(default="", description="Character archetype")
    growth_arc: str = Field(default="", description="Character growth arc")
    starting_state: str = Field(default="", description="Initial state")
    ending_state: str = Field(default="", description="Final state")
    transformation: str = Field(default="", description="What transformation occurs")
    lessons_learned: list[str] = Field(default_factory=list, description="Lessons through story")
    impact_on_story: str = Field(default="", description="Their narrative impact")


class SupportingCharacterSkill(BaseModel):
    """Skill or ability of supporting character."""
    name: str = Field(description="Skill name")
    description: str = Field(default="", description="Skill description")
    category: str = Field(default="", description="Skill category")
    proficiency_level: str = Field(default="", description="Proficiency level")
    source: str = Field(default="", description="How skill was acquired")
    usefulness_to_protagonist: str = Field(default="", description="How protagonist benefits")


class SupportingCharacterConflict(BaseModel):
    """Conflict involving supporting character."""
    conflict_type: str = Field(description="Type: internal, external, interpersonal")
    description: str = Field(description="Conflict description")
    parties_involved: list[str] = Field(default_factory=list, description="People involved")
    cause: str = Field(default="", description="Root cause")
    stakes: str = Field(default="", description="What's at stake")
    resolution: str = Field(default="", description="How it might be resolved")


class SupportingCharacter(BaseModel):
    """Supporting character model for secondary characters.

    Supporting characters are those who support the protagonist in various ways.
    They can be mentors, sidekicks, best friends, love interests, allies, etc.
    Each has their own arc, motivations, and relationship with the protagonist.
    """

    id: str = Field(description="Unique character identifier")
    name: str = Field(description="Character name")

    # Role classification
    supporting_role_type: SupportingRoleType = Field(
        description="Type of supporting role"
    )
    description: str = Field(default="", description="Brief description")

    # Physical appearance
    age: Optional[str] = Field(default=None, description="Age description")
    age_numeric: Optional[int] = Field(default=None, description="Numeric age")
    appearance: SupportingCharacterAppearance = Field(
        default_factory=SupportingCharacterAppearance,
        description="Physical appearance details"
    )
    distinguishing_features: list[str] = Field(
        default_factory=list,
        description="Distinguishing physical features"
    )
    presence: str = Field(
        default="",
        description="How they present themselves (charisma, aura)"
    )

    # Personality
    personality: SupportingCharacterPersonality = Field(
        default_factory=SupportingCharacterPersonality,
        description="Personality details"
    )

    # Background
    background: SupportingCharacterBackground = Field(
        default_factory=SupportingCharacterBackground,
        description="Background details"
    )
    backstory: str = Field(default="", description="Character backstory")

    # Motivation
    motivation: SupportingCharacterMotivation = Field(
        default_factory=SupportingCharacterMotivation,
        description="Motivation details"
    )

    # Relationship with protagonist
    relationship_to_protagonist: SupportingCharacterRelationship = Field(
        default_factory=SupportingCharacterRelationship,
        description="Relationship details with protagonist"
    )

    # Skills and abilities
    skills: list[SupportingCharacterSkill] = Field(
        default_factory=list,
        description="Character's skills"
    )
    combat_abilities: list[str] = Field(
        default_factory=list,
        description="Combat capabilities"
    )
    social_abilities: list[str] = Field(
        default_factory=list,
        description="Social capabilities"
    )
    intellectual_abilities: list[str] = Field(
        default_factory=list,
        description="Intellectual capabilities"
    )

    # Equipment and resources
    equipment: list[str] = Field(
        default_factory=list,
        description="Important items/equipment"
    )
    resources: list[str] = Field(
        default_factory=list,
        description="Resources they control"
    )

    # Character arc
    character_arc: SupportingCharacterArc = Field(
        default_factory=SupportingCharacterArc,
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
        description="Emotional wounds"
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
    screen_time_estimate: str = Field(
        default="",
        description="Estimated screen time (high/medium/low)"
    )

    # Conflicts
    conflicts: list[SupportingCharacterConflict] = Field(
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
        description="Current status (active, deceased, missing, retired)"
    )


class SupportingCharacterProfile(BaseModel):
    """Complete supporting character profile with all details."""

    basic_info: dict = Field(
        default_factory=dict,
        description="Basic character information"
    )
    appearance: SupportingCharacterAppearance = Field(
        default_factory=SupportingCharacterAppearance,
        description="Physical appearance"
    )
    personality: SupportingCharacterPersonality = Field(
        default_factory=SupportingCharacterPersonality,
        description="Personality"
    )
    background: SupportingCharacterBackground = Field(
        default_factory=SupportingCharacterBackground,
        description="Background"
    )
    motivation: SupportingCharacterMotivation = Field(
        default_factory=SupportingCharacterMotivation,
        description="Motivation"
    )
    relationship_to_protagonist: SupportingCharacterRelationship = Field(
        default_factory=SupportingCharacterRelationship,
        description="Relationship"
    )
    skills: list[SupportingCharacterSkill] = Field(
        default_factory=list,
        description="Skills"
    )
    character_arc: SupportingCharacterArc = Field(
        default_factory=SupportingCharacterArc,
        description="Character arc"
    )
    speech_pattern: str = Field(default="", description="Speech pattern")
    catchphrases: list[str] = Field(default_factory=list, description="Catchphrases")
    narrative_function: str = Field(default="", description="Narrative function")
    thematic_significance: str = Field(default="", description="Thematic significance")


class SupportingCharacterSystem(BaseModel):
    """System for managing multiple supporting characters."""

    name: str = Field(default="", description="System name")
    protagonist_id: str = Field(default="", description="Associated protagonist ID")
    supporting_characters: list[SupportingCharacter] = Field(
        default_factory=list,
        description="All supporting characters"
    )
    archetypes: list[SupportingArchetype] = Field(
        default_factory=list,
        description="Available supporting archetypes"
    )
    relationship_templates: list[dict] = Field(
        default_factory=list,
        description="Relationship templates"
    )
    role_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Suggested role distribution"
    )