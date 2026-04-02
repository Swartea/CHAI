"""Sentence quality check models for defective and redundant sentence optimization."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SentenceQualityType(str, Enum):
    """Types of sentence quality issues."""
    # 病句类型 (Defective sentence types)
    # 成分残缺 - missing sentence components
    MISSING_SUBJECT = "missing_subject"  # 缺主语
    MISSING_PREDICATE = "missing_predicate"  # 缺谓语
    MISSING_OBJECT = "missing_object"  # 缺宾语
    MISSING_MODIFIER = "missing_modifier"  # 缺定语/状语

    # 成分赘余 - redundant components
    REDUNDANT_SUBJECT = "redundant_subject"  # 多余主语
    REDUNDANT_PREDICATE = "redundant_predicate"  # 多余谓语
    REDUNDANT_OBJECT = "redundant_object"  # 多余宾语
    REDUNDANT_MODIFIER = "redundant_modifier"  # 多余修饰

    # 搭配不当 - collocation errors
    SUBJECT_PREDICATE_MISMATCH = "subject_predicate_mismatch"  # 主谓不搭配
    VERB_OBJECT_MISMATCH = "verb_object_mismatch"  # 动宾不搭配
    MODIFIER_MODIFIED_MISMATCH = "modifier_modified_mismatch"  # 修饰语与中心语不搭配

    # 语序不当 - improper word order
    ADJECTIVE_ORDER_WRONG = "adjective_order_wrong"  # 形容词语序不当
    ADVERB_POSITION_WRONG = "adverb_position_wrong"  # 副词位置不当
    CLAUSE_ORDER_WRONG = "clause_order_wrong"  # 从句顺序不当

    # 结构混乱 - structural confusion
    MIXED_STRUCTURE = "mixed_structure"  # 句式杂糅
    INCOMPLETE_PARALLEL = "incomplete_parallel"  # 并列结构不完整
    UNBALANCED_CONSTRUCTION = "unbalanced_construction"  # 句子结构不平衡

    # 语义不明 - unclear meaning
    PRONOUN_AMBIGUITY = "pronoun_ambiguity"  # 代词指代不明
    REFERENCE_UNCLEAR = "reference_unclear"  # 指示词指代不明
    VAGUE_EXPRESSION = "vague_expression"  # 表达含糊
    MULTIPLE_MEANINGS = "multiple_meanings"  # 一词多义歧义

    # 逻辑矛盾 - logical contradictions
    SELF_CONTRADICTION = "self_contradiction"  # 自相矛盾
    CAUSE_EFFECT_WRONG = "cause_effect_wrong"  # 因果关系错误
    CONDITION_LOGIC_WRONG = "condition_logic_wrong"  # 条件关系错误
    TIME_SEQUENCE_WRONG = "time_sequence_wrong"  # 时间顺序错误

    # 冗余句子类型 (Redundant sentence types)
    REPETITIVE_MEANING = "repetitive_meaning"  # 意思重复
    REDUNDANT_DESCRIPTION = "redundant_description"  # 描写冗余
    UNNECESSARY_EXPANSION = "unnecessary_expansion"  # 不必要的铺陈
    FILLER_PHRASE = "filler_phrase"  # 废话/填充词
    EMPTY_SENTENCE = "empty_sentence"  # 空洞无物
    TAUTOLOGICAL = "tautological"  # 同义反复
    WORDY_SENTENCE = "wordy_sentence"  # 句子冗长

    # 表达不当 - inappropriate expression
    COLLOQUIAL_INAPPROPRIATE = "colloquial_inappropriate"  # 口语化不当
    FORMAL_INAPPROPRIATE = "formal_inappropriate"  # 书面语不当
    EMOTIONAL_TONE_WRONG = "emotional_tone_wrong"  # 感情色彩不当
    REGISTER_MISMATCH = "register_mismatch"  # 语体风格不统一

    # 其他问题
    UNPARALLEL_STRUCTURE = "unparallel_structure"  # 不对称的并列
    INCONSISTENT_TENSE = "inconsistent_tense"  # 时态不一致
    MIXED_LANGUAGE = "mixed_language"  # 中英文混杂


class SentenceQualitySeverity(str, Enum):
    """Severity of sentence quality issues."""
    CRITICAL = "critical"  # 严重问题，影响理解
    MAJOR = "major"  # 较大问题
    MINOR = "minor"  # 小问题
    SUGGESTION = "suggestion"  # 建议优化


class SentenceQualityIssue(BaseModel):
    """A detected sentence quality issue."""
    issue_id: str = Field(description="Unique issue identifier")
    chapter: int = Field(description="Chapter where issue is found")
    sentence: str = Field(description="The sentence containing the issue")
    position: int = Field(default=0, description="Character position in chapter")
    issue_type: SentenceQualityType = Field(description="Type of quality issue")
    severity: SentenceQualitySeverity = Field(description="Issue severity")
    original_text: str = Field(description="Original text with issue")
    suggested_fix: str = Field(default="", description="Suggested correction")
    alternative_fixes: list[str] = Field(default_factory=list, description="Alternative fix suggestions")
    description: str = Field(description="Description of the issue")
    ai_suggested_fix: Optional[str] = Field(default=None, description="AI-generated fix suggestion")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Detection confidence")
    reason: str = Field(default="", description="Why this is an issue")


class SentenceQualityResult(BaseModel):
    """Result of checking a single passage or sentence."""
    passage: str = Field(description="The checked passage")
    passage_type: str = Field(default="", description="Type: dialogue, narration, etc.")
    issue_count: int = Field(default=0, description="Number of issues found")
    issues: list[SentenceQualityIssue] = Field(default_factory=list, description="Detected issues")
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quality score for this passage")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")


class ChapterSentenceQualityProfile(BaseModel):
    """Sentence quality profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Statistics
    total_sentences: int = Field(default=0, description="Total sentences")
    total_characters: int = Field(default=0, description="Total characters")
    dialogue_sentences: int = Field(default=0, description="Dialogue sentences")
    narration_sentences: int = Field(default=0, description="Narration sentences")

    # Issue counts by type
    issue_counts: dict[str, int] = Field(default_factory=dict, description="Issues by type")
    disease_counts: int = Field(default=0, description="Defective sentence count (病句)")
    redundancy_counts: int = Field(default=0, description="Redundant sentence count (冗余句子)")
    total_issues: int = Field(default=0, description="Total issues")

    # Severity distribution
    critical_issues: int = Field(default=0, description="Critical issues")
    major_issues: int = Field(default=0, description="Major issues")
    minor_issues: int = Field(default=0, description="Minor issues")
    suggestions: int = Field(default=0, description="Optimization suggestions")

    # Scores
    disease_sentence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Defective sentence score")
    redundancy_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Redundancy score")
    overall_quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall quality score")

    # Quality indicators
    needs_revision: bool = Field(default=False, description="Whether chapter needs revision")
    is_concise: bool = Field(default=True, description="Whether writing is concise")


class SentenceQualityAnalysis(BaseModel):
    """Comprehensive sentence quality analysis for a novel."""
    # Overall scores
    overall_disease_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_redundancy_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters checked")
    total_sentences: int = Field(default=0, description="Total sentences")
    total_disease_sentences: int = Field(default=0, description="Total defective sentences")
    total_redundant_sentences: int = Field(default=0, description="Total redundant sentences")
    total_issues: int = Field(default=0, description="Total issues found")

    # Issue distribution by type
    issues_by_type: dict[str, int] = Field(default_factory=dict, description="Issue counts by type")

    # Severity distribution
    critical_count: int = Field(default=0, description="Critical issues")
    major_count: int = Field(default=0, description="Major issues")
    minor_count: int = Field(default=0, description="Minor issues")
    suggestion_count: int = Field(default=0, description="Optimization suggestions")

    # Per-chapter analysis
    chapter_profiles: list[ChapterSentenceQualityProfile] = Field(default_factory=list)

    # All detected issues
    all_issues: list[SentenceQualityIssue] = Field(default_factory=list, description="All issues")

    # Common issues
    common_disease_types: list[tuple[str, int]] = Field(default_factory=list, description="Common disease sentence types")
    common_redundancy_types: list[tuple[str, int]] = Field(default_factory=list, description="Common redundancy types")

    # Quality indicators
    chapters_needing_revision: list[int] = Field(default_factory=list, description="Chapters needing revision")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class SentenceQualityRevision(BaseModel):
    """Revision suggestion for a sentence quality issue."""
    issue_id: str = Field(description="Issue identifier")
    chapter: int = Field(description="Chapter number")
    original_text: str = Field(description="Original text")
    suggested_fix: str = Field(description="Suggested fix")
    alternative_fixes: list[str] = Field(default_factory=list, description="Alternative fixes")
    revision_type: str = Field(default="", description="Type of revision: disease_fix or redundancy_optimization")
    priority: int = Field(default=0, description="Priority for this revision")
    changes_made: list[str] = Field(default_factory=list, description="Changes to be made")


class SentenceQualityPlan(BaseModel):
    """Plan for fixing sentence quality issues."""
    # Issues to fix
    critical_to_fix: list[str] = Field(default_factory=list, description="Critical issue IDs")
    major_to_fix: list[str] = Field(default_factory=list, description="Major issue IDs")
    minor_to_fix: list[str] = Field(default_factory=list, description="Minor issue IDs")
    suggestions_to_apply: list[str] = Field(default_factory=list, description="Suggestion IDs")

    # Categories
    disease_fixes: list[str] = Field(default_factory=list, description="Defective sentence IDs to fix")
    redundancy_optimizations: list[str] = Field(default_factory=list, description="Redundant sentence IDs to optimize")

    # Chapters needing work
    chapters_to_revise: list[int] = Field(default_factory=list, description="Chapters to revise")

    # Priority order (issue_id, priority)
    priority_order: list[tuple[str, int]] = Field(default_factory=list)

    # Estimated work
    estimated_disease_fixes: int = Field(default=0, description="Estimated disease sentence fixes")
    estimated_redundancy_optimizations: int = Field(default=0, description="Estimated redundancy optimizations")
    ai_assistance_needed: bool = Field(default=True, description="Whether AI assistance is needed")

    # Focus areas
    focus_on_disease_sentences: bool = Field(default=True, description="Focus on defective sentences")
    focus_on_redundancy: bool = Field(default=True, description="Focus on redundant sentences")


class SentenceQualityReport(BaseModel):
    """Final report for sentence quality check."""
    analysis: SentenceQualityAnalysis = Field(description="Complete analysis")
    revision_plan: SentenceQualityPlan = Field(description="Plan for revisions")

    # Summary
    summary: str = Field(default="", description="Human-readable summary")

    # Revisions
    revisions_completed: list[SentenceQualityRevision] = Field(default_factory=list)

    # Final status
    final_quality_score: Optional[float] = Field(default=None)
    improvement_achieved: Optional[float] = Field(default=None)


class DiseaseSentencePattern(BaseModel):
    """Pattern for detecting defective sentences (病句)."""
    pattern: str = Field(description="Regex pattern to match")
    issue_type: SentenceQualityType = Field(description="Type of issue")
    description: str = Field(description="Description of the disease")
    example_wrong: str = Field(default="", description="Wrong example")
    example_correct: str = Field(default="", description="Correct example")
    severity: SentenceQualitySeverity = Field(default=SentenceQualitySeverity.MAJOR)


class RedundancyPattern(BaseModel):
    """Pattern for detecting redundant sentences or phrases."""
    redundant_text: str = Field(description="The redundant text pattern")
    correction: str = Field(description="The corrected text")
    redundancy_type: SentenceQualityType = Field(description="Type of redundancy")
    description: str = Field(description="Description of why it's redundant")
    examples: list[str] = Field(default_factory=list, description="Example occurrences")


class SentenceQualityTemplate(BaseModel):
    """Template for sentence quality optimization."""
    template_name: str = Field(description="Name of the template")
    template_type: str = Field(description="Type: disease_fix or redundancy_optimization")
    pattern: str = Field(description="Pattern to match")
    replacement: str = Field(description="Replacement text")
    description: str = Field(description="What this template optimizes")
    examples: list[tuple[str, str]] = Field(default_factory=list, description="(before, after) examples")
