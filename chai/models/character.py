"""Character models for novel characters."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CharacterRole(str, Enum):
    """Character role types."""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


class CharacterRelationship(BaseModel):
    """Relationship between two characters."""

    character_id: str = Field(description="Related character ID")
    relationship_type: str = Field(description="Type: family, friend, enemy, lover, mentor, etc.")
    description: str = Field(description="Relationship description")
    dynamics: str = Field(description="Interaction dynamics")


class Character(BaseModel):
    """Character model with full attributes."""

    id: str = Field(description="Unique character identifier")
    name: str = Field(description="Character name")

    role: CharacterRole = Field(description="Character role in story")

    # Appearance
    age: Optional[str] = Field(default=None, description="Age description")
    appearance: dict = Field(
        default_factory=dict,
        description="Physical appearance details"
    )

    # Personality
    personality: dict = Field(
        default_factory=dict,
        description="Personality traits and MBTI if applicable"
    )
    strengths: list[str] = Field(default_factory=list, description="Character strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Character weaknesses")

    # Background
    backstory: str = Field(default="", description="Character backstory")
    motivation: str = Field(default="", description="Character motivation")
    goal: str = Field(default="", description="Character's main goal")

    # Relationships
    relationships: list[CharacterRelationship] = Field(
        default_factory=list,
        description="Character relationships"
    )

    # Character arc
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
