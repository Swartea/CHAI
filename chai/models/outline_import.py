"""Models for importing existing story outlines to continue writing.

This module provides data models for parsing, validating, and integrating
external story outlines into the CHAI writing system.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ImportFormat(str, Enum):
    """Supported import formats for story outlines."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    CHAPTER_OUTLINE = "chapter_outline"


class ImportSource(str, Enum):
    """Source of the imported outline."""
    USER_FILE = "user_file"
    AI_GENERATED = "ai_generated"
    EXTERNAL_TOOL = "external_tool"
    LEGACY_PROJECT = "legacy_project"
    TEMPLATE = "template"


class OutlineValidationStatus(str, Enum):
    """Validation status of imported outline."""
    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"
    EMPTY = "empty"


class ChapterWritingStatus(str, Enum):
    """Writing status of a chapter in imported outline."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"  # Some content exists
    COMPLETE = "complete"
    NEEDS_REVISION = "needs_revision"


class ImportedVolume(BaseModel):
    """Volume data from imported outline."""
    id: str = Field(default_factory=lambda: f"vol_{uuid.uuid4().hex[:8]}")
    number: int = Field(description="Volume number")
    title: str = Field(description="Volume title")
    chapter_start: int = Field(description="Starting chapter number")
    chapter_end: int = Field(description="Ending chapter number")
    description: str = Field(default="", description="Volume description")
    theme: str = Field(default="", description="Volume theme")
    central_conflict: str = Field(default="", description="Central conflict")


class ImportedChapter(BaseModel):
    """Chapter data from imported outline."""
    id: str = Field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:8]}")
    number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")
    is_prologue: bool = Field(default=False, description="Is prologue")
    is_epilogue: bool = Field(default=False, description="Is epilogue")
    is_bridge: bool = Field(default=False, description="Is bridge chapter")
    summary: str = Field(default="", description="Chapter summary")
    content: Optional[str] = Field(default=None, description="Existing chapter content")
    word_count: int = Field(default=0, description="Existing word count")
    status: ChapterWritingStatus = Field(
        default=ChapterWritingStatus.PENDING,
        description="Writing status"
    )
    pov_character: Optional[str] = Field(default=None, description="POV character")
    characters_involved: list[str] = Field(default_factory=list)
    tension_level: str = Field(default="moderate", description="Tension level")
    pacing_notes: str = Field(default="", description="Pacing notes")
    scene_summaries: list[str] = Field(default_factory=list)
    plot_threads_advanced: list[str] = Field(default_factory=list)
    foreshadowing_planted: list[str] = Field(default_factory=list)
    foreshadowing_payoffs: list[str] = Field(default_factory=list)


class ImportedScene(BaseModel):
    """Scene data from imported outline."""
    id: str = Field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    number: int = Field(description="Scene number within chapter")
    chapter_id: str = Field(description="Parent chapter ID")
    location: str = Field(default="", description="Scene location")
    time_period: str = Field(default="", description="Time period")
    setting_description: str = Field(default="", description="Setting description")
    characters: list[str] = Field(default_factory=list)
    pov_character: Optional[str] = Field(default=None)
    scene_purpose: str = Field(default="rising_action", description="Scene purpose")
    scene_summary: str = Field(default="", description="Scene summary")
    key_dialogues: list[str] = Field(default_factory=list)
    character_actions: list[str] = Field(default_factory=list)
    mood: str = Field(default="", description="Scene mood")
    tension_level: str = Field(default="moderate", description="Tension level")


class ImportedPlotThread(BaseModel):
    """Plot thread from imported outline."""
    id: str = Field(default_factory=lambda: f"thread_{uuid.uuid4().hex[:8]}")
    name: str = Field(description="Thread name")
    thread_type: str = Field(default="subplot", description="Thread type")
    description: str = Field(default="", description="Thread description")
    chapters_active: list[int] = Field(default_factory=list)
    current_state: str = Field(default="", description="Current state")
    key_events: list[str] = Field(default_factory=list)


class ImportedForeshadowing(BaseModel):
    """Foreshadowing element from imported outline."""
    id: str = Field(default_factory=lambda: f"fore_{uuid.uuid4().hex[:8]}")
    element: str = Field(description="Foreshadowing element")
    foreshadowing_type: str = Field(default="indirect", description="Foreshadowing type")
    chapter_planted: int = Field(description="Chapter planted")
    scene_location: str = Field(default="", description="Location in chapter")
    description: str = Field(default="", description="How it appears")
    chapter_payoff: Optional[int] = Field(default=None, description="Chapter payoff")
    payoff_description: str = Field(default="", description="How payoff occurs")
    status: str = Field(default="planted", description="Foreshadowing status")


class ImportedCharacter(BaseModel):
    """Character reference from imported outline."""
    id: str = Field(default_factory=lambda: f"char_{uuid.uuid4().hex[:8]}")
    name: str = Field(description="Character name")
    role: str = Field(default="supporting", description="Character role")
    description: str = Field(default="", description="Character description")


class ImportedWorldSetting(BaseModel):
    """World setting from imported outline."""
    id: str = Field(default_factory=lambda: f"world_{uuid.uuid4().hex[:8]}")
    name: str = Field(default="", description="World name")
    genre: str = Field(default="", description="Genre")
    description: str = Field(default="", description="World description")


class RawOutlineData(BaseModel):
    """Raw outline data before parsing into StoryOutline model."""
    title: Optional[str] = Field(default=None, description="Story title")
    genre: Optional[str] = Field(default=None, description="Genre")
    theme: Optional[str] = Field(default=None, description="Central theme")
    author: Optional[str] = Field(default=None, description="Author name")
    description: Optional[str] = Field(default=None, description="Story description")

    # Structure
    outline_type: str = Field(default="three_act", description="Outline structure type")
    target_word_count: int = Field(default=80000, description="Target word count")
    target_chapter_count: int = Field(default=24, description="Target chapter count")

    # Raw content
    volumes_data: list[dict] = Field(default_factory=list)
    chapters_data: list[dict] = Field(default_factory=list)
    scenes_data: list[dict] = Field(default_factory=list)
    plot_threads_data: list[dict] = Field(default_factory=list)
    foreshadowing_data: list[dict] = Field(default_factory=list)
    characters_data: list[dict] = Field(default_factory=list)
    world_setting_data: Optional[dict] = Field(default=None)

    # Metadata
    source_format: ImportFormat = Field(default=ImportFormat.JSON)
    source: ImportSource = Field(default=ImportSource.USER_FILE)
    original_file_name: Optional[str] = Field(default=None)
    imported_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    notes: str = Field(default="", description="Import notes")


class OutlineImportResult(BaseModel):
    """Result of importing a story outline."""
    success: bool = Field(description="Whether import succeeded")
    outline_id: str = Field(
        default_factory=lambda: f"imported_{uuid.uuid4().hex[:8]}"
    )

    # Import stats
    import_format: ImportFormat = Field(description="Format used for import")
    source: ImportSource = Field(description="Import source")

    # Validation
    validation_status: OutlineValidationStatus = Field(
        description="Validation status"
    )
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)

    # Content stats
    total_chapters: int = Field(default=0)
    completed_chapters: int = Field(default=0)
    partial_chapters: int = Field(default=0)
    pending_chapters: int = Field(default=0)

    # Writing status analysis
    writing_status_summary: dict = Field(default_factory=dict)

    # Next writing position
    next_chapter_to_write: Optional[int] = Field(
        default=None,
        description="Next chapter number to continue writing"
    )
    continuation_context: dict = Field(
        default_factory=dict,
        description="Context for continuing from next chapter"
    )

    # Original data reference
    raw_data: Optional[RawOutlineData] = Field(
        default=None,
        description="Original raw outline data"
    )

    # Timestamp
    imported_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class ContinuationContext(BaseModel):
    """Context information for continuing to write from an imported outline."""
    story_title: str = Field(description="Story title")
    genre: str = Field(description="Genre")

    # Last written position
    last_written_chapter: Optional[int] = Field(
        default=None,
        description="Last chapter number that was written"
    )
    last_written_scene: Optional[int] = Field(
        default=None,
        description="Last scene number within chapter"
    )

    # Summary of written content
    written_chapters_summary: list[dict] = Field(
        default_factory=list,
        description="Summary of already-written chapters"
    )

    # Last content excerpt for continuity
    last_content_excerpt: Optional[str] = Field(
        default=None,
        description="Last 500 characters of last chapter for continuity"
    )

    # Pending chapters
    pending_chapters: list[ImportedChapter] = Field(
        default_factory=list,
        description="Chapters that still need writing"
    )

    # Active plot threads
    active_plot_threads: list[str] = Field(
        default_factory=list,
        description="Plot threads that should continue"
    )

    # Pending foreshadowing
    pending_foreshadowing: list[str] = Field(
        default_factory=list,
        description="Foreshadowing elements yet to pay off"
    )

    # Character states
    character_states: dict = Field(
        default_factory=dict,
        description="Current states of main characters"
    )

    # World context
    world_context: str = Field(
        default="",
        description="Summary of world setting for continuity"
    )


class OutlineAnalysis(BaseModel):
    """Analysis of imported outline structure and completeness."""
    outline_id: str = Field(description="Outline ID")

    # Structure analysis
    has_volume_structure: bool = Field(default=False)
    has_chapter_structure: bool = Field(default=False)
    has_scene_structure: bool = Field(default=False)
    has_plot_threads: bool = Field(default=False)
    has_foreshadowing: bool = Field(default=False)

    # Content completeness
    chapters_with_summaries: int = Field(default=0)
    chapters_with_content: int = Field(default=0)
    chapters_empty: int = Field(default=0)

    # Writing progress
    total_word_count: int = Field(default=0)
    average_chapter_word_count: float = Field(default=0.0)
    writing_progress_percentage: float = Field(default=0.0)

    # Structural issues
    missing_chapter_numbers: list[int] = Field(default_factory=list)
    duplicate_chapter_numbers: list[int] = Field(default_factory=list)
    orphaned_scenes: list[str] = Field(default_factory=list)

    # Recommendations
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improving the outline"
    )


class OutlineMergeRequest(BaseModel):
    """Request to merge imported outline with existing project data."""
    # Imported outline data
    imported_outline: RawOutlineData

    # Existing project reference (optional)
    existing_project_id: Optional[str] = Field(default=None)

    # Merge options
    merge_strategy: str = Field(
        default="replace_missing",
        description="Strategy: replace_missing, merge_all, prefer_existing"
    )
    preserve_existing_content: bool = Field(
        default=True,
        description="Keep existing chapter content when merging"
    )
    fill_missing_outline: bool = Field(
        default=True,
        description="Generate outline for missing chapters"
    )

    # Character mapping
    character_mappings: dict = Field(
        default_factory=dict,
        description="Map imported character names to existing characters"
    )

    # World setting
    use_existing_world_setting: bool = Field(
        default=True,
        description="Use existing world setting instead of imported"
    )