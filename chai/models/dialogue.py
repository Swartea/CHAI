"""Dialogue generation models for character-consistent dialogue writing."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DialoguePurpose(str, Enum):
    """Purpose of dialogue in the scene."""
    INFORMATION_GATHERING = "information_gathering"  # Exchange of information
    CONFLICT = "conflict"                             # Argument, dispute, confrontation
    ALLIANCE_BUILDING = "alliance_building"          # Building trust or partnerships
    REVELATION = "revelation"                        # Revealing secrets or truths
    EMOTIONAL = "emotional"                          # Emotional expression or connection
    MANIPULATION = "manipulation"                   # Deception, persuasion, manipulation
    TENSION_BUILDING = "tension_building"           # Creating suspense or unease
    COMIC_RELIEF = "comic_relief"                   # Humor and levity
    PLOT_ADVANCEMENT = "plot_advancement"           # Moving the story forward
    CHARACTER_REVELATION = "character_revelation"   # Showing character depth


class DialogueType(str, Enum):
    """Type/style of dialogue."""
    DIRECT = "direct"                                # Direct speech with quotes
    INDIRECT = "indirect"                            # Reported speech
    INTERNAL = "internal"                            # Internal thought/monologue
    WHISPERED = "whispered"                          # Secretive speech
    SHOUTED = "shouted"                              # Loud speech
    SILENT = "silent"                                # Subtext/double meaning


class DialogueTone(str, Enum):
    """Tone of dialogue."""
    FORMAL = "formal"                                # Formal, polite
    CASUAL = "casual"                                # Informal, relaxed
    INTIMATE = "intimate"                            # Close, personal
    HOSTILE = "hostile"                              # Aggressive, antagonistic
    SUSPICIOUS = "suspicious"                        # Doubtful, questioning
    JOYFUL = "joyful"                                # Happy, excited
    SAD = "sad"                                      # Melancholic, grieving
    TENSE = "tense"                                  # Nervous, suspenseful
    ROMANTIC = "romantic"                             # Loving, affectionate
    IRONIC = "ironic"                                # Sarcastic, ironic


class CharacterDialogueStyle(BaseModel):
    """Character's individual dialogue style profile."""

    # Speech patterns
    speech_pattern: str = Field(
        default="",
        description="Overall speech pattern description"
    )
    vocabulary_level: str = Field(
        default="moderate",
        description="Vocabulary level: simple, moderate, sophisticated, scholarly"
    )
    sentence_structure: str = Field(
        default="mixed",
        description="Sentence structure: short, long, mixed, fragmented"
    )

    # Language characteristics
    formal_or_informal: str = Field(
        default="neutral",
        description="Formality level: formal, neutral, informal, colloquial"
    )
    use_of_honorifics: bool = Field(
        default=True,
        description="Whether character uses honorifics/titles"
    )
    accent_dialect: Optional[str] = Field(
        default=None,
        description="Accent or dialect description"
    )

    # Verbal habits
    catchphrases: list[str] = Field(
        default_factory=list,
        description="Character's catchphrases or recurring expressions"
    )
    filler_words: list[str] = Field(
        default_factory=list,
        description="Filler words the character uses (e.g., 'um', 'well', 'you know')"
    )
    verbal_tics: list[str] = Field(
        default_factory=list,
        description="Recurring verbal habits or quirks"
    )
    speech_quirks: list[str] = Field(
        default_factory=list,
        description="Unique speech characteristics"
    )

    # Emotional expression
    emotional_restraint: str = Field(
        default="moderate",
        description="Emotional restraint: suppressed, moderate, expressive"
    )
    directness: str = Field(
        default="moderate",
        description="Directness: indirect, moderate, direct"
    )
    passive_aggressive: bool = Field(
        default=False,
        description="Tendency for passive-aggressive speech"
    )

    # Communication style
    interruption_tendency: str = Field(
        default="rare",
        description="Interruption tendency: never, rare, occasional, frequent"
    )
    listening_quality: str = Field(
        default="attentive",
        description="Listening quality: inattentive, selective, attentive, empathetic"
    )
    response_delay: str = Field(
        default="normal",
        description="Response delay: instant, normal, thoughtful, long_pause"
    )


class DialogueLine(BaseModel):
    """A single line of dialogue."""

    id: str = Field(description="Unique dialogue line ID")
    speaker_id: str = Field(description="Character ID of speaker")
    speaker_name: str = Field(description="Character name for display")

    # Content
    content: str = Field(default="", description="Dialogue text content")

    # Type and tone
    dialogue_type: DialogueType = Field(
        default=DialogueType.DIRECT,
        description="Type of dialogue"
    )
    tone: DialogueTone = Field(
        default=DialogueTone.CASUAL,
        description="Tone of the dialogue"
    )

    # Subtext and meaning
    subtext: Optional[str] = Field(
        default=None,
        description="Underlying meaning or subtext"
    )
    literal_meaning: Optional[str] = Field(
        default=None,
        description="Literal meaning if different from subtext"
    )

    # Context
    purpose: DialoguePurpose = Field(
        default=DialoguePurpose.PLOT_ADVANCEMENT,
        description="Purpose of this dialogue line"
    )
    emotional_state: str = Field(
        default="neutral",
        description="Speaker's emotional state"
    )

    # Characteristics
    is_catchphrase: bool = Field(
        default=False,
        description="Whether this is a catchphrase"
    )
    is_important: bool = Field(
        default=False,
        description="Whether this is an important/key line"
    )

    # Word count
    word_count: int = Field(
        default=0,
        description="Word count of dialogue"
    )


class DialogueExchange(BaseModel):
    """A complete exchange/dialogue between characters."""

    id: str = Field(description="Unique exchange ID")
    scene_id: str = Field(description="Associated scene ID")

    # Participants
    participants: list[str] = Field(
        default_factory=list,
        description="Character IDs participating"
    )
    participant_names: list[str] = Field(
        default_factory=list,
        description="Character names for display"
    )

    # Lines
    lines: list[DialogueLine] = Field(
        default_factory=list,
        description="Dialogue lines in order"
    )

    # Purpose and context
    purpose: DialoguePurpose = Field(
        default=DialoguePurpose.PLOT_ADVANCEMENT,
        description="Primary purpose of this exchange"
    )
    topic: str = Field(
        default="",
        description="Topic of conversation"
    )

    # Dynamics
    power_dynamic: str = Field(
        default="equal",
        description="Power dynamic: dominant, submissive, equal, shifting"
    )
    emotional_tone: DialogueTone = Field(
        default=DialogueTone.CASUAL,
        description="Overall emotional tone"
    )

    # Quality metrics
    naturalness_score: float = Field(
        default=0.0,
        description="How natural the dialogue sounds (0-1)"
    )
    character_consistency_score: float = Field(
        default=0.0,
        description="Consistency with character voices (0-1)"
    )
    purpose_fulfillment_score: float = Field(
        default=0.0,
        description="How well it fulfills its purpose (0-1)"
    )

    # Context
    setting_context: str = Field(
        default="",
        description="Scene setting context"
    )
    situation_context: str = Field(
        default="",
        description="Situation/context description"
    )

    # Word count
    total_word_count: int = Field(
        default=0,
        description="Total word count of all lines"
    )


class DialoguePlan(BaseModel):
    """Plan for generating a dialogue scene."""

    id: str = Field(description="Unique plan ID")
    scene_id: str = Field(description="Associated scene ID")

    # Participants
    characters: list[dict] = Field(
        default_factory=list,
        description="Character profiles participating"
    )
    speaker_count: int = Field(
        default=2,
        description="Number of speakers"
    )

    # Exchange structure
    exchanges: list[DialogueExchange] = Field(
        default_factory=list,
        description="Dialogue exchanges to generate"
    )

    # Purpose and context
    purpose: DialoguePurpose = Field(
        default=DialoguePurpose.PLOT_ADVANCEMENT,
        description="Primary dialogue purpose"
    )
    topic: str = Field(
        default="",
        description="Main topic of dialogue"
    )
    situation: str = Field(
        default="",
        description="Situation/context description"
    )

    # Style guidance
    dialogue_type: DialogueType = Field(
        default=DialogueType.DIRECT,
        description="Preferred dialogue type"
    )
    target_tone: DialogueTone = Field(
        default=DialogueTone.CASUAL,
        description="Target overall tone"
    )
    dialogue_ratio: float = Field(
        default=0.4,
        description="Target ratio of dialogue to total text (0-1)"
    )

    # Pacing
    pacing: str = Field(
        default="moderate",
        description="Pacing: slow, moderate, fast"
    )
    tension_level: str = Field(
        default="moderate",
        description="Tension: low, moderate, high, climactic"
    )

    # Length targets
    target_line_count: int = Field(
        default=10,
        description="Target number of dialogue lines"
    )
    target_word_count: int = Field(
        default=500,
        description="Target total word count"
    )

    # Plot integration
    plot_points_to_cover: list[str] = Field(
        default_factory=list,
        description="Plot points to convey through dialogue"
    )
    information_to_reveal: list[str] = Field(
        default_factory=list,
        description="Information to reveal in dialogue"
    )
    secrets_to_keep: list[str] = Field(
        default_factory=list,
        description="Secrets that should NOT be revealed"
    )

    # Character relationship context
    relationship_type: str = Field(
        default="neutral",
        description="Relationship between speakers: friendly, hostile, romantic, professional, etc."
    )
    relationship_history: str = Field(
        default="",
        description="History between the characters"
    )

    # Emotional arc
    starting_emotion: str = Field(
        default="neutral",
        description="Starting emotional state"
    )
    ending_emotion: str = Field(
        default="neutral",
        description="Ending emotional state after dialogue"
    )

    # Style customization
    include_subtext: bool = Field(
        default=True,
        description="Whether to include subtext/double meanings"
    )
    include_gestures: bool = Field(
        default=True,
        description="Whether to include gesture descriptions"
    )
    include_interruptions: bool = Field(
        default=False,
        description="Whether to include dialogue interruptions"
    )


class DialogueDraft(BaseModel):
    """Generated dialogue draft."""

    id: str = Field(description="Unique draft ID")
    plan_id: str = Field(description="Associated plan ID")
    scene_id: str = Field(description="Associated scene ID")

    # Content
    exchanges: list[DialogueExchange] = Field(
        default_factory=list,
        description="Generated dialogue exchanges"
    )
    combined_text: str = Field(
        default="",
        description="Combined dialogue text for integration"
    )

    # Word count
    total_line_count: int = Field(
        default=0,
        description="Total number of dialogue lines"
    )
    total_word_count: int = Field(
        default=0,
        description="Total word count"
    )

    # Quality metrics
    naturalness_score: float = Field(
        default=0.0,
        description="Naturalness score (0-1)"
    )
    character_voice_score: float = Field(
        default=0.0,
        description="Character voice consistency score (0-1)"
    )
    purpose_fulfillment_score: float = Field(
        default=0.0,
        description="Purpose fulfillment score (0-1)"
    )

    # Flags
    has_plot_advancement: bool = Field(
        default=False,
        description="Contains meaningful plot advancement"
    )
    has_character_development: bool = Field(
        default=False,
        description="Reveals character development"
    )
    has_tension: bool = Field(
        default=False,
        description="Contains building tension"
    )

    # Status
    status: str = Field(
        default="draft",
        description="Status: draft, revised, finalized"
    )


class DialogueRevision(BaseModel):
    """Revision details for dialogue."""

    original_draft: DialogueDraft = Field(
        description="Original draft"
    )
    revision_notes: list[str] = Field(
        default_factory=list,
        description="What to revise"
    )
    revised_exchanges: list[DialogueExchange] = Field(
        default_factory=list,
        description="Revised dialogue exchanges"
    )
    quality_score: Optional[float] = Field(
        default=None,
        description="Quality score after revision (0-1)"
    )


class DialogueAnalysis(BaseModel):
    """Analysis of dialogue quality."""

    draft_id: str = Field(description="Draft ID analyzed")

    # Character voice analysis
    character_voice_consistency: dict[str, float] = Field(
        default_factory=dict,
        description="Voice consistency score per character (0-1)"
    )
    speech_pattern_adherence: float = Field(
        default=0.0,
        description="Adherence to established speech patterns (0-1)"
    )

    # Naturalness analysis
    naturalness_score: float = Field(
        default=0.0,
        description="Overall naturalness (0-1)"
    )
    dialogue_flow_score: float = Field(
        default=0.0,
        description="Flow between lines (0-1)"
    )

    # Purpose analysis
    purpose_clarity: float = Field(
        default=0.0,
        description="Clarity of dialogue purpose (0-1)"
    )
    information_transfer: float = Field(
        default=0.0,
        description="Effective information transfer (0-1)"
    )

    # Emotional authenticity
    emotional_authenticity: float = Field(
        default=0.0,
        description="Emotional truthfulness (0-1)"
    )
    subtext_effectiveness: float = Field(
        default=0.0,
        description="Subtext effectiveness (0-1)"
    )

    # Context fit
    situation_appropriateness: float = Field(
        default=0.0,
        description="Appropriateness to situation (0-1)"
    )
    relationship_consistency: float = Field(
        default=0.0,
        description="Consistency with relationship dynamic (0-1)"
    )

    # Overall scores
    overall_quality_score: float = Field(
        default=0.0,
        description="Overall quality score (0-1)"
    )

    # Issues and recommendations
    critical_issues: list[str] = Field(
        default_factory=list,
        description="Critical issues that must be fixed"
    )
    minor_issues: list[str] = Field(
        default_factory=list,
        description="Minor issues to improve"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )


class DialogueTemplate(BaseModel):
    """Template for dialogue generation by situation type."""

    id: str = Field(description="Template ID")
    name: str = Field(description="Template name")

    # Applicable purposes
    applicable_purposes: list[DialoguePurpose] = Field(
        default_factory=list,
        description="Dialogue purposes this template fits"
    )
    applicable_tones: list[DialogueTone] = Field(
        default_factory=list,
        description="Tones this template fits"
    )

    # Structure guidance
    typical_line_count: int = Field(
        default=10,
        description="Typical number of lines"
    )
    typical_participants: int = Field(
        default=2,
        description="Typical number of participants"
    )

    # Pacing
    pacing_pattern: str = Field(
        default="moderate",
        description="Typical pacing pattern"
    )
    tension_curve: list[str] = Field(
        default_factory=list,
        description="Expected tension progression"
    )

    # Content patterns
    opening_pattern: str = Field(
        default="",
        description="How dialogue typically opens"
    )
    development_pattern: str = Field(
        default="",
        description="How dialogue typically develops"
    )
    closing_pattern: str = Field(
        default="",
        description="How dialogue typically closes"
    )

    # Style guidance
    dialogue_style: DialogueType = Field(
        default=DialogueType.DIRECT,
        description="Typical dialogue type"
    )
    subtext_depth: str = Field(
        default="moderate",
        description="Typical subtext level: subtle, moderate, deep"
    )

    # Example phrases
    typical_opening_phrases: list[str] = Field(
        default_factory=list,
        description="Typical opening phrases"
    )
    transition_phrases: list[str] = Field(
        default_factory=list,
        description="Typical transition phrases"
    )
    closing_phrases: list[str] = Field(
        default_factory=list,
        description="Typical closing phrases"
    )
