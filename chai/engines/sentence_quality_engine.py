"""Sentence quality check engine for defective and redundant sentence optimization."""

import re
import uuid
from typing import Optional
from collections import Counter

from chai.models import Novel, Chapter
from chai.models.sentence_quality_check import (
    SentenceQualityType,
    SentenceQualitySeverity,
    SentenceQualityIssue,
    SentenceQualityResult,
    ChapterSentenceQualityProfile,
    SentenceQualityAnalysis,
    SentenceQualityRevision,
    SentenceQualityPlan,
    SentenceQualityReport,
    DiseaseSentencePattern,
    RedundancyPattern,
    SentenceQualityTemplate,
)
from chai.services import AIService


# Disease sentence patterns (病句 patterns)
DISEASE_PATTERNS: list[DiseaseSentencePattern] = [
    # 成分残缺 - Missing components
    DiseaseSentencePattern(
        pattern=r"^[，、\s]+[的得地了着过]",
        issue_type=SentenceQualityType.MISSING_SUBJECT,
        description="句子开头缺少主语",
        example_wrong="非常的高兴。",
        example_correct="他非常高高兴。",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    DiseaseSentencePattern(
        pattern=r"^[的得地了着过\s]+[，、。]",
        issue_type=SentenceQualityType.MISSING_PREDICATE,
        description="谓语残缺",
        example_wrong="他是学生。",
        example_correct="他是一名学生。",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    # 主谓不搭配
    DiseaseSentencePattern(
        pattern=r"(他的|她的|它的|我的|你的|这个|那个).*(提高|增加|减少|降低|改善|改变|解决|完成|实现|达到)",
        issue_type=SentenceQualityType.SUBJECT_PREDICATE_MISMATCH,
        description="主谓搭配不当",
        example_wrong="他的身高提高了。",
        example_correct="他的身高增加了。",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    # 动宾不搭配
    DiseaseSentencePattern(
        pattern=r"(提高|增加|改善|改变|完成|达到|实现|解决).*(水平|能力|条件|环境|情况|问题|困难|矛盾)",
        issue_type=SentenceQualityType.VERB_OBJECT_MISMATCH,
        description="动宾搭配不当",
        example_wrong="提高生活水平",
        example_correct="改善生活水平",
        severity=SentenceQualitySeverity.MINOR,
    ),
    # 成分赘余
    DiseaseSentencePattern(
        pattern=r"^的[，。]",
        issue_type=SentenceQualityType.REDUNDANT_SUBJECT,
        description="多余的主语",
        example_wrong="的的苹果。",
        example_correct="的苹果。",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    # 句式杂糅
    DiseaseSentencePattern(
        pattern=r"根据.*调查表明|由于.*原因所以|虽然.*但是同时",
        issue_type=SentenceQualityType.MIXED_STRUCTURE,
        description="句式杂糅",
        example_wrong="根据调查表明结果表明",
        example_correct="调查表明 / 根据调查结果表明",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    # 代词指代不明
    DiseaseSentencePattern(
        pattern=r"(这个|那个|他|她|它).*(这个|那个|他|她|它).*(这个|那个|他|她|它)",
        issue_type=SentenceQualityType.PRONOUN_AMBIGUITY,
        description="代词指代不明，多次出现指代不清的代词",
        severity=SentenceQualitySeverity.MAJOR,
    ),
    DiseaseSentencePattern(
        pattern=r"他们|她们|它们",
        issue_type=SentenceQualityType.PRONOUN_AMBIGUITY,
        description="'他们'/'她们'/'它们'指代不明，需明确",
        severity=SentenceQualitySeverity.MINOR,
    ),
    # 自相矛盾
    DiseaseSentencePattern(
        pattern=r"但是.*实际上|然而.*事实是|虽然.*但实际上|不但不.*反而",
        issue_type=SentenceQualityType.SELF_CONTRADICTION,
        description="可能存在自相矛盾",
        severity=SentenceQualitySeverity.MINOR,
    ),
    # 空洞表达
    DiseaseSentencePattern(
        pattern=r"^(很好|不错|还行|一般|普通|正常|适当|合理|必要|重要|很好|非常好)$",
        issue_type=SentenceQualityType.VAGUE_EXPRESSION,
        description="表达过于空洞，缺乏具体内容",
        example_wrong="很好。",
        example_correct="他的表现比预期更好。",
        severity=SentenceQualitySeverity.SUGGESTION,
    ),
    # 一句话分作两句说（语义重复）
    DiseaseSentencePattern(
        pattern=r"^(这是|那是|他是|她是|它是|我的|你的|他的|她的).*\1",
        issue_type=SentenceQualityType.REPETITIVE_MEANING,
        description="同一意思重复表达",
        severity=SentenceQualitySeverity.MINOR,
    ),
]

# Redundancy patterns (冗余句子 patterns)
REDUNDANCY_PATTERNS: list[RedundancyPattern] = [
    # 重复词语
    RedundancyPattern(
        redundant_text="非常极其",
        correction="极其",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'非常'和'极其'意思重复",
    ),
    RedundancyPattern(
        redundant_text="大约左右",
        correction="大约",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'大约'和'左右'意思重复",
    ),
    RedundancyPattern(
        redundant_text="多年的以来",
        correction="多年以来",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'多年的'和'以来'意思重复",
    ),
    RedundancyPattern(
        redundant_text="十分非常",
        correction="十分",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'十分'和'非常'意思重复",
    ),
    RedundancyPattern(
        redundant_text="各种各样",
        correction="各种",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'各种'和'各样'意思重复",
    ),
    RedundancyPattern(
        redundant_text="多年来一直",
        correction="多年来",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'多年来'和'一直'语义重复",
    ),
    RedundancyPattern(
        redundant_text="不断地不断",
        correction="不断地",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'不断地'和'不断'重复",
    ),
    RedundancyPattern(
        redundant_text="一次又一次",
        correction="一次又一次",
        redundancy_type=SentenceQualityType.REPETITIVE_MEANING,
        description="'一次又一次'本身就是重复结构，可保留但要注意上下文",
    ),
    RedundancyPattern(
        redundant_text="突然忽然",
        correction="突然",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'突然'和'忽然'意思相同",
    ),
    RedundancyPattern(
        redundant_text="结果最后",
        correction="最后",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'结果'和'最后'意思重复",
    ),
    RedundancyPattern(
        redundant_text="就是为了",
        correction="就是为了",
        redundancy_type=SentenceQualityType.FILLER_PHRASE,
        description="'就是为了'可能为冗余表达",
    ),
    RedundancyPattern(
        redundant_text="不得不说",
        correction="不得不说",
        redundancy_type=SentenceQualityType.FILLER_PHRASE,
        description="'不得不说'为废话结构",
    ),
    RedundancyPattern(
        redundant_text="不言而喻",
        correction="不言而喻",
        redundancy_type=SentenceQualityType.FILLER_PHRASE,
        description="'不言而喻'可能为冗余填充词",
    ),
    RedundancyPattern(
        redundant_text="可想而知",
        correction="可想而知",
        redundancy_type=SentenceQualityType.FILLER_PHRASE,
        description="'可想而知'可能为冗余填充词",
    ),
    RedundancyPattern(
        redundant_text="其实实际上",
        correction="实际上",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'其实'和'实际上'意思重复",
    ),
    RedundancyPattern(
        redundant_text="基本大概",
        correction="大概",
        redundancy_type=SentenceQualityType.REDUNDANT_DESCRIPTION,
        description="'基本'和'大概'意思重复",
    ),
    # 冗长的表达
    RedundancyPattern(
        redundant_text="因为其",
        correction="因为",
        redundancy_type=SentenceQualityType.WORDY_SENTENCE,
        description="'因为其'可简化为'因为'",
    ),
    RedundancyPattern(
        redundant_text="除此之外",
        correction="此外",
        redundancy_type=SentenceQualityType.WORDY_SENTENCE,
        description="'除此之外'可简化为'此外'",
    ),
    RedundancyPattern(
        redundant_text="在很大程度上",
        correction="很大程度",
        redundancy_type=SentenceQualityType.WORDY_SENTENCE,
        description="表达冗长",
    ),
    RedundancyPattern(
        redundant_text="就...而言",
        correction="对...而言",
        redundancy_type=SentenceQualityType.WORDY_SENTENCE,
        description="'就...而言'可优化为'对...而言'",
    ),
]

# Sentence quality templates
SENTENCE_QUALITY_TEMPLATES: list[SentenceQualityTemplate] = [
    # Disease sentence fixes
    SentenceQualityTemplate(
        template_name="missing_subject_fix",
        template_type="disease_fix",
        pattern=r"^[，、\s]+[的得地了着过]",
        replacement="",
        description="补全缺少的主语",
        examples=[
            ("非常的高兴。", "他非常高高兴。"),
        ],
    ),
    SentenceQualityTemplate(
        template_name="mixed_structure_fix",
        template_type="disease_fix",
        pattern=r"根据.*调查表明",
        replacement="调查表明",
        description="修正句式杂糅",
        examples=[
            ("根据调查表明情况属实。", "调查表明情况属实。"),
        ],
    ),
    # Redundancy optimizations
    SentenceQualityTemplate(
        template_name="非常极其_fix",
        template_type="redundancy_optimization",
        pattern="非常极其",
        replacement="极其",
        description="删除意思重复的词",
        examples=[
            ("非常极其重要。", "极其重要。"),
        ],
    ),
    SentenceQualityTemplate(
        template_name="各种各样_fix",
        template_type="redundancy_optimization",
        pattern="各种各样的",
        replacement="各种",
        description="简化重复结构",
        examples=[
            ("各种各样的花朵。", "各种花朵。"),
        ],
    ),
]

# Filler phrases that indicate empty/wet writing
FILLER_PHRASES: list[str] = [
    "不用说",
    "毫无疑问",
    "不可否认",
    "显而易见",
    "毫无疑问",
    "应当指出",
    "必须指出",
    "值得注意的是",
    "从某种意义上说",
    "总的来说",
    "总之",
    "总而言之",
    "换句话说",
    "也就是说",
    "即是说",
    "正如所述",
    "如前所述",
    "正如所说",
]


class SentenceQualityEngine:
    """Engine for checking and optimizing defective sentences and redundant sentences."""

    def __init__(self, ai_service: AIService):
        """Initialize sentence quality engine with AI service."""
        self.ai_service = ai_service

    def check_novel_quality(self, novel: Novel) -> SentenceQualityAnalysis:
        """Check all chapters for sentence quality issues.

        Args:
            novel: Novel to check

        Returns:
            Comprehensive sentence quality analysis
        """
        chapters = list(novel.chapters.values()) if isinstance(novel.chapters, dict) else novel.chapters
        total_chapters = len(chapters)

        if total_chapters == 0:
            return SentenceQualityAnalysis()

        # Analyze each chapter
        chapter_profiles = []
        all_issues = []

        for chapter in chapters:
            profile, issues = self.check_chapter_quality(chapter)
            chapter_profiles.append(profile)
            all_issues.extend(issues)

        # Aggregate statistics
        total_sentences = sum(p.total_sentences for p in chapter_profiles)
        total_disease = sum(p.disease_counts for p in chapter_profiles)
        total_redundant = sum(p.redundancy_counts for p in chapter_profiles)
        total_issues = len(all_issues)

        # Count by type
        issues_by_type: dict[str, int] = {}
        for issue in all_issues:
            issue_type = issue.issue_type.value
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1

        # Count by severity
        critical_count = sum(1 for i in all_issues if i.severity == SentenceQualitySeverity.CRITICAL)
        major_count = sum(1 for i in all_issues if i.severity == SentenceQualitySeverity.MAJOR)
        minor_count = sum(1 for i in all_issues if i.severity == SentenceQualitySeverity.MINOR)
        suggestion_count = sum(1 for i in all_issues if i.severity == SentenceQualitySeverity.SUGGESTION)

        # Calculate overall scores
        overall_disease = self._calculate_disease_score(total_disease, total_sentences)
        overall_redundancy = self._calculate_redundancy_score(total_redundant, total_sentences)
        overall_quality = (overall_disease + overall_redundancy) / 2

        # Find common disease types
        disease_types = [i.issue_type.value for i in all_issues
                        if i.issue_type.name.startswith("MISSING") or
                           i.issue_type.name.startswith("MISMATCH") or
                           i.issue_type.name.startswith("MIXED") or
                           i.issue_type.name.startswith("AMBIGUITY")]
        common_disease = Counter(disease_types).most_common(10)

        # Find common redundancy types
        redundancy_types = [i.issue_type.value for i in all_issues
                          if i.issue_type.name.startswith("REDUNDANT") or
                             i.issue_type.name.startswith("REPETITIVE") or
                             i.issue_type.name.startswith("WORDY") or
                             i.issue_type.name.startswith("FILLER")]
        common_redundancy = Counter(redundancy_types).most_common(10)

        # Chapters needing revision
        chapters_needing_revision = [p.chapter_number for p in chapter_profiles if p.needs_revision]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            all_issues, issues_by_type, chapters_needing_revision, total_disease, total_redundant
        )

        analysis = SentenceQualityAnalysis(
            overall_disease_score=overall_disease,
            overall_redundancy_score=overall_redundancy,
            overall_quality_score=overall_quality,
            total_chapters=total_chapters,
            total_sentences=total_sentences,
            total_disease_sentences=total_disease,
            total_redundant_sentences=total_redundant,
            total_issues=total_issues,
            issues_by_type=issues_by_type,
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            suggestion_count=suggestion_count,
            chapter_profiles=chapter_profiles,
            all_issues=all_issues,
            common_disease_types=common_disease,
            common_redundancy_types=common_redundancy,
            chapters_needing_revision=chapters_needing_revision,
            has_critical_issues=critical_count > 0,
            recommendations=recommendations,
        )

        return analysis

    def check_chapter_quality(self, chapter: Chapter) -> tuple[ChapterSentenceQualityProfile, list[SentenceQualityIssue]]:
        """Check a single chapter for sentence quality issues.

        Args:
            chapter: Chapter to check

        Returns:
            Tuple of (chapter profile, list of issues)
        """
        content = chapter.content or ""
        issues = []

        if not content:
            return ChapterSentenceQualityProfile(
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
            sentence_issues = self._check_sentence_quality(sentence, chapter.number, idx)
            issues.extend(sentence_issues)

        # Check for redundancy patterns across content
        redundancy_issues = self._check_redundancy_patterns(content, chapter.number)
        issues.extend(redundancy_issues)

        # Check for disease sentence patterns
        disease_issues = self._check_disease_patterns(content, chapter.number)
        issues.extend(disease_issues)

        # Check for filler phrases
        filler_issues = self._check_filler_phrases(content, chapter.number)
        issues.extend(filler_issues)

        # Count issues by type
        issue_counts: dict[str, int] = {}
        disease_counts = 0
        redundancy_counts = 0

        for issue in issues:
            issue_type = issue.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

            # Categorize as disease or redundancy
            if issue.issue_type.name.startswith(("MISSING", "MISMATCH", "MIXED", "AMBIGUITY",
                                                   "WRONG", "SELF_CONTRADICTION", "VAGUE")):
                disease_counts += 1
            elif issue.issue_type.name.startswith(("REDUNDANT", "REPETITIVE", "WORDY", "FILLER",
                                                    "EMPTY", "UNNECESSARY", "TAUTOLOGICAL")):
                redundancy_counts += 1

        # Severity distribution
        critical_issues = sum(1 for i in issues if i.severity == SentenceQualitySeverity.CRITICAL)
        major_issues = sum(1 for i in issues if i.severity == SentenceQualitySeverity.MAJOR)
        minor_issues = sum(1 for i in issues if i.severity == SentenceQualitySeverity.MINOR)
        suggestions = sum(1 for i in issues if i.severity == SentenceQualitySeverity.SUGGESTION)

        # Calculate scores
        disease_score = max(0.0, 1.0 - (disease_counts / max(1, total_sentences)) * 0.5)
        redundancy_score = max(0.0, 1.0 - (redundancy_counts / max(1, total_sentences)) * 0.3)
        overall_score = (disease_score + redundancy_score) / 2

        # Quality indicators
        needs_revision = major_issues > 0 or critical_issues > 0 or (minor_issues > total_sentences * 0.1)
        is_concise = redundancy_score > 0.9 and not (redundancy_counts > total_sentences * 0.05)

        profile = ChapterSentenceQualityProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title or "",
            total_sentences=total_sentences,
            total_characters=total_characters,
            dialogue_sentences=dialogue_sentences,
            narration_sentences=narration_sentences,
            issue_counts=issue_counts,
            disease_counts=disease_counts,
            redundancy_counts=redundancy_counts,
            total_issues=len(issues),
            critical_issues=critical_issues,
            major_issues=major_issues,
            minor_issues=minor_issues,
            suggestions=suggestions,
            disease_sentence_score=disease_score,
            redundancy_score=redundancy_score,
            overall_quality_score=overall_score,
            needs_revision=needs_revision,
            is_concise=is_concise,
        )

        return profile, issues

    def create_revision_plan(self, analysis: SentenceQualityAnalysis) -> SentenceQualityPlan:
        """Create a revision plan based on analysis.

        Args:
            analysis: Sentence quality analysis

        Returns:
            Revision plan
        """
        critical_ids = [i.issue_id for i in analysis.all_issues
                       if i.severity == SentenceQualitySeverity.CRITICAL]
        major_ids = [i.issue_id for i in analysis.all_issues
                    if i.severity == SentenceQualitySeverity.MAJOR]
        minor_ids = [i.issue_id for i in analysis.all_issues
                    if i.severity == SentenceQualitySeverity.MINOR]
        suggestion_ids = [i.issue_id for i in analysis.all_issues
                        if i.severity == SentenceQualitySeverity.SUGGESTION]

        # Categorize issues
        disease_ids = [i.issue_id for i in analysis.all_issues
                      if i.issue_type.name.startswith(("MISSING", "MISMATCH", "MIXED", "AMBIGUITY",
                                                       "WRONG", "SELF_CONTRADICTION", "VAGUE"))]
        redundancy_ids = [i.issue_id for i in analysis.all_issues
                         if i.issue_type.name.startswith(("REDUNDANT", "REPETITIVE", "WORDY", "FILLER",
                                                           "EMPTY", "UNNECESSARY", "TAUTOLOGICAL"))]

        # Create priority order
        priority_order: list[tuple[str, int]] = []
        for iid in critical_ids:
            priority_order.append((iid, 100))
        for iid in major_ids:
            priority_order.append((iid, 70))
        for iid in minor_ids:
            priority_order.append((iid, 30))
        for iid in suggestion_ids:
            priority_order.append((iid, 10))

        priority_order.sort(key=lambda x: x[1], reverse=True)

        plan = SentenceQualityPlan(
            critical_to_fix=critical_ids,
            major_to_fix=major_ids,
            minor_to_fix=minor_ids,
            suggestions_to_apply=suggestion_ids,
            disease_fixes=disease_ids,
            redundancy_optimizations=redundancy_ids,
            chapters_to_revise=analysis.chapters_needing_revision,
            priority_order=priority_order,
            estimated_disease_fixes=len(disease_ids),
            estimated_redundancy_optimizations=len(redundancy_ids),
            ai_assistance_needed=len(analysis.all_issues) > 10,
            focus_on_disease_sentences=len(disease_ids) > 0,
            focus_on_redundancy=len(redundancy_ids) > 0,
        )

        return plan

    def generate_quality_report(
        self,
        analysis: SentenceQualityAnalysis,
        plan: Optional[SentenceQualityPlan] = None,
    ) -> SentenceQualityReport:
        """Generate a complete quality report.

        Args:
            analysis: Sentence quality analysis
            plan: Optional revision plan

        Returns:
            Complete quality report
        """
        if plan is None:
            plan = self.create_revision_plan(analysis)

        summary = self._generate_summary(analysis)

        report = SentenceQualityReport(
            analysis=analysis,
            revision_plan=plan,
            summary=summary,
            revisions_completed=[],
        )

        return report

    def get_quality_summary(self, analysis: SentenceQualityAnalysis) -> str:
        """Get a human-readable summary of sentence quality check.

        Args:
            analysis: Sentence quality analysis

        Returns:
            Summary string
        """
        lines = [
            "=== 病句与冗余句子优化报告 ===",
            "",
            f"检查章节数: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"病句数量: {analysis.total_disease_sentences}",
            f"冗余句子数量: {analysis.total_redundant_sentences}",
            f"总问题数: {analysis.total_issues}",
            "",
            "--- 问题分布 ---",
            f"严重问题: {analysis.critical_count}",
            f"较大问题: {analysis.major_count}",
            f"一般问题: {analysis.minor_count}",
            f"优化建议: {analysis.suggestion_count}",
            "",
            "--- 评分 ---",
            f"病句评分: {analysis.overall_disease_score:.0%}",
            f"冗余评分: {analysis.overall_redundancy_score:.0%}",
            f"综合评分: {analysis.overall_quality_score:.0%}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision))}")

        if analysis.common_disease_types:
            lines.append("")
            lines.append("--- 常见病句类型 ---")
            for dtype, count in analysis.common_disease_types[:5]:
                lines.append(f"  {dtype}: {count}次")

        if analysis.common_redundancy_types:
            lines.append("")
            lines.append("--- 常见冗余类型 ---")
            for rtype, count in analysis.common_redundancy_types[:5]:
                lines.append(f"  {rtype}: {count}次")

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

    def _check_sentence_quality(self, sentence: str, chapter: int, sentence_idx: int) -> list[SentenceQualityIssue]:
        """Check a single sentence for quality issues."""
        issues = []

        # Check disease patterns
        for pattern in DISEASE_PATTERNS:
            matches = re.finditer(pattern.pattern, sentence)
            for match in matches:
                issue = SentenceQualityIssue(
                    issue_id=f"disease_{chapter}_{sentence_idx}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=sentence,
                    position=match.start(),
                    issue_type=pattern.issue_type,
                    severity=pattern.severity,
                    original_text=match.group(),
                    suggested_fix="",
                    description=pattern.description,
                    confidence=0.8,
                    reason=f"病句: {pattern.description}",
                )
                issues.append(issue)

        return issues

    def _check_redundancy_patterns(self, content: str, chapter: int) -> list[SentenceQualityIssue]:
        """Check for redundancy patterns in content."""
        issues = []

        for pattern in REDUNDANCY_PATTERNS:
            redundant = pattern.redundant_text
            if redundant in content:
                idx = 0
                while True:
                    idx = content.find(redundant, idx)
                    if idx == -1:
                        break

                    context = self._get_context_sentence(content, idx)

                    issue = SentenceQualityIssue(
                        issue_id=f"redundancy_{chapter}_{uuid.uuid4().hex[:6]}",
                        chapter=chapter,
                        sentence=context,
                        position=idx,
                        issue_type=pattern.redundancy_type,
                        severity=SentenceQualitySeverity.MINOR,
                        original_text=redundant,
                        suggested_fix=pattern.correction,
                        description=pattern.description,
                        confidence=0.9,
                        reason=f"冗余: {pattern.description}",
                    )
                    issues.append(issue)
                    idx += len(redundant)

        return issues

    def _check_disease_patterns(self, content: str, chapter: int) -> list[SentenceQualityIssue]:
        """Check for disease sentence patterns in content."""
        issues = []

        # Check for empty/promising sentences
        empty_patterns = [
            (r"^[，。、\s]+$", "只有标点符号的句子"),
            (r"^的$", "只有一个字'的'的句子"),
        ]

        for pattern, desc in empty_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                lines = content[:match.start()].count('\n') + 1
                issue = SentenceQualityIssue(
                    issue_id=f"disease_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=match.group(),
                    position=match.start(),
                    issue_type=SentenceQualityType.VAGUE_EXPRESSION,
                    severity=SentenceQualitySeverity.CRITICAL,
                    original_text=match.group(),
                    suggested_fix="",
                    description=desc,
                    confidence=0.95,
                    reason=f"病句: {desc}",
                )
                issues.append(issue)

        return issues

    def _check_filler_phrases(self, content: str, chapter: int) -> list[SentenceQualityIssue]:
        """Check for filler phrases in content."""
        issues = []

        for filler in FILLER_PHRASES:
            if filler in content:
                idx = 0
                while True:
                    idx = content.find(filler, idx)
                    if idx == -1:
                        break

                    context = self._get_context_sentence(content, idx)

                    issue = SentenceQualityIssue(
                        issue_id=f"filler_{chapter}_{uuid.uuid4().hex[:6]}",
                        chapter=chapter,
                        sentence=context,
                        position=idx,
                        issue_type=SentenceQualityType.FILLER_PHRASE,
                        severity=SentenceQualitySeverity.SUGGESTION,
                        original_text=filler,
                        suggested_fix="",
                        description=f"填充词/废话结构: {filler}",
                        confidence=0.7,
                        reason=f"冗余: 填充词结构，建议删除或简化",
                    )
                    issues.append(issue)
                    idx += len(filler)

        return issues

    def _get_context_sentence(self, content: str, position: int, context_size: int = 30) -> str:
        """Get the sentence containing the position."""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)

        before = content[start:position]
        after = content[position:end]

        for i in range(len(before) - 1, -1, -1):
            if before[i] in '。！？?!\n':
                start = start + i + 1
                break

        for i, c in enumerate(after):
            if c in '。！？?!\n':
                end = position + i + 1
                break

        return content[start:end].strip()

    def _calculate_disease_score(self, disease_count: int, total_sentences: int) -> float:
        """Calculate disease sentence score."""
        if total_sentences == 0:
            return 1.0
        return max(0.0, 1.0 - (disease_count / total_sentences) * 0.5)

    def _calculate_redundancy_score(self, redundancy_count: int, total_sentences: int) -> float:
        """Calculate redundancy score."""
        if total_sentences == 0:
            return 1.0
        return max(0.0, 1.0 - (redundancy_count / total_sentences) * 0.3)

    def _generate_recommendations(
        self,
        issues: list[SentenceQualityIssue],
        issues_by_type: dict[str, int],
        chapters_needing_revision: list[int],
        total_disease: int,
        total_redundant: int,
    ) -> list[str]:
        """Generate recommendations based on issues."""
        recs = []

        # Critical issues
        critical = [i for i in issues if i.severity == SentenceQualitySeverity.CRITICAL]
        if critical:
            recs.append(f"存在 {len(critical)} 个严重问题，必须立即修正")

        # Major issues
        major = [i for i in issues if i.severity == SentenceQualitySeverity.MAJOR]
        if major:
            recs.append(f"存在 {len(major)} 个较大问题，建议优先修正")

        # Disease sentences
        if total_disease > 5:
            recs.append(f"发现 {total_disease} 个病句，建议重点修改病句以提高文章质量")

        # Redundancy
        if total_redundant > 10:
            recs.append(f"发现 {total_redundant} 处冗余表达，建议精简以提高文章简洁度")

        # Common issues by type
        if issues_by_type:
            most_common = max(issues_by_type.items(), key=lambda x: x[1], default=(None, 0))
            if most_common[0]:
                recs.append(f"最常见的问题是 {most_common[0]}，共出现 {most_common[1]} 次")

        # Chapter-specific
        if len(chapters_needing_revision) > 5:
            recs.append(f"有 {len(chapters_needing_revision)} 个章节需要重点修改")

        # Suggestion-level
        suggestions = [i for i in issues if i.severity == SentenceQualitySeverity.SUGGESTION]
        if suggestions and len(suggestions) > 20:
            recs.append(f"有 {len(suggestions)} 处可优化的冗余表达，可选择性处理")

        if not recs:
            recs.append("整体句子质量良好，仅需小幅优化")

        return recs

    def _generate_summary(self, analysis: SentenceQualityAnalysis) -> str:
        """Generate human-readable summary."""
        lines = [
            "《病句与冗余句子优化报告》",
            "",
            f"检查章节: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"病句数量: {analysis.total_disease_sentences}",
            f"冗余句子数量: {analysis.total_redundant_sentences}",
            f"总问题数: {analysis.total_issues}",
            "",
            "问题分布:",
            f"  严重问题: {analysis.critical_count}",
            f"  较大问题: {analysis.major_count}",
            f"  一般问题: {analysis.minor_count}",
            f"  优化建议: {analysis.suggestion_count}",
            "",
            "评分:",
            f"  病句评分: {analysis.overall_disease_score:.0%}",
            f"  冗余评分: {analysis.overall_redundancy_score:.0%}",
            f"  综合评分: {analysis.overall_quality_score:.0%}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision[:10]))}")
            if len(analysis.chapters_needing_revision) > 10:
                lines.append(f"  (还有 {len(analysis.chapters_needing_revision) - 10} 个)")

        if analysis.common_disease_types:
            lines.append("")
            lines.append("常见病句类型:")
            for dtype, count in analysis.common_disease_types[:5]:
                lines.append(f"  {dtype}: {count}次")

        if analysis.common_redundancy_types:
            lines.append("")
            lines.append("常见冗余类型:")
            for rtype, count in analysis.common_redundancy_types[:5]:
                lines.append(f"  {rtype}: {count}次")

        return "\n".join(lines)
