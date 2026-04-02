"""Story outline models for comprehensive story planning."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StoryOutlineType(str, Enum):
    """Types of story outline structures."""
    THREE_ACT = "three_act"
    HEROS_JOURNEY = "heros_journey"
    SEVEN_POINT = "seven_point"
    SAVE_THE_CAT = "save_the_cat"
    FREYTAGS_PYRAMID = "freytags_pyramid"
    KISHOTENKETSU = "kishotenketsu"


class OutlineStatus(str, Enum):
    """Status of outline elements."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    REVISED = "revised"


class TensionLevel(str, Enum):
    """Tension/intensity levels for pacing."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CLIMAX = "climax"
    RELEASE = "release"


class ForeshadowingType(str, Enum):
    """Types of foreshadowing."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    CHARACTER_BASED = "character_based"
    ENVIRONMENTAL = "environmental"
    DIALOGUE = "dialogue"
    SYMBOLIC = "symbolic"


class ForeshadowingStatus(str, Enum):
    """Status of foreshadowing payoff."""
    PLANTED = "planted"
    DEVELOPING = "developing"
    PAYED_OFF = "payed_off"
    REPURPOSED = "repurposed"


class PlotThreadType(str, Enum):
    """Types of plot threads."""
    MAIN = "main"
    ROMANTIC = "romantic"
    CHARACTER = "character"
    SUBPLOT = "subplot"
    WORLD_BUILDING = "world_building"
    MYSTERY = "mystery"


class ScenePurpose(str, Enum):
    """Purpose of a scene in the story."""
    exposition = "exposition"
    rising_action = "rising_action"
    COMPLICATION = "complication"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    CHARACTER_DEVELOPMENT = "character_development"
    WORLD_BUILDING = "world_building"
    TRANSITION = "transition"
    RELATIONSHIP = "relationship"


class ForeshadowingElement(BaseModel):
    """A foreshadowing element planted in the story."""

    id: str = Field(description="Unique foreshadowing ID")
    element: str = Field(description="The foreshadowing element itself")
    foreshadowing_type: ForeshadowingType = Field(
        description="Type of foreshadowing technique"
    )

    # Location where it's planted
    chapter_planted: int = Field(description="Chapter where foreshadowing is planted")
    scene_location: str = Field(default="", description="Specific location in chapter")
    description: str = Field(default="", description="How the foreshadowing appears")

    # Payoff tracking
    chapter_payoff: Optional[int] = Field(
        default=None, description="Chapter where it pays off"
    )
    payoff_description: str = Field(default="", description="How the payoff occurs")

    status: ForeshadowingStatus = Field(
        default=ForeshadowingStatus.PLANTED, description="Current status"
    )

    subtlety_level: float = Field(
        default=0.5, description="How subtle (0=very obvious, 1=very subtle)"
    )


class PlotThread(BaseModel):
    """A thematic or plot thread running through the story."""

    id: str = Field(description="Unique thread ID")
    name: str = Field(description="Name of the thread")
    thread_type: PlotThreadType = Field(description="Type of plot thread")

    # Thread progression
    description: str = Field(description="Thread description")
    chapters_active: list[int] = Field(
        default_factory=list, description="Chapters where this thread is active"
    )

    # Thread state
    status: OutlineStatus = Field(
        default=OutlineStatus.PENDING, description="Current status"
    )
    current_state: str = Field(
        default="", description="Current state of the thread"
    )

    # Key events in this thread
    key_events: list[str] = Field(
        default_factory=list, description="Key events in this thread"
    )


class VolumeOutline(BaseModel):
    """Outline for a volume/part of the novel."""

    id: str = Field(description="Unique volume ID")
    number: int = Field(description="Volume number")
    title: str = Field(description="Volume title")

    # Volume structure
    chapter_start: int = Field(description="Starting chapter number")
    chapter_end: int = Field(description="Ending chapter number")

    # Volume content
    description: str = Field(description="Volume description/synopsis")
    theme: str = Field(default="", description="Volume-specific theme")
    central_conflict: str = Field(default="", description="Central conflict of volume")

    # Volume arc
    arc_summary: str = Field(
        default="", description="Summary of character arc in this volume"
    )
    key_events: list[str] = Field(
        default_factory=list, description="Key events in this volume"
    )

    # Status
    status: OutlineStatus = Field(
        default=OutlineStatus.PENDING, description="Outline status"
    )


class ChapterOutline(BaseModel):
    """Outline for a single chapter."""

    id: str = Field(description="Unique chapter ID")
    number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")

    # Chapter type
    is_prologue: bool = Field(default=False, description="Is prologue")
    is_epilogue: bool = Field(default=False, description="Is epilogue")
    is_bridge: bool = Field(
        default=False, description="Is a bridge/transition chapter"
    )

    # Chapter content
    summary: str = Field(description="Chapter summary")
    chapter_goals: list[str] = Field(
        default_factory=list, description="Goals to accomplish in chapter"
    )

    # POV and characters
    pov_character: Optional[str] = Field(
        default=None, description="POV character name"
    )
    characters_involved: list[str] = Field(
        default_factory=list, description="Character IDs appearing"
    )

    # Plot points
    plot_point_ids: list[str] = Field(
        default_factory=list, description="Plot point IDs in this chapter"
    )
    plot_threads_advanced: list[str] = Field(
        default_factory=list, description="Plot thread IDs advanced"
    )

    # Pacing
    tension_level: TensionLevel = Field(
        default=TensionLevel.MODERATE, description="Tension level"
    )
    pacing_notes: str = Field(default="", description="Pacing notes")

    # Scene breakdown
    scene_count: int = Field(default=3, description="Number of scenes")
    scene_summaries: list[str] = Field(
        default_factory=list, description="Summary of each scene"
    )

    # Foreshadowing
    foreshadowing_planted: list[str] = Field(
        default_factory=list, description="Foreshadowing IDs planted"
    )
    foreshadowing_payoffs: list[str] = Field(
        default_factory=list, description="Foreshadowing IDs paid off"
    )

    # Status
    status: OutlineStatus = Field(
        default=OutlineStatus.PENDING, description="Outline status"
    )
    target_word_count: int = Field(
        default=3000, description="Target word count"
    )


class SceneOutline(BaseModel):
    """Outline for a single scene."""

    id: str = Field(description="Unique scene ID")
    number: int = Field(description="Scene number within chapter")
    chapter_id: str = Field(description="Parent chapter ID")

    # Scene content
    location: str = Field(default="", description="Scene location")
    time_period: str = Field(default="", description="Time period (day/night, season)")
    setting_description: str = Field(
        default="", description="Environmental details"
    )

    # Characters
    characters: list[str] = Field(
        default_factory=list, description="Character IDs in scene"
    )
    pov_character: Optional[str] = Field(
        default=None, description="POV character"
    )

    # Scene purpose
    scene_purpose: ScenePurpose = Field(
        default=ScenePurpose.rising_action, description="Purpose in story"
    )
    purpose_description: str = Field(
        default="", description="Detailed purpose description"
    )

    # Content
    scene_summary: str = Field(default="", description="What happens in scene")
    key_dialogues: list[str] = Field(
        default_factory=list, description="Key dialogue points"
    )
    character_actions: list[str] = Field(
        default_factory=list, description="Key character actions"
    )

    # Emotional tone
    mood: str = Field(default="", description="Scene mood/atmosphere")
    emotional_beat: str = Field(
        default="", description="Emotional beat of scene"
    )

    # Thread advancement
    plot_threads_advanced: list[str] = Field(
        default_factory=list, description="Plot threads advanced"
    )
    foreshadowing_planted: list[str] = Field(
        default_factory=list, description="Foreshadowing IDs"
    )

    # Pacing
    tension_level: TensionLevel = Field(
        default=TensionLevel.MODERATE, description="Scene tension"
    )
    duration_words: int = Field(
        default=800, description="Estimated word count"
    )


class StoryOutline(BaseModel):
    """Complete story outline for a novel."""

    id: str = Field(description="Unique outline ID")
    title: str = Field(description="Story title")
    genre: str = Field(description="Genre")
    theme: str = Field(description="Central theme")

    # Structure type
    outline_type: StoryOutlineType = Field(
        default=StoryOutlineType.THREE_ACT, description="Outline structure type"
    )

    # Target metrics
    target_word_count: int = Field(
        default=80000, description="Target total word count"
    )
    target_volume_count: int = Field(
        default=1, description="Target number of volumes"
    )
    target_chapter_count: int = Field(
        default=24, description="Target number of chapters"
    )

    # Outline components
    volumes: list[VolumeOutline] = Field(
        default_factory=list, description="Volume outlines"
    )
    chapters: list[ChapterOutline] = Field(
        default_factory=list, description="Chapter outlines"
    )
    scenes: list[SceneOutline] = Field(
        default_factory=list, description="Scene outlines"
    )

    # Thread management
    plot_threads: list[PlotThread] = Field(
        default_factory=list, description="All plot threads"
    )
    foreshadowing_elements: list[ForeshadowingElement] = Field(
        default_factory=list, description="All foreshadowing elements"
    )

    # Structural elements
    prologue_outline: Optional[ChapterOutline] = Field(
        default=None, description="Prologue outline if exists"
    )
    epilogue_outline: Optional[ChapterOutline] = Field(
        default=None, description="Epilogue outline if exists"
    )

    # Integration
    main_character_ids: list[str] = Field(
        default_factory=list, description="Main character IDs"
    )
    supporting_character_ids: list[str] = Field(
        default_factory=list, description="Supporting character IDs"
    )
    antagonist_ids: list[str] = Field(
        default_factory=list, description="Antagonist IDs"
    )

    # World hooks
    world_setting_id: Optional[str] = Field(
        default=None, description="World setting ID"
    )

    # Status
    status: OutlineStatus = Field(
        default=OutlineStatus.PENDING, description="Overall outline status"
    )

    # Metadata
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class StoryOutlineAnalysis(BaseModel):
    """Analysis of a story outline for quality and consistency."""

    outline_id: str = Field(description="Outline ID")

    # Structural analysis
    pacing_analysis: dict = Field(
        default_factory=dict, description="Pacing consistency analysis"
    )
    tension_curve: list[dict] = Field(
        default_factory=list, description="Chapter-by-chapter tension"
    )

    # Thread analysis
    thread_coverage: dict = Field(
        default_factory=dict, description="Plot thread coverage analysis"
    )
    unresolved_threads: list[str] = Field(
        default_factory=list, description="Unresolved plot threads"
    )

    # Foreshadowing analysis
    foreshadowing_balance: dict = Field(
        default_factory=dict, description="Foreshadowing balance analysis"
    )
    orphaned_foreshadowing: list[str] = Field(
        default_factory=list, description="Foreshadowing without payoff"
    )

    # Character analysis
    character_screen_time: dict = Field(
        default_factory=dict, description="Character appearance distribution"
    )
    protagonist_dominance: float = Field(
        default=0.5, description="Ratio of protagonist focus"
    )

    # Consistency checks
    timeline_consistency: list[str] = Field(
        default_factory=list, description="Timeline inconsistencies"
    )
    plot_holes: list[str] = Field(
        default_factory=list, description="Identified plot holes"
    )

    # Quality metrics
    coherence_score: float = Field(
        default=0.0, description="Overall coherence score (0-1)"
    )
    completeness_score: float = Field(
        default=0.0, description="Outline completeness score (0-1)"
    )
