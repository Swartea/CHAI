"""Models for full book polishing after all chapters are completed."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PolishingStatus(str, Enum):
    """Status of polishing process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    NEEDS_REVISION = "needs_revision"
    FAILED = "failed"


class PolishingType(str, Enum):
    """Types of polishing available for full book."""
    GLOBAL_TONE = "global_tone"  # Overall tone consistency across book
    CHARACTER_VOICE = "character_voice"  # Character voice consistency
    NARRATIVE_PACING = "narrative_pacing"  # Pacing analysis across volumes/chapters
    THEME_COHERENCE = "theme_coherence"  # Theme and motif consistency
    WORLD_RULES = "world_rules"  # World logic consistency
    PLOT_THREADS = "plot_threads"  # Subplot/foreshadowing coherence
    EMOTIONAL_ARC = "emotional_arc"  # Emotional progression consistency
    DIALOGUE_UNIVERSAL = "dialogue_universal"  # Cross-chapter dialogue consistency
    DESCRIPTION_CONSISTENCY = "description_consistency"  # Scene/character description consistency
    TRANSITION_BOOK = "book_transition"  # Chapter-to-chapter transitions
    REPETITION_CHECK = "repetition_check"  # Word/phrase repetition across chapters
    READABILITY = "readability"  # Overall readability analysis


class PolishingSeverity(str, Enum):
    """Severity levels for polishing issues."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class PolishingIssue(BaseModel):
    """A single polishing issue found."""
    issue_id: str
    polishing_type: PolishingType
    severity: PolishingSeverity
    chapter_start: Optional[int] = None  # Starting chapter of the issue
    chapter_end: Optional[int] = None  # Ending chapter of the issue
    character_name: Optional[str] = None  # Character related to the issue
    description: str
    location_hint: str = ""  # Where in the text to look
    suggestion: str = ""  # How to fix it
    example: str = ""  # Example of the issue


class PolishingResult(BaseModel):
    """Result of a single polishing type."""
    polishing_type: PolishingType
    status: PolishingStatus
    score: float = Field(default=1.0, description="Score from 0.0 to 1.0")
    issue_count: int = 0
    critical_issues: list[PolishingIssue] = Field(default_factory=list)
    major_issues: list[PolishingIssue] = Field(default_factory=list)
    moderate_issues: list[PolishingIssue] = Field(default_factory=list)
    minor_issues: list[PolishingIssue] = Field(default_factory=list)
    details: dict = Field(default_factory=dict)
    suggestions: list[str] = Field(default_factory=list)


class VolumePolishingProfile(BaseModel):
    """Polishing profile for a single volume."""
    volume_id: str
    volume_number: int
    title: str
    status: PolishingStatus
    overall_score: float = 1.0
    issues_found: int = 0
    polishing_results: list[PolishingResult] = Field(default_factory=list)


class ChapterPolishingProfile(BaseModel):
    """Polishing profile for a chapter (cross-reference data)."""
    chapter_id: str
    chapter_number: int
    title: str
    tone_profile: Optional[str] = None
    pacing_score: float = 1.0
    character_mentions: dict[str, int] = Field(default_factory=dict)  # character_name -> count
    key_themes: list[str] = Field(default_factory=list)
    emotional_tone: Optional[str] = None


class BookPolishingConfig(BaseModel):
    """Configuration for full book polishing."""
    # Which polishing types to enable (all enabled by default)
    enable_global_tone: bool = True
    enable_character_voice: bool = True
    enable_narrative_pacing: bool = True
    enable_theme_coherence: bool = True
    enable_world_rules: bool = True
    enable_plot_threads: bool = True
    enable_emotional_arc: bool = True
    enable_dialogue_universal: bool = True
    enable_description_consistency: bool = True
    enable_transition_book: bool = True
    enable_repetition_check: bool = True
    enable_readability: bool = True

    # Thresholds
    min_acceptable_score: float = 0.7  # Minimum score to pass
    min_chapter_count: int = 1  # Minimum chapters for analysis

    # Check strictness
    strict_consistency: bool = False
    strict_pacing: bool = False


class PolishingPlan(BaseModel):
    """Plan for revision based on polishing results."""
    volume_revisions: list[str] = Field(default_factory=list)
    chapter_revisions: list[tuple[int, str]] = Field(default_factory=list)  # (chapter_number, reason)
    global_fixes: list[str] = Field(default_factory=list)
    character_voice_fixes: list[str] = Field(default_factory=list)
    pacing_fixes: list[str] = Field(default_factory=list)
    theme_fixes: list[str] = Field(default_factory=list)
    world_rules_fixes: list[str] = Field(default_factory=list)
    plot_thread_fixes: list[str] = Field(default_factory=list)
    emotional_arc_fixes: list[str] = Field(default_factory=list)
    dialogue_fixes: list[str] = Field(default_factory=list)
    description_fixes: list[str] = Field(default_factory=list)
    transition_fixes: list[str] = Field(default_factory=list)
    repetition_fixes: list[str] = Field(default_factory=list)
    readability_fixes: list[str] = Field(default_factory=list)


class VolumePolishingReport(BaseModel):
    """Polishing report for a single volume."""
    volume_id: str
    volume_number: int
    title: str
    status: PolishingStatus
    overall_score: float
    polishing_results: list[PolishingResult]
    revision_plan: Optional[PolishingPlan] = None
    polished_at: str
    summary: str = ""


class BookPolishingReport(BaseModel):
    """Comprehensive polishing report for the entire book."""
    book_id: str
    title: str
    total_volumes: int
    total_chapters: int
    status: PolishingStatus
    overall_score: float
    volume_reports: list[VolumePolishingReport]
    polishing_results: list[PolishingResult]  # Global-level results
    revision_plan: Optional[PolishingPlan] = None
    polished_at: str
    summary: str = ""


class PolishingSummary(BaseModel):
    """Summary of polishing across all volumes and chapters."""
    total_volumes: int
    total_chapters: int
    volumes_passed: int
    volumes_needing_revision: int
    average_score: float
    global_issues: list[str] = Field(default_factory=list)
    critical_patterns: list[str] = Field(default_factory=list)
    recommended_fixes: list[str] = Field(default_factory=list)
    overall_recommendation: str = ""


class FullBookPolishingRequest(BaseModel):
    """Request for full book polishing."""
    book_id: str
    title: str
    volumes: list[dict] = Field(default_factory=list)  # Volume data with chapters
    # Each volume dict contains:
    # - volume_id, volume_number, title, chapters: list of {chapter_id, chapter_number, title, content}
    config: BookPolishingConfig = Field(default_factory=BookPolishingConfig)
    # Context data for polishing
    world_setting: Optional[dict] = None
    characters: list[dict] = Field(default_factory=list)
    subplot_design: Optional[dict] = None
    climax_ending: Optional[dict] = None
    outline_components: Optional[dict] = None
    previous_self_check_results: Optional[list[dict]] = None


class FullBookPolishingResult(BaseModel):
    """Result of full book polishing."""
    success: bool
    book_id: str
    title: str
    status: PolishingStatus
    report: BookPolishingReport
    summary: PolishingSummary
    revision_plan: Optional[PolishingPlan] = None
    error_message: Optional[str] = None


class PolishingIssueTracker(BaseModel):
    """Tracker for issues across chapters/volumes."""
    all_issues: list[PolishingIssue] = Field(default_factory=list)
    issue_count_by_type: dict[str, int] = Field(default_factory=dict)
    issue_count_by_severity: dict[str, int] = Field(default_factory=dict)
    chapters_with_issues: dict[int, int] = Field(default_factory=dict)  # chapter_number -> issue_count
    volumes_with_issues: dict[int, int] = Field(default_factory=dict)  # volume_number -> issue_count