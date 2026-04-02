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
    """Magic, technology, or superpower system rules."""

    name: str = Field(description="System name")
    system_type: str = Field(description="Type: magic, technology, superpower, mixed")

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
