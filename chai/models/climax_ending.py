"""Climax and ending design models for powerful story conclusions."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClimaxType(str, Enum):
    """Types of climax structures."""
    # Primary climaxes
    FINAL_CLIMAX = "final_climax"
    SUB_CLIMAX = "sub_climax"
    ACT_CLIMAX = "act_climax"

    # Thematic climaxes
    EMOTIONAL_CLIMAX = "emotional_climax"
    REVELATION_CLIMAX = "revelation_climax"
    TRANSFORMATION_CLIMAX = "transformation_climax"

    # Action climaxes
    COMBAT_CLIMAX = "combat_climax"
    SACRIFICE_CLIMAX = "sacrifice_climax"
    DECISION_CLIMAX = "decision_climax"

    # Conflict climaxes
    IDEOLOGICAL_CLIMAX = "ideological_climax"
    RELATIONSHIP_CLIMAX = "relationship_climax"
    INTERNAL_CLIMAX = "internal_climax"


class ClimaxIntensity(str, Enum):
    """Intensity level of climax."""
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"
    CATASTROPHIC = "catastrophic"


class ClimaxStatus(str, Enum):
    """Status of climax design."""
    CONCEPT = "concept"
    PLANNED = "planned"
    DEVELOPED = "developed"
    INTEGRATED = "integrated"


class ClimaxElement(BaseModel):
    """A single element within the climax structure."""

    id: str = Field(description="Unique element ID")
    name: str = Field(description="Element name")
    description: str = Field(description="Element description")

    # Element type
    element_type: str = Field(description="Type: action, dialogue, revelation, etc.")

    # Chapter placement
    chapter: int = Field(description="Chapter number")
    sequence_order: int = Field(description="Order within climax sequence")

    # Character involvement
    character_ids: list[str] = Field(
        default_factory=list, description="Characters involved"
    )
    protagonist_central: bool = Field(
        default=False, description="Is protagonist central to this element"
    )

    # Stakes and tension
    stakes: str = Field(default="", description="What's at stake")
    tension_level: ClimaxIntensity = Field(
        default=ClimaxIntensity.HIGH, description="Tension intensity"
    )

    # Connection
    plot_thread_ids: list[str] = Field(
        default_factory=list, description="Plot threads resolved here"
    )
    foreshadowing_ids: list[str] = Field(
        default_factory=list, description="Foreshadowing paid off"
    )


class ClimaxStructure(BaseModel):
    """Structure of a climax sequence."""

    id: str = Field(description="Unique structure ID")
    climax_type: ClimaxType = Field(description="Type of climax")
    name: str = Field(description="Climax name")

    # Build-up
    buildup_chapters: list[int] = Field(
        default_factory=list, description="Chapters building tension"
    )
    trigger_event: str = Field(default="", description="Event that triggers the climax")

    # Climax sequence
    elements: list[ClimaxElement] = Field(
        default_factory=list, description="Elements in climax sequence"
    )
    peak_moment: str = Field(default="", description="The peak moment description")
    peak_chapter: int = Field(default=0, description="Chapter of peak moment")

    # Resolution setup
    immediate_resolution: str = Field(
        default="", description="How climax is immediately resolved"
    )

    # Impact
    consequences: list[str] = Field(
        default_factory=list, description="Immediate consequences"
    )
    world_changes: list[str] = Field(
        default_factory=list, description="Changes to the world"
    )

    # Emotional impact
    emotional_impact: str = Field(default="", description="Emotional impact on reader")
    catharsis_level: float = Field(
        default=0.5, ge=0.0, le=1.0, description=" catharsis level"
    )


class ClimaxDesign(BaseModel):
    """Complete climax design for a story."""

    id: str = Field(description="Unique design ID")
    story_id: str = Field(description="Associated story ID")

    # Climax structure
    main_climax: ClimaxStructure = Field(
        description="The main/final climax"
    )
    sub_climaxes: list[ClimaxStructure] = Field(
        default_factory=list, description="Secondary climaxes"
    )

    # Timing
    climax_chapter: int = Field(default=0, description="Chapter of main climax")
    climax_duration_chapters: int = Field(
        default=1, description="How many chapters climax spans"
    )

    # Integration
    story_beat_ids: list[str] = Field(
        default_factory=list, description="Story beats integrated"
    )
    character_arc_ids: list[str] = Field(
        default_factory=list, description="Character arcs resolved"
    )
    plot_thread_ids: list[str] = Field(
        default_factory=list, description="Plot threads resolved"
    )

    # Emotional arc
    pre_climax_tension: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Tension before climax"
    )
    climax_tension: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Peak tension during climax"
    )
    post_climax_tension: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Tension after climax"
    )

    # Status
    status: ClimaxStatus = Field(
        default=ClimaxStatus.CONCEPT, description="Design status"
    )


class EndingType(str, Enum):
    """Types of story endings."""
    # Resolution endings
    CLEAN_RESOLUTION = "clean_resolution"
    BITTERSWEET = "bittersweet"
    TRAGIC = "tragic"

    # Question endings
    OPEN_ENDED = "open_ended"
    CLIFFHANGER = "cliffhanger"
    AMBIGUOUS = "ambiguous"

    # Structural endings
    CIRCULAR = "circular"
    LINEAR = "linear"
    PARALLEL = "parallel"

    # Thematic endings
    TRIUMPHANT = "triumphant"
    PYRRHIC_VICTORY = "pyrrhic_victory"
    REDEMPTIVE = "redemptive"
    CAUTIONARY = "cautionary"

    # Special endings
    TWIST_ENDING = "twist_ending"
    EXPANDED_UNIVERSE = "expanded_universe"
    CLEANSED = "cleansed"
    FALLEN_HERO = "fallen_hero"


class EndingStatus(str, Enum):
    """Status of ending design."""
    CONCEPT = "concept"
    PLANNED = "planned"
    DEVELOPED = "developed"
    REFINED = "refined"


class EndingElement(BaseModel):
    """A single element within the ending structure."""

    id: str = Field(description="Unique element ID")
    name: str = Field(description="Element name")
    description: str = Field(description="Element description")

    # Element type
    element_type: str = Field(
        default="", description="Type: resolution, reflection, image, etc."
    )

    # Chapter placement
    chapter: int = Field(default=0, description="Chapter number")
    sequence_order: int = Field(default=0, description="Order within ending sequence")

    # Character involvement
    character_ids: list[str] = Field(
        default_factory=list, description="Characters involved"
    )

    # Purpose
    purpose: str = Field(default="", description="Purpose of this element")
    emotional_effect: str = Field(
        default="", description="Emotional effect on reader"
    )


class EndingStructure(BaseModel):
    """Structure of the ending sequence."""

    id: str = Field(description="Unique structure ID")
    ending_type: EndingType = Field(description="Type of ending")
    name: str = Field(description="Ending name")

    # Resolution coverage
    resolved_threads: list[str] = Field(
        default_factory=list, description="Plot threads resolved"
    )
    unresolved_threads: list[str] = Field(
        default_factory=list, description="Plot threads intentionally left open"
    )

    # Ending elements
    elements: list[EndingElement] = Field(
        default_factory=list, description="Elements in ending sequence"
    )

    # Final images/moments
    final_image: str = Field(default="", description="Final image description")
    final_line: str = Field(default="", description="Final line of dialogue/text")
    closing_symbol: str = Field(
        default="", description="Closing symbol or motif"
    )

    # Emotional arc
    emotional_tone: str = Field(default="", description="Overall emotional tone")
    reader_emotional_journey: list[str] = Field(
        default_factory=list, description="Reader's emotional journey through ending"
    )

    # Aftermath
    character_fates: dict[str, str] = Field(
        default_factory=dict, description="Character ID to fate description"
    )
    world_state: str = Field(default="", description="Final world state")


class EndingDesign(BaseModel):
    """Complete ending design for a story."""

    id: str = Field(description="Unique design ID")
    story_id: str = Field(description="Associated story ID")

    # Ending structure
    ending: EndingStructure = Field(description="The ending structure")

    # Timing
    ending_chapter: int = Field(default=0, description="Chapter where ending begins")
    epilogue_chapters: int = Field(
        default=0, description="Number of epilogue chapters"
    )

    # Integration
    climax_id: str = Field(default="", description="Associated climax design ID")
    character_arc_ids: list[str] = Field(
        default_factory=list, description="Character arcs concluded"
    )

    # Thematic resolution
    theme_resolution: str = Field(
        default="", description="How the theme is resolved"
    )
    thematic_statement: str = Field(
        default="", description="Final thematic statement"
    )

    # Closure
    main_question_answered: str = Field(
        default="", description="How the central question is answered"
    )
    closure_level: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Level of closure provided (0=open, 1=complete)"
    )

    # Status
    status: EndingStatus = Field(
        default=EndingStatus.CONCEPT, description="Design status"
    )


class ClimaxEndingConnection(BaseModel):
    """Connection between climax and ending."""

    id: str = Field(description="Unique connection ID")

    # Connection elements
    climax_id: str = Field(default="", description="Associated climax ID")
    ending_id: str = Field(default="", description="Associated ending ID")

    # Transition
    transition_chapters: int = Field(
        default=1, description="Chapters between climax and ending"
    )
    transition_nature: str = Field(
        default="", description="Nature of transition (falling action, reflection, etc.)"
    )

    # Coherence
    emotional_flow: str = Field(
        default="", description="How emotions flow from climax to ending"
    )
    plot_continuity: str = Field(
        default="", description="Plot continuity description"
    )

    # Balance
    climax_weight: float = Field(
        default=0.6, ge=0.0, le=1.0,
        description="Weight of climax vs ending (0=ending heavy, 1=climax heavy)"
    )


class ClimaxEndingSystem(BaseModel):
    """Complete climax and ending system for a story."""

    id: str = Field(description="Unique system ID")
    story_id: str = Field(description="Associated story ID")

    # Core designs
    climax_design: ClimaxDesign = Field(description="Climax design")
    ending_design: EndingDesign = Field(description="Ending design")

    # Connection
    connection: ClimaxEndingConnection = Field(
        description="Connection between climax and ending"
    )

    # Integration with story structure
    main_structure_id: Optional[str] = Field(
        default=None, description="Associated main story structure ID"
    )
    story_outline_id: Optional[str] = Field(
        default=None, description="Associated story outline ID"
    )

    # Quality metrics
    emotional_impact_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Emotional impact score"
    )
    thematic_coherence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Thematic coherence score"
    )
    satisfaction_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Reader satisfaction score"
    )

    # Metadata
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class ClimaxAnalysis(BaseModel):
    """Analysis of climax design quality."""

    design_id: str = Field(description="Climax design ID")

    # Structural analysis
    structural_integrity: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Structural integrity score"
    )
    element_balance: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Balance of elements"
    )

    # Emotional analysis
    emotional_peak_effectiveness: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Peak moment effectiveness"
    )
    tension_curve_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Tension curve quality"
    )

    # Integration analysis
    plot_thread_resolution: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Plot thread resolution quality"
    )
    character_arc_resolution: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Character arc resolution quality"
    )

    # Issues
    identified_issues: list[str] = Field(
        default_factory=list, description="Identified issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )


class EndingAnalysis(BaseModel):
    """Analysis of ending design quality."""

    design_id: str = Field(description="Ending design ID")

    # Closure analysis
    closure_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Closure quality score"
    )
    thread_resolution_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Plot thread resolution quality"
    )

    # Emotional analysis
    emotional_satisfaction: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Emotional satisfaction score"
    )
    thematic_resolution_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Thematic resolution quality"
    )

    # Character analysis
    character_fate_satisfaction: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Character fate satisfaction"
    )

    # Issues
    identified_issues: list[str] = Field(
        default_factory=list, description="Identified issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )


class ClimaxEndingAnalysis(BaseModel):
    """Comprehensive analysis of climax and ending system."""

    system_id: str = Field(description="System ID")

    # Individual analyses
    climax_analysis: ClimaxAnalysis = Field(description="Climax analysis")
    ending_analysis: EndingAnalysis = Field(description="Ending analysis")

    # Connection analysis
    transition_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Transition quality"
    )
    emotional_flow_quality: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Emotional flow quality"
    )
    narrative_coherence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Narrative coherence score"
    )

    # Overall quality
    overall_quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall quality score"
    )

    # Issues and recommendations
    identified_issues: list[str] = Field(
        default_factory=list, description="Identified issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )
