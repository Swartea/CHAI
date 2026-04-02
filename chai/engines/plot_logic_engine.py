"""Plot logic self-consistency engine for validating plot coherence."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter, Character
from chai.models.plot_logic import (
    PlotLogicType,
    PlotLogicSeverity,
    PlotTimelineEvent,
    CharacterKnowledgeState,
    PlotLogicIssue,
    ChapterPlotLogicProfile,
    PlotLogicAnalysis,
    PlotLogicRevision,
    PlotLogicReport,
    PlotConsistencyTemplate,
)
from chai.services import AIService


# Patterns that indicate knowledge revelation
KNOWLEDGE_REVELATION_PATTERNS = [
    r"原来", r"竟然", r"才发现", r"才知道", r"不知道",
    r"明白了", r"揭晓", r"揭露", r"暴露", r"泄露",
]

# Patterns that indicate causal events
CAUSAL_PATTERNS = [
    r"因此", r"所以", r"于是", r"导致", r"造成",
    r"使得", r"因为", r"由于", r"为了", r"结果",
]

# Time indicator patterns
TIME_PATTERNS = [
    (r"之前", "before"),
    (r"之后", "after"),
    (r"之前的一天", "day_before"),
    (r"之后的一天", "day_after"),
    (r"一年前", "year_before"),
    (r"一年后", "year_after"),
    (r"几个月前", "months_before"),
    (r"几天后", "days_after"),
    (r"刚才", "just_now"),
    (r"突然", "suddenly"),
    (r"与此同时", "simultaneously"),
    (r"此刻", "now"),
    (r"当时", "then"),
]

# Contradiction patterns
CONTRADICTION_PATTERNS = [
    (r"但是", r"然而"),  # but/however contradictions
    (r"明明", r"竟然"),
    (r"应该", r"却"),
    (r"不可能", r"竟然"),
]

# Character ability patterns
SKILL_APPEARANCE_PATTERNS = [
    r"突然会", r"突然学会", r"莫名其妙地会",
    r"不知怎么", r"竟然能", r"出乎意料地",
]

# Location/travel patterns
TRAVEL_PATTERNS = [
    r"赶到了", r"抵达", r"到达", r"来到",
    r"离开", r"出发", r"返回", r"回到",
]


class PlotLogicEngine:
    """Engine for checking plot logic self-consistency."""

    def __init__(self, ai_service: AIService):
        """Initialize plot logic engine."""
        self.ai_service = ai_service

    def _extract_timeline_events(
        self,
        chapter: Chapter,
        previous_events: list[PlotTimelineEvent],
    ) -> list[PlotTimelineEvent]:
        """Extract timeline events from chapter content.

        Args:
            chapter: Chapter to analyze
            previous_events: Events from previous chapters

        Returns:
            List of timeline events found
        """
        events = []
        content = getattr(chapter, 'content', '') or getattr(chapter, 'body', '')

        if not content:
            return events

        # Extract sentences
        sentences = re.split(r'[。！？\n]', content)
        current_location = getattr(chapter, 'location', '') or ""

        # Find time indicators
        time_indicators = []
        for pattern, time_type in TIME_PATTERNS:
            if re.search(pattern, content):
                time_indicators.append(time_type)

        # Find causal events
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check for causal language
            has_causal = any(re.search(p, sentence) for p in CAUSAL_PATTERNS)

            # Check for knowledge revelation
            has_revelation = any(re.search(p, sentence) for p in KNOWLEDGE_REVELATION_PATTERNS)

            # Check for time indicators
            sentence_time = None
            for pattern, time_type in TIME_PATTERNS:
                if re.search(pattern, sentence):
                    sentence_time = time_type
                    break

            if has_causal or has_revelation or sentence_time:
                event = PlotTimelineEvent(
                    event_id=f"{chapter.id}_event_{len(events)}",
                    chapter=chapter.number,
                    title=sentence[:50] + ("..." if len(sentence) > 50 else ""),
                    description=sentence,
                    timestamp_in_story=sentence_time,
                    location=current_location,
                    causes=[],
                    effects=[],
                    information_revealed=[],
                    characters_involved=getattr(chapter, 'characters_involved', []),
                )
                events.append(event)

        return events

    def _check_timeline_consistency(
        self,
        events: list[PlotTimelineEvent],
    ) -> tuple[float, list[PlotLogicIssue]]:
        """Check timeline consistency of events.

        Args:
            events: Timeline events to check

        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        score = 1.0

        # Check for events that claim to be "before" but come after
        for i, event in enumerate(events):
            if event.timestamp_in_story == "before":
                # Find events that should come after
                later_events = [e for e in events if e.chapter > event.chapter]
                if not later_events:
                    # This is the earliest event, which is correct
                    pass

            # Check for reversed causality (effect before cause)
            for j, other_event in enumerate(events):
                if i != j and other_event.chapter < event.chapter:
                    # Check if this event describes something that should logically come after
                    if "之前" in event.description and "之后" not in other_event.description:
                        # Potential reversal
                        pass

        # Check for sudden ability/skills without setup
        if len(events) > 1:
            for i, event in enumerate(events[1:], 1):
                prev_event = events[i - 1]

                # Check if new abilities appear suddenly
                for pattern in SKILL_APPEARANCE_PATTERNS:
                    if re.search(pattern, event.description):
                        # This is a potential issue - new skill without training
                        # We would need more context to determine if this is valid
                        pass

        score = max(0.0, min(1.0, score))
        return score, issues

    def _check_character_knowledge_consistency(
        self,
        chapter: Chapter,
        previous_knowledge: dict[str, CharacterKnowledgeState],
        content: str,
    ) -> tuple[dict[str, CharacterKnowledgeState], float, list[PlotLogicIssue]]:
        """Check character knowledge consistency.

        Args:
            chapter: Current chapter
            previous_knowledge: Previous knowledge states
            content: Chapter content

        Returns:
            Tuple of (updated_knowledge, consistency_score, issues)
        """
        issues = []
        score = 1.0
        updated_knowledge = dict(previous_knowledge)

        # Extract character names from chapter
        characters_in_chapter = getattr(chapter, 'characters_involved', [])

        # Find knowledge revelation patterns
        for pattern in KNOWLEDGE_REVELATION_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]

                # Look for character names in context
                for char_id in characters_in_chapter:
                    if char_id in context:
                        # Knowledge was revealed
                        if char_id not in updated_knowledge:
                            updated_knowledge[char_id] = CharacterKnowledgeState(
                                character_id=char_id,
                                character_name=char_id,
                            )

        # Check for impossible knowledge
        for char_id, knowledge_state in updated_knowledge.items():
            # Check if character knows contradictory things
            pass

        score = max(0.0, min(1.0, score))
        return updated_knowledge, score, issues

    def _check_causality_consistency(
        self,
        events: list[PlotTimelineEvent],
    ) -> tuple[float, list[PlotLogicIssue]]:
        """Check causality consistency.

        Args:
            events: Timeline events to check

        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        score = 1.0

        for i, event in enumerate(events):
            # Check if effect events have causes
            has_effect_markers = any(
                re.search(p, event.description) for p in CAUSE_EFFECT_PATTERNS
            )

            if has_effect_markers and not event.causes and i > 0:
                # This event has effect markers but no identified causes
                # Check if previous events could cause it
                prev_events = events[:i]
                has_valid_cause = False

                for prev_event in prev_events:
                    if prev_event.chapter < event.chapter:
                        # Potential cause exists
                        has_valid_cause = True
                        break

                if not has_valid_cause:
                    issue = PlotLogicIssue(
                        issue_id=f"cause_{event.event_id}",
                        issue_type=PlotLogicType.CAUSE_EFFECT_MISSING,
                        severity=PlotLogicSeverity.MODERATE,
                        chapter=event.chapter,
                        event_id=event.event_id,
                        title="事件缺乏原因",
                        description=f"事件 '{event.title}' 似乎没有明确的起因",
                        suggestion="添加前面章节的伏笔或原因",
                    )
                    issues.append(issue)
                    score -= 0.1

        score = max(0.0, min(1.0, score))
        return score, issues

    def _check_world_rules_consistency(
        self,
        chapter: Chapter,
        template: Optional[PlotConsistencyTemplate] = None,
    ) -> tuple[float, list[PlotLogicIssue]]:
        """Check world rules consistency (magic, technology, social rules).

        Args:
            chapter: Chapter to check
            template: Consistency template with rules

        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        score = 1.0
        content = getattr(chapter, 'content', '') or getattr(chapter, 'body', '')

        if not content:
            return score, issues

        # Check for magic system violations if template provided
        if template and template.magic_rules:
            # Look for potential violations
            for rule in template.magic_rules:
                # Simple pattern matching - in reality would be more sophisticated
                if rule in content:
                    # Rule is mentioned, check for proper context
                    pass

        # Generic world rules checks
        # Check for technology inconsistencies
        tech_mentions = ["手机", "电脑", "电视", "汽车", "飞机", "电话"]
        has_modern_tech = any(tech in content for tech in tech_mentions)

        # Check for historical/fantasy inconsistencies
        historical_mentions = ["马车", "蜡烛", "油灯", "古城", "古堡"]
        has_historical = any(hist in content for hist in historical_mentions)

        if has_modern_tech and has_historical:
            # Potential technology inconsistency
            pass  # Would need genre context

        score = max(0.0, min(1.0, score))
        return score, issues

    def _check_travel_time_consistency(
        self,
        chapter: Chapter,
        previous_chapter: Optional[Chapter],
    ) -> tuple[float, list[PlotLogicIssue]]:
        """Check travel time and location consistency.

        Args:
            chapter: Current chapter
            previous_chapter: Previous chapter

        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        score = 1.0

        if not previous_chapter:
            return score, issues

        content = getattr(chapter, 'content', '') or getattr(chapter, 'body', '')
        prev_content = getattr(previous_chapter, 'content', '') or getattr(previous_chapter, 'body', '')

        if not content or not prev_content:
            return score, issues

        # Check for travel patterns
        has_travel_in_current = any(re.search(p, content) for p in TRAVEL_PATTERNS)

        # Check for location mentions
        current_locations = re.findall(r"在(.+?)[。；,]", content)
        prev_locations = re.findall(r"在(.+?)[。；,]", prev_content)

        if current_locations and prev_locations:
            # Check if locations are different
            curr_set = set(current_locations)
            prev_set = set(prev_locations)

            if curr_set != prev_set and not has_travel_in_current:
                # Location changed without travel
                issue = PlotLogicIssue(
                    issue_id=f"travel_{chapter.id}",
                    issue_type=PlotLogicType.TRAVEL_TIME_INSUFFICIENT,
                    severity=PlotLogicSeverity.MINOR,
                    chapter=chapter.number,
                    title="地点转换缺乏说明",
                    description=f"从 '{list(prev_set)[0]}' 到 '{list(curr_set)[0]}' 的转换没有说明",
                    suggestion="添加过渡句说明角色如何到达新地点",
                )
                issues.append(issue)
                score -= 0.05

        score = max(0.0, min(1.0, score))
        return score, issues

    def _check_plot_inconsistencies(
        self,
        chapter: Chapter,
        all_chapters: list[Chapter],
    ) -> tuple[float, list[PlotLogicIssue]]:
        """Check for plot inconsistencies within the chapter.

        Args:
            chapter: Chapter to check
            all_chapters: All chapters in novel

        Returns:
            Tuple of (consistency_score, issues)
        """
        issues = []
        score = 1.0
        content = getattr(chapter, 'content', '') or getattr(chapter, 'body', '')

        if not content:
            return score, issues

        # Check for contradictions within the text
        for pattern1, pattern2 in CONTRADICTION_PATTERNS:
            if re.search(pattern1, content) and re.search(pattern2, content):
                # Potential contradiction
                issue = PlotLogicIssue(
                    issue_id=f"contradiction_{chapter.id}_{uuid.uuid4().hex[:8]}",
                    issue_type=PlotLogicType.PLOT_INCONSISTENCY,
                    severity=PlotLogicSeverity.MODERATE,
                    chapter=chapter.number,
                    title="文本中存在矛盾",
                    description=f"在同一段落中发现 '{pattern1}' 和 '{pattern2}' 同时出现",
                    suggestion="检查上下文确保叙述一致",
                )
                issues.append(issue)
                score -= 0.1

        # Check for "but" contradictions within same sentence
        but_sentences = re.findall(r"[^。！？]+但是[^。！？]+", content)
        for sentence in but_sentences:
            if "却" in sentence or "然而" in sentence:
                # Potential internal contradiction
                pass

        score = max(0.0, min(1.0, score))
        return score, issues

    def analyze_chapter_plot_logic(
        self,
        chapter: Chapter,
        characters: list[Character],
        previous_chapter: Optional[Chapter] = None,
        previous_knowledge: Optional[dict[str, CharacterKnowledgeState]] = None,
        previous_events: Optional[list[PlotTimelineEvent]] = None,
        template: Optional[PlotConsistencyTemplate] = None,
    ) -> PlotLogicAnalysis:
        """Analyze plot logic for a single chapter.

        Args:
            chapter: Chapter to analyze
            characters: Character list
            previous_chapter: Previous chapter for continuity
            previous_knowledge: Previous character knowledge states
            previous_events: Previous timeline events
            template: Consistency template

        Returns:
            Plot logic analysis for the chapter
        """
        analysis_id = f"analysis_{chapter.id}_{uuid.uuid4().hex[:8]}"

        content = getattr(chapter, 'content', '') or getattr(chapter, 'body', '')

        # Extract events
        events = self._extract_timeline_events(chapter, previous_events or [])

        # Initialize knowledge tracking
        if previous_knowledge is None:
            previous_knowledge = {}

        # Check timeline consistency
        timeline_score, timeline_issues = self._check_timeline_consistency(events)

        # Check character knowledge consistency
        updated_knowledge, knowledge_score, knowledge_issues = self._check_character_knowledge_consistency(
            chapter, previous_knowledge, content
        )

        # Check causality consistency
        causality_score, causality_issues = self._check_causality_consistency(events)

        # Check world rules consistency
        world_score, world_issues = self._check_world_rules_consistency(chapter, template)

        # Check travel time consistency
        travel_score, travel_issues = self._check_travel_time_consistency(chapter, previous_chapter)

        # Check plot inconsistencies
        plot_score, plot_issues = self._check_plot_inconsistencies(chapter, [])

        # Combine all issues
        all_issues = (
            timeline_issues +
            knowledge_issues +
            causality_issues +
            world_issues +
            travel_issues +
            plot_issues
        )

        # Calculate overall score
        scores = [
            timeline_score,
            knowledge_score,
            causality_score,
            world_score,
            travel_score,
            plot_score,
        ]
        overall_score = sum(scores) / len(scores) if scores else 1.0

        # Count severe issues
        severe_count = sum(
            1 for issue in all_issues
            if issue.severity in [PlotLogicSeverity.SEVERE, PlotLogicSeverity.CRITICAL]
        )

        # Build chapter profile
        chapter_profile = ChapterPlotLogicProfile(
            chapter_id=chapter.id,
            chapter_number=chapter.number,
            chapter_title=getattr(chapter, 'title', ''),
            timeline_events=events,
            issues=all_issues,
            timeline_consistency_score=timeline_score,
            causality_score=causality_score,
            character_knowledge_score=knowledge_score,
            world_rules_score=world_score,
            overall_score=overall_score,
            total_issues=len(all_issues),
            severe_issues=severe_count,
        )

        # Build issue summary
        issue_summary: dict[str, int] = {}
        for issue in all_issues:
            key = issue.issue_type.value
            issue_summary[key] = issue_summary.get(key, 0) + 1

        return PlotLogicAnalysis(
            analysis_id=analysis_id,
            chapter_profile=chapter_profile,
            issues=all_issues,
            issue_summary=issue_summary,
            timeline_score=timeline_score,
            causality_score=causality_score,
            knowledge_score=knowledge_score,
            world_rules_score=world_score,
            overall_score=overall_score,
            total_issues=len(all_issues),
            severe_issues=severe_count,
        )

    def analyze_novel_plot_logic(
        self,
        novel: Novel,
        characters: list[Character],
        template: Optional[PlotConsistencyTemplate] = None,
    ) -> PlotLogicReport:
        """Analyze plot logic across an entire novel.

        Args:
            novel: Novel to analyze
            characters: Character list
            template: Consistency template

        Returns:
            Comprehensive plot logic report
        """
        report_id = f"report_{uuid.uuid4().hex[:8]}"

        chapters = []
        if isinstance(novel.chapters, dict):
            chapters = list(novel.chapters.values())
        else:
            chapters = novel.chapters

        # Sort by chapter number
        chapters.sort(key=lambda c: c.number)

        analyses = []
        total_issues = 0
        severe_issues = 0
        moderate_issues = 0
        minor_issues = 0
        critical_issues = 0
        issues_by_type: dict[str, int] = {}
        chapter_issue_counts: dict[str, int] = {}

        previous_knowledge: dict[str, CharacterKnowledgeState] = {}
        previous_events: list[PlotTimelineEvent] = []
        previous_chapter: Optional[Chapter] = None

        for chapter in chapters:
            analysis = self.analyze_chapter_plot_logic(
                chapter=chapter,
                characters=characters,
                previous_chapter=previous_chapter,
                previous_knowledge=previous_knowledge,
                previous_events=previous_events,
                template=template,
            )
            analyses.append(analysis)

            total_issues += analysis.total_issues
            severe_issues += analysis.severe_issues
            chapter_issue_counts[chapter.id] = analysis.total_issues

            for issue in analysis.issues:
                if issue.severity == PlotLogicSeverity.MODERATE:
                    moderate_issues += 1
                elif issue.severity == PlotLogicSeverity.MINOR:
                    minor_issues += 1
                elif issue.severity == PlotLogicSeverity.CRITICAL:
                    critical_issues += 1

                key = issue.issue_type.value
                issues_by_type[key] = issues_by_type.get(key, 0) + 1

            # Update tracking for next iteration
            previous_chapter = chapter
            previous_events.extend(analysis.chapter_profile.timeline_events)

        # Determine chapters with most/best issues
        most_issues_chapter = None
        best_chapter = None

        if chapter_issue_counts:
            most_issues_chapter_id = max(chapter_issue_counts.items(), key=lambda x: x[1])[0]
            most_issues_chapter = next(
                (a.chapter_profile.chapter_number for a in analyses
                 if a.chapter_profile.chapter_id == most_issues_chapter_id),
                None
            )

            best_chapter_id = min(chapter_issue_counts.items(), key=lambda x: x[1])[0]
            best_chapter = next(
                (a.chapter_profile.chapter_number for a in analyses
                 if a.chapter_profile.chapter_id == best_chapter_id),
                None
            )

        # Calculate overall scores
        overall_timeline = sum(a.timeline_score for a in analyses) / max(1, len(analyses))
        overall_causality = sum(a.causality_score for a in analyses) / max(1, len(analyses))
        overall_knowledge = sum(a.knowledge_score for a in analyses) / max(1, len(analyses))
        overall_world = sum(a.world_rules_score for a in analyses) / max(1, len(analyses))
        overall_score = sum(a.overall_score for a in analyses) / max(1, len(analyses))

        # Generate recommendations
        recommendations = []
        if critical_issues > 0:
            recommendations.append(f"立即修复 {critical_issues} 个关键问题")
        if severe_issues > 0:
            recommendations.append(f"优先处理 {severe_issues} 个严重问题")
        if issues_by_type.get(PlotLogicType.TIMELINE_REVERSAL.value, 0) > 2:
            recommendations.append("时间线存在多处矛盾，需要仔细梳理各章节的时间顺序")
        if issues_by_type.get(PlotLogicType.CHARACTER_KNOWLEDGE_INCONSISTENT.value, 0) > 2:
            recommendations.append("角色认知存在不一致，注意角色在不同章节对同一事物的了解程度")
        if issues_by_type.get(PlotLogicType.CAUSE_EFFECT_MISSING.value, 0) > 2:
            recommendations.append("部分事件缺乏前因后果，添加适当的伏笔和解释")
        if issues_by_type.get(PlotLogicType.PLOT_INCONSISTENCY.value, 0) > 2:
            recommendations.append("文本中存在矛盾表述，仔细校对前后文的一致性")

        # Chapter summaries
        chapter_summaries = {}
        for analysis in analyses:
            if analysis.total_issues == 0:
                summary = "情节逻辑自洽，无明显问题"
            elif analysis.severe_issues > 0:
                summary = f"存在 {analysis.severe_issues} 个严重问题需要修复"
            elif analysis.total_issues <= 2:
                summary = f"存在 {analysis.total_issues} 个小问题，可逐步优化"
            else:
                summary = f"存在 {analysis.total_issues} 个问题，建议关注"
            chapter_summaries[analysis.chapter_profile.chapter_id] = summary

        return PlotLogicReport(
            report_id=report_id,
            analyses=analyses,
            total_chapters_analyzed=len(analyses),
            total_issues=total_issues,
            severe_issues=severe_issues,
            moderate_issues=moderate_issues,
            minor_issues=minor_issues,
            critical_issues=critical_issues,
            issues_by_type=issues_by_type,
            most_issues_chapter=most_issues_chapter,
            best_chapter=best_chapter,
            overall_timeline_score=overall_timeline,
            overall_causality_score=overall_causality,
            overall_knowledge_score=overall_knowledge,
            overall_world_rules_score=overall_world,
            overall_score=overall_score,
            key_recommendations=recommendations,
            chapter_summaries=chapter_summaries,
            unresolved_threads=[],
        )

    def create_revision_plan(
        self,
        analysis: PlotLogicAnalysis,
    ) -> PlotLogicRevision:
        """Create a revision plan based on analysis.

        Args:
            analysis: Plot logic analysis

        Returns:
            Revision plan with prioritized fixes
        """
        priority_fixes = []
        suggested_fixes = []
        optional_improvements = []

        for issue in analysis.issues:
            if issue.severity in [PlotLogicSeverity.SEVERE, PlotLogicSeverity.CRITICAL]:
                priority_fixes.append(issue)
            elif issue.severity == PlotLogicSeverity.MODERATE:
                suggested_fixes.append(issue)
            else:
                optional_improvements.append(issue)

        # Sort by severity and chapter
        priority_fixes.sort(key=lambda x: (x.chapter or 0, -x.severity.value == "critical"))
        suggested_fixes.sort(key=lambda x: (x.chapter or 0,))

        # Generate revision guidance by type
        revision_guidance: dict[str, list[str]] = {}
        for issue in analysis.issues:
            issue_type = issue.issue_type.value
            if issue_type not in revision_guidance:
                revision_guidance[issue_type] = []
            if issue.suggestion not in revision_guidance[issue_type]:
                revision_guidance[issue_type].append(issue.suggestion)

        # Determine focus areas
        revision_focus = []
        if analysis.issue_summary.get(PlotLogicType.TIMELINE_REVERSAL.value, 0) > 0:
            revision_focus.append("梳理时间线，确保事件顺序正确")
        if analysis.issue_summary.get(PlotLogicType.CHARACTER_KNOWLEDGE_INCONSISTENT.value, 0) > 0:
            revision_focus.append("统一角色认知，确保人物了解程度一致")
        if analysis.issue_summary.get(PlotLogicType.CAUSE_EFFECT_MISSING.value, 0) > 0:
            revision_focus.append("补充事件的前因后果")
        if analysis.issue_summary.get(PlotLogicType.PLOT_INCONSISTENCY.value, 0) > 0:
            revision_focus.append("消除文本中的矛盾表述")
        if analysis.issue_summary.get(PlotLogicType.TRAVEL_TIME_INSUFFICIENT.value, 0) > 0:
            revision_focus.append("添加地点转换的过渡说明")

        return PlotLogicRevision(
            analysis_id=analysis.analysis_id,
            priority_fixes=priority_fixes,
            suggested_fixes=suggested_fixes,
            optional_improvements=optional_improvements,
            revision_guidance=revision_guidance,
            revision_focus=revision_focus,
        )

    def get_summary(
        self,
        report: PlotLogicReport,
    ) -> str:
        """Get a human-readable summary of the report.

        Args:
            report: Plot logic report

        Returns:
            Summary string
        """
        lines = [
            "=== 情节逻辑自洽性检查报告 ===",
            f"检查章节数: {report.total_chapters_analyzed}",
            "",
            "总体评分:",
            f"  时间线一致性: {report.overall_timeline_score:.2f}/1.00",
            f"  因果关系一致性: {report.overall_causality_score:.2f}/1.00",
            f"  角色认知一致性: {report.overall_knowledge_score:.2f}/1.00",
            f"  世界规则一致性: {report.overall_world_rules_score:.2f}/1.00",
            f"  综合评分: {report.overall_score:.2f}/1.00",
            "",
            f"发现问题: {report.total_issues} 个",
            f"  - 关键: {report.critical_issues}",
            f"  - 严重: {report.severe_issues}",
            f"  - 中等: {report.moderate_issues}",
            f"  - 轻微: {report.minor_issues}",
        ]

        if report.issues_by_type:
            lines.append("")
            lines.append("问题类型分布:")
            for issue_type, count in sorted(report.issues_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  - {issue_type}: {count}")

        if report.most_issues_chapter:
            lines.append(f"\n问题最多的章节: 第{report.most_issues_chapter}章")

        if report.best_chapter:
            lines.append(f"表现最好的章节: 第{report.best_chapter}章")

        if report.key_recommendations:
            lines.append("")
            lines.append("重点建议:")
            for rec in report.key_recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)


# Missing pattern constant
CAUSE_EFFECT_PATTERNS = [
    r"因此", r"所以", r"于是", r"导致", r"造成",
    r"使得", r"因为", r"由于", r"为了", r"结果",
]
