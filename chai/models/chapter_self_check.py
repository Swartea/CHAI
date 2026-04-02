"""Models for chapter self-check after completion."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SelfCheckStatus(str, Enum):
    """Status of self-check."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class SelfCheckType(str, Enum):
    """Types of self-check available."""
    GRAMMAR = "grammar"  # Grammar and typo check
    SENTENCE_QUALITY = "sentence_quality"  # Disease and redundant sentences
    DIALOGUE_TAG = "dialogue_tag"  # Dialogue tag standardization
    PUNCTUATION = "punctuation"  # Punctuation standardization
    WORD_COUNT = "word_count"  # Word count validation (2000-4000)
    FORESHADOWING = "foreshadowing"  # Foreshadowing and callback check
    TRANSITION = "transition"  # Chapter transition quality
    STYLE = "style"  # Style consistency
    TONE = "tone"  # Tone consistency
    DESCRIPTION_DENSITY = "description_density"  # Description density balance
    DIALOGUE_NATURALNESS = "dialogue_naturalness"  # Dialogue naturalness
    SCENE_VIVIDNESS = "scene_vividness"  # Scene vividness
    PLOT_LOGIC = "plot_logic"  # Plot logic consistency
    PAYOFF_COMPLETENESS = "payoff_completeness"  # Payoff completeness


class SelfCheckSeverity(str, Enum):
    """Severity levels for check issues."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class SelfCheckResult(BaseModel):
    """Result of a single check type."""
    check_type: SelfCheckType
    status: SelfCheckStatus
    score: float = Field(default=1.0, description="Score from 0.0 to 1.0")
    issue_count: int = 0
    critical_issues: list[str] = Field(default_factory=list)
    major_issues: list[str] = Field(default_factory=list)
    moderate_issues: list[str] = Field(default_factory=list)
    minor_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    details: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class ChapterSelfCheckProfile(BaseModel):
    """Complete self-check profile for a chapter."""
    chapter_id: str
    chapter_number: int
    title: str
    status: SelfCheckStatus
    overall_score: float = Field(default=1.0, description="Overall score from 0.0 to 1.0")
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warning: int = 0
    total_issues: int = 0
    check_results: list[SelfCheckResult] = Field(default_factory=list)
    checked_at: Optional[str] = None


class ChapterSelfCheckConfig(BaseModel):
    """Configuration for chapter self-check."""
    # Which checks to enable (all enabled by default)
    enable_grammar: bool = True
    enable_sentence_quality: bool = True
    enable_dialogue_tag: bool = True
    enable_punctuation: bool = True
    enable_word_count: bool = True
    enable_foreshadowing: bool = True
    enable_transition: bool = True
    enable_style: bool = True
    enable_tone: bool = True
    enable_description_density: bool = True
    enable_dialogue_naturalness: bool = True
    enable_scene_vividness: bool = True
    enable_plot_logic: bool = True
    enable_payoff_completeness: bool = True

    # Thresholds
    min_word_count: int = 2000
    max_word_count: int = 4000
    min_acceptable_score: float = 0.7  # Minimum score to pass

    # Check strictness
    strict_grammar: bool = False
    strict_word_count: bool = False
    strict_style: bool = False


class SelfCheckPlan(BaseModel):
    """Plan for revision based on self-check results."""
    chapter_id: str
    chapter_number: int
    priority_fixes: list[str] = Field(default_factory=list)
    grammar_fixes: list[str] = Field(default_factory=list)
    sentence_fixes: list[str] = Field(default_factory=list)
    dialogue_tag_fixes: list[str] = Field(default_factory=list)
    punctuation_fixes: list[str] = Field(default_factory=list)
    word_count_fixes: list[str] = Field(default_factory=list)
    transition_fixes: list[str] = Field(default_factory=list)
    style_fixes: list[str] = Field(default_factory=list)
    other_fixes: list[str] = Field(default_factory=list)


class ChapterSelfCheckReport(BaseModel):
    """Comprehensive self-check report for a chapter."""
    chapter_id: str
    chapter_number: int
    title: str
    status: SelfCheckStatus
    overall_score: float
    check_results: list[SelfCheckResult]
    revision_plan: Optional[SelfCheckPlan] = None
    checked_at: str
    summary: str = ""


class NovelSelfCheckSummary(BaseModel):
    """Summary of self-check across all chapters."""
    total_chapters: int
    chapters_passed: int
    chapters_failed: int
    chapters_warning: int
    average_score: float
    common_issues: list[str] = Field(default_factory=list)
    chapters_needing_revision: list[int] = Field(default_factory=list)
    overall_recommendation: str = ""


class ChapterSelfCheckRequest(BaseModel):
    """Request for chapter self-check."""
    chapter_id: str
    chapter_number: int
    title: str
    content: str
    previous_chapter_content: Optional[str] = None
    next_chapter_content: Optional[str] = None
    config: ChapterSelfCheckConfig = Field(default_factory=ChapterSelfCheckConfig)
    # Context data for checks
    world_setting: Optional[dict] = None
    characters: list[dict] = Field(default_factory=list)
    subplot_design: Optional[dict] = None
    climax_ending: Optional[dict] = None
    outline_components: Optional[dict] = None


class ChapterSelfCheckResult(BaseModel):
    """Result of chapter self-check."""
    success: bool
    chapter_id: str
    chapter_number: int
    status: SelfCheckStatus
    profile: ChapterSelfCheckProfile
    report: ChapterSelfCheckReport
    revision_plan: Optional[SelfCheckPlan] = None
    error_message: Optional[str] = None
