"""Dialogue naturalness models for validating character dialogue quality."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DialogueNaturalnessType(str, Enum):
    """Types of dialogue naturalness issues."""
    # Speech pattern issues
    SPEECH_PATTERN_MISMATCH = "speech_pattern_mismatch"  # Dialogue doesn't match established pattern
    VOCABULARY_INCONSISTENT = "vocabulary_inconsistent"   # Vocabulary level mismatch
    FORMALITY_INCONSISTENT = "formality_inconsistent"    # Formality level mismatch

    # Character voice issues
    CHARACTER_VOICE_BREAK = "character_voice_break"      # Character speaks out of character
    EMOTIONAL_TONE_MISMATCH = "emotional_tone_mismatch"  # Emotional response inconsistent
    SPEECH_QUIRK_MISSING = "speech_quirk_missing"        # Character's unique quirks not present
    CATCHPHRASE_MISSING = "catchphrase_missing"          # Expected catchphrase not used

    # Naturalness issues
    UNNATURAL_PHRASING = "unnatural_phrasing"            # Phrasing sounds unnatural
    ROBOTIC_SPEECH = "robotic_speech"                   # Sounds like AI/generated
    MONOTONE_RESPONSE = "monotone_response"              # All responses sound the same
    CONTEXT_APPROPRIATENESS = "context_appropriateness"  # Dialogue doesn't fit situation

    # Flow issues
    CONVERSATION_FLOW_POOR = "conversation_flow_poor"    # Conversation doesn't flow naturally
    RESPONSE_MISMATCH = "response_mismatch"              # Response doesn't address previous line
    PACING_ISSUES = "pacing_issues"                     # Pacing too fast/slow

    # Relationship issues
    RELATIONSHIP_DYNAMIC_INCONSISTENT = "relationship_dynamic_inconsistent"  # Power dynamic wrong

    # Information issues
    INFORMATION_TRANSFER_POOR = "information_transfer_poor"  # Information not conveyed clearly
    REVEAL_TOO_ABRUPT = "reveal_too_abrupt"               # Important reveal feels rushed


class DialogueNaturalnessSeverity(str, Enum):
    """Severity of dialogue naturalness issues."""
    MINOR = "minor"      # Small improvement suggestions
    MODERATE = "moderate"  # Should be addressed
    SEVERE = "severe"    # Breaks immersion, must fix


class CharacterDialogueProfile(BaseModel):
    """Character profile for dialogue naturalness checking."""

    character_id: str = Field(description="Character ID")
    character_name: str = Field(description="Character name")

    # Speech characteristics
    speech_pattern: str = Field(
        default="",
        description="Overall speech pattern description"
    )
    vocabulary_level: str = Field(
        default="moderate",
        description="Vocabulary level: simple, moderate, sophisticated"
    )
    formality_level: str = Field(
        default="neutral",
        description="Formality: formal, neutral, informal, colloquial"
    )
    sentence_structure: str = Field(
        default="mixed",
        description="Sentence structure: short, long, mixed, fragmented"
    )

    # Verbal habits
    catchphrases: list[str] = Field(
        default_factory=list,
        description="Character's catchphrases"
    )
    filler_words: list[str] = Field(
        default_factory=list,
        description="Filler words character uses"
    )
    verbal_tics: list[str] = Field(
        default_factory=list,
        description="Recurring verbal habits"
    )
    speech_quirks: list[str] = Field(
        default_factory=list,
        description="Unique speech characteristics"
    )

    # Emotional patterns
    emotional_restraint: str = Field(
        default="moderate",
        description="Emotional restraint: suppressed, moderate, expressive"
    )
    emotional_triggers: list[str] = Field(
        default_factory=list,
        description="Topics that trigger emotional responses"
    )

    # Communication style
    directness: str = Field(
        default="moderate",
        description="Directness: indirect, moderate, direct"
    )
    passive_aggressive: bool = Field(
        default=False,
        description="Whether character uses passive-aggressive speech"
    )
    interruption_tendency: str = Field(
        default="rare",
        description="Interruption tendency: never, rare, occasional, frequent"
    )

    # Context
    background: str = Field(
        default="",
        description="Character background relevant to speech"
    )
    education_level: str = Field(
        default="moderate",
        description="Education level affecting speech"
    )


class DialogueLineCheck(BaseModel):
    """Check result for a single dialogue line."""

    line_index: int = Field(description="Line index in the dialogue")
    speaker_name: str = Field(description="Name of speaker")
    content: str = Field(description="Dialogue content")

    # Issue findings
    issues: list[str] = Field(
        default_factory=list,
        description="Issues found in this line"
    )
    issue_types: list[DialogueNaturalnessType] = Field(
        default_factory=list,
        description="Types of issues found"
    )
    severity: DialogueNaturalnessSeverity = Field(
        default=DialogueNaturalnessSeverity.MINOR,
        description="Overall severity"
    )

    # Quality scores (0-1)
    naturalness_score: float = Field(
        default=1.0,
        description="How natural this line sounds"
    )
    character_consistency_score: float = Field(
        default=1.0,
        description="Consistency with character voice"
    )
    context_fit_score: float = Field(
        default=1.0,
        description="Appropriateness to situation"
    )

    # Suggestions
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )


class DialogueExchangeCheck(BaseModel):
    """Check result for a dialogue exchange."""

    exchange_index: int = Field(description="Exchange index")
    participants: list[str] = Field(
        default_factory=list,
        description="Character names participating"
    )

    # Exchange-level checks
    line_checks: list[DialogueLineCheck] = Field(
        default_factory=list,
        description="Individual line check results"
    )

    # Flow analysis
    conversation_flow_score: float = Field(
        default=1.0,
        description="How naturally the conversation flows"
    )
    response_continuity_score: float = Field(
        default=1.0,
        description="Whether responses address previous lines"
    )
    pacing_score: float = Field(
        default=1.0,
        description="Appropriateness of pacing"
    )

    # Dynamics
    power_dynamic_score: float = Field(
        default=1.0,
        description="Appropriateness of power dynamics"
    )

    # Summary
    total_issues: int = Field(
        default=0,
        description="Total issues found"
    )
    severe_issues: int = Field(
        default=0,
        description="Severe issues count"
    )
    overall_score: float = Field(
        default=1.0,
        description="Overall exchange quality score"
    )


class ChapterDialogueProfile(BaseModel):
    """Profile of dialogue in a chapter."""

    chapter_id: str = Field(description="Chapter ID")
    chapter_title: str = Field(default="", description="Chapter title")

    # Dialogue statistics
    total_dialogue_lines: int = Field(
        default=0,
        description="Total number of dialogue lines"
    )
    total_exchanges: int = Field(
        default=0,
        description="Total number of exchanges"
    )
    speaking_characters: list[str] = Field(
        default_factory=list,
        description="Characters who speak in this chapter"
    )
    dialogue_ratio: float = Field(
        default=0.0,
        description="Ratio of dialogue to total text"
    )

    # Exchange results
    exchange_checks: list[DialogueExchangeCheck] = Field(
        default_factory=list,
        description="Results of each exchange check"
    )

    # Character-specific analysis
    character_dialogue_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Line count per character"
    )
    character_issue_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Issue count per character"
    )

    # Overall chapter scores
    overall_naturalness_score: float = Field(
        default=1.0,
        description="Overall dialogue naturalness"
    )
    overall_character_consistency_score: float = Field(
        default=1.0,
        description="Overall character voice consistency"
    )


class DialogueNaturalnessIssue(BaseModel):
    """A specific dialogue naturalness issue."""

    issue_type: DialogueNaturalnessType = Field(
        description="Type of issue"
    )
    severity: DialogueNaturalnessSeverity = Field(
        description="Severity level"
    )

    # Location
    chapter_id: Optional[str] = Field(
        default=None,
        description="Chapter where issue occurs"
    )
    exchange_index: int = Field(
        default=0,
        description="Exchange index"
    )
    line_index: int = Field(
        default=0,
        description="Line index within exchange"
    )
    speaker_name: str = Field(
        default="",
        description="Speaker involved"
    )

    # Details
    description: str = Field(
        description="Issue description"
    )
    current_content: str = Field(
        description="Current problematic content"
    )
    expected_pattern: Optional[str] = Field(
        default=None,
        description="Expected pattern if applicable"
    )

    # Fix guidance
    suggestion: str = Field(
        description="How to fix this issue"
    )


class DialogueNaturalnessAnalysis(BaseModel):
    """Analysis of dialogue naturalness across exchanges."""

    analysis_id: str = Field(description="Unique analysis ID")

    # Chapter profile
    chapter_profile: ChapterDialogueProfile = Field(
        description="Chapter-level dialogue profile"
    )

    # Issue summary
    issues: list[DialogueNaturalnessIssue] = Field(
        default_factory=list,
        description="All issues found"
    )
    issue_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues by type"
    )

    # Character-specific issues
    character_issues: dict[str, list[DialogueNaturalnessIssue]] = Field(
        default_factory=dict,
        description="Issues grouped by character"
    )

    # Quality metrics
    naturalness_score: float = Field(
        default=1.0,
        description="Overall naturalness (0-1)"
    )
    character_voice_score: float = Field(
        default=1.0,
        description="Character voice consistency (0-1)"
    )
    context_fit_score: float = Field(
        default=1.0,
        description="Situation appropriateness (0-1)"
    )
    conversation_flow_score: float = Field(
        default=1.0,
        description="Conversation flow (0-1)"
    )

    # Overall
    overall_score: float = Field(
        default=1.0,
        description="Overall dialogue quality score (0-1)"
    )

    # Counts
    total_lines: int = Field(default=0, description="Total dialogue lines analyzed")
    total_issues: int = Field(default=0, description="Total issues found")
    severe_issues: int = Field(default=0, description="Severe issues count")


class DialogueNaturalnessRevision(BaseModel):
    """Revision plan for dialogue naturalness issues."""

    analysis_id: str = Field(description="Associated analysis ID")

    # Issues to address
    priority_fixes: list[DialogueNaturalnessIssue] = Field(
        default_factory=list,
        description="High priority fixes (severe issues)"
    )
    suggested_fixes: list[DialogueNaturalnessIssue] = Field(
        default_factory=list,
        description="Medium priority fixes"
    )
    optional_improvements: list[DialogueNaturalnessIssue] = Field(
        default_factory=list,
        description="Low priority improvements"
    )

    # Character-specific guidance
    character_guidance: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Per-character improvement guidance"
    )

    # Overall revision direction
    revision_focus: list[str] = Field(
        default_factory=list,
        description="Main areas to focus revision on"
    )


class DialogueNaturalnessReport(BaseModel):
    """Comprehensive report for dialogue naturalness."""

    report_id: str = Field(description="Unique report ID")

    # Analysis results
    analyses: list[DialogueNaturalnessAnalysis] = Field(
        default_factory=list,
        description="Analyses per chapter"
    )

    # Aggregate statistics
    total_chapters_analyzed: int = Field(
        default=0,
        description="Number of chapters analyzed"
    )
    total_dialogue_lines: int = Field(
        default=0,
        description="Total dialogue lines"
    )
    total_exchanges: int = Field(
        default=0,
        description="Total exchanges"
    )

    # Issue statistics
    total_issues: int = Field(default=0, description="Total issues across all chapters")
    severe_issues: int = Field(default=0, description="Severe issues")
    moderate_issues: int = Field(default=0, description="Moderate issues")
    minor_issues: int = Field(default=0, description="Minor issues")

    # Issue breakdown by type
    issues_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Issue counts by type"
    )

    # Character statistics
    most_issues_character: Optional[str] = Field(
        default=None,
        description="Character with most issues"
    )
    best_voice_character: Optional[str] = Field(
        default=None,
        description="Character with most consistent voice"
    )

    # Overall scores
    overall_naturalness_score: float = Field(
        default=1.0,
        description="Overall naturalness"
    )
    overall_character_consistency_score: float = Field(
        default=1.0,
        description="Overall character consistency"
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
