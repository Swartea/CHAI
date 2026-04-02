"""Models for incremental writing (断点续写) - checkpoint and session management.

This module provides data models for saving writing progress, managing checkpoints,
and resuming writing from the last saved position.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WritingSessionStatus(str, Enum):
    """Status of a writing session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CheckpointType(str, Enum):
    """Type of checkpoint."""
    MANUAL = "manual"  # User-triggered save
    AUTO = "auto"  # Automatic save
    CHAPTER_COMPLETE = "chapter_complete"  # After completing a chapter
    SESSION_END = "session_end"  # When ending a writing session


class CheckpointStatus(str, Enum):
    """Status of a checkpoint."""
    CREATED = "created"
    VALIDATED = "validated"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"


class RecoveryStatus(str, Enum):
    """Status of recovery from checkpoint."""
    SUCCESS = "success"
    PARTIAL = "partial"  # Some data recovered
    FAILED = "failed"  # Recovery failed


class WritingPhase(str, Enum):
    """Phase of writing process."""
    PLANNING = "planning"
    OUTLINING = "outlining"
    WRITING_CHAPTER = "writing_chapter"
    REVISING_CHAPTER = "revising_chapter"
    COMPLETED = "completed"


class Checkpoint(BaseModel):
    """A checkpoint containing writing progress at a point in time."""

    id: str = Field(default_factory=lambda: f"cp_{uuid.uuid4().hex[:8]}")
    checkpoint_type: CheckpointType = Field(description="Type of checkpoint")

    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    validated_at: Optional[str] = Field(default=None)
    expires_at: Optional[str] = Field(
        default=None,
        description="When this checkpoint expires (for auto-save cleanup)"
    )

    # Status
    status: CheckpointStatus = Field(default=CheckpointStatus.CREATED)

    # Writing position
    chapter_number: int = Field(description="Chapter number at checkpoint")
    scene_number: Optional[int] = Field(
        default=None,
        description="Scene number within chapter"
    )
    word_count: int = Field(default=0, description="Word count at checkpoint")
    target_word_count: int = Field(
        default=3000,
        description="Target word count for current chapter"
    )

    # Content snapshot (optional, for quick recovery)
    last_content_preview: Optional[str] = Field(
        default=None,
        description="Last 500 characters for quick preview"
    )
    full_content_path: Optional[str] = Field(
        default=None,
        description="Path to full content file if stored externally"
    )

    # Context for continuation
    continuation_hint: str = Field(
        default="",
        description="Hint for where to continue writing"
    )
    last_scene_summary: Optional[str] = Field(
        default=None,
        description="Summary of what happened in last scene"
    )

    # Quality metrics at checkpoint
    coherence_score: float = Field(default=0.0)
    pacing_score: float = Field(default=0.0)


class WritingSession(BaseModel):
    """A writing session containing checkpoint history and progress."""

    id: str = Field(default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}")

    # Novel info
    novel_id: str = Field(description="Novel ID")
    title: str = Field(description="Novel title")
    genre: str = Field(default="", description="Genre")

    # Session info
    status: WritingSessionStatus = Field(
        default=WritingSessionStatus.ACTIVE
    )
    phase: WritingPhase = Field(default=WritingPhase.WRITING_CHAPTER)

    # Timestamps
    started_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    last_active_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    ended_at: Optional[str] = Field(default=None)

    # Checkpoints in this session
    checkpoints: list[Checkpoint] = Field(default_factory=list)

    # Current writing position
    current_chapter: int = Field(default=1)
    current_scene: Optional[int] = Field(default=None)
    current_word_count: int = Field(default=0)

    # Progress stats
    total_word_count: int = Field(default=0)
    chapters_completed: int = Field(default=0)
    target_total_word_count: int = Field(default=80000)

    # Auto-save settings
    auto_save_enabled: bool = Field(default=True)
    auto_save_interval: int = Field(default=10)

    # Notes
    session_notes: str = Field(default="", description="Session notes")


class IncrementalWritingProject(BaseModel):
    """Complete project state for incremental writing."""

    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")

    # Novel metadata
    novel_id: str = Field(description="Novel ID")
    title: str = Field(description="Novel title")
    genre: str = Field(default="", description="Genre")
    author: str = Field(default="", description="Author name")

    # Writing sessions
    sessions: list[WritingSession] = Field(default_factory=list)
    current_session_id: Optional[str] = Field(default=None)

    # All checkpoints (across sessions)
    checkpoints: list[Checkpoint] = Field(default_factory=list)

    # Latest checkpoint for quick resume
    latest_checkpoint_id: Optional[str] = Field(default=None)

    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    last_modified_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # Progress
    total_word_count: int = Field(default=0)
    target_total_word_count: int = Field(default=80000)
    completed_chapters: list[int] = Field(default_factory=list)
    in_progress_chapters: list[int] = Field(default_factory=list)
    pending_chapters: list[int] = Field(default_factory=list)

    # Overall stats
    total_sessions_count: int = Field(default=0)
    total_writing_time_hours: float = Field(default=0.0)

    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional project metadata"
    )


class ChapterProgress(BaseModel):
    """Progress tracking for a single chapter."""

    chapter_number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")

    # Status
    status: WritingSessionStatus = Field(
        default=WritingSessionStatus.ACTIVE
    )

    # Content
    content: str = Field(default="", description="Chapter content")
    word_count: int = Field(default=0, description="Current word count")
    target_word_count: int = Field(default=3000, description="Target word count")

    # Progress
    progress_percentage: float = Field(
        default=0.0,
        description="Progress as percentage"
    )

    # Checkpoint info
    last_checkpoint_id: Optional[str] = Field(default=None)
    last_checkpoint_at: Optional[str] = Field(default=None)
    checkpoint_count: int = Field(default=0, description="Number of checkpoints")

    # Scene tracking
    scenes_completed: int = Field(default=0)
    total_scenes: int = Field(default=1)

    # Quality
    coherence_score: float = Field(default=0.0)
    pacing_score: float = Field(default=0.0)

    # Timestamps
    started_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)
    last_modified_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class ResumeContext(BaseModel):
    """Context information for resuming writing from checkpoint."""

    # Novel info
    novel_title: str = Field(description="Novel title")
    genre: str = Field(description="Genre")

    # Last writing position
    last_chapter: int = Field(description="Last chapter number written")
    last_scene: Optional[int] = Field(
        default=None,
        description="Last scene number"
    )
    last_word_count: int = Field(default=0, description="Total word count")

    # Last content for continuity
    last_content_excerpt: Optional[str] = Field(
        default=None,
        description="Last 500 characters of last chapter"
    )
    last_scene_summary: Optional[str] = Field(
        default=None,
        description="Summary of last scene"
    )

    # Continuation hint
    continuation_hint: str = Field(
        default="",
        description="Hint for continuing the story"
    )

    # Active plot threads (for continuity)
    active_plot_threads: list[str] = Field(
        default_factory=list,
        description="Plot threads that should continue"
    )

    # Pending foreshadowing
    pending_foreshadowing: list[str] = Field(
        default_factory=list,
        description="Foreshadowing elements yet to pay off"
    )

    # Character states (key character states at last writing)
    character_states: dict = Field(
        default_factory=dict,
        description="Current states of main characters"
    )

    # World context
    world_context: str = Field(
        default="",
        description="Summary of world setting for continuity"
    )

    # Quality at checkpoint
    coherence_score: float = Field(default=0.0)
    pacing_score: float = Field(default=0.0)

    # Checkpoint timestamp
    checkpoint_created_at: Optional[str] = Field(default=None)


class IncrementalWritingRecovery(BaseModel):
    """Result of recovery from incremental writing checkpoint."""

    success: bool = Field(description="Whether recovery succeeded")
    recovery_status: RecoveryStatus = Field(description="Recovery status")

    # Project state
    project: Optional[IncrementalWritingProject] = Field(
        default=None,
        description="Recovered project state"
    )

    # Checkpoint used
    checkpoint_id: Optional[str] = Field(default=None)
    checkpoint_created_at: Optional[str] = Field(default=None)

    # Resume context
    resume_context: Optional[ResumeContext] = Field(
        default=None,
        description="Context for resuming"
    )

    # Statistics
    recovered_word_count: int = Field(default=0)
    recovered_chapters: int = Field(default=0)
    recovered_sessions: int = Field(default=0)

    # Warnings/errors
    recovery_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings during recovery"
    )
    recovery_errors: list[str] = Field(
        default_factory=list,
        description="Errors during recovery"
    )

    # Timestamp
    recovered_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class AutoSaveConfig(BaseModel):
    """Configuration for auto-save functionality."""

    enabled: bool = Field(default=True)
    auto_save_interval: int = Field(default=10)
    max_checkpoints: int = Field(
        default=50,
        description="Maximum auto-save checkpoints to keep"
    )
    checkpoint_expiry_hours: int = Field(
        default=168,
        description="Expiry time for auto-save checkpoints (7 days)"
    )
    save_content_preview: bool = Field(
        default=True,
        description="Whether to save content preview"
    )
    backup_before_save: bool = Field(
        default=True,
        description="Whether to create backup before saving"
    )


class IncrementalWritingSummary(BaseModel):
    """Summary of incremental writing progress."""

    novel_title: str = Field(description="Novel title")
    genre: str = Field(description="Genre")

    # Overall progress
    total_word_count: int = Field(default=0)
    target_word_count: int = Field(default=80000)
    progress_percentage: float = Field(default=0.0)

    # Chapters
    total_chapters: int = Field(default=0)
    completed_chapters: int = Field(default=0)
    in_progress_chapters: int = Field(default=0)
    pending_chapters: int = Field(default=0)

    # Next writing position
    next_chapter_to_write: Optional[int] = Field(default=None)
    next_chapter_title: Optional[str] = Field(default=None)

    # Sessions
    total_sessions: int = Field(default=0)
    total_writing_time_hours: float = Field(default=0.0)

    # Checkpoints
    total_checkpoints: int = Field(default=0)
    latest_checkpoint_at: Optional[str] = Field(default=None)

    # Auto-save status
    auto_save_enabled: bool = Field(default=True)
    last_auto_save_at: Optional[str] = Field(default=None)

    # Quality metrics
    average_coherence: float = Field(default=0.0)
    average_pacing: float = Field(default=0.0)
