"""Chapter body generation models for generating full chapter text from outline."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ChapterBodyStatus(str, Enum):
    """Status of chapter body generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    REVISED = "revised"
    FAILED = "failed"


class ChapterBodySectionType(str, Enum):
    """Type of section within chapter body."""
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    ACTION = "action"
    REFLECTION = "reflection"
    DESCRIPTION = "description"
    TRANSITION = "transition"


class ChapterBodySection(BaseModel):
    """A section within the chapter body."""

    id: str = Field(description="Unique section ID")
    order: int = Field(description="Order within chapter")
    section_type: ChapterBodySectionType = Field(
        default=ChapterBodySectionType.NARRATIVE,
        description="Type of section"
    )

    # Content
    content: str = Field(default="", description="Generated section content")
    word_count: int = Field(default=0, description="Word count")

    # Purpose
    purpose: str = Field(default="", description="Section purpose")
    key_events: list[str] = Field(default_factory=list, description="Key events in this section")

    # Characters
    characters_involved: list[str] = Field(
        default_factory=list,
        description="Character IDs in this section"
    )

    # Setting
    location: str = Field(default="", description="Scene location")
    time_period: str = Field(default="", description="Time period")

    # Narrative
    pov_character: Optional[str] = Field(default=None, description="POV character")
    tension_level: str = Field(default="moderate", description="Tension: low/moderate/high/climax")
    mood: str = Field(default="", description="Mood/tone")

    # Integration
    plot_point_ids: list[str] = Field(default_factory=list, description="Plot points advanced")
    subplot_ids: list[str] = Field(default_factory=list, description="Subplots advanced")
    foreshadowing_planted: list[str] = Field(default_factory=list, description="Foreshadowing planted")
    foreshadowing_paid_off: list[str] = Field(default_factory=list, description="Foreshadowing paid off")


class ChapterBody(BaseModel):
    """Full chapter body content with sections."""

    id: str = Field(description="Unique chapter body ID")
    chapter_number: int = Field(description="Chapter number")

    # Metadata
    title: str = Field(description="Chapter title")
    chapter_type: str = Field(default="normal", description="Chapter type")

    # Full content
    content: str = Field(default="", description="Full combined chapter content")

    # Sections
    sections: list[ChapterBodySection] = Field(
        default_factory=list,
        description="Chapter sections"
    )

    # Word count
    word_count: int = Field(default=0, description="Total word count")
    meets_target: bool = Field(default=False, description="Meets word count target")

    # Quality
    coherence_score: float = Field(default=0.0, description="Coherence score (0-1)")
    pacing_score: float = Field(default=0.0, description="Pacing score (0-1)")
    character_voice_score: float = Field(default=0.0, description="Character voice score (0-1)")

    # Flags
    has_plot_advancement: bool = Field(default=False, description="Has plot advancement")
    has_character_development: bool = Field(default=False, description="Has character development")
    foreshadowing_properly_planted: bool = Field(default=False, description="Foreshadowing properly placed")

    # Status
    status: ChapterBodyStatus = Field(
        default=ChapterBodyStatus.PENDING,
        description="Generation status"
    )

    # Integration
    synopsis_id: Optional[str] = Field(default=None, description="Associated synopsis ID")
    climax_design_id: Optional[str] = Field(default=None, description="Climax design ID if applicable")


class ManuscriptStatus(str, Enum):
    """Status of the full manuscript generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CHAPTERS_COMPLETE = "chapters_complete"
    COMPLETE = "complete"
    FAILED = "failed"


class ChapterGenerationProgress(BaseModel):
    """Progress tracking for a single chapter generation."""

    chapter_number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")
    status: ChapterBodyStatus = Field(default=ChapterBodyStatus.PENDING)
    word_count: int = Field(default=0)
    started_at: Optional[str] = Field(default=None, description="ISO timestamp")
    completed_at: Optional[str] = Field(default=None, description="ISO timestamp")
    error_message: Optional[str] = Field(default=None, description="Error if failed")
    retry_count: int = Field(default=0, description="Number of retries")


class ManuscriptBody(BaseModel):
    """Full manuscript with all chapter bodies."""

    id: str = Field(description="Unique manuscript ID")

    # Novel metadata
    title: str = Field(description="Novel title")
    genre: str = Field(default="", description="Genre")

    # Chapters
    chapters: list[ChapterBody] = Field(
        default_factory=list,
        description="All chapter bodies"
    )

    # Progress
    progress: list[ChapterGenerationProgress] = Field(
        default_factory=list,
        description="Generation progress per chapter"
    )

    # Status
    status: ManuscriptStatus = Field(
        default=ManuscriptStatus.PENDING,
        description="Overall manuscript status"
    )

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters")
    completed_chapters: int = Field(default=0, description="Completed chapters")
    total_word_count: int = Field(default=0, description="Total word count")

    # Quality
    average_coherence: float = Field(default=0.0, description="Average coherence score")
    average_pacing: float = Field(default=0.0, description="Average pacing score")
    foreshadowing_coverage: float = Field(default=0.0, description="Foreshadowing coverage ratio")


class ManuscriptGenerationRequest(BaseModel):
    """Request for manuscript generation."""

    # Story outline reference
    story_outline_id: Optional[str] = Field(default=None, description="Story outline ID")

    # Chapter synopses
    chapter_synopses: list[dict] = Field(
        default_factory=list,
        description="Chapter synopsis data"
    )

    # Design references
    subplot_design_id: Optional[str] = Field(default=None, description="Subplot design ID")
    climax_ending_system_id: Optional[str] = Field(default=None, description="Climax/ending system ID")

    # Context
    world_setting: Optional[dict] = Field(default=None, description="World setting data")
    characters: list[dict] = Field(default_factory=list, description="Character data")

    # Generation settings
    start_chapter: int = Field(default=1, description="Starting chapter number")
    end_chapter: Optional[int] = Field(default=None, description="Ending chapter number")
    parallel_generation: bool = Field(default=False, description="Generate chapters in parallel")

    # Quality settings
    revision_pass: bool = Field(default=True, description="Run revision pass")
    style_check: bool = Field(default=True, description="Run style check")


class ManuscriptGenerationResult(BaseModel):
    """Result of manuscript generation."""

    # Success
    success: bool = Field(description="Whether generation succeeded")

    # Manuscript
    manuscript: Optional[ManuscriptBody] = Field(
        default=None,
        description="Generated manuscript"
    )

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters generated")
    total_word_count: int = Field(default=0, description="Total word count")
    generation_time_seconds: float = Field(default=0.0, description="Generation time")

    # Failed chapters
    failed_chapters: list[dict] = Field(
        default_factory=list,
        description="Failed chapter information"
    )

    # Quality metrics
    average_coherence: float = Field(default=0.0, description="Average coherence score")
    average_pacing: float = Field(default=0.0, description="Average pacing score")

    # Error
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class ChapterBodyAnalysis(BaseModel):
    """Analysis of chapter body quality."""

    chapter_id: str = Field(description="Chapter body ID")

    # Structural analysis
    structure_score: float = Field(default=0.0, description="Structure score (0-1)")
    has_clear_opening: bool = Field(default=False, description="Has clear opening")
    has_climax: bool = Field(default=False, description="Has climax point")
    has_satisfying_resolution: bool = Field(default=False, description="Has satisfying resolution")

    # Pacing analysis
    pacing_score: float = Field(default=0.0, description="Pacing score (0-1)")
    pacing_issues: list[str] = Field(default_factory=list, description="Pacing issues")

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
    foreshadowing_planted_count: int = Field(default=0, description="Foreshadowing planted")
    foreshadowing_payoff_count: int = Field(default=0, description="Foreshadowing paid off")
    foreshadowing_balance: float = Field(default=0.0, description="Balance of planting vs payoff")

    # Word count analysis
    word_count_ratio: float = Field(default=0.0, description="Actual vs target ratio")
    section_word_distribution: dict = Field(
        default_factory=dict,
        description="Word count distribution across sections"
    )

    # Overall
    overall_quality_score: float = Field(
        default=0.0,
        description="Overall quality score (0-1)"
    )
    readability_score: float = Field(
        default=0.0,
        description="Readability score (0-1)"
    )

    # Issues
    critical_issues: list[str] = Field(
        default_factory=list,
        description="Critical issues"
    )
    minor_issues: list[str] = Field(
        default_factory=list,
        description="Minor issues"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations"
    )
