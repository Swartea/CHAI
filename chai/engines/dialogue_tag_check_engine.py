"""Dialogue tag standardization check engine for quality assurance."""

import re
import uuid
from typing import Optional
from collections import Counter

from chai.models import Novel, Chapter
from chai.models.dialogue_tag_check import (
    DialogueTagType,
    DialogueTagIssueType,
    DialogueTagSeverity,
    DialogueTagStyle,
    DialogueTagPattern,
    DialogueTagIssue,
    DialogueTagCheckResult,
    ChapterDialogueTagProfile,
    DialogueTagCheckAnalysis,
    DialogueTagCheckRevision,
    DialogueTagCheckPlan,
    DialogueTagCheckReport,
    DialogueTagTemplate,
)
from chai.services import AIService


# Standard dialogue tag verbs in Chinese
STANDARD_TAG_VERBS = [
    "说", "道", "问", "答", "回答", "回应",
    "喊", "叫道", "喊道", "呼", "惊呼",
    "低语", "轻声", "小声", "喃喃", "喃喃道",
    "笑", "笑道", "笑着说", "笑着", "微笑", "微笑着",
    "哭", "哭道", "泣道", "哽咽道",
    "叹息道", "叹道", "叹气",
    "叹道", "补充道", "解释道", "提醒道",
    "嘟囔道", "嘀咕道", "怒道", "厉声道",
    "冷冷道", "淡淡道", "缓缓道", "慢慢道",
    "沉声道", "沉声道", "低声道", "高声道",
]

# Common non-standard or inconsistent tag verbs
NON_STANDARD_TAGS = [
    "表示", "指出", "认为", "以为", "感觉",
    "发现", "看到", "听到", "想到", "觉得",
]

# Quote patterns for different styles
QUOTE_PATTERNS = {
    DialogueTagStyle.CHINESE_MARKS: (r'「([^「」]*)」', r'「([^「」]*)」'),
    DialogueTagStyle.CHINESE_SINGLE: (r'『([^『』]*)』', r'『([^『』]*)』'),
    DialogueTagStyle.STRAIGHT_DOUBLE: (r'"([^"]*)"', r'"([^"]*)"'),
    DialogueTagStyle.ANGLE_BRACKETS: (r'《([^《》]*)》', r'《([^《》]*)》'),
}

# Dialogue tag patterns for detection
DIALOGUE_PATTERNS = [
    DialogueTagPattern(
        pattern=r'「([^「」]*)」[，、]?([\u4e00-\u9fa5]{1,4})[道说问答喊叫]?[，、。]',
        issue_type=DialogueTagIssueType.TAG_AFTER_COMMA,
        description="标签在逗号/顿号后，可能导致阅读不畅",
        severity=DialogueTagSeverity.MINOR,
    ),
    DialogueTagPattern(
        pattern=r'"([^"]*)"[，、]?([\u4e00-\u9fa5]{1,4})[道说问答喊叫]?[，。]',
        issue_type=DialogueTagIssueType.TAG_AFTER_COMMA,
        description="标签在逗号/顿号后，可能导致阅读不畅",
        severity=DialogueTagSeverity.MINOR,
    ),
]

# Standard templates for different genres
STANDARD_TEMPLATES: dict[str, DialogueTagTemplate] = {
    "default": DialogueTagTemplate(
        id="default",
        name="默认风格",
        quote_style=DialogueTagStyle.CHINESE_MARKS,
        example_before="他说：「你好。」",
        example_after="他说：「你好。」",
        tag_placement=DialogueTagStyle.TAG_BEFORE,
        preferred_tag_verbs=["说", "道", "问", "答", "喊", "低语"],
        discouraged_tag_verbs=["表示", "指出", "认为"],
        punctuation_before_tag="，",
        punctuation_after_tag="：",
    ),
    "formal": DialogueTagTemplate(
        id="formal",
        name="正式风格",
        quote_style=DialogueTagStyle.CHINESE_MARKS,
        example_before="他沉声道：「此事需从长计议。」",
        example_after="他沉声道：「此事需从长计议。」",
        tag_placement=DialogueTagStyle.TAG_BEFORE,
        preferred_tag_verbs=["说", "道", "沉声道", "缓缓道", "淡淡道"],
        discouraged_tag_verbs=["笑", "喊道", "嘟囔道"],
        punctuation_before_tag="，",
        punctuation_after_tag="：",
    ),
    "literary": DialogueTagTemplate(
        id="literary",
        name="文学风格",
        quote_style=DialogueTagStyle.CHINESE_SINGLE,
        example_before="她轻声道：『此去经年，应是良辰好景虚设。』",
        example_after="她轻声道：『此去经年，应是良辰好景虚设。』",
        tag_placement=DialogueTagStyle.TAG_BEFORE,
        preferred_tag_verbs=["道", "问", "答", "低语", "叹息道"],
        discouraged_tag_verbs=["喊", "叫道", "嘟囔道"],
        punctuation_before_tag="，",
        punctuation_after_tag="：",
    ),
}


class DialogueTagCheckEngine:
    """Engine for checking and standardizing dialogue tags."""

    def __init__(self, ai_service: AIService):
        """Initialize dialogue tag check engine."""
        self.ai_service = ai_service

    def _extract_dialogues(self, content: str) -> list[tuple[str, str, str]]:
        """Extract dialogues from content.

        Returns:
            List of tuples: (full_match, quote_content, tag_part)
        """
        dialogues = []

        # Extract 「」 dialogues
        for match in re.finditer(r'「([^」]*)」', content):
            quote_content = match.group(1)
            position = match.start()
            # Look for tag before or after
            before = content[:position]
            after = content[match.end():]
            dialogues.append((match.group(0), quote_content, f"before:{before[-10:] if before else ''} after:{after[:10] if after else ''}"))

        # Extract "" dialogues
        for match in re.finditer(r'"([^"]*)"', content):
            quote_content = match.group(1)
            position = match.start()
            before = content[:position]
            after = content[match.end():]
            dialogues.append((match.group(0), quote_content, f"before:{before[-10:] if before else ''} after:{after[:10] if after else ''}"))

        # Extract 『』 dialogues
        for match in re.finditer(r'『([^』]*)』', content):
            quote_content = match.group(1)
            position = match.start()
            before = content[:position]
            after = content[match.end():]
            dialogues.append((match.group(0), quote_content, f"before:{before[-10:] if before else ''} after:{after[:10] if after else ''}"))

        return dialogues

    def _detect_quote_style(self, content: str) -> DialogueTagStyle:
        """Detect the dominant quote style in content."""
        chinese_marks = len(re.findall(r'「|」', content))
        chinese_single = len(re.findall(r'『|』', content))
        straight_double = len(re.findall(r'"', content))

        counts = {
            DialogueTagStyle.CHINESE_MARKS: chinese_marks // 2,
            DialogueTagStyle.CHINESE_SINGLE: chinese_single // 2,
            DialogueTagStyle.STRAIGHT_DOUBLE: straight_double,
        }

        if counts[DialogueTagStyle.CHINESE_MARKS] == 0 and counts[DialogueTagStyle.CHINESE_SINGLE] == 0 and counts[DialogueTagStyle.STRAIGHT_DOUBLE] == 0:
            return DialogueTagStyle.CHINESE_MARKS

        return max(counts, key=counts.get)

    def _detect_tag_verbs(self, content: str) -> Counter:
        """Detect tag verbs used in content."""
        tag_verbs = []

        # Pattern for tag verbs after dialogue
        patterns = [
            r'」[，、]?([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹]?',
            r'"[，、]?([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹]?',
            r'』[，、]?([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹]?',
            # Pattern for tag verbs before dialogue
            r'([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹道]+[：:，「」]?\s*「',
            r'([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹道]+[：:，「」]?\s*"',
            r'([\u4e00-\u9fa5]{1,4})[道说问答喊叫低语轻叹道]+[：:，「」]?\s*『',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            tag_verbs.extend(matches)

        # Normalize: remove common suffixes
        normalized = []
        for verb in tag_verbs:
            if verb.endswith('道'):
                verb = verb[:-1]
            if verb.endswith('说'):
                verb = verb[:-1]
            if verb in ['笑着说', '笑着', '微笑', '微笑着']:
                verb = '笑'
            elif verb in ['低声', '轻声道', '小声道', '喃喃道', '喃喃']:
                verb = '低语'
            elif verb in ['叹道', '叹息道', '叹气']:
                verb = '叹息'
            elif verb in ['怒道', '厉声道', '冷冷道', '淡淡道', '缓缓道', '慢慢道', '沉声道', '高声道']:
                verb = verb[:2] if len(verb) > 2 else verb
            normalized.append(verb)

        return Counter(normalized)

    def _detect_tag_placement(self, content: str) -> dict[str, int]:
        """Detect tag placement patterns."""
        tag_after = len(re.findall(r'[」"』][，、]?[\u4e00-\u9fa5]{1,4}[道说问答喊叫]', content))
        tag_before = len(re.findall(r'[\u4e00-\u9fa5]{1,4}[道说问答喊叫道][：:]?\s*[「"『]', content))

        return {
            "tag_after": tag_after,
            "tag_before": tag_before,
            "no_tag": len(re.findall(r'[「"『][^」"』]*[」"』](?![，、]?[\u4e00-\u9fa5])', content)),
        }

    def _check_quote_consistency(self, content: str) -> list[DialogueTagIssue]:
        """Check for quote style consistency issues."""
        issues = []
        chinese_marks = len(re.findall(r'「|」', content))
        chinese_single = len(re.findall(r'『|』', content))
        straight_double = len(re.findall(r'"', content))

        # Detect mixed usage
        quote_types_used = []
        if chinese_marks > 0:
            quote_types_used.append("「」")
        if chinese_single > 0:
            quote_types_used.append("『』")
        if straight_double > 0:
            quote_types_used.append('""')

        if len(quote_types_used) > 1:
            issues.append(DialogueTagIssue(
                issue_id=str(uuid.uuid4()),
                chapter=0,
                sentence="",
                position=0,
                issue_type=DialogueTagIssueType.MIXED_QUOTE_TYPES,
                severity=DialogueTagSeverity.MAJOR,
                original_text=f"混用引号: {', '.join(quote_types_used)}",
                suggested_fix=f"统一使用{quote_types_used[0]}",
                description=f"检测到混用引号类型: {', '.join(quote_types_used)}",
                confidence=0.9,
            ))

        return issues

    def _check_tag_verb_consistency(self, content: str) -> list[DialogueTagIssue]:
        """Check for tag verb consistency issues."""
        issues = []
        tag_verbs = self._detect_tag_verbs(content)

        if len(tag_verbs) < 2:
            return issues

        # Check for non-standard tags
        most_common = tag_verbs.most_common(1)[0][0] if tag_verbs else None

        for verb, count in tag_verbs.items():
            if verb in NON_STANDARD_TAGS:
                issues.append(DialogueTagIssue(
                    issue_id=str(uuid.uuid4()),
                    chapter=0,
                    sentence="",
                    position=0,
                    issue_type=DialogueTagIssueType.NON_STANDARD_TAG,
                    severity=DialogueTagSeverity.MINOR,
                    original_text=verb,
                    suggested_fix=f"使用标准标签动词如「说」「道」替代「{verb}」",
                    description=f"非标准标签动词: 「{verb}」出现{count}次",
                    dialogue_tag_type=DialogueTagType.SAID,
                    confidence=0.8,
                ))

        return issues

    def _check_dialogue_result(self, passage: str) -> DialogueTagCheckResult:
        """Check a single dialogue passage for tag issues."""
        issues = []

        # Check quote consistency
        issues.extend(self._check_quote_consistency(passage))

        # Check tag verb consistency
        issues.extend(self._check_tag_verb_consistency(passage))

        # Check for tag after comma
        for pattern in DIALOGUE_PATTERNS:
            matches = re.finditer(pattern.pattern, passage)
            for match in matches:
                issues.append(DialogueTagIssue(
                    issue_id=str(uuid.uuid4()),
                    chapter=0,
                    sentence=passage,
                    position=match.start(),
                    issue_type=pattern.issue_type,
                    severity=pattern.severity,
                    original_text=match.group(0),
                    suggested_fix="调整标签位置",
                    description=pattern.description,
                    confidence=0.7,
                ))

        # Check for unclosed dialogue
        open_quotes = passage.count('「') + passage.count('"') + passage.count('『')
        close_quotes = passage.count('」') + passage.count('"') + passage.count('』')
        if open_quotes != close_quotes:
            issues.append(DialogueTagIssue(
                issue_id=str(uuid.uuid4()),
                chapter=0,
                sentence=passage,
                position=0,
                issue_type=DialogueTagIssueType.UNCLOSED_DIALOGUE,
                severity=DialogueTagSeverity.CRITICAL,
                original_text=passage,
                suggested_fix="确保引号成对出现",
                description="引号未成对出现，可能有未关闭的对话",
                confidence=0.95,
            ))

        tag_score = max(0.0, 1.0 - len(issues) * 0.1)

        return DialogueTagCheckResult(
            passage=passage,
            passage_type="dialogue",
            issue_count=len(issues),
            issues=issues,
            tag_score=tag_score,
            has_critical_issues=any(i.severity == DialogueTagSeverity.CRITICAL for i in issues),
        )

    def check_chapter_dialogue_tags(
        self,
        chapter: Chapter,
        target_quote_style: DialogueTagStyle = DialogueTagStyle.CHINESE_MARKS,
        target_tag_placement: DialogueTagStyle = DialogueTagStyle.TAG_BEFORE,
    ) -> ChapterDialogueTagProfile:
        """Check dialogue tags in a single chapter.

        Args:
            chapter: Chapter to check
            target_quote_style: Target quote style to enforce
            target_tag_placement: Target tag placement

        Returns:
            Chapter dialogue tag profile
        """
        content = chapter.content if hasattr(chapter, 'content') else str(chapter)

        # Extract dialogues
        dialogues = self._extract_dialogues(content)

        # Detect quote style
        quote_style = self._detect_quote_style(content)

        # Detect tag verbs
        tag_verbs = self._detect_tag_verbs(content)

        # Detect tag placement
        placement = self._detect_tag_placement(content)

        # Count quote styles
        chinese_marks = len(re.findall(r'「[^」]*」', content))
        chinese_single = len(re.findall(r'『[^』]*』', content))
        straight_double = len(re.findall(r'"[^"]*"', content))

        # Check for issues
        issues = []
        issues.extend(self._check_quote_consistency(content))
        issues.extend(self._check_tag_verb_consistency(content))

        # Count action tags
        action_tag_pattern = r'[笑|哭|低|轻|沉|怒|叹|惊|喃][地道说问道]?[着]?'
        action_tags = len(re.findall(action_tag_pattern, content))

        # Determine severity counts
        critical_count = sum(1 for i in issues if i.severity == DialogueTagSeverity.CRITICAL)
        major_count = sum(1 for i in issues if i.severity == DialogueTagSeverity.MAJOR)
        minor_count = sum(1 for i in issues if i.severity == DialogueTagSeverity.MINOR)
        typographical_count = sum(1 for i in issues if i.severity == DialogueTagSeverity.TYPOGRAPHICAL)

        # Calculate scores
        quote_consistency = 1.0 if len([k for k, v in {
            DialogueTagStyle.CHINESE_MARKS: chinese_marks,
            DialogueTagStyle.CHINESE_SINGLE: chinese_single,
            DialogueTagStyle.STRAIGHT_DOUBLE: straight_double,
        }.items() if v > 0]) <= 1 else 0.7

        verb_consistency = 1.0 if len(tag_verbs) <= 5 else max(0.5, 1.0 - (len(tag_verbs) - 5) * 0.05)

        placement_total = placement["tag_after"] + placement["tag_before"]
        placement_consistency = 1.0 if placement_total == 0 else abs(placement["tag_after"] - placement["tag_before"]) / placement_total

        overall_score = (quote_consistency + verb_consistency + placement_consistency) / 3

        return ChapterDialogueTagProfile(
            chapter_number=chapter.number if hasattr(chapter, 'number') else 0,
            chapter_title=chapter.title if hasattr(chapter, 'title') else "",
            total_dialogues=len(dialogues),
            total_dialogue_lines=sum(1 for _ in re.findall(r'[「"『]', content)) // 2,
            chinese_marks_count=chinese_marks,
            chinese_single_count=chinese_single,
            straight_double_count=straight_double,
            tag_verb_counts=dict(tag_verbs),
            most_common_tag_verb=tag_verbs.most_common(1)[0][0] if tag_verbs else "",
            tag_verb_variety=len(tag_verbs),
            tag_after_count=placement["tag_after"],
            tag_before_count=placement["tag_before"],
            no_tag_count=placement["no_tag"],
            action_tag_count=action_tags,
            no_action_tag_count=len(dialogues) - action_tags if dialogues else 0,
            issue_counts={},
            total_issues=len(issues),
            critical_issues=critical_count,
            major_issues=major_count,
            minor_issues=minor_count,
            typographical_issues=typographical_count,
            tag_score=overall_score,
            quote_consistency_score=quote_consistency,
            verb_consistency_score=verb_consistency,
            placement_consistency_score=placement_consistency,
            primary_quote_style=quote_style,
            is_style_consistent=quote_consistency >= 0.9,
            dominant_tag_placement=DialogueTagStyle.TAG_BEFORE if placement["tag_before"] > placement["tag_after"] else DialogueTagStyle.TAG_AFTER,
            needs_revision=critical_count > 0 or major_count > 0,
        )

    def check_novel_dialogue_tags(
        self,
        novel: Novel,
        target_quote_style: DialogueTagStyle = DialogueTagStyle.CHINESE_MARKS,
        target_tag_placement: DialogueTagStyle = DialogueTagStyle.TAG_BEFORE,
    ) -> DialogueTagCheckAnalysis:
        """Check dialogue tags in entire novel.

        Args:
            novel: Novel to check
            target_quote_style: Target quote style to enforce
            target_tag_placement: Target tag placement

        Returns:
            Comprehensive dialogue tag analysis
        """
        chapter_profiles = []
        all_issues = []
        total_dialogues = 0
        total_dialogue_lines = 0

        quote_styles: Counter = Counter()
        tag_verb_usage: Counter = Counter()
        tag_placement_distribution: Counter = Counter()

        for volume in novel.volumes:
            for chapter in volume.chapters:
                profile = self.check_chapter_dialogue_tags(
                    chapter,
                    target_quote_style,
                    target_tag_placement,
                )
                chapter_profiles.append(profile)
                all_issues.extend(profile.total_issues > 0 and [] or [])

                total_dialogues += profile.total_dialogues
                total_dialogue_lines += profile.total_dialogue_lines

                quote_styles[profile.primary_quote_style] += 1
                tag_verb_usage.update(profile.tag_verb_counts)
                tag_placement_distribution["tag_before"] += profile.tag_before_count
                tag_placement_distribution["tag_after"] += profile.tag_after_count

        # Aggregate issues from all chapters
        for profile in chapter_profiles:
            if profile.total_issues > 0:
                # Re-check each chapter for issues to aggregate
                content = ""
                for vol in novel.volumes:
                    for ch in vol.chapters:
                        if ch.number == profile.chapter_number:
                            content = ch.content
                            break
                if content:
                    chapter_issues = []
                    chapter_issues.extend(self._check_quote_consistency(content))
                    chapter_issues.extend(self._check_tag_verb_consistency(content))
                    for issue in chapter_issues:
                        issue.chapter = profile.chapter_number
                        all_issues.append(issue)

        # Determine overall quote style
        if quote_styles:
            primary_style = quote_styles.most_common(1)[0][0]
            is_consistent = quote_styles.most_common(1)[0][1] == len(chapter_profiles) if chapter_profiles else True
        else:
            primary_style = DialogueTagStyle.CHINESE_MARKS
            is_consistent = True

        # Calculate overall scores
        overall_quote_score = sum(p.quote_consistency_score for p in chapter_profiles) / len(chapter_profiles) if chapter_profiles else 1.0
        overall_verb_score = sum(p.verb_consistency_score for p in chapter_profiles) / len(chapter_profiles) if chapter_profiles else 1.0
        overall_placement_score = sum(p.placement_consistency_score for p in chapter_profiles) / len(chapter_profiles) if chapter_profiles else 1.0
        overall_tag_score = (overall_quote_score + overall_verb_score + overall_placement_score) / 3

        # Severity counts
        critical_count = sum(p.critical_issues for p in chapter_profiles)
        major_count = sum(p.major_issues for p in chapter_profiles)
        minor_count = sum(p.minor_issues for p in chapter_profiles)
        typographical_count = sum(p.typographical_issues for p in chapter_profiles)

        # Generate recommendations
        recommendations = []
        if not is_consistent:
            recommendations.append(f"统一全书的引号风格，建议使用「」")
        if tag_verb_usage:
            most_common = tag_verb_usage.most_common(1)[0][0]
            if most_common not in STANDARD_TAG_VERBS:
                recommendations.append(f"常用的标签动词「{most_common}」不是标准用法，建议使用「说」或「道」")
        if tag_placement_distribution["tag_before"] != tag_placement_distribution["tag_after"]:
            dominant = "tag_before" if tag_placement_distribution["tag_before"] > tag_placement_distribution["tag_after"] else "tag_after"
            recommendations.append(f"统一标签位置，建议标签放在对话前面（他说：「...」）")

        return DialogueTagCheckAnalysis(
            overall_tag_score=overall_tag_score,
            overall_quote_consistency_score=overall_quote_score,
            overall_verb_consistency_score=overall_verb_score,
            overall_placement_consistency_score=overall_placement_score,
            total_chapters=len(chapter_profiles),
            total_dialogues=total_dialogues,
            total_dialogue_lines=total_dialogue_lines,
            quote_style_distribution=dict(quote_styles),
            primary_quote_style=primary_style,
            is_quote_style_consistent=is_consistent,
            tag_verb_usage=dict(tag_verb_usage),
            most_common_tag_verb=tag_verb_usage.most_common(1)[0][0] if tag_verb_usage else "",
            tag_verb_variety=len(tag_verb_usage),
            tag_placement_distribution=dict(tag_placement_distribution),
            dominant_placement=DialogueTagStyle.TAG_BEFORE if tag_placement_distribution.get("tag_before", 0) > tag_placement_distribution.get("tag_after", 0) else DialogueTagStyle.TAG_AFTER,
            issues_by_type={},
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            typographical_count=typographical_count,
            chapter_profiles=chapter_profiles,
            all_issues=all_issues,
            recommendations=recommendations,
        )

    def create_revision_plan(
        self,
        analysis: DialogueTagCheckAnalysis,
        target_quote_style: DialogueTagStyle = DialogueTagStyle.CHINESE_MARKS,
        target_tag_placement: DialogueTagStyle = DialogueTagStyle.TAG_BEFORE,
    ) -> DialogueTagCheckPlan:
        """Create a revision plan for dialogue tag standardization.

        Args:
            analysis: Analysis results
            target_quote_style: Target quote style
            target_tag_placement: Target tag placement

        Returns:
            Revision plan
        """
        priority_fixes = [i.issue_id for i in analysis.all_issues if i.severity in [DialogueTagSeverity.CRITICAL, DialogueTagSeverity.MAJOR]]

        revision_order = ["quote_style", "tag_placement", "tag_verbs"]

        return DialogueTagCheckPlan(
            chapter_number=0,
            issues_to_fix=priority_fixes,
            target_quote_style=target_quote_style,
            target_tag_placement=target_tag_placement,
            standardize_tag_verbs=True,
            keep_action_tags=True,
            revision_order=revision_order,
        )

    async def revise_chapter_dialogue_tags(
        self,
        chapter: Chapter,
        plan: DialogueTagCheckPlan,
    ) -> DialogueTagCheckRevision:
        """Revise dialogue tags in a chapter based on plan.

        Args:
            chapter: Chapter to revise
            plan: Revision plan

        Returns:
            Revision result
        """
        original_text = chapter.content if hasattr(chapter, 'content') else str(chapter)

        prompt = f"""请根据以下规范修改对话标签：

原文：
{original_text}

修改要求：
1. 统一引号风格为「」
2. 统一标签位置为「他说：'...'」格式
3. 使用标准标签动词（说、道、问、答等）
4. 保持动作标签（如「他笑着说」）
5. 直接输出修改后的文本，不要解释

修改后的文本："""

        revised_text = await self.ai_service.generate(prompt, temperature=0.3)

        return DialogueTagCheckRevision(
            original_text=original_text,
            revision_notes=[],
            revised_text=revised_text,
            quality_score=0.85,
        )

    def generate_check_report(
        self,
        analysis: DialogueTagCheckAnalysis,
        plan: Optional[DialogueTagCheckPlan] = None,
    ) -> DialogueTagCheckReport:
        """Generate a comprehensive check report.

        Args:
            analysis: Analysis results
            plan: Optional revision plan

        Returns:
            Check report
        """
        summary_parts = []

        summary_parts.append(f"对话标签检查报告")
        summary_parts.append(f"=" * 40)
        summary_parts.append(f"检查章节数: {analysis.total_chapters}")
        summary_parts.append(f"总对话数: {analysis.total_dialogues}")
        summary_parts.append(f"总对话行数: {analysis.total_dialogue_lines}")
        summary_parts.append("")

        summary_parts.append(f"整体评分: {analysis.overall_tag_score:.1%}")
        summary_parts.append(f"引号一致性: {analysis.overall_quote_consistency_score:.1%}")
        summary_parts.append(f"标签动词一致性: {analysis.overall_verb_consistency_score:.1%}")
        summary_parts.append(f"标签位置一致性: {analysis.overall_placement_consistency_score:.1%}")
        summary_parts.append("")

        if analysis.critical_count > 0:
            summary_parts.append(f"严重问题: {analysis.critical_count}")
        if analysis.major_count > 0:
            summary_parts.append(f"较大问题: {analysis.major_count}")
        if analysis.minor_count > 0:
            summary_parts.append(f"小问题: {analysis.minor_count}")

        summary_parts.append("")
        summary_parts.append(f"主要引号风格: {analysis.primary_quote_style.value}")
        summary_parts.append(f"最常用标签动词: {analysis.most_common_tag_verb or '无'}")

        if analysis.recommendations:
            summary_parts.append("")
            summary_parts.append("改进建议:")
            for rec in analysis.recommendations:
                summary_parts.append(f"  - {rec}")

        return DialogueTagCheckReport(
            analysis=analysis,
            revision_plan=plan,
            summary="\n".join(summary_parts),
            priority_fixes=[i for i in analysis.all_issues if i.severity in [DialogueTagSeverity.CRITICAL, DialogueTagSeverity.MAJOR]],
        )

    def get_tag_summary(self, analysis: DialogueTagCheckAnalysis) -> str:
        """Get a human-readable summary of dialogue tag analysis.

        Args:
            analysis: Analysis results

        Returns:
            Summary string
        """
        return self.generate_check_report(analysis).summary
