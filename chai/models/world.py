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


class SocialClass(BaseModel):
    """A social class or stratum in society."""

    name: str = Field(description="Class name")
    description: str = Field(description="Detailed description of this class")
    typical_members: list[str] = Field(
        default_factory=list,
        description="Typical members of this class"
    )
    lifestyle: str = Field(default="", description="Typical lifestyle and living conditions")
    rights: list[str] = Field(
        default_factory=list,
        description="Rights and privileges enjoyed by this class"
    )
    obligations: list[str] = Field(
        default_factory=list,
        description="Duties and obligations of this class"
    )
    relationship_with_other_classes: list[dict] = Field(
        default_factory=list,
        description="Relationships with other classes: {'class': 'name', 'type': 'ally/rival/conflict', 'description': '...'}"
    )
    economic_base: str = Field(
        default="",
        description="Economic foundation: land ownership, trade, labor, etc."
    )
    political_influence: int = Field(
        default=0,
        description="Political influence level (0-10)"
    )
    population_percentage: str = Field(
        default="",
        description="Approximate percentage of population"
    )


class Faction(BaseModel):
    """A major faction, organization, or power group in society."""

    name: str = Field(description="Faction name")
    faction_type: str = Field(
        description="Type: royal, religious, military, mercantile, criminal, magical, political, guild, secret, etc."
    )
    description: str = Field(description="Detailed description of the faction")

    # Leadership and structure
    leader: str = Field(default="", description="Current leader or head")
    leadership_structure: str = Field(
        default="",
        description="How leadership is determined: hereditary, elected, meritocratic, etc."
    )
    internal_hierarchy: list[str] = Field(
        default_factory=list,
        description="Hierarchy levels within the faction"
    )

    # Membership
    membership: str = Field(default="", description="Size and composition of membership")
    recruitment: str = Field(
        default="",
        description="How new members are recruited"
    )
    membership_requirements: list[str] = Field(
        default_factory=list,
        description="Requirements to join"
    )

    # Goals and ideology
    goals: list[str] = Field(default_factory=list, description="Primary objectives")
    ideology: str = Field(default="", description="Core ideology or belief system")
    values: list[str] = Field(default_factory=list, description="Core values")

    # Resources and power
    resources: list[str] = Field(
        default_factory=list,
        description="Key resources controlled by the faction"
    )
    power_level: int = Field(
        default=5,
        description="Overall power level (1-10)"
    )
    military_strength: str = Field(
        default="",
        description="Military or combat capability description"
    )
    economic_power: str = Field(
        default="",
        description="Economic wealth and influence"
    )
    political_alignment: str = Field(
        default="",
        description="Political stance and alignment"
    )

    # Territory and presence
    territories: list[str] = Field(
        default_factory=list,
        description="Areas or regions controlled"
    )
    headquarters: str = Field(
        default="",
        description="Main headquarters or base location"
    )
    symbol: str = Field(default="", description="Faction emblem or symbol")

    # History
    founding_story: str = Field(
        default="",
        description="How and when the faction was founded"
    )
    founding_date: str = Field(default="", description="Approximate founding date")
    historical_events: list[dict] = Field(
        default_factory=list,
        description="Key historical events involving this faction"
    )

    # Relationships
    allies: list[str] = Field(
        default_factory=list,
        description="Faction names of allies"
    )
    rivals: list[str] = Field(
        default_factory=list,
        description="Faction names of rivals"
    )
    enemies: list[str] = Field(
        default_factory=list,
        description="Faction names of enemies"
    )

    # Notable members
    notable_members: list[dict] = Field(
        default_factory=list,
        description="Famous or important members: {'name': '...', 'role': '...', 'description': '...'}"
    )

    # Current status
    current_status: str = Field(
        default="",
        description="Current status: rising, peak, declining, dormant, destroyed"
    )
    current_goals: list[str] = Field(
        default_factory=list,
        description="Current objectives and activities"
    )


class FactionRelationship(BaseModel):
    """Relationship between two factions."""

    faction_a: str = Field(description="First faction name")
    faction_b: str = Field(description="Second faction name")
    relationship_type: str = Field(
        description="Type: alliance, rivalry, hostile, neutral, tributary, vassal, sovereign, trade_partner, secret_alliance"
    )
    description: str = Field(description="Nature of the relationship")
    history: str = Field(default="", description="How this relationship formed")
    current_status: str = Field(
        default="",
        description="Current state: stable, tense, deteriorating, improving"
    )
    key_events: list[str] = Field(
        default_factory=list,
        description="Key events that shaped the relationship"
    )


class Guild(BaseModel):
    """A guild or professional organization."""

    name: str = Field(description="Guild name")
    profession: str = Field(description="What profession or trade the guild covers")
    description: str = Field(description="Guild description")
    hierarchy: list[str] = Field(
        default_factory=list,
        description="Guild hierarchy levels"
    )
    membership_requirements: list[str] = Field(
        default_factory=list,
        description="How to join and ranks"
    )
    notable_members: list[str] = Field(
        default_factory=list,
        description="Famous guild members"
    )
    resources: list[str] = Field(
        default_factory=list,
        description="Guild resources and assets"
    )
    influence: str = Field(default="", description="Influence and reach")
    headquarters: str = Field(default="", description="Guild hall location")
    allied_factions: list[str] = Field(
        default_factory=list,
        description="Factions allied with this guild"
    )
    rival_guilds: list[str] = Field(
        default_factory=list,
        description="Competing or rival guilds"
    )


class CriminalOrganization(BaseModel):
    """A criminal syndicate or underworld organization."""

    name: str = Field(description="Organization name")
    description: str = Field(description="Description of the organization")
    organizational_structure: str = Field(
        default="",
        description="How the organization is structured"
    )
    leader: str = Field(default="", description="Leader or boss")
    territories: list[str] = Field(
        default_factory=list,
        description="Territories they control"
    )
    illegal_activities: list[str] = Field(
        default_factory=list,
        description="Types of crimes they engage in"
    )
    legitimate_businesses: list[str] = Field(
        default_factory=list,
        description="Front businesses or legitimate operations"
    )
    alliances: list[str] = Field(
        default_factory=list,
        description="Allied criminal organizations"
    )
    rival_organizations: list[str] = Field(
        default_factory=list,
        description="Rival criminal groups"
    )
    law_enforcement_relationship: str = Field(
        default="",
        description="How they interact with authorities"
    )
    influence: str = Field(
        default="",
        description="Underworld influence and reach"
    )


class ReligiousInstitution(BaseModel):
    """A religious organization or church."""

    name: str = Field(description="Institution name")
    deity_or_belief: str = Field(
        default="",
        description="Primary deity, gods, or belief system"
    )
    description: str = Field(description="Description of the religion")
    hierarchy: list[str] = Field(
        default_factory=list,
        description="Religious hierarchy"
    )
    holy_sites: list[str] = Field(
        default_factory=list,
        description="Important religious locations"
    )
    practices: list[str] = Field(
        default_factory=list,
        description="Key religious practices and rituals"
    )
    political_influence: str = Field(
        default="",
        description="Political power and influence"
    )
    factions_within: list[str] = Field(
        default_factory=list,
        description="Major internal factions or denominations"
    )
    relationship_with_state: str = Field(
        default="",
        description="Relationship with political authorities"
    )
    allied_factions: list[str] = Field(
        default_factory=list,
        description="Factions allied with this religion"
    )
    rival_religions: list[str] = Field(
        default_factory=list,
        description="Competing or opposing religions"
    )


class SecretSociety(BaseModel):
    """A secret society or hidden organization."""

    name: str = Field(description="Society name")
    description: str = Field(description="Description and purpose")
    secrecy_level: str = Field(
        default="",
        description="How secret: semi-secret, very secret, legendary"
    )
    membership: str = Field(default="", description="Membership size and type")
    hierarchy: list[str] = Field(
        default_factory=list,
        description="Internal structure and ranks"
    )
    initiation_rituals: list[str] = Field(
        default_factory=list,
        description="How members are initiated"
    )
    goals: list[str] = Field(default_factory=list, description="True goals")
    public_goals: list[str] = Field(
        default_factory=list,
        description="Publicly stated goals (may differ from true)"
    )
    headquarters: str = Field(
        default="",
        description="Hidden headquarters or meeting places"
    )
    member_identifiers: list[str] = Field(
        default_factory=list,
        description="How members identify each other"
    )
    notable_members: list[str] = Field(
        default_factory=list,
        description="Famous or known members"
    )
    allied_secret_societies: list[str] = Field(
        default_factory=list,
        description="Allied hidden organizations"
    )
    rival_secret_societies: list[str] = Field(
        default_factory=list,
        description="Competing secret societies"
    )


class SocialConflict(BaseModel):
    """A social conflict or systemic tension in society."""

    name: str = Field(description="Conflict name")
    description: str = Field(description="What the conflict is about")
    parties_involved: list[str] = Field(
        description="Classes, factions, or groups involved"
    )
    cause: str = Field(description="Root cause of the conflict")
    current_status: str = Field(
        description="Status: brewing, active, frozen, resolved, escalating"
    )
    key_battles_or_events: list[dict] = Field(
        default_factory=list,
        description="Major confrontations or events"
    )
    stakes: str = Field(description="What's at stake")
    potential_resolutions: list[str] = Field(
        default_factory=list,
        description="Possible ways to resolve"
    )
    impact_on_society: str = Field(
        default="",
        description="How this conflict affects society"
    )


class SocialStructure(BaseModel):
    """Social structure and faction distribution.

    Comprehensive social hierarchy, factions, organizations,
    conflicts, and power distribution in the world.
    """

    # Social classes
    classes: list[dict] = Field(
        default_factory=list,
        description="Social classes and their descriptions"
    )
    social_mobility: str = Field(
        default="",
        description="How easy/difficult it is to change social class"
    )
    family_structures: list[str] = Field(
        default_factory=list,
        description="Major family structure types"
    )
    wealth_distribution: str = Field(
        default="",
        description="How wealth is distributed across society"
    )

    # Factions and organizations
    factions: list[dict] = Field(
        default_factory=list,
        description="Major factions and organizations"
    )
    guilds: list[dict] = Field(
        default_factory=list,
        description="Guilds and professional organizations"
    )
    criminal_organizations: list[dict] = Field(
        default_factory=list,
        description="Criminal syndicates and underworld groups"
    )
    religious_institutions: list[dict] = Field(
        default_factory=list,
        description="Religious organizations and churches"
    )
    secret_societies: list[dict] = Field(
        default_factory=list,
        description="Secret societies and hidden organizations"
    )

    # Relationships
    faction_relationships: list[dict] = Field(
        default_factory=list,
        description="Relationships between factions"
    )

    # Power distribution
    power_distribution: dict = Field(
        default_factory=dict,
        description="How power is distributed in society"
    )
    economic_system: dict = Field(
        default_factory=dict,
        description="Economic system details"
    )

    # Social tensions
    social_conflicts: list[dict] = Field(
        default_factory=list,
        description="Major social conflicts and tensions"
    )
    conflict_lines: list[str] = Field(
        default_factory=list,
        description="Main fault lines in society"
    )

    # Cultural norms
    social_norms: list[str] = Field(
        default_factory=list,
        description="Important social norms and expectations"
    )
    taboos: list[str] = Field(
        default_factory=list,
        description="Major social taboos"
    )

    # Regional variations
    regional_variations: list[dict] = Field(
        default_factory=list,
        description="How social structure varies by region"
    )
