"""Punctuation standardization check engine for quality assurance."""

import re
import uuid
from typing import Optional
from collections import Counter

from chai.models import Novel, Chapter
from chai.models.punctuation_check import (
    PunctuationErrorType,
    PunctuationSeverity,
    PunctuationIssue,
    PunctuationCheckResult,
    ChapterPunctuationProfile,
    PunctuationCheckAnalysis,
    PunctuationCheckRevision,
    PunctuationCheckPlan,
    PunctuationCheckReport,
    PunctuationStyle,
    PunctuationTemplate,
    STANDARD_TEMPLATES,
)
from chai.services import AIService


# Punctuation patterns for detection
PUNCTUATION_PATTERNS = [
    # 英文逗号在中文中
    (
        r'[\u4e00-\u9fa5]，',
        PunctuationErrorType.CHINESE_COMMA_ENGLISH,
        "中文句子中不应使用中文逗号后接其他中文标点",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    # 英文句号在中文中
    (
        r'[\u4e00-\u9fa5]\.',
        PunctuationErrorType.CHINESE_PERIOD_ENGLISH,
        "中文句子中不应使用英文句号",
        PunctuationSeverity.MAJOR,
    ),
    # 引号不成对
    (
        r'"[^"]*$',
        PunctuationErrorType.INCONSISTENT_QUOTE_PAIR,
        "英文引号未闭合",
        PunctuationSeverity.MAJOR,
    ),
    (
        r'「[^」]*$',
        PunctuationErrorType.INCONSISTENT_QUOTE_PAIR,
        "中文引号「未闭合",
        PunctuationSeverity.MAJOR,
    ),
    (
        r'『[^』]*$',
        PunctuationErrorType.INCONSISTENT_QUOTE_PAIR,
        "中文引号『未闭合",
        PunctuationSeverity.MAJOR,
    ),
    # 标点前有空格
    (
        r' [，。！？；：、】」』]',
        PunctuationErrorType.SPACE_BEFORE_PUNCTUATION,
        "标点符号前不应有空格",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    # 标点后有多余空格（句末）
    (
        r'[。！？][ ]+$',
        PunctuationErrorType.EXTRA_PUNCTUATION,
        "句末标点后不应有多余空格",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    # 省略号重复
    (
        r'……+',
        PunctuationErrorType.MULTIPLE_ELLIPSIS,
        "省略号不应重复",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    # 英文省略号在中文中
    (
        r'\.\.\.+',
        PunctuationErrorType.ENGLISH_ELLIPSIS,
        "中文文本中应使用中文省略号……",
        PunctuationSeverity.MAJOR,
    ),
    # 英文分号在中文中
    (
        r'[\u4e00-\u9fa5];',
        PunctuationErrorType.ENGLISH_SEMICOLON,
        "中文文本中不应使用英文分号",
        PunctuationSeverity.MINOR,
    ),
    # 英文冒号在中文中
    (
        r'[\u4e00-\u9fa5]:',
        PunctuationErrorType.ENGLISH_COLON,
        "中文文本中不应使用英文冒号",
        PunctuationSeverity.MINOR,
    ),
    # 破折号间距错误
    (
        r'—— +',
        PunctuationErrorType.DASH_SPACING_ERROR,
        "破折号后不应有空格",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    (
        r' +——',
        PunctuationErrorType.DASH_SPACING_ERROR,
        "破折号前不应有空格",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    # 英文破折号在中文中
    (
        r'--',
        PunctuationErrorType.MIXED_DASH_STYLE,
        "中文文本中应使用中文破折号——",
        PunctuationSeverity.MINOR,
    ),
    # 括号不成对
    (
        r'\([^)]*$',
        PunctuationErrorType.UNPAIRED_PARENTHESES,
        "左括号未闭合",
        PunctuationSeverity.MAJOR,
    ),
    (
        r'（[^）]*$',
        PunctuationErrorType.UNPAIRED_PARENTHESES,
        "中文左括号（未闭合",
        PunctuationSeverity.MAJOR,
    ),
    # 多种标点叠加
    (
        r'[！？]{2,}',
        PunctuationErrorType.REPEATED_PUNCTUATION,
        "感叹号和问号不应叠加",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    (
        r'，，+',
        PunctuationErrorType.REPEATED_PUNCTUATION,
        "逗号不应重复",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
    (
        r'。。+',
        PunctuationErrorType.REPEATED_PUNCTUATION,
        "句号不应重复",
        PunctuationSeverity.TYPOGRAPHICAL,
    ),
]


class PunctuationCheckEngine:
    """Engine for checking and standardizing punctuation in manuscript."""

    def __init__(self, ai_service: AIService, template_name: str = "default"):
        """Initialize punctuation check engine with AI service.

        Args:
            ai_service: AI service for advanced corrections
            template_name: Punctuation template to use (default, formal, literary)
        """
        self.ai_service = ai_service
        self.template = STANDARD_TEMPLATES.get(template_name, STANDARD_TEMPLATES["default"])

    def check_novel_punctuation(self, novel: Novel) -> PunctuationCheckAnalysis:
        """Check all chapters for punctuation issues.

        Args:
            novel: Novel to check

        Returns:
            Comprehensive punctuation analysis
        """
        # Extract chapters from volumes
        chapters = []
        for volume in novel.volumes:
            chapters.extend(volume.chapters)
        total_chapters = len(chapters)

        if total_chapters == 0:
            return PunctuationCheckAnalysis()

        # Analyze each chapter
        chapter_profiles = []
        all_issues = []

        for chapter in chapters:
            profile, issues = self.check_chapter_punctuation(chapter)
            chapter_profiles.append(profile)
            all_issues.extend(issues)

        # Aggregate statistics
        total_sentences = sum(p.total_sentences for p in chapter_profiles)
        total_issues = len(all_issues)

        # Count by type
        issues_by_type: dict[str, int] = {}
        for issue in all_issues:
            issue_type = issue.issue_type.value
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1

        # Count by severity
        critical_count = sum(1 for i in all_issues if i.severity == PunctuationSeverity.CRITICAL)
        major_count = sum(1 for i in all_issues if i.severity == PunctuationSeverity.MAJOR)
        minor_count = sum(1 for i in all_issues if i.severity == PunctuationSeverity.MINOR)
        typographical_count = sum(1 for i in all_issues if i.severity == PunctuationSeverity.TYPOGRAPHICAL)

        # Calculate overall scores
        overall_punctuation = self._calculate_punctuation_score(all_issues, total_sentences)
        overall_quote = self._calculate_quote_score(all_issues, total_sentences)
        overall_spacing = self._calculate_spacing_score(all_issues, total_sentences)

        # Style analysis
        quote_styles = [p.quote_style_consistency for p in chapter_profiles]
        dash_styles = [p.dash_style_consistency for p in chapter_profiles]
        quote_style_used = self._determine_domino_style(quote_styles)
        dash_style_used = self._determine_domino_style(dash_styles)
        style_consistency = PunctuationStyle.CONSISTENT if quote_style_used == PunctuationStyle.CONSISTENT else PunctuationStyle.INCONSISTENT

        # Chapters needing revision
        chapters_needing_revision = [p.chapter_number for p in chapter_profiles if p.needs_revision]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            all_issues, issues_by_type, chapters_needing_revision
        )

        analysis = PunctuationCheckAnalysis(
            overall_punctuation_score=overall_punctuation,
            overall_quote_score=overall_quote,
            overall_spacing_score=overall_spacing,
            total_chapters=total_chapters,
            total_sentences=total_sentences,
            total_issues=total_issues,
            issues_by_type=issues_by_type,
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            typographical_count=typographical_count,
            quote_style_used=quote_style_used,
            dash_style_used=dash_style_used,
            style_consistency=style_consistency,
            chapter_profiles=chapter_profiles,
            all_issues=all_issues,
            chapters_needing_revision=chapters_needing_revision,
            has_critical_issues=critical_count > 0,
            recommendations=recommendations,
        )

        return analysis

    def check_chapter_punctuation(self, chapter: Chapter) -> tuple[ChapterPunctuationProfile, list[PunctuationIssue]]:
        """Check a single chapter for punctuation issues.

        Args:
            chapter: Chapter to check

        Returns:
            Tuple of (chapter profile, list of issues)
        """
        content = chapter.content or ""
        issues = []

        if not content:
            return ChapterPunctuationProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title or "",
            ), []

        # Split into sentences
        sentences = self._split_sentences(content)

        # Analyze sentences
        total_sentences = len(sentences)
        total_characters = len(content)
        dialogue_sentences = sum(1 for s in sentences if self._is_dialogue(s))
        narration_sentences = total_sentences - dialogue_sentences

        # Detect issues in each sentence
        for idx, sentence in enumerate(sentences):
            sentence_issues = self._check_sentence(sentence, chapter.number, idx)
            issues.extend(sentence_issues)

        # Check for structural issues
        structural_issues = self._check_structural_issues(content, chapter.number)
        issues.extend(structural_issues)

        # Check quote consistency
        quote_issues = self._check_quote_consistency(content, chapter.number)
        issues.extend(quote_issues)

        # Count issues by type
        issue_counts: dict[str, int] = {}
        for issue in issues:
            issue_type = issue.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Severity distribution
        critical_issues = sum(1 for i in issues if i.severity == PunctuationSeverity.CRITICAL)
        major_issues = sum(1 for i in issues if i.severity == PunctuationSeverity.MAJOR)
        minor_issues = sum(1 for i in issues if i.severity == PunctuationSeverity.MINOR)
        typographical_issues = sum(1 for i in issues if i.severity == PunctuationSeverity.TYPOGRAPHICAL)

        # Calculate scores
        punctuation_score = max(0.0, 1.0 - (len(issues) / max(1, total_sentences)) * 0.5)
        quote_score = max(0.0, 1.0 - (sum(1 for i in issues if "quote" in i.issue_type.value) / max(1, total_sentences)))
        spacing_score = max(0.0, 1.0 - (sum(1 for i in issues if "space" in i.issue_type.value) / max(1, total_sentences)))

        # Style consistency
        quote_style_consistency = self._check_quote_style_consistency(content)
        dash_style_consistency = self._check_dash_style_consistency(content)
        overall_style = PunctuationStyle.CHINESE  # Default

        # Dialogue vs narration issues
        dialogue_issues = sum(1 for i in issues if self._is_dialogue(i.sentence))
        narration_issues = len(issues) - dialogue_issues

        # Quality indicators
        needs_revision = major_issues > 0 or critical_issues > 0 or (minor_issues > total_sentences * 0.1)

        profile = ChapterPunctuationProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title or "",
            total_sentences=total_sentences,
            total_characters=total_characters,
            dialogue_sentences=dialogue_sentences,
            narration_sentences=narration_sentences,
            issue_counts=issue_counts,
            total_issues=len(issues),
            critical_issues=critical_issues,
            major_issues=major_issues,
            minor_issues=minor_issues,
            typographical_issues=typographical_issues,
            quote_style_consistency=quote_style_consistency,
            dash_style_consistency=dash_style_consistency,
            overall_style=overall_style,
            punctuation_score=punctuation_score,
            quote_score=quote_score,
            spacing_score=spacing_score,
            dialogue_issues=dialogue_issues,
            narration_issues=narration_issues,
            needs_revision=needs_revision,
        )

        return profile, issues

    def create_revision_plan(self, analysis: PunctuationCheckAnalysis) -> PunctuationCheckPlan:
        """Create a revision plan based on analysis.

        Args:
            analysis: Punctuation check analysis

        Returns:
            Revision plan
        """
        critical_ids = [i.issue_id for i in analysis.all_issues
                       if i.severity == PunctuationSeverity.CRITICAL]
        major_ids = [i.issue_id for i in analysis.all_issues
                    if i.severity == PunctuationSeverity.MAJOR]
        minor_ids = [i.issue_id for i in analysis.all_issues
                    if i.severity == PunctuationSeverity.MINOR]

        # Create priority order
        priority_order: list[tuple[str, int]] = []
        for iid in critical_ids:
            priority_order.append((iid, 100))
        for iid in major_ids:
            priority_order.append((iid, 70))
        for iid in minor_ids:
            priority_order.append((iid, 30))

        priority_order.sort(key=lambda x: x[1], reverse=True)

        # Determine focus areas
        quote_count = sum(1 for i in analysis.all_issues if "quote" in i.issue_type.value)
        spacing_count = sum(1 for i in analysis.all_issues if "space" in i.issue_type.value)
        ellipsis_count = sum(1 for i in analysis.all_issues if "ellipsis" in i.issue_type.value)

        plan = PunctuationCheckPlan(
            critical_to_fix=critical_ids,
            major_to_fix=major_ids,
            minor_to_fix=minor_ids,
            chapters_to_revise=analysis.chapters_needing_revision,
            priority_order=priority_order,
            estimated_fixes=len(analysis.all_issues),
            focus_on_quotes=quote_count > 0,
            focus_on_spacing=spacing_count > 0,
            focus_on_ellipsis=ellipsis_count > 0,
        )

        return plan

    def generate_check_report(
        self,
        analysis: PunctuationCheckAnalysis,
        plan: Optional[PunctuationCheckPlan] = None,
    ) -> PunctuationCheckReport:
        """Generate a complete check report.

        Args:
            analysis: Punctuation check analysis
            plan: Optional revision plan

        Returns:
            Complete check report
        """
        if plan is None:
            plan = self.create_revision_plan(analysis)

        summary = self._generate_summary(analysis)

        report = PunctuationCheckReport(
            analysis=analysis,
            revision_plan=plan,
            summary=summary,
            revisions_completed=[],
        )

        return report

    def get_punctuation_summary(self, analysis: PunctuationCheckAnalysis) -> str:
        """Get a human-readable summary of punctuation check.

        Args:
            analysis: Punctuation check analysis

        Returns:
            Summary string
        """
        lines = [
            "=== 标点符号规范化检查报告 ===",
            "",
            f"检查章节数: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"总问题数: {analysis.total_issues}",
            "",
            "--- 问题分布 ---",
            f"严重问题: {analysis.critical_count}",
            f"较大问题: {analysis.major_count}",
            f"一般问题: {analysis.minor_count}",
            f"排版问题: {analysis.typographical_count}",
            "",
            "--- 评分 ---",
            f"标点评分: {analysis.overall_punctuation_score:.0%}",
            f"引号评分: {analysis.overall_quote_score:.0%}",
            f"间距评分: {analysis.overall_spacing_score:.0%}",
            "",
            f"引号风格: {analysis.quote_style_used.value}",
            f"破折号风格: {analysis.dash_style_used.value}",
            f"风格一致性: {analysis.style_consistency.value}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision))}")

        return "\n".join(lines)

    # Helper methods

    def _split_sentences(self, content: str) -> list[str]:
        """Split content into sentences."""
        # Split by Chinese sentence endings
        sentences = re.split(r'[。！？!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _is_dialogue(self, sentence: str) -> bool:
        """Check if a sentence is dialogue."""
        dialogue_markers = ['"', '"', '"', '"', '「', '」', '『', '』', '说：', '说道：', '答道：', '问道：']
        return any(marker in sentence for marker in dialogue_markers)

    def _check_sentence(self, sentence: str, chapter: int, sentence_idx: int) -> list[PunctuationIssue]:
        """Check a single sentence for punctuation issues."""
        issues = []

        # Check punctuation patterns
        for pattern, issue_type, description, severity in PUNCTUATION_PATTERNS:
            matches = re.finditer(pattern, sentence)
            for match in matches:
                issue = PunctuationIssue(
                    issue_id=f"punct_{chapter}_{sentence_idx}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=sentence,
                    position=match.start(),
                    issue_type=issue_type,
                    severity=severity,
                    original_text=match.group(),
                    suggested_fix=self._get_suggested_fix(issue_type, match.group()),
                    description=description,
                    confidence=0.85,
                )
                issues.append(issue)

        return issues

    def _check_structural_issues(self, content: str, chapter: int) -> list[PunctuationIssue]:
        """Check for structural punctuation issues in content."""
        issues = []

        # Check for mixed Chinese/English punctuation
        # English comma in Chinese text
        english_comma_pattern = r'([\u4e00-\u9fa5]),([\u4e00-\u9fa5])'
        matches = re.finditer(english_comma_pattern, content)
        for match in matches:
            issue = PunctuationIssue(
                issue_id=f"punct_struct_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence=self._get_context_sentence(content, match.start()),
                position=match.start(),
                issue_type=PunctuationErrorType.MIXED_PUNCTUATION,
                severity=PunctuationSeverity.MAJOR,
                original_text=match.group(),
                suggested_fix=match.group().replace(',', '，'),
                description="中文文本中混用了英文逗号",
                confidence=0.9,
            )
            issues.append(issue)

        # English period in Chinese text
        english_period_pattern = r'([\u4e00-\u9fa5])\.([\u4e00-\u9fa5])'
        matches = re.finditer(english_period_pattern, content)
        for match in matches:
            issue = PunctuationIssue(
                issue_id=f"punct_struct_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence=self._get_context_sentence(content, match.start()),
                position=match.start(),
                issue_type=PunctuationErrorType.MIXED_PUNCTUATION,
                severity=PunctuationSeverity.MAJOR,
                original_text=match.group(),
                suggested_fix=match.group().replace('.', '。'),
                description="中文文本中混用了英文句号",
                confidence=0.9,
            )
            issues.append(issue)

        # Check for English quotes mixed with Chinese
        if '"' in content and '「' in content:
            issue = PunctuationIssue(
                issue_id=f"punct_struct_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence="混合使用了英文引号和中文引号",
                position=0,
                issue_type=PunctuationErrorType.MIXED_QUOTE_STYLE,
                severity=PunctuationSeverity.MAJOR,
                original_text='"...「..."',
                suggested_fix="统一使用中文引号「」",
                description="混合使用了英文引号和中文引号",
                confidence=0.85,
            )
            issues.append(issue)

        # Check for English parentheses in Chinese
        if '(' in content and '（' in content:
            issue = PunctuationIssue(
                issue_id=f"punct_struct_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence="混合使用了英文括号和中文括号",
                position=0,
                issue_type=PunctuationErrorType.MIXED_PARENTHESES_STYLE,
                severity=PunctuationSeverity.MINOR,
                original_text="(...（...",
                suggested_fix="统一使用中文括号（）",
                description="混合使用了英文括号和中文括号",
                confidence=0.8,
            )
            issues.append(issue)

        # Check for wrong ellipsis length (should be 6 dots …… not 3 .)
        ellipsis_pattern = r'(?<=[^。])(\.{3,5})(?=[^。])'
        matches = re.finditer(ellipsis_pattern, content)
        for match in matches:
            issue = PunctuationIssue(
                issue_id=f"punct_ellipsis_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence=self._get_context_sentence(content, match.start()),
                position=match.start(),
                issue_type=PunctuationErrorType.WRONG_ELLIPSIS_LENGTH,
                severity=PunctuationSeverity.MAJOR,
                original_text=match.group(),
                suggested_fix="……",
                description="中文省略号应为六个点……",
                confidence=0.9,
            )
            issues.append(issue)

        # Check for repeated punctuation (Chinese)
        repeated_patterns = [
            (r'[！？]{2,}', '！？'),
            (r'[。，]{2,}', '。，'),
            (r'，，+', '，'),
            (r'。。+', '。'),
        ]
        for pattern, chars in repeated_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                issue = PunctuationIssue(
                    issue_id=f"punct_repeat_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=self._get_context_sentence(content, match.start()),
                    position=match.start(),
                    issue_type=PunctuationErrorType.REPEATED_PUNCTUATION,
                    severity=PunctuationSeverity.TYPOGRAPHICAL,
                    original_text=match.group(),
                    suggested_fix=chars[0],
                    description="标点符号重复",
                    confidence=0.9,
                )
                issues.append(issue)

        # Check for space before punctuation
        space_before_patterns = [
            (r' [，。！？；：、】」』]', '标点前有空格'),
            (r' [？！；：、】」』]', '标点前有空格'),
        ]
        for pattern, desc in space_before_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                issue = PunctuationIssue(
                    issue_id=f"punct_space_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=self._get_context_sentence(content, match.start()),
                    position=match.start(),
                    issue_type=PunctuationErrorType.SPACE_BEFORE_PUNCTUATION,
                    severity=PunctuationSeverity.TYPOGRAPHICAL,
                    original_text=match.group(),
                    suggested_fix=match.group().strip(),
                    description=desc,
                    confidence=0.85,
                )
                issues.append(issue)

        return issues

    def _check_quote_consistency(self, content: str, chapter: int) -> list[PunctuationIssue]:
        """Check for quote consistency issues."""
        issues = []

        # Count different quote types
        chinese_double = content.count('「') + content.count('」')
        chinese_single = content.count('『') + content.count('』')
        english_double = content.count('"')
        english_single = content.count("'")

        # Check for unpaired quotes
        if content.count('「') != content.count('」'):
            issue = PunctuationIssue(
                issue_id=f"punct_quote_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence="引号不成对",
                position=0,
                issue_type=PunctuationErrorType.INCONSISTENT_QUOTE_PAIR,
                severity=PunctuationSeverity.MAJOR,
                original_text="「...",
                suggested_fix="补全引号",
                description="中文双引号「」不成对",
                confidence=0.95,
            )
            issues.append(issue)

        if content.count('『') != content.count('』'):
            issue = PunctuationIssue(
                issue_id=f"punct_quote_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence="引号不成对",
                position=0,
                issue_type=PunctuationErrorType.INCONSISTENT_QUOTE_PAIR,
                severity=PunctuationSeverity.MAJOR,
                original_text="『...",
                suggested_fix="补全引号",
                description="中文单引号『』不成对",
                confidence=0.95,
            )
            issues.append(issue)

        # Check for mixing quote types (should not mix within same dialogue)
        if english_double > 0 and chinese_double > 0:
            issue = PunctuationIssue(
                issue_id=f"punct_quote_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence="引号风格混用",
                position=0,
                issue_type=PunctuationErrorType.MIXED_QUOTE_STYLE,
                severity=PunctuationSeverity.MAJOR,
                original_text='"...「..."',
                suggested_fix="统一使用中文引号「」",
                description="混用了英文引号和中文引号",
                confidence=0.9,
            )
            issues.append(issue)

        return issues

    def _check_quote_style_consistency(self, content: str) -> PunctuationStyle:
        """Check quote style consistency in content."""
        chinese_double = content.count('「') + content.count('」')
        chinese_single = content.count('『') + content.count('』')
        english_double = content.count('"')
        english_single = content.count("'")

        total_quotes = chinese_double + chinese_single + english_double + english_single

        if total_quotes == 0:
            return PunctuationStyle.CONSISTENT

        chinese_ratio = (chinese_double + chinese_single) / total_quotes

        if chinese_ratio > 0.9:
            return PunctuationStyle.CHINESE
        elif chinese_ratio < 0.1:
            return PunctuationStyle.ENGLISH
        else:
            return PunctuationStyle.MIXED

    def _check_dash_style_consistency(self, content: str) -> PunctuationStyle:
        """Check dash style consistency in content."""
        chinese_dash = content.count('——')
        english_dash = content.count('--')

        total_dashes = chinese_dash + english_dash

        if total_dashes == 0:
            return PunctuationStyle.CONSISTENT

        chinese_ratio = chinese_dash / total_dashes

        if chinese_ratio > 0.9:
            return PunctuationStyle.CHINESE
        elif chinese_ratio < 0.1:
            return PunctuationStyle.ENGLISH
        else:
            return PunctuationStyle.MIXED

    def _get_suggested_fix(self, issue_type: PunctuationErrorType, original: str) -> str:
        """Get suggested fix based on issue type."""
        fixes = {
            PunctuationErrorType.ENGLISH_ELLIPSIS: "……",
            PunctuationErrorType.ENGLISH_SEMICOLON: "；",
            PunctuationErrorType.ENGLISH_COLON: "：",
            PunctuationErrorType.MIXED_DASH_STYLE: "——",
            PunctuationErrorType.SPACE_BEFORE_PUNCTUATION: original.strip(),
        }
        return fixes.get(issue_type, original)

    def _get_context_sentence(self, content: str, position: int, context_size: int = 30) -> str:
        """Get the sentence containing the position."""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)

        # Find sentence boundaries
        before = content[start:position]
        after = content[position:end]

        # Try to find sentence boundaries
        for i in range(len(before) - 1, -1, -1):
            if before[i] in '。！？?!\n':
                start = start + i + 1
                break

        for i, c in enumerate(after):
            if c in '。！？?!\n':
                end = position + i + 1
                break

        return content[start:end].strip()

    def _calculate_punctuation_score(self, issues: list[PunctuationIssue], total_sentences: int) -> float:
        """Calculate overall punctuation score."""
        if total_sentences == 0:
            return 1.0

        error_rate = len(issues) / total_sentences
        return max(0.0, 1.0 - error_rate * 0.5)

    def _calculate_quote_score(self, issues: list[PunctuationIssue], total_sentences: int) -> float:
        """Calculate quote style score."""
        if total_sentences == 0:
            return 1.0

        quote_issues = [i for i in issues if "quote" in i.issue_type.value]
        error_rate = len(quote_issues) / total_sentences
        return max(0.0, 1.0 - error_rate)

    def _calculate_spacing_score(self, issues: list[PunctuationIssue], total_sentences: int) -> float:
        """Calculate spacing score."""
        if total_sentences == 0:
            return 1.0

        spacing_issues = [i for i in issues if "space" in i.issue_type.value]
        error_rate = len(spacing_issues) / total_sentences
        return max(0.0, 1.0 - error_rate)

    def _determine_domino_style(self, styles: list[PunctuationStyle]) -> PunctuationStyle:
        """Determine the dominant style from a list."""
        if not styles:
            return PunctuationStyle.CONSISTENT

        style_counts = Counter(styles)
        most_common = style_counts.most_common(1)[0][0]

        # If more than 80% are the same, consider it consistent
        if style_counts[most_common] / len(styles) > 0.8:
            return most_common

        return PunctuationStyle.INCONSISTENT

    def _generate_recommendations(
        self,
        issues: list[PunctuationIssue],
        issues_by_type: dict[str, int],
        chapters_needing_revision: list[int],
    ) -> list[str]:
        """Generate recommendations based on issues."""
        recs = []

        # Critical issues
        critical = [i for i in issues if i.severity == PunctuationSeverity.CRITICAL]
        if critical:
            recs.append(f"存在 {len(critical)} 个严重标点错误，必须立即修正")

        # Major issues
        major = [i for i in issues if i.severity == PunctuationSeverity.MAJOR]
        if major:
            recs.append(f"存在 {len(major)} 个较大标点问题，建议优先修正")

        # Quote issues
        quote_count = issues_by_type.get(PunctuationErrorType.MIXED_QUOTE_STYLE.value, 0) + \
                      issues_by_type.get(PunctuationErrorType.INCONSISTENT_QUOTE_PAIR.value, 0)
        if quote_count > 3:
            recs.append("引号问题较多，建议统一使用中文引号「」")

        # Spacing issues
        spacing_count = issues_by_type.get(PunctuationErrorType.SPACE_BEFORE_PUNCTUATION.value, 0) + \
                       issues_by_type.get(PunctuationErrorType.SPACE_AFTER_PUNCTUATION.value, 0)
        if spacing_count > 5:
            recs.append("标点间距问题较多，注意标点前后不要加空格")

        # Ellipsis issues
        ellipsis_count = issues_by_type.get(PunctuationErrorType.ENGLISH_ELLIPSIS.value, 0) + \
                        issues_by_type.get(PunctuationErrorType.WRONG_ELLIPSIS_LENGTH.value, 0)
        if ellipsis_count > 0:
            recs.append("省略号应使用中文省略号……，而非英文...")

        # Mixed punctuation
        mixed_count = issues_by_type.get(PunctuationErrorType.MIXED_PUNCTUATION.value, 0)
        if mixed_count > 3:
            recs.append("中英文标点混用问题较多，中文文本应使用中文标点")

        # Chapter-specific
        if len(chapters_needing_revision) > 5:
            recs.append(f"有 {len(chapters_needing_revision)} 个章节需要重点修改标点")

        if not recs:
            recs.append("整体标点符号质量良好，仅需小幅修改")

        return recs

    def _generate_summary(self, analysis: PunctuationCheckAnalysis) -> str:
        """Generate human-readable summary."""
        lines = [
            "《标点符号规范化检查报告》",
            "",
            f"检查章节: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"总问题数: {analysis.total_issues}",
            "",
            "问题分布:",
            f"  严重问题: {analysis.critical_count}",
            f"  较大问题: {analysis.major_count}",
            f"  一般问题: {analysis.minor_count}",
            f"  排版问题: {analysis.typographical_count}",
            "",
            "评分:",
            f"  标点评分: {analysis.overall_punctuation_score:.0%}",
            f"  引号评分: {analysis.overall_quote_score:.0%}",
            f"  间距评分: {analysis.overall_spacing_score:.0%}",
            "",
            f"引号风格: {analysis.quote_style_used.value}",
            f"破折号风格: {analysis.dash_style_used.value}",
            f"风格一致性: {analysis.style_consistency.value}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision[:10]))}")
            if len(analysis.chapters_needing_revision) > 10:
                lines.append(f"  (还有 {len(analysis.chapters_needing_revision) - 10} 个)")

        return "\n".join(lines)
