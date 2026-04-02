"""Data models for book deconstruction results.

Stores extracted templates and patterns from deconstructed popular books:
- Character templates
- Plot patterns
- World setting templates
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CharacterTemplateType(str, Enum):
    """Type of character template."""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MENTOR = "mentor"
    LOVE_INTEREST = "love_interest"
    SIDEKICK = "sidekick"


class PlotPatternType(str, Enum):
    """Type of plot pattern."""
    HEROS_JOURNEY = "heros_journey"
    THREE_ACT = "three_act"
    SAVE_THE_CAT = "save_the_cat"
    SEVEN_POINT = "seven_point"
    MYTHIC = "mythic"
    SUBVERSION = "subversion"


class WorldTemplateType(str, Enum):
    """Type of world template."""
    FANTASY = "fantasy"
    SCIFI = "sci-fi"
    URBAN = "urban"
    HISTORICAL = "historical"
    MODERN = "modern"
    POST_APOCALYPTIC = "post_apocalyptic"


class DeconstructSource(BaseModel):
    """Source book information for deconstruction."""
    book_id: str = Field(description="Original book ID from platform")
    book_title: str = Field(description="Original book title")
    author: str = Field(description="Book author")
    platform: str = Field(default="fanqie", description="Source platform")
    url: str = Field(default="", description="Book URL")


class CharacterTemplate(BaseModel):
    """Extracted character template from book deconstruction."""
    id: str = Field(description="Unique template ID")
    name: str = Field(description="Template name (e.g., '草根逆袭型男主')")

    template_type: CharacterTemplateType = Field(description="Character role type")
    genre: str = Field(description="Applicable genre")
    source: DeconstructSource = Field(description="Source book info")

    # Template attributes
    age_range: str = Field(default="", description="Typical age range")
    background_template: str = Field(
        default="",
        description="Background story template"
    )
    personality_traits: list[str] = Field(
        default_factory=list,
        description="Key personality traits"
    )
    strengths: list[str] = Field(default_factory=list, description="Typical strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Typical weaknesses")
    speech_pattern: str = Field(default="", description="Speech pattern description")
    growth_arc_template: str = Field(
        default="",
        description="Character growth arc template"
    )
    relationship_patterns: list[str] = Field(
        default_factory=list,
        description="Typical relationship patterns with other characters"
    )

    # Usage frequency
    usage_count: int = Field(default=0, description="Times this template was used")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PlotPattern(BaseModel):
    """Extracted plot pattern from book deconstruction."""
    id: str = Field(description="Unique pattern ID")
    name: str = Field(description="Pattern name (e.g., '逆境崛起')")

    pattern_type: PlotPatternType = Field(description="Plot structure type")
    genre: str = Field(description="Applicable genre")
    source: DeconstructSource = Field(description="Source book info")

    # Pattern description
    description: str = Field(default="", description="Pattern description")
    structure_summary: str = Field(
        default="",
        description="High-level structure summary"
    )
    key_beat_templates: list[str] = Field(
        default_factory=list,
        description="Key plot beat templates"
    )
    pacing_notes: str = Field(default="", description="Pacing characteristics")
    tension_curve: list[str] = Field(
        default_factory=list,
        description="Tension progression notes"
    )

    # Template variations
    variations: list[str] = Field(
        default_factory=list,
        description="Common variations of this pattern"
    )

    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class WorldTemplate(BaseModel):
    """Extracted world setting template from book deconstruction."""
    id: str = Field(description="Unique template ID")
    name: str = Field(description="Template name (e.g., '修仙世界观')")

    template_type: WorldTemplateType = Field(description="World type")
    genre: str = Field(description="Applicable genre")
    source: DeconstructSource = Field(description="Source book info")

    # Template attributes
    world_summary: str = Field(default="", description="World overview")
    geography_template: dict = Field(
        default_factory=dict,
        description="Geography setting template"
    )
    political_template: dict = Field(
        default_factory=dict,
        description="Political structure template"
    )
    cultural_template: dict = Field(
        default_factory=dict,
        description="Cultural elements template"
    )
    magic_system_template: Optional[dict] = Field(
        default=None,
        description="Magic/tech system template"
    )
    social_structure_template: Optional[dict] = Field(
        default=None,
        description="Social structure template"
    )

    # Recurring elements
    recurring_locations: list[str] = Field(
        default_factory=list,
        description="Typical locations in this world type"
    )
    typical_conflicts: list[str] = Field(
        default_factory=list,
        description="Typical world conflicts"
    )

    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DeconstructionResult(BaseModel):
    """Complete result of deconstructing a book."""
    id: str = Field(description="Unique result ID")
    source: DeconstructSource

    # Extracted templates
    character_templates: list[CharacterTemplate] = Field(
        default_factory=list,
        description="Extracted character templates"
    )
    plot_patterns: list[PlotPattern] = Field(
        default_factory=list,
        description="Extracted plot patterns"
    )
    world_template: Optional[WorldTemplate] = Field(
        default=None,
        description="Extracted world template"
    )

    # Overall analysis
    genre_classification: str = Field(default="", description="Genre classification")
    tone_and_style: str = Field(default="", description="Tone and writing style notes")
    target_audience: str = Field(default="", description="Target audience")
    word_count_range: tuple[int, int] = Field(
        default=(0, 0),
        description="Typical word count range (min, max)"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="pending", description="Status: pending, completed, failed")


class BookDeconstructTemplate(BaseModel):
    """Template used to prompt AI to deconstruct a book.

    Contains the prompt templates and extraction instructions.
    """
    name: str = Field(description="Template name")
    genre: str = Field(description="Genre this template is for")
    version: str = Field(default="1.0")

    # System prompt for deconstruction
    system_prompt: str = Field(
        default="",
        description="System prompt for deconstruction AI"
    )

    # Book info extraction prompt
    book_info_prompt: str = Field(
        default="",
        description="Prompt for extracting basic book information"
    )

    # Character extraction prompt
    character_extraction_prompt: str = Field(
        default="",
        description="Prompt for extracting character templates"
    )

    # Plot pattern extraction prompt
    plot_extraction_prompt: str = Field(
        default="",
        description="Prompt for extracting plot patterns"
    )

    # World setting extraction prompt
    world_extraction_prompt: str = Field(
        default="",
        description="Prompt for extracting world setting templates"
    )

    # Overall analysis prompt
    analysis_prompt: str = Field(
        default="",
        description="Prompt for overall genre/style analysis"
    )
