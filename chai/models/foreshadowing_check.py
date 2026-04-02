"""Foreshadowing and callback check models for quality assurance."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CallbackStatus(str, Enum):
    """Status of a foreshadowing callback."""
    ORPHANED = "orphaned"  # Planted but never called back
    UNPLANTED_CALLBACK = "unplanted_callback"  # Called back without proper planting
    PROPERLY_CALLED = "properly_called"  # Properly planted and called back
    PARTIALLY_CALLED = "partially_called"  # Called back but incompletely
    PREMATURE_CALLBACK = "premature_callback"  # Called back too early
    DELAYED_CALLBACK = "delayed_callback"  # Called back too late


class CallbackQuality(str, Enum):
    """Quality of the callback."""
    EXCELLENT = "excellent"  # Perfect match, enhances reading
    GOOD = "good"  # Good connection
    ACCEPTABLE = "acceptable"  # Functional but could be better
    WEAK = "weak"  # Weak connection
    MISSING = "missing"  # No clear callback found


class ForeshadowingCheckIssue(BaseModel):
    """An issue found during foreshadowing check."""
    issue_id: str = Field(description="Unique issue identifier")
    foreshadowing_id: str = Field(description="Related foreshadowing element ID")
    chapter: int = Field(description="Chapter where issue is detected")
    issue_type: str = Field(description="Type of issue")
    severity: str = Field(description="Severity: minor/moderate/severe/critical")
    description: str = Field(description="Human-readable description")
    suggested_fix: str = Field(default="", description="Suggested fix")
    priority: int = Field(default=0, description="Priority for fixing")


class PlantedForeshadowing(BaseModel):
    """A planted foreshadowing element found in text."""
    foreshadowing_id: str = Field(description="Unique identifier")
    plant_chapter: int = Field(description="Chapter where planted")
    plant_content: str = Field(description="The planted content")
    plant_context: str = Field(description="Surrounding context")
    technique: str = Field(default="", description="Foreshadowing technique used")
    subtlety_level: float = Field(default=0.5, ge=0.0, le=1.0)
    related_characters: list[str] = Field(default_factory=list)
    thematic_tags: list[str] = Field(default_factory=list)
    callback_chapter: Optional[int] = Field(default=None, description="Chapter of callback if found")
    callback_content: Optional[str] = Field(default=None, description="Callback content if found")


class CallbackMatch(BaseModel):
    """A match between foreshadowing plant and callback."""
    plant_chapter: int = Field(description="Chapter of plant")
    callback_chapter: int = Field(description="Chapter of callback")
    plant_content: str = Field(description="Planted content")
    callback_content: str = Field(description="Callback content")
    match_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Similarity score")
    quality: CallbackQuality = Field(default=CallbackQuality.ACCEPTABLE)
    is_thematic: bool = Field(default=False, description="Is this a thematic callback")
    is_character: bool = Field(default=False, description="Is this a character callback")
    is_plot: bool = Field(default=False, description="Is this a plot callback")
    connection_description: str = Field(default="", description="How they connect")


class ForeshadowingCheckResult(BaseModel):
    """Result of checking a single foreshadowing element."""
    foreshadowing_id: str = Field(description="Foreshadowing element ID")
    status: CallbackStatus = Field(description="Callback status")
    quality: CallbackQuality = Field(default=CallbackQuality.ACCEPTABLE)

    # Plant info
    plant_chapter: int = Field(description="Planted chapter")
    plant_content: str = Field(default="", description="Plant content")

    # Callback info
    callback_chapter: Optional[int] = Field(default=None, description="Callback chapter if found")
    callback_content: Optional[str] = Field(default=None, description="Callback content if found")
    callback_found: bool = Field(default=False, description="Whether callback was found")

    # Timing
    timing_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Timing appropriateness")
    timing_issue: Optional[str] = Field(default=None, description="Timing issue if any")

    # Quality metrics
    connection_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Plant-callback connection strength")
    thematic_alignment: float = Field(default=0.0, ge=0.0, le=1.0, description="Thematic alignment score")

    # Issues
    issues: list[str] = Field(default_factory=list, description="Issues found")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class ChapterForeshadowingProfile(BaseModel):
    """Foreshadowing profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Planted elements in this chapter
    plants: list[str] = Field(default_factory=list, description="IDs of elements planted")
    plant_count: int = Field(default=0, description="Number of plants")

    # Callbacks in this chapter
    callbacks: list[str] = Field(default_factory=list, description="IDs of callbacks")
    callback_count: int = Field(default=0, description="Number of callbacks")

    # Balance
    plant_callback_ratio: float = Field(default=0.0, ge=0.0, description="Ratio of plants to callbacks")
    foreshadowing_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall density")

    # Quality
    chapter_callback_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ForeshadowingCheckAnalysis(BaseModel):
    """Comprehensive analysis of all foreshadowing and callbacks."""
    # Overall scores
    overall_callback_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_foreshadowing_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Statistics
    total_planted: int = Field(default=0, description="Total foreshadowing elements planted")
    total_called_back: int = Field(default=0, description="Total properly called back")
    total_orphaned: int = Field(default=0, description="Total orphaned (not called back)")
    total_unplanted: int = Field(default=0, description="Total unplanted callbacks")

    # Payoff ratio
    payoff_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Ratio of planted to called back")

    # Per-chapter analysis
    chapter_profiles: list[ChapterForeshadowingProfile] = Field(default_factory=list)

    # Individual results
    check_results: list[ForeshadowingCheckResult] = Field(default_factory=list)

    # Matched pairs
    callback_matches: list[CallbackMatch] = Field(default_factory=list, description="All plant-callback pairs")

    # Issues
    issues: list[ForeshadowingCheckIssue] = Field(default_factory=list)

    # Orphaned foreshadowing
    orphaned_foreshadowing: list[str] = Field(default_factory=list, description="IDs of orphaned elements")
    orphaned_count: int = Field(default=0)

    # Quality distribution
    excellent_callbacks: int = Field(default=0)
    good_callbacks: int = Field(default=0)
    acceptable_callbacks: int = Field(default=0)
    weak_callbacks: int = Field(default=0)
    missing_callbacks: int = Field(default=0)

    # Timing issues
    premature_callbacks: int = Field(default=0)
    delayed_callbacks: int = Field(default=0)

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class ForeshadowingCheckRevision(BaseModel):
    """Revision for improving a foreshadowing callback."""
    foreshadowing_id: str = Field(description="Foreshadowing element ID")

    # What to add/revise
    suggested_plant_addition: str = Field(default="", description="Suggested plant text to add")
    suggested_callback_addition: str = Field(default="", description="Suggested callback text to add")
    suggested_improvement: str = Field(default="", description="Suggested improvement for existing")

    # Chapters affected
    plant_chapter: int = Field(description="Plant chapter")
    callback_chapter: int = Field(description="Callback chapter")

    # Quality improvement
    before_score: float = Field(description="Score before revision")
    after_score: float = Field(description="Estimated score after revision")

    # Changes
    changes_made: list[str] = Field(default_factory=list)


class ForeshadowingCheckPlan(BaseModel):
    """Plan for improving foreshadowing callbacks."""
    # Issues to address
    orphaned_to_address: list[str] = Field(default_factory=list, description="Orphaned IDs to add callbacks")
    weak_to_strengthen: list[str] = Field(default_factory=list, description="Weak callbacks to strengthen")
    timing_issues_to_fix: list[str] = Field(default_factory=list, description="Timing issues to address")

    # Priority order
    priority_order: list[tuple[str, int]] = Field(default_factory=list, description="(ID, priority) pairs")

    # Estimated work
    estimated_additions: int = Field(default=0, description="New callbacks to add")
    estimated_revisions: int = Field(default=0, description="Existing to revise")

    # AI assistance
    ai_generation: bool = Field(default=True, description="Use AI to generate additions")


class ForeshadowingCheckReport(BaseModel):
    """Final report for foreshadowing check."""
    analysis: ForeshadowingCheckAnalysis = Field(description="Complete analysis")
    revision_plan: ForeshadowingCheckPlan = Field(description="Plan for revisions")

    # Summary
    summary: str = Field(default="", description="Human-readable summary")

    # Revisions
    revisions_completed: list[ForeshadowingCheckRevision] = Field(default_factory=list)

    # Final status
    final_callback_score: Optional[float] = Field(default=None)
    improvement_achieved: Optional[float] = Field(default=None)