"""Chapter content generation models for writing detailed chapter text."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ChapterContentType(str, Enum):
    """Type of chapter content."""
    NORMAL = "normal"
    PROLOGUE = "prologue"
    EPILOGUE = "epilogue"
    BRIDGE = "bridge"
    CLIMAX = "climax"
    TRANSITION = "transition"


class ChapterContentStatus(str, Enum):
    """Status of chapter content generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    REVISED = "revised"
    REJECTED = "rejected"


class NarrativePoint(str, Enum):
    """Narrative point within a chapter."""
    OPENING = "opening"
    SETUP = "setup"
    DEVELOPMENT = "development"
    COMPLICATION = "complication"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


class DialogueStyle(str, Enum):
    """Style of dialogue."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    MIXED = "mixed"


class ChapterSectionContent(BaseModel):
    """Content for a section within a chapter."""

    id: str = Field(description="Unique section ID")
    narrative_point: NarrativePoint = Field(description="Position in narrative arc")
    order: int = Field(description="Order within chapter")

    # Content
    content: str = Field(default="", description="Generated content for this section")
    word_count: int = Field(default=0, description="Word count of this section")

    # Purpose
    purpose: str = Field(default="", description="Purpose of this section")
    key_events: list[str] = Field(default_factory=list, description="Key events")

    # Characters
    characters_present: list[str] = Field(default_factory=list, description="Character IDs")
    pov_character: Optional[str] = Field(default=None, description="POV character")

    # Setting
    location: str = Field(default="", description="Scene location")
    time_period: str = Field(default="", description="Time period")

    # Tone
    mood: str = Field(default="", description="Mood/tone")
    tension_level: str = Field(default="moderate", description="Tension: low/moderate/high/climax")

    # Foreshadowing
    foreshadowing_elements: list[str] = Field(
        default_factory=list,
        description="Foreshadowing IDs planted"
    )


class ChapterContentPlan(BaseModel):
    """Detailed plan for generating chapter content."""

    id: str = Field(description="Unique plan ID")
    chapter_synopsis_id: str = Field(description="Associated synopsis ID")
    chapter_number: int = Field(description="Chapter number")

    # Chapter metadata
    title: str = Field(description="Chapter title")
    chapter_type: ChapterContentType = Field(
        default=ChapterContentType.NORMAL,
        description="Type of chapter"
    )

    # Content structure
    sections: list[ChapterSectionContent] = Field(
        default_factory=list,
        description="Sections to generate"
    )

    # Word count targets
    target_word_count: int = Field(default=3000, description="Target word count")
    min_word_count: int = Field(default=2000, description="Minimum word count")
    max_word_count: int = Field(default=4000, description="Maximum word count")

    # POV
    pov_character: Optional[str] = Field(default=None, description="POV character")
    pov_third_person: bool = Field(
        default=True,
        description="True for third person, False for first person"
    )

    # Characters
    characters_present: list[str] = Field(
        default_factory=list,
        description="Characters appearing in chapter"
    )
    main_dialogue_character: Optional[str] = Field(
        default=None,
        description="Main dialogue/screen time character"
    )

    # Setting
    primary_location: str = Field(default="", description="Primary location")
    time_setting: str = Field(default="", description="Time setting")
    scene_transitions: list[str] = Field(
        default_factory=list,
        description="Planned scene transitions"
    )

    # Plot advancement
    plot_points_to_cover: list[str] = Field(
        default_factory=list,
        description="Plot point IDs to include"
    )
    plot_threads_to_advance: list[str] = Field(
        default_factory=list,
        description="Plot thread IDs to advance"
    )

    # Subplot integration
    subplot_ids: list[str] = Field(
        default_factory=list,
        description="Subplot IDs relevant to this chapter"
    )

    # Foreshadowing
    foreshadowing_to_plant: list[str] = Field(
        default_factory=list,
        description="Foreshadowing IDs to plant"
    )
    foreshadowing_to_payoff: list[str] = Field(
        default_factory=list,
        description="Foreshadowing IDs to payoff"
    )

    # Climax/Ending integration
    is_climax_chapter: bool = Field(default=False, description="Is this a climax chapter")
    climax_element_ids: list[str] = Field(
        default_factory=list,
        description="Climax element IDs if climax chapter"
    )

    # Emotional arc
    emotional_arc: str = Field(
        default="",
        description="Emotional arc description (e.g., hope→despair→determination)"
    )

    # Pacing
    pacing_notes: str = Field(default="", description="Pacing instructions")
    target_pacing: str = Field(
        default="moderate",
        description="Target pacing: slow/moderate/fast"
    )

    # Style
    dialogue_style: DialogueStyle = Field(
        default=DialogueStyle.MIXED,
        description="Dialogue style preference"
    )
    descriptive_density: str = Field(
        default="moderate",
        description="Descriptive density: sparse/moderate/rich"
    )

    # Status
    status: ChapterContentStatus = Field(
        default=ChapterContentStatus.PENDING,
        description="Generation status"
    )

    # Previous chapter context
    previous_chapter_summary: Optional[str] = Field(
        default=None,
        description="Summary of previous chapter for continuity"
    )


class ChapterContentDraft(BaseModel):
    """Draft of generated chapter content."""

    id: str = Field(description="Unique draft ID")
    plan_id: str = Field(description="Associated plan ID")
    chapter_number: int = Field(description="Chapter number")

    # Content
    title: str = Field(description="Chapter title")
    content: str = Field(default="", description="Full chapter content")

    # Section content
    section_contents: list[ChapterSectionContent] = Field(
        default_factory=list,
        description="Content per section"
    )

    # Word count
    word_count: int = Field(default=0, description="Actual word count")
    meets_target: bool = Field(default=False, description="Meets word count target")

    # Quality metrics
    coherence_score: float = Field(
        default=0.0,
        description="Coherence score (0-1)"
    )
    pacing_score: float = Field(
        default=0.0,
        description="Pacing score (0-1)"
    )
    character_voice_score: float = Field(
        default=0.0,
        description="Character voice consistency score (0-1)"
    )

    # Flags
    has_plot_advancement: bool = Field(
        default=False,
        description="Has meaningful plot advancement"
    )
    has_character_development: bool = Field(
        default=False,
        description="Has character development"
    )
    foreshadowing_properly_planted: bool = Field(
        default=False,
        description="Foreshadowing properly placed"
    )

    # Status
    status: ChapterContentStatus = Field(
        default=ChapterContentStatus.PENDING,
        description="Draft status"
    )

    # Revision notes
    revision_notes: list[str] = Field(
        default_factory=list,
        description="Notes for revision"
    )


class ChapterContentRevision(BaseModel):
    """Revision notes and changes for chapter content."""

    id: str = Field(description="Unique revision ID")
    draft_id: str = Field(description="Associated draft ID")

    # Revision type
    revision_type: str = Field(
        description="Type: minor/pmoderate/major"
    )

    # Issues identified
    issues: list[str] = Field(
        default_factory=list,
        description="Issues identified"
    )

    # Specific changes needed
    changes_needed: list[str] = Field(
        default_factory=list,
        description="Specific changes required"
    )

    # Affected sections
    affected_sections: list[str] = Field(
        default_factory=list,
        description="Section IDs that need changes"
    )

    # Priority
    priority: int = Field(
        default=1,
        description="Priority (1=high, 2=medium, 3=low)"
    )


class ChapterContentAnalysis(BaseModel):
    """Analysis of chapter content quality."""

    draft_id: str = Field(description="Draft ID analyzed")

    # Structural analysis
    structure_score: float = Field(
        default=0.0,
        description="Structure score (0-1)"
    )
    has_clear_opening: bool = Field(
        default=False,
        description="Has clear opening"
    )
    has_climax: bool = Field(
        default=False,
        description="Has identifiable climax"
    )
    has_satisfying_resolution: bool = Field(
        default=False,
        description="Has satisfying resolution"
    )

    # Pacing analysis
    pacing_score: float = Field(
        default=0.0,
        description="Pacing score (0-1)"
    )
    pacing_issues: list[str] = Field(
        default_factory=list,
        description="Pacing issues identified"
    )

    # Character analysis
    character_voice_consistency: dict = Field(
        default_factory=dict,
        description="Character voice consistency by character ID"
    )
    dialogue_naturalness: float = Field(
        default=0.0,
        description="Dialogue naturalness score (0-1)"
    )

    # Content analysis
    plot_advancement_quality: float = Field(
        default=0.0,
        description="Plot advancement quality (0-1)"
    )
    thematic_coherence: float = Field(
        default=0.0,
        description="Thematic coherence score (0-1)"
    )

    # Foreshadowing analysis
    foreshadowing_planted_count: int = Field(
        default=0,
        description="Number of foreshadowing elements planted"
    )
    foreshadowing_payoff_count: int = Field(
        default=0,
        description="Number of foreshadowing elements paid off"
    )
    foreshadowing_balance: float = Field(
        default=0.0,
        description="Balance of planting vs payoff (0-1)"
    )

    # Word count analysis
    word_count_ratio: float = Field(
        default=0.0,
        description="Actual vs target word count ratio"
    )
    section_word_distribution: dict = Field(
        default_factory=dict,
        description="Word count distribution across sections"
    )

    # Overall scores
    overall_quality_score: float = Field(
        default=0.0,
        description="Overall quality score (0-1)"
    )
    readability_score: float = Field(
        default=0.0,
        description="Readability score (0-1)"
    )

    # Issues and recommendations
    critical_issues: list[str] = Field(
        default_factory=list,
        description="Critical issues that must be addressed"
    )
    minor_issues: list[str] = Field(
        default_factory=list,
        description="Minor issues that could be improved"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )


class ChapterContentTemplate(BaseModel):
    """Template for chapter content generation by type."""

    id: str = Field(description="Template ID")
    name: str = Field(description="Template name")

    # Applicable chapter types
    chapter_types: list[ChapterContentType] = Field(
        default_factory=list,
        description="Chapter types this template applies to"
    )

    # Section structure
    section_structure: list[dict] = Field(
        default_factory=list,
        description="Section structure with narrative points"
    )

    # Word count distribution (percentage per section)
    word_distribution: list[float] = Field(
        default_factory=list,
        description="Word count percentage per section"
    )

    # Pacing template
    pacing_template: list[str] = Field(
        default_factory=list,
        description="Tension levels per section"
    )

    # Style guidance
    dialogue_ratio: float = Field(
        default=0.3,
        description="Target dialogue ratio (0-1)"
    )
    description_density: str = Field(
        default="moderate",
        description="Description density"
    )

    # Special requirements
    has_hook_ending: bool = Field(
        default=True,
        description="Should have hook ending"
    )
    has_scene_breaks: bool = Field(
        default=True,
        description="Should have scene breaks"
    )