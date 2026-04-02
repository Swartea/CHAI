"""Chapter word count engine for validating 2000-4000 character target."""

import re
from typing import Optional

from chai.models.chapter_word_count import (
    WordCountStatus,
    WordCountSeverity,
    ChapterWordCountProfile,
    ChapterWordCountIssue,
    ChapterWordCountAnalysis,
    ChapterWordCountRevision,
    ChapterWordCountReport,
)


# Default word count targets
DEFAULT_MIN_TARGET = 2000
DEFAULT_MAX_TARGET = 4000
DEFAULT_OPTIMAL_TARGET = 3000

# Severity thresholds (as ratio to target)
SEVERITY_MINOR_THRESHOLD = 0.1  # 10% deviation
SEVERITY_MODERATE_THRESHOLD = 0.2  # 20% deviation
SEVERITY_SEVERE_THRESHOLD = 0.3  # 30% deviation


class ChapterWordCountEngine:
    """Engine for validating chapter word counts meet 2000-4000 target."""

    def __init__(
        self,
        min_target: int = DEFAULT_MIN_TARGET,
        max_target: int = DEFAULT_MAX_TARGET,
        optimal_target: int = DEFAULT_OPTIMAL_TARGET,
    ):
        """Initialize chapter word count engine.

        Args:
            min_target: Minimum word count target (default 2000)
            max_target: Maximum word count target (default 4000)
            optimal_target: Optimal word count target (default 3000)
        """
        self.min_target = min_target
        self.max_target = max_target
        self.optimal_target = optimal_target

    def count_chinese_words(self, text: str) -> int:
        """Count Chinese words (characters as words).

        Args:
            text: Text to count

        Returns:
            Word count (Chinese characters + English words)
        """
        if not text:
            return 0
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = sum(len(w) for w in re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words

    def analyze_chapter(
        self,
        chapter_id: str,
        chapter_number: int,
        title: str,
        content: str,
        min_target: Optional[int] = None,
        max_target: Optional[int] = None,
        optimal_target: Optional[int] = None,
    ) -> ChapterWordCountProfile:
        """Analyze word count for a single chapter.

        Args:
            chapter_id: Unique chapter ID
            chapter_number: Chapter number
            title: Chapter title
            content: Chapter content
            min_target: Override minimum target
            max_target: Override maximum target
            optimal_target: Override optimal target

        Returns:
            ChapterWordCountProfile with analysis
        """
        min_t = min_target or self.min_target
        max_t = max_target or self.max_target
        optimal_t = optimal_target or self.optimal_target

        # Count words
        actual_count = self.count_chinese_words(content)

        # Calculate deviations
        deviation_from_min = min_t - actual_count if actual_count < min_t else 0
        deviation_from_max = actual_count - max_t if actual_count > max_t else 0
        deviation_from_optimal = abs(actual_count - optimal_t)

        # Calculate ratios
        ratio_to_min = actual_count / min_t if min_t > 0 else 0.0
        ratio_to_max = actual_count / max_t if max_t > 0 else 0.0
        ratio_to_optimal = actual_count / optimal_t if optimal_t > 0 else 0.0

        # Determine status
        if actual_count < min_t:
            status = WordCountStatus.TOO_SHORT
        elif actual_count > max_t:
            status = WordCountStatus.TOO_LONG
        elif optimal_t * 0.9 <= actual_count <= optimal_t * 1.1:
            status = WordCountStatus.OPTIMAL
        else:
            status = WordCountStatus.ACCEPTABLE

        # Determine severity
        severity = self._calculate_severity(
            actual_count, min_t, max_t, optimal_t
        )

        # Check if within target
        is_within_target = min_t <= actual_count <= max_t

        # Percent of optimal target
        percent_of_target = (actual_count / optimal_t * 100) if optimal_t > 0 else 0.0

        return ChapterWordCountProfile(
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            title=title,
            actual_word_count=actual_count,
            min_target=min_t,
            max_target=max_t,
            optimal_target=optimal_t,
            deviation_from_min=deviation_from_min,
            deviation_from_max=deviation_from_max,
            deviation_from_optimal=deviation_from_optimal,
            ratio_to_min=ratio_to_min,
            ratio_to_max=ratio_to_max,
            ratio_to_optimal=ratio_to_optimal,
            status=status,
            severity=severity,
            is_within_target=is_within_target,
            percent_of_target=percent_of_target,
        )

    def _calculate_severity(
        self,
        actual: int,
        min_t: int,
        max_t: int,
        optimal_t: int,
    ) -> WordCountSeverity:
        """Calculate severity of word count deviation."""
        if actual < min_t:
            deviation_ratio = (min_t - actual) / min_t
        elif actual > max_t:
            deviation_ratio = (actual - max_t) / max_t
        else:
            return WordCountSeverity.NONE

        if deviation_ratio >= SEVERITY_SEVERE_THRESHOLD:
            return WordCountSeverity.SEVERE
        elif deviation_ratio >= SEVERITY_MODERATE_THRESHOLD:
            return WordCountSeverity.MODERATE
        elif deviation_ratio >= SEVERITY_MINOR_THRESHOLD:
            return WordCountSeverity.MINOR
        else:
            return WordCountSeverity.NONE

    def identify_issue(
        self,
        profile: ChapterWordCountProfile,
    ) -> Optional[ChapterWordCountIssue]:
        """Identify a word count issue for a chapter.

        Args:
            profile: Chapter word count profile

        Returns:
            ChapterWordCountIssue if issue found, None otherwise
        """
        if profile.is_within_target and profile.status != WordCountStatus.OPTIMAL:
            # Acceptable but not optimal - still an issue worth noting
            if profile.status == WordCountStatus.TOO_SHORT:
                return ChapterWordCountIssue(
                    chapter_id=profile.chapter_id,
                    chapter_number=profile.chapter_number,
                    issue_type="too_short",
                    severity=WordCountSeverity.MINOR,
                    actual_word_count=profile.actual_word_count,
                    expected_word_count=profile.optimal_target,
                    deviation=abs(profile.deviation_from_optimal),
                    deviation_percent=abs(profile.deviation_from_optimal) / profile.optimal_target * 100
                        if profile.optimal_target > 0 else 0,
                    words_to_add=profile.optimal_target - profile.actual_word_count
                        if profile.actual_word_count < profile.optimal_target else None,
                    recommendation=f"章节字数略少，建议增加到约 {profile.optimal_target} 字以达到最佳效果"
                )
            elif profile.status == WordCountStatus.TOO_LONG:
                return ChapterWordCountIssue(
                    chapter_id=profile.chapter_id,
                    chapter_number=profile.chapter_number,
                    issue_type="too_long",
                    severity=WordCountSeverity.MINOR,
                    actual_word_count=profile.actual_word_count,
                    expected_word_count=profile.optimal_target,
                    deviation=abs(profile.deviation_from_optimal),
                    deviation_percent=abs(profile.deviation_from_optimal) / profile.optimal_target * 100
                        if profile.optimal_target > 0 else 0,
                    words_to_remove=profile.actual_word_count - profile.optimal_target
                        if profile.actual_word_count > profile.optimal_target else None,
                    recommendation=f"章节字数略多，建议精简到约 {profile.optimal_target} 字以达到最佳效果"
                )
            return None

        if profile.status == WordCountStatus.TOO_SHORT:
            words_to_add = profile.min_target - profile.actual_word_count
            severity = self._calculate_severity(
                profile.actual_word_count,
                profile.min_target,
                profile.max_target,
                profile.optimal_target
            )
            return ChapterWordCountIssue(
                chapter_id=profile.chapter_id,
                chapter_number=profile.chapter_number,
                issue_type="too_short",
                severity=severity,
                actual_word_count=profile.actual_word_count,
                expected_word_count=profile.min_target,
                deviation=words_to_add,
                deviation_percent=words_to_add / profile.min_target * 100
                    if profile.min_target > 0 else 0,
                words_to_add=words_to_add,
                recommendation=self._generate_expansion_recommendation(
                    profile, words_to_add
                )
            )

        if profile.status == WordCountStatus.TOO_LONG:
            words_to_remove = profile.actual_word_count - profile.max_target
            severity = self._calculate_severity(
                profile.actual_word_count,
                profile.min_target,
                profile.max_target,
                profile.optimal_target
            )
            return ChapterWordCountIssue(
                chapter_id=profile.chapter_id,
                chapter_number=profile.chapter_number,
                issue_type="too_long",
                severity=severity,
                actual_word_count=profile.actual_word_count,
                expected_word_count=profile.max_target,
                deviation=words_to_remove,
                deviation_percent=words_to_remove / profile.max_target * 100
                    if profile.max_target > 0 else 0,
                words_to_remove=words_to_remove,
                recommendation=self._generate_contraction_recommendation(
                    profile, words_to_remove
                )
            )

        return None

    def _generate_expansion_recommendation(
        self,
        profile: ChapterWordCountProfile,
        words_to_add: int,
    ) -> str:
        """Generate recommendation for expanding chapter."""
        if words_to_add > 1000:
            return (
                f"章节字数过少（{profile.actual_word_count}字），"
                f"需要大幅扩展约 {words_to_add} 字。"
                f"建议：1) 增加场景细节描写；2) 深化角色内心活动；"
                f"3) 添加更多对话；4) 丰富情节发展"
            )
        elif words_to_add > 500:
            return (
                f"章节字数偏少（{profile.actual_word_count}字），"
                f"建议增加约 {words_to_add} 字。"
                f"可以考虑：1) 补充场景过渡；2) 增加角色互动；3) 扩展现有场景"
            )
        else:
            return (
                f"章节字数略少（{profile.actual_word_count}字），"
                f"建议小幅补充约 {words_to_add} 字内容"
            )

    def _generate_contraction_recommendation(
        self,
        profile: ChapterWordCountProfile,
        words_to_remove: int,
    ) -> str:
        """Generate recommendation for contracting chapter."""
        if words_to_remove > 1000:
            return (
                f"章节字数过多（{profile.actual_word_count}字），"
                f"需要精简约 {words_to_remove} 字。"
                f"建议：1) 删除冗余描写；2) 精简对话；"
                f"3) 合并相似场景；4) 压缩情节推进节奏"
            )
        elif words_to_remove > 500:
            return (
                f"章节字数偏多（{profile.actual_word_count}字），"
                f"建议精简约 {words_to_remove} 字。"
                f"可以考虑：1) 删减重复内容；2) 简化场景描写"
            )
        else:
            return (
                f"章节字数略多（{profile.actual_word_count}字），"
                f"建议小幅精简约 {words_to_remove} 字"
            )

    def analyze_novel(
        self,
        novel_id: str,
        chapters: list[dict],
    ) -> ChapterWordCountAnalysis:
        """Analyze word counts for all chapters in a novel.

        Args:
            novel_id: Novel ID
            chapters: List of chapter dicts with id, number, title, content

        Returns:
            ChapterWordCountAnalysis with aggregated statistics
        """
        chapter_profiles = []
        issues = []

        for chapter in chapters:
            profile = self.analyze_chapter(
                chapter_id=chapter.get("id", f"ch_{chapter['number']}"),
                chapter_number=chapter["number"],
                title=chapter.get("title", f"第{chapter['number']}章"),
                content=chapter.get("content", ""),
            )
            chapter_profiles.append(profile)

            # Identify issues
            issue = self.identify_issue(profile)
            if issue:
                issues.append(issue)

        # Calculate aggregated statistics
        word_counts = [p.actual_word_count for p in chapter_profiles]
        total_chapters = len(word_counts)
        total_word_count = sum(word_counts)

        if total_chapters > 0:
            average_word_count = total_word_count / total_chapters
            sorted_counts = sorted(word_counts)
            if total_chapters % 2 == 0:
                median_word_count = (
                    sorted_counts[total_chapters // 2 - 1] +
                    sorted_counts[total_chapters // 2]
                ) / 2
            else:
                median_word_count = sorted_counts[total_chapters // 2]
            min_word_count = min(word_counts) if word_counts else 0
            max_word_count = max(word_counts) if word_counts else 0
        else:
            average_word_count = 0.0
            median_word_count = 0.0
            min_word_count = 0
            max_word_count = 0

        # Calculate variance and std dev
        if total_chapters > 0:
            variance = sum(
                (wc - average_word_count) ** 2 for wc in word_counts
            ) / total_chapters
            word_count_variance = variance
            word_count_std_dev = variance ** 0.5
            is_consistent = word_count_std_dev < average_word_count * 0.2
        else:
            word_count_variance = 0.0
            word_count_std_dev = 0.0
            is_consistent = True

        # Count chapters by status
        chapters_within_target = sum(
            1 for p in chapter_profiles if p.is_within_target
        )
        chapters_too_short = sum(
            1 for p in chapter_profiles if p.status == WordCountStatus.TOO_SHORT
        )
        chapters_too_long = sum(
            1 for p in chapter_profiles if p.status == WordCountStatus.TOO_LONG
        )

        # Calculate scores
        compliance_score = (
            chapters_within_target / total_chapters
            if total_chapters > 0 else 1.0
        )
        consistency_score = (
            1.0 - min(1.0, word_count_std_dev / average_word_count)
            if average_word_count > 0 else 1.0
        )
        overall_score = (compliance_score + consistency_score) / 2

        # Generate recommendations
        recommendations = self._generate_recommendations(
            chapters_within_target,
            total_chapters,
            chapters_too_short,
            chapters_too_long,
            is_consistent,
        )

        return ChapterWordCountAnalysis(
            novel_id=novel_id,
            chapter_profiles=chapter_profiles,
            total_chapters=total_chapters,
            chapters_within_target=chapters_within_target,
            chapters_too_short=chapters_too_short,
            chapters_too_long=chapters_too_long,
            average_word_count=average_word_count,
            median_word_count=median_word_count,
            min_word_count=min_word_count,
            max_word_count=max_word_count,
            total_word_count=total_word_count,
            word_count_variance=word_count_variance,
            word_count_std_dev=word_count_std_dev,
            is_consistent=is_consistent,
            compliance_score=compliance_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        chapters_within_target: int,
        total_chapters: int,
        chapters_too_short: int,
        chapters_too_long: int,
        is_consistent: bool,
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        if chapters_within_target == total_chapters:
            recommendations.append("所有章节字数均在目标范围内，表现优秀")
        else:
            if chapters_too_short > 0:
                recommendations.append(
                    f"有 {chapters_too_short} 个章节字数偏少，需要扩展内容"
                )
            if chapters_too_long > 0:
                recommendations.append(
                    f"有 {chapters_too_long} 个章节字数偏多，需要精简内容"
                )

        if not is_consistent:
            recommendations.append(
                "章节间字数差异较大，建议保持更一致的写作节奏"
            )

        if total_chapters > 0:
            compliance_rate = chapters_within_target / total_chapters * 100
            if compliance_rate >= 90:
                recommendations.append(
                    f"整体字数合规率达 {compliance_rate:.1f}%，表现良好"
                )
            elif compliance_rate >= 70:
                recommendations.append(
                    f"整体字数合规率为 {compliance_rate:.1f}%，建议进一步优化"
                )
            else:
                recommendations.append(
                    f"整体字数合规率仅 {compliance_rate:.1f}%，需要重点调整"
                )

        return recommendations

    def create_revision_plan(
        self,
        profile: ChapterWordCountProfile,
    ) -> Optional[ChapterWordCountRevision]:
        """Create revision plan for a chapter with word count issues.

        Args:
            profile: Chapter word count profile

        Returns:
            ChapterWordCountRevision if revision needed, None otherwise
        """
        if profile.is_within_target and profile.status == WordCountStatus.OPTIMAL:
            return None

        needs_expansion = profile.actual_word_count < profile.min_target
        needs_contraction = profile.actual_word_count > profile.max_target

        words_to_add = max(0, profile.min_target - profile.actual_word_count)
        words_to_remove = max(0, profile.actual_word_count - profile.max_target)

        # Calculate priority
        if not profile.is_within_target:
            priority = 1  # High priority
        elif profile.status != WordCountStatus.OPTIMAL:
            priority = 2  # Medium priority
        else:
            priority = 3  # Low priority

        # Generate section suggestions
        section_suggestions = []
        if needs_expansion:
            section_suggestions = [
                {"type": "add", "description": "增加场景细节描写", "words": words_to_add // 2},
                {"type": "add", "description": "深化角色内心活动", "words": words_to_add // 2},
            ]
        elif needs_contraction:
            section_suggestions = [
                {"type": "remove", "description": "精简冗余描写", "words": words_to_remove // 2},
                {"type": "remove", "description": "压缩重复内容", "words": words_to_remove // 2},
            ]

        return ChapterWordCountRevision(
            chapter_id=profile.chapter_id,
            chapter_number=profile.chapter_number,
            current_word_count=profile.actual_word_count,
            target_range=(profile.min_target, profile.max_target),
            needs_expansion=needs_expansion,
            needs_contraction=needs_contraction,
            words_to_add=words_to_add,
            words_to_remove=words_to_remove,
            section_suggestions=section_suggestions,
            priority=priority,
        )

    def generate_report(
        self,
        novel_id: str,
        novel_title: str,
        chapters: list[dict],
    ) -> ChapterWordCountReport:
        """Generate comprehensive word count report for a novel.

        Args:
            novel_id: Novel ID
            novel_title: Novel title
            chapters: List of chapter dicts with id, number, title, content

        Returns:
            ChapterWordCountReport with full analysis
        """
        analysis = self.analyze_novel(novel_id, chapters)

        # Create revision plans for chapters with issues
        revision_plans = []
        for profile in analysis.chapter_profiles:
            revision = self.create_revision_plan(profile)
            if revision:
                revision_plans.append(revision)

        chapters_needing_revision = len(revision_plans)

        # Estimate revision time
        total_words_to_adjust = sum(
            max(r.words_to_add, r.words_to_remove)
            for r in revision_plans
        )
        # Roughly 30 words per minute for revision
        estimated_minutes = total_words_to_adjust // 30
        estimated_revision_time = f"{estimated_minutes} 分钟"

        # Determine if passed
        passed = (
            analysis.chapters_within_target == analysis.total_chapters
            and analysis.chapters_too_short == 0
            and analysis.chapters_too_long == 0
        )

        # Generate summary
        summary = self._generate_summary(
            analysis.total_chapters,
            analysis.chapters_within_target,
            analysis.average_word_count,
            passed,
        )

        return ChapterWordCountReport(
            novel_id=novel_id,
            novel_title=novel_title,
            analysis=analysis,
            revision_plans=revision_plans,
            summary=summary,
            passed=passed,
            total_chapters=analysis.total_chapters,
            chapters_needing_revision=chapters_needing_revision,
            estimated_revision_time=estimated_revision_time,
        )

    def _generate_summary(
        self,
        total_chapters: int,
        chapters_within_target: int,
        average_word_count: float,
        passed: bool,
    ) -> str:
        """Generate human-readable summary."""
        if passed:
            return (
                f"全书 {total_chapters} 章字数检查全部通过。"
                f"平均每章 {average_word_count:.0f} 字，符合 2000-4000 字目标。"
            )
        else:
            compliance_rate = (
                chapters_within_target / total_chapters * 100
                if total_chapters > 0 else 0
            )
            return (
                f"全书 {total_chapters} 章中仅 {chapters_within_target} 章符合目标。"
                f"合规率 {compliance_rate:.1f}%，平均每章 {average_word_count:.0f} 字。"
                f"建议根据报告进行修订。"
            )

    def get_summary(
        self,
        report: ChapterWordCountReport,
    ) -> str:
        """Get a short summary from a report.

        Args:
            report: Word count report

        Returns:
            Short summary string
        """
        return report.summary