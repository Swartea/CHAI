"""Main story structure models for narrative framework implementation."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MainStoryStructureType(str, Enum):
    """Types of main story structure frameworks."""
    THREE_ACT = "three_act"
    HEROS_JOURNEY = "heros_journey"
    SEVEN_POINT = "seven_point"
    SAVE_THE_CAT = "save_the_cat"
    FREYTAGS_PYRAMID = "freytags_pyramid"
    KISHOTENKETSU = "kishotenketsu"


class StoryBeatType(str, Enum):
    """Types of story beats within a structure."""
    # Common beats
    EXPOSITION = "exposition"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CRISIS = "crisis"
    MIDPOINT = "midpoint"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"

    # Hero's Journey specific
    ORDINARY_WORLD = "ordinary_world"
    CALL_TO_ADVENTURE = "call_to_adventure"
    REFUSAL_OF_CALL = "refusal_of_call"
    MEETING_THE_MENTOR = "meeting_the_mentor"
    CROSSING_THE_THRESHOLD = "crossing_the_threshold"
    TESTS_ALLIES_ENEMIES = "tests_allies_enemies"
    APPROACH_TO_INMOST_CAVE = "approach_to_innermost_cave"
    ORDEAL = "ordeal"
    REWARD = "reward"
    THE_ROAD_BACK = "the_road_back"
    RESURRECTION = "resurrection"
    RETURN_WITH_ELIXIR = "return_with_elixir"

    # Seven-Point specific
    HOOK = "hook"
    FIRST_TURN = "first_turn"
    PINCER_ONE = "pincer_one"
    FIRST_TURNING_POINT = "first_turning_point"
    SECOND_TURN = "second_turn"
    PINCER_TWO = "pincer_two"
    SECOND_TURNING_POINT = "second_turning_point"
    DARK_MOMENT = "dark_moment"
    THIRD_TURNING_POINT = "third_turning_point"
    ALL_IS_LOST = "all_is_lost"

    # Save the Cat specific
    OPENING_IMAGE = "opening_image"
    THEME_STATED = "theme_stated"
    SETUP = "setup"
    CATALYST = "catalyst"
    DEBATE = "debate"
    BREAK_INTO_TWO = "break_into_two"
    B_STORY = "b_story"
    FUN_AND_GAMES = "fun_and_games"
    BAD_GUYS_CLOSE_IN = "bad_guys_close_in"
    DARK_NIGHT_OF_SOUL = "dark_night_of_soul"
    BREAK_INTO_THREE = "break_into_three"
    FINALE = "finale"
    FINAL_IMAGE = "final_image"

    # Kishotenketsu specific
    INTRODUCTION = "introduction"
    DEVELOPMENT = "development"
    TWIST = "twist"
    CONCLUSION = "conclusion"


class StoryBeatStatus(str, Enum):
    """Status of a story beat."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    REVISED = "revised"


class StoryBeat(BaseModel):
    """A single story beat in the narrative structure."""

    id: str = Field(description="Unique beat ID")
    beat_type: StoryBeatType = Field(description="Type of story beat")
    name: str = Field(description="Beat name")
    description: str = Field(description="Beat description")

    # Position in structure
    order: int = Field(description="Order within the structure")
    act_number: Optional[int] = Field(
        default=None, description="Act number (for multi-act structures)"
    )

    # Chapter mapping
    start_chapter: int = Field(description="Starting chapter number")
    end_chapter: int = Field(description="Ending chapter number")

    # Content
    purpose: str = Field(description="Purpose of this beat")
    key_events: list[str] = Field(
        default_factory=list, description="Key events in this beat"
    )
    character_involvement: list[str] = Field(
        default_factory=list, description="Character IDs involved"
    )

    # Thematic elements
    themes_explored: list[str] = Field(
        default_factory=list, description="Themes explored in this beat"
    )
    tension_level: str = Field(
        default="moderate", description="Tension level: low/moderate/high/climax"
    )

    # Status
    status: StoryBeatStatus = Field(
        default=StoryBeatStatus.PENDING, description="Beat status"
    )

    # Optional AI-generated content
    ai_content: Optional[str] = Field(
        default=None, description="AI-generated beat content"
    )


class ActStructure(BaseModel):
    """Structure of an act within the story."""

    id: str = Field(description="Unique act ID")
    number: int = Field(description="Act number")
    name: str = Field(description="Act name")
    description: str = Field(description="Act description")

    # Chapter range
    start_chapter: int = Field(description="Starting chapter")
    end_chapter: int = Field(description="Ending chapter")

    # Beats in this act
    beats: list[StoryBeat] = Field(
        default_factory=list, description="Story beats in this act"
    )

    # Act purpose
    purpose: str = Field(description="Purpose of this act")
    key_conflict: str = Field(description="Key conflict in this act")

    # Thematic focus
    thematic_focus: str = Field(
        default="", description="Thematic focus of this act"
    )


class MainStoryStructure(BaseModel):
    """Complete main story structure for a novel."""

    id: str = Field(description="Unique structure ID")
    title: str = Field(description="Story title")
    genre: str = Field(description="Genre")
    theme: str = Field(description="Central theme")

    # Structure type
    structure_type: MainStoryStructureType = Field(
        description="Story structure framework used"
    )

    # Target metrics
    target_chapters: int = Field(
        default=24, description="Target number of chapters"
    )
    target_word_count: int = Field(
        default=80000, description="Target word count"
    )

    # Acts
    acts: list[ActStructure] = Field(
        default_factory=list, description="Act structures"
    )

    # All beats
    beats: list[StoryBeat] = Field(
        default_factory=list, description="All story beats"
    )

    # Integration
    main_character_ids: list[str] = Field(
        default_factory=list, description="Main character IDs"
    )
    antagonist_id: Optional[str] = Field(
        default=None, description="Main antagonist ID"
    )

    # Core story elements
    core_conflict: str = Field(description="Core conflict description")
    central_question: str = Field(
        default="", description="Central question the story explores"
    )
    thematic_statement: str = Field(
        default="", description="Thematic statement"
    )

    # Status
    status: StoryBeatStatus = Field(
        default=StoryBeatStatus.PENDING, description="Structure status"
    )

    # Metadata
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class StructureAnalysis(BaseModel):
    """Analysis of a story structure for quality and consistency."""

    structure_id: str = Field(description="Structure ID")

    # Structural integrity
    beat_coverage: dict = Field(
        default_factory=dict, description="Coverage of structure beats"
    )
    missing_beats: list[str] = Field(
        default_factory=list, description="Missing required beats"
    )

    # Pacing analysis
    pacing_score: float = Field(
        default=0.0, description="Pacing score (0-1)"
    )
    chapter_distribution: dict = Field(
        default_factory=dict, description="Chapter distribution analysis"
    )

    # Tension curve
    tension_curve: list[dict] = Field(
        default_factory=list, description="Beat-by-beat tension"
    )

    # Thematic analysis
    thematic_coherence: float = Field(
        default=0.0, description="Thematic coherence score (0-1)"
    )
    thematic_progression: list[str] = Field(
        default_factory=list, description="How themes develop"
    )

    # Character arc alignment
    character_arc_alignment: dict = Field(
        default_factory=dict, description="Alignment with character arcs"
    )

    # Quality metrics
    coherence_score: float = Field(
        default=0.0, description="Overall coherence score (0-1)"
    )
    completeness_score: float = Field(
        default=0.0, description="Structure completeness score (0-1)"
    )

    # Issues
    structural_issues: list[str] = Field(
        default_factory=list, description="Identified structural issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )