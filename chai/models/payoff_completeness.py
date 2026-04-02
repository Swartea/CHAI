"""Payoff completeness models for validating foreshadowing resolution quality."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PayoffCompletenessType(str, Enum):
    """Types of payoff completeness checks."""
    FULL_PAYOFF = "full_payoff"  # Completely resolved
    PARTIAL_PAYOFF = "partial_payoff"  # Incompletely resolved
    NO_PAYOFF = "no_payoff"  # Not resolved at all
    MULTI_STAGE_PAYOFF = "multi_stage_payoff"  # Resolved across multiple chapters
    THEMATIC_PAYOFF = "thematic_payoff"  # Thematic resolution
    EMOTIONAL_PAYOFF = "emotional_payoff"  # Emotional resolution
    PLOT_PAYOFF = "plot_payoff"  # Plot-level resolution


class PayoffCompletenessSeverity(str, Enum):
    """Severity of payoff completeness issues."""
    CRITICAL = "critical"  # Major element unresolved
    SEVERE = "severe"  # Important element poorly resolved
    MODERATE = "moderate"  # Some aspects unresolved
    MINOR = "minor"  # Minor completeness issue
    NONE = "none"  # No issue


class PayoffSatisfactionLevel(str, Enum):
    """How satisfying the payoff is."""
    EXCELLENT = "excellent"  # Highly satisfying payoff
    GOOD = "good"  # Satisfying payoff
    ACCEPTABLE = "acceptable"  # Adequate payoff
    WEAK = "weak"  # Weak, could be better
    DISAPPOINTING = "disappointing"  # Poor payoff


class PayoffCompletenessIssue(BaseModel):
    """An issue found during payoff completeness check."""
    issue_id: str = Field(description="Unique issue identifier")
    foreshadowing_id: str = Field(description="Related foreshadowing element ID")
    plant_chapter: int = Field(description="Chapter where planted")
    payoff_chapter: Optional[int] = Field(default=None, description="Chapter of payoff if found")
    issue_type: str = Field(description="Type of issue")
    severity: PayoffCompletenessSeverity = Field(description="Severity level")
    description: str = Field(description="Human-readable description")
    suggested_fix: str = Field(default="", description="Suggested fix")
    priority: int = Field(default=0, description="Priority for fixing")


class PlantedElementPayoff(BaseModel):
    """A planted foreshadowing element and its payoff status."""
    foreshadowing_id: str = Field(description="Unique identifier")
    plant_chapter: int = Field(description="Chapter where planted")
    plant_content: str = Field(description="The planted content")
    plant_context: str = Field(description="Surrounding context")

    # Payoff status
    has_payoff: bool = Field(default=False, description="Whether payoff exists")
    payoff_chapter: Optional[int] = Field(default=None, description="Chapter of payoff")
    payoff_content: Optional[str] = Field(default=None, description="Payoff content")

    # Completeness assessment
    completeness_type: PayoffCompletenessType = Field(default=PayoffCompletenessType.NO_PAYOFF)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="How complete the payoff is")
    satisfaction_level: PayoffSatisfactionLevel = Field(default=PayoffSatisfactionLevel.DISAPPOINTING)

    # Payoff quality metrics
    resolution_clarity: float = Field(default=0.0, ge=0.0, le=1.0, description="How clearly resolved")
    emotional_impact: float = Field(default=0.0, ge=0.0, le=1.0, description="Emotional impact of payoff")
    thematic_alignment: float = Field(default=0.0, ge=0.0, le=1.0, description="Thematic alignment")
    reader_expectation_met: float = Field(default=0.0, ge=0.0, le=1.0, description="Reader expectation fulfillment")

    # Issues
    issues: list[str] = Field(default_factory=list, description="Issues found")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class ChapterPayoffProfile(BaseModel):
    """Payoff profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Payoff elements in this chapter
    payoffs: list[str] = Field(default_factory=list, description="IDs of payoffs in this chapter")
    payoff_count: int = Field(default=0, description="Number of payoffs")
    plants: list[str] = Field(default_factory=list, description="IDs of plants in this chapter")
    plant_count: int = Field(default=0, description="Number of plants")

    # Balance metrics
    payoff_to_plant_ratio: float = Field(default=0.0, ge=0.0, description="Ratio of payoffs to plants")
    payoff_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall density")

    # Quality metrics
    avg_satisfaction_score: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    chapter_payoff_score: float = Field(default=0.0, ge=0.0, le=1.0)


class PayoffCompletenessAnalysis(BaseModel):
    """Comprehensive analysis of payoff completeness."""
    # Overall scores
    overall_completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_satisfaction_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Statistics
    total_plants: int = Field(default=0, description="Total foreshadowing elements planted")
    total_with_payoff: int = Field(default=0, description="Total with some payoff")
    total_full_payoff: int = Field(default=0, description="Total with complete payoff")
    total_partial_payoff: int = Field(default=0, description="Total with partial payoff")
    total_no_payoff: int = Field(default=0, description="Total with no payoff")

    # Payoff ratio
    payoff_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Ratio of plants with payoff")
    full_payoff_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Ratio of full payoffs")

    # Per-chapter analysis
    chapter_profiles: list[ChapterPayoffProfile] = Field(default_factory=list)

    # Individual results
    payoff_results: list[PlantedElementPayoff] = Field(default_factory=list)

    # Issues
    issues: list[PayoffCompletenessIssue] = Field(default_factory=list)

    # Unresolved elements
    unresolved_ids: list[str] = Field(default_factory=list, description="IDs of unresolved elements")
    unresolved_count: int = Field(default=0)

    # Partial payoffs
    partial_payoff_ids: list[str] = Field(default_factory=list, description="IDs of partial payoffs")
    partial_payoff_count: int = Field(default=0)

    # Quality distribution
    excellent_payoffs: int = Field(default=0)
    good_payoffs: int = Field(default=0)
    acceptable_payoffs: int = Field(default=0)
    weak_payoffs: int = Field(default=0)
    disappointing_payoffs: int = Field(default=0)

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class PayoffCompletenessRevision(BaseModel):
    """Revision for improving payoff completeness."""
    foreshadowing_id: str = Field(description="Foreshadowing element ID")

    # What to add/revise
    suggested_additions: str = Field(default="", description="Suggested payoff text to add")
    suggested_improvements: str = Field(default="", description="Suggested improvements")

    # Chapters affected
    plant_chapter: int = Field(description="Plant chapter")
    payoff_chapter: Optional[int] = Field(description="Payoff chapter")

    # Quality improvement
    before_score: float = Field(description="Score before revision")
    after_score: float = Field(description="Estimated score after revision")

    # Changes
    changes_made: list[str] = Field(default_factory=list)


class PayoffCompletenessPlan(BaseModel):
    """Plan for improving payoff completeness."""
    # Issues to address
    unresolved_to_address: list[str] = Field(default_factory=list, description="Unresolved IDs to add payoffs")
    partial_to_strengthen: list[str] = Field(default_factory=list, description="Partial payoffs to strengthen")
    weak_to_improve: list[str] = Field(default_factory=list, description="Weak payoffs to improve")

    # Priority order
    priority_order: list[tuple[str, int]] = Field(default_factory=list, description="(ID, priority) pairs")

    # Estimated work
    estimated_new_payoffs: int = Field(default=0, description="New payoffs to add")
    estimated_improvements: int = Field(default=0, description="Existing to improve")

    # AI assistance
    ai_generation: bool = Field(default=True, description="Use AI to generate additions")


class PayoffCompletenessReport(BaseModel):
    """Final report for payoff completeness check."""
    analysis: PayoffCompletenessAnalysis = Field(description="Complete analysis")
    revision_plan: PayoffCompletenessPlan = Field(description="Plan for revisions")

    # Summary
    summary: str = Field(default="", description="Human-readable summary")

    # Revisions
    revisions_completed: list[PayoffCompletenessRevision] = Field(default_factory=list)

    # Final status
    final_completeness_score: Optional[float] = Field(default=None)
    improvement_achieved: Optional[float] = Field(default=None)
