"""Grammar and typo check models for quality assurance."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class GrammarErrorType(str, Enum):
    """Types of grammar errors."""
    # Structural errors
    INCOMPLETE_SENTENCE = "incomplete_sentence"  # 句子不完整
    RUN_ON_SENTENCE = "run_on_sentence"  # 句子冗长/流水句
    FRAGMENT = "fragment"  # 片段/残句

    # 的/地/得 errors
    DE_CONFUSION = "de_confusion"  # 的/地/得混淆
    MISSING_DE = "missing_de"  # 缺少的/地/得
    EXTRA_DE = "extra_de"  # 多余的/地/得

    # 了 errors
    REPEATED_LE = "repeated_le"  # 了重复使用
    MISSING_LE = "missing_le"  # 缺少了
    EXTRA_LE = "extra_le"  # 多余的了

    # Punctuation errors
    MISSING_PUNCTUATION = "missing_punctuation"  # 缺少标点
    EXTRA_PUNCTUATION = "extra_punctuation"  # 多余标点
    PUNCTUATION_CONFUSION = "punctuation_confusion"  # 标点混用

    # Word choice errors
    WRONG_WORD = "wrong_word"  # 用词不当
    REDUNDANT_WORD = "redundant_word"  # 冗余用词
    colloquial_INAPPROPRIATE = "colloquial_inappropriate"  # 口语化不当

    # Typo errors
    TYPO = "typo"  # 错别字
    HOMOPHONE_ERROR = "homophone_error"  # 同音字错误
    CHARACTER_CONFUSION = "character_confusion"  # 形近字错误

    # Subject-verb agreement
    SUBJECT_VERB_DISAGREEMENT = "subject_verb_disagreement"  # 主谓不一致

    # Preposition errors
    WRONG_PREPOSITION = "wrong_preposition"  # 介词错误
    MISSING_PREPOSITION = "missing_preposition"  # 缺少介词

    # Parallel structure
    PARALLEL_ERROR = "parallel_error"  # 并列结构错误

    # Pronoun errors
    PRONOUN_AMBIGUITY = "pronoun_ambiguity"  # 代词指代不明
    PRONOUN_ERROR = "pronoun_error"  # 代词错误


class GrammarErrorSeverity(str, Enum):
    """Severity of grammar errors."""
    CRITICAL = "critical"  # 严重错误，影响理解
    MAJOR = "major"  # 较大错误
    MINOR = "minor"  # 小错误
    TYPOGRAPHICAL = "typographical"  # 排版/格式问题


class GrammarError(BaseModel):
    """A detected grammar or typo error."""
    error_id: str = Field(description="Unique error identifier")
    chapter: int = Field(description="Chapter where error is found")
    sentence: str = Field(description="The sentence containing the error")
    position: int = Field(default=0, description="Character position in chapter")
    error_type: GrammarErrorType = Field(description="Type of error")
    severity: GrammarErrorSeverity = Field(description="Error severity")
    original_text: str = Field(description="Original text with error")
    suggested_fix: str = Field(default="", description="Suggested correction")
    description: str = Field(description="Description of the error")
    ai_suggested_fix: Optional[str] = Field(default=None, description="AI-generated fix suggestion")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Detection confidence")


class GrammarCheckResult(BaseModel):
    """Result of checking a single passage or sentence."""
    passage: str = Field(description="The checked passage")
    passage_type: str = Field(default="", description="Type: dialogue, narration, etc.")
    error_count: int = Field(default=0, description="Number of errors found")
    errors: list[GrammarError] = Field(default_factory=list, description="Detected errors")
    grammar_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Grammar score for this passage")
    has_critical_errors: bool = Field(default=False, description="Whether critical errors exist")


class ChapterGrammarProfile(BaseModel):
    """Grammar profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Statistics
    total_sentences: int = Field(default=0, description="Total sentences")
    total_characters: int = Field(default=0, description="Total characters")
    dialogue_sentences: int = Field(default=0, description="Dialogue sentences")
    narration_sentences: int = Field(default=0, description="Narration sentences")

    # Error counts by type
    error_counts: dict[str, int] = Field(default_factory=dict, description="Errors by type")
    total_errors: int = Field(default=0, description="Total errors")

    # Severity distribution
    critical_errors: int = Field(default=0, description="Critical errors")
    major_errors: int = Field(default=0, description="Major errors")
    minor_errors: int = Field(default=0, description="Minor errors")
    typographical_errors: int = Field(default=0, description="Typographical errors")

    # Scores
    grammar_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall grammar score")
    typo_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Typo score")
    punctuation_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Punctuation score")

    # Dialogue specific
    dialogue_errors: int = Field(default=0, description="Errors in dialogue")
    narration_errors: int = Field(default=0, description="Errors in narration")

    # Quality indicators
    is_well_written: bool = Field(default=True, description="Whether chapter is well written")
    needs_revision: bool = Field(default=False, description="Whether chapter needs revision")


class GrammarCheckAnalysis(BaseModel):
    """Comprehensive grammar and typo analysis for a novel."""
    # Overall scores
    overall_grammar_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_typo_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_punctuation_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters checked")
    total_sentences: int = Field(default=0, description="Total sentences")
    total_errors: int = Field(default=0, description="Total errors found")

    # Error distribution by type
    errors_by_type: dict[str, int] = Field(default_factory=dict, description="Error counts by type")

    # Severity distribution
    critical_count: int = Field(default=0, description="Critical errors")
    major_count: int = Field(default=0, description="Major errors")
    minor_count: int = Field(default=0, description="Minor errors")
    typographical_count: int = Field(default=0, description="Typographical errors")

    # Per-chapter analysis
    chapter_profiles: list[ChapterGrammarProfile] = Field(default_factory=list)

    # All detected errors
    all_errors: list[GrammarError] = Field(default_factory=list, description="All errors")

    # Common errors
    common_typos: list[tuple[str, int]] = Field(default_factory=list, description="Common typos (word, count)")
    common_grammar_errors: list[tuple[str, int]] = Field(default_factory=list, description="Common grammar errors")

    # Quality indicators
    chapters_needing_revision: list[int] = Field(default_factory=list, description="Chapters needing revision")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class GrammarCheckRevision(BaseModel):
    """Revision suggestion for a grammar error."""
    error_id: str = Field(description="Error identifier")
    chapter: int = Field(description="Chapter number")
    original_text: str = Field(description="Original text")
    suggested_fix: str = Field(description="Suggested fix")
    revision_type: str = Field(default="", description="Type of revision")
    priority: int = Field(default=0, description="Priority for this revision")
    changes_made: list[str] = Field(default_factory=list, description="Changes to be made")


class GrammarCheckPlan(BaseModel):
    """Plan for fixing grammar and typo errors."""
    # Errors to fix
    critical_to_fix: list[str] = Field(default_factory=list, description="Critical error IDs")
    major_to_fix: list[str] = Field(default_factory=list, description="Major error IDs")
    minor_to_fix: list[str] = Field(default_factory=list, description="Minor error IDs")

    # Chapters needing work
    chapters_to_revise: list[int] = Field(default_factory=list, description="Chapters to revise")

    # Priority order (error_id, priority)
    priority_order: list[tuple[str, int]] = Field(default_factory=list)

    # Estimated work
    estimated_fixes: int = Field(default=0, description="Estimated number of fixes")
    ai_assistance_needed: bool = Field(default=True, description="Whether AI assistance is needed")

    # Focus areas
    focus_on_typos: bool = Field(default=True, description="Focus on typo fixes")
    focus_on_grammar: bool = Field(default=True, description="Focus on grammar fixes")
    focus_on_punctuation: bool = Field(default=True, description="Focus on punctuation fixes")


class GrammarCheckReport(BaseModel):
    """Final report for grammar and typo check."""
    analysis: GrammarCheckAnalysis = Field(description="Complete analysis")
    revision_plan: GrammarCheckPlan = Field(description="Plan for revisions")

    # Summary
    summary: str = Field(default="", description="Human-readable summary")

    # Revisions
    revisions_completed: list[GrammarCheckRevision] = Field(default_factory=list)

    # Final status
    final_grammar_score: Optional[float] = Field(default=None)
    improvement_achieved: Optional[float] = Field(default=None)


class TypoPattern(BaseModel):
    """A typo pattern for detection."""
    pattern: str = Field(description="The typo pattern (wrong form)")
    correction: str = Field(description="The correct form")
    error_type: GrammarErrorType = Field(default=GrammarErrorType.TYPO)
    examples: list[str] = Field(default_factory=list, description="Example occurrences")


class GrammarPattern(BaseModel):
    """A grammar pattern for detection."""
    pattern: str = Field(description="Regex pattern to match")
    error_type: GrammarErrorType = Field(description="Type of grammar error")
    description: str = Field(description="Description of the error")
    example_wrong: str = Field(default="", description="Wrong example")
    example_correct: str = Field(default="", description="Correct example")
    severity: GrammarErrorSeverity = Field(default=GrammarErrorSeverity.MINOR)