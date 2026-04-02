"""Chapter transition models for ensuring smooth transitions between chapters."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TransitionType(str, Enum):
    """Types of transitions between chapters."""
    SCENE_CONTINUATION = "scene_continuation"  # Same scene, continues naturally
    SCENE_SWITCH = "scene_switch"  # New location/situation
    TIME_JUMP = "time_jump"  # Time has passed
    POV_SWITCH = "pov_switch"  # Point of view character changes
    PARALLEL_NARRATIVE = "parallel_narrative"  # Parallel storylines converge or diverge
    EMOTIONAL_SHIFT = "emotional_shift"  # Emotional tone changes significantly
    TENSION_PEAK = "tension_peak"  # Cliffhanger or high tension ending
    TENSION_RELEASE = "tension_release"  # Tension eases after climax
    REVELATION = "revelation"  # Major plot revelation
    STATUS_QUO = "status_quo"  # Return to normal after disturbance


class TransitionQuality(str, Enum):
    """Quality of transition between chapters."""
    EXCELLENT = "excellent"  # Seamless, enhances reading experience
    GOOD = "good"  # Smooth with minor improvements possible
    ACCEPTABLE = "acceptable"  # Functional but could be improved
    ROUGH = "rough"  # Noticeable jarring effect
    JARRING = "jarring"  # Breaks reader immersion


class TransitionSmoothness(str, Enum):
    """How smooth the transition feels."""
    SEAMLESS = "seamless"  # No perceptible break
    GRADUAL = "gradual"  # Gentle transition
    ABRUPT = "abrupt"  # Sudden change
    CONFUSING = "confusing"  # Reader may be disoriented


class ChapterEndingType(str, Enum):
    """Type of chapter ending."""
    CLIFFHANGER = "cliffhanger"  # Ends at high tension point
    RESOLUTION = "resolution"  # Provides closure
    OPEN_ENDING = "open_ending"  # Questions remain but less tense
    REVELATION_ENDING = "revelation_ending"  # Ends with important information
    QUIET_ENDING = "quiet_ending"  # Low tension, peaceful
    SUSPENSE_ENDING = "suspense_ending"  # Building suspense
    DRAMATIC_ENDING = "dramatic_ending"  # Dramatic moment
    QUESTION_ENDING = "question_ending"  # Raises questions


class ChapterOpeningType(str, Enum):
    """Type of chapter opening."""
    DIRECT_CONTINUATION = "direct_continuation"  # Picks up where last ended
    SCENE_SETUP = "scene_setup"  # Establishes new scene
    TIME_MARKER = "time_marker"  # Indicates time has passed
    FLASHBACK = "flashback"  # Returns to past events
    POV_CHANGE = "pov_change"  # New character's perspective
    IN_MEDIAS_RES = "in_medias_res"  # In the middle of action
    REFLECTION = "reflection"  # Character reflection/thought
    DIALOGUE_START = "dialogue_start"  # Opens with dialogue


class TransitionElement(BaseModel):
    """Elements that make up a good transition."""
    # Time continuity
    time_continuity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well time flow is maintained (0-1)"
    )
    time_gap_acknowledged: bool = Field(
        default=True,
        description="Whether time jumps are properly acknowledged"
    )

    # Scene continuity
    scene_continuity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well scene flow is maintained (0-1)"
    )
    location_clear: bool = Field(
        default=True,
        description="Whether new location is clearly established"
    )

    # Character continuity
    character_continuity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well character flow is maintained (0-1)"
    )
    character_progression: bool = Field(
        default=True,
        description="Whether character development continues logically"
    )

    # Emotional continuity
    emotional_continuity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well emotional tone is maintained (0-1)"
    )
    tension_flow: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well tension/pacing flows (0-1)"
    )

    # Plot continuity
    plot_continuity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well plot threads continue (0-1)"
    )
    unanswered_questions_managed: bool = Field(
        default=True,
        description="Whether cliffhangers are handled appropriately"
    )

    # Structural elements
    has_bridge_passage: bool = Field(
        default=False,
        description="Whether there's explicit bridging content"
    )
    callback_elements: list[str] = Field(
        default_factory=list,
        description="References to previous events/chapters"
    )
    setup_for_next: list[str] = Field(
        default_factory=list,
        description="Elements that set up the next chapter"
    )


class ChapterTransitionProfile(BaseModel):
    """Profile for transition from one chapter to the next."""
    from_chapter_number: int = Field(description="Source chapter number")
    from_chapter_title: str = Field(default="", description="Source chapter title")
    to_chapter_number: int = Field(description="Target chapter number")
    to_chapter_title: str = Field(default="", description="Target chapter title")

    # Ending characteristics of source chapter
    from_ending_type: ChapterEndingType = Field(
        default=ChapterEndingType.RESOLUTION,
        description="Type of ending"
    )
    from_tension_level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Tension level at end of chapter"
    )
    from_emotional_tone: str = Field(
        default="neutral",
        description="Emotional tone at end"
    )
    from_location: str = Field(
        default="",
        description="Location at end of chapter"
    )

    # Opening characteristics of target chapter
    to_opening_type: ChapterOpeningType = Field(
        default=ChapterOpeningType.DIRECT_CONTINUATION,
        description="Type of opening"
    )
    to_tension_level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Tension level at start of chapter"
    )
    to_emotional_tone: str = Field(
        default="neutral",
        description="Emotional tone at start"
    )
    to_location: str = Field(
        default="",
        description="Location at start of chapter"
    )

    # Transition analysis
    transition_type: TransitionType = Field(
        default=TransitionType.SCENE_CONTINUATION,
        description="Type of transition"
    )
    transition_elements: TransitionElement = Field(
        default_factory=TransitionElement,
        description="Detailed transition elements"
    )

    # Quality assessment
    quality: TransitionQuality = Field(
        default=TransitionQuality.GOOD,
        description="Overall transition quality"
    )
    smoothness: TransitionSmoothness = Field(
        default=TransitionSmoothness.GRADUAL,
        description="How smooth the transition feels"
    )
    consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Consistency score for this transition"
    )

    # Issues
    issues: list[str] = Field(
        default_factory=list,
        description="Detected transition issues"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class TransitionIssue(BaseModel):
    """Represents a detected issue with chapter transitions."""
    issue_id: str = Field(description="Unique issue identifier")

    # Location
    from_chapter: int = Field(description="Source chapter number")
    to_chapter: int = Field(description="Target chapter number")

    # Issue type
    issue_type: str = Field(description="Type of issue")
    severity: str = Field(description="Severity: minor/moderate/severe/critical")

    # Description
    description: str = Field(description="Human-readable description")
    affected_elements: list[str] = Field(
        default_factory=list,
        description="Elements affected by this issue"
    )

    # Fix
    suggested_fix: str = Field(
        default="",
        description="Suggested way to fix the issue"
    )
    fix_priority: int = Field(
        default=0,
        description="Priority for fixing (higher = more important)"
    )


class TransitionConnection(BaseModel):
    """Connection analysis between two adjacent chapters."""
    # Chapters involved
    from_chapter: int = Field(description="Source chapter number")
    to_chapter: int = Field(description="Target chapter number")

    # Thread connections
    continuing_threads: list[str] = Field(
        default_factory=list,
        description="Plot threads that continue"
    )
    new_threads_introduced: list[str] = Field(
        default_factory=list,
        description="New plot threads introduced"
    )
    threads_concluded: list[str] = Field(
        default_factory=list,
        description="Plot threads that conclude"
    )

    # Character connections
    shared_characters: list[str] = Field(
        default_factory=list,
        description="Characters appearing in both chapters"
    )
    characters_exiting: list[str] = Field(
        default_factory=list,
        description="Characters not in next chapter"
    )
    characters_entering: list[str] = Field(
        default_factory=list,
        description="Characters new to next chapter"
    )

    # Thematic connections
    thematic_links: list[str] = Field(
        default_factory=list,
        description="Thematic elements that connect"
    )
    thematic_shifts: list[str] = Field(
        default_factory=list,
        description="Thematic elements that shift"
    )

    # Narrative flow
    narrative_flow_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="How well narrative flows between chapters"
    )


class TransitionAnalysis(BaseModel):
    """Comprehensive analysis of all chapter transitions in a manuscript."""
    # Overall assessment
    overall_transition_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall transition quality score"
    )

    # Individual transitions
    transition_profiles: list[ChapterTransitionProfile] = Field(
        default_factory=list,
        description="Profile for each transition"
    )

    # Connections
    connections: list[TransitionConnection] = Field(
        default_factory=list,
        description="Connection analysis between chapters"
    )

    # Issues found
    issues: list[TransitionIssue] = Field(
        default_factory=list,
        description="All detected transition issues"
    )

    # Statistics
    total_transitions: int = Field(
        default=0,
        description="Total number of transitions analyzed"
    )
    excellent_transitions: int = Field(
        default=0,
        description="Number of excellent transitions"
    )
    good_transitions: int = Field(
        default=0,
        description="Number of good transitions"
    )
    acceptable_transitions: int = Field(
        default=0,
        description="Number of acceptable transitions"
    )
    rough_transitions: int = Field(
        default=0,
        description="Number of rough transitions"
    )
    jarring_transitions: int = Field(
        default=0,
        description="Number of jarring transitions"
    )
    average_consistency: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Average consistency across transitions"
    )

    # Critical points
    weakest_transitions: list[tuple[int, int, float]] = Field(
        default_factory=list,
        description="Weakest transitions (from_ch, to_ch, score)"
    )
    critical_issues: list[str] = Field(
        default_factory=list,
        description="Critical issues that must be addressed"
    )

    # Recommendations
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improving transitions"
    )


class TransitionRevision(BaseModel):
    """Revision for improving a chapter transition."""
    from_chapter: int = Field(description="Source chapter number")
    to_chapter: int = Field(description="Target chapter number")

    # Content changes
    from_chapter_revised: str = Field(
        default="",
        description="Revised ending of source chapter"
    )
    to_chapter_revised: str = Field(
        default="",
        description="Revised opening of target chapter"
    )

    # Bridge content
    bridge_content: str = Field(
        default="",
        description="New bridge passage if needed"
    )

    # Quality improvement
    before_score: float = Field(
        description="Consistency score before revision"
    )
    after_score: float = Field(
        description="Consistency score after revision"
    )

    # Changes made
    changes_made: list[str] = Field(
        default_factory=list,
        description="Description of changes made"
    )

    # Issues addressed
    issues_addressed: list[str] = Field(
        default_factory=list,
        description="Issues that were addressed"
    )
    issues_remaining: list[str] = Field(
        default_factory=list,
        description="Issues that still need attention"
    )


class TransitionPlan(BaseModel):
    """Plan for improving chapter transitions."""
    # Transitions to revise
    transitions_to_revise: list[tuple[int, int]] = Field(
        default_factory=list,
        description="List of (from_chapter, to_chapter) pairs to revise"
    )

    priority_order: list[tuple[int, int]] = Field(
        default_factory=list,
        description="Priority order for revision"
    )

    # Focus areas
    focus_time_continuity: bool = Field(
        default=False,
        description="Focus on improving time continuity"
    )
    focus_scene_continuity: bool = Field(
        default=False,
        description="Focus on improving scene continuity"
    )
    focus_emotional_flow: bool = Field(
        default=False,
        description="Focus on improving emotional flow"
    )
    focus_plot_continuity: bool = Field(
        default=False,
        description="Focus on improving plot continuity"
    )

    # Estimated work
    estimated_revisions: int = Field(
        default=0,
        description="Estimated number of revisions needed"
    )

    # AI assistance
    ai_bridge_generation: bool = Field(
        default=True,
        description="Use AI to generate bridge passages"
    )


class TransitionReport(BaseModel):
    """Final report for chapter transition improvements."""
    analysis: TransitionAnalysis = Field(
        description="Complete transition analysis"
    )
    revision_plan: TransitionPlan = Field(
        description="Plan for revisions"
    )

    # Summary
    summary: str = Field(
        default="",
        description="Human-readable summary"
    )

    # Revisions completed
    revisions_completed: list[TransitionRevision] = Field(
        default_factory=list,
        description="Revisions that were completed"
    )

    # Final status
    final_transition_score: Optional[float] = Field(
        default=None,
        description="Final transition score after revisions"
    )
    improvement_achieved: Optional[float] = Field(
        default=None,
        description="Improvement in transition quality achieved"
    )
