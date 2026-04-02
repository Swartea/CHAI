"""Tone unification models for maintaining consistent tone across the full manuscript."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ToneUnificationType(str, Enum):
    """Types of tone to unify across the manuscript."""
    EMOTIONAL_TONE = "emotional_tone"  # Overall emotional register
    NARRATIVE_TONE = "narrative_tone"   # Narrative voice and style
    ATMOSPHERIC_TONE = "atmospheric_tone"  # Scene atmosphere consistency
    DIALOGUE_TONE = "dialogue_tone"    # Dialogue consistency across characters
    DESCRIPTIVE_TONE = "descriptive_tone"  # Descriptive language consistency


class ToneShiftType(str, Enum):
    """Types of tone shifts detected."""
    GRADUAL_SHIFT = "gradual_shift"  # Slow, gradual change over chapters
    ABRUPT_SHIFT = "abrupt_shift"    # Sudden change between chapters
    CYCLICAL_SHIFT = "cyclical_shift"  # Repeating pattern of shifts
    REGIONAL_DRIFT = "regional_drift"  # Drift localized to certain chapters
    CHARACTER_VOICE_SHIFT = "character_voice_shift"  # Character dialogue inconsistency


class ToneShiftSeverity(str, Enum):
    """Severity of tone shift."""
    NEGLIGIBLE = "negligible"  # Barely noticeable, acceptable variation
    MINOR = "minor"            # Small shift, noticeable to careful reader
    MODERATE = "moderate"      # Clear shift, affects reading experience
    SEVERE = "severe"          # Major shift, disrupts continuity
    CRITICAL = "critical"      # Complete tonal break, jarring


class ChapterToneProfile(BaseModel):
    """Tone profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Emotional tone
    emotional_intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Overall emotional intensity (0-1)"
    )
    emotional_valence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Emotional valence positive/negative (0-1)"
    )

    # Tone markers
    tone_markers: dict[str, float] = Field(
        default_factory=dict,
        description="Tone marker frequencies as {marker: frequency}"
    )

    # Language characteristics
    sentence_avg_length: float = Field(
        default=20.0,
        description="Average sentence length in characters"
    )
    paragraph_avg_length: float = Field(
        default=150.0,
        description="Average paragraph length in characters"
    )
    dialogue_ratio: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Ratio of dialogue to narration"
    )

    # Vocabulary metrics
    vocabulary_sophistication: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Vocabulary sophistication level"
    )

    # Atmosphere
    primary_atmosphere: str = Field(
        default="neutral",
        description="Primary atmospheric tone"
    )
    atmosphere_shifts: list[str] = Field(
        default_factory=list,
        description="Atmosphere changes within chapter"
    )

    # Tone consistency score for this chapter (compared to overall)
    consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How consistent this chapter is with the unified tone"
    )


class ToneShift(BaseModel):
    """Represents a detected tone shift between chapters."""
    shift_id: str = Field(description="Unique identifier for this shift")

    # Location
    start_chapter: int = Field(description="Chapter where shift begins")
    end_chapter: int = Field(description="Chapter where shift ends")

    # Type and severity
    shift_type: ToneShiftType = Field(description="Type of shift")
    severity: ToneShiftSeverity = Field(description="Severity of the shift")

    # Description
    description: str = Field(description="Human-readable description of the shift")

    # Metrics
    magnitude: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Magnitude of the shift (0-1)"
    )

    # Cause analysis
    likely_cause: Optional[str] = Field(
        default=None,
        description="Likely cause of the shift"
    )

    # Affected aspects
    affected_aspects: list[ToneUnificationType] = Field(
        default_factory=list,
        description="Aspects of tone that shifted"
    )


class UnifiedToneProfile(BaseModel):
    """The target unified tone profile for the entire manuscript."""
    # Target tone values
    target_emotional_intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Target emotional intensity"
    )
    target_emotional_valence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Target emotional valence"
    )

    # Acceptable ranges
    intensity_range: tuple[float, float] = Field(
        default=(0.3, 0.7),
        description="Acceptable range for emotional intensity"
    )
    valence_range: tuple[float, float] = Field(
        default=(0.3, 0.7),
        description="Acceptable range for emotional valence"
    )

    # Language targets
    target_sentence_avg_length: float = Field(
        default=20.0,
        description="Target average sentence length"
    )
    sentence_length_range: tuple[float, float] = Field(
        default=(15.0, 30.0),
        description="Acceptable sentence length range"
    )

    target_paragraph_avg_length: float = Field(
        default=150.0,
        description="Target average paragraph length"
    )
    paragraph_length_range: tuple[float, float] = Field(
        default=(100.0, 200.0),
        description="Acceptable paragraph length range"
    )

    target_dialogue_ratio: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Target dialogue ratio"
    )
    dialogue_ratio_range: tuple[float, float] = Field(
        default=(0.2, 0.4),
        description="Acceptable dialogue ratio range"
    )

    target_vocabulary_sophistication: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Target vocabulary sophistication"
    )

    # Atmosphere targets
    target_atmosphere: str = Field(
        default="neutral",
        description="Primary target atmosphere"
    )
    allowed_atmospheres: list[str] = Field(
        default_factory=list,
        description="Allowed atmospheric variations"
    )

    # Tone to emphasize
    emphasized_tones: list[str] = Field(
        default_factory=list,
        description="Tones to emphasize throughout"
    )
    avoided_tones: list[str] = Field(
        default_factory=list,
        description="Tones to avoid"
    )


class ToneUnificationAnalysis(BaseModel):
    """Comprehensive tone unification analysis for the entire manuscript."""
    # Overall status
    overall_uniformity_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall tone uniformity score"
    )

    # Chapter profiles
    chapter_profiles: list[ChapterToneProfile] = Field(
        default_factory=list,
        description="Tone profile for each chapter"
    )

    # Unified tone profile
    unified_tone_profile: UnifiedToneProfile = Field(
        description="Target unified tone profile"
    )

    # Detected shifts
    detected_shifts: list[ToneShift] = Field(
        default_factory=list,
        description="All detected tone shifts"
    )

    # Most problematic chapters
    problematic_chapters: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Chapters with lowest consistency (chapter_num, score)"
    )

    # Statistics
    total_chapters_analyzed: int = Field(
        default=0,
        description="Total number of chapters analyzed"
    )
    chapters_with_shifts: int = Field(
        default=0,
        description="Number of chapters with detected shifts"
    )
    average_consistency: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Average consistency across all chapters"
    )

    # Recommendations
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improving tone uniformity"
    )


class ToneUnificationRevision(BaseModel):
    """Revision plan for unifying tone across chapters."""
    original_content: str = Field(description="Original chapter content")
    revised_content: str = Field(description="Revised content with unified tone")
    chapter_number: int = Field(description="Chapter number")

    # Changes made
    changes_made: list[str] = Field(
        default_factory=list,
        description="Description of changes made"
    )

    # Consistency improvement
    before_score: float = Field(
        description="Consistency score before revision"
    )
    after_score: float = Field(
        description="Consistency score after revision"
    )

    # Specific issues addressed
    issues_addressed: list[str] = Field(
        default_factory=list,
        description="Tone issues that were addressed"
    )
    issues_remaining: list[str] = Field(
        default_factory=list,
        description="Tone issues that still need attention"
    )


class ToneUnificationPlan(BaseModel):
    """Plan for tone unification across the manuscript."""
    target_profile: UnifiedToneProfile = Field(
        description="Target unified tone profile"
    )

    chapters_to_revise: list[int] = Field(
        default_factory=list,
        description="List of chapter numbers to revise"
    )

    priority_order: list[int] = Field(
        default_factory=list,
        description="Priority order for revision"
    )

    estimated_revisions: int = Field(
        default=0,
        description="Estimated number of revisions needed"
    )

    ai_polishing_enabled: bool = Field(
        default=True,
        description="Whether AI polishing is enabled"
    )


class ToneUnificationReport(BaseModel):
    """Final report for tone unification."""
    analysis: ToneUnificationAnalysis = Field(
        description="Complete tone analysis"
    )
    revision_plan: ToneUnificationPlan = Field(
        description="Plan for revisions"
    )

    # Summary
    summary: str = Field(
        default="",
        description="Human-readable summary"
    )

    # Chapters revised
    revisions_completed: list[ToneUnificationRevision] = Field(
        default_factory=list,
        description="Revisions that were completed"
    )

    # Final status
    final_uniformity_score: Optional[float] = Field(
        default=None,
        description="Final uniformity score after revisions"
    )
    improvement_achieved: Optional[float] = Field(
        default=None,
        description="Improvement in uniformity achieved"
    )