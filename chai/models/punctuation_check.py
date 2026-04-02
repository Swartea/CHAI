"""Punctuation standardization check models for quality assurance."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PunctuationErrorType(str, Enum):
    """Types of punctuation errors."""
    # Quote style issues
    MIXED_QUOTE_STYLE = "mixed_quote_style"                    # 引号风格混用
    INCONSISTENT_QUOTE_PAIR = "inconsistent_quote_pair"      # 引号不成对

    # Chinese vs Western punctuation
    MIXED_PUNCTUATION = "mixed_punctuation"                  # 中英文标点混用
    CHINESE_COMMA_ENGLISH = "chinese_comma_english"          # 中文句子中用了英文逗号
    CHINESE_PERIOD_ENGLISH = "chinese_period_english"        # 中文句子中用了英文句号

    # Punctuation repetition
    REPEATED_PUNCTUATION = "repeated_punctuation"            # 标点重复
    MULTIPLE_ELLIPSIS = "multiple_ellipsis"                  # 省略号叠加

    # Spacing issues
    SPACE_BEFORE_PUNCTUATION = "space_before_punctuation"    # 标点前有空格
    SPACE_AFTER_PUNCTUATION = "space_after_punctuation"     # 标点后有空格
    NO_SPACE_AFTER_PUNCTUATION = "no_space_after_punctuation"  # 标点后缺少空格

    # Dash and connection issues
    MIXED_DASH_STYLE = "mixed_dash_style"                    # 破折号风格不统一
    DASH_SPACING_ERROR = "dash_spacing_error"                # 破折号间距错误

    # Ellipsis issues
    ENGLISH_ELLIPSIS = "english_ellipsis"                     # 英文省略号用在中文中
    WRONG_ELLIPSIS_LENGTH = "wrong_ellipsis_length"          # 省略号长度错误

    # Punctuation in dialogue
    MISSING_PUNCTUATION_BEFORE_QUOTE = "missing_punctuation_before_quote"
    MISSING_PUNCTUATION_AFTER_QUOTE = "missing_punctuation_after_quote"
    PUNCTUATION_INSIDE_QUOTE = "punctuation_inside_quote"  # 标点在引号内/外位置错误

    # Parentheses issues
    MIXED_PARENTHESES_STYLE = "mixed_parentheses_style"      # 括号风格不统一
    UNPAIRED_PARENTHESES = "unpaired_parentheses"           # 括号不成对

    # List punctuation
    MIXED_LIST_PUNCTUATION = "mixed_list_punctuation"        # 列举时顿号逗号混用

    # Semicolon/colon usage
    ENGLISH_SEMICOLON = "english_semicolon"                  # 中文文本中使用英文分号
    ENGLISH_COLON = "english_colon"                          # 中文文本中使用英文冒号

    # Other
    EXTRA_PUNCTUATION = "extra_punctuation"                  # 多余标点
    MISSING_PUNCTUATION = "missing_punctuation"              # 缺少标点
    LINE_BREAK_PUNCTUATION = "line_break_punctuation"       # 换行处标点错误


class PunctuationSeverity(str, Enum):
    """Severity of punctuation errors."""
    CRITICAL = "critical"   # 严重错误，影响阅读
    MAJOR = "major"         # 较大问题
    MINOR = "minor"         # 小问题
    TYPOGRAPHICAL = "typographical"  # 排版/格式问题


class PunctuationStyle(str, Enum):
    """Punctuation style options."""
    CHINESE = "chinese"               # 中文标点风格
    ENGLISH = "english"               # 英文标点风格
    MIXED = "mixed"                   # 混用
    CONSISTENT = "consistent"         # 一致
    INCONSISTENT = "inconsistent"     # 不一致


class PunctuationPattern(BaseModel):
    """Pattern for detecting specific punctuation issues."""
    pattern: str = Field(description="Regex pattern")
    issue_type: PunctuationErrorType = Field(description="Type of issue detected")
    description: str = Field(description="Description of the issue")
    severity: PunctuationSeverity = Field(description="Severity level")


class PunctuationIssue(BaseModel):
    """A detected punctuation issue."""
    issue_id: str = Field(description="Unique issue identifier")
    chapter: int = Field(description="Chapter where issue is found")
    sentence: str = Field(description="The sentence containing the issue")
    position: int = Field(default=0, description="Character position in chapter")
    issue_type: PunctuationErrorType = Field(description="Type of issue")
    severity: PunctuationSeverity = Field(description="Issue severity")
    original_text: str = Field(description="Original text with issue")
    suggested_fix: str = Field(default="", description="Suggested correction")
    description: str = Field(description="Description of the issue")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Detection confidence")


class PunctuationCheckResult(BaseModel):
    """Result of checking a single passage."""
    passage: str = Field(description="The checked passage")
    passage_type: str = Field(default="", description="Type: dialogue, narration, etc.")
    issue_count: int = Field(default=0, description="Number of issues found")
    issues: list[PunctuationIssue] = Field(default_factory=list, description="Detected issues")
    punctuation_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Punctuation score for this passage")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")


class ChapterPunctuationProfile(BaseModel):
    """Punctuation profile for a single chapter."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(default="", description="Chapter title")

    # Statistics
    total_sentences: int = Field(default=0, description="Total sentences")
    total_characters: int = Field(default=0, description="Total characters")
    dialogue_sentences: int = Field(default=0, description="Dialogue sentences")
    narration_sentences: int = Field(default=0, description="Narration sentences")

    # Issue counts by type
    issue_counts: dict[str, int] = Field(default_factory=dict, description="Issues by type")
    total_issues: int = Field(default=0, description="Total issues")

    # Severity distribution
    critical_issues: int = Field(default=0, description="Critical issues")
    major_issues: int = Field(default=0, description="Major issues")
    minor_issues: int = Field(default=0, description="Minor issues")
    typographical_issues: int = Field(default=0, description="Typographical issues")

    # Style consistency
    quote_style_consistency: PunctuationStyle = Field(default=PunctuationStyle.CONSISTENT)
    dash_style_consistency: PunctuationStyle = Field(default=PunctuationStyle.CONSISTENT)
    overall_style: PunctuationStyle = Field(default=PunctuationStyle.CHINESE)

    # Scores
    punctuation_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall punctuation score")
    quote_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quote style score")
    spacing_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Spacing score")

    # Dialogue specific
    dialogue_issues: int = Field(default=0, description="Issues in dialogue")
    narration_issues: int = Field(default=0, description="Issues in narration")

    # Quality indicators
    needs_revision: bool = Field(default=False, description="Whether chapter needs revision")


class PunctuationCheckAnalysis(BaseModel):
    """Comprehensive punctuation analysis for a novel."""
    # Overall scores
    overall_punctuation_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_quote_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_spacing_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Statistics
    total_chapters: int = Field(default=0, description="Total chapters checked")
    total_sentences: int = Field(default=0, description="Total sentences")
    total_issues: int = Field(default=0, description="Total issues found")

    # Issue distribution by type
    issues_by_type: dict[str, int] = Field(default_factory=dict, description="Issue counts by type")

    # Severity distribution
    critical_count: int = Field(default=0, description="Critical issues")
    major_count: int = Field(default=0, description="Major issues")
    minor_count: int = Field(default=0, description="Minor issues")
    typographical_count: int = Field(default=0, description="Typographical issues")

    # Style analysis
    quote_style_used: PunctuationStyle = Field(default=PunctuationStyle.CHINESE)
    dash_style_used: PunctuationStyle = Field(default=PunctuationStyle.CHINESE)
    style_consistency: PunctuationStyle = Field(default=PunctuationStyle.CONSISTENT)

    # Per-chapter analysis
    chapter_profiles: list[ChapterPunctuationProfile] = Field(default_factory=list)

    # All detected issues
    all_issues: list[PunctuationIssue] = Field(default_factory=list)

    # Quality indicators
    chapters_needing_revision: list[int] = Field(default_factory=list, description="Chapters needing revision")
    has_critical_issues: bool = Field(default=False, description="Whether critical issues exist")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class PunctuationCheckRevision(BaseModel):
    """Revision suggestion for a punctuation issue."""
    issue_id: str = Field(description="Issue identifier")
    chapter: int = Field(description="Chapter number")
    original_text: str = Field(description="Original text")
    suggested_fix: str = Field(description="Suggested fix")
    revision_type: str = Field(default="", description="Type of revision")
    priority: int = Field(default=0, description="Priority for this revision")


class PunctuationCheckPlan(BaseModel):
    """Plan for fixing punctuation errors."""
    # Issues to fix
    critical_to_fix: list[str] = Field(default_factory=list, description="Critical issue IDs")
    major_to_fix: list[str] = Field(default_factory=list, description="Major issue IDs")
    minor_to_fix: list[str] = Field(default_factory=list, description="Minor issue IDs")

    # Chapters needing work
    chapters_to_revise: list[int] = Field(default_factory=list, description="Chapters to revise")

    # Priority order (issue_id, priority)
    priority_order: list[tuple[str, int]] = Field(default_factory=list)

    # Estimated work
    estimated_fixes: int = Field(default=0, description="Estimated number of fixes")

    # Focus areas
    focus_on_quotes: bool = Field(default=True, description="Focus on quote fixes")
    focus_on_spacing: bool = Field(default=True, description="Focus on spacing fixes")
    focus_on_ellipsis: bool = Field(default=True, description="Focus on ellipsis fixes")


class PunctuationCheckReport(BaseModel):
    """Final report for punctuation check."""
    analysis: PunctuationCheckAnalysis = Field(description="Complete analysis")
    revision_plan: PunctuationCheckPlan = Field(description="Plan for revisions")

    # Summary
    summary: str = Field(default="", description="Human-readable summary")

    # Revisions
    revisions_completed: list[PunctuationCheckRevision] = Field(default_factory=list)

    # Final status
    final_punctuation_score: Optional[float] = Field(default=None)
    improvement_achieved: Optional[float] = Field(default=None)


class PunctuationTemplate(BaseModel):
    """Template for punctuation style."""
    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    quote_style: str = Field(description="Quote style: chinese_brackets, english_double, chinese_single")
    dash_style: str = Field(description="Dash style: chinese_dash, english_dash")
    comma_style: str = Field(description="Comma style: chinese_comma, english_comma")
    ellipsis_style: str = Field(description="Ellipsis style: chinese_ellipsis, english_ellipsis")
    parentheses_style: str = Field(description="Parentheses style: chinese, english")


# Standard punctuation templates
STANDARD_TEMPLATES = {
    "default": PunctuationTemplate(
        name="默认中文标点",
        description="标准中文出版标点规范",
        quote_style="chinese_brackets",      # 「」
        dash_style="chinese_dash",           # —— (em dash)
        comma_style="chinese_comma",         # ，
        ellipsis_style="chinese_ellipsis",   # …… (six dots)
        parentheses_style="chinese",         # （）
    ),
    "formal": PunctuationTemplate(
        name="正式文体",
        description="正式出版物的标点规范",
        quote_style="chinese_brackets",
        dash_style="chinese_dash",
        comma_style="chinese_comma",
        ellipsis_style="chinese_ellipsis",
        parentheses_style="chinese",
    ),
    "literary": PunctuationTemplate(
        name="文学创作",
        description="文学作品的标点规范",
        quote_style="chinese_brackets",
        dash_style="chinese_dash",
        comma_style="chinese_comma",
        ellipsis_style="chinese_ellipsis",
        parentheses_style="chinese",
    ),
}
