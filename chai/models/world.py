"""World setting models for novel world-building."""

from typing import Optional
from pydantic import BaseModel, Field


class WorldSetting(BaseModel):
    """Complete world setting including geography, politics, culture, and history."""

    name: str = Field(description="World name")
    genre: str = Field(description="Genre: fantasy, sci-fi, urban, mystery, romance, etc.")

    geography: dict = Field(
        default_factory=dict,
        description="Geographic features: continents, countries, cities, landmarks"
    )
    politics: dict = Field(
        default_factory=dict,
        description="Political structures: governments, factions, alliances"
    )
    culture: dict = Field(
        default_factory=dict,
        description="Cultural elements: religions, languages, traditions, customs"
    )
    history: dict = Field(
        default_factory=dict,
        description="Historical events and timeline"
    )

    magic_system: Optional["MagicSystem"] = Field(default=None, description="Magic/tech/superpower system")
    social_structure: Optional["SocialStructure"] = Field(default=None, description="Social structure and factions")


class MagicSystem(BaseModel):
    """Magic, technology, or superpower system rules.

    Comprehensive system defining how supernatural/extraordinary
    abilities work in the world.
    """

    name: str = Field(description="System name")
    system_type: str = Field(
        description="Type: magic, technology, superpower, mixed, supernatural"
    )

    # Core mechanics
    rules: list[str] = Field(
        default_factory=list,
        description="Fundamental rules of the system"
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="System limitations and costs"
    )
    levels: list[str] = Field(
        default_factory=list,
        description="Power levels or mastery stages"
    )

    # Power source and origin
    source_of_power: str = Field(
        default="",
        description="Origin/source of power (e.g., mana, ki, technology, mutation)"
    )
    power_origin_story: str = Field(
        default="",
        description="How this system came to exist in the world"
    )

    # Schools, types, and styles
    schools_or_types: list[dict] = Field(
        default_factory=list,
        description="Different schools, styles, or branches of the system"
    )

    # How practitioners learn and train
    training_methods: list[dict] = Field(
        default_factory=list,
        description="Methods to learn and master the system"
    )
    typical_training_duration: str = Field(
        default="",
        description="How long it takes to reach proficiency"
    )

    # Artifacts, tools, and items
    artifacts: list[dict] = Field(
        default_factory=list,
        description="Significant items, weapons, or tools related to the system"
    )
    consumables: list[str] = Field(
        default_factory=list,
        description="Consumable items used in the system"
    )

    # Organizations and factions
    organizations: list[dict] = Field(
        default_factory=list,
        description="Groups, sects, orders related to this system"
    )

    # Interactions and conflicts
    power_interactions: list[str] = Field(
        default_factory=list,
        description="How this system interacts with other systems or itself"
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Specific weaknesses or vulnerabilities"
    )

    # Societal impact
    world_influence: str = Field(
        default="",
        description="How this system affects society, politics, culture"
    )
    social_acceptance: str = Field(
        default="",
        description="How society views users of this system (accepted, feared, illegal)"
    )

    # History and evolution
    history: list[dict] = Field(
        default_factory=list,
        description="Historical development and key events"
    )

    # Taboos and forbidden techniques
    forbidden_techniques: list[dict] = Field(
        default_factory=list,
        description="Banned or taboo practices and why"
    )

    # Associated phenomena
    associated_phenomena: list[str] = Field(
        default_factory=list,
        description="Related supernatural phenomena or side effects"
    )


class PowerTechnique(BaseModel):
    """A specific power, spell, skill, or technique within a magic system."""

    name: str = Field(description="Technique name")
    description: str = Field(description="What the technique does")

    # Categorization
    school: str = Field(default="", description="School or style it belongs to")
    type: str = Field(description="Type: attack, defense, support, utility, etc.")

    # Power metrics
    power_level: int = Field(description="Power level (1-10)")
    mastery_level: str = Field(description="Required mastery: beginner, intermediate, advanced, master")

    # Costs and limitations
    energy_cost: str = Field(default="", description="Energy/stamina cost")
    cooldown: str = Field(default="", description="Cooldown time if any")
    conditions: list[str] = Field(default_factory=list, description="Conditions to use")

    # Effects
    primary_effect: str = Field(description="Primary effect description")
    secondary_effects: list[str] = Field(default_factory=list, description="Additional effects")
    side_effects: list[str] = Field(default_factory=list, description="Unintended consequences")

    # Countermeasures
    countermeasures: list[str] = Field(
        default_factory=list,
        description="How to defend against or counter this technique"
    )

    # Visual/auditory manifestations
    manifestation: str = Field(default="", description="How it appears when used")


class PowerConflict(BaseModel):
    """Conflict or competition centered around a power system."""

    name: str = Field(description="Conflict name")
    description: str = Field(description="What the conflict is about")

    parties_involved: list[str] = Field(
        description="Factions, organizations, or individuals involved"
    )

    cause: str = Field(description="Root cause of the conflict")
    current_status: str = Field(
        description="Status: brewing, active, frozen, resolved"
    )

    key_battles: list[dict] = Field(default_factory=list, description="Major confrontations")

    stakes: str = Field(description="What's at stake in this conflict")

    potential_resolution: list[str] = Field(
        default_factory=list,
        description="Possible ways to resolve"
    )


class SocialStructure(BaseModel):
    """Social structure and faction distribution."""

    classes: list[dict] = Field(
        default_factory=list,
        description="Social classes and their descriptions"
    )
    factions: list[dict] = Field(
        default_factory=list,
        description="Major factions and organizations"
    )
    power_distribution: dict = Field(
        default_factory=dict,
        description="How power is distributed in society"
    )
