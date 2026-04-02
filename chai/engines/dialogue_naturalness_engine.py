"""Dialogue naturalness engine for validating character dialogue quality."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter, Character
from chai.models.dialogue_naturalness import (
    DialogueNaturalnessType,
    DialogueNaturalnessSeverity,
    CharacterDialogueProfile,
    DialogueLineCheck,
    DialogueExchangeCheck,
    ChapterDialogueProfile,
    DialogueNaturalnessIssue,
    DialogueNaturalnessAnalysis,
    DialogueNaturalnessRevision,
    DialogueNaturalnessReport,
)
from chai.services import AIService


# Patterns that indicate robotic/unnatural speech
UNNATURAL_PATTERNS = [
    r"^好的，我理解$",
    r"^我明白你的意思$",
    r"^根据我的分析",
    r"^从客观角度来看",
    r"^作为一个.*我认为",
    r"^首先，然后，最后",  # Formulaic structure
    r"^一方面，另一方",
    r"^总的来说",
]

# Patterns that indicate AI-generated speech
AI_GENERATED_PATTERNS = [
    r"^当然，我很乐意",
    r"^好的，让我们",
    r"^非常感谢你的",
    r"^我建议你可以",
    r"^如果你愿意的话",
    r"^我相信你一定",
]

# Formal speech indicators
FORMAL_INDICATORS = [
    "您", "贵", "令", "尊", "谨", "承蒙", "不胜", "感激",
]

# Informal/casual indicators
INFORMAL_INDICATORS = [
    "哈", "嘿", "哇", "哎", "啧", "嘁", "啥", "咋", "嘛", "呗",
]

# Education-related vocabulary
EDUCATED_VOCAB = [
    "因此", "然而", "虽然", "但是", "然而", "不过", "倘若",
    "既然", "所以", "因为", "虽然", "尽管", "然而",
]

# Fillers
FILLER_PATTERNS = [
    r"^这个嘛",
    r"^那个",
    r"^嗯",
    r"^啊",
    r"^呃",
    r"^就是",
    r"^然后",
    r"^所以说",
    r"^你知道",
    r"^我是说",
]


class DialogueNaturalnessEngine:
    """Engine for checking dialogue naturalness and character voice consistency."""

    def __init__(self, ai_service: AIService):
        """Initialize dialogue naturalness engine."""
        self.ai_service = ai_service

    def build_character_profile(
        self,
        character: Character,
    ) -> CharacterDialogueProfile:
        """Build a dialogue profile from a character.

        Args:
            character: Character model instance

        Returns:
            Character dialogue profile for checking
        """
        # Extract speech-related attributes
        speech_pattern = ""
        if hasattr(character, 'speech_pattern') and character.speech_pattern:
            speech_pattern = character.speech_pattern

        catchphrases = []
        if hasattr(character, 'catchphrases'):
            catchphrases = list(character.catchphrases)

        speech_quirks = []
        if hasattr(character, 'speech_characteristics'):
            speech_quirks = list(character.speech_characteristics)

        filler_words = []
        verbal_tics = []

        # Extract from speech pattern description if available
        if speech_pattern:
            # Look for filler-like phrases
            if "经常" in speech_pattern or "习惯" in speech_pattern:
                verbal_tics = ["...", "——"]  # Default tics

        # Determine vocabulary level from personality/background
        vocabulary_level = "moderate"
        formality_level = "neutral"

        if hasattr(character, 'personality_description'):
            desc = character.personality_description.lower()
            if any(word in desc for word in ["文雅", "书卷", "学者", "斯文"]):
                vocabulary_level = "sophisticated"
                formality_level = "formal"
            elif any(word in desc for word in ["粗犷", "豪爽", "直率", "粗俗"]):
                vocabulary_level = "simple"
                formality_level = "informal"

        # Build background context
        background = ""
        if hasattr(character, 'background'):
            if isinstance(character.background, str):
                background = character.background[:200]
            elif hasattr(character.background, 'origin'):
                background = str(character.background)[:200]

        return CharacterDialogueProfile(
            character_id=character.id,
            character_name=character.name,
            speech_pattern=speech_pattern,
            vocabulary_level=vocabulary_level,
            formality_level=formality_level,
            sentence_structure="mixed",
            catchphrases=catchphrases,
            filler_words=filler_words,
            verbal_tics=verbal_tics,
            speech_quirks=speech_quirks,
            emotional_restraint="moderate",
            emotional_triggers=[],
            directness="moderate",
            passive_aggressive=False,
            interruption_tendency="rare",
            background=background,
            education_level="moderate",
        )

    def _extract_dialogue_lines(
        self,
        text: str,
    ) -> list[tuple[str, str]]:
        """Extract dialogue lines from text.

        Args:
            text: Text containing dialogue

        Returns:
            List of (speaker, content) tuples
        """
        lines = []
        current_speaker = None

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check for dialogue markers
            # Pattern: "角色名：" or "角色名:" at start
            match = re.match(r'^([^：:]+)[：:]\s*(.+)', line)
            if match:
                current_speaker = match.group(1).strip()
                content = match.group(2).strip()
                if current_speaker and content:
                    lines.append((current_speaker, content))
                    continue

            # If no speaker marker but line looks like dialogue content
            if current_speaker and line and not line.startswith('#'):
                # Check if it looks like dialogue continuation
                if not line.startswith('。') and not line.startswith('，'):
                    lines.append((current_speaker, line))

        return lines

    def _check_line_naturalness(
        self,
        content: str,
        speaker_profile: Optional[CharacterDialogueProfile],
        context_situation: str = "",
    ) -> tuple[list[DialogueNaturalnessIssue], float, float]:
        """Check naturalness of a single dialogue line.

        Args:
            content: Dialogue line content
            speaker_profile: Character's dialogue profile
            context_situation: Context situation description

        Returns:
            Tuple of (issues, naturalness_score, character_consistency_score)
        """
        issues = []
        naturalness_score = 1.0
        character_score = 1.0

        if not content:
            return issues, naturalness_score, character_score

        # Check for robotic/unnatural patterns
        for pattern in UNNATURAL_PATTERNS:
            if re.search(pattern, content):
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.ROBOTIC_SPEECH,
                    severity=DialogueNaturalnessSeverity.SEVERE,
                    description=f"对话听起来公式化、不自然：{pattern}",
                    current_content=content,
                    suggestion="使用更自然、口语化的表达方式",
                ))
                naturalness_score -= 0.2

        # Check for AI-generated patterns
        for pattern in AI_GENERATED_PATTERNS:
            if re.search(pattern, content):
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.ROBOTIC_SPEECH,
                    severity=DialogueNaturalnessSeverity.MODERATE,
                    description=f"对话听起来像AI生成的",
                    current_content=content,
                    suggestion="改用更有个性的表达",
                ))
                naturalness_score -= 0.15

        # Check formality consistency
        if speaker_profile:
            formal_count = sum(1 for ind in FORMAL_INDICATORS if ind in content)
            informal_count = sum(1 for ind in INFORMAL_INDICATORS if ind in content)

            expected_formality = speaker_profile.formality_level
            if expected_formality == "formal" and informal_count > formal_count:
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.FORMALITY_INCONSISTENT,
                    severity=DialogueNaturalnessSeverity.MODERATE,
                    description="角色平时说话正式，但这句话过于随意",
                    current_content=content,
                    suggestion="使用更正式的用语",
                ))
                character_score -= 0.2
            elif expected_formality == "informal" and formal_count > informal_count:
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.FORMALITY_INCONSISTENT,
                    severity=DialogueNaturalnessSeverity.MODERATE,
                    description="角色平时说话随意，但这句话过于正式",
                    current_content=content,
                    suggestion="使用更口语化的表达",
                ))
                character_score -= 0.2

            # Check for catchphrase presence if expected
            if speaker_profile.catchphrases:
                has_catchphrase = any(cp in content for cp in speaker_profile.catchphrases)
                if not has_catchphrase and len(content) > 20:
                    # Only flag if context suggests this might be a key line
                    pass  # Don't penalize absence of catchphrase, it's optional

        # Check for unnatural length
        if len(content) < 3:
            issues.append(DialogueNaturalnessIssue(
                issue_type=DialogueNaturalnessType.UNNATURAL_PHRASING,
                severity=DialogueNaturalnessSeverity.MINOR,
                description="对话行过短",
                current_content=content,
                suggestion="增加对话内容",
            ))
            naturalness_score -= 0.1

        # Check for very long lines without punctuation (run-on)
        if len(content) > 100 and content.count('。') + content.count('！') + content.count('？') == 0:
            issues.append(DialogueNaturalnessIssue(
                issue_type=DialogueNaturalnessType.UNNATURAL_PHRASING,
                severity=DialogueNaturalnessSeverity.MODERATE,
                description="对话行过长且没有标点",
                current_content=content[:50] + "...",
                suggestion="拆分长句，添加适当标点",
            ))
            naturalness_score -= 0.15

        # Check for unnatural phrasing patterns
        unnatural_phrases = [
            ("非常感谢你的", "听起来像客套话，不够自然"),
            ("我建议你", "建议口吻过于正式"),
            ("我认为", "思考过程不需要说出来"),
        ]
        for phrase, reason in unnatural_phrases:
            if phrase in content:
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.UNNATURAL_PHRASING,
                    severity=DialogueNaturalnessSeverity.MINOR,
                    description=reason,
                    current_content=content,
                    suggestion=f"避免使用'{phrase}'这种开头",
                ))
                naturalness_score -= 0.1

        # Clamp scores
        naturalness_score = max(0.0, min(1.0, naturalness_score))
        character_score = max(0.0, min(1.0, character_score))

        return issues, naturalness_score, character_score

    def _check_conversation_flow(
        self,
        lines: list[tuple[str, str]],
    ) -> tuple[float, list[DialogueNaturalnessIssue]]:
        """Check if conversation flows naturally between speakers.

        Args:
            lines: List of (speaker, content) tuples

        Returns:
            Tuple of (flow_score, issues)
        """
        issues = []
        flow_score = 1.0

        if len(lines) < 2:
            return flow_score, issues

        # Check for response mismatch (speaker doesn't respond to previous topic)
        for i in range(1, len(lines)):
            prev_speaker, prev_content = lines[i - 1]
            curr_speaker, curr_content = lines[i]

            # Skip if same speaker continues
            if curr_speaker == prev_speaker:
                continue

            # Check for very short responses after a question
            question_markers = ["？", "吗", "怎么", "为什么", "什么", "是不是"]
            has_question = any(q in prev_content for q in question_markers)

            if has_question and len(curr_content) < 5:
                issues.append(DialogueNaturalnessIssue(
                    issue_type=DialogueNaturalnessType.RESPONSE_MISMATCH,
                    severity=DialogueNaturalnessSeverity.MODERATE,
                    exchange_index=0,
                    line_index=i,
                    speaker_name=curr_speaker,
                    description="问题后回应过短，未充分回答",
                    current_content=curr_content,
                    suggestion="对问题作出更充分的回应",
                ))
                flow_score -= 0.1

        # Check for conversation pacing (too many rapid exchanges)
        if len(lines) > 6:
            # Group consecutive exchanges
            exchange_count = 0
            prev_speaker = None
            for speaker, _ in lines:
                if speaker != prev_speaker:
                    exchange_count += 1
                    prev_speaker = speaker

            # If exchanges are very short, might be pacing issue
            if exchange_count > len(lines) * 0.8:
                # Almost every line is a speaker change - very rapid fire
                pass  # Could be appropriate for tense scenes, so just note it

        return max(0.0, min(1.0, flow_score)), issues

    def analyze_chapter_dialogue(
        self,
        chapter: Chapter,
        characters: list[Character],
        situation: str = "",
    ) -> DialogueNaturalnessAnalysis:
        """Analyze dialogue naturalness in a chapter.

        Args:
            chapter: Chapter to analyze
            characters: Character list for profile lookup
            situation: Context situation description

        Returns:
            Dialogue naturalness analysis for the chapter
        """
        analysis_id = f"analysis_{chapter.id}_{uuid.uuid4().hex[:8]}"

        # Build character profiles
        char_profiles: dict[str, CharacterDialogueProfile] = {}
        for char in characters:
            char_profiles[char.name] = self.build_character_profile(char)

        # Extract dialogue from chapter content
        content = ""
        if hasattr(chapter, 'content') and chapter.content:
            content = chapter.content
        elif hasattr(chapter, 'body') and chapter.body:
            content = chapter.body

        dialogue_lines = self._extract_dialogue_lines(content)

        if not dialogue_lines:
            return DialogueNaturalnessAnalysis(
                analysis_id=analysis_id,
                chapter_profile=ChapterDialogueProfile(
                    chapter_id=chapter.id,
                    chapter_title=getattr(chapter, 'title', ''),
                ),
                overall_score=1.0,
            )

        # Analyze each line
        all_issues = []
        line_checks = []
        character_counts: dict[str, int] = {}
        character_issue_counts: dict[str, int] = {}

        for idx, (speaker, line_content) in enumerate(dialogue_lines):
            # Count lines per character
            character_counts[speaker] = character_counts.get(speaker, 0) + 1

            # Get speaker profile
            speaker_profile = char_profiles.get(speaker)

            # Check line
            line_issues, nat_score, char_score = self._check_line_naturalness(
                line_content,
                speaker_profile,
                situation,
            )

            # Determine severity
            severity = DialogueNaturalnessSeverity.MINOR
            if any(i.severity == DialogueNaturalnessSeverity.SEVERE for i in line_issues):
                severity = DialogueNaturalnessSeverity.SEVERE
            elif any(i.severity == DialogueNaturalnessSeverity.MODERATE for i in line_issues):
                severity = DialogueNaturalnessSeverity.MODERATE

            # Count issues per character
            if line_issues:
                character_issue_counts[speaker] = character_issue_counts.get(speaker, 0) + len(line_issues)
                for issue in line_issues:
                    issue.line_index = idx
                    issue.exchange_index = 0
                    issue.speaker_name = speaker
                    issue.chapter_id = chapter.id
                    all_issues.append(issue)

            line_checks.append(DialogueLineCheck(
                line_index=idx,
                speaker_name=speaker,
                content=line_content,
                issues=[i.description for i in line_issues],
                issue_types=[i.issue_type for i in line_issues],
                severity=severity,
                naturalness_score=nat_score,
                character_consistency_score=char_score,
                context_fit_score=1.0,
                suggestions=[i.suggestion for i in line_issues],
            ))

        # Check conversation flow
        flow_score, flow_issues = self._check_conversation_flow(dialogue_lines)
        for issue in flow_issues:
            issue.chapter_id = chapter.id
            all_issues.append(issue)

        # Build exchange check (simplified - one exchange for whole chapter)
        exchange_check = DialogueExchangeCheck(
            exchange_index=0,
            participants=list(set(s[0] for s in dialogue_lines)),
            line_checks=line_checks,
            conversation_flow_score=flow_score,
            response_continuity_score=flow_score,
            pacing_score=flow_score,
            power_dynamic_score=1.0,
            total_issues=len(all_issues),
            severe_issues=sum(1 for i in all_issues if i.severity == DialogueNaturalnessSeverity.SEVERE),
            overall_score=sum(lc.naturalness_score for lc in line_checks) / max(1, len(line_checks)),
        )

        # Build chapter profile
        chapter_profile = ChapterDialogueProfile(
            chapter_id=chapter.id,
            chapter_title=getattr(chapter, 'title', ''),
            total_dialogue_lines=len(dialogue_lines),
            total_exchanges=1,
            speaking_characters=list(set(s[0] for s in dialogue_lines)),
            dialogue_ratio=len(dialogue_lines) / max(1, len(content.split('\n'))),
            exchange_checks=[exchange_check],
            character_dialogue_counts=character_counts,
            character_issue_counts=character_issue_counts,
            overall_naturalness_score=exchange_check.overall_score,
            overall_character_consistency_score=sum(lc.character_consistency_score for lc in line_checks) / max(1, len(line_checks)),
        )

        # Build issue summary
        issue_summary: dict[str, int] = {}
        for issue in all_issues:
            key = issue.issue_type.value
            issue_summary[key] = issue_summary.get(key, 0) + 1

        # Group issues by character
        character_issues: dict[str, list[DialogueNaturalnessIssue]] = {}
        for issue in all_issues:
            if issue.speaker_name:
                if issue.speaker_name not in character_issues:
                    character_issues[issue.speaker_name] = []
                character_issues[issue.speaker_name].append(issue)

        # Calculate overall scores
        overall_naturalness = sum(lc.naturalness_score for lc in line_checks) / max(1, len(line_checks))
        overall_character = sum(lc.character_consistency_score for lc in line_checks) / max(1, len(line_checks))

        return DialogueNaturalnessAnalysis(
            analysis_id=analysis_id,
            chapter_profile=chapter_profile,
            issues=all_issues,
            issue_summary=issue_summary,
            character_issues=character_issues,
            naturalness_score=overall_naturalness,
            character_voice_score=overall_character,
            context_fit_score=1.0,
            conversation_flow_score=flow_score,
            overall_score=(overall_naturalness + overall_character + flow_score) / 3,
            total_lines=len(dialogue_lines),
            total_issues=len(all_issues),
            severe_issues=sum(1 for i in all_issues if i.severity == DialogueNaturalnessSeverity.SEVERE),
        )

    def analyze_novel_dialogue(
        self,
        novel: Novel,
        characters: list[Character],
        situation: str = "",
    ) -> DialogueNaturalnessReport:
        """Analyze dialogue naturalness across a novel.

        Args:
            novel: Novel to analyze
            characters: Character list for profile lookup
            situation: Overall situation description

        Returns:
            Comprehensive dialogue naturalness report
        """
        report_id = f"report_{uuid.uuid4().hex[:8]}"

        chapters = []
        if isinstance(novel.chapters, dict):
            chapters = list(novel.chapters.values())
        else:
            chapters = novel.chapters

        analyses = []
        total_lines = 0
        total_exchanges = 0
        total_issues = 0
        severe_issues = 0
        moderate_issues = 0
        minor_issues = 0
        issues_by_type: dict[str, int] = {}
        character_total_issues: dict[str, int] = {}
        character_total_lines: dict[str, int] = {}

        for chapter in chapters:
            analysis = self.analyze_chapter_dialogue(chapter, characters, situation)
            analyses.append(analysis)

            total_lines += analysis.total_lines
            total_issues += analysis.total_issues
            severe_issues += analysis.severe_issues
            total_exchanges += analysis.chapter_profile.total_exchanges

            for issue in analysis.issues:
                if issue.severity == DialogueNaturalnessSeverity.MODERATE:
                    moderate_issues += 1
                elif issue.severity == DialogueNaturalnessSeverity.MINOR:
                    minor_issues += 1

                key = issue.issue_type.value
                issues_by_type[key] = issues_by_type.get(key, 0) + 1

                if issue.speaker_name:
                    character_total_issues[issue.speaker_name] = character_total_issues.get(issue.speaker_name, 0) + 1

            for char_name, count in analysis.chapter_profile.character_dialogue_counts.items():
                character_total_lines[char_name] = character_total_lines.get(char_name, 0) + count

        # Determine best and worst characters
        most_issues_char = None
        best_voice_char = None

        if character_total_issues:
            most_issues_char = max(character_total_issues.items(), key=lambda x: x[1])[0]

        # Best voice = most lines with fewest issues
        if character_total_lines:
            best_ratio = 0
            for char, lines in character_total_lines.items():
                issues = character_total_issues.get(char, 0)
                ratio = lines / max(1, issues + 1)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_voice_char = char

        # Calculate overall scores
        overall_naturalness = sum(a.naturalness_score for a in analyses) / max(1, len(analyses))
        overall_character = sum(a.character_voice_score for a in analyses) / max(1, len(analyses))

        # Generate recommendations
        recommendations = []
        if severe_issues > 0:
            recommendations.append(f"重点关注 {severe_issues} 个严重问题，优先修复")
        if issues_by_type.get(DialogueNaturalnessType.ROBOTIC_SPEECH.value, 0) > 3:
            recommendations.append("对话整体偏公式化，建议增加更多口语化和个性化的表达")
        if issues_by_type.get(DialogueNaturalnessType.FORMALITY_INCONSISTENT.value, 0) > 2:
            recommendations.append("部分角色语言风格不一致，需要对照角色设定调整")
        if issues_by_type.get(DialogueNaturalnessType.CONVERSATION_FLOW_POOR.value, 0) > 2:
            recommendations.append("部分对话的衔接不够流畅，注意回应要承接上文")

        # Chapter summaries
        chapter_summaries = {}
        for analysis in analyses:
            if analysis.total_issues == 0:
                summary = "对话自然流畅，符合角色设定"
            elif analysis.severe_issues > 0:
                summary = f"存在 {analysis.severe_issues} 个严重问题需要修复"
            else:
                summary = f"存在 {analysis.total_issues} 个问题，建议优化"
            chapter_summaries[analysis.chapter_profile.chapter_id] = summary

        return DialogueNaturalnessReport(
            report_id=report_id,
            analyses=analyses,
            total_chapters_analyzed=len(analyses),
            total_dialogue_lines=total_lines,
            total_exchanges=total_exchanges,
            total_issues=total_issues,
            severe_issues=severe_issues,
            moderate_issues=moderate_issues,
            minor_issues=minor_issues,
            issues_by_type=issues_by_type,
            most_issues_character=most_issues_char,
            best_voice_character=best_voice_char,
            overall_naturalness_score=overall_naturalness,
            overall_character_consistency_score=overall_character,
            key_recommendations=recommendations,
            chapter_summaries=chapter_summaries,
        )

    def create_revision_plan(
        self,
        analysis: DialogueNaturalnessAnalysis,
    ) -> DialogueNaturalnessRevision:
        """Create a revision plan based on analysis.

        Args:
            analysis: Dialogue naturalness analysis

        Returns:
            Revision plan with prioritized fixes
        """
        priority_fixes = []
        suggested_fixes = []
        optional_improvements = []

        for issue in analysis.issues:
            if issue.severity == DialogueNaturalnessSeverity.SEVERE:
                priority_fixes.append(issue)
            elif issue.severity == DialogueNaturalnessSeverity.MODERATE:
                suggested_fixes.append(issue)
            else:
                optional_improvements.append(issue)

        # Sort by severity within each category
        priority_fixes.sort(key=lambda x: (x.exchange_index, x.line_index))
        suggested_fixes.sort(key=lambda x: (x.exchange_index, x.line_index))

        # Generate character guidance
        character_guidance: dict[str, list[str]] = {}
        for issue in analysis.issues:
            char = issue.speaker_name
            if char:
                if char not in character_guidance:
                    character_guidance[char] = []
                if issue.suggestion not in character_guidance[char]:
                    character_guidance[char].append(issue.suggestion)

        # Determine focus areas
        revision_focus = []
        if analysis.issue_summary.get(DialogueNaturalnessType.ROBOTIC_SPEECH.value, 0) > 0:
            revision_focus.append("改进对话的自然度，避免公式化表达")
        if analysis.issue_summary.get(DialogueNaturalnessType.CHARACTER_VOICE_BREAK.value, 0) > 0:
            revision_focus.append("保持角色语言风格的一致性")
        if analysis.issue_summary.get(DialogueNaturalnessType.FORMALITY_INCONSISTENT.value, 0) > 0:
            revision_focus.append("调整语言的正式程度以匹配角色")
        if analysis.issue_summary.get(DialogueNaturalnessType.CONVERSATION_FLOW_POOR.value, 0) > 0:
            revision_focus.append("改善对话的衔接和流程")

        return DialogueNaturalnessRevision(
            analysis_id=analysis.analysis_id,
            priority_fixes=priority_fixes,
            suggested_fixes=suggested_fixes,
            optional_improvements=optional_improvements,
            character_guidance=character_guidance,
            revision_focus=revision_focus,
        )

    def get_summary(
        self,
        report: DialogueNaturalnessReport,
    ) -> str:
        """Get a human-readable summary of the report.

        Args:
            report: Dialogue naturalness report

        Returns:
            Summary string
        """
        lines = [
            "=== 对话自然度检查报告 ===",
            f"检查章节数: {report.total_chapters_analyzed}",
            f"对话行数: {report.total_dialogue_lines}",
            f"对话轮次: {report.total_exchanges}",
            "",
            f"总体自然度评分: {report.overall_naturalness_score:.2f}/1.00",
            f"角色一致性评分: {report.overall_character_consistency_score:.2f}/1.00",
            "",
            f"发现问题: {report.total_issues} 个",
            f"  - 严重: {report.severe_issues}",
            f"  - 中等: {report.moderate_issues}",
            f"  - 轻微: {report.minor_issues}",
        ]

        if report.issues_by_type:
            lines.append("")
            lines.append("问题类型分布:")
            for issue_type, count in sorted(report.issues_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  - {issue_type}: {count}")

        if report.most_issues_character:
            lines.append(f"\n问题最多的角色: {report.most_issues_character}")

        if report.best_voice_character:
            lines.append(f"语言最自然的角色: {report.best_voice_character}")

        if report.key_recommendations:
            lines.append("")
            lines.append("重点建议:")
            for rec in report.key_recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)
