"""Description density engine for balancing descriptive detail throughout the novel."""

import re
import uuid
import math
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.description_density import (
    DescriptionDensityType,
    DescriptionDensityLevel,
    DescriptionBalanceStatus,
    SceneDescriptionMetrics,
    ChapterDensityProfile,
    DensityShift,
    UnifiedDensityProfile,
    DescriptionDensityAnalysis,
    DescriptionDensityRevision,
    DescriptionDensityPlan,
    DescriptionDensityReport,
    DescriptionDensityTemplate,
)
from chai.services import AIService


# Keywords and markers for description density analysis
ENVIRONMENT_MARKERS = [
    "天空", "大地", "地面", "墙壁", "天花板", "地板", "窗户", "门", "房间",
    "街道", "道路", "森林", "山脉", "河流", "海洋", "城市", "村庄", "建筑",
    "灯光", "阴影", "阳光", "月光", "黑暗", "明亮", "颜色", "形状", "大小",
    "环境", "场景", "位置", "背景", "周围", "四周", "远方", "近处",
]

SENSORY_MARKERS = [
    # Visual
    "看见", "看到", "注视", "凝视", "观察", "发现", "注意到", "瞥见",
    # Auditory
    "听到", "听见", "声音", "声响", "噪音", "寂静", "安静", "回声",
    # Olfactory
    "闻到", "气味", "芳香", "臭味", "香味", "腥味",
    # Gustatory
    "味道", "品尝", "甘甜", "苦涩", "酸味", "辣味",
    # Tactile
    "感觉", "触摸", "接触", "感受", "刺痛", "温暖", "寒冷", "光滑", "粗糙",
    # General
    "感官", "感知", "直觉",
]

EMOTIONAL_MARKERS = [
    "高兴", "快乐", "愉快", "开心", "喜悦", "兴奋", "激动", "愤怒", "生气",
    "悲伤", "难过", "痛苦", "伤心", "绝望", "恐惧", "害怕", "担心", "焦虑",
    "爱", "喜欢", "讨厌", "恨", "怨恨", "感激", "感动", "温暖", "幸福",
    "紧张", "放松", "平静", "安宁", "平和", "满足", "欣慰", "安心",
    "惊讶", "震惊", "诧异", "意外", "困惑", "迷茫", "失落", "孤独",
]

ACTION_VERBS = [
    "走", "跑", "跳", "飞", "游", "爬", "站立", "坐下", "躺下", "倒下",
    "看", "听", "说", "问", "答", "喊", "叫", "唱", "笑", "哭",
    "拿", "握", "抓", "抛", "扔", "推", "拉", "打", "踢", "撞",
    "吃", "喝", "睡", "醒", "呼吸", "心跳", "颤抖", "发抖",
    "攻击", "防御", "躲避", "逃跑", "追击", "战斗", "挣扎", "反抗",
    "思考", "回忆", "想象", "计划", "决定", "选择",
]

# Pre-built density templates
DENSITY_TEMPLATES: dict[str, DescriptionDensityTemplate] = {
    "epic_fantasy": DescriptionDensityTemplate(
        template_name="epic_fantasy",
        template_description="Epic fantasy with rich world-building and action",
        applicable_genres=["fantasy", "epic", "adventure"],
        applicable_scene_types=["battle", "ceremony", "discovery"],
        environment_density=0.20,
        action_density=0.25,
        dialogue_density=0.25,
        internal_thought_density=0.10,
        sensory_density=0.12,
        emotional_density=0.08,
    ),
    "urban_fantasy": DescriptionDensityTemplate(
        template_name="urban_fantasy",
        template_description="Modern urban fantasy with balance of action and dialogue",
        applicable_genres=["fantasy", "urban", "contemporary"],
        applicable_scene_types=["investigation", "confrontation", "social"],
        environment_density=0.12,
        action_density=0.20,
        dialogue_density=0.38,
        internal_thought_density=0.12,
        sensory_density=0.08,
        emotional_density=0.10,
    ),
    "romance": DescriptionDensityTemplate(
        template_name="romance",
        template_description="Romantic story with emotional depth and intimate scenes",
        applicable_genres=["romance", "contemporary", "historical"],
        applicable_scene_types=["intimate", "conflict", "reconciliation"],
        environment_density=0.10,
        action_density=0.08,
        dialogue_density=0.35,
        internal_thought_density=0.22,
        sensory_density=0.10,
        emotional_density=0.15,
    ),
    "mystery": DescriptionDensityTemplate(
        template_name="mystery",
        template_description="Mystery/suspense with building tension and clues",
        applicable_genres=["mystery", "thriller", "detective"],
        applicable_scene_types=["investigation", "revelation", "confrontation"],
        environment_density=0.15,
        action_density=0.15,
        dialogue_density=0.35,
        internal_thought_density=0.18,
        sensory_density=0.08,
        emotional_density=0.09,
    ),
    "scifi": DescriptionDensityTemplate(
        template_name="scifi",
        template_description="Science fiction with technical details and world-building",
        applicable_genres=["sci-fi", "science fiction", "space opera"],
        applicable_scene_types=["discovery", "conflict", "technical"],
        environment_density=0.18,
        action_density=0.22,
        dialogue_density=0.28,
        internal_thought_density=0.12,
        sensory_density=0.12,
        emotional_density=0.08,
    ),
    "literary": DescriptionDensityTemplate(
        template_name="literary",
        template_description="Literary fiction with rich prose and introspection",
        applicable_genres=["literary", "contemporary", "historical"],
        applicable_scene_types=["reflection", "dialogue", "observation"],
        environment_density=0.15,
        action_density=0.10,
        dialogue_density=0.25,
        internal_thought_density=0.28,
        sensory_density=0.12,
        emotional_density=0.10,
    ),
    "action_adventure": DescriptionDensityTemplate(
        template_name="action_adventure",
        template_description="Fast-paced action with dynamic scenes",
        applicable_genres=["action", "adventure", "military"],
        applicable_scene_types=["battle", "chase", "escape"],
        environment_density=0.10,
        action_density=0.40,
        dialogue_density=0.25,
        internal_thought_density=0.08,
        sensory_density=0.07,
        emotional_density=0.10,
    ),
    "horror": DescriptionDensityTemplate(
        template_name="horror",
        template_description="Horror with atmospheric tension and sensory details",
        applicable_genres=["horror", "dark fantasy", "gothic"],
        applicable_scene_types=["terror", "discovery", "confrontation"],
        environment_density=0.18,
        action_density=0.15,
        dialogue_density=0.20,
        internal_thought_density=0.15,
        sensory_density=0.20,
        emotional_density=0.12,
    ),
}


class DescriptionDensityEngine:
    """Engine for analyzing and balancing description density throughout the novel."""

    def __init__(self, ai_service: AIService):
        """Initialize description density engine with AI service."""
        self.ai_service = ai_service
        self._templates = dict(DENSITY_TEMPLATES)

    def analyze_chapter_density(self, chapter: Chapter) -> ChapterDensityProfile:
        """Analyze the description density profile of a single chapter.

        Args:
            chapter: Chapter to analyze

        Returns:
            ChapterDensityProfile with density metrics
        """
        content = chapter.content
        if not content:
            return ChapterDensityProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title,
            )

        # Calculate basic metrics
        total_chars = len(content)
        sentences = re.findall(r'[。！？.!?]', content)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        sentence_avg_length = total_chars / max(1, sentence_count)
        paragraph_avg_length = total_chars / max(1, paragraph_count)

        # Count dialogue
        dialogues = re.findall(r'"[^"]*"', content)
        dialogue_chars = sum(len(d) for d in dialogues)
        dialogue_density = dialogue_chars / total_chars if total_chars > 0 else 0

        # Count environment markers
        env_count = sum(content.count(marker) for marker in ENVIRONMENT_MARKERS)
        env_density = min(1.0, env_count / max(1, total_chars) * 100)

        # Count sensory markers
        sensory_count = sum(content.count(marker) for marker in SENSORY_MARKERS)
        sensory_density = min(1.0, sensory_count / max(1, total_chars) * 100)

        # Count emotional markers
        emotional_count = sum(content.count(marker) for marker in EMOTIONAL_MARKERS)
        emotional_density = min(1.0, emotional_count / max(1, total_chars) * 100)

        # Count action verbs
        action_count = sum(content.count(verb) for verb in ACTION_VERBS)
        action_density = min(1.0, action_count / max(1, total_chars) * 50)

        # Estimate internal thought density (heuristic: first-person thoughts, introspection)
        internal_markers = ["想", "觉得", "知道", "明白", "思考", "回忆", "想着", "心里", "心中", "暗自"]
        internal_count = sum(content.count(marker) for marker in internal_markers)
        internal_thought_density = min(1.0, internal_count / max(1, total_chars) * 80)

        # Count descriptive words (adjectives ending in 的, adverbs ending in 地)
        descriptive_pattern = r'\w+的|\w+地'
        descriptive_words = re.findall(descriptive_pattern, content)
        descriptive_count = len(descriptive_words)

        # Determine overall density level
        total_density_metric = (
            env_density * 0.2 +
            action_density * 0.25 +
            dialogue_density * 0.2 +
            internal_thought_density * 0.15 +
            sensory_density * 0.1 +
            emotional_density * 0.1
        )

        if total_density_metric < 0.15:
            overall_density = DescriptionDensityLevel.SPARSE
        elif total_density_metric < 0.25:
            overall_density = DescriptionDensityLevel.LIGHT
        elif total_density_metric < 0.40:
            overall_density = DescriptionDensityLevel.MODERATE
        elif total_density_metric < 0.55:
            overall_density = DescriptionDensityLevel.RICH
        else:
            overall_density = DescriptionDensityLevel.EXCESSIVE

        # Calculate density and balance scores
        density_score = 1.0 - min(0.5, abs(total_density_metric - 0.30) * 2)
        balance_score = self._calculate_balance_score(
            env_density, action_density, dialogue_density,
            internal_thought_density, sensory_density, emotional_density
        )

        # Determine balance status
        if balance_score >= 0.85:
            balance_status = DescriptionBalanceStatus.BALANCED
        elif balance_score >= 0.70:
            balance_status = DescriptionBalanceStatus.SLIGHTLY_UNEVEN
        elif balance_score >= 0.50:
            balance_status = DescriptionBalanceStatus.UNEVEN
        else:
            balance_status = DescriptionBalanceStatus.SEVERELY_UNEVEN

        # Collect issues
        issues = self._identify_density_issues(
            env_density, action_density, dialogue_density,
            internal_thought_density, sensory_density, emotional_density,
            chapter.number
        )

        return ChapterDensityProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title,
            total_words=chapter.word_count or total_chars,
            overall_density=overall_density,
            balance_status=balance_status,
            environment_density=env_density,
            action_density=action_density,
            dialogue_density=dialogue_density,
            internal_thought_density=internal_thought_density,
            sensory_density=sensory_density,
            emotional_density=emotional_density,
            descriptive_word_count=descriptive_count,
            sensory_detail_count=sensory_count,
            action_verb_count=action_count,
            density_score=density_score,
            balance_score=balance_score,
            density_issues=issues,
        )

    def _calculate_balance_score(
        self,
        env: float,
        action: float,
        dialogue: float,
        internal: float,
        sensory: float,
        emotional: float,
    ) -> float:
        """Calculate how well-balanced the description types are."""
        values = [env, action, dialogue, internal, sensory, emotional]
        if not values:
            return 1.0

        mean = sum(values) / len(values)
        if mean == 0:
            return 1.0

        # Calculate coefficient of variation (lower = more balanced)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean if mean > 0 else 0

        # Convert CV to a 0-1 score (lower CV = higher score)
        # Typical CV for balanced content is < 0.5
        score = max(0.0, 1.0 - cv)
        return score

    def _identify_density_issues(
        self,
        env: float,
        action: float,
        dialogue: float,
        internal: float,
        sensory: float,
        emotional: float,
        chapter_num: int,
    ) -> list[str]:
        """Identify specific description density issues in a chapter."""
        issues = []

        # Check for excessive or insufficient elements
        if env > 0.25:
            issues.append(f"Chapter {chapter_num}: Excessive environment description ({env:.1%})")
        elif env < 0.05:
            issues.append(f"Chapter {chapter_num}: Sparse environment description ({env:.1%})")

        if action > 0.40:
            issues.append(f"Chapter {chapter_num}: Excessive action description ({action:.1%})")
        elif action < 0.05:
            issues.append(f"Chapter {chapter_num}: Minimal action scenes ({action:.1%})")

        if dialogue > 0.50:
            issues.append(f"Chapter {chapter_num}: Too much dialogue ({dialogue:.1%})")
        elif dialogue < 0.10:
            issues.append(f"Chapter {chapter_num}: Sparse dialogue ({dialogue:.1%})")

        if internal > 0.35:
            issues.append(f"Chapter {chapter_num}: Excessive internal thoughts ({internal:.1%})")
        elif internal < 0.03:
            issues.append(f"Chapter {chapter_num}: Lacking internal thoughts ({internal:.1%})")

        if sensory > 0.20:
            issues.append(f"Chapter {chapter_num}: Excessive sensory details ({sensory:.1%})")
        elif sensory < 0.02:
            issues.append(f"Chapter {chapter_num}: Sparse sensory details ({sensory:.1%})")

        if emotional > 0.20:
            issues.append(f"Chapter {chapter_num}: Excessive emotional expression ({emotional:.1%})")
        elif emotional < 0.02:
            issues.append(f"Chapter {chapter_num}: Sparse emotional expression ({emotional:.1%})")

        return issues

    def detect_density_shifts(
        self,
        chapter_profiles: list[ChapterDensityProfile],
    ) -> list[DensityShift]:
        """Detect shifts in description density between chapters.

        Args:
            chapter_profiles: List of chapter density profiles in order

        Returns:
            List of detected DensityShift objects
        """
        shifts: list[DensityShift] = []

        if len(chapter_profiles) < 2:
            return shifts

        for i in range(len(chapter_profiles) - 1):
            current = chapter_profiles[i]
            next_chapter = chapter_profiles[i + 1]

            # Calculate differences for each density type
            env_diff = abs(current.environment_density - next_chapter.environment_density)
            action_diff = abs(current.action_density - next_chapter.action_density)
            dialogue_diff = abs(current.dialogue_density - next_chapter.dialogue_density)
            internal_diff = abs(current.internal_thought_density - next_chapter.internal_thought_density)
            sensory_diff = abs(current.sensory_density - next_chapter.sensory_density)
            emotional_diff = abs(current.emotional_density - next_chapter.emotional_density)

            # Overall shift magnitude
            shift_magnitude = (
                env_diff + action_diff + dialogue_diff +
                internal_diff + sensory_diff + emotional_diff
            ) / 6

            # Determine affected aspects
            affected: list[DescriptionDensityType] = []
            if env_diff > 0.05:
                affected.append(DescriptionDensityType.ENVIRONMENT)
            if action_diff > 0.05:
                affected.append(DescriptionDensityType.ACTION)
            if dialogue_diff > 0.08:
                affected.append(DescriptionDensityType.DIALOGUE)
            if internal_diff > 0.05:
                affected.append(DescriptionDensityType.INTERNAL_THOUGHT)
            if sensory_diff > 0.03:
                affected.append(DescriptionDensityType.SENSORY)
            if emotional_diff > 0.03:
                affected.append(DescriptionDensityType.EMOTIONAL)

            if shift_magnitude > 0.03 and affected:
                # Determine severity
                if shift_magnitude > 0.15:
                    severity = "severe"
                elif shift_magnitude > 0.08:
                    severity = "moderate"
                else:
                    severity = "minor"

                # Determine shift type
                total_current = (
                    current.environment_density + current.action_density +
                    current.dialogue_density + current.internal_thought_density +
                    current.sensory_density + current.emotional_density
                )
                total_next = (
                    next_chapter.environment_density + next_chapter.action_density +
                    next_chapter.dialogue_density + next_chapter.internal_thought_density +
                    next_chapter.sensory_density + next_chapter.emotional_density
                )

                if total_next > total_current:
                    shift_type = "increase"
                elif total_next < total_current:
                    shift_type = "decrease"
                else:
                    shift_type = "redistribution"

                affected_names = [a.value for a in affected]
                shifts.append(DensityShift(
                    shift_id=str(uuid.uuid4())[:8],
                    start_chapter=current.chapter_number,
                    end_chapter=next_chapter.chapter_number,
                    shift_type=shift_type,
                    severity=severity,
                    description=(
                        f"Chapter {current.chapter_number} to {next_chapter.chapter_number}: "
                        f"{shift_type} in description density "
                        f"(magnitude: {shift_magnitude:.2f})"
                    ),
                    magnitude=shift_magnitude,
                    affected_aspects=affected,
                    likely_cause=self._analyze_shift_cause(current, next_chapter),
                ))

        return shifts

    def _analyze_shift_cause(
        self,
        before: ChapterDensityProfile,
        after: ChapterDensityProfile,
    ) -> str:
        """Analyze the likely cause of a density shift."""
        causes = []

        if abs(before.action_density - after.action_density) > 0.1:
            causes.append("action scene intensity change")

        if abs(before.dialogue_density - after.dialogue_density) > 0.15:
            causes.append("dialogue proportion change")

        if abs(before.environment_density - after.environment_density) > 0.08:
            causes.append("scene/location transition")

        if abs(before.internal_thought_density - after.internal_thought_density) > 0.1:
            causes.append("narrative focus shift (external vs internal)")

        if before.overall_density != after.overall_density:
            causes.append(f"overall density shift from {before.overall_density.value} to {after.overall_density.value}")

        return ", ".join(causes) if causes else "unknown cause"

    def create_unified_density_profile(
        self,
        chapter_profiles: list[ChapterDensityProfile],
    ) -> UnifiedDensityProfile:
        """Create the target unified density profile from chapter analyses.

        Args:
            chapter_profiles: List of chapter density profiles

        Returns:
            UnifiedDensityProfile with target values
        """
        if not chapter_profiles:
            return UnifiedDensityProfile()

        # Calculate averages
        avg_env = sum(p.environment_density for p in chapter_profiles) / len(chapter_profiles)
        avg_action = sum(p.action_density for p in chapter_profiles) / len(chapter_profiles)
        avg_dialogue = sum(p.dialogue_density for p in chapter_profiles) / len(chapter_profiles)
        avg_internal = sum(p.internal_thought_density for p in chapter_profiles) / len(chapter_profiles)
        avg_sensory = sum(p.sensory_density for p in chapter_profiles) / len(chapter_profiles)
        avg_emotional = sum(p.emotional_density for p in chapter_profiles) / len(chapter_profiles)

        # Calculate variance for ranges
        def calc_range(avg: float, values: list[float]) -> tuple[float, float]:
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            std_dev = math.sqrt(variance)
            return (
                max(0.02, avg - 1.5 * std_dev),
                min(0.60, avg + 1.5 * std_dev),
            )

        env_range = calc_range(avg_env, [p.environment_density for p in chapter_profiles])
        action_range = calc_range(avg_action, [p.action_density for p in chapter_profiles])
        dialogue_range = calc_range(avg_dialogue, [p.dialogue_density for p in chapter_profiles])
        internal_range = calc_range(avg_internal, [p.internal_thought_density for p in chapter_profiles])
        sensory_range = calc_range(avg_sensory, [p.sensory_density for p in chapter_profiles])
        emotional_range = calc_range(avg_emotional, [p.emotional_density for p in chapter_profiles])

        # Determine overall density level
        total_avg = avg_env + avg_action + avg_dialogue + avg_internal + avg_sensory + avg_emotional
        if total_avg < 0.15:
            overall_density = DescriptionDensityLevel.SPARSE
        elif total_avg < 0.25:
            overall_density = DescriptionDensityLevel.LIGHT
        elif total_avg < 0.40:
            overall_density = DescriptionDensityLevel.MODERATE
        elif total_avg < 0.55:
            overall_density = DescriptionDensityLevel.RICH
        else:
            overall_density = DescriptionDensityLevel.EXCESSIVE

        return UnifiedDensityProfile(
            target_overall_density=overall_density,
            target_environment_density=avg_env,
            target_action_density=avg_action,
            target_dialogue_density=avg_dialogue,
            target_internal_thought_density=avg_internal,
            target_sensory_density=avg_sensory,
            target_emotional_density=avg_emotional,
            environment_range=env_range,
            action_range=action_range,
            dialogue_range=dialogue_range,
            internal_thought_range=internal_range,
            sensory_range=sensory_range,
            emotional_range=emotional_range,
        )

    def calculate_chapter_consistency(
        self,
        profile: ChapterDensityProfile,
        unified: UnifiedDensityProfile,
    ) -> float:
        """Calculate how consistent a chapter is with the unified density profile.

        Args:
            profile: Chapter's density profile
            unified: Target unified density profile

        Returns:
            Consistency score from 0 to 1
        """
        scores = []

        # Environment consistency
        in_range = unified.environment_range[0] <= profile.environment_density <= unified.environment_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.environment_density - unified.environment_range[0]),
                abs(profile.environment_density - unified.environment_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 5))

        # Action consistency
        in_range = unified.action_range[0] <= profile.action_density <= unified.action_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.action_density - unified.action_range[0]),
                abs(profile.action_density - unified.action_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 5))

        # Dialogue consistency
        in_range = unified.dialogue_range[0] <= profile.dialogue_density <= unified.dialogue_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.dialogue_density - unified.dialogue_range[0]),
                abs(profile.dialogue_density - unified.dialogue_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 5))

        # Internal thought consistency
        in_range = unified.internal_thought_range[0] <= profile.internal_thought_density <= unified.internal_thought_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.internal_thought_density - unified.internal_thought_range[0]),
                abs(profile.internal_thought_density - unified.internal_thought_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 5))

        # Sensory consistency
        in_range = unified.sensory_range[0] <= profile.sensory_density <= unified.sensory_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.sensory_density - unified.sensory_range[0]),
                abs(profile.sensory_density - unified.sensory_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 10))

        # Emotional consistency
        in_range = unified.emotional_range[0] <= profile.emotional_density <= unified.emotional_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.emotional_density - unified.emotional_range[0]),
                abs(profile.emotional_density - unified.emotional_range[1])
            )
            scores.append(max(0.0, 1.0 - distance * 10))

        return sum(scores) / len(scores)

    def analyze_novel_density(
        self,
        novel: Novel,
    ) -> DescriptionDensityAnalysis:
        """Perform comprehensive description density analysis on the novel.

        Args:
            novel: Novel to analyze

        Returns:
            DescriptionDensityAnalysis with complete analysis
        """
        # Collect all chapters
        all_chapters: list[Chapter] = []
        for volume in novel.volumes:
            all_chapters.extend(volume.chapters)

        all_chapters.sort(key=lambda c: c.number)

        if not all_chapters:
            return DescriptionDensityAnalysis(
                total_chapters_analyzed=0,
                unified_profile=UnifiedDensityProfile(),
            )

        # Analyze each chapter
        chapter_profiles: list[ChapterDensityProfile] = []
        for chapter in all_chapters:
            if chapter.content:
                profile = self.analyze_chapter_density(chapter)
                chapter_profiles.append(profile)

        # Create unified density profile
        unified = self.create_unified_density_profile(chapter_profiles)

        # Calculate consistency scores
        for profile in chapter_profiles:
            profile.density_score = self.calculate_chapter_consistency(profile, unified)

        # Detect shifts
        shifts = self.detect_density_shifts(chapter_profiles)

        # Find problematic chapters
        problematic = [(p.chapter_number, p.density_score) for p in chapter_profiles
                       if p.density_score < 0.8]
        problematic.sort(key=lambda x: x[1])

        # Calculate statistics
        total = len(chapter_profiles)
        total_words = sum(p.total_words for p in chapter_profiles)
        avg_words = total_words / total if total > 0 else 0

        # Calculate variance
        density_values = [p.density_score for p in chapter_profiles]
        density_variance = sum((v - (sum(density_values) / len(density_values))) ** 2
                              for v in density_values) / len(density_values) if density_values else 0

        # Calculate overall scores
        avg_density = sum(p.density_score for p in chapter_profiles) / total if total > 0 else 1.0
        avg_balance = sum(p.balance_score for p in chapter_profiles) / total if total > 0 else 1.0

        # Calculate uniformity (affected by shifts)
        if shifts:
            severity_weights = {
                "minor": 0.05,
                "moderate": 0.15,
                "severe": 0.30,
            }
            shift_penalty = sum(severity_weights.get(s.severity, 0.1) for s in shifts)
            uniformity = max(0.0, avg_density - shift_penalty * 0.3)
        else:
            uniformity = avg_density

        # Generate recommendations
        recommendations = self._generate_recommendations(chapter_profiles, shifts, unified)

        return DescriptionDensityAnalysis(
            total_chapters_analyzed=total,
            chapter_profiles=chapter_profiles,
            unified_profile=unified,
            detected_shifts=shifts,
            problematic_chapters=problematic,
            overall_density_score=avg_density,
            overall_balance_score=avg_balance,
            uniformity_score=uniformity,
            avg_chapter_words=avg_words,
            density_variance=density_variance,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        chapter_profiles: list[ChapterDensityProfile],
        shifts: list[DensityShift],
        unified: UnifiedDensityProfile,
    ) -> list[str]:
        """Generate recommendations for improving description density balance."""
        recommendations: list[str] = []

        if not chapter_profiles:
            return recommendations

        # Check for severe shifts
        severe_shifts = [s for s in shifts if s.severity == "severe"]
        if severe_shifts:
            recommendations.append(
                f"Address {len(severe_shifts)} severe density shifts between chapters "
                f"{severe_shifts[0].start_chapter}-{severe_shifts[-1].end_chapter}"
            )

        # Check for unbalanced chapters
        unbalanced = [p for p in chapter_profiles
                     if p.balance_status in [DescriptionBalanceStatus.UNEVEN,
                                             DescriptionBalanceStatus.SEVERELY_UNEVEN]]
        if unbalanced:
            recommendations.append(
                f"Revise {len(unbalanced)} chapters with uneven description density"
            )

        # Check for sparse chapters
        sparse_chapters = [p for p in chapter_profiles
                          if p.overall_density == DescriptionDensityLevel.SPARSE]
        if sparse_chapters:
            recommendations.append(
                f"Add more descriptive detail to {len(sparse_chapters)} sparse chapters: "
                f"{[p.chapter_number for p in sparse_chapters[:3]]}"
            )

        # Check for excessive chapters
        excessive_chapters = [p for p in chapter_profiles
                            if p.overall_density == DescriptionDensityLevel.EXCESSIVE]
        if excessive_chapters:
            recommendations.append(
                f"Trim excessive description in {len(excessive_chapters)} chapters: "
                f"{[p.chapter_number for p in excessive_chapters[:3]]}"
            )

        # Specific aspect recommendations
        aspect_issues = self._check_specific_aspects(chapter_profiles, unified)
        if aspect_issues:
            recommendations.extend(aspect_issues)

        # General recommendation
        if not recommendations:
            recommendations.append("Description density is well-balanced across the manuscript")
            recommendations.append("Minor refinements can further enhance reading experience")

        return recommendations

    def _check_specific_aspects(
        self,
        chapter_profiles: list[ChapterDensityProfile],
        unified: UnifiedDensityProfile,
    ) -> list[str]:
        """Check for specific aspect imbalances."""
        issues = []

        avg_env = sum(p.environment_density for p in chapter_profiles) / len(chapter_profiles)
        avg_action = sum(p.action_density for p in chapter_profiles) / len(chapter_profiles)
        avg_dialogue = sum(p.dialogue_density for p in chapter_profiles) / len(chapter_profiles)
        avg_internal = sum(p.internal_thought_density for p in chapter_profiles) / len(chapter_profiles)
        avg_sensory = sum(p.sensory_density for p in chapter_profiles) / len(chapter_profiles)
        avg_emotional = sum(p.emotional_density for p in chapter_profiles) / len(chapter_profiles)

        if avg_env < unified.environment_range[0]:
            issues.append("Consider adding more environment/scene descriptions")
        elif avg_env > unified.environment_range[1]:
            issues.append("Consider reducing environment descriptions to improve pacing")

        if avg_sensory < 0.05:
            issues.append("Add more sensory details to enhance immersion")

        if avg_emotional < 0.03:
            issues.append("Consider adding more emotional depth to scenes")

        if avg_internal < 0.05 and avg_dialogue > 0.40:
            issues.append("Balance dialogue-heavy scenes with more internal thoughts")

        return issues

    async def revise_chapter_for_density(
        self,
        chapter: Chapter,
        unified: UnifiedDensityProfile,
        target_score: float = 0.85,
    ) -> DescriptionDensityRevision:
        """Revise a chapter to align with the unified density profile.

        Args:
            chapter: Chapter to revise
            unified: Target unified density profile
            target_score: Target consistency score

        Returns:
            DescriptionDensityRevision with original and revised content
        """
        original = chapter.content
        before_profile = self.analyze_chapter_density(chapter)
        before_score = before_profile.density_score

        # Build revision prompt
        prompt = f"""请根据以下描写密度要求润色章节内容：

目标描写密度特征：
- 环境描写比例：{unified.target_environment_density:.1%}
- 动作描写比例：{unified.target_action_density:.1%}
- 对话比例：{unified.target_dialogue_density:.1%}
- 内心独白比例：{unified.target_internal_thought_density:.1%}
- 感官细节比例：{unified.target_sensory_density:.1%}
- 情感表达比例：{unified.target_emotional_density:.1%}

原文（第{chapter.number}章 {chapter.title}）：
{original}

要求：
1. 保持原文情节、角色对话和关键信息不变
2. 调整描写密度以符合目标比例
3. 确保各类型描写比例均衡
4. 避免过度描写或描写不足
5. 保持章节内部描写一致性
6. 不要添加或删除重要情节内容

直接输出润色后的内容，不要添加任何说明。"""

        revised = await self.ai_service.generate(prompt, temperature=0.3)
        revised = revised.strip()

        # Analyze revised content
        temp_chapter = Chapter(
            id=chapter.id,
            number=chapter.number,
            title=chapter.title,
            content=revised,
            word_count=len(revised),
        )
        after_profile = self.analyze_chapter_density(temp_chapter)
        after_score = self.calculate_chapter_consistency(after_profile, unified)

        # Determine changes made
        changes = []
        if abs(before_profile.environment_density - after_profile.environment_density) > 0.03:
            changes.append(f"环境描写: {before_profile.environment_density:.1%} → {after_profile.environment_density:.1%}")
        if abs(before_profile.action_density - after_profile.action_density) > 0.05:
            changes.append(f"动作描写: {before_profile.action_density:.1%} → {after_profile.action_density:.1%}")
        if abs(before_profile.dialogue_density - after_profile.dialogue_density) > 0.05:
            changes.append(f"对话比例: {before_profile.dialogue_density:.1%} → {after_profile.dialogue_density:.1%}")
        if abs(before_profile.internal_thought_density - after_profile.internal_thought_density) > 0.03:
            changes.append(f"内心独白: {before_profile.internal_thought_density:.1%} → {after_profile.internal_thought_density:.1%}")
        if abs(before_profile.sensory_density - after_profile.sensory_density) > 0.02:
            changes.append(f"感官细节: {before_profile.sensory_density:.1%} → {after_profile.sensory_density:.1%}")
        if abs(before_profile.emotional_density - after_profile.emotional_density) > 0.02:
            changes.append(f"情感表达: {before_profile.emotional_density:.1%} → {after_profile.emotional_density:.1%}")

        if not changes:
            changes.append("轻微描写密度调整")

        return DescriptionDensityRevision(
            original_content=original,
            revised_content=revised,
            chapter_number=chapter.number,
            changes_made=changes,
            before_score=before_score,
            after_score=after_score,
            issues_addressed=[i for i in before_profile.density_issues if before_score < target_score],
            issues_remaining=[],
        )

    def create_revision_plan(
        self,
        analysis: DescriptionDensityAnalysis,
        target_score: float = 0.80,
    ) -> DescriptionDensityPlan:
        """Create a plan for revising chapters to achieve density balance.

        Args:
            analysis: Description density analysis
            target_score: Target consistency score

        Returns:
            DescriptionDensityPlan with revision priorities
        """
        # Identify chapters that need revision
        to_revise: list[tuple[int, float]] = []
        for profile in analysis.chapter_profiles:
            if profile.density_score < target_score:
                to_revise.append((profile.chapter_number, profile.density_score))

        # Sort by priority (lowest score first)
        to_revise.sort(key=lambda x: x[1])

        chapters_to_revise = [c[0] for c in to_revise]
        priority_order = chapters_to_revise

        return DescriptionDensityPlan(
            target_profile=analysis.unified_profile,
            chapters_to_revise=chapters_to_revise,
            priority_order=priority_order,
            estimated_revisions=len(chapters_to_revise),
            ai_polishing_enabled=True,
        )

    def generate_density_report(
        self,
        analysis: DescriptionDensityAnalysis,
    ) -> DescriptionDensityReport:
        """Generate a comprehensive description density report.

        Args:
            analysis: Description density analysis

        Returns:
            DescriptionDensityReport with summary
        """
        # Build summary
        summary_parts = [
            f"分析了 {analysis.total_chapters_analyzed} 个章节的描写密度特征",
        ]

        if analysis.detected_shifts:
            summary_parts.append(f"发现 {len(analysis.detected_shifts)} 处描写密度变化")
        else:
            summary_parts.append("全书描写密度基本均衡")

        summary_parts.append(f"整体均匀度评分：{analysis.uniformity_score:.2f}")

        if analysis.problematic_chapters:
            worst = analysis.problematic_chapters[:2]
            summary_parts.append(
                f"需要关注章节：{', '.join(str(c) for c, _ in worst)}"
            )

        summary = "。".join(summary_parts) + "。"

        return DescriptionDensityReport(
            analysis=analysis,
            revision_plan=self.create_revision_plan(analysis),
            summary=summary,
        )

    def get_chapter_density_summary(
        self,
        profile: ChapterDensityProfile,
    ) -> str:
        """Get a human-readable summary of a chapter's description density.

        Args:
            profile: Chapter density profile

        Returns:
            Human-readable summary string
        """
        density_desc = profile.overall_density.value
        balance_desc = profile.balance_status.value

        return (
            f"第{profile.chapter_number}章「{profile.chapter_title}」："
            f"描写{density_desc}、"
            f"均衡性[{balance_desc}]、"
            f"环境{profile.environment_density:.0%}、"
            f"动作{profile.action_density:.0%}、"
            f"对话{profile.dialogue_density:.0%}、"
            f"内心{profile.internal_thought_density:.0%}"
        )

    def get_template(self, template_name: str) -> Optional[DescriptionDensityTemplate]:
        """Get a density template by name."""
        return self._templates.get(template_name)

    def get_all_templates(self) -> dict[str, DescriptionDensityTemplate]:
        """Get all available density templates."""
        return self._templates.copy()

    def apply_template(self, template_name: str) -> Optional[UnifiedDensityProfile]:
        """Apply a density template and return the resulting profile."""
        template = self._templates.get(template_name)
        if template is None:
            return None
        return template.to_unified_profile()
