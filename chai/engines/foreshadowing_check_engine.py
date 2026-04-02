"""Foreshadowing and callback check engine for quality assurance."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.foreshadowing_check import (
    CallbackStatus,
    CallbackQuality,
    ForeshadowingCheckIssue,
    PlantedForeshadowing,
    CallbackMatch,
    ForeshadowingCheckResult,
    ChapterForeshadowingProfile,
    ForeshadowingCheckAnalysis,
    ForeshadowingCheckRevision,
    ForeshadowingCheckPlan,
    ForeshadowingCheckReport,
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
CALLBACK_KEYWORDS = [
    "原来", "竟然", "才", "终于", "果然", "正如",
    "一如", "正如此刻", "此时此刻", "正如当年",
    "此时此刻", "恰如", "一如当年", "正如所料",
    "预言", "应验", "实现", "成真", "应验了",
    "等待", "终于等到", "终于等到你", "等到",
    "是时候了", "时候到了", "时机已到",
]

# Keywords indicating callback in dialogue
CALLBACK_DIALOGUE_MARKERS = [
    "我就知道", "我说过", "你忘了", "你记得吗",
    "当初我说过", "我说过会", "我说过要",
    "这就是", "这就是当年", "这就是那",
    "原来是你", "原来是他", "原来是这样",
]

# Thematic callback patterns
THEMATIC_PATTERNS = [
    (r"命运", r"命运"),
    (r"轮回", r"轮回"),
    (r"代价", r"代价"),
    (r"选择", r"选择"),
    (r"牺牲", r"牺牲"),
    (r"爱", r"爱"),
    (r"恨", r"恨"),
    (r"希望", r"希望"),
    (r"绝望", r"绝望"),
]

# Character callback patterns
CHARACTER_CALLBACK_PATTERNS = [
    (r"想起了", r"曾经"),
    (r"记得.*吗", r"记得"),
    (r"依然", r"依然"),
    (r"从未忘记", r"从未忘记"),
    (r"故人", r"故人"),
]

# Plot callback patterns
PLOT_CALLBACK_PATTERNS = [
    (r"那把剑", r"剑"),
    (r"那把刀", r"刀"),
    (r"那封信", r"信"),
    (r"那个秘密", r"秘密"),
    (r"那个预言", r"预言"),
    (r"当年的", r"当年"),
    (r"多年以后", r"多年"),
    (r"从那以后", r"从那"),
]


class ForeshadowingCheckEngine:
    """Engine for checking foreshadowing and callbacks in manuscript."""

    def __init__(self, ai_service: AIService):
        """Initialize foreshadowing check engine with AI service."""
        self.ai_service = ai_service

    def check_novel_foreshadowing(
        self,
        novel: Novel,
        planted_foreshadowing: Optional[list[PlantedForeshadowing]] = None,
    ) -> ForeshadowingCheckAnalysis:
        """Check all foreshadowing and callbacks in a novel.

        Args:
            novel: Novel to check
            planted_foreshadowing: Optional list of pre-identified planted elements

        Returns:
            Comprehensive foreshadowing check analysis
        """
        chapters = list(novel.chapters.values()) if isinstance(novel.chapters, dict) else novel.chapters
        total_chapters = len(chapters)

        if total_chapters == 0:
            return ForeshadowingCheckAnalysis()

        # Auto-detect planted foreshadowing if not provided
        if planted_foreshadowing is None:
            planted_foreshadowing = self._auto_detect_plants(chapters)

        # Detect callbacks
        callbacks = self._auto_detect_callbacks(chapters)

        # Match plants to callbacks
        matches = self._match_plants_to_callbacks(planted_foreshadowing, callbacks, chapters)

        # Build per-chapter profiles
        chapter_profiles = self._build_chapter_profiles(
            chapters, planted_foreshadowing, callbacks, matches
        )

        # Build check results
        check_results = self._build_check_results(
            planted_foreshadowing, callbacks, matches, chapters
        )

        # Identify orphaned and unplanted
        orphaned = self._identify_orphaned(planted_foreshadowing, matches)
        unplanted = self._identify_unplanted(callbacks, matches)

        # Build issues
        issues = self._build_issues(check_results, orphaned, unplanted)

        # Calculate statistics
        total_planted = len(planted_foreshadowing)
        total_called_back = sum(1 for r in check_results if r.status == CallbackStatus.PROPERLY_CALLED)
        payoff_ratio = total_called_back / total_planted if total_planted > 0 else 0.0

        # Count quality distribution
        excellent = sum(1 for r in check_results if r.quality == CallbackQuality.EXCELLENT)
        good = sum(1 for r in check_results if r.quality == CallbackQuality.GOOD)
        acceptable = sum(1 for r in check_results if r.quality == CallbackQuality.ACCEPTABLE)
        weak = sum(1 for r in check_results if r.quality == CallbackQuality.WEAK)
        missing = sum(1 for r in check_results if r.quality == CallbackQuality.MISSING)

        # Count timing issues
        premature = sum(1 for r in check_results if r.status == CallbackStatus.PREMATURE_CALLBACK)
        delayed = sum(1 for r in check_results if r.status == CallbackStatus.DELAYED_CALLBACK)

        # Calculate overall scores
        overall_callback = self._calculate_overall_callback_score(check_results, matches)
        overall_foreshadowing = self._calculate_overall_foreshadowing_score(
            chapter_profiles, total_chapters
        )

        analysis = ForeshadowingCheckAnalysis(
            overall_callback_score=overall_callback,
            overall_foreshadowing_score=overall_foreshadowing,
            total_planted=total_planted,
            total_called_back=total_called_back,
            total_orphaned=len(orphaned),
            total_unplanted=len(unplanted),
            payoff_ratio=payoff_ratio,
            chapter_profiles=chapter_profiles,
            check_results=check_results,
            callback_matches=matches,
            issues=issues,
            orphaned_foreshadowing=orphaned,
            orphaned_count=len(orphaned),
            excellent_callbacks=excellent,
            good_callbacks=good,
            acceptable_callbacks=acceptable,
            weak_callbacks=weak,
            missing_callbacks=missing,
            premature_callbacks=premature,
            delayed_callbacks=delayed,
            recommendations=self._generate_recommendations(check_results, orphaned, premature, delayed),
        )

        return analysis

    def check_chapter_foreshadowing(
        self,
        chapter: Chapter,
        prev_chapter: Optional[Chapter] = None,
        next_chapter: Optional[Chapter] = None,
    ) -> ChapterForeshadowingProfile:
        """Check foreshadowing in a single chapter.

        Args:
            chapter: Chapter to check
            prev_chapter: Previous chapter for context
            next_chapter: Next chapter for context

        Returns:
            Chapter foreshadowing profile
        """
        plants = self._detect_plants_in_chapter(chapter)
        callbacks = self._detect_callbacks_in_chapter(chapter)

        plant_count = len(plants)
        callback_count = len(callbacks)

        # Calculate density
        content_length = len(chapter.content) if chapter.content else 0
        foreshadowing_density = min(1.0, (plant_count + callback_count) * 0.1)

        # Calculate chapter callback score
        if plant_count > 0 and callback_count > 0:
            ratio = callback_count / plant_count
            chapter_score = min(1.0, ratio)
        elif plant_count > 0:
            chapter_score = 0.3  # Has plants but no callbacks yet
        elif callback_count > 0:
            chapter_score = 0.5  # Has callbacks (could be good or bad)
        else:
            chapter_score = 0.0

        profile = ChapterForeshadowingProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title or "",
            plants=[p.foreshadowing_id for p in plants],
            plant_count=plant_count,
            callbacks=[c.get("id", "") for c in callbacks],
            callback_count=callback_count,
            plant_callback_ratio=callback_count / plant_count if plant_count > 0 else 0.0,
            foreshadowing_density=foreshadowing_density,
            chapter_callback_score=chapter_score,
        )

        return profile

    def create_revision_plan(
        self,
        analysis: ForeshadowingCheckAnalysis,
    ) -> ForeshadowingCheckPlan:
        """Create a revision plan based on analysis.

        Args:
            analysis: Foreshadowing check analysis

        Returns:
            Revision plan
        """
        orphaned = analysis.orphaned_foreshadowing
        weak = [r.foreshadowing_id for r in analysis.check_results if r.quality == CallbackQuality.WEAK]
        timing_issues = [
            r.foreshadowing_id for r in analysis.check_results
            if r.status in (CallbackStatus.PREMATURE_CALLBACK, CallbackStatus.DELAYED_CALLBACK)
        ]

        # Create priority order based on severity
        priority_pairs = []
        for r in analysis.check_results:
            if r.status == CallbackStatus.ORPHANED:
                priority_pairs.append((r.foreshadowing_id, 100))  # Highest priority
            elif r.quality == CallbackQuality.MISSING:
                priority_pairs.append((r.foreshadowing_id, 90))
            elif r.status == CallbackStatus.PREMATURE_CALLBACK:
                priority_pairs.append((r.foreshadowing_id, 80))
            elif r.status == CallbackStatus.DELAYED_CALLBACK:
                priority_pairs.append((r.foreshadowing_id, 70))
            elif r.quality == CallbackQuality.WEAK:
                priority_pairs.append((r.foreshadowing_id, 50))

        priority_pairs.sort(key=lambda x: x[1], reverse=True)

        plan = ForeshadowingCheckPlan(
            orphaned_to_address=orphaned,
            weak_to_strengthen=weak,
            timing_issues_to_fix=timing_issues,
            priority_order=priority_pairs,
            estimated_additions=len(orphaned),
            estimated_revisions=len(weak) + len(timing_issues),
            ai_generation=True,
        )

        return plan

    def generate_check_report(
        self,
        analysis: ForeshadowingCheckAnalysis,
        plan: Optional[ForeshadowingCheckPlan] = None,
    ) -> ForeshadowingCheckReport:
        """Generate a complete check report.

        Args:
            analysis: Foreshadowing check analysis
            plan: Optional revision plan

        Returns:
            Complete check report
        """
        if plan is None:
            plan = self.create_revision_plan(analysis)

        summary = self._generate_summary(analysis)

        report = ForeshadowingCheckReport(
            analysis=analysis,
            revision_plan=plan,
            summary=summary,
            revisions_completed=[],
        )

        return report

    def get_callback_summary(self, analysis: ForeshadowingCheckAnalysis) -> str:
        """Get a human-readable summary of callback status.

        Args:
            analysis: Foreshadowing check analysis

        Returns:
            Summary string
        """
        lines = [
            "=== 伏笔与呼应检查报告 ===",
            "",
            f"总伏笔数: {analysis.total_planted}",
            f"已回收: {analysis.total_called_back}",
            f"未回收(孤儿伏笔): {analysis.total_orphaned}",
            f"伏笔回收率: {analysis.payoff_ratio:.0%}",
            "",
            "--- 质量分布 ---",
            f"优秀: {analysis.excellent_callbacks}",
            f"良好: {analysis.good_callbacks}",
            f"一般: {analysis.acceptable_callbacks}",
            f"较弱: {analysis.weak_callbacks}",
            f"缺失: {analysis.missing_callbacks}",
            "",
            "--- 时间问题 ---",
            f"过早回收: {analysis.premature_callbacks}",
            f"过晚回收: {analysis.delayed_callbacks}",
            "",
        ]

        if analysis.orphaned_foreshadowing:
            lines.append(f"孤儿伏笔 IDs: {', '.join(analysis.orphaned_foreshadowing[:5])}")
            if len(analysis.orphaned_foreshadowing) > 5:
                lines.append(f"  (还有 {len(analysis.orphaned_foreshadowing) - 5} 个)")

        return "\n".join(lines)

    # Helper methods

    def _auto_detect_plants(self, chapters: list[Chapter]) -> list[PlantedForeshadowing]:
        """Auto-detect planted foreshadowing elements in chapters."""
        plants = []

        for chapter in chapters:
            chapter_plants = self._detect_plants_in_chapter(chapter)
            plants.extend(chapter_plants)

        return plants

    def _detect_plants_in_chapter(self, chapter: Chapter) -> list[PlantedForeshadowing]:
        """Detect foreshadowing plants in a single chapter."""
        plants = []
        content = chapter.content or ""

        if not content:
            return plants

        # Look for plant keywords and patterns
        for keyword in FORESHADOWING_PLANT_KEYWORDS:
            if keyword in content:
                # Find context around keyword
                idx = content.find(keyword)
                start = max(0, idx - 100)
                end = min(len(content), idx + len(keyword) + 100)
                context = content[start:end]

                plant = PlantedForeshadowing(
                    foreshadowing_id=f"auto_plant_{chapter.number}_{len(plants)}",
                    plant_chapter=chapter.number,
                    plant_content=context,
                    plant_context=context,
                    technique="auto_detected",
                    subtlety_level=0.5,
                )
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
                if not any(p.plant_content == context for p in plants):
                    plant = PlantedForeshadowing(
                        foreshadowing_id=f"auto_plant_{chapter.number}_{len(plants)}",
                        plant_chapter=chapter.number,
                        plant_content=context,
                        plant_context=context,
                        technique=technique,
                        subtlety_level=0.6,
                    )
                    plants.append(plant)

        return plants

    def _auto_detect_callbacks(self, chapters: list[Chapter]) -> list[dict]:
        """Auto-detect callback moments in chapters."""
        callbacks = []

        for chapter in chapters:
            chapter_callbacks = self._detect_callbacks_in_chapter(chapter)
            callbacks.extend(chapter_callbacks)

        return callbacks

    def _detect_callbacks_in_chapter(self, chapter: Chapter) -> list[dict]:
        """Detect callbacks in a single chapter."""
        callbacks = []
        content = chapter.content or ""

        if not content:
            return callbacks

        # Look for callback keywords
        for keyword in CALLBACK_KEYWORDS:
            if keyword in content:
                idx = content.find(keyword)
                start = max(0, idx - 100)
                end = min(len(content), idx + len(keyword) + 100)
                context = content[start:end]

                callback = {
                    "id": f"auto_callback_{chapter.number}_{len(callbacks)}",
                    "chapter": chapter.number,
                    "content": context,
                    "keyword": keyword,
                }
                callbacks.append(callback)

        # Check for dialogue callback markers
        for marker in CALLBACK_DIALOGUE_MARKERS:
            if marker in content:
                idx = content.find(marker)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(marker) + 100)
                context = content[start:end]

                callback = {
                    "id": f"auto_callback_{chapter.number}_{len(callbacks)}",
                    "chapter": chapter.number,
                    "content": context,
                    "keyword": marker,
                    "is_dialogue": True,
                }
                callbacks.append(callback)

        return callbacks

    def _match_plants_to_callbacks(
        self,
        plants: list[PlantedForeshadowing],
        callbacks: list[dict],
        chapters: list[Chapter],
    ) -> list[CallbackMatch]:
        """Match planted foreshadowing to their callbacks."""
        matches = []

        # Build chapter content map for quick lookup
        chapter_content = {ch.number: ch.content or "" for ch in chapters}

        for plant in plants:
            plant_chapter = plant.plant_chapter
            plant_content = plant.plant_content

            # Find potential callbacks in later chapters
            best_match = None
            best_score = 0.0

            for callback in callbacks:
                if callback["chapter"] <= plant_chapter:
                    continue

                # Calculate basic match score
                score = self._calculate_match_score(plant, callback, chapter_content)

                if score > best_score and score > 0.3:
                    best_score = score
                    best_match = callback

            if best_match:
                match = CallbackMatch(
                    plant_chapter=plant_chapter,
                    callback_chapter=best_match["chapter"],
                    plant_content=plant_content,
                    callback_content=best_match["content"],
                    match_score=best_score,
                    quality=self._score_to_quality(best_score),
                    is_thematic=self._is_thematic_match(plant, best_match),
                    is_character=self._is_character_match(plant, best_match),
                    is_plot=self._is_plot_match(plant, best_match),
                    connection_description=self._describe_connection(plant, best_match),
                )
                matches.append(match)

        return matches

    def _calculate_match_score(
        self,
        plant: PlantedForeshadowing,
        callback: dict,
        chapter_content: dict[int, str],
    ) -> float:
        """Calculate match score between plant and callback."""
        score = 0.0

        plant_text = plant.plant_content.lower()
        callback_text = callback["content"].lower()

        # Check for word overlap
        plant_words = set(plant_text.split())
        callback_words = set(callback_text.split())

        if len(plant_words) > 0:
            overlap = len(plant_words & callback_words)
            word_score = overlap / len(plant_words)
            score += word_score * 0.4

        # Check for thematic patterns
        for plant_pat, callback_pat in THEMATIC_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                score += 0.2

        # Check for character patterns
        for plant_pat, callback_pat in CHARACTER_CALLBACK_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                score += 0.15

        # Check for plot patterns
        for plant_pat, callback_pat in PLOT_CALLBACK_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                score += 0.25

        return min(1.0, score)

    def _score_to_quality(self, score: float) -> CallbackQuality:
        """Convert numeric score to quality enum."""
        if score >= 0.8:
            return CallbackQuality.EXCELLENT
        elif score >= 0.6:
            return CallbackQuality.GOOD
        elif score >= 0.4:
            return CallbackQuality.ACCEPTABLE
        elif score >= 0.2:
            return CallbackQuality.WEAK
        else:
            return CallbackQuality.MISSING

    def _is_thematic_match(self, plant: PlantedForeshadowing, callback: dict) -> bool:
        """Check if match is thematic."""
        plant_text = plant.plant_content.lower()
        callback_text = callback["content"].lower()

        for plant_pat, callback_pat in THEMATIC_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                return True
        return False

    def _is_character_match(self, plant: PlantedForeshadowing, callback: dict) -> bool:
        """Check if match is character-related."""
        plant_text = plant.plant_content.lower()
        callback_text = callback["content"].lower()

        for plant_pat, callback_pat in CHARACTER_CALLBACK_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                return True
        return False

    def _is_plot_match(self, plant: PlantedForeshadowing, callback: dict) -> bool:
        """Check if match is plot-related."""
        plant_text = plant.plant_content.lower()
        callback_text = callback["content"].lower()

        for plant_pat, callback_pat in PLOT_CALLBACK_PATTERNS:
            if re.search(plant_pat, plant_text) and re.search(callback_pat, callback_text):
                return True
        return False

    def _describe_connection(self, plant: PlantedForeshadowing, callback: dict) -> str:
        """Describe the connection between plant and callback."""
        if self._is_thematic_match(plant, callback):
            return "主题呼应"
        elif self._is_character_match(plant, callback):
            return "人物呼应"
        elif self._is_plot_match(plant, callback):
            return "情节呼应"
        else:
            return "一般呼应"

    def _build_chapter_profiles(
        self,
        chapters: list[Chapter],
        plants: list[PlantedForeshadowing],
        callbacks: list[dict],
        matches: list[CallbackMatch],
    ) -> list[ChapterForeshadowingProfile]:
        """Build profile for each chapter."""
        # Group plants and callbacks by chapter
        plants_by_chapter: dict[int, list[str]] = {}
        callbacks_by_chapter: dict[int, list[str]] = {}

        for plant in plants:
            if plant.plant_chapter not in plants_by_chapter:
                plants_by_chapter[plant.plant_chapter] = []
            plants_by_chapter[plant.plant_chapter].append(plant.foreshadowing_id)

        for callback in callbacks:
            ch = callback["chapter"]
            if ch not in callbacks_by_chapter:
                callbacks_by_chapter[ch] = []
            callbacks_by_chapter[ch].append(callback["id"])

        # Build profiles
        profiles = []
        for chapter in chapters:
            plant_ids = plants_by_chapter.get(chapter.number, [])
            callback_ids = callbacks_by_chapter.get(chapter.number, [])

            plant_count = len(plant_ids)
            callback_count = len(callback_ids)

            profile = ChapterForeshadowingProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title or "",
                plants=plant_ids,
                plant_count=plant_count,
                callbacks=callback_ids,
                callback_count=callback_count,
                plant_callback_ratio=callback_count / plant_count if plant_count > 0 else 0.0,
                foreshadowing_density=min(1.0, (plant_count + callback_count) * 0.1),
                chapter_callback_score=self._calculate_chapter_score(plant_count, callback_count),
            )
            profiles.append(profile)

        return profiles

    def _calculate_chapter_score(self, plant_count: int, callback_count: int) -> float:
        """Calculate callback score for a chapter."""
        if plant_count > 0 and callback_count > 0:
            ratio = callback_count / plant_count
            return min(1.0, ratio)
        elif plant_count > 0:
            return 0.3
        elif callback_count > 0:
            return 0.5
        else:
            return 0.0

    def _build_check_results(
        self,
        plants: list[PlantedForeshadowing],
        callbacks: list[dict],
        matches: list[CallbackMatch],
        chapters: list[Chapter],
    ) -> list[ForeshadowingCheckResult]:
        """Build check results for each planted foreshadowing."""
        # Build match lookup
        match_by_plant_chapter: dict[int, list[CallbackMatch]] = {}
        for match in matches:
            if match.plant_chapter not in match_by_plant_chapter:
                match_by_plant_chapter[match.plant_chapter] = []
            match_by_plant_chapter[match.plant_chapter].append(match)

        results = []

        for plant in plants:
            plant_matches = match_by_plant_chapter.get(plant.plant_chapter, [])

            if not plant_matches:
                # Orphaned
                result = ForeshadowingCheckResult(
                    foreshadowing_id=plant.foreshadowing_id,
                    status=CallbackStatus.ORPHANED,
                    quality=CallbackQuality.MISSING,
                    plant_chapter=plant.plant_chapter,
                    plant_content=plant.plant_content,
                    callback_found=False,
                    timing_score=0.0,
                    connection_score=0.0,
                    thematic_alignment=0.0,
                    issues=["伏笔未回收"],
                    recommendations=["在后续章节中添加对此伏笔的呼应"],
                )
            else:
                # Use best match
                best_match = max(plant_matches, key=lambda m: m.match_score)

                # Determine timing
                timing_score = self._calculate_timing_score(plant, best_match)
                timing_issue = None
                status = CallbackStatus.PROPERLY_CALLED

                chapters_span = best_match.callback_chapter - plant.plant_chapter
                if chapters_span < 3:
                    status = CallbackStatus.PREMATURE_CALLBACK
                    timing_issue = "回收过早"
                elif chapters_span > 15:
                    status = CallbackStatus.DELAYED_CALLBACK
                    timing_issue = "回收过晚"

                result = ForeshadowingCheckResult(
                    foreshadowing_id=plant.foreshadowing_id,
                    status=status,
                    quality=best_match.quality,
                    plant_chapter=plant.plant_chapter,
                    plant_content=plant.plant_content,
                    callback_chapter=best_match.callback_chapter,
                    callback_content=best_match.callback_content,
                    callback_found=True,
                    timing_score=timing_score,
                    timing_issue=timing_issue,
                    connection_score=best_match.match_score,
                    thematic_alignment=1.0 if best_match.is_thematic else 0.5,
                    issues=[],
                    recommendations=self._generate_result_recommendations(status, best_match),
                )

            results.append(result)

        return results

    def _calculate_timing_score(self, plant: PlantedForeshadowing, match: CallbackMatch) -> float:
        """Calculate timing appropriateness score."""
        chapters_span = match.callback_chapter - plant.plant_chapter

        # Ideal: 3-15 chapters apart
        if 3 <= chapters_span <= 15:
            return 1.0
        elif chapters_span < 3:
            return max(0.0, chapters_span / 3)
        elif chapters_span <= 20:
            return max(0.5, 1.0 - (chapters_span - 15) / 10)
        else:
            return max(0.0, 0.5 - (chapters_span - 20) / 20)

    def _generate_result_recommendations(
        self,
        status: CallbackStatus,
        match: CallbackMatch,
    ) -> list[str]:
        """Generate recommendations for a single result."""
        recs = []

        if status == CallbackStatus.PREMATURE_CALLBACK:
            recs.append("考虑在更多章节后再回收此伏笔，增加张力")
        elif status == CallbackStatus.DELAYED_CALLBACK:
            recs.append("伏笔回收太晚，读者可能已忘记，考虑提前回收")

        if match.quality == CallbackQuality.WEAK:
            recs.append("加强伏笔与呼应的关联性")
        elif match.quality == CallbackQuality.EXCELLENT:
            recs.append("此伏笔处理优秀，可作为范例")

        if not match.is_thematic and not match.is_character and not match.is_plot:
            recs.append("考虑增加更多层面的呼应")

        return recs

    def _identify_orphaned(
        self,
        plants: list[PlantedForeshadowing],
        matches: list[CallbackMatch],
    ) -> list[str]:
        """Identify orphaned foreshadowing (planted but not called back)."""
        matched_plant_chapters = {m.plant_chapter for m in matches}
        orphaned = [
            p.foreshadowing_id for p in plants
            if p.plant_chapter not in matched_plant_chapters
        ]
        return orphaned

    def _identify_unplanted(
        self,
        callbacks: list[dict],
        matches: list[CallbackMatch],
    ) -> list[str]:
        """Identify unplanted callbacks (called back without proper plant)."""
        # This is harder to determine automatically
        # For now, return callbacks that don't have obvious plant matches
        return []

    def _build_issues(
        self,
        results: list[ForeshadowingCheckResult],
        orphaned: list[str],
        unplanted: list[str],
    ) -> list[ForeshadowingCheckIssue]:
        """Build list of issues."""
        issues = []

        # Add orphaned issues
        for orphan_id in orphaned:
            issue = ForeshadowingCheckIssue(
                issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                foreshadowing_id=orphan_id,
                chapter=0,  # Unknown
                issue_type="orphaned",
                severity="moderate",
                description="伏笔已种植但未被回收",
                suggested_fix="在后续章节中添加对此伏笔的呼应",
                priority=50,
            )
            issues.append(issue)

        # Add quality issues
        for result in results:
            if result.quality == CallbackQuality.WEAK:
                issue = ForeshadowingCheckIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    chapter=result.callback_chapter or result.plant_chapter,
                    issue_type="weak_callback",
                    severity="minor",
                    description="伏笔与呼应的关联性较弱",
                    suggested_fix="加强伏笔元素在后续章节中的出现",
                    priority=30,
                )
                issues.append(issue)

            if result.status == CallbackStatus.PREMATURE_CALLBACK:
                issue = ForeshadowingCheckIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    chapter=result.callback_chapter or 0,
                    issue_type="premature_callback",
                    severity="minor",
                    description="伏笔回收过早，张力不足",
                    suggested_fix="延迟回收以增加期待感",
                    priority=40,
                )
                issues.append(issue)

            if result.status == CallbackStatus.DELAYED_CALLBACK:
                issue = ForeshadowingCheckIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    foreshadowing_id=result.foreshadowing_id,
                    chapter=result.callback_chapter or 0,
                    issue_type="delayed_callback",
                    severity="minor",
                    description="伏笔回收过晚，读者可能已遗忘",
                    suggested_fix="提前回收或在回收前多次暗示",
                    priority=35,
                )
                issues.append(issue)

        return issues

    def _calculate_overall_callback_score(
        self,
        results: list[ForeshadowingCheckResult],
        matches: list[CallbackMatch],
    ) -> float:
        """Calculate overall callback quality score."""
        if not results:
            return 0.0

        scores = []

        for result in results:
            if result.callback_found:
                score = (result.connection_score * 0.4 +
                        result.timing_score * 0.3 +
                        (1.0 if result.quality in (CallbackQuality.EXCELLENT, CallbackQuality.GOOD) else 0.5))
                scores.append(score)
            else:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_overall_foreshadowing_score(
        self,
        profiles: list[ChapterForeshadowingProfile],
        total_chapters: int,
    ) -> float:
        """Calculate overall foreshadowing distribution score."""
        if not profiles:
            return 0.0

        # Check distribution - should have some foreshadowing throughout
        chapters_with_plants = sum(1 for p in profiles if p.plant_count > 0)
        chapters_with_callbacks = sum(1 for p in profiles if p.callback_count > 0)

        plant_coverage = chapters_with_plants / total_chapters if total_chapters > 0 else 0.0
        callback_coverage = chapters_with_callbacks / total_chapters if total_chapters > 0 else 0.0

        # Good distribution: plants early, callbacks spread out
        avg_density = sum(p.foreshadowing_density for p in profiles) / len(profiles)

        return (plant_coverage * 0.3 + callback_coverage * 0.3 + avg_density * 0.4)

    def _generate_recommendations(
        self,
        results: list[ForeshadowingCheckResult],
        orphaned: list[str],
        premature: int,
        delayed: int,
    ) -> list[str]:
        """Generate overall recommendations."""
        recs = []

        if len(orphaned) > 0:
            recs.append(f"建议为 {len(orphaned)} 个孤儿伏笔添加回收呼应")

        if premature > 2:
            recs.append("多个伏笔回收过早，建议拉长伏笔周期增加张力")

        if delayed > 2:
            recs.append("多个伏笔回收过晚，建议在回收前增加暗示频率")

        # Check for quality issues
        weak_count = sum(1 for r in results if r.quality == CallbackQuality.WEAK)
        if weak_count > 3:
            recs.append(f"存在 {weak_count} 个较弱的伏笔呼应，建议加强关联性")

        if not recs:
            recs.append("伏笔与呼应系统整体良好，保持当前节奏")

        return recs

    def _generate_summary(self, analysis: ForeshadowingCheckAnalysis) -> str:
        """Generate human-readable summary."""
        lines = [
            "《伏笔与呼应检查报告》",
            "",
            f"总伏笔数: {analysis.total_planted}",
            f"已回收: {analysis.total_called_back} ({analysis.payoff_ratio:.0%})",
            f"未回收: {analysis.total_orphaned}",
            "",
            "质量评估:",
            f"  优秀: {analysis.excellent_callbacks}",
            f"  良好: {analysis.good_callbacks}",
            f"  一般: {analysis.acceptable_callbacks}",
            f"  较弱: {analysis.weak_callbacks}",
            f"  缺失: {analysis.missing_callbacks}",
            "",
            f"伏笔评分: {analysis.overall_foreshadowing_score:.0%}",
            f"呼应评分: {analysis.overall_callback_score:.0%}",
        ]

        return "\n".join(lines)