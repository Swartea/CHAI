"""Subplot and foreshadowing design models for comprehensive story crafting."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SubplotType(str, Enum):
    """Types of subplots."""
    ROMANTIC = "romantic"
    FRIENDSHIP = "friendship"
    FAMILY = "family"
    RIVALRY = "rivalry"
    REVENGE = "revenge"
    REDEMPTION = "redemption"
    MYSTERY = "mystery"
    ACTION = "action"
    COMEDY = "comedy"
    TRAGEDY = "tragedy"
    GROWTH = "growth"
    CONSPIRACY = "conspiracy"
    SACRIFICE = "sacrifice"
    BETRAYAL = "betrayal"
    REUNION = "reunion"


class SubplotStatus(str, Enum):
    """Status of a subplot."""
    CONCEPT = "concept"
    PLANNED = "planned"
    ACTIVE = "active"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"


class SubplotImportance(str, Enum):
    """Importance level of a subplot."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class SubplotConnection(str, Enum):
    """How subplot connects to main story."""
    INDEPENDENT = "independent"
    PARALLEL = "parallel"
    CAUSAL = "causal"
    CONTRASTING = "contrasting"
    THEMATIC = "thematic"


class ForeshadowingTechnique(str, Enum):
    """Techniques for planting foreshadowing."""
    # Explicit techniques
    DIRECT_HINT = "direct_hint"
    PROPHECY = "prophecy"
    WARNING = "warning"
    RECURRING_SYMBOL = "recurring_symbol"

    # Implicit techniques
    CHEKHOVS_GUN = "chekhovs_gun"
    DRAMATIC_IRONY = "dramatic_irony"
    PLANT_AND_PAYOFF = "plant_and_payoff"
    CROSSED_CHEKS = "crossed_cheks"

    # Subtle techniques
    ATMOSPHERIC_HINT = "atmospheric_hint"
    CHARACTER_REACTION = "character_reaction"
    INCIDENTAL_DETAIL = "incidental_detail"
    NAMING_PATTERN = "naming_pattern"

    # Symbolic techniques
    SYMBOLIC = "symbolic"
    OBJECT_SYMBOL = "object_symbol"
    COLOR_SYMBOL = "color_symbol"
    ANIMAL_SYMBOL = "animal_symbol"
    NATURE_SYMBOL = "nature_symbol"


class ForeshadowingStrength(str, Enum):
    """Strength of foreshadowing connection."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    DEFINITIVE = "definitive"


class ForeshadowingPattern(str, Enum):
    """Common foreshadowing patterns."""
    # Temporal patterns
    EARLY_PLANT_LATE_PAYOFF = "early_plant_late_payoff"
    MULTI_STAGE_REVEAL = "multi_stage_reveal"
    CIRCULAR_RETURN = "circular_return"

    # Structural patterns
    PARALLEL_STRUCTURE = "parallel_structure"
    MIRROR_SCENES = "mirror_scenes"
    PROPHETIC_DREAM = "prophetic_dream"

    # Character patterns
    TRAIT_FOREShadow = "trait_foreshadow"
    SKILL_PREVIEW = "skill_preview"
    RELATIONSHIP_SEEDING = "relationship_seeding"

    # Mystery patterns
    CLUE_AND_RED_HERRING = "clue_and_red_herring"
    FALSE_SOLUTION = "false_solution"
    REVELATION_CHAIN = "revelation_chain"


class ForeshadowingPlanting(BaseModel):
    """Detailed information about how foreshadowing is planted."""

    technique: ForeshadowingTechnique = Field(
        description="The technique used to plant"
    )
    chapter: int = Field(description="Chapter where planted")
    scene_location: str = Field(
        default="", description="Specific scene location"
    )
    presentation_method: str = Field(
        default="", description="How it appears in text"
    )
    supporting_context: str = Field(
        default="", description="Surrounding context that hints"
    )
    subtlety_level: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="How subtle (0=obvious, 1=hidden)"
    )
    reinforcement_chapters: list[int] = Field(
        default_factory=list,
        description="Chapters that reinforce the foreshadowing"
    )


class ForeshadowingPayoff(BaseModel):
    """Detailed information about how foreshadowing pays off."""

    chapter: int = Field(
        default=0, description="Chapter of payoff"
    )
    payoff_type: str = Field(
        default="", description="Type of payoff (revelation, consequence, etc.)"
    )
    payoff_method: str = Field(
        default="", description="How the payoff is delivered"
    )
    emotional_impact: str = Field(
        default="", description="Emotional effect on reader"
    )
    connection_strength: ForeshadowingStrength = Field(
        default=ForeshadowingStrength.MODERATE,
        description="How clearly it connects to plant"
    )
    reader_awareness: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Whether readers typically notice"
    )


class SubplotChapterBeat(BaseModel):
    """A beat/event in a subplot within a chapter."""

    chapter: int = Field(description="Chapter number")
    beat_description: str = Field(
        default="", description="What happens in this chapter"
    )
    character_states: dict = Field(
        default_factory=dict,
        description="Character emotional states"
    )
    relationship_changes: dict = Field(
        default_factory=dict,
        description="How relationships shift"
    )
    tension_level: str = Field(
        default="moderate", description="low/moderate/high/climax"
    )
    subplot_progress: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Progress toward subplot resolution"
    )


class SubplotArc(BaseModel):
    """The complete arc of a subplot."""

    id: str = Field(description="Unique subplot arc ID")
    name: str = Field(description="Subplot name")
    subplot_type: SubplotType = Field(description="Type of subplot")

    # Characters involved
    primary_characters: list[str] = Field(
        default_factory=list,
        description="Main characters in this subplot"
    )
    secondary_characters: list[str] = Field(
        default_factory=list,
        description="Supporting characters"
    )

    # Arc structure
    introduction: str = Field(
        default="", description="How subplot is introduced"
    )
    rising_action: list[str] = Field(
        default_factory=list,
        description="Key events in rising action"
    )
    climax: str = Field(
        default="", description="Subplot climax event"
    )
    falling_action: list[str] = Field(
        default_factory=list,
        description="Key events in falling action"
    )
    resolution: str = Field(
        default="", description="How subplot resolves"
    )

    # Chapter beats
    chapter_beats: list[SubplotChapterBeat] = Field(
        default_factory=list,
        description="Subplot events per chapter"
    )

    # Thematic connection
    thematic_connection: str = Field(
        default="", description="Connection to main theme"
    )
    emotional_tone: str = Field(
        default="", description="Emotional quality of subplot"
    )


class Subplot(BaseModel):
    """A subplot in the story."""

    id: str = Field(description="Unique subplot ID")
    name: str = Field(description="Subplot name")
    subplot_type: SubplotType = Field(description="Type of subplot")

    # Scope
    importance: SubplotImportance = Field(
        default=SubplotImportance.MODERATE,
        description="Importance level"
    )
    estimated_word_count: int = Field(
        default=5000, description="Estimated words devoted"
    )

    # Timing
    start_chapter: int = Field(
        default=1, description="Starting chapter"
    )
    end_chapter: int = Field(
        default=24, description="Ending chapter"
    )
    peak_chapter: Optional[int] = Field(
        default=None, description="Chapter of subplot climax"
    )

    # Characters
    involved_characters: list[str] = Field(
        default_factory=list,
        description="Character IDs involved"
    )
    primary_conflict: str = Field(
        default="", description="Main conflict in subplot"
    )

    # Story integration
    connection_to_main: SubplotConnection = Field(
        default=SubplotConnection.PARALLEL,
        description="How it connects to main story"
    )
    main_story_dependency: str = Field(
        default="", description="Dependency on main story beats"
    )

    # Arc
    arc: Optional[SubplotArc] = Field(
        default=None,
        description="Subplot arc details"
    )

    # Status
    status: SubplotStatus = Field(
        default=SubplotStatus.CONCEPT,
        description="Current status"
    )

    # Foreshadowing links
    foreshadowing_elements: list[str] = Field(
        default_factory=list,
        description="Foreshadowing element IDs related"
    )

    # Quality metrics
    coherence_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Internal consistency score"
    )
    reader_satisfaction: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Expected reader satisfaction"
    )


class ForeshadowingElementDetail(BaseModel):
    """Detailed foreshadowing element with full tracking."""

    id: str = Field(description="Unique foreshadowing ID")
    name: str = Field(description="Descriptive name")
    element: str = Field(
        default="", description="The foreshadowing element itself"
    )

    # Type classification
    foreshadowing_type: ForeshadowingTechnique = Field(
        description="Technique used"
    )
    pattern_type: Optional[ForeshadowingPattern] = Field(
        default=None, description="Pattern if applicable"
    )

    # Planting information
    planting: ForeshadowingPlanting = Field(
        description="How and where planted"
    )

    # Payoff information
    payoff: ForeshadowingPayoff = Field(
        description="How and when it pays off"
    )

    # What it foreshadows
    foreshadows: str = Field(
        default="", description="What event/revelation it foreshadows"
    )
    related_characters: list[str] = Field(
        default_factory=list,
        description="Characters connected"
    )
    thematic_significance: str = Field(
        default="", description="Thematic importance"
    )

    # Linked subplot
    linked_subplot_id: Optional[str] = Field(
        default=None, description="Associated subplot if any"
    )

    # Status
    is_planted: bool = Field(
        default=False, description="Whether planted in text"
    )
    is_paid_off: bool = Field(
        default=False, description="Whether paid off"
    )


class SubplotForeshadowingSystem(BaseModel):
    """Complete system for managing subplots and foreshadowing."""

    id: str = Field(description="System ID")
    story_id: str = Field(description="Associated story ID")

    # Subplots
    subplots: list[Subplot] = Field(
        default_factory=list,
        description="All subplots in story"
    )

    # Foreshadowing
    foreshadowing_elements: list[ForeshadowingElementDetail] = Field(
        default_factory=list,
        description="All foreshadowing elements"
    )

    # Distribution metrics
    subplot_distribution: dict = Field(
        default_factory=dict,
        description="Subplot chapters by type"
    )
    foreshadowing_density: dict = Field(
        default_factory=dict,
        description="Foreshadowing per chapter"
    )

    # Quality tracking
    overall_coherence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Overall subplot-foreshadow coherence"
    )
    payoff_ratio: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Ratio of planted to paid off"
    )


class SubplotAnalysis(BaseModel):
    """Analysis of subplot quality and integration."""

    subplot_id: str = Field(description="Subplot ID")

    # Integration analysis
    main_story_integration: dict = Field(
        default_factory=dict,
        description="How well integrated with main story"
    )
    pacing_impact: dict = Field(
        default_factory=dict,
        description="Impact on story pacing"
    )

    # Character analysis
    character_development: dict = Field(
        default_factory=dict,
        description="Character growth through subplot"
    )
    relationship_evolution: list[dict] = Field(
        default_factory=list,
        description="How relationships develop"
    )

    # Balance metrics
    screen_time_ratio: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of story devoted"
    )
    reader_engagement: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Expected engagement level"
    )

    # Issues
    potential_conflicts: list[str] = Field(
        default_factory=list,
        description="Potential conflicts with other elements"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )


class ForeshadowingAnalysis(BaseModel):
    """Analysis of foreshadowing system."""

    # Coverage analysis
    coverage_by_chapter: dict = Field(
        default_factory=dict,
        description="Foreshadowing coverage per chapter"
    )
    coverage_gaps: list[int] = Field(
        default_factory=list,
        description="Chapters lacking foreshadowing"
    )

    # Pattern analysis
    pattern_distribution: dict = Field(
        default_factory=dict,
        description="Distribution of foreshadowing patterns"
    )
    effectiveness_scores: dict = Field(
        default_factory=dict,
        description="Effectiveness by pattern type"
    )

    # Payoff analysis
    payoff_timing: dict = Field(
        default_factory=dict,
        description="Timing analysis of payoffs"
    )
    delayed_payoffs: list[str] = Field(
        default_factory=list,
        description="Payoffs that waited too long"
    )
    rushed_payoffs: list[str] = Field(
        default_factory=list,
        description="Payoffs that were too quick"
    )

    # Connection analysis
    subplot_connections: dict = Field(
        default_factory=dict,
        description="Links between foreshadowing and subplots"
    )
    orphaned_elements: list[str] = Field(
        default_factory=list,
        description="Foreshadowing without clear payoff"
    )

    # Quality metrics
    overall_balance: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Overall foreshadowing balance"
    )
    reader_experience: dict = Field(
        default_factory=dict,
        description="Reader experience metrics"
    )


class SubplotForeshadowingDesign(BaseModel):
    """Complete design document for subplots and foreshadowing."""

    id: str = Field(description="Design document ID")
    story_id: str = Field(description="Associated story ID")
    title: str = Field(description="Design title")

    # Design components
    system: SubplotForeshadowingSystem = Field(
        description="The complete system"
    )

    # Analyses
    subplot_analyses: list[SubplotAnalysis] = Field(
        default_factory=list,
        description="Analysis of each subplot"
    )
    foreshadowing_analysis: ForeshadowingAnalysis = Field(
        description="Overall foreshadowing analysis"
    )

    # Integration points
    main_story_beats: list[str] = Field(
        default_factory=list,
        description="Main story beats affected"
    )
    character_arcs: list[str] = Field(
        default_factory=list,
        description="Character arcs engaged"
    )

    # Summary
    design_summary: str = Field(
        default="", description="Human-readable summary"
    )
    key_subplots: list[str] = Field(
        default_factory=list,
        description="Key subplot IDs for priority"
    )
    key_foreshadowing: list[str] = Field(
        default_factory=list,
        description="Key foreshadowing IDs"
    )

    # Metadata
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Last update timestamp"
    )
