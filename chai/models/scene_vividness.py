"""Scene vividness models for validating scene description quality."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SceneVividnessType(str, Enum):
    """Types of scene vividness issues."""
    # Imagery issues
    VAGUE_IMAGERY = "vague_imagery"                    # Description is too abstract/generic
    ABSENT_VISUAL_DETAILS = "absent_visual_details"    # Missing visual specifics
    UNCLEAR_SPATIAL_LAYOUT = "unclear_spatial_layout"  # Reader can't picture arrangement

    # Sensory issues
    SINGLE_SENSE_OVERUSE = "single_sense_overuse"      # Only one sense dominates
    ABSENT_SENSORY_DETAILS = "absent_sensory_details"  # Missing sensory engagement
    SENSORY_IMBALANCE = "sensory_imbalance"           # Uneven sensory distribution

    # Show don't tell issues
    TELLING_INSTEAD_SHOWING = "telling_instead_showing"  # States emotions directly
    ABSTRACT_EMOTIONS = "abstract_emotions"           # "The room felt sad" without showing why
    OFF_STAGE_BACKGROUND = "off_stage_background"     # Off-stage behavior mentioned

    # Language issues
    CLICHE_DESCRIPTIONS = "cliche_descriptions"       # Overused, predictable phrases
    FILTER_WORDS = "filter_words"                     # "He saw", "She heard", "She felt"
    WEAK_ADJECTIVES = "weak_adjectives"               # Very, quite, rather, somewhat
    PASSIVE_VOICE_OVERUSE = "passive_voice_overuse"   # Too much passive construction

    # Structure issues
    LIST_LIKE_DESCRIPTION = "list_like_description"  # Sounds like a list of features
    NO_FOCAL_POINT = "no_focal_point"                # No clear point of focus
    TANGENT_DETAILS = "tangent_details"               # Irrelevant details distract

    # Contrast/comparison issues
    MISSING_CONTRASTS = "missing_contrasts"          # No juxtaposition for impact
    METAPHOR_MISSING = "metaphor_missing"            # No vivid comparisons


class SceneVividnessSeverity(str, Enum):
    """Severity of scene vividness issues."""
    MINOR = "minor"           # Small improvement suggestions
    MODERATE = "moderate"   # Should be addressed
    SEVERE = "severe"       # Breaks immersion, must fix


class ImageryClarity(str, Enum):
    """How clear the imagery is in scene description."""
    UNCLEAR = "unclear"      # Reader struggles to picture scene
    FUZZY = "fuzzy"          # Vague, general impression
    ADEQUATE = "adequate"    # Basic picture forms
    CLEAR = "clear"          # Clear mental image
    VIVID = "vivid"         # Strong, engaging visual


class SensoryEngagement(str, Enum):
    """Level of sensory engagement in scene."""
    NONE = "none"            # No sensory details
    MINIMAL = "minimal"      # Only one sense
    MODERATE = "moderate"    # 2-3 senses engaged
    RICH = "rich"           # Full sensory engagement


class ShowDontTellLevel(str, Enum):
    """How well show don't tell is applied."""
    MOSTLY_TELLING = "mostly_telling"   # Direct statements of emotion/state
    PARTIAL_SHOWING = "partial_showing"  # Some showing, some telling
    MOSTLY_SHOWING = "mostly_showing"   # Mostly shows, little telling
    EXCELLENT = "excellent"            # Excellent showing, immersive


class SceneVividnessIssue(BaseModel):
    """A specific vividness issue found in scene description."""
    issue_type: SceneVividnessType = Field(
        description="Type of vividness issue"
    )
    severity: SceneVividnessSeverity = Field(
        description="Severity of the issue"
    )
    location: str = Field(
        description="Where in the text the issue occurs"
    )
    description: str = Field(
        description="Description of the issue"
    )
    example: Optional[str] = Field(
        default=None,
        description="Example from text demonstrating the issue"
    )
    suggestion: str = Field(
        description="How to fix the issue"
    )


class VisualDetailCheck(BaseModel):
    """Check results for visual details."""
    has_color_details: bool = Field(
        default=False,
        description="Whether color specifics are present"
    )
    has_texture_details: bool = Field(
        default=False,
        description="Whether texture/surface details are present"
    )
    has_size_scale: bool = Field(
        default=False,
        description="Whether scale/size is conveyed"
    )
    has_light_shadow: bool = Field(
        default=False,
        description="Whether light and shadow are described"
    )
    has_spatial_arrangement: bool = Field(
        default=False,
        description="Whether spatial layout is clear"
    )
    has_focal_point: bool = Field(
        default=False,
        description="Whether there's a clear focal point"
    )
    color_word_count: int = Field(
        default=0,
        description="Number of color-specific words used"
    )
    visual_verb_count: int = Field(
        default=0,
        description="Number of visual/action verbs used"
    )


class SensoryDetailCheck(BaseModel):
    """Check results for sensory details."""
    visual_count: int = Field(
        default=0,
        description="Visual sensory details count"
    )
    auditory_count: int = Field(
        default=0,
        description="Auditory sensory details count"
    )
    tactile_count: int = Field(
        default=0,
        description="Tactile sensory details count"
    )
    olfactory_count: int = Field(
        default=0,
        description="Olfactory sensory details count"
    )
    gustatory_count: int = Field(
        default=0,
        description="Gustatory sensory details count"
    )
    sense_diversity_score: float = Field(
        default=0.0,
        description="Score 0-1 for sense diversity"
    )


class ShowDontTellCheck(BaseModel):
    """Check results for show don't tell patterns."""
    telling_phrases: list[str] = Field(
        default_factory=list,
        description="Direct statements that tell instead of show"
    )
    showing_count: int = Field(
        default=0,
        description="Effective showing examples"
    )
    telling_count: int = Field(
        default=0,
        description="Telling instances"
    )
    showing_ratio: float = Field(
        default=0.0,
        description="Ratio of showing to total (0-1)"
    )


class LanguageQualityCheck(BaseModel):
    """Check results for language quality."""
    filter_word_count: int = Field(
        default=0,
        description="Filter words like 'saw', 'heard', 'felt'"
    )
    weak_adjective_count: int = Field(
        default=0,
        description="Weak qualifiers: very, quite, rather"
    )
    cliche_count: int = Field(
        default=0,
        description="Cliche phrases detected"
    )
    passive_voice_count: int = Field(
        default=0,
        description="Passive voice constructions"
    )
    concrete_word_ratio: float = Field(
        default=0.0,
        description="Ratio of concrete to abstract words (0-1)"
    )


class SceneVividnessProfile(BaseModel):
    """Complete vividness profile for a scene description."""
    scene_id: str = Field(
        description="Scene identifier"
    )
    word_count: int = Field(
        default=0,
        description="Total word count"
    )

    # Overall scores
    vividness_score: float = Field(
        default=0.0,
        description="Overall vividness score 0-1"
    )
    imagery_clarity: ImageryClarity = Field(
        default=ImageryClarity.ADEQUATE,
        description="Imagery clarity level"
    )
    sensory_engagement: SensoryEngagement = Field(
        default=SensoryEngagement.MODERATE,
        description="Sensory engagement level"
    )
    show_dont_tell_level: ShowDontTellLevel = Field(
        default=ShowDontTellLevel.PARTIAL_SHOWING,
        description="Show don't tell level"
    )

    # Detailed checks
    visual_details: VisualDetailCheck = Field(
        default_factory=VisualDetailCheck,
        description="Visual detail analysis"
    )
    sensory_details: SensoryDetailCheck = Field(
        default_factory=SensoryDetailCheck,
        description="Sensory detail analysis"
    )
    show_dont_tell: ShowDontTellCheck = Field(
        default_factory=ShowDontTellCheck,
        description="Show don't tell analysis"
    )
    language_quality: LanguageQualityCheck = Field(
        default_factory=LanguageQualityCheck,
        description="Language quality analysis"
    )

    # Issues found
    issues: list[SceneVividnessIssue] = Field(
        default_factory=list,
        description="Vividness issues found"
    )

    # Strengths
    strengths: list[str] = Field(
        default_factory=list,
        description="Vividness strengths"
    )


class SceneVividnessAnalysis(BaseModel):
    """Analysis result for scene vividness."""
    scene_id: str = Field(
        description="Scene identifier"
    )
    profile: SceneVividnessProfile = Field(
        description="Vividness profile"
    )

    # Summary metrics
    overall_vividness: float = Field(
        default=0.0,
        description="Overall vividness score 0-1"
    )
    visual_imagery_score: float = Field(
        default=0.0,
        description="Visual imagery effectiveness 0-1"
    )
    sensory_balance_score: float = Field(
        default=0.0,
        description="Sensory balance 0-1"
    )
    show_dont_tell_score: float = Field(
        default=0.0,
        description="Show don't tell effectiveness 0-1"
    )
    language_quality_score: float = Field(
        default=0.0,
        description="Language quality 0-1"
    )

    # Statistics
    total_issues: int = Field(
        default=0,
        description="Total vividness issues found"
    )
    minor_issues: int = Field(
        default=0,
        description="Minor issues count"
    )
    moderate_issues: int = Field(
        default=0,
        description="Moderate issues count"
    )
    severe_issues: int = Field(
        default=0,
        description="Severe issues count"


    )
    issue_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues by type"
    )


class SceneVividnessRevision(BaseModel):
    """Revision plan for improving scene vividness."""
    original_scene_id: str = Field(
        description="Scene identifier"
    )
    revision_notes: list[str] = Field(
        default_factory=list,
        description="What to revise"
    )
    priority_fixes: list[str] = Field(
        default_factory=list,
        description="High priority fixes"
    )
    suggested_additions: list[str] = Field(
        default_factory=list,
        description="What to add for more vividness"
    )
    suggested_cuts: list[str] = Field(
        default_factory=list,
        description="What to remove or revise"
    )
    revised_description: Optional[str] = Field(
        default=None,
        description="Revised scene description (if AI-assisted)"
    )


class SceneVividnessReport(BaseModel):
    """Comprehensive vividness report for a chapter or manuscript."""
    chapter_id: Optional[str] = Field(
        default=None,
        description="Chapter identifier if chapter-level"
    )
    manuscript_id: Optional[str] = Field(
        default=None,
        description="Manuscript identifier if full manuscript"
    )

    # Scene profiles
    scene_profiles: list[SceneVividnessProfile] = Field(
        default_factory=list,
        description="Vividness profile for each scene"
    )

    # Aggregate scores
    average_vividness: float = Field(
        default=0.0,
        description="Average vividness score across scenes"
    )
    vividness_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of scenes by vividness level"
    )

    # Issue summary
    total_issues: int = Field(
        default=0,
        description="Total issues across all scenes"
    )
    most_common_issues: list[tuple[str, int]] = Field(
        default_factory=list,
        description="Most common issue types"
    )

    # Recommendations
    recommendations: list[str] = Field(
        default_factory=list,
        description="Overall recommendations"
    )

    # Chapter averages
    scene_count: int = Field(
        default=0,
        description="Number of scenes analyzed"
    )
    vivid_scene_count: int = Field(
        default=0,
        description="Number of vivid scenes (score > 0.7)"
    )
    dull_scene_count: int = Field(
        default=0,
        description="Number of dull scenes (score < 0.4)"
    )


class SceneVividnessTemplate(str, Enum):
    """Templates for scene vividness standards."""
    MINIMAL = "minimal"           # Basic vividness
    STANDARD = "standard"         # Good vividness
    CINEMATIC = "cinematic"       # Highly vivid, film-like
    LITERARY = "literary"         # Literary prose quality
