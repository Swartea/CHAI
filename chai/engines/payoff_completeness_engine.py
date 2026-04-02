"""Payoff completeness engine for validating foreshadowing resolution quality."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.payoff_completeness import (
    PayoffCompletenessType,
    PayoffCompletenessSeverity,
    PayoffSatisfactionLevel,
    PayoffCompletenessIssue,
    PlantedElementPayoff,
    ChapterPayoffProfile,
    PayoffCompletenessAnalysis,
    PayoffCompletenessRevision,
    PayoffCompletenessPlan,
    PayoffCompletenessReport,
)
from chai.services import AIService


# Keywords that indicate foreshadowing planting
FORESHADOWING_PLANT_KEYWORDS = [
    "有一天", "总有一天", "将来", "未来", "后来", "有一天会",
    "预示", "征兆", "预兆", "暗示", "伏笔",
    "记得", "想起", "似乎", "仿佛", "犹如",
    "突然", "没想到", "意料之外", "偶然", "巧合",
    "那把剑", "那把刀", "那枚", "那块", "那只",
    "古老的", "神秘的", "失落的", "遗忘的",
    "隐藏的", "封印的", "沉睡的", "等待的",
]

# Keywords that indicate callbacks (payoff moments)
PAYOFF_KEYWORDS = [
    "原来", "竟然", "才", "终于", "果然", "正如",
    "一如", "正如此刻", "此时此刻", "正如当年",
    "此时此刻", "恰如", "一如当年", "正如所料",
    "预言", "应验", "实现", "成真", "应验了",
    "等待", "终于等到", "终于等到你", "等到",
    "是时候了", "时候到了", "时机已到",
    "兑现", "实现", "完成", "达成",
]

# Keywords indicating strong payoff resolution
STRONG_PAYOFF_MARKERS = [
    "正如命运", "正如预言", "一如所料", "果然如此",
    "这就是", "这就是当年", "这就是那",
    "全部", "彻底", "完全", "圆满",
    "终结", "结束", "完成", "实现",
]

# Keywords indicating partial or weak payoff
WEAK_PAYOFF_MARKERS = [
    "也许", "可能", "大概", "似乎",
    "勉强", "勉强及格", "总算",
    "还没", "尚未", "未完全",
    "部分", "局部",
]

# Thematic resolution patterns
THEMATIC_RESOLUTION_PATTERNS = [
    (r"命运", r"(命运|宿命|注定)"),
    (r"代价", r"(代价|牺牲|交换)"),
    (r"选择", r"(选择|抉择|决定)"),
    (r"希望", r"(希望|曙光|光明)"),
    (r"绝望", r"(绝望|黑暗|深渊)"),
    (r"爱", r"(爱|情感|羁绊)"),
    (r"成长", r"(成长|蜕变|觉醒)"),
]


class PayoffCompletenessEngine:
    """Engine for checking payoff completeness and satisfaction."""

    def __init__(self, ai_service: AIService):
        """Initialize payoff completeness engine with AI service."""
        self.ai_service = ai_service

    def analyze_novel_payoff_completeness(
        self,
        novel: Novel,
        planted_foreshadowing: Optional[list[dict]] = None,
    ) -> PayoffCompletenessAnalysis:
        """Analyze all payoff completeness in a novel.

        Args:
            novel: Novel to check
            planted_foreshadowing: Optional list of pre-identified planted elements

        Returns:
            Comprehensive payoff completeness analysis
        """
        chapters = list(novel.chapters.values()) if isinstance(novel.chapters, dict) else novel.chapters
        total_chapters = len(chapters)

        if total_chapters == 0:
            return PayoffCompletenessAnalysis()

        # Auto-detect planted foreshadowing if not provided
        if planted_foreshadowing is None:
            planted_foreshadowing = self._auto_detect_plants(chapters)

        # Detect payoffs
        payoffs = self._auto_detect_payoffs(chapters)

        # Analyze each planted element
        payoff_results = self._analyze_payoff_results(planted_foreshadowing, payoffs, chapters)

        # Build per-chapter profiles
        chapter_profiles = self._build_chapter_profiles(
            chapters, planted_foreshadowing, payoffs, payoff_results
        )

        # Identify issues
        issues = self._identify_issues(payoff_results)

        # Calculate statistics
        total_plants = len(planted_foreshadowing)
        total_with_payoff = sum(1 for r in payoff_results if r.has_payoff)
        total_full_payoff = sum(1 for r in payoff_results if r.completeness_type == PayoffCompletenessType.FULL_PAYOFF)
        total_partial_payoff = sum(1 for r in payoff_results if r.completeness_type == PayoffCompletenessType.PARTIAL_PAYOFF)
        total_no_payoff = sum(1 for r in payoff_results if r.completeness_type == PayoffCompletenessType.NO_PAYOFF)

        payoff_ratio = total_with_payoff / total_plants if total_plants > 0 else 0.0
        full_payoff_ratio = total_full_payoff / total_plants if total_plants > 0 else 0.0

        # Count satisfaction distribution
        excellent = sum(1 for r in payoff_results if r.satisfaction_level == PayoffSatisfactionLevel.EXCELLENT)
        good = sum(1 for r in payoff_results if r.satisfaction_level == PayoffSatisfactionLevel.GOOD)
        acceptable = sum(1 for r in payoff_results if r.satisfaction_level == PayoffSatisfactionLevel.ACCEPTABLE)
        weak = sum(1 for r in payoff_results if r.satisfaction_level == PayoffSatisfactionLevel.WEAK)
        disappointing = sum(1 for r in payoff_results if r.satisfaction_level == PayoffSatisfactionLevel.DISAPPOINTING)

        # Calculate overall scores
        overall_completeness = self._calculate_overall_completeness(payoff_results)
        overall_satisfaction = self._calculate_overall_satisfaction(payoff_results)

        # Identify unresolved and partial
        unresolved = [r.foreshadowing_id for r in payoff_results if not r.has_payoff]
        partial = [r.foreshadowing_id for r in payoff_results if r.completeness_type == PayoffCompletenessType.PARTIAL_PAYOFF]

        analysis = PayoffCompletenessAnalysis(
            overall_completeness_score=overall_completeness,
            overall_satisfaction_score=overall_satisfaction,
            total_plants=total_plants,
            total_with_payoff=total_with_payoff,
            total_full_payoff=total_full_payoff,
            total_partial_payoff=total_partial_payoff,
            total_no_payoff=total_no_payoff,
            payoff_ratio=payoff_ratio,
            full_payoff_ratio=full_payoff_ratio,
            chapter_profiles=chapter_profiles,
            payoff_results=payoff_results,
            issues=issues,
            unresolved_ids=unresolved,
            unresolved_count=len(unresolved),
            partial_payoff_ids=partial,
            partial_payoff_count=len(partial),
            excellent_payoffs=excellent,
            good_payoffs=good,
            acceptable_payoffs=acceptable,
            weak_payoffs=weak,
            disappointing_payoffs=disappointing,
            recommendations=self._generate_recommendations(payoff_results, unresolved, partial),
        )

        return analysis

    def analyze_chapter_payoff_completeness(
        self,
        chapter: Chapter,
        prev_chapter: Optional[Chapter] = None,
        next_chapter: Optional[Chapter] = None,
    ) -> ChapterPayoffProfile:
        """Analyze payoff completeness in a single chapter.

        Args:
            chapter: Chapter to check
            prev_chapter: Previous chapter for context
            next_chapter: Next chapter for context

        Returns:
            Chapter payoff profile
        """
        plants = self._detect_plants_in_chapter(chapter)
        payoffs = self._detect_payoffs_in_chapter(chapter)

        plant_count = len(plants)
        payoff_count = len(payoffs)

        # Calculate density
        content_length = len(chapter.content) if chapter.content else 0
        payoff_density = min(1.0, (plant_count + payoff_count) * 0.1)

        # Calculate chapter scores
        avg_satisfaction = 0.5
        avg_completeness = 0.5
        if payoff_count > 0:
            satisfaction_scores = [self._assess_payoff_satisfaction(p.get("content", "")) for p in payoffs]
            completeness_scores = [self._assess_payoff_completeness(p.get("content", "")) for p in payoffs]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            avg_completeness = sum(completeness_scores) / len(completeness_scores)

        profile = ChapterPayoffProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title or "",
            payoffs=[p.get("id", "") for p in payoffs],
            payoff_count=payoff_count,
            plants=[p.get("id", "") for p in plants],
            plant_count=plant_count,
            payoff_to_plant_ratio=payoff_count / plant_count if plant_count > 0 else 0.0,
            payoff_density=payoff_density,
            avg_satisfaction_score=avg_satisfaction,
            avg_completeness_score=avg_completeness,
            chapter_payoff_score=(avg_satisfaction + avg_completeness) / 2,
        )

        return profile

    def check_payoff_completeness(
        self,
        plant: dict,
        payoff: Optional[dict],
    ) -> PlantedElementPayoff:
        """Check completeness for a single planted element.

        Args:
            plant: Planted foreshadowing element
            payoff: Payoff element if found

        Returns:
            Payoff completeness result
        """
        plant_content = plant.get("content", "")
        plant_chapter = plant.get("chapter", 0)
        plant_context = plant.get("context", plant_content)
        foreshadowing_id = plant.get("id", f"fs_{uuid.uuid4().hex[:8]}")

        if payoff is None:
            # No payoff found
            result = PlantedElementPayoff(
                foreshadowing_id=foreshadowing_id,
                plant_chapter=plant_chapter,
                plant_content=plant_content,
                plant_context=plant_context,
                has_payoff=False,
                completeness_type=PayoffCompletenessType.NO_PAYOFF,
                completeness_score=0.0,
                satisfaction_level=PayoffSatisfactionLevel.DISAPPOINTING,
                resolution_clarity=0.0,
                emotional_impact=0.0,
                thematic_alignment=0.0,
                reader_expectation_met=0.0,
                issues=["伏笔未回收"],
                recommendations=["在后续章节中添加对此伏笔的完整回收"],
            )
        else:
            payoff_content = payoff.get("content", "")
            payoff_chapter = payoff.get("chapter", 0)

            # Assess completeness and satisfaction
            completeness_score = self._assess_payoff_completeness(payoff_content)
            satisfaction_score = self._assess_payoff_satisfaction(payoff_content)
            resolution_clarity = self._assess_resolution_clarity(payoff_content)
            emotional_impact = self._assess_emotional_impact(payoff_content)
            thematic_alignment = self._assess_thematic_alignment(plant_content, payoff_content)
            expectation_met = self._assess_reader_expectation(plant_content, payoff_content)

            # Determine type
            if completeness_score >= 0.8:
                completeness_type = PayoffCompletenessType.FULL_PAYOFF
            elif completeness_score >= 0.3:
                completeness_type = PayoffCompletenessType.PARTIAL_PAYOFF
            else:
                completeness_type = PayoffCompletenessType.NO_PAYOFF

            # Determine satisfaction level
            if satisfaction_score >= 0.8:
                satisfaction_level = PayoffSatisfactionLevel.EXCELLENT
            elif satisfaction_score >= 0.6:
                satisfaction_level = PayoffSatisfactionLevel.GOOD
            elif satisfaction_score >= 0.4:
                satisfaction_level = PayoffSatisfactionLevel.ACCEPTABLE
            elif satisfaction_score >= 0.2:
                satisfaction_level = PayoffSatisfactionLevel.WEAK
            else:
                satisfaction_level = PayoffSatisfactionLevel.DISAPPOINTING

            issues = self._find_payoff_issues(
                completeness_score, satisfaction_score, resolution_clarity,
                emotional_impact, thematic_alignment, payoff_content
            )

            recommendations = self._generate_payoff_recommendations(
                completeness_type, satisfaction_level, issues
            )

            result = PlantedElementPayoff(
                foreshadowing_id=foreshadowing_id,
                plant_chapter=plant_chapter,
                plant_content=plant_content,
                plant_context=plant_context,
                has_payoff=True,
                payoff_chapter=payoff_chapter,
                payoff_content=payoff_content,
                completeness_type=completeness_type,
                completeness_score=completeness_score,
                satisfaction_level=satisfaction_level,
                resolution_clarity=resolution_clarity,
                emotional_impact=emotional_impact,
                thematic_alignment=thematic_alignment,
                reader_expectation_met=expectation_met,
                issues=issues,
                recommendations=recommendations,
            )

        return result

    def create_revision_plan(
        self,
        analysis: PayoffCompletenessAnalysis,
    ) -> PayoffCompletenessPlan:
        """Create a revision plan based on analysis.

        Args:
            analysis: Payoff completeness analysis

        Returns:
            Revision plan
        """
        unresolved = analysis.unresolved_ids
        partial = analysis.partial_payoff_ids
        weak = [r.foreshadowing_id for r in analysis.payoff_results
                if r.satisfaction_level in (PayoffSatisfactionLevel.WEAK, PayoffSatisfactionLevel.DISAPPOINTING)]

        # Create priority order based on severity
        priority_pairs = []
        for r in analysis.payoff_results:
            if r.completeness_type == PayoffCompletenessType.NO_PAYOFF:
                priority_pairs.append((r.foreshadowing_id, 100))  # Highest priority
            elif r.completeness_type == PayoffCompletenessType.PARTIAL_PAYOFF:
                priority_pairs.append((r.foreshadowing_id, 70))
            elif r.satisfaction_level == PayoffSatisfactionLevel.DISAPPOINTING:
                priority_pairs.append((r.foreshadowing_id, 60))
            elif r.satisfaction_level == PayoffSatisfactionLevel.WEAK:
                priority_pairs.append((r.foreshadowing_id, 40))

        priority_pairs.sort(key=lambda x: x[1], reverse=True)

        plan = PayoffCompletenessPlan(
            unresolved_to_address=unresolved,
            partial_to_strengthen=partial,
            weak_to_improve=weak,
            priority_order=priority_pairs,
            estimated_new_payoffs=len(unresolved),
            estimated_improvements=len(partial) + len(weak),
            ai_generation=True,
        )

        return plan

    def generate_report(
        self,
        analysis: PayoffCompletenessAnalysis,
        plan: Optional[PayoffCompletenessPlan] = None,
    ) -> PayoffCompletenessReport:
        """Generate a complete report.

        Args:
            analysis: Payoff completeness analysis
            plan: Optional revision plan

        Returns:
            Complete report
        """
        if plan is None:
            plan = self.create_revision_plan(analysis)

        summary = self._generate_summary(analysis)

        report = PayoffCompletenessReport(
            analysis=analysis,
            revision_plan=plan,
            summary=summary,
            revisions_completed=[],
        )

        return report

    def get_summary(self, analysis: PayoffCompletenessAnalysis) -> str:
        """Get a human-readable summary.

        Args:
            analysis: Payoff completeness analysis

        Returns:
            Summary string
        """
        lines = [
            "=== 伏笔回收完整性检查报告 ===",
            "",
            f"总伏笔数: {analysis.total_plants}",
            f"已回收: {analysis.total_with_payoff}",
            f"完整回收: {analysis.total_full_payoff}",
            f"部分回收: {analysis.total_partial_payoff}",
            f"未回收: {analysis.total_no_payoff}",
            f"完整回收率: {analysis.full_payoff_ratio:.0%}",
            f"整体完整度: {analysis.overall_completeness_score:.0%}",
            f"整体满意度: {analysis.overall_satisfaction_score:.0%}",
            "",
            "--- 满意度分布 ---",
            f"优秀: {analysis.excellent_payoffs}",
            f"良好: {analysis.good_payoffs}",
            f"一般: {analysis.acceptable_payoffs}",
            f"较弱: {analysis.weak_payoffs}",
            f"令人失望: {analysis.disappointing_payoffs}",
            "",
        ]

        if analysis.unresolved_ids:
            lines.append(f"未回收伏笔 IDs: {', '.join(analysis.unresolved_ids[:5])}")
            if len(analysis.unresolved_ids) > 5:
                lines.append(f"  (还有 {len(analysis.unresolved_ids) - 5} 个)")

        return "\n".join(lines)

    # Helper methods

    def _auto_detect_plants(self, chapters: list[Chapter]) -> list[dict]:
        """Auto-detect planted foreshadowing elements in chapters."""
        plants = []

        for chapter in chapters:
            chapter_plants = self._detect_plants_in_chapter(chapter)
            plants.extend(chapter_plants)

        return plants

    def _detect_plants_in_chapter(self, chapter: Chapter) -> list[dict]:
        """Detect foreshadowing plants in a single chapter."""
        plants = []
        content = chapter.content or ""

        if not content:
            return plants

        # Look for plant keywords and patterns
        for keyword in FORESHADOWING_PLANT_KEYWORDS:
            if keyword in content:
                idx = content.find(keyword)
                start = max(0, idx - 100)
                end = min(len(content), idx + len(keyword) + 100)
                context = content[start:end]

                plant = {
                    "id": f"auto_plant_{chapter.number}_{len(plants)}",
                    "chapter": chapter.number,
                    "content": context,
                    "context": context,
                    "keyword": keyword,
                }
                plants.append(plant)

        # Check for specific foreshadowing patterns
        patterns = [
            (r"那把[刀剑武器]", "object_foreshadowing"),
            (r"古老的[东西]", "ancient_foreshadowing"),
            (r"神秘的[现象]", "mysterious_foreshadowing"),
            (r"总有一天", "prophecy_foreshadowing"),
            (r"预示着", "omen_foreshadowing"),
        ]

        for pattern, technique in patterns:
            for match in re.finditer(pattern, content):
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]

                # Avoid duplicates
                if not any(p["content"] == context for p in plants):
                    plant = {
                        "id": f"auto_plant_{chapter.number}_{len(plants)}",
                        "chapter": chapter.number,
                        "content": context,
                        "context": context,
                        "technique": technique,
                    }
                    plants.append(plant)

        return plants

    def _auto_detect_payoffs(self, chapters: list[Chapter]) -> list[dict]:
        """Auto-detect payoff moments in chapters."""
        payoffs = []

        for chapter in chapters:
            chapter_payoffs = self._detect_payoffs_in_chapter(chapter)
            payoffs.extend(chapter_payoffs)

        return payoffs

    def _detect_payoffs_in_chapter(self, chapter: Chapter) -> list[dict]:
        """Detect payoff moments in a single chapter."""
        payoffs = []
        content = chapter.content or ""

        if not content:
            return payoffs

        # Look for payoff keywords
        for keyword in PAYOFF_KEYWORDS:
            if keyword in content:
                idx = content.find(keyword)
                start = max(0, idx - 100)
                end = min(len(content), idx + len(keyword) + 100)
                context = content[start:end]

                payoff = {
                    "id": f"auto_payoff_{chapter.number}_{len(payoffs)}",
                    "chapter": chapter.number,
                    "content": context,
                    "keyword": keyword,
                }
                payoffs.append(payoff)

        # Check for strong payoff markers
        for marker in STRONG_PAYOFF_MARKERS:
            if marker in content:
                idx = content.find(marker)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(marker) + 100)
                context = content[start:end]

                payoff = {
                    "id": f"auto_payoff_{chapter.number}_{len(payoffs)}",
                    "chapter": chapter.number,
                    "content": context,
                    "keyword": marker,
                    "is_strong": True,
                }
                payoffs.append(payoff)

        return payoffs

    def _analyze_payoff_results(
        self,
        plants: list[dict],
        payoffs: list[dict],
        chapters: list[Chapter],
    ) -> list[PlantedElementPayoff]:
        """Analyze payoff completeness for all planted elements."""
        results = []

        # Build chapter content map
        chapter_content = {ch.number: ch.content or "" for ch in chapters}

        for plant in plants:
            plant_chapter = plant.get("chapter", 0)

            # Find potential payoff in later chapters
            best_payoff = None
            best_score = 0.0

            for payoff in payoffs:
                if payoff.get("chapter", 0) <= plant_chapter:
                    continue

                score = self._calculate_payoff_match_score(plant, payoff, chapter_content)

                if score > best_score and score > 0.2:
                    best_score = score
                    best_payoff = payoff

            # Check completeness
            result = self.check_payoff_completeness(plant, best_payoff)
            results.append(result)

        return results

    def _calculate_payoff_match_score(
        self,
        plant: dict,
        payoff: dict,
        chapter_content: dict[int, str],
    ) -> float:
        """Calculate match score between plant and payoff."""
        score = 0.0

        plant_text = plant.get("content", "").lower()
        payoff_text = payoff.get("content", "").lower()

        # Check for word overlap
        plant_words = set(plant_text.split())
        payoff_words = set(payoff_text.split())

        if len(plant_words) > 0:
            overlap = len(plant_words & payoff_words)
            word_score = overlap / len(plant_words)
            score += word_score * 0.3

        # Check for thematic patterns
        for plant_pat, payoff_pat in THEMATIC_RESOLUTION_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(payoff_pat, payoff_text):
                score += 0.2

        # Check for strong payoff markers
        if payoff.get("is_strong", False):
            score += 0.2

        # Check for resolution keywords
        for keyword in STRONG_PAYOFF_MARKERS:
            if keyword in payoff_text:
                score += 0.15

        return min(1.0, score)

    def _assess_payoff_completeness(self, payoff_content: str) -> float:
        """Assess how complete the payoff is."""
        score = 0.5  # Base score

        content_lower = payoff_content.lower()

        # Strong resolution markers increase score
        for marker in STRONG_PAYOFF_MARKERS:
            if marker in content_lower:
                score += 0.15

        # Weak markers decrease score
        for marker in WEAK_PAYOFF_MARKERS:
            if marker in content_lower:
                score -= 0.15

        # Check for resolution indicators
        resolution_words = ["完成", "实现", "达成", "终结", "结束", "圆满", "彻底"]
        for word in resolution_words:
            if word in content_lower:
                score += 0.1

        return max(0.0, min(1.0, score))

    def _assess_payoff_satisfaction(self, payoff_content: str) -> float:
        """Assess how satisfying the payoff is."""
        score = 0.5  # Base score

        content_lower = payoff_content.lower()

        # Strong payoff markers increase satisfaction
        for marker in STRONG_PAYOFF_MARKERS:
            if marker in content_lower:
                score += 0.2

        # Emotional markers increase satisfaction
        emotional_markers = ["激动", "感动", "兴奋", "欣慰", "释然", "圆满"]
        for marker in emotional_markers:
            if marker in content_lower:
                score += 0.1

        # Weak markers decrease satisfaction
        for marker in WEAK_PAYOFF_MARKERS:
            if marker in content_lower:
                score -= 0.2

        return max(0.0, min(1.0, score))

    def _assess_resolution_clarity(self, payoff_content: str) -> float:
        """Assess how clearly the payoff resolves the plant."""
        score = 0.5

        content_lower = payoff_content.lower()

        # Clarity markers
        clarity_markers = ["原来", "果然", "正如", "这就是", "这就是当年", "全部", "彻底", "完全"]
        for marker in clarity_markers:
            if marker in content_lower:
                score += 0.15

        # Vague markers reduce clarity
        vague_markers = ["也许", "可能", "似乎", "大概", "不完全"]
        for marker in vague_markers:
            if marker in content_lower:
                score -= 0.15

        return max(0.0, min(1.0, score))

    def _assess_emotional_impact(self, payoff_content: str) -> float:
        """Assess the emotional impact of the payoff."""
        score = 0.5

        content_lower = payoff_content.lower()

        # High impact markers
        impact_markers = ["激动", "震撼", "感动", "热泪盈眶", "欣喜若狂", "释然", "圆满"]
        for marker in impact_markers:
            if marker in content_lower:
                score += 0.15

        # Neutral/low impact markers
        low_impact_markers = ["平静", "淡然", "平静地", "默默"]
        for marker in low_impact_markers:
            if marker in content_lower:
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _assess_thematic_alignment(self, plant_content: str, payoff_content: str) -> float:
        """Assess thematic alignment between plant and payoff."""
        score = 0.5

        plant_lower = plant_content.lower()
        payoff_lower = payoff_content.lower()

        # Check thematic patterns
        for plant_pat, payoff_pat in THEMATIC_RESOLUTION_PATTERNS:
            if re.search(plant_pat, plant_lower) and re.search(payoff_pat, payoff_lower):
                score += 0.2

        return max(0.0, min(1.0, score))

    def _assess_reader_expectation(self, plant_content: str, payoff_content: str) -> float:
        """Assess whether reader expectation is met."""
        score = 0.5

        plant_lower = plant_content.lower()
        payoff_lower = payoff_content.lower()

        # Plant-payoff connection
        plant_words = set(plant_lower.split())
        payoff_words = set(payoff_lower.split())
        overlap = len(plant_words & payoff_words)

        if overlap > 0:
            score += min(0.3, overlap * 0.05)

        # Strong payoff signals increase expectation
        for marker in STRONG_PAYOFF_MARKERS:
            if marker in payoff_lower:
                score += 0.1

        return max(0.0, min(1.0, score))

    def _find_payoff_issues(
        self,
        completeness: float,
        satisfaction: float,
        clarity: float,
        emotional: float,
        thematic: float,
        payoff_content: str,
    ) -> list[str]:
        """Find issues with the payoff."""
        issues = []

        if completeness < 0.3:
            issues.append("伏笔回收不完整")
        elif completeness < 0.6:
            issues.append("伏笔回收部分完成")

        if satisfaction < 0.3:
            issues.append("回收令人失望")
        elif satisfaction < 0.5:
            issues.append("回收满意度较低")

        if clarity < 0.4:
            issues.append("回收表达不够清晰")

        if emotional < 0.3:
            issues.append("情感冲击不足")

        if thematic < 0.4:
            issues.append("主题呼应不够")

        payoff_lower = payoff_content.lower()
        for marker in WEAK_PAYOFF_MARKERS:
            if marker in payoff_lower:
                issues.append("使用了弱化词汇")
                break

        return issues

    def _generate_payoff_recommendations(
        self,
        completeness_type: PayoffCompletenessType,
        satisfaction: PayoffSatisfactionLevel,
        issues: list[str],
    ) -> list[str]:
        """Generate recommendations for a single payoff."""
        recs = []

        if completeness_type == PayoffCompletenessType.NO_PAYOFF:
            recs.append("需要添加完整的伏笔回收")
        elif completeness_type == PayoffCompletenessType.PARTIAL_PAYOFF:
            recs.append("需要更完整地回收此伏笔")

        if satisfaction == PayoffSatisfactionLevel.DISAPPOINTING:
            recs.append("需要增强回收的情感冲击")
        elif satisfaction == PayoffSatisfactionLevel.WEAK:
            recs.append("可以考虑增强回收的感染力")

        if "回收表达不够清晰" in issues:
            recs.append("使用更明确的语言表达回收")

        if "主题呼应不够" in issues:
            recs.append("增加与主题的关联")

        return recs

    def _build_chapter_profiles(
        self,
        chapters: list[Chapter],
        plants: list[dict],
        payoffs: list[dict],
        results: list[PlantedElementPayoff],
    ) -> list[ChapterPayoffProfile]:
        """Build profile for each chapter."""
        # Group plants and payoffs by chapter
        plants_by_chapter: dict[int, list[str]] = {}
        payoffs_by_chapter: dict[int, list[str]] = {}

        for plant in plants:
            ch = plant.get("chapter", 0)
            if ch not in plants_by_chapter:
                plants_by_chapter[ch] = []
            plants_by_chapter[ch].append(plant.get("id", ""))

        for payoff in payoffs:
            ch = payoff.get("chapter", 0)
            if ch not in payoffs_by_chapter:
                payoffs_by_chapter[ch] = []
            payoffs_by_chapter[ch].append(payoff.get("id", ""))

        # Build profiles
        profiles = []
        for chapter in chapters:
            plant_ids = plants_by_chapter.get(chapter.number, [])
            payoff_ids = payoffs_by_chapter.get(chapter.number, [])

            plant_count = len(plant_ids)
            payoff_count = len(payoff_ids)

            profile = ChapterPayoffProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title or "",
                plants=plant_ids,
                plant_count=plant_count,
                payoffs=payoff_ids,
                payoff_count=payoff_count,
                payoff_to_plant_ratio=payoff_count / plant_count if plant_count > 0 else 0.0,
                payoff_density=min(1.0, (plant_count + payoff_count) * 0.1),
                avg_satisfaction_score=0.5,
                avg_completeness_score=0.5,
                chapter_payoff_score=0.5,
            )
            profiles.append(profile)

        return profiles

    def _identify_issues(
        self,
        results: list[PlantedElementPayoff],
    ) -> list[PayoffCompletenessIssue]:
        """Identify issues from results."""
        issues = []

        for result in results:
            if not result.has_payoff or result.completeness_type == PayoffCompletenessType.NO_PAYOFF:
                issue = PayoffCompletenessIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    plant_chapter=result.plant_chapter,
                    payoff_chapter=result.payoff_chapter,
                    issue_type="no_payoff",
                    severity=PayoffCompletenessSeverity.CRITICAL,
                    description="伏笔未回收",
                    suggested_fix="在后续章节中添加完整的伏笔回收",
                    priority=100,
                )
                issues.append(issue)

            elif result.completeness_type == PayoffCompletenessType.PARTIAL_PAYOFF:
                issue = PayoffCompletenessIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    plant_chapter=result.plant_chapter,
                    payoff_chapter=result.payoff_chapter,
                    issue_type="partial_payoff",
                    severity=PayoffCompletenessSeverity.SEVERE,
                    description="伏笔部分回收，不够完整",
                    suggested_fix="增强伏笔回收的完整性",
                    priority=70,
                )
                issues.append(issue)

            if result.satisfaction_level in (PayoffSatisfactionLevel.WEAK, PayoffSatisfactionLevel.DISAPPOINTING):
                issue = PayoffCompletenessIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    plant_chapter=result.plant_chapter,
                    payoff_chapter=result.payoff_chapter,
                    issue_type="low_satisfaction",
                    severity=PayoffCompletenessSeverity.MODERATE,
                    description=f"伏笔回收满意度较低: {result.satisfaction_level.value}",
                    suggested_fix="增强回收的情感冲击和表达",
                    priority=50,
                )
                issues.append(issue)

        return issues

    def _calculate_overall_completeness(
        self,
        results: list[PlantedElementPayoff],
    ) -> float:
        """Calculate overall completeness score."""
        if not results:
            return 0.0

        scores = [r.completeness_score for r in results]
        return sum(scores) / len(scores)

    def _calculate_overall_satisfaction(
        self,
        results: list[PlantedElementPayoff],
    ) -> float:
        """Calculate overall satisfaction score."""
        if not results:
            return 0.0

        # Convert satisfaction levels to numeric scores
        score_map = {
            PayoffSatisfactionLevel.EXCELLENT: 1.0,
            PayoffSatisfactionLevel.GOOD: 0.75,
            PayoffSatisfactionLevel.ACCEPTABLE: 0.5,
            PayoffSatisfactionLevel.WEAK: 0.25,
            PayoffSatisfactionLevel.DISAPPOINTING: 0.0,
        }

        scores = [score_map.get(r.satisfaction_level, 0.5) for r in results]
        return sum(scores) / len(scores)

    def _generate_recommendations(
        self,
        results: list[PlantedElementPayoff],
        unresolved: list[str],
        partial: list[str],
    ) -> list[str]:
        """Generate overall recommendations."""
        recs = []

        if len(unresolved) > 0:
            recs.append(f"建议为 {len(unresolved)} 个未回收的伏笔添加完整回收")

        if len(partial) > 0:
            recs.append(f"建议增强 {len(partial)} 个部分回收的伏笔的完整性")

        # Check for common issues
        weak_count = sum(1 for r in results if r.satisfaction_level == PayoffSatisfactionLevel.WEAK)
        if weak_count > 3:
            recs.append(f"存在 {weak_count} 个较弱的伏笔回收，建议增强情感冲击")

        low_clarity_count = sum(1 for r in results if r.resolution_clarity < 0.4)
        if low_clarity_count > 2:
            recs.append(f"存在 {low_clarity_count} 个回收表达不够清晰，建议使用更明确的语言")

        if not recs:
            recs.append("伏笔回收完整性整体良好")

        return recs

    def _generate_summary(self, analysis: PayoffCompletenessAnalysis) -> str:
        """Generate human-readable summary."""
        lines = [
            "《伏笔回收完整性检查报告》",
            "",
            f"总伏笔数: {analysis.total_plants}",
            f"已回收: {analysis.total_with_payoff} ({analysis.payoff_ratio:.0%})",
            f"完整回收: {analysis.total_full_payoff} ({analysis.full_payoff_ratio:.0%})",
            f"部分回收: {analysis.total_partial_payoff}",
            f"未回收: {analysis.total_no_payoff}",
            "",
            "满意度评估:",
            f"  优秀: {analysis.excellent_payoffs}",
            f"  良好: {analysis.good_payoffs}",
            f"  一般: {analysis.acceptable_payoffs}",
            f"  较弱: {analysis.weak_payoffs}",
            f"  令人失望: {analysis.disappointing_payoffs}",
            "",
            f"完整度评分: {analysis.overall_completeness_score:.0%}",
            f"满意度评分: {analysis.overall_satisfaction_score:.0%}",
        ]

        return "\n".join(lines)
