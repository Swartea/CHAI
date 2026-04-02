"""Plot logic self-consistency models for validating plot coherence."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PlotLogicType(str, Enum):
    """Types of plot logic issues."""
    # Timeline issues
    TIMELINE_REVERSAL = "timeline_reversal"  # Events in wrong order
    TIME_TRAVEL_CONTRADICTION = "time_travel_contradiction"  # Time travel logic error
    SEASON_WEATHER_INCONSISTENT = "season_weather_inconsistent"  # Weather doesn't match season
    TIME_JUMP_ISSUE = "time_jump_issue"  # Time progression doesn't match

    # Character knowledge issues
    CHARACTER_KNOWLEDGE_INCONSISTENT = "character_knowledge_inconsistent"  # Knows what they shouldn't
    FORGOTTEN_INFORMATION = "forgotten_information"  # Character forgets established info
    INFORMATION_LEAKED_PREMATURELY = "information_leaked_prematurely"  # Knows too early

    # Causality issues
    CAUSE_EFFECT_MISSING = "cause_effect_missing"  # Consequence without cause
    UNJUSTIFIED_EVENT = "unjustified_event"  # Event happens without reason
    CONTRADICTORY_MOTIVATION = "contradictory_motivation"  # Actions contradict motivation

    # World rules issues
    MAGIC_SYSTEM_VIOLATION = "magic_system_violation"  # Magic doesn't follow rules
    TECHNOLOGY_INCONSISTENT = "technology_inconsistent"  # Tech level contradiction
    SOCIAL_RULES_VIOLATED = "social_rules_violated"  # Social norms contradicted

    # Character ability issues
    SKILL_APPEARED_MAGICALLY = "skill_appeared_magically"  # New skill without training
    SKILL_LEVEL_INCONSISTENT = "skill_level_inconsistent"  # Skill level changes randomly
    CHARACTER_ABILITY_EXAGGERATED = "character_ability_exaggerated"  # Overpowered without reason

    # Location/travel issues
    TRAVEL_TIME_INSUFFICIENT = "travel_time_insufficient"  # Distance doesn't match travel time
    LOCATION_CONTRADICTION = "location_contradiction"  # Character in two places
    IMPOSSIBLE_REACHABILITY = "impossible_reachability"  # Can't get there from here

    # Plot hole issues
    UNRESOLVED_PLOT_THREAD = "unresolved_plot_thread"  # Plot point never resolved
    PLOT_INCONSISTENCY = "plot_inconsistency"  # Plot facts contradict
    RETCON_DETECTED = "retcon_detected"  # Previously established fact changed

    # Character consistency issues
    CHARACTER_PERSONALITY_BREAK = "character_personality_break"  # Acts out of character
    RELATIONSHIP_INCONSISTENT = "relationship_inconsistent"  # Relationship changes suddenly

    # Setup/payoff issues
    SETUP_NEVER_USED = "setup_never_used"  # Setup element never pays off
    PAYOFF_WITHOUT_SETUP = "payoff_without_setup"  # Payoff without proper setup


class PlotLogicSeverity(str, Enum):
    """Severity of plot logic issues."""
    MINOR = "minor"      # Small inconsistency, easily fixed
    MODERATE = "moderate"  # Should be addressed
    SEVERE = "severe"    # Breaks immersion significantly
    CRITICAL = "critical"  # Major plot hole, must fix


class PlotTimelineEvent(BaseModel):
    """A timeline event in the story."""

    event_id: str = Field(description="Unique event ID")
    chapter: int = Field(description="Chapter where event occurs")
    title: str = Field(description="Event title")
    description: str = Field(description="What happens")
    timestamp_in_story: Optional[str] = Field(
        default=None,
        description="Story time (e.g., 'Day 1', 'Three years later')"
    )

    # Involved parties
    characters_involved: list[str] = Field(
        default_factory=list,
        description="Character IDs involved"
    )
    location: str = Field(
        default="",
        description="Location of event"
    )

    # Causality
    causes: list[str] = Field(
        default_factory=list,
        description="Event IDs that cause this event"
    )
    effects: list[str] = Field(
        default_factory=list,
        description="Event IDs that are effects of this event"
    )

    # Knowledge
    information_revealed: list[str] = Field(
        default_factory=list,
        description="Information revealed at this event"
    )
    characters_aware: list[str] = Field(
        default_factory=list,
        description="Characters who become aware of information"
    )


class CharacterKnowledgeState(BaseModel):
    """Track what a character knows at each point."""

    character_id: str = Field(description="Character ID")
    character_name: str = Field(description="Character name")

    # What the character knows
    known_information: list[str] = Field(
        default_factory=list,
        description="Information the character knows"
    )
    known_by_others: list[str] = Field(
        default_factory=list,
        description="Information others know about this character"
    )

    # Relationships
    relationships: dict[str, str] = Field(
        default_factory=dict,
        description="Current relationship status with other characters"
    )

    # Abilities
    known_skills: list[str] = Field(
        default_factory=list,
        description="Skills others know this character has"
    )


class PlotLogicIssue(BaseModel):
    """A specific plot logic issue found."""

    issue_id: str = Field(description="Unique issue ID")
    issue_type: PlotLogicType = Field(description="Type of issue")
    severity: PlotLogicSeverity = Field(description="Severity level")

    # Location
    chapter: Optional[int] = Field(
        default=None,
        description="Chapter where issue occurs"
    )
    event_id: Optional[str] = Field(
        default=None,
        description="Related event ID"
    )
    character_id: Optional[str] = Field(
        default=None,
        description="Character involved"
    )

    # Details
    title: str = Field(description="Issue title")
    description: str = Field(description="Issue description")
    conflicting_facts: list[str] = Field(
        default_factory=list,
        description="Facts that conflict"
    )

    # Fix guidance
    suggestion: str = Field(
        description="How to fix this issue"
    )
    related_chapters: list[int] = Field(
        default_factory=list,
        description="Chapters involved in the issue"
    )


class ChapterPlotLogicProfile(BaseModel):
    """Plot logic profile for a chapter."""

    chapter_id: str = Field(description="Chapter ID")
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Events in this chapter
    timeline_events: list[PlotTimelineEvent] = Field(
        default_factory=list,
        description="Timeline events in chapter"
    )

    # Knowledge changes
    knowledge_changes: list[dict] = Field(
        default_factory=list,
        description="Character knowledge state changes"
    )

    # Issues found
    issues: list[PlotLogicIssue] = Field(
        default_factory=list,
        description="Issues found in this chapter"
    )

    # Scores
    timeline_consistency_score: float = Field(
        default=1.0,
        description="Timeline consistency (0-1)"
    )
    causality_score: float = Field(
        default=1.0,
        description="Causality consistency (0-1)"
    )
    character_knowledge_score: float = Field(
        default=1.0,
        description="Character knowledge consistency (0-1)"
    )
    world_rules_score: float = Field(
        default=1.0,
        description="World rules consistency (0-1)"
    )
    overall_score: float = Field(
        default=1.0,
        description="Overall chapter plot logic score (0-1)"
    )

    # Counts
    total_issues: int = Field(default=0, description="Total issues")
    severe_issues: int = Field(default=0, description="Severe issues")


class PlotLogicAnalysis(BaseModel):
    """Analysis of plot logic across a section."""

    analysis_id: str = Field(description="Unique analysis ID")

    # Chapter profile
    chapter_profile: ChapterPlotLogicProfile = Field(
        description="Chapter-level analysis"
    )

    # Issue summary
    issues: list[PlotLogicIssue] = Field(
        default_factory=list,
        description="All issues found"
    )
    issue_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues by type"
    )

    # Quality metrics
    timeline_score: float = Field(
        default=1.0,
        description="Timeline consistency (0-1)"
    )
    causality_score: float = Field(
        default=1.0,
        description="Causality consistency (0-1)"
    )
    knowledge_score: float = Field(
        default=1.0,
        description="Character knowledge consistency (0-1)"
    )
    world_rules_score: float = Field(
        default=1.0,
        description="World rules consistency (0-1)"
    )

    # Overall
    overall_score: float = Field(
        default=1.0,
        description="Overall plot logic score (0-1)"
    )

    # Counts
    total_issues: int = Field(default=0, description="Total issues found")
    severe_issues: int = Field(default=0, description="Severe issues count")


class PlotLogicRevision(BaseModel):
    """Revision plan for plot logic issues."""

    analysis_id: str = Field(description="Associated analysis ID")

    # Issues to address
    priority_fixes: list[PlotLogicIssue] = Field(
        default_factory=list,
        description="High priority fixes (severe issues)"
    )
    suggested_fixes: list[PlotLogicIssue] = Field(
        default_factory=list,
        description="Medium priority fixes"
    )
    optional_improvements: list[PlotLogicIssue] = Field(
        default_factory=list,
        description="Low priority improvements"
    )

    # Revision guidance by type
    revision_guidance: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Guidance grouped by issue type"
    )

    # Overall revision direction
    revision_focus: list[str] = Field(
        default_factory=list,
        description="Main areas to focus revision on"
    )


class PlotLogicReport(BaseModel):
    """Comprehensive report for plot logic analysis."""

    report_id: str = Field(description="Unique report ID")

    # Analysis results
    analyses: list[PlotLogicAnalysis] = Field(
        default_factory=list,
        description="Analyses per chapter"
    )

    # Aggregate statistics
    total_chapters_analyzed: int = Field(
        default=0,
        description="Number of chapters analyzed"
    )

    # Issue statistics
    total_issues: int = Field(default=0, description="Total issues across all chapters")
    severe_issues: int = Field(default=0, description="Severe issues")
    moderate_issues: int = Field(default=0, description="Moderate issues")
    minor_issues: int = Field(default=0, description="Minor issues")
    critical_issues: int = Field(default=0, description="Critical issues")

    # Issue breakdown by type
    issues_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Issue counts by type"
    )

    # Problematic chapters
    most_issues_chapter: Optional[int] = Field(
        default=None,
        description="Chapter with most issues"
    )
    best_chapter: Optional[int] = Field(
        default=None,
        description="Chapter with best consistency"
    )

    # Overall scores
    overall_timeline_score: float = Field(
        default=1.0,
        description="Overall timeline consistency"
    )
    overall_causality_score: float = Field(
        default=1.0,
        description="Overall causality consistency"
    )
    overall_knowledge_score: float = Field(
        default=1.0,
        description="Overall character knowledge consistency"
    )
    overall_world_rules_score: float = Field(
        default=1.0,
        description="Overall world rules consistency"
    )
    overall_score: float = Field(
        default=1.0,
        description="Overall plot logic score"
    )

    # Recommendations
    key_recommendations: list[str] = Field(
        default_factory=list,
        description="Key improvement recommendations"
    )
    chapter_summaries: dict[str, str] = Field(
        default_factory=dict,
        description="Per-chapter summary descriptions"
    )

    # Unresolved plot threads
    unresolved_threads: list[str] = Field(
        default_factory=list,
        description="Plot threads that haven't been resolved"
    )


class PlotConsistencyTemplate(BaseModel):
    """Template for plot consistency checking."""

    template_name: str = Field(description="Template name")
    template_description: str = Field(
        default="",
        description="Template description"
    )

    # World rules to check
    magic_rules: list[str] = Field(
        default_factory=list,
        description="Magic system rules"
    )
    technology_rules: list[str] = Field(
        default_factory=list,
        description="Technology rules"
    )
    social_rules: list[str] = Field(
        default_factory=list,
        description="Social structure rules"
    )

    # Known inconsistencies to ignore
    accepted_issues: list[str] = Field(
        default_factory=list,
        description="Known issues that are accepted"
    )

    # Sensitivity settings
    timeline_strictness: float = Field(
        default=0.8,
        description="How strict to check timeline (0-1)"
    )
    causality_strictness: float = Field(
        default=0.8,
        description="How strict to check causality (0-1)"
    )
    knowledge_strictness: float = Field(
        default=0.7,
        description="How strict to check character knowledge (0-1)"
    )
    world_rules_strictness: float = Field(
        default=0.9,
        description="How strict to check world rules (0-1)"
    )
