"""Chapter word count models for validating 2000-4000 character target."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WordCountStatus(str, Enum):
    """Status of chapter word count validation."""
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    ACCEPTABLE = "acceptable"
    OPTIMAL = "optimal"


class WordCountSeverity(str, Enum):
    """Severity of word count deviation."""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class ChapterWordCountProfile(BaseModel):
    """Word count profile for a single chapter."""

    chapter_id: str = Field(description="Unique chapter ID")
    chapter_number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")

    # Actual word count
    actual_word_count: int = Field(default=0, description="Actual word count")

    # Target range (2000-4000)
    min_target: int = Field(default=2000, description="Minimum target word count")
    max_target: int = Field(default=4000, description="Maximum target word count")
    optimal_target: int = Field(default=3000, description="Optimal target word count")

    # Deviation metrics
    deviation_from_min: int = Field(default=0, description="Words below min target")
    deviation_from_max: int = Field(default=0, description="Words above max target")
    deviation_from_optimal: int = Field(default=0, description="Words from optimal")

    # Ratios
    ratio_to_min: float = Field(default=0.0, description="Actual / min target ratio")
    ratio_to_max: float = Field(default=0.0, description="Actual / max target ratio")
    ratio_to_optimal: float = Field(default=0.0, description="Actual / optimal target ratio")

    # Status
    status: WordCountStatus = Field(
        default=WordCountStatus.ACCEPTABLE,
        description="Word count status"
    )
    severity: WordCountSeverity = Field(
        default=WordCountSeverity.NONE,
        description="Deviation severity"
    )

    # Analysis
    is_within_target: bool = Field(
        default=True,
        description="Is word count within target range"
    )
    percent_of_target: float = Field(
        default=0.0,
        description="Actual as percentage of optimal target"
    )


class ChapterWordCountIssue(BaseModel):
    """Issue identified with chapter word count."""

    chapter_id: str = Field(description="Chapter ID")
    chapter_number: int = Field(description="Chapter number")

    # Issue details
    issue_type: str = Field(description="Type: too_short, too_long, unbalanced")
    severity: WordCountSeverity = Field(description="Issue severity")

    # Specifics
    actual_word_count: int = Field(description="Actual word count")
    expected_word_count: int = Field(description="Expected word count")
    deviation: int = Field(description="Deviation in words")
    deviation_percent: float = Field(description="Deviation as percentage")

    # Recommendations
    words_to_add: Optional[int] = Field(
        default=None,
        description="Words to add if too short"
    )
    words_to_remove: Optional[int] = Field(
        default=None,
        description="Words to remove if too long"
    )
    recommendation: str = Field(description="Recommendation text")


class ChapterWordCountAnalysis(BaseModel):
    """Analysis of chapter word count quality."""

    novel_id: str = Field(description="Novel ID")

    # Per-chapter profiles
    chapter_profiles: list[ChapterWordCountProfile] = Field(
        default_factory=list,
        description="Word count profiles per chapter"
    )

    # Aggregated statistics
    total_chapters: int = Field(default=0, description="Total chapters analyzed")
    chapters_within_target: int = Field(default=0, description="Chapters within target range")
    chapters_too_short: int = Field(default=0, description="Chapters below minimum")
    chapters_too_long: int = Field(default=0, description="Chapters above maximum")

    # Overall statistics
    average_word_count: float = Field(default=0.0, description="Average word count")
    median_word_count: float = Field(default=0.0, description="Median word count")
    min_word_count: int = Field(default=0, description="Minimum word count")
    max_word_count: int = Field(default=0, description="Maximum word count")
    total_word_count: int = Field(default=0, description="Total word count across all chapters")

    # Variance analysis
    word_count_variance: float = Field(default=0.0, description="Variance in word counts")
    word_count_std_dev: float = Field(default=0.0, description="Standard deviation")
    is_consistent: bool = Field(default=True, description="Are chapters consistent")

    # Quality scores
    compliance_score: float = Field(
        default=1.0,
        description="Percentage of chapters within target (0-1)"
    )
    consistency_score: float = Field(
        default=1.0,
        description="Consistency score (0-1)"
    )
    overall_score: float = Field(
        default=1.0,
        description="Overall word count quality score (0-1)"
    )

    # Issues
    issues: list[ChapterWordCountIssue] = Field(
        default_factory=list,
        description="Identified issues"
    )

    # Recommendations
    recommendations: list[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )


class ChapterWordCountRevision(BaseModel):
    """Revision plan for word count issues."""

    chapter_id: str = Field(description="Chapter ID")
    chapter_number: int = Field(description="Chapter number")

    # Current state
    current_word_count: int = Field(description="Current word count")
    target_range: tuple[int, int] = Field(
        description="Target range (min, max)"
    )

    # Revision type
    needs_expansion: bool = Field(
        default=False,
        description="Does chapter need to be expanded"
    )
    needs_contraction: bool = Field(
        default=False,
        description="Does chapter need to be shortened"
    )

    # Target adjustments
    words_to_add: int = Field(
        default=0,
        description="Words to add"
    )
    words_to_remove: int = Field(
        default=0,
        description="Words to remove"
    )

    # Section-level suggestions
    section_suggestions: list[dict] = Field(
        default_factory=list,
        description="Suggestions per section for word count adjustment"
    )

    # Priority
    priority: int = Field(
        default=2,
        description="Priority (1=high, 2=medium, 3=low)"
    )


class ChapterWordCountReport(BaseModel):
    """Comprehensive word count report for novel."""

    novel_id: str = Field(description="Novel ID")
    novel_title: str = Field(description="Novel title")

    # Analysis results
    analysis: ChapterWordCountAnalysis = Field(
        description="Word count analysis"
    )

    # Revision plans
    revision_plans: list[ChapterWordCountRevision] = Field(
        default_factory=list,
        description="Revision plans for chapters with issues"
    )

    # Summary
    summary: str = Field(description="Human-readable summary")
    passed: bool = Field(default=True, description="Whether all chapters pass target")

    # Metadata
    total_chapters: int = Field(default=0)
    chapters_needing_revision: int = Field(default=0)
    estimated_revision_time: str = Field(
        default="0 minutes",
        description="Estimated time for revisions"
    )