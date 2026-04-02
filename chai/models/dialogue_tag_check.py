"""Dialogue tag standardization check models for quality assurance."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DialogueTagType(str, Enum):
    """Types of dialogue tags."""
    # Tag verbs
    SAID = "said"                    # 说
    ASKED = "asked"                  # 问
    ANSWERED = "answered"            # 答
    SHOUTED = "shouted"              # 喊/叫道
    WHISPERED = "whispered"          # 低语/轻声道
    CALLED = "called"                # 叫/喊道
    REPLIED = "replied"              # 回答
    RESPONDED = "responded"          # 回应
    EXCLAIMED = "exclaimed"          # 惊呼
    MUTTERED = "muttered"            # 喃喃道
    GROANED = "groaned"              # 呻吟道
    SIGHED = "sighed"                # 叹息道
    LAUGHED = "laughed"              # 笑道
    SMILED = "smiled"                # 笑着
    CRIED = "cried"                  # 哭道
    SOBBED = "sobbed"                # 泣道

    # Action tags
    ACTION = "action"                # 带动作的标签
    NO_TAG = "no_tag"                # 无标签（独立句子）


class DialogueTagIssueType(str, Enum):
    """Types of dialogue tag issues."""
    # Quote style issues
    INCONSISTENT_QUOTE_STYLE = "inconsistent_quote_style"      # 引号风格不统一
    MIXED_QUOTE_TYPES = "mixed_quote_types"                   # 混用不同引号

    # Tag verb issues
    INCONSISTENT_TAG_VERB = "inconsistent_tag_verb"            # 标签动词不统一
    NON_STANDARD_TAG = "non_standard_tag"                     # 非标准标签动词
    REDUNDANT_TAG = "redundant_tag"                           # 冗余标签

    # Tag placement issues
    INCONSISTENT_PLACEMENT = "inconsistent_placement"         # 标签位置不统一
    TAG_AFTER_COMMA = "tag_after_comma"                       # 标签前逗号使用不当

    # Action tag issues
    INCONSISTENT_ACTION = "inconsistent_action"               # 动作描写不统一
    MISSING_ACTION_TAG = "missing_action_tag"                 # 缺少动作标签
    EXTRA_ACTION_TAG = "extra_action_tag"                     # 过多动作标签

    # Punctuation issues
    MISSING_PUNCTUATION_BEFORE_TAG = "missing_punctuation_before_tag"
    EXTRA_PUNCTUATION_AFTER_TAG = "extra_punctuation_after_tag"
    PUNCTUATION_BEFORE_TAG_INCONSISTENT = "punctuation_before_tag_inconsistent"

    # Spacing issues
    INCONSISTENT_SPACING = "inconsistent_spacing"             # 空格不一致

    # Other issues
    TAG_WITH_QUOTE_MARKS = "tag_with_quote_marks"             # 标签与引号连用问题
    UNCLOSED_DIALOGUE = "unclosed_dialogue"                   # 未关闭的对话


class DialogueTagSeverity(str, Enum):
    """Severity of dialogue tag issues."""
    CRITICAL = "critical"   # 严重错误，影响阅读
    MAJOR = "major"         # 较大问题
    MINOR = "minor"         # 小问题
    TYPOGRAPHICAL = "typographical"  # 排版/格式问题


class DialogueTagStyle(str, Enum):
    """Dialogue tag styles."""
    # Quote styles
    CHINESE_MARKS = "chinese_marks"           # 「」
    CHINESE_SINGLE = "chinese_single"         # 『』
    STRAIGHT_DOUBLE = "straight_double"       # ""
    ANGLE_BRACKETS = "angle_brackets"         # <>
    MIXED = "mixed"                            # 混用

    # Tag placement
    TAG_AFTER = "tag_after"                   # 标签在引号后：「...」他说
    TAG_BEFORE = "tag_before"                  # 标签在引号前：他说：「...」
    TAG_INTERCALATED = "tag_intercalated"     # 标签在中间：「他说，...」

    # Style consistency
    CONSISTENT = "consistent"                 # 一致
    INCONSISTENT = "inconsistent"             # 不一致


class DialogueTagPattern(BaseModel):
    """Pattern for detecting specific dialogue tag issues."""
    pattern: str = Field(description="Regex pattern")
    issue_type: DialogueTagIssueType = Field(description="Type of issue detected")
    description: str = Field(description="Description of the issue")
    severity: DialogueTagSeverity = Field(description="Severity level")


class DialogueTagIssue(BaseModel):
    """A detected dialogue tag issue."""
    issue_id: str = Field(description="Unique issue identifier")
    chapter: int = Field(description="Chapter where issue is found")
    sentence: str = Field(description="The sentence containing the issue")
    position: int = Field(default=0, description="Character position in chapter")
    issue_type: DialogueTagIssueType = Field(description="Type of issue")
    severity: DialogueTagSeverity = Field(description="Issue severity")
    original_text: str = Field(description="Original text with issue")
    suggested_fix: str = Field(default="", description="Suggested correction")
    description: str = Field(description="Description of the issue")
    dialogue_tag_type: Optional[DialogueTagType] = Field(default=None, description="Detected tag type")
    quote_style: Optional[DialogueTagStyle] = Field(default=None, description="Quote style used")
    ai_suggested_fix: Optional[str] = Field(default=None, description="AI-generated fix suggestion")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Detection confidence")


class DialogueTagCheckResult(BaseModel):
    """Result of checking a single passage or sentence."""
    passage: str = Field(description="The checked passage")
    passage_type: str = Field(default="", description="Type: dialogue, narration, etc.")
    issue_count: int = Field(default=0, description="Number of issues found")
    issues: list[DialogueTagIssue] = Field(default_factory=list, description="Detected issues")
    tag_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Tag compliance score")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")


class ChapterDialogueTagProfile(BaseModel):
    """Dialogue tag profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Statistics
    total_dialogues: int = Field(default=0, description="Total dialogue instances")
    total_dialogue_lines: int = Field(default=0, description="Total dialogue lines")

    # Quote style distribution
    chinese_marks_count: int = Field(default=0, description="「」 count")
    chinese_single_count: int = Field(default=0, description="『』 count")
    straight_double_count: int = Field(default=0, description="\"\" count")
    other_quotes_count: int = Field(default=0, description="Other quotes count")

    # Tag verb usage
    tag_verb_counts: dict[str, int] = Field(default_factory=dict, description="Tag verb frequency")
    most_common_tag_verb: str = Field(default="", description="Most used tag verb")
    tag_verb_variety: int = Field(default=0, description="Unique tag verbs used")

    # Tag placement
    tag_after_count: int = Field(default=0, description="Tags after dialogue")
    tag_before_count: int = Field(default=0, description="Tags before dialogue")
    no_tag_count: int = Field(default=0, description="Dialogue without tags")

    # Action tags
    action_tag_count: int = Field(default=0, description="Dialogue with action tags")
    no_action_tag_count: int = Field(default=0, description="Dialogue without action tags")

    # Issue counts
    issue_counts: dict[str, int] = Field(default_factory=dict, description="Issues by type")
    total_issues: int = Field(default=0, description="Total issues")

    # Severity distribution
    critical_issues: int = Field(default=0, description="Critical issues")
    major_issues: int = Field(default=0, description="Major issues")
    minor_issues: int = Field(default=0, description="Minor issues")
    typographical_issues: int = Field(default=0, description="Typographical issues")

    # Scores
    tag_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall tag compliance score")
    quote_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quote style consistency")
    verb_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Tag verb consistency")
    placement_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Tag placement consistency")

    # Style consistency
    primary_quote_style: DialogueTagStyle = Field(default=DialogueTagStyle.CHINESE_MARKS, description="Primary quote style")
    is_style_consistent: bool = Field(default=True, description="Whether style is consistent")
    dominant_tag_placement: DialogueTagStyle = Field(default=DialogueTagStyle.TAG_BEFORE, description="Dominant tag placement")

    # Quality indicators
    needs_revision: bool = Field(default=False, description="Whether chapter needs tag revision")


class DialogueTagCheckAnalysis(BaseModel):
    """Comprehensive dialogue tag analysis for a novel."""
    # Overall scores
    overall_tag_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_quote_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_verb_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_placement_consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters checked")
    total_dialogues: int = Field(default=0, description="Total dialogue instances")
    total_dialogue_lines: int = Field(default=0, description="Total dialogue lines")

    # Quote style distribution
    quote_style_distribution: dict[str, int] = Field(default_factory=dict, description="Quote style counts")
    primary_quote_style: DialogueTagStyle = Field(default=DialogueTagStyle.CHINESE_MARKS, description="Primary quote style")
    is_quote_style_consistent: bool = Field(default=True, description="Whether quote style is consistent")

    # Tag verb statistics
    tag_verb_usage: dict[str, int] = Field(default_factory=dict, description="Tag verb frequency across novel")
    most_common_tag_verb: str = Field(default="", description="Most used tag verb in novel")
    tag_verb_variety: int = Field(default=0, description="Unique tag verbs used")

    # Tag placement statistics
    tag_placement_distribution: dict[str, int] = Field(default_factory=dict, description="Tag placement counts")
    dominant_placement: DialogueTagStyle = Field(default=DialogueTagStyle.TAG_BEFORE, description="Dominant placement")

    # Issue distribution by type
    issues_by_type: dict[str, int] = Field(default_factory=dict, description="Issue counts by type")

    # Severity distribution
    critical_count: int = Field(default=0, description="Critical issues")
    major_count: int = Field(default=0, description="Major issues")
    minor_count: int = Field(default=0, description="Minor issues")
    typographical_count: int = Field(default=0, description="Typographical issues")

    # Per-chapter analysis
    chapter_profiles: list[ChapterDialogueTagProfile] = Field(default_factory=list)

    # All detected issues
    all_issues: list[DialogueTagIssue] = Field(default_factory=list, description="All issues")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")


class DialogueTagCheckRevision(BaseModel):
    """Revision details for dialogue tag issues."""
    original_text: str = Field(description="Original text")
    revision_notes: list[str] = Field(default_factory=list, description="What to revise")
    revised_text: str = Field(default="", description="Revised text")
    quality_score: Optional[float] = Field(default=None, description="Quality score after revision (0-1)")


class DialogueTagCheckPlan(BaseModel):
    """Plan for dialogue tag revision."""
    chapter_number: int = Field(description="Chapter number")
    issues_to_fix: list[str] = Field(default_factory=list, description="Issue IDs to fix")
    target_quote_style: DialogueTagStyle = Field(default=DialogueTagStyle.CHINESE_MARKS, description="Target quote style")
    target_tag_placement: DialogueTagStyle = Field(default=DialogueTagStyle.TAG_BEFORE, description="Target tag placement")
    standardize_tag_verbs: bool = Field(default=True, description="Whether to standardize tag verbs")
    keep_action_tags: bool = Field(default=True, description="Whether to preserve action tags")
    revision_order: list[str] = Field(default_factory=list, description="Order of revisions")


class DialogueTagCheckReport(BaseModel):
    """Comprehensive report for dialogue tag check."""
    analysis: DialogueTagCheckAnalysis = Field(description="Analysis results")
    revision_plan: Optional[DialogueTagCheckPlan] = Field(default=None, description="Revision plan")
    summary: str = Field(default="", description="Human-readable summary")
    priority_fixes: list[DialogueTagIssue] = Field(default_factory=list, description="Issues to fix first")


class DialogueTagTemplate(BaseModel):
    """Template for dialogue tag standardization."""
    id: str = Field(description="Template ID")
    name: str = Field(description="Template name")

    # Quote style
    quote_style: DialogueTagStyle = Field(description="Preferred quote style")
    example_before: str = Field(default="", description="Example before")
    example_after: str = Field(default="", description="Example after")

    # Tag placement
    tag_placement: DialogueTagStyle = Field(description="Preferred tag placement")

    # Preferred tag verbs
    preferred_tag_verbs: list[str] = Field(default_factory=list, description="List of preferred tag verbs")
    discouraged_tag_verbs: list[str] = Field(default_factory=list, description="List of discouraged tag verbs")

    # Punctuation rules
    punctuation_before_tag: str = Field(default="，", description="Punctuation before tag")
    punctuation_after_tag: str = Field(default="：", description="Punctuation after tag")
