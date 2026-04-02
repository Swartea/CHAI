"""Action and plot advancement models for dynamic scene writing."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of action sequences."""
    COMBAT = "combat"                          # Fighting, battle, duel
    CHASE = "chase"                            # Pursuit, escape
    INVESTIGATION = "investigation"            # Searching, discovering clues
    CONFRONTATION = "confrontation"            # Facing an opponent, argument
    DISCOVERY = "discovery"                     # Finding something important
    CONFLICT = "conflict"                       # General conflict, struggle
    ESCAPE = "escape"                           # Fleeing, evading
    RESCUE = "rescue"                           # Saving someone or something
    NEGOTIATION = "negotiation"                 # High-stakes discussion
    MANEUVER = "maneuver"                      # Tactical movement, strategy
    REVELATION = "revelation"                   # Dramatic truth reveal
    SACRIFICE = "sacrifice"                    # Self-sacrifice, giving up something
    TRIUMPH = "triumph"                         # Victory, success moment
    FAILURE = "failure"                         # Defeat, setback
    BETRAYAL = "betrayal"                       # Treachery, turning point
    ALLIANCE = "alliance"                       # Forming bonds, partnerships


class ActionIntensity(str, Enum):
    """Intensity level of action sequences."""
    LOW = "low"                                 # Minor tension, subtle actions
    MODERATE = "moderate"                       # Building tension, moderate action
    HIGH = "high"                               # Intense moments, significant action
    EXTREME = "extreme"                         # Climactic, peak action
    CLIMACTIC = "climactic"                     # Highest intensity, turning point


class ActionPhase(str, Enum):
    """Phase of an action sequence."""
    SETUP = "setup"                             # Initial setup, establishing situation
    INITIATION = "initiation"                   # Beginning of action
    ESCALATION = "escalation"                   # Building intensity
    CRISIS = "crisis"                           # Peak tension, critical moment
    RESOLUTION = "resolution"                   # Action concludes
    AFTERMATH = "aftermath"                    # Consequences, reflection


class PlotAdvancementType(str, Enum):
    """Types of plot advancement."""
    MAIN_PLOT = "main_plot"                     # Major story progression
    SUBPLOT = "subplot"                         # Secondary storyline
    CHARACTER_DEVELOPMENT = "character_development"  # Character growth moment
    REVELATION = "revelation"                   # Important truth revealed
    DECISION = "decision"                        # Character makes crucial choice
    TURNING_POINT = "turning_point"             # Story direction changes
    CLIMAX = "climax"                           # Peak story moment
    SETBACK = "setback"                         # Obstacle, failure
    BREAKTHROUGH = "breakthrough"               # Major progress
    FORESHADOWING = "foreshadowing"             # Hint at future events
    PAYOFF = "payoff"                           # Foreshadowing payoff
    RELATIONSHIP_CHANGE = "relationship_change" # Bond shifts between characters


class PlotBeatType(str, Enum):
    """Specific plot beat types."""
    INCITING_INCIDENT = "inciting_incident"      # Event that starts the story
    FIRST_CULPRIT = "first_culprit"             # First antagonist appears
    POINT_OF_NO_RETURN = "point_of_no_return"   # Irreversible decision
    COMPLICATION = "complication"               # New obstacle
    CRISIS_DECISION = "crisis_decision"         # Crucial choice under pressure
    CLIMAX = " climax"                           # Peak confrontation
    RESOLUTION = "resolution"                    # Conflict resolved
    FALSE_VICTORY = "false_victory"             # Apparent success that fails
    FALSE_DEFEAT = "false_defeat"               # Apparent failure that leads to good
    REVERSAL = "reversal"                       # Sudden change in fortune
    REVEAL = "reveal"                           # Information revealed
    ALLIANCE_FORMED = "alliance_formed"         # New partnership
    ALLIANCE_BROKEN = "alliance_broken"         # Betrayal, trust broken


class PacingType(str, Enum):
    """Narrative pacing types."""
    SLOW = "slow"                               # Detailed, contemplative
    MODERATE = "moderate"                       # Standard pace
    FAST = "fast"                               # Quick progression
    BUILDING = "building"                       # Accelerating
    CRESCENDO = "crescendo"                     # Building to peak
    DENouement = "denouement"                   # Winding down


class ActionBeat(BaseModel):
    """A single beat/moment in an action sequence."""

    id: str = Field(description="Unique beat ID")
    sequence_id: str = Field(description="Parent action sequence ID")

    # Content
    description: str = Field(default="", description="Beat description")
    action_type: ActionType = Field(default=ActionType.CONFLICT, description="Type of action")

    # Timing
    phase: ActionPhase = Field(default=ActionPhase.SETUP, description="Phase in sequence")
    pacing: PacingType = Field(default=PacingType.MODERATE, description="Pacing type")

    # Intensity
    intensity: ActionIntensity = Field(default=ActionIntensity.MODERATE, description="Intensity level")
    tension_level: float = Field(default=0.5, description="Tension 0-1")

    # Characters involved
    character_ids: list[str] = Field(default_factory=list, description="Characters in this beat")
    character_actions: dict[str, str] = Field(default_factory=dict, description="Actions by character ID")

    # Location and setting
    location: str = Field(default="", description="Location of this beat")
    time_offset: str = Field(default="", description="Time offset from sequence start")

    # Word count
    word_count: int = Field(default=0, description="Word count for this beat")

    # Flags
    is_climactic: bool = Field(default=False, description="Is this a climactic moment")
    has_revelation: bool = Field(default=False, description="Does this beat contain revelation")
    changes_status_quo: bool = Field(default=False, description="Does this change the story status quo")


class ActionSequence(BaseModel):
    """A complete action sequence with multiple beats."""

    id: str = Field(description="Unique sequence ID")
    scene_id: str = Field(description="Associated scene ID")

    # Type and context
    action_type: ActionType = Field(default=ActionType.CONFLICT, description="Primary action type")
    title: str = Field(default="", description="Sequence title")
    purpose: str = Field(default="", description="Purpose in story")

    # Beats
    beats: list[ActionBeat] = Field(default_factory=list, description="Sequence of beats")

    # Structure
    starting_intensity: ActionIntensity = Field(default=ActionIntensity.LOW, description="Starting intensity")
    peak_intensity: ActionIntensity = Field(default=ActionIntensity.HIGH, description="Peak intensity")
    ending_intensity: ActionIntensity = Field(default=ActionIntensity.MODERATE, description="Ending intensity")

    # Progression
    pacing_type: PacingType = Field(default=PacingType.MODERATE, description="Overall pacing")
    tension_curve: list[float] = Field(default_factory=list, description="Tension progression 0-1")

    # Characters
    primary_character_ids: list[str] = Field(default_factory=list, description="Main characters")
    antagonist_ids: list[str] = Field(default_factory=list, description="Antagonists involved")

    # Setting
    location: str = Field(default="", description="Primary location")
    duration: str = Field(default="", description="Sequence duration")

    # Quality metrics
    coherence_score: float = Field(default=0.0, description="Sequence coherence 0-1")
    excitement_score: float = Field(default=0.0, description="Excitement level 0-1")
    pacing_score: float = Field(default=0.0, description="Pacing effectiveness 0-1")

    # Stakes
    stakes: str = Field(default="", description="What's at stake")
    consequences: list[str] = Field(default_factory=list, description="Consequences of this action")

    # Word count
    total_word_count: int = Field(default=0, description="Total word count")


class PlotAdvancementBeat(BaseModel):
    """A single beat that advances the plot."""

    id: str = Field(description="Unique beat ID")
    plot_arc_id: str = Field(description="Associated plot arc ID")

    # Content
    description: str = Field(default="", description="Beat description")
    plot_type: PlotAdvancementType = Field(default=PlotAdvancementType.MAIN_PLOT, description="Plot advancement type")
    beat_type: PlotBeatType = Field(default=PlotBeatType.COMPLICATION, description="Specific beat type")

    # Context
    chapter_number: int = Field(default=0, description="Chapter number")
    scene_number: int = Field(default=0, description="Scene number")
    order_in_chapter: int = Field(default=0, description="Order within chapter")

    # Characters
    character_ids: list[str] = Field(default_factory=list, description="Characters involved")
    character_decisions: dict[str, str] = Field(default_factory=dict, description="Decisions by character")

    # Plot connections
    connects_to_previous: bool = Field(default=True, description="Connects to previous beat")
    sets_up_future: bool = Field(default=False, description="Sets up future events")
    foreshadowing_ids: list[str] = Field(default_factory=list, description="Foreshadowing elements")

    # Impact
    impact_level: str = Field(default="moderate", description="Impact: low, moderate, high, critical")
    changes_relationships: bool = Field(default=False, description="Changes character relationships")
    new_information: list[str] = Field(default_factory=list, description="New information revealed")

    # Word count
    word_count: int = Field(default=0, description="Word count for this beat")


class PlotArcAdvancement(BaseModel):
    """Plot arc with advancement beats."""

    id: str = Field(description="Unique arc ID")
    arc_name: str = Field(description="Name of this plot arc")
    arc_type: str = Field(default="main", description="Arc type: main, romantic, subplot, mystery")

    # Beats
    beats: list[PlotAdvancementBeat] = Field(default_factory=list, description="Advancement beats in order")

    # Progress tracking
    arc_progress: float = Field(default=0.0, description="Progress through arc 0-1")
    current_phase: str = Field(default="setup", description="Current arc phase")

    # Story position
    starts_at_chapter: int = Field(default=1, description="Chapter where arc starts")
    climax_at_chapter: int = Field(default=0, description="Chapter of climax")
    ends_at_chapter: int = Field(default=0, description="Chapter where arc ends")

    # Quality
    coherence_score: float = Field(default=0.0, description="Arc coherence 0-1")
    tension_score: float = Field(default=0.0, description="Arc tension effectiveness 0-1")


class ActionPlotPlan(BaseModel):
    """Plan for generating action and plot advancement."""

    id: str = Field(description="Unique plan ID")
    scene_id: str = Field(description="Associated scene ID")

    # Action sequences
    action_sequences: list[ActionSequence] = Field(default_factory=list, description="Action sequences")

    # Plot arcs
    plot_arcs: list[PlotArcAdvancement] = Field(default_factory=list, description="Plot arcs")

    # Purpose
    primary_action_type: ActionType = Field(default=ActionType.CONFLICT, description="Primary action type")
    primary_plot_type: PlotAdvancementType = Field(default=PlotAdvancementType.MAIN_PLOT, description="Primary plot advancement")

    # Intensity targets
    target_intensity: ActionIntensity = Field(default=ActionIntensity.MODERATE, description="Target intensity")
    target_tension: float = Field(default=0.5, description="Target tension 0-1")

    # Length
    target_action_count: int = Field(default=5, description="Target number of action beats")
    target_plot_count: int = Field(default=3, description="Target number of plot beats")
    target_word_count: int = Field(default=800, description="Target word count")

    # Integration
    include_dialogue: bool = Field(default=True, description="Include dialogue")
    include_description: bool = Field(default=True, description="Include scene description")
    balance_action_plot: float = Field(default=0.5, description="Balance: 0=action, 1=plot")

    # Stakes
    stakes_description: str = Field(default="", description="What's at stake")
    consequences_preview: list[str] = Field(default_factory=list, description="Preview of consequences")

    # Pacing
    pacing_type: PacingType = Field(default=PacingType.MODERATE, description="Overall pacing")

    # Character actions
    character_goals: dict[str, str] = Field(default_factory=dict, description="Goals for each character")
    character_conflicts: dict[str, str] = Field(default_factory=dict, description="Conflicts for each character")


class ActionPlotDraft(BaseModel):
    """Generated action and plot advancement draft."""

    id: str = Field(description="Unique draft ID")
    plan_id: str = Field(description="Associated plan ID")
    scene_id: str = Field(description="Associated scene ID")

    # Content sections
    action_content: str = Field(default="", description="Generated action sequences")
    plot_content: str = Field(default="", description="Generated plot advancement content")
    combined_content: str = Field(default="", description="Fully integrated content")

    # Structure
    action_sequences: list[ActionSequence] = Field(default_factory=list, description="Action sequences")
    plot_arcs: list[PlotArcAdvancement] = Field(default_factory=list, description="Plot arcs")

    # Quality metrics
    action_coherence_score: float = Field(default=0.0, description="Action coherence 0-1")
    plot_coherence_score: float = Field(default=0.0, description="Plot coherence 0-1")
    pacing_score: float = Field(default=0.0, description="Pacing effectiveness 0-1")
    tension_score: float = Field(default=0.0, description="Tension effectiveness 0-1")
    excitement_score: float = Field(default=0.0, description="Excitement level 0-1")

    # Flags
    has_climactic_moment: bool = Field(default=False, description="Contains climactic moment")
    has_revelation: bool = Field(default=False, description="Contains revelation")
    advances_plot: bool = Field(default=False, description="Meaningfully advances plot")
    has_stakes_clarity: bool = Field(default=False, description="Stakes are clear")

    # Word counts
    action_word_count: int = Field(default=0, description="Action content word count")
    plot_word_count: int = Field(default=0, description="Plot content word count")
    total_word_count: int = Field(default=0, description="Total word count")

    # Status
    status: str = Field(default="draft", description="Status: draft, revised, finalized")


class ActionPlotRevision(BaseModel):
    """Revision details for action and plot content."""

    original_draft: ActionPlotDraft = Field(description="Original draft")
    revision_notes: list[str] = Field(default_factory=list, description="What to revise")
    revised_content: str = Field(default="", description="Revised combined content")
    quality_score: Optional[float] = Field(default=None, description="Quality score after revision 0-1")


class ActionPlotAnalysis(BaseModel):
    """Analysis of action and plot advancement quality."""

    draft_id: str = Field(description="Draft ID analyzed")

    # Action analysis
    action_coherence: float = Field(default=0.0, description="Action sequence coherence 0-1")
    action_pacing: float = Field(default=0.0, description="Action pacing effectiveness 0-1")
    action_clarity: float = Field(default=0.0, description="Action clarity 0-1")
    combat真实性: float = Field(default=0.0, description="Combat authenticity 0-1")
    tension_progression: float = Field(default=0.0, description="Tension progression 0-1")

    # Plot analysis
    plot_coherence: float = Field(default=0.0, description="Plot advancement coherence 0-1")
    plot_pacing: float = Field(default=0.0, description="Plot pacing 0-1")
    character_decision_clarity: float = Field(default=0.0, description="Character decision clarity 0-1")
    stakes_clarity: float = Field(default=0.0, description="Stakes clarity 0-1")
    foreshadowing_effectiveness: float = Field(default=0.0, description="Foreshadowing payoff 0-1")

    # Integration
    action_plot_balance: float = Field(default=0.0, description="Balance between action and plot 0-1")
    dialogue_integration: float = Field(default=0.0, description="Dialogue integration 0-1")
    description_integration: float = Field(default=0.0, description="Scene description integration 0-1")

    # Overall
    overall_quality_score: float = Field(default=0.0, description="Overall quality 0-1")

    # Issues
    critical_issues: list[str] = Field(default_factory=list, description="Critical issues")
    minor_issues: list[str] = Field(default_factory=list, description="Minor issues")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class ActionPlotTemplate(BaseModel):
    """Template for action and plot generation by situation type."""

    id: str = Field(description="Template ID")
    name: str = Field(description="Template name")

    # Applicable types
    applicable_action_types: list[ActionType] = Field(default_factory=list, description="Action types this template fits")
    applicable_plot_types: list[PlotAdvancementType] = Field(default_factory=list, description="Plot types this template fits")

    # Structure guidance
    typical_beat_count: int = Field(default=5, description="Typical number of beats")
    typical_action_ratio: float = Field(default=0.5, description="Ratio of action to plot content")

    # Pacing
    pacing_pattern: PacingType = Field(default=PacingType.MODERATE, description="Typical pacing")
    intensity_curve: list[ActionIntensity] = Field(default_factory=list, description="Expected intensity progression")

    # Tension
    starting_tension: float = Field(default=0.3, description="Starting tension 0-1")
    peak_tension: float = Field(default=0.9, description="Peak tension 0-1")
    ending_tension: float = Field(default=0.5, description="Ending tension 0-1")

    # Content patterns
    opening_pattern: str = Field(default="", description="How action typically opens")
    development_pattern: str = Field(default="", description="How action typically develops")
    climax_pattern: str = Field(default="", description="How climax is typically handled")
    closing_pattern: str = Field(default="", description="How action typically closes")

    # Style guidance
    action_detail_level: str = Field(default="moderate", description="Action detail: brief, moderate, detailed")
    dialogue_in_action: bool = Field(default=True, description="Include dialogue during action")
    internal_thought_in_action: bool = Field(default=False, description="Include internal thoughts during action")

    # Example beats
    typical_opening_beats: list[str] = Field(default_factory=list, description="Typical opening beats")
    typical_climax_beats: list[str] = Field(default_factory=list, description="Typical climax beats")
    typical_closing_beats: list[str] = Field(default_factory=list, description="Typical closing beats")