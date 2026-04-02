"""Style consistency models for maintaining narrative voice and tone throughout the novel."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StyleConsistencyType(str, Enum):
    """Types of style consistency to maintain."""
    TONE = "tone"                          # Overall narrative tone
    VOICE = "voice"                        # Narrative voice (first-person, third omniscient, etc.)
    PACING = "pacing"                      # Pacing consistency
    DESCRIPTIVE_DENSITY = "descriptive_density"  # Level of descriptive detail
    DIALOGUE_RATIO = "dialogue_ratio"      # Balance of dialogue to narration
    SENTENCE_STRUCTURE = "sentence_structure"    # Complexity of sentences
    VOCABULARY = "vocabulary"              # Lexical consistency
    EMOTIONAL_TONE = "emotional_tone"      # Emotional register
    PERSPECTIVE = "perspective"            # Point of view consistency


class NarrativeTone(str, Enum):
    """Narrative tone types."""
    EPIC = "epic"                          # Grand, heroic, sweeping
    DRAMATIC = "dramatic"                  # Intense, emotional, weighty
    LYRICAL = "lyrical"                    # Poetic, flowing, musical
    INTIMATE = "intimate"                  # Personal, close, revealing
    MYSTERIOUS = "mysterious"              # Eerie, suspenseful, puzzling
    ROMANTIC = "romantic"                  # Love, passion, sentiment
    DARK = "dark"                          # Grim, bleak, foreboding
    LIGHT = "light"                        # Humorous, cheerful, optimistic
    GRITTY = "gritty"                      # Raw, realistic, harsh
    WHIMSICAL = "whimsical"                # Playful, fantastical, quirky
    SUSPENSEFUL = "suspenseful"            # Tense, gripping, uncertain
    NOSTALGIC = "nostalgic"                # Reflective, longing, bittersweet


class NarrativeVoice(str, Enum):
    """Narrative voice types."""
    THIRD_OMNISCIENT = "third_omniscient"  # All-knowing narrator
    THIRD_LIMITED = "third_limited"        # Limited to one character's perspective
    FIRST_PERSON = "first_person"          # First-person narrator
    SECOND_PERSON = "second_person"        # "You" perspective
    STREAM_OF_CONSCIOUSNESS = "stream_of_consciousness"  # Interior thoughts


class PacingLevel(str, Enum):
    """Pacing levels."""
    FAST = "fast"                          # Quick, action-packed
    MODERATE = "moderate"                  # Balanced flow
    SLOW = "slow"                          # Detailed, contemplative


class DescriptiveDensity(str, Enum):
    """Descriptive density levels."""
    HIGH = "high"                          # Rich, detailed descriptions
    MEDIUM = "medium"                      # Balanced
    LOW = "low"                            # Sparse, minimal


class SentenceComplexity(str, Enum):
    """Sentence complexity levels."""
    SIMPLE = "simple"                      # Short, declarative sentences
    MIXED = "mixed"                         # Varied sentence lengths
    COMPLEX = "complex"                     # Long, compound-complex


class VocabularyLevel(str, Enum):
    """Vocabulary sophistication levels."""
    SIMPLE = "simple"                      # Everyday language
    MODERATE = "moderate"                  # General vocabulary
    SOPHISTICATED = "sophisticated"        # Literary, elevated
    SCHOLARLY = "scholarly"                # Technical, academic


class StyleConsistencyIssue(str, Enum):
    """Types of style consistency issues."""
    TONE_SHIFT = "tone_shift"              # Abrupt tone change
    VOICE_BREAK = "voice_break"            # Narrative voice inconsistency
    PACING_INCONSISTENCY = "pacing_inconsistency"  # Uneven pacing
    DENSITY_SHIFT = "density_shift"        # Descriptive density change
    DIALOGUE_NARRATION_IMBALANCE = "dialogue_narration_imbalance"  # Ratio change
    SENTENCE_STRUCTURE_INCONSISTENCY = "sentence_structure_inconsistency"
    VOCABULARY_DRIFT = "vocabulary_drift"  # Lexical inconsistency
    EMOTIONAL_TONE_INCONSISTENCY = "emotional_tone_inconsistency"
    PERSPECTIVE_SHIFT = "perspective_shift"  # POV changes within scene


class StyleConsistencyStatus(str, Enum):
    """Status of style consistency check."""
    CONSISTENT = "consistent"              # Fully consistent
    MINOR_ISSUES = "minor_issues"          # Small inconsistencies
    MAJOR_ISSUES = "major_issues"          # Significant problems
    INCONSISTENT = "inconsistent"          # Serious inconsistencies


class StyleConsistencyCheck(BaseModel):
    """Result of a style consistency check."""
    check_type: StyleConsistencyType = Field(
        description="Type of consistency check performed"
    )
    status: StyleConsistencyStatus = Field(
        description="Consistency status"
    )
    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Consistency score from 0 to 1"
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of specific issues found"
    )
    chapter_number: Optional[int] = Field(
        default=None,
        description="Chapter number if check was per-chapter"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class StyleProfile(BaseModel):
    """Complete style profile for a novel or character."""

    # Overall tone
    tones: list[NarrativeTone] = Field(
        default_factory=list,
        description="Primary narrative tones"
    )
    dominant_tone: NarrativeTone = Field(
        default=NarrativeTone.DRAMATIC,
        description="Dominant tone in the narrative"
    )

    # Voice
    narrative_voice: NarrativeVoice = Field(
        default=NarrativeVoice.THIRD_OMNISCIENT,
        description="Narrative voice type"
    )

    # Pacing
    pacing: PacingLevel = Field(
        default=PacingLevel.MODERATE,
        description="Overall pacing level"
    )
    pacing_variation: list[tuple[str, PacingLevel]] = Field(
        default_factory=list,
        description="Pacing by chapter/section as (identifier, level) tuples"
    )

    # Description
    descriptive_density: DescriptiveDensity = Field(
        default=DescriptiveDensity.MEDIUM,
        description="Level of descriptive detail"
    )

    # Dialogue
    dialogue_ratio: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Proportion of dialogue to narration (0.0 to 1.0)"
    )

    # Sentence structure
    sentence_structure: SentenceComplexity = Field(
        default=SentenceComplexity.MIXED,
        description="Sentence complexity"
    )

    # Vocabulary
    vocabulary_level: VocabularyLevel = Field(
        default=VocabularyLevel.MODERATE,
        description="Lexical sophistication"
    )

    # Emotional tone
    emotional_tone: str = Field(
        default="neutral",
        description="Overall emotional register"
    )

    # Perspective consistency
    perspective_consistent: bool = Field(
        default=True,
        description="Whether POV is consistent"
    )

    # Character voice profiles
    character_voices: dict[str, str] = Field(
        default_factory=dict,
        description="Character ID to voice description mapping"
    )


class StyleConsistencyAnalysis(BaseModel):
    """Comprehensive style consistency analysis."""
    overall_status: StyleConsistencyStatus = Field(
        description="Overall consistency status"
    )
    overall_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall consistency score"
    )

    # Individual checks
    tone_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Tone consistency check"
    )
    voice_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Voice consistency check"
    )
    pacing_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Pacing consistency check"
    )
    descriptive_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Descriptive density check"
    )
    dialogue_ratio_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Dialogue ratio check"
    )
    sentence_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Sentence structure check"
    )
    vocabulary_check: Optional[StyleConsistencyCheck] = Field(
        default=None,
        description="Vocabulary consistency check"
    )

    # All issues
    all_issues: list[str] = Field(
        default_factory=list,
        description="All consistency issues found"
    )
    all_recommendations: list[str] = Field(
        default_factory=list,
        description="All recommendations"
    )

    # Chapter-specific issues
    chapter_issues: dict[int, list[str]] = Field(
        default_factory=dict,
        description="Issues by chapter number"
    )


class StyleConsistencyPlan(BaseModel):
    """Plan for maintaining style consistency."""
    style_profile: StyleProfile = Field(
        description="Target style profile"
    )
    consistency_checks: list[StyleConsistencyCheck] = Field(
        default_factory=list,
        description="Planned consistency checks"
    )
    target_chapters: Optional[list[int]] = Field(
        default=None,
        description="Specific chapters to check (None = all)"
    )
    ai_polishing_enabled: bool = Field(
        default=True,
        description="Whether AI polishing is enabled"
    )


class StyleConsistencyRevision(BaseModel):
    """Revision of content for style consistency."""
    original_content: str = Field(
        description="Original content"
    )
    revised_content: str = Field(
        description="Revised content after consistency fixes"
    )
    changes_made: list[str] = Field(
        default_factory=list,
        description="Description of changes made"
    )
    issues_fixed: list[str] = Field(
        default_factory=list,
        description="Issues that were addressed"
    )
    issues_remaining: list[str] = Field(
        default_factory=list,
        description="Issues that still need attention"
    )


class StyleConsistencyTemplate(BaseModel):
    """Template for style consistency configuration."""
    template_name: str = Field(
        description="Name of the template"
    )
    template_description: str = Field(
        description="Description of when to use this template"
    )

    # Style profile for this template
    tones: list[NarrativeTone] = Field(
        default_factory=list,
        description="Target tones"
    )
    narrative_voice: NarrativeVoice = Field(
        description="Target narrative voice"
    )
    pacing: PacingLevel = Field(
        description="Target pacing"
    )
    descriptive_density: DescriptiveDensity = Field(
        description="Target descriptive density"
    )
    dialogue_ratio: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Target dialogue ratio"
    )
    sentence_structure: SentenceComplexity = Field(
        description="Target sentence complexity"
    )
    vocabulary_level: VocabularyLevel = Field(
        description="Target vocabulary level"
    )

    # Consistency rules
    strict_tone_matching: bool = Field(
        default=True,
        description="Whether tone must strictly match"
    )
    strict_voice_matching: bool = Field(
        default=True,
        description="Whether narrative voice must strictly match"
    )
    allow_pacing_variation: bool = Field(
        default=True,
        description="Whether pacing can vary by chapter type"
    )
    character_voice_preservation: bool = Field(
        default=True,
        description="Whether to preserve individual character voices"
    )

    def to_style_profile(self) -> StyleProfile:
        """Convert template to StyleProfile."""
        return StyleProfile(
            tones=self.tones,
            dominant_tone=self.tones[0] if self.tones else NarrativeTone.DRAMATIC,
            narrative_voice=self.narrative_voice,
            pacing=self.pacing,
            descriptive_density=self.descriptive_density,
            dialogue_ratio=self.dialogue_ratio,
            sentence_structure=self.sentence_structure,
            vocabulary_level=self.vocabulary_level,
        )


class StyleConsistencyDraft(BaseModel):
    """Draft content with style consistency applied."""
    content: str = Field(
        description="Draft content"
    )
    target_profile: StyleProfile = Field(
        description="Style profile applied"
    )
    applied_templates: list[str] = Field(
        default_factory=list,
        description="Templates used"
    )
    consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Achieved consistency score"
    )
    notes: str = Field(
        default="",
        description="Notes about the draft"
    )


class CharacterVoiceProfile(BaseModel):
    """Individual character voice profile for consistency."""
    character_id: str = Field(
        description="Character ID"
    )
    character_name: str = Field(
        description="Character name"
    )

    # Speech characteristics
    speech_pattern: str = Field(
        default="",
        description="Overall speech pattern description"
    )
    vocabulary_level: VocabularyLevel = Field(
        default=VocabularyLevel.MODERATE,
        description="Character's vocabulary level"
    )
    sentence_structure: SentenceComplexity = Field(
        default=SentenceComplexity.MIXED,
        description="Character's sentence complexity"
    )

    # Language traits
    formality_level: str = Field(
        default="neutral",
        description="Formality: formal, neutral, informal, colloquial"
    )
    use_of_honorifics: bool = Field(
        default=True,
        description="Uses honorifics/titles"
    )
    dialect_or_accent: Optional[str] = Field(
        default=None,
        description="Dialect or accent description"
    )

    # Verbal habits
    catchphrases: list[str] = Field(
        default_factory=list,
        description="Character's catchphrases"
    )
    filler_words: list[str] = Field(
        default_factory=list,
        description="Filler words used"
    )
    verbal_tics: list[str] = Field(
        default_factory=list,
        description="Recurring verbal quirks"
    )

    # Emotional expression
    emotional_restraint: str = Field(
        default="moderate",
        description="suppressed, moderate, or expressive"
    )
    directness: str = Field(
        default="moderate",
        description="Direct vs indirect speech"
    )

    # Dialogue consistency
    consistency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Voice consistency score"
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Voice consistency issues"
    )
