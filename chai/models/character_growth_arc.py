"""Character growth arc models for novel character development planning."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class GrowthArcType(str, Enum):
    """Types of character growth arcs."""
    POSITIVE = "positive"  # Character grows and improves
    NEGATIVE = "negative"  # Character degrades or falls
    FLAT = "flat"  # Character remains relatively unchanged
    CIRCULAR = "circular"  # Character returns to starting state with new understanding
    FALL_AND_RISE = "fall_and_rise"  # Character falls then rises again
    RISE_AND_FALL = "rise_and_fall"  # Character rises then falls
    TRANSFORMATION = "transformation"  # Complete character transformation
    BOND = "bond"  # Character arc focused on relationships
    EDUCATION = "education"  # Learning/growth focused arc


class ArcStageType(str, Enum):
    """Types of stages within a growth arc."""
    STATUS_QUO = "status_quo"  # Initial state before change
    INCITING_INCIDENT = "inciting_incident"  # Event that disrupts status quo
    RISING_ACTION = "rising_action"  # Character responds and grows
    COMPLICATION = "complication"  # Obstacles and setbacks
    CRISIS = "crisis"  # Maximum challenge/trial
    CLIMAX = "climax"  # Peak moment of transformation
    FALLING_ACTION = "falling_action"  # Aftermath of climax
    RESOLUTION = "resolution"  # New equilibrium established


class GrowthMetricType(str, Enum):
    """Types of metrics to measure character growth."""
    SKILL = "skill"  # Skill acquisition or improvement
    WISDOM = "wisdom"  # Gaining insight or understanding
    EMOTIONAL = "emotional"  # Emotional maturity
    MORAL = "moral"  # Moral/ethical development
    RELATIONSHIP = "relationship"  # Interpersonal growth
    SELF_AWARENESS = "self_awareness"  # Self-knowledge
    POWER = "power"  # Physical/political/social power
    COMPASSION = "compassion"  # Empathy development
    COURAGE = "courage"  # Bravery development
    INDEPENDENCE = "independence"  # Self-reliance


class GrowthTrigger(BaseModel):
    """Event or condition that triggers character growth."""
    trigger_type: str = Field(description="Type of trigger (event, realization, relationship, challenge)")
    description: str = Field(description="What triggers the growth")
    source: str = Field(description="Where this trigger comes from (internal, external, relationship)")
    timing: str = Field(description="When this trigger occurs (early, mid, late arc)")
    intensity: str = Field(default="medium", description="Intensity: low, medium, high, extreme")
    impact: str = Field(description="How this impacts the character")


class GrowthObstacle(BaseModel):
    """Obstacle that prevents or complicates character growth."""
    obstacle_type: str = Field(description="Type of obstacle (internal, external, social)")
    description: str = Field(description="What the obstacle is")
    resistance: str = Field(description="How it resists growth")
    overcome: bool = Field(default=False, description="Whether this was overcome")
    overcoming_method: str = Field(default="", description="How it was overcome if applicable")
    growth_from_overcoming: str = Field(default="", description="What growth came from overcoming")


class GrowthLesson(BaseModel):
    """Lesson learned during a growth stage."""
    lesson_type: str = Field(description="Type of lesson (moral, practical, emotional, social)")
    description: str = Field(description="What was learned")
    application: str = Field(description="How this lesson is applied")
    integration_level: str = Field(default="partial", description="How well integrated: surface, partial, complete")
    revisit_required: bool = Field(default=False, description="Whether this lesson needs revisiting")


class GrowthStage(BaseModel):
    """A stage in character's growth arc."""
    stage_type: ArcStageType = Field(description="Type of arc stage")
    stage_name: str = Field(description="Name of this stage")
    description: str = Field(description="What happens at this stage")
    chapter_range: str = Field(default="", description="Chapter range where this occurs (e.g., '1-5')")
    trigger_event: str = Field(default="", description="Event that triggers this stage")
    emotional_state: str = Field(description="Character's emotional state at this stage")
    mental_state: str = Field(default="", description="Character's mental state at this stage")

    # Growth specifics
    lessons_learned: list[GrowthLesson] = Field(default_factory=list, description="Lessons learned")
    new_abilities_or_insights: list[str] = Field(default_factory=list, description="What character gains")
    perspective_shift: str = Field(default="", description="How character's perspective changes")
    behavioral_changes: list[str] = Field(default_factory=list, description="Observable behavioral changes")

    # Relationships
    key_relationships_at_stage: list[str] = Field(default_factory=list, description="Important relationships at this stage")
    relationship_developments: dict[str, str] = Field(default_factory=dict, description="How key relationships develop")

    # Conflicts
    conflicts_faced: list[str] = Field(default_factory=list, description="Conflicts at this stage")
    internal_struggles: list[str] = Field(default_factory=list, description="Internal conflicts")

    # Metrics
    growth_metrics: dict[str, float] = Field(default_factory=dict, description="Growth metrics at this stage (0.0-1.0)")


class GrowthArcProfile(BaseModel):
    """Complete profile for a character's growth arc."""
    character_id: str = Field(description="Character this arc belongs to")
    character_name: str = Field(description="Character name")

    # Arc type and theme
    arc_type: GrowthArcType = Field(description="Type of growth arc")
    arc_name: str = Field(description="Name of the arc (e.g., '从恐惧到勇气')")
    arc_summary: str = Field(description="One sentence arc summary")
    theme: str = Field(description="Central theme of the arc")

    # Start and end states
    starting_state: str = Field(description="Character state at arc beginning")
    ending_state: str = Field(description="Character state at arc end")
    starting_strengths: list[str] = Field(default_factory=list, description="Strengths at start")
    starting_weaknesses: list[str] = Field(default_factory=list, description="Weaknesses at start")
    ending_strengths: list[str] = Field(default_factory=list, description="Strengths at end")
    ending_weaknesses: list[str] = Field(default_factory=list, description="Weaknesses at end")

    # Core wounds and desires
    core_wound: str = Field(description="Core emotional wound driving the arc")
    core_desire: str = Field(description="Core desire driving the arc")
    core_fear: str = Field(description="Core fear in the arc")

    # Arc structure
    stages: list[GrowthStage] = Field(default_factory=list, description="All stages in the arc")
    total_chapters: int = Field(default=0, description="Total chapters in arc")

    # Triggers and obstacles
    arc_triggers: list[GrowthTrigger] = Field(default_factory=list, description="Growth triggers")
    obstacles: list[GrowthObstacle] = Field(default_factory=list, description="Obstacles to growth")

    # Key moments
    key_moments: list[str] = Field(default_factory=list, description="Key moments in the arc")
    turning_points: list[str] = Field(default_factory=list, description="Turning points")

    # Relationships
    key_relationship_arcs: dict[str, str] = Field(default_factory=dict, description="How key relationships develop")

    # Growth metrics
    primary_growth_metric: GrowthMetricType = Field(description="Primary metric for growth")
    secondary_growth_metrics: list[GrowthMetricType] = Field(default_factory=list, description="Secondary metrics")
    growth_trajectory: list[float] = Field(default_factory=list, description="Growth trajectory values (0.0-1.0 per stage)")

    # Lie the character believes
    initial_belief: str = Field(description="Lie or false belief at arc start")
    truth_learned: str = Field(description="Truth learned by arc end")
    belief_transformation: str = Field(description="How the belief transforms")

    # Thematic connections
    thematic_connections: list[str] = Field(default_factory=list, description="Thematic elements connected to arc")
    symbol_or_motif: str = Field(default="", description="Symbol or motif representing the arc")


class CharacterGrowthArcSystem(BaseModel):
    """System containing growth arcs for all characters in a story."""
    story_id: str = Field(description="Story/novel identifier")
    story_title: str = Field(description="Story title")

    # Individual character arcs
    character_arcs: list[GrowthArcProfile] = Field(default_factory=list, description="Growth arcs for all characters")

    # Arc relationships
    arc_interdependencies: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Which arcs affect which other arcs (arc_id -> [dependent_arc_ids])"
    )

    # Thematic throughlines
    thematic_throughlines: list[str] = Field(default_factory=list, description="Main thematic throughlines")

    # Arc distribution analysis
    arc_type_distribution: dict[str, int] = Field(default_factory=dict, description="Count of each arc type")
    protagonist_arc_id: str = Field(default="", description="ID of protagonist's primary arc")

    # Narrative structure
    parallel_arcs: list[list[str]] = Field(default_factory=list, description="Arcs that run parallel")
    intersecting_arcs: list[tuple[str, str]] = Field(default_factory=list, description="Arcs that intersect")


class GrowthArcAnalysis(BaseModel):
    """Analysis of character growth arcs."""
    character_id: str = Field(description="Character analyzed")
    arc_coherence: float = Field(description="How coherent the arc is (0.0-1.0)")
    growth_pacing: str = Field(description="Pacing assessment: too_fast, balanced, too_slow")
    emotional_authenticity: float = Field(description="How authentic the emotional growth feels (0.0-1.0)")
    thematic_integration: float = Field(description="Integration with story themes (0.0-1.0)")
    relationship_impact: float = Field(description="Impact on relationships (0.0-1.0)")
    stakes_clarity: float = Field(description="How clear the stakes are (0.0-1.0)")

    # Potential issues
    potential_issues: list[str] = Field(default_factory=list, description="Potential arc problems")
    strengths: list[str] = Field(default_factory=list, description="Arc strengths")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations for improvement")
