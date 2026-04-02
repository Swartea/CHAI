"""Chapter synopsis and plot point models for detailed story planning."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SynopsisPlotPointType(str, Enum):
    """Types of plot points in a chapter synopsis."""
    # Major turning points
    TURNING_POINT = "turning_point"
    CLIMAX = "climax"
    SUB_CLIMAX = "sub_climax"

    # Key events
    KEY_EVENT = "key_event"
    INCITING_INCIDENT = "inciting_incident"
    CRISIS = "crisis"
    REVELATION = "revelation"
    DECISION_POINT = "decision_point"

    # Complications
    COMPLICATION = "complication"
    OBSTACLE = "obstacle"
    BETRAYAL = "betrayal"
    SETBACK = "setback"

    # Character moments
    CHARACTER_MOMENT = "character_moment"
    GROWTH_MOMENT = "growth_moment"
    RELATIONSHIP_SHIFT = "relationship_shift"

    # Plot advancement
    PLOT_ADVANCEMENT = "plot_advancement"
    SUBPLOT_INTEGRATION = "subplot_integration"
    FORESHADOW_PAYOFF = "foreshadow_payoff"

    # Structure markers
    STRUCTURE_MARKER = "structure_marker"
    TRANSITION = "transition"
    BRIDGE = "bridge"


class SynopsisPlotPointStatus(str, Enum):
    """Status of a synopsis plot point."""
    PENDING = "pending"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    REVISED = "revised"


class PlotPointImportance(str, Enum):
    """Importance level of a plot point."""
    ESSENTIAL = "essential"
    IMPORTANT = "important"
    NOTABLE = "notable"
    MINOR = "minor"


class SynopsisPlotPoint(BaseModel):
    """A single plot point in the chapter synopsis."""

    id: str = Field(description="Unique plot point ID")
    name: str = Field(description="Plot point name")
    plot_point_type: SynopsisPlotPointType = Field(description="Type of plot point")

    # Description
    description: str = Field(description="What happens at this plot point")
    significance: str = Field(
        default="", description="Why this plot point matters"
    )

    # Chapter placement
    chapter: int = Field(description="Primary chapter number")
    scene_hint: Optional[str] = Field(
        default=None, description="Which scene (e.g., 'scene_2')"
    )

    # Importance and status
    importance: PlotPointImportance = Field(
        default=PlotPointImportance.IMPORTANT, description="Importance level"
    )
    status: SynopsisPlotPointStatus = Field(
        default=SynopsisPlotPointStatus.PENDING, description="Current status"
    )

    # Story structure integration
    story_beat_id: Optional[str] = Field(
        default=None, description="Associated story beat ID"
    )
    act_number: Optional[int] = Field(
        default=None, description="Act number this belongs to"
    )

    # Character involvement
    character_ids: list[str] = Field(
        default_factory=list, description="Character IDs involved"
    )
    protagonist_involved: bool = Field(
        default=False, description="Is protagonist directly involved"
    )

    # Plot thread connection
    plot_thread_ids: list[str] = Field(
        default_factory=list, description="Plot thread IDs this advances"
    )
    main_conflict_advancement: bool = Field(
        default=False, description="Does this advance the main conflict"
    )

    # Emotional impact
    emotional_impact: str = Field(
        default="", description="Emotional impact description"
    )
    tension_level: str = Field(
        default="moderate", description="Tension level: low/moderate/high/climax"
    )

    # Foreshadowing
    foreshadowing_id: Optional[str] = Field(
        default=None, description="Foreshadowing ID if this is a payoff"
    )
    plants_foreshadowing: bool = Field(
        default=False, description="Does this plant foreshadowing"
    )

    # Consequences
    consequences: list[str] = Field(
        default_factory=list, description="Immediate consequences"
    )
    setups: list[str] = Field(
        default_factory=list, description="What this sets up"
    )

    # POV
    pov_character: Optional[str] = Field(
        default=None, description="POV character for this plot point"
    )


class ChapterSynopsisSection(BaseModel):
    """A section within a chapter synopsis."""

    id: str = Field(description="Unique section ID")
    name: str = Field(description="Section name (opening, development, etc.)")
    order: int = Field(description="Order within the chapter")

    # Content
    synopsis_text: str = Field(description="Synopsis text for this section")
    key_events: list[str] = Field(
        default_factory=list, description="Key events in this section"
    )
    character_actions: list[str] = Field(
        default_factory=list, description="Key character actions"
    )

    # Scene info
    location: Optional[str] = Field(
        default=None, description="Scene location"
    )
    time_period: Optional[str] = Field(
        default=None, description="Time period"
    )

    # Emotional tone
    mood: str = Field(default="", description="Mood/tone of this section")
    tension_level: str = Field(
        default="moderate", description="Tension level"
    )


class ChapterSynopsis(BaseModel):
    """Detailed synopsis for a single chapter."""

    id: str = Field(description="Unique synopsis ID")
    chapter_number: int = Field(description="Chapter number")

    # Basic info
    title: str = Field(description="Chapter title")
    summary: str = Field(
        description="Overall chapter summary (1-2 sentences)"
    )

    # Detailed sections
    sections: list[ChapterSynopsisSection] = Field(
        default_factory=list, description="Chapter divided into sections"
    )

    # Full synopsis text
    detailed_synopsis: str = Field(
        default="", description="Detailed synopsis text (300-500 chars)"
    )

    # Plot points in this chapter
    plot_point_ids: list[str] = Field(
        default_factory=list, description="Plot point IDs covered"
    )

    # Characters
    pov_character: Optional[str] = Field(
        default=None, description="POV character"
    )
    characters_present: list[str] = Field(
        default_factory=list, description="Characters appearing in chapter"
    )
    new_characters: list[str] = Field(
        default_factory=list, description="New characters introduced"
    )

    # Setting
    primary_location: str = Field(
        default="", description="Primary location"
    )
    time_setting: str = Field(
        default="", description="Time setting (day 1, night, etc.)"
    )

    # Story progression
    plot_threads_advanced: list[str] = Field(
        default_factory=list, description="Plot threads advanced"
    )
    character_development: list[str] = Field(
        default_factory=list, description="Character development moments"
    )

    # Foreshadowing
    foreshadowing_planted: list[str] = Field(
        default_factory=list, description="Foreshadowing elements planted"
    )
    foreshadowing_payoffs: list[str] = Field(
        default_factory=list, description="Foreshadowing elements paid off"
    )

    # Thematic elements
    themes_explored: list[str] = Field(
        default_factory=list, description="Themes explored"
    )

    # Emotional arc
    chapter_emotional_arc: str = Field(
        default="", description="Emotional arc of the chapter"
    )

    # Pacing
    pacing_notes: str = Field(
        default="", description="Pacing notes"
    )
    word_count_target: int = Field(
        default=3000, description="Target word count"
    )

    # Status
    status: SynopsisPlotPointStatus = Field(
        default=SynopsisPlotPointStatus.PENDING, description="Synopsis status"
    )

    # Chapter type markers
    is_prologue: bool = Field(default=False, description="Is prologue chapter")
    is_epilogue: bool = Field(default=False, description="Is epilogue chapter")
    is_bridge: bool = Field(default=False, description="Is bridge/transition chapter")
    is_climax_chapter: bool = Field(default=False, description="Is climax chapter")


class PlotPointArrangement(BaseModel):
    """Arrangement of plot points across chapters."""

    id: str = Field(description="Unique arrangement ID")
    story_arc_id: Optional[str] = Field(
        default=None, description="Associated story arc/structure ID"
    )

    # All plot points
    plot_points: list[SynopsisPlotPoint] = Field(
        default_factory=list, description="All plot points"
    )

    # Chapter to plot points mapping
    chapter_to_points: dict[str, list[str]] = Field(
        default_factory=dict, description="Chapter ID to plot point IDs mapping"
    )

    # Plot thread to plot points mapping
    thread_to_points: dict[str, list[str]] = Field(
        default_factory=dict, description="Plot thread ID to plot point IDs mapping"
    )

    # Statistics
    total_chapters: int = Field(default=24, description="Total chapter count")
    plot_points_per_chapter_avg: float = Field(
        default=2.0, description="Average plot points per chapter"
    )

    # Quality metrics
    turning_point_coverage: float = Field(
        default=0.0, description="Coverage of major turning points"
    )
    subplot_balance: float = Field(
        default=0.0, description="Balance of subplot advancement"
    )


class ChapterSynopsisAnalysis(BaseModel):
    """Analysis of chapter synopsis quality and arrangement."""

    synopsis_id: str = Field(description="Synopsis or arrangement ID")

    # Coverage analysis
    chapter_coverage: float = Field(
        default=0.0, description="Percentage of chapters with synopses"
    )
    plot_point_coverage: float = Field(
        default=0.0, description="Percentage of chapters with plot points"
    )

    # Pacing analysis
    pacing_score: float = Field(
        default=0.0, description="Pacing quality score (0-1)"
    )
    tension_distribution: dict = Field(
        default_factory=dict, description="Tension distribution analysis"
    )

    # Plot thread analysis
    thread_coverage: dict = Field(
        default_factory=dict, description="Plot thread coverage"
    )
    unresolved_plotlines: list[str] = Field(
        default_factory=list, description="Unresolved plot threads"
    )

    # Character analysis
    character_screen_time: dict = Field(
        default_factory=dict, description="Character appearance distribution"
    )
    protagonist_focus_ratio: float = Field(
        default=0.0, description="Ratio of protagonist POV chapters"
    )

    # Foreshadowing analysis
    foreshadowing_balance: dict = Field(
        default_factory=dict, description="Foreshadowing balance"
    )
    orphaned_foreshadowing: list[str] = Field(
        default_factory=list, description="Foreshadowing without payoff"
    )

    # Quality scores
    coherence_score: float = Field(
        default=0.0, description="Overall coherence score (0-1)"
    )
    completeness_score: float = Field(
        default=0.0, description="Completeness score (0-1)"
    )

    # Issues
    identified_issues: list[str] = Field(
        default_factory=list, description="Identified issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )