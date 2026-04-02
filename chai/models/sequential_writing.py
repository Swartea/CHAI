"""Sequential writing models for auto-writing chapters in order.

This module provides models for the sequential writing workflow - the fourth step
in the CHAI novel writing workflow after complete outline generation.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SequentialWritingStatus(str, Enum):
    """Status of sequential writing process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WRITING_CHAPTER = "writing_chapter"
    CHAPTER_COMPLETE = "chapter_complete"
    CHECKPOINT_SAVED = "checkpoint_saved"
    PAUSED = "paused"
    COMPLETE = "complete"
    FAILED = "failed"


class WritingOrderMode(str, Enum):
    """Mode for writing order."""
    SEQUENTIAL = "sequential"  # Chapter 1, 2, 3...
    VOLUME_FIRST = "volume_first"  # All chapters in volume 1, then volume 2...
    CUSTOM = "custom"  # Custom order based on chapter priorities


class ChapterWritingState(str, Enum):
    """State of an individual chapter."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


class SequentialWritingConfig(BaseModel):
    """Configuration for sequential writing."""
    order_mode: WritingOrderMode = Field(default=WritingOrderMode.SEQUENTIAL, description="Writing order mode")
    start_chapter: int = Field(default=1, description="Starting chapter number")
    end_chapter: Optional[int] = Field(default=None, description="Ending chapter number (None = all)")
    auto_checkpoint: bool = Field(default=True, description="Automatically save checkpoints")
    checkpoint_interval: int = Field(default=1, description="Create checkpoint after every N chapters")
    skip_completed: bool = Field(default=True, description="Skip already completed chapters when resuming")
    validate_outline: bool = Field(default=True, description="Validate outline before writing")


class SequentialChapterProgress(BaseModel):
    """Progress for a single chapter in sequential writing."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")
    state: ChapterWritingState = Field(default=ChapterWritingState.PENDING, description="Current state")
    word_count: int = Field(default=0, description="Generated word count")
    target_word_count: int = Field(default=3000, description="Target word count")
    started_at: Optional[str] = Field(default=None, description="When writing started")
    completed_at: Optional[str] = Field(default=None, description="When writing completed")
    error_message: Optional[str] = Field(default=None, description="Error if failed")
    retry_count: int = Field(default=0, description="Number of retries")


class SequentialWritingProgress(BaseModel):
    """Overall progress of sequential writing."""
    total_chapters: int = Field(default=0, description="Total chapters to write")
    completed_chapters: int = Field(default=0, description="Completed chapters")
    in_progress_chapter: Optional[int] = Field(default=None, description="Currently writing chapter")
    total_word_count: int = Field(default=0, description="Total words written")
    average_word_count: int = Field(default=0, description="Average words per chapter")
    estimated_remaining_words: int = Field(default=0, description="Estimated remaining words")
    progress_percentage: float = Field(default=0.0, description="Progress as percentage")
    chapter_progress: list[SequentialChapterProgress] = Field(default_factory=list, description="Per-chapter progress")


class SequentialWritingRequest(BaseModel):
    """Request for sequential writing."""
    project_id: str = Field(description="Project ID")
    project_title: str = Field(description="Novel title")
    genre: str = Field(default="", description="Genre")
    outline_components: dict = Field(description="Complete outline components")
    world_setting: Optional[dict] = Field(default=None, description="World setting dict")
    characters: list[dict] = Field(default_factory=list, description="Character dicts")
    subplot_design: Optional[dict] = Field(default=None, description="Subplot design dict")
    climax_ending_system: Optional[dict] = Field(default=None, description="Climax/ending system dict")
    config: SequentialWritingConfig = Field(default_factory=SequentialWritingConfig)
    resume_from_checkpoint: bool = Field(default=False, description="Resume from latest checkpoint")


class SequentialWritingResult(BaseModel):
    """Result of sequential writing operation."""
    success: bool = Field(description="Whether writing succeeded")
    writing_id: str = Field(description="Unique writing session ID")
    project_id: str = Field(description="Project ID")
    status: SequentialWritingStatus = Field(description="Writing status")
    progress: SequentialWritingProgress = Field(description="Writing progress")
    last_chapter_completed: Optional[int] = Field(default=None, description="Last completed chapter")
    last_checkpoint_id: Optional[str] = Field(default=None, description="Last checkpoint ID")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    writing_time_seconds: float = Field(default=0.0, description="Total writing time")


class SequentialWritingSummary(BaseModel):
    """Summary of sequential writing session."""
    writing_id: str = Field(description="Writing session ID")
    project_title: str = Field(description="Novel title")
    genre: str = Field(description="Genre")
    status: SequentialWritingStatus = Field(description="Status")
    total_chapters: int = Field(description="Total chapters")
    completed_chapters: int = Field(description="Completed chapters")
    total_word_count: int = Field(description="Total words written")
    progress_percentage: float = Field(description="Progress percentage")
    next_chapter_to_write: Optional[int] = Field(default=None, description="Next chapter number")
    next_chapter_title: Optional[str] = Field(default=None, description="Next chapter title")
    estimated_remaining_time_minutes: Optional[float] = Field(default=None, description="Estimated remaining time")


class CheckpointInfo(BaseModel):
    """Information about a writing checkpoint."""
    checkpoint_id: str = Field(description="Checkpoint ID")
    chapter_number: int = Field(description="Chapter when checkpoint was created")
    created_at: str = Field(description="When checkpoint was created")
    total_word_count: int = Field(description="Word count at checkpoint")
    completed_chapters: list[int] = Field(default_factory=list, description="Completed chapter numbers")
