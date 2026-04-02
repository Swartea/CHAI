"""Tone unification engine for maintaining consistent tone across the full manuscript."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.tone_unification import (
    ToneUnificationType,
    ToneShiftType,
    ToneShiftSeverity,
    ChapterToneProfile,
    ToneShift,
    UnifiedToneProfile,
    ToneUnificationAnalysis,
    ToneUnificationRevision,
    ToneUnificationPlan,
    ToneUnificationReport,
)
from chai.services import AIService


# Tone keywords for analysis
TONE_KEYWORDS = {
    # Emotional intensity markers (high intensity)
    "high_intensity": ["紧张", "危机", "生死", "绝望", "疯狂", "愤怒", "恐惧", "悲痛", "激烈", "高潮"],
    # Emotional intensity markers (low intensity)
    "low_intensity": ["平静", "安宁", "淡然", "平和", "舒缓", "轻松", "日常", "闲聊", "平常", "普通"],
    # Positive valence
    "positive": ["希望", "喜悦", "幸福", "爱", "温馨", "美好", "欢快", "兴奋", "期待", "感激"],
    # Negative valence
    "negative": ["绝望", "悲伤", "痛苦", "恐惧", "愤怒", "仇恨", "绝望", "黑暗", "阴沉", "冷酷"],
    # Epic tone
    "epic": ["史诗", "壮阔", "宏大", "伟大", "传奇", "英雄", "荣耀", "战场", "王国", "帝国"],
    # Dark tone
    "dark": ["黑暗", "阴影", "死亡", "血腥", "残酷", "邪恶", "深渊", "噩梦", "恐惧", "绝望"],
    # Lyrical tone
    "lyrical": ["优美", "诗意", "柔和", "温柔", "婉约", "如画", "梦幻", "轻纱", "月光", "微风"],
    # Romantic tone
    "romantic": ["爱", "情", "心", "吻", "恋", "相思", "甜蜜", "温柔", "依偎", "拥抱"],
    # Mysterious tone
    "mysterious": ["神秘", "谜", "未知", "诡异", "悬疑", "暗藏", "隐", "密", "不可知", "诡异"],
    # Tense/suspenseful tone
    "suspenseful": ["紧张", "悬念", "心跳", "屏息", "危机", "步步", "险象", "危机四伏", "一触即发", "千钧一发"],
    # Light tone
    "light": ["轻松", "愉快", "阳光", "欢笑", "幽默", "诙谐", "嬉戏", "调侃", "玩笑", "乐趣"],
    # Nostalgic tone
    "nostalgic": ["回忆", "过去", "怀念", "往事", "当年", "似水", "年华", "岁月", "往昔", "追忆"],
}


class ToneUnificationEngine:
    """Engine for unifying tone across the full manuscript."""

    def __init__(self, ai_service: AIService):
        """Initialize tone unification engine with AI service."""
        self.ai_service = ai_service

    def analyze_chapter_tone(self, chapter: Chapter) -> ChapterToneProfile:
        """Analyze the tone profile of a single chapter.

        Args:
            chapter: Chapter to analyze

        Returns:
            ChapterToneProfile with detected tone characteristics
        """
        content = chapter.content
        if not content:
            return ChapterToneProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title,
            )

        # Calculate basic metrics
        sentences = re.findall(r'[。！？.!?]', content)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        sentence_avg_length = len(content) / max(1, len(sentences))
        paragraph_avg_length = len(content) / max(1, len(paragraphs))

        # Count dialogue
        dialogues = re.findall(r'"[^"]*"', content)
        dialogue_ratio = sum(len(d) for d in dialogues) / max(1, len(content))

        # Analyze tone markers
        tone_markers: dict[str, float] = {}
        for tone_category, keywords in TONE_KEYWORDS.items():
            count = sum(content.count(kw) for kw in keywords)
            frequency = count / max(1, len(content)) * 1000  # per 1000 chars
            tone_markers[tone_category] = frequency

        # Calculate emotional intensity and valence
        high_intensity = tone_markers.get("high_intensity", 0)
        low_intensity = tone_markers.get("low_intensity", 0)
        total_intensity_markers = high_intensity + low_intensity

        if total_intensity_markers > 0:
            emotional_intensity = high_intensity / total_intensity_markers
        else:
            emotional_intensity = 0.5

        positive = tone_markers.get("positive", 0)
        negative = tone_markers.get("negative", 0)
        total_valence_markers = positive + negative

        if total_valence_markers > 0:
            emotional_valence = positive / total_valence_markers
        else:
            emotional_valence = 0.5

        # Determine primary atmosphere
        atmosphere_scores = {
            "epic": tone_markers.get("epic", 0),
            "dark": tone_markers.get("dark", 0),
            "lyrical": tone_markers.get("lyrical", 0),
            "romantic": tone_markers.get("romantic", 0),
            "mysterious": tone_markers.get("mysterious", 0),
            "suspenseful": tone_markers.get("suspenseful", 0),
            "light": tone_markers.get("light", 0),
            "nostalgic": tone_markers.get("nostalgic", 0),
        }

        primary_atmosphere = max(atmosphere_scores, key=atmosphere_scores.get) if any(atmosphere_scores.values()) else "neutral"

        # Detect atmosphere shifts within chapter (simplified)
        atmosphere_shifts: list[str] = []
        third_points = len(paragraphs) // 3
        if third_points > 0:
            sections = [
                content.split('\n\n')[0] if paragraphs else "",
                '\n\n'.join(paragraphs[third_points:2*third_points]) if len(paragraphs) > third_points else "",
                '\n\n'.join(paragraphs[-third_points:]) if len(paragraphs) > third_points else "",
            ]
            section_atmospheres = []
            for section in sections:
                section_scores = {}
                for tone, keywords in TONE_KEYWORDS.items():
                    count = sum(section.count(kw) for kw in keywords)
                    section_scores[tone] = count
                if section_scores and max(section_scores.values()) > 0:
                    section_atmospheres.append(max(section_scores, key=section_scores.get))

            if len(set(section_atmospheres)) > 1:
                atmosphere_shifts = section_atmospheres

        # Calculate vocabulary sophistication
        sophisticated_markers = ["然而", "因此", "虽然", "但是", "于是", "倘若", "既已", "何必", "莫非", "岂能"]
        sophisticated_count = sum(content.count(w) for w in sophisticated_markers)
        simple_markers = ["的", "了", "是", "在", "有", "我", "你", "他", "她", "它"]
        simple_count = sum(content.count(w) for w in simple_markers)

        if simple_count > 0:
            sophistication_ratio = sophisticated_count / simple_count
            vocabulary_sophistication = min(1.0, sophistication_ratio * 0.5)
        else:
            vocabulary_sophistication = 0.5

        return ChapterToneProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title,
            emotional_intensity=emotional_intensity,
            emotional_valence=emotional_valence,
            tone_markers=tone_markers,
            sentence_avg_length=sentence_avg_length,
            paragraph_avg_length=paragraph_avg_length,
            dialogue_ratio=dialogue_ratio,
            vocabulary_sophistication=vocabulary_sophistication,
            primary_atmosphere=primary_atmosphere,
            atmosphere_shifts=atmosphere_shifts,
        )

    def detect_tone_shifts(
        self,
        chapter_profiles: list[ChapterToneProfile],
    ) -> list[ToneShift]:
        """Detect tone shifts between chapters.

        Args:
            chapter_profiles: List of chapter tone profiles in order

        Returns:
            List of detected ToneShift objects
        """
        shifts: list[ToneShift] = []

        if len(chapter_profiles) < 2:
            return shifts

        for i in range(len(chapter_profiles) - 1):
            current = chapter_profiles[i]
            next_chapter = chapter_profiles[i + 1]

            # Calculate differences
            intensity_diff = abs(current.emotional_intensity - next_chapter.emotional_intensity)
            valence_diff = abs(current.emotional_valence - next_chapter.emotional_valence)
            sentence_diff = abs(current.sentence_avg_length - next_chapter.sentence_avg_length)
            dialogue_diff = abs(current.dialogue_ratio - next_chapter.dialogue_ratio)
            atmosphere_changed = current.primary_atmosphere != next_chapter.primary_atmosphere

            # Determine if significant shift occurred
            shift_magnitude = (intensity_diff + valence_diff + (sentence_diff / 50) + dialogue_diff) / 4

            if shift_magnitude > 0.15 or (atmosphere_changed and shift_magnitude > 0.1):
                # Determine shift type
                if shift_magnitude > 0.3:
                    shift_type = ToneShiftType.ABRUPT_SHIFT
                    severity = ToneShiftSeverity.MODERATE if shift_magnitude < 0.5 else ToneShiftSeverity.SEVERE
                elif atmosphere_changed:
                    shift_type = ToneShiftType.REGIONAL_DRIFT
                    severity = ToneShiftSeverity.MINOR if shift_magnitude < 0.2 else ToneShiftSeverity.MODERATE
                else:
                    shift_type = ToneShiftType.GRADUAL_SHIFT
                    severity = ToneShiftSeverity.NEGLIGIBLE if shift_magnitude < 0.2 else ToneShiftSeverity.MINOR

                # Determine affected aspects
                affected: list[ToneUnificationType] = []
                if intensity_diff > 0.1:
                    affected.append(ToneUnificationType.EMOTIONAL_TONE)
                if valence_diff > 0.1:
                    affected.append(ToneUnificationType.EMOTIONAL_TONE)
                if sentence_diff > 10:
                    affected.append(ToneUnificationType.NARRATIVE_TONE)
                if dialogue_diff > 0.1:
                    affected.append(ToneUnificationType.DIALOGUE_TONE)
                if atmosphere_changed:
                    affected.append(ToneUnificationType.ATMOSPHERIC_TONE)

                # Generate description
                if shift_type == ToneShiftType.ABRUPT_SHIFT:
                    desc = f"Chapter {current.chapter_number} to {next_chapter.chapter_number}: Abrupt tone shift detected"
                elif atmosphere_changed:
                    desc = f"Chapter {current.chapter_number} to {next_chapter.chapter_number}: Atmosphere shift from {current.primary_atmosphere} to {next_chapter.primary_atmosphere}"
                else:
                    desc = f"Chapter {current.chapter_number} to {next_chapter.chapter_number}: Gradual tone drift"

                shifts.append(ToneShift(
                    shift_id=str(uuid.uuid4())[:8],
                    start_chapter=current.chapter_number,
                    end_chapter=next_chapter.chapter_number,
                    shift_type=shift_type,
                    severity=severity,
                    description=desc,
                    magnitude=shift_magnitude,
                    likely_cause=self._analyze_shift_cause(current, next_chapter),
                    affected_aspects=affected,
                ))

        # Detect cyclical shifts (simplified - looks for repeated patterns)
        if len(shifts) >= 4:
            last_shifts = shifts[-4:]
            if all(s.shift_type == ToneShiftType.GRADUAL_SHIFT for s in last_shifts):
                shifts.append(ToneShift(
                    shift_id=str(uuid.uuid4())[:8],
                    start_chapter=last_shifts[0].start_chapter,
                    end_chapter=last_shifts[-1].end_chapter,
                    shift_type=ToneShiftType.CYCLICAL_SHIFT,
                    severity=ToneShiftSeverity.MODERATE,
                    description=f"Cyclical tone pattern detected from chapter {last_shifts[0].start_chapter} to {last_shifts[-1].end_chapter}",
                    magnitude=0.3,
                    likely_cause="Natural ebb and flow of narrative tension",
                    affected_aspects=[ToneUnificationType.EMOTIONAL_TONE],
                ))

        return shifts

    def _analyze_shift_cause(
        self,
        before: ChapterToneProfile,
        after: ChapterToneProfile,
    ) -> str:
        """Analyze the likely cause of a tone shift."""
        causes = []

        if abs(before.dialogue_ratio - after.dialogue_ratio) > 0.15:
            causes.append("dialogue ratio change")

        if abs(before.sentence_avg_length - after.sentence_avg_length) > 15:
            causes.append("sentence structure change")

        if before.primary_atmosphere != after.primary_atmosphere:
            causes.append(f"atmosphere shift to {after.primary_atmosphere}")

        intensity_change = after.emotional_intensity - before.emotional_intensity
        if abs(intensity_change) > 0.2:
            if intensity_change > 0:
                causes.append("emotional intensity increase")
            else:
                causes.append("emotional intensity decrease")

        valence_change = after.emotional_valence - before.emotional_valence
        if abs(valence_change) > 0.2:
            if valence_change > 0:
                causes.append("more positive tone")
            else:
                causes.append("more negative tone")

        return ", ".join(causes) if causes else "unknown cause"

    def create_unified_tone_profile(
        self,
        chapter_profiles: list[ChapterToneProfile],
    ) -> UnifiedToneProfile:
        """Create the target unified tone profile from chapter analyses.

        Args:
            chapter_profiles: List of chapter tone profiles

        Returns:
            UnifiedToneProfile with target values
        """
        if not chapter_profiles:
            return UnifiedToneProfile()

        # Calculate averages
        avg_intensity = sum(p.emotional_intensity for p in chapter_profiles) / len(chapter_profiles)
        avg_valence = sum(p.emotional_valence for p in chapter_profiles) / len(chapter_profiles)
        avg_sentence = sum(p.sentence_avg_length for p in chapter_profiles) / len(chapter_profiles)
        avg_paragraph = sum(p.paragraph_avg_length for p in chapter_profiles) / len(chapter_profiles)
        avg_dialogue = sum(p.dialogue_ratio for p in chapter_profiles) / len(chapter_profiles)
        avg_vocab = sum(p.vocabulary_sophistication for p in chapter_profiles) / len(chapter_profiles)

        # Count atmosphere frequencies
        atmosphere_counts: dict[str, int] = {}
        for profile in chapter_profiles:
            atm = profile.primary_atmosphere
            atmosphere_counts[atm] = atmosphere_counts.get(atm, 0) + 1

        dominant_atmosphere = max(atmosphere_counts, key=atmosphere_counts.get) if atmosphere_counts else "neutral"

        # Determine allowed atmospheres (those with significant presence)
        allowed_atmospheres = [atm for atm, count in atmosphere_counts.items()
                             if count >= len(chapter_profiles) * 0.1]

        # Calculate variance for ranges
        intensity_variance = sum((p.emotional_intensity - avg_intensity) ** 2 for p in chapter_profiles) / len(chapter_profiles)
        valence_variance = sum((p.emotional_valence - avg_valence) ** 2 for p in chapter_profiles) / len(chapter_profiles)

        # Create ranges (mean ± 1.5 std dev, clamped to 0-1)
        import math
        intensity_std = math.sqrt(intensity_variance)
        valence_std = math.sqrt(valence_variance)

        intensity_range = (
            max(0.0, avg_intensity - 1.5 * intensity_std),
            min(1.0, avg_intensity + 1.5 * intensity_std),
        )
        valence_range = (
            max(0.0, avg_valence - 1.5 * valence_std),
            min(1.0, avg_valence + 1.5 * valence_std),
        )

        # Sentence and paragraph ranges
        sentence_variance = sum((p.sentence_avg_length - avg_sentence) ** 2 for p in chapter_profiles) / len(chapter_profiles)
        sentence_std = math.sqrt(sentence_variance)
        sentence_range = (
            max(10.0, avg_sentence - 1.5 * sentence_std),
            avg_sentence + 1.5 * sentence_std,
        )

        paragraph_variance = sum((p.paragraph_avg_length - avg_paragraph) ** 2 for p in chapter_profiles) / len(chapter_profiles)
        paragraph_std = math.sqrt(paragraph_variance)
        paragraph_range = (
            max(50.0, avg_paragraph - 1.5 * paragraph_std),
            avg_paragraph + 1.5 * paragraph_std,
        )

        dialogue_variance = sum((p.dialogue_ratio - avg_dialogue) ** 2 for p in chapter_profiles) / len(chapter_profiles)
        dialogue_std = math.sqrt(dialogue_variance)
        dialogue_range = (
            max(0.1, avg_dialogue - 1.5 * dialogue_std),
            min(0.6, avg_dialogue + 1.5 * dialogue_std),
        )

        return UnifiedToneProfile(
            target_emotional_intensity=avg_intensity,
            target_emotional_valence=avg_valence,
            intensity_range=intensity_range,
            valence_range=valence_range,
            target_sentence_avg_length=avg_sentence,
            sentence_length_range=sentence_range,
            target_paragraph_avg_length=avg_paragraph,
            paragraph_length_range=paragraph_range,
            target_dialogue_ratio=avg_dialogue,
            dialogue_ratio_range=dialogue_range,
            target_vocabulary_sophistication=avg_vocab,
            target_atmosphere=dominant_atmosphere,
            allowed_atmospheres=allowed_atmospheres,
        )

    def calculate_chapter_consistency(
        self,
        profile: ChapterToneProfile,
        unified: UnifiedToneProfile,
    ) -> float:
        """Calculate how consistent a chapter is with the unified tone.

        Args:
            profile: Chapter's tone profile
            unified: Target unified tone profile

        Returns:
            Consistency score from 0 to 1
        """
        scores = []

        # Intensity consistency
        in_range = unified.intensity_range[0] <= profile.emotional_intensity <= unified.intensity_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.emotional_intensity - unified.intensity_range[0]),
                abs(profile.emotional_intensity - unified.intensity_range[1])
            )
            scores.append(max(0.0, 1.0 - distance))

        # Valence consistency
        in_range = unified.valence_range[0] <= profile.emotional_valence <= unified.valence_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.emotional_valence - unified.valence_range[0]),
                abs(profile.emotional_valence - unified.valence_range[1])
            )
            scores.append(max(0.0, 1.0 - distance))

        # Sentence length consistency
        in_range = unified.sentence_length_range[0] <= profile.sentence_avg_length <= unified.sentence_length_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.sentence_avg_length - unified.sentence_length_range[0]),
                abs(profile.sentence_avg_length - unified.sentence_length_range[1])
            ) / 20  # normalize
            scores.append(max(0.0, 1.0 - distance))

        # Dialogue ratio consistency
        in_range = unified.dialogue_ratio_range[0] <= profile.dialogue_ratio <= unified.dialogue_ratio_range[1]
        if in_range:
            scores.append(1.0)
        else:
            distance = min(
                abs(profile.dialogue_ratio - unified.dialogue_ratio_range[0]),
                abs(profile.dialogue_ratio - unified.dialogue_ratio_range[1])
            ) * 3  # normalize
            scores.append(max(0.0, 1.0 - distance))

        # Atmosphere consistency
        if profile.primary_atmosphere in unified.allowed_atmospheres:
            scores.append(1.0)
        else:
            scores.append(0.5)

        return sum(scores) / len(scores)

    def analyze_novel_tone(
        self,
        novel: Novel,
    ) -> ToneUnificationAnalysis:
        """Perform comprehensive tone unification analysis on the novel.

        Args:
            novel: Novel to analyze

        Returns:
            ToneUnificationAnalysis with complete analysis
        """
        # Collect all chapters
        all_chapters: list[Chapter] = []
        for volume in novel.volumes:
            all_chapters.extend(volume.chapters)

        all_chapters.sort(key=lambda c: c.number)

        if not all_chapters:
            return ToneUnificationAnalysis(
                total_chapters_analyzed=0,
                unified_tone_profile=UnifiedToneProfile(),
            )

        # Analyze each chapter
        chapter_profiles: list[ChapterToneProfile] = []
        for chapter in all_chapters:
            if chapter.content:
                profile = self.analyze_chapter_tone(chapter)
                chapter_profiles.append(profile)

        # Create unified tone profile
        unified = self.create_unified_tone_profile(chapter_profiles)

        # Calculate consistency scores
        for profile in chapter_profiles:
            profile.consistency_score = self.calculate_chapter_consistency(profile, unified)

        # Detect shifts
        shifts = self.detect_tone_shifts(chapter_profiles)

        # Find problematic chapters
        problematic = [(p.chapter_number, p.consistency_score) for p in chapter_profiles
                       if p.consistency_score < 0.8]
        problematic.sort(key=lambda x: x[1])

        # Calculate statistics
        total = len(chapter_profiles)
        chapters_with_shifts = len(set(s.shift_id for s in shifts))
        average_consistency = sum(p.consistency_score for p in chapter_profiles) / total if total > 0 else 1.0

        # Calculate overall uniformity score
        if shifts:
            severity_weights = {
                ToneShiftSeverity.NEGLIGIBLE: 0.05,
                ToneShiftSeverity.MINOR: 0.1,
                ToneShiftSeverity.MODERATE: 0.2,
                ToneShiftSeverity.SEVERE: 0.4,
                ToneShiftSeverity.CRITICAL: 0.6,
            }
            shift_penalty = sum(severity_weights.get(s.severity, 0.1) for s in shifts)
            overall_uniformity = max(0.0, average_consistency - shift_penalty * 0.3)
        else:
            overall_uniformity = average_consistency

        # Generate recommendations
        recommendations = self._generate_recommendations(chapter_profiles, shifts, unified)

        return ToneUnificationAnalysis(
            overall_uniformity_score=overall_uniformity,
            chapter_profiles=chapter_profiles,
            unified_tone_profile=unified,
            detected_shifts=shifts,
            problematic_chapters=problematic,
            total_chapters_analyzed=total,
            chapters_with_shifts=chapters_with_shifts,
            average_consistency=average_consistency,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        chapter_profiles: list[ChapterToneProfile],
        shifts: list[ToneShift],
        unified: UnifiedToneProfile,
    ) -> list[str]:
        """Generate recommendations for improving tone uniformity."""
        recommendations: list[str] = []

        if not chapter_profiles:
            return recommendations

        # Check for severe shifts
        severe_shifts = [s for s in shifts if s.severity in [ToneShiftSeverity.SEVERE, ToneShiftSeverity.CRITICAL]]
        if severe_shifts:
            recommendations.append(
                f"Address {len(severe_shifts)} severe tone shifts between chapters "
                f"{severe_shifts[0].start_chapter}-{severe_shifts[-1].end_chapter}"
            )

        # Check for patterns
        if any(s.shift_type == ToneShiftType.CYCLICAL_SHIFT for s in shifts):
            recommendations.append(
                "Consider smoothing out cyclical tone patterns for more consistent reading experience"
            )

        # Check atmosphere issues
        dominant = unified.target_atmosphere
        non_dominant = [p for p in chapter_profiles if p.primary_atmosphere != dominant]
        if non_dominant:
            recommendations.append(
                f"Revise {len(non_dominant)} chapters to align atmosphere with dominant tone ({dominant})"
            )

        # Check consistency outliers
        low_consistency = [p for p in chapter_profiles if p.consistency_score < 0.7]
        if low_consistency:
            recommendations.append(
                f"Focus revision on chapters with lowest consistency: "
                f"{[p.chapter_number for p in low_consistency[:3]]}"
            )

        # General recommendations
        if not recommendations:
            recommendations.append("Tone is generally consistent across the manuscript")
            recommendations.append("Minor polish revisions can further enhance uniformity")

        return recommendations

    async def revise_chapter_for_tone(
        self,
        chapter: Chapter,
        unified: UnifiedToneProfile,
        target_score: float = 0.9,
    ) -> ToneUnificationRevision:
        """Revise a chapter to align with the unified tone.

        Args:
            chapter: Chapter to revise
            unified: Target unified tone profile
            target_score: Target consistency score

        Returns:
            ToneUnificationRevision with original and revised content
        """
        original = chapter.content
        before_profile = self.analyze_chapter_tone(chapter)
        before_score = before_profile.consistency_score

        # Build revision prompt
        prompt = f"""请根据以下语调统一要求润色章节内容：

目标语调特征：
- 情感强度目标：{unified.target_emotional_intensity:.2f}（范围：{unified.intensity_range[0]:.2f}-{unified.intensity_range[1]:.2f}）
- 情感valence目标：{unified.target_emotional_valence:.2f}（范围：{unified.valence_range[0]:.2f}-{unified.valence_range[1]:.2f}）
- 平均句子长度：{unified.target_sentence_avg_length:.1f}字符（范围：{unified.sentence_length_range[0]:.1f}-{unified.sentence_length_range[1]:.1f}）
- 对话比例：{unified.target_dialogue_ratio:.0%}（范围：{unified.dialogue_ratio_range[0]:.0%}-{unified.dialogue_ratio_range[1]:.0%}）
- 主要氛围：{unified.target_atmosphere}

原文（第{chapter.number}章 {chapter.title}）：
{original}

要求：
1. 保持原文情节、角色对话和关键信息不变
2. 调整叙述语调以符合目标特征
3. 确保与全书语调统一
4. 保持章节内部氛围一致
5. 不要添加或删除重要情节内容

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
        after_profile = self.analyze_chapter_tone(temp_chapter)
        after_score = self.calculate_chapter_consistency(after_profile, unified)

        # Determine changes made
        changes = []
        if abs(before_profile.emotional_intensity - after_profile.emotional_intensity) > 0.1:
            changes.append("Adjusted emotional intensity")
        if abs(before_profile.emotional_valence - after_profile.emotional_valence) > 0.1:
            changes.append("Adjusted emotional valence")
        if abs(before_profile.sentence_avg_length - after_profile.sentence_avg_length) > 5:
            changes.append("Adjusted sentence structure")
        if before_profile.primary_atmosphere != after_profile.primary_atmosphere:
            changes.append(f"Changed atmosphere from {before_profile.primary_atmosphere} to {after_profile.primary_atmosphere}")
        if not changes:
            changes.append("Minor tonal refinements")

        return ToneUnificationRevision(
            original_content=original,
            revised_content=revised,
            chapter_number=chapter.number,
            changes_made=changes,
            before_score=before_score,
            after_score=after_score,
            issues_addressed=[s.description for s in [before_profile] if before_score < target_score],
            issues_remaining=[],
        )

    def create_revision_plan(
        self,
        analysis: ToneUnificationAnalysis,
        target_score: float = 0.85,
    ) -> ToneUnificationPlan:
        """Create a plan for revising chapters to achieve tone uniformity.

        Args:
            analysis: Tone unification analysis
            target_score: Target consistency score

        Returns:
            ToneUnificationPlan with revision priorities
        """
        # Identify chapters that need revision
        to_revise: list[tuple[int, float]] = []
        for profile in analysis.chapter_profiles:
            if profile.consistency_score < target_score:
                to_revise.append((profile.chapter_number, profile.consistency_score))

        # Sort by priority (lowest score first)
        to_revise.sort(key=lambda x: x[1])

        chapters_to_revise = [c[0] for c in to_revise]
        priority_order = chapters_to_revise

        return ToneUnificationPlan(
            target_profile=analysis.unified_tone_profile,
            chapters_to_revise=chapters_to_revise,
            priority_order=priority_order,
            estimated_revisions=len(chapters_to_revise),
            ai_polishing_enabled=True,
        )

    def generate_unification_report(
        self,
        analysis: ToneUnificationAnalysis,
    ) -> ToneUnificationReport:
        """Generate a comprehensive tone unification report.

        Args:
            analysis: Tone unification analysis

        Returns:
            ToneUnificationReport with summary
        """
        # Build summary
        summary_parts = [
            f"分析了 {analysis.total_chapters_analyzed} 个章节的语调特征",
        ]

        if analysis.detected_shifts:
            summary_parts.append(f"发现 {len(analysis.detected_shifts)} 处语调变化")
        else:
            summary_parts.append("全书语调基本统一")

        summary_parts.append(f"整体统一性评分：{analysis.overall_uniformity_score:.2f}")

        if analysis.problematic_chapters:
            worst = analysis.problematic_chapters[:2]
            summary_parts.append(
                f"需要关注章节：{', '.join(str(c) for c, _ in worst)}"
            )

        summary = "。".join(summary_parts) + "。"

        return ToneUnificationReport(
            analysis=analysis,
            revision_plan=self.create_revision_plan(analysis),
            summary=summary,
        )

    def get_chapter_tone_summary(
        self,
        profile: ChapterToneProfile,
    ) -> str:
        """Get a human-readable summary of a chapter's tone.

        Args:
            profile: Chapter tone profile

        Returns:
            Human-readable summary string
        """
        intensity_desc = "高强度" if profile.emotional_intensity > 0.7 else "中等强度" if profile.emotional_intensity > 0.4 else "低强度"
        valence_desc = "正面" if profile.emotional_valence > 0.6 else "负面" if profile.emotional_valence < 0.4 else "中性"

        return (
            f"第{profile.chapter_number}章「{profile.chapter_title}」："
            f"语调{intensity_desc}、情感{valence_desc}、"
            f"氛围[{profile.primary_atmosphere}]、"
            f"一致性评分{profile.consistency_score:.2f}"
        )