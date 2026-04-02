"""Description density models for balancing descriptive detail throughout the novel."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DescriptionDensityType(str, Enum):
    """Types of description density to analyze."""
    ENVIRONMENT = "environment"                    # Environment/scene description
    ACTION = "action"                             # Action sequence description
    DIALOGUE = "dialogue"                         # Dialogue proportion
    INTERNAL_THOUGHT = "internal_thought"         # Internal thought/narration
    SENSORY = "sensory"                           # Sensory detail (sight, sound, smell, etc.)
    EMOTIONAL = "emotional"                       # Emotional/internal experience
    CHARACTER = "character"                       # Character appearance/behavior description
    BACKSTORY = "backstory"                       # Background/flashback content


class DescriptionDensityLevel(str, Enum):
    """Levels of description density."""
    SPARSE = "sparse"                            # Minimal description
    LIGHT = "light"                              # Light description
    MODERATE = "moderate"                        # Balanced description
    RICH = "rich"                                # Rich description
    EXCESSIVE = "excessive"                       # Too much description


class DescriptionBalanceStatus(str, Enum):
    """Status of description density balance."""
    BALANCED = "balanced"                         # Well balanced
    SLIGHTLY_UNEVEN = "slightly_uneven"          # Minor imbalance
    UNEVEN = "uneven"                            # Significant imbalance
    SEVERELY_UNEVEN = "severely_uneven"          # Serious imbalance


class SceneDescriptionMetrics(BaseModel):
    """Metrics for a single scene's description."""
    scene_id: str = Field(description="Scene identifier")
    scene_title: str = Field(default="", description="Scene title")
    scene_type: str = Field(default="", description="Type of scene")
    total_characters: int = Field(default=0, description="Total character count")
    environment_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Environment description ratio")
    action_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Action description ratio")
    dialogue_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Dialogue ratio")
    internal_thought_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Internal thought ratio")
    sensory_detail_count: int = Field(default=0, description="Count of sensory details")
    emotional_markers: int = Field(default=0, description="Count of emotional markers")
    avg_sentence_length: float = Field(default=0.0, description="Average sentence length in characters")
    paragraph_count: int = Field(default=0, description="Number of paragraphs")
    avg_paragraph_length: float = Field(default=0.0, description="Average paragraph length")


class ChapterDensityProfile(BaseModel):
    """Description density profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")
    total_words: int = Field(default=0, description="Total word count")

    # Overall density assessment
    overall_density: DescriptionDensityLevel = Field(
        default=DescriptionDensityLevel.MODERATE,
        description="Overall description density level"
    )
    balance_status: DescriptionBalanceStatus = Field(
        default=DescriptionBalanceStatus.BALANCED,
        description="Balance status across description types"
    )

    # Individual density metrics
    environment_density: float = Field(
        default=0.15, ge=0.0, le=1.0,
        description="Environment description ratio (0.0-1.0)"
    )
    action_density: float = Field(
        default=0.20, ge=0.0, le=1.0,
        description="Action description ratio (0.0-1.0)"
    )
    dialogue_density: float = Field(
        default=0.30, ge=0.0, le=1.0,
        description="Dialogue ratio (0.0-1.0)"
    )
    internal_thought_density: float = Field(
        default=0.15, ge=0.0, le=1.0,
        description="Internal thought ratio (0.0-1.0)"
    )
    sensory_density: float = Field(
        default=0.10, ge=0.0, le=1.0,
        description="Sensory detail ratio (0.0-1.0)"
    )
    emotional_density: float = Field(
        default=0.10, ge=0.0, le=1.0,
        description="Emotional expression ratio (0.0-1.0)"
    )

    # Scene-level breakdown
    scene_metrics: list[SceneDescriptionMetrics] = Field(
        default_factory=list,
        description="Per-scene description metrics"
    )

    # Descriptive markers
    descriptive_word_count: int = Field(
        default=0,
        description="Count of descriptive words (adjectives, adverbs)"
    )
    sensory_detail_count: int = Field(
        default=0,
        description="Count of sensory details"
    )
    action_verb_count: int = Field(
        default=0,
        description="Count of action verbs"
    )

    # Calculated scores
    density_score: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Overall density consistency score (0.0-1.0)"
    )
    balance_score: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Balance score across description types"
    )

    # Issues found
    density_issues: list[str] = Field(
        default_factory=list,
        description="Description density issues found"
    )


class DensityShift(BaseModel):
    """Represents a shift in description density between chapters."""
    shift_id: str = Field(description="Unique shift identifier")
    start_chapter: int = Field(description="Starting chapter number")
    end_chapter: int = Field(description="Ending chapter number")
    shift_type: str = Field(description="Type of shift (increase/decrease/oscillation)")
    severity: str = Field(description="Severity: minor, moderate, severe")
    description: str = Field(description="Human-readable description")
    magnitude: float = Field(default=0.0, description="Magnitude of the shift")
    affected_aspects: list[DescriptionDensityType] = Field(
        default_factory=list,
        description="Which aspects are affected"
    )
    likely_cause: str = Field(default="", description="Likely cause of the shift")


class UnifiedDensityProfile(BaseModel):
    """Target unified density profile for the entire novel."""
    # Target values
    target_overall_density: DescriptionDensityLevel = Field(
        default=DescriptionDensityLevel.MODERATE,
        description="Target overall density"
    )
    target_environment_density: float = Field(
        default=0.15, ge=0.0, le=1.0,
        description="Target environment density"
    )
    target_action_density: float = Field(
        default=0.20, ge=0.0, le=1.0,
        description="Target action density"
    )
    target_dialogue_density: float = Field(
        default=0.30, ge=0.0, le=1.0,
        description="Target dialogue density"
    )
    target_internal_thought_density: float = Field(
        default=0.15, ge=0.0, le=1.0,
        description="Target internal thought density"
    )
    target_sensory_density: float = Field(
        default=0.10, ge=0.0, le=1.0,
        description="Target sensory density"
    )
    target_emotional_density: float = Field(
        default=0.10, ge=0.0, le=1.0,
        description="Target emotional density"
    )

    # Allowed ranges (tolerance)
    environment_range: tuple[float, float] = Field(
        default=(0.10, 0.20),
        description="Allowed range for environment density"
    )
    action_range: tuple[float, float] = Field(
        default=(0.15, 0.25),
        description="Allowed range for action density"
    )
    dialogue_range: tuple[float, float] = Field(
        default=(0.25, 0.40),
        description="Allowed range for dialogue density"
    )
    internal_thought_range: tuple[float, float] = Field(
        default=(0.10, 0.20),
        description="Allowed range for internal thought density"
    )
    sensory_range: tuple[float, float] = Field(
        default=(0.05, 0.15),
        description="Allowed range for sensory density"
    )
    emotional_range: tuple[float, float] = Field(
        default=(0.05, 0.15),
        description="Allowed range for emotional density"
    )


class DescriptionDensityAnalysis(BaseModel):
    """Comprehensive description density analysis for the novel."""
    total_chapters_analyzed: int = Field(
        default=0,
        description="Total number of chapters analyzed"
    )
    chapter_profiles: list[ChapterDensityProfile] = Field(
        default_factory=list,
        description="Per-chapter density profiles"
    )
    unified_profile: UnifiedDensityProfile = Field(
        default=UnifiedDensityProfile(),
        description="Target unified density profile"
    )
    detected_shifts: list[DensityShift] = Field(
        default_factory=list,
        description="Density shifts detected between chapters"
    )
    problematic_chapters: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Chapters with issues (chapter_num, score)"
    )

    # Overall scores
    overall_density_score: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Overall density consistency score"
    )
    overall_balance_score: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Overall balance score"
    )
    uniformity_score: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Overall uniformity across the novel"
    )

    # Statistics
    avg_chapter_words: float = Field(
        default=0.0,
        description="Average words per chapter"
    )
    density_variance: float = Field(
        default=0.0,
        description="Variance in density across chapters"
    )

    # Recommendations
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class DescriptionDensityRevision(BaseModel):
    """Revision of content for description density balance."""
    original_content: str = Field(description="Original content")
    revised_content: str = Field(description="Revised content")
    chapter_number: int = Field(description="Chapter number")
    changes_made: list[str] = Field(
        default_factory=list,
        description="Description of changes made"
    )
    before_score: float = Field(
        default=0.0,
        description="Density score before revision"
    )
    after_score: float = Field(
        default=0.0,
        description="Density score after revision"
    )
    issues_addressed: list[str] = Field(
        default_factory=list,
        description="Issues that were addressed"
    )
    issues_remaining: list[str] = Field(
        default_factory=list,
        description="Issues that still need attention"
    )


class DescriptionDensityPlan(BaseModel):
    """Plan for revising content to achieve description density balance."""
    target_profile: UnifiedDensityProfile = Field(
        description="Target density profile"
    )
    chapters_to_revise: list[int] = Field(
        default_factory=list,
        description="Chapters that need revision"
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


class DescriptionDensityReport(BaseModel):
    """Comprehensive report on description density analysis."""
    analysis: DescriptionDensityAnalysis = Field(
        description="Full analysis results"
    )
    revision_plan: DescriptionDensityPlan = Field(
        description="Revision plan"
    )
    summary: str = Field(
        default="",
        description="Human-readable summary"
    )


class DescriptionDensityTemplate(BaseModel):
    """Template for description density configuration by genre/scene type."""
    template_name: str = Field(description="Template name")
    template_description: str = Field(description="Template description")
    applicable_genres: list[str] = Field(
        default_factory=list,
        description="Applicable genre types"
    )
    applicable_scene_types: list[str] = Field(
        default_factory=list,
        description="Applicable scene types"
    )

    # Target densities for this template
    environment_density: float = Field(default=0.15, ge=0.0, le=1.0)
    action_density: float = Field(default=0.20, ge=0.0, le=1.0)
    dialogue_density: float = Field(default=0.30, ge=0.0, le=1.0)
    internal_thought_density: float = Field(default=0.15, ge=0.0, le=1.0)
    sensory_density: float = Field(default=0.10, ge=0.0, le=1.0)
    emotional_density: float = Field(default=0.10, ge=0.0, le=1.0)

    # Pacing modifiers
    fast_paced_modifier: float = Field(
        default=0.8,
        description="Multiplier for fast-paced scenes"
    )
    slow_paced_modifier: float = Field(
        default=1.2,
        description="Multiplier for slow-paced scenes"
    )

    def to_unified_profile(self) -> UnifiedDensityProfile:
        """Convert template to UnifiedDensityProfile."""
        return UnifiedDensityProfile(
            target_environment_density=self.environment_density,
            target_action_density=self.action_density,
            target_dialogue_density=self.dialogue_density,
            target_internal_thought_density=self.internal_thought_density,
            target_sensory_density=self.sensory_density,
            target_emotional_density=self.emotional_density,
            environment_range=(
                max(0.05, self.environment_density * 0.7),
                min(0.30, self.environment_density * 1.3),
            ),
            action_range=(
                max(0.05, self.action_density * 0.7),
                min(0.40, self.action_density * 1.3),
            ),
            dialogue_range=(
                max(0.15, self.dialogue_density * 0.7),
                min(0.50, self.dialogue_density * 1.3),
            ),
            internal_thought_range=(
                max(0.05, self.internal_thought_density * 0.7),
                min(0.30, self.internal_thought_density * 1.3),
            ),
            sensory_range=(
                max(0.02, self.sensory_density * 0.7),
                min(0.25, self.sensory_density * 1.3),
            ),
            emotional_range=(
                max(0.02, self.emotional_density * 0.7),
                min(0.25, self.emotional_density * 1.3),
            ),
        )
