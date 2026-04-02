"""Character models for novel characters."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class CharacterRole(str, Enum):
    """Character role types."""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"
    MENTOR = "mentor"
    LOVE_INTEREST = "love_interest"
    SIDEKICK = "sidekick"
    DEuteragonist = "deuteragonist"


class CharacterRelationshipType(str, Enum):
    """Types of relationships between characters."""
    FAMILY = "family"
    FRIEND = "friend"
    ENEMY = "enemy"
    RIVAL = "rival"
    LOVER = "lover"
    MENTOR = "mentor"
    STUDENT = "student"
    COLLEAGUE = "colleague"
    SUPERIOR = "superior"
    SUBORDINATE = "subordinate"
    ALLY = "ally"
    Nemesis = "nemesis"


class CharacterRelationship(BaseModel):
    """Relationship between two characters."""

    character_id: str = Field(description="Related character ID")
    character_name: str = Field(default="", description="Related character name for display")
    relationship_type: str = Field(description="Type: family, friend, enemy, lover, mentor, etc.")
    description: str = Field(description="Relationship description")
    dynamics: str = Field(description="Interaction dynamics")
    history: str = Field(default="", description="How this relationship formed")
    current_status: str = Field(default="", description="Current status of relationship")
    key_events: list[str] = Field(default_factory=list, description="Key events in this relationship")


class CharacterArchetype(BaseModel):
    """Character archetype definition."""
    name: str = Field(description="Archetype name (e.g., The Hero, The Mentor)")
    description: str = Field(description="Archetype description")
    typical_traits: list[str] = Field(default_factory=list, description="Typical personality traits")
    typical_motivations: list[str] = Field(default_factory=list, description="Typical motivations")
    typical_weaknesses: list[str] = Field(default_factory=list, description="Typical weaknesses")
    growth_potential: str = Field(default="", description="Typical growth potential")
    examples_in_literature: list[str] = Field(default_factory=list, description="Famous examples")


class CharacterSkill(BaseModel):
    """Character skill or ability."""
    name: str = Field(description="Skill name")
    description: str = Field(default="", description="Skill description")
    category: str = Field(default="", description="Skill category (combat, social, magical, etc.)")
    proficiency_level: str = Field(default="", description="Proficiency: beginner, intermediate, advanced, master")
    source: str = Field(default="", description="How the skill was acquired")
    conditions: list[str] = Field(default_factory=list, description="Conditions for using this skill")
    limitations: list[str] = Field(default_factory=list, description="Skill limitations")
    synergy_with_other_skills: list[str] = Field(default_factory=list, description="Skills that work well with this")


class CharacterGroup(BaseModel):
    """Group, organization, or team a character belongs to."""
    group_id: str = Field(description="Group identifier")
    name: str = Field(description="Group name")
    group_type: str = Field(description="Type: faction, family, guild, team, etc.")
    role: str = Field(default="", description="Character's role in the group")
    position: str = Field(default="", description="Position/rank in the group")
    joined_at: str = Field(default="", description="When character joined")
    tenure: str = Field(default="", description="Duration of membership")
    contributions: list[str] = Field(default_factory=list, description="Character's contributions")
    group_reputation: str = Field(default="", description="Character's reputation within group")
    group_conflicts: list[str] = Field(default_factory=list, description="Conflicts within the group")


class CharacterConflict(BaseModel):
    """Character's internal or external conflicts."""
    conflict_type: str = Field(description="Type: internal, external, interpersonal")
    description: str = Field(description="Conflict description")
    parties_involved: list[str] = Field(default_factory=list, description="Other parties involved")
    cause: str = Field(default="", description="Root cause")
    stakes: str = Field(default="", description="What's at stake")
    current_status: str = Field(default="", description="Current status (active, resolved, escalating)")
    potential_resolution: str = Field(default="", description="Possible ways to resolve")
    impact_on_character: str = Field(default="", description="How this affects the character")


class CharacterGrowthStage(BaseModel):
    """A stage in character's growth arc."""
    stage_name: str = Field(description="Name of this stage")
    description: str = Field(description="What happens at this stage")
    trigger_event: str = Field(default="", description="Event that triggers this stage")
    lessons_learned: list[str] = Field(default_factory=list, description="Lessons the character learns")
    new_abilities_or_insights: list[str] = Field(default_factory=list, description="What the character gains")
    emotional_state: str = Field(default="", description="Character's emotional state")
    chapter_or_arc_reference: str = Field(default="", description="When this occurs in story")


class CharacterSystem(BaseModel):
    """Complete character system with archetypes, relationships, and growth."""

    # System metadata
    name: str = Field(default="", description="Character system name")
    genre: str = Field(default="", description="Genre this system is designed for")
    theme: str = Field(default="", description="Central theme")

    # Character archetypes available in this system
    archetypes: list[CharacterArchetype] = Field(
        default_factory=list,
        description="Available character archetypes"
    )

    # Relationship templates
    relationship_templates: list[dict] = Field(
        default_factory=list,
        description="Templates for character relationships"
    )

    # Character generation guidelines
    generation_guidelines: str = Field(
        default="",
        description="Guidelines for generating characters"
    )

    # Statistical distribution suggestions
    role_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Suggested distribution of character roles"
    )

    # Group/organization templates
    group_templates: list[dict] = Field(
        default_factory=list,
        description="Templates for character groups"
    )


class Character(BaseModel):
    """Character model with full attributes."""

    id: str = Field(description="Unique character identifier")
    name: str = Field(description="Character name")

    role: CharacterRole = Field(description="Character role in story")

    # Enhanced appearance
    age: Optional[str] = Field(default=None, description="Age description")
    age_numeric: Optional[int] = Field(default=None, description="Numeric age if applicable")
    appearance: dict = Field(
        default_factory=dict,
        description="Physical appearance details"
    )
    distinguishing_features: list[str] = Field(
        default_factory=list,
        description="Distinguishing physical features"
    )
    presence: str = Field(
        default="",
        description="How the character presents themselves (charisma, aura, etc.)"
    )

    # Enhanced personality
    personality: dict = Field(
        default_factory=dict,
        description="Personality traits and MBTI if applicable"
    )
    personality_description: str = Field(
        default="",
        description="Detailed personality description"
    )
    values: list[str] = Field(
        default_factory=list,
        description="Core values"
    )
    fears: list[str] = Field(
        default_factory=list,
        description="Character's fears"
    )
    desires: list[str] = Field(
        default_factory=list,
        description="Character's deepest desires"
    )
    strengths: list[str] = Field(default_factory=list, description="Character strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Character weaknesses")
    habits: list[str] = Field(default_factory=list, description="Habits and mannerisms")

    # Enhanced background
    backstory: str = Field(default="", description="Character backstory")
    origin: str = Field(default="", description="Where the character comes from")
    family_background: str = Field(default="", description="Family background")
    education: str = Field(default="", description="Education and training")
    previous_occupations: list[str] = Field(default_factory=list, description="Previous jobs/roles")
    formative_experiences: list[str] = Field(default_factory=list, description="Key experiences that shaped them")
    motivation: str = Field(default="", description="Character motivation")
    goal: str = Field(default="", description="Character's main goal")
    internal_conflict: str = Field(default="", description="Internal conflict")

    # Skills and abilities
    skills: list[CharacterSkill] = Field(
        default_factory=list,
        description="Character's skills and abilities"
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
        description="Intellectual/analytical capabilities"
    )

    # Resources and equipment
    resources: list[str] = Field(
        default_factory=list,
        description="Resources the character has access to"
    )
    equipment: list[str] = Field(
        default_factory=list,
        description="Important items/equipment"
    )
    vehicles: list[str] = Field(
        default_factory=list,
        description="Vehicles the character uses"
    )

    # Group affiliations
    groups: list[CharacterGroup] = Field(
        default_factory=list,
        description="Groups/organizations the character belongs to"
    )

    # Relationships
    relationships: list[CharacterRelationship] = Field(
        default_factory=list,
        description="Character relationships"
    )

    # Character arc - enhanced
    archetype: str = Field(default="", description="Character archetype")
    growth_arc: str = Field(
        default="",
        description="Character growth and development arc"
    )
    growth_stages: list[CharacterGrowthStage] = Field(
        default_factory=list,
        description="Detailed growth stages"
    )
    starting_state: str = Field(default="", description="Starting state")
    ending_state: str = Field(default="", description="Ending state after growth")
    character_development_notes: str = Field(
        default="",
        description="Detailed development notes"
    )

    # Psychological profile
    psychological_profile: dict = Field(
        default_factory=dict,
        description="Psychological profile details"
    )
    attachment_style: str = Field(default="", description="Attachment style")
    defense_mechanisms: list[str] = Field(default_factory=list, description="Defense mechanisms")
    emotional_wounds: list[str] = Field(default_factory=list, description="Emotional wounds")
    resilience_factors: list[str] = Field(default_factory=list, description="What helps them cope")

    # Dialogue - enhanced
    speech_pattern: str = Field(
        default="",
        description="Speech patterns and catchphrases"
    )
    speech_characteristics: list[str] = Field(
        default_factory=list,
        description="Speech characteristics (accent, vocabulary, etc.)"
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

    # Conflicts
    conflicts: list[CharacterConflict] = Field(
        default_factory=list,
        description="Character's conflicts"
    )

    # Story progression
    first_appearance: str = Field(
        default="",
        description="When the character first appears"
    )
    death: Optional[str] = Field(
        default=None,
        description="Death information if character dies"
    )
    status: str = Field(
        default="active",
        description="Current status (active, deceased, missing, etc.)"
    )
