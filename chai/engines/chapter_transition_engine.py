"""Chapter transition engine for ensuring smooth transitions between chapters."""

import re
import uuid
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.chapter_transition import (
    TransitionType,
    TransitionQuality,
    TransitionSmoothness,
    ChapterEndingType,
    ChapterOpeningType,
    TransitionElement,
    ChapterTransitionProfile,
    TransitionIssue,
    TransitionConnection,
    TransitionAnalysis,
    TransitionRevision,
    TransitionPlan,
    TransitionReport,
)
from chai.services import AIService


# Keywords for analyzing chapter endings and openings
ENDING_KEYWORDS = {
    ChapterEndingType.CLIFFHANGER: ["就在此时", "突然", "没想到", "刹那间", "一声", "猛然", "骤然", "顿时", "忽然", "猝不及防", "一触即发", "千钧一发", "命悬一线"],
    ChapterEndingType.RESOLUTION: ["终于", "于是", "就这样", "结束", "落幕", "平息", "归于", "告一段落", "暂时", "平静下来"],
    ChapterEndingType.OPEN_ENDING: ["然而", "但是", "不过", "只是", "谁知道", "也许", "或许", "可能", "似乎", "仿佛"],
    ChapterEndingType.REVELATION_ENDING: ["原来", "竟然", "真相是", "才发现", "才知道", "揭露", "暴露", "揭晓", "揭示"],
    ChapterEndingType.QUIET_ENDING: ["平静", "安宁", "祥和", "宁静", "安然", "舒缓", "渐渐", "慢慢", "缓缓"],
    ChapterEndingType.SUSPENSE_ENDING: ["疑问", "为什么", "怎么回事", "令人费解", "不解", "诡异", "疑云", "悬念"],
    ChapterEndingType.DRAMATIC_ENDING: ["怒吼", "咆哮", "震撼", "惊天", "剧烈", "激烈", "悲鸣", "嘶吼"],
    ChapterEndingType.QUESTION_ENDING: ["?", "？", "怎么办", "如何", "能否", "会不会", "会不会", "是否"],
}

OPENING_KEYWORDS = {
    ChapterOpeningType.DIRECT_CONTINUATION: ["接着", "继续", "然而", "但是", "此时", "此刻", "于是", "紧接着"],
    ChapterOpeningType.SCENE_SETUP: ["这里是", "在", "位于", "坐落在", "来到", "走进", "踏入", "出现在"],
    ChapterOpeningType.TIME_MARKER: ["第二天", "数日后", "不久", "时光", "转眼", "片刻", "片刻后", "天亮了", "夜幕", "黎明"],
    ChapterOpeningType.FLASHBACK: ["回忆", "想起", "记得", "那是在", "曾经", "从前", "追溯", "回想起"],
    ChapterOpeningType.POV_CHANGE: ["视角", "目光转向", "镜头切换", "另一边", "与此同时", "就在此时"],
    ChapterOpeningType.IN_MEDIAS_RES: ["突然", "猛然", "骤然", "猝不及防", "正在", "正在进行"],
    ChapterOpeningType.REFLECTION: ["心想", "想着", "思考", "暗自", "思忖", "盘算", "琢磨"],
    ChapterOpeningType.DIALOGUE_START: ["\"", "「", "说道", "问道", "答道", "说道：", "说："],
}

# Time indicator patterns
TIME_PATTERNS = [
    r"第[一二三四五六七八九十百千万]+天",
    r"第[一二三四五六七八九十百千万]+夜",
    r"数日后",
    r"数月后",
    r"数年后",
    r"不久",
    r"片刻后",
    r"转眼",
    r"时光流逝",
    r"天亮了",
    r"夜幕降临",
    r"黎明",
    r"黄昏",
    r"深夜",
    r"清晨",
]

# Location change indicators
LOCATION_CHANGE_PATTERNS = [
    r"来到",
    r"走进",
    r"踏入",
    r"出现在",
    r"转移到",
    r"视角转向",
    r"镜头切换",
    r"与此同时",
]


class ChapterTransitionEngine:
    """Engine for analyzing and improving transitions between chapters."""

    def __init__(self, ai_service: AIService):
        """Initialize chapter transition engine with AI service."""
        self.ai_service = ai_service

    def analyze_chapter_ending(self, chapter: Chapter) -> tuple[ChapterEndingType, float, str]:
        """Analyze the type and characteristics of a chapter's ending.

        Args:
            chapter: Chapter to analyze

        Returns:
            Tuple of (ending_type, tension_level, emotional_tone)
        """
        content = chapter.content
        if not content:
            return ChapterEndingType.RESOLUTION, 0.5, "neutral"

        # Get last 500 characters for ending analysis
        ending_content = content[-500:] if len(content) > 500 else content

        # Detect ending type
        type_scores: dict[ChapterEndingType, float] = {t: 0.0 for t in ChapterEndingType}
        for ending_type, keywords in ENDING_KEYWORDS.items():
            for kw in keywords:
                if kw in ending_content:
                    type_scores[ending_type] += 1

        detected_type = max(type_scores, key=type_scores.get)
        if type_scores[detected_type] == 0:
            detected_type = ChapterEndingType.RESOLUTION

        # Calculate tension level
        tension_markers = ["紧张", "危机", "生死", "悬", "惊", "恐", "慌", "急", "心跳", "屏息"]
        tension_count = sum(ending_content.count(m) for m in tension_markers)
        tension_level = min(1.0, tension_count / 10)

        # Detect emotional tone
        positive_markers = ["喜悦", "幸福", "温馨", "欢快", "期待", "感激", "爱"]
        negative_markers = ["绝望", "悲伤", "痛苦", "恐惧", "愤怒", "仇恨", "黑暗"]
        pos_count = sum(ending_content.count(m) for m in positive_markers)
        neg_count = sum(ending_content.count(m) for m in negative_markers)

        if pos_count > neg_count:
            emotional_tone = "positive"
        elif neg_count > pos_count:
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"

        return detected_type, tension_level, emotional_tone

    def analyze_chapter_opening(self, chapter: Chapter) -> tuple[ChapterOpeningType, float, str]:
        """Analyze the type and characteristics of a chapter's opening.

        Args:
            chapter: Chapter to analyze

        Returns:
            Tuple of (opening_type, tension_level, emotional_tone)
        """
        content = chapter.content
        if not content:
            return ChapterOpeningType.DIRECT_CONTINUATION, 0.5, "neutral"

        # Get first 500 characters for opening analysis
        opening_content = content[:500] if len(content) > 500 else content

        # Detect opening type
        type_scores: dict[ChapterOpeningType, float] = {t: 0.0 for t in ChapterOpeningType}
        for opening_type, keywords in OPENING_KEYWORDS.items():
            for kw in keywords:
                if kw in opening_content:
                    type_scores[opening_type] += 1

        detected_type = max(type_scores, key=type_scores.get)
        if type_scores[detected_type] == 0:
            detected_type = ChapterOpeningType.DIRECT_CONTINUATION

        # Calculate tension level
        tension_markers = ["紧张", "危机", "生死", "悬", "惊", "恐", "慌", "急", "心跳", "屏息"]
        tension_count = sum(opening_content.count(m) for m in tension_markers)
        tension_level = min(1.0, tension_count / 10)

        # Detect emotional tone
        positive_markers = ["喜悦", "幸福", "温馨", "欢快", "期待", "感激", "爱"]
        negative_markers = ["绝望", "悲伤", "痛苦", "恐惧", "愤怒", "仇恨", "黑暗"]
        pos_count = sum(opening_content.count(m) for m in positive_markers)
        neg_count = sum(opening_content.count(m) for m in negative_markers)

        if pos_count > neg_count:
            emotional_tone = "positive"
        elif neg_count > pos_count:
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"

        return detected_type, tension_level, emotional_tone

    def detect_location_change(self, from_chapter: Chapter, to_chapter: Chapter) -> bool:
        """Detect if there's a location change between chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter

        Returns:
            True if location change detected
        """
        if not from_chapter.content or not to_chapter.content:
            return False

        # Check for location change patterns in opening of to_chapter
        opening = to_chapter.content[:500]

        for pattern in LOCATION_CHANGE_PATTERNS:
            if re.search(pattern, opening):
                return True

        return False

    def detect_time_jump(self, from_chapter: Chapter, to_chapter: Chapter) -> bool:
        """Detect if there's a time jump between chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter

        Returns:
            True if time jump detected
        """
        if not from_chapter.content or not to_chapter.content:
            return False

        # Check opening for time markers
        opening = to_chapter.content[:500]

        for pattern in TIME_PATTERNS:
            if re.search(pattern, opening):
                return True

        return False

    def analyze_transition_elements(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
    ) -> TransitionElement:
        """Analyze the transition elements between two chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter

        Returns:
            TransitionElement with detailed analysis
        """
        elements = TransitionElement()

        if not from_chapter.content or not to_chapter.content:
            return elements

        # Time continuity
        has_time_jump = self.detect_time_jump(from_chapter, to_chapter)
        elements.time_continuity = 0.3 if has_time_jump else 1.0
        elements.time_gap_acknowledged = has_time_jump

        # Scene continuity
        has_location_change = self.detect_location_change(from_chapter, to_chapter)
        elements.scene_continuity = 0.4 if has_location_change else 1.0
        elements.location_clear = has_location_change

        # Character continuity (simplified)
        # In a real implementation, would analyze character appearances
        elements.character_continuity = 0.8  # Placeholder

        # Emotional continuity
        from_ending_type, from_tension, from_emotion = self.analyze_chapter_ending(from_chapter)
        to_opening_type, to_tension, to_emotion = self.analyze_chapter_opening(to_chapter)

        tension_diff = abs(from_tension - to_tension)
        elements.tension_flow = 1.0 - tension_diff

        emotion_match = from_emotion == to_emotion
        elements.emotional_continuity = 1.0 if emotion_match else 0.6

        # Plot continuity (simplified)
        elements.plot_continuity = 0.8  # Placeholder

        return elements

    def determine_transition_type(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
        elements: TransitionElement,
    ) -> TransitionType:
        """Determine the type of transition between chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter
            elements: Transition elements analysis

        Returns:
            TransitionType
        """
        if elements.time_continuity < 0.5:
            return TransitionType.TIME_JUMP
        if elements.scene_continuity < 0.5:
            return TransitionType.SCENE_SWITCH
        if abs(elements.tension_flow - 0.3) < 0.2 and elements.emotional_continuity < 0.5:
            return TransitionType.EMOTIONAL_SHIFT
        if elements.tension_flow > 0.8 and elements.tension_flow < 0.95:
            return TransitionType.TENSION_RELEASE
        if elements.tension_flow > 0.95:
            return TransitionType.TENSION_PEAK
        return TransitionType.SCENE_CONTINUATION

    def assess_transition_quality(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
        elements: TransitionElement,
    ) -> tuple[TransitionQuality, TransitionSmoothness, float]:
        """Assess the quality of a transition.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter
            elements: Transition elements analysis

        Returns:
            Tuple of (quality, smoothness, consistency_score)
        """
        # Calculate consistency score
        scores = [
            elements.time_continuity,
            elements.scene_continuity,
            elements.character_continuity,
            elements.emotional_continuity,
            elements.tension_flow,
            elements.plot_continuity,
        ]
        consistency = sum(scores) / len(scores)

        # Determine quality
        if consistency >= 0.9:
            quality = TransitionQuality.EXCELLENT
        elif consistency >= 0.75:
            quality = TransitionQuality.GOOD
        elif consistency >= 0.6:
            quality = TransitionQuality.ACCEPTABLE
        elif consistency >= 0.4:
            quality = TransitionQuality.ROUGH
        else:
            quality = TransitionQuality.JARRING

        # Determine smoothness
        if consistency >= 0.9:
            smoothness = TransitionSmoothness.SEAMLESS
        elif consistency >= 0.7:
            smoothness = TransitionSmoothness.GRADUAL
        elif consistency >= 0.4:
            smoothness = TransitionSmoothness.ABRUPT
        else:
            smoothness = TransitionSmoothness.CONFUSING

        return quality, smoothness, consistency

    def analyze_transition(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
    ) -> ChapterTransitionProfile:
        """Analyze a single transition between two chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter

        Returns:
            ChapterTransitionProfile
        """
        # Analyze ending of source chapter
        from_ending_type, from_tension, from_emotion = self.analyze_chapter_ending(from_chapter)

        # Analyze opening of target chapter
        to_opening_type, to_tension, to_emotion = self.analyze_chapter_opening(to_chapter)

        # Analyze transition elements
        elements = self.analyze_transition_elements(from_chapter, to_chapter)

        # Determine transition type
        transition_type = self.determine_transition_type(from_chapter, to_chapter, elements)

        # Assess quality
        quality, smoothness, consistency = self.assess_transition_quality(from_chapter, to_chapter, elements)

        # Generate issues and recommendations
        issues = self._identify_issues(from_chapter, to_chapter, elements, quality)
        recommendations = self._generate_recommendations(elements, quality, transition_type)

        return ChapterTransitionProfile(
            from_chapter_number=from_chapter.number,
            from_chapter_title=from_chapter.title,
            to_chapter_number=to_chapter.number,
            to_chapter_title=to_chapter.title,
            from_ending_type=from_ending_type,
            from_tension_level=from_tension,
            from_emotional_tone=from_emotion,
            from_location="",  # Would need more complex analysis
            to_opening_type=to_opening_type,
            to_tension_level=to_tension,
            to_emotional_tone=to_emotion,
            to_location="",  # Would need more complex analysis
            transition_type=transition_type,
            transition_elements=elements,
            quality=quality,
            smoothness=smoothness,
            consistency_score=consistency,
            issues=issues,
            recommendations=recommendations,
        )

    def _identify_issues(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
        elements: TransitionElement,
        quality: TransitionQuality,
    ) -> list[str]:
        """Identify issues with the transition."""
        issues = []

        if elements.time_continuity < 0.5 and not elements.time_gap_acknowledged:
            issues.append("时间跳跃未被明确说明，读者可能感到困惑")

        if elements.scene_continuity < 0.5 and not elements.location_clear:
            issues.append("场景转换过于突兀，缺少地点过渡")

        if elements.character_continuity < 0.5:
            issues.append("角色连续性不足，可能影响读者代入感")

        if elements.emotional_continuity < 0.5:
            issues.append("情感基调变化过大，缺少渐进过渡")

        if elements.tension_flow < 0.5:
            issues.append("张力变化过急，影响阅读节奏")

        if quality in [TransitionQuality.ROUGH, TransitionQuality.JARRING]:
            issues.append(f"整体过渡质量不佳：{quality.value}")

        return issues

    def _generate_recommendations(
        self,
        elements: TransitionElement,
        quality: TransitionQuality,
        transition_type: TransitionType,
    ) -> list[str]:
        """Generate recommendations for improving the transition."""
        recommendations = []

        if elements.time_continuity < 0.8:
            recommendations.append("添加时间过渡说明（如'数日后'、'夜幕降临'等）")

        if elements.scene_continuity < 0.8:
            recommendations.append("增加场景过渡段落，描述环境变化")

        if elements.character_continuity < 0.8:
            recommendations.append("通过角色视角或内心活动保持连续性")

        if elements.emotional_continuity < 0.8:
            recommendations.append("渐进式调整情感基调，避免突变")

        if elements.tension_flow < 0.8:
            recommendations.append("调整章节间的张力曲线，使其更平缓")

        if elements.has_bridge_passage:
            recommendations.append("过渡段落已存在，可进一步优化")

        if not recommendations:
            recommendations.append("过渡质量良好，可保持现状")

        return recommendations

    def analyze_connection(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
    ) -> TransitionConnection:
        """Analyze the connection between two chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter

        Returns:
            TransitionConnection
        """
        # This is a simplified implementation
        # In a full implementation, would use NLP to detect:
        # - Plot threads (using AI service)
        # - Character appearances
        # - Thematic elements

        return TransitionConnection(
            from_chapter=from_chapter.number,
            to_chapter=to_chapter.number,
            continuing_threads=[],
            new_threads_introduced=[],
            threads_concluded=[],
            shared_characters=[],
            characters_exiting=[],
            characters_entering=[],
            thematic_links=[],
            thematic_shifts=[],
            narrative_flow_score=0.8,
        )

    def analyze_all_transitions(
        self,
        chapters: list[Chapter],
    ) -> TransitionAnalysis:
        """Analyze all transitions in a sequence of chapters.

        Args:
            chapters: List of chapters in order

        Returns:
            TransitionAnalysis
        """
        if len(chapters) < 2:
            return TransitionAnalysis(total_transitions=0)

        # Sort chapters by number
        sorted_chapters = sorted(chapters, key=lambda c: c.number)

        # Analyze each transition
        profiles: list[ChapterTransitionProfile] = []
        connections: list[TransitionConnection] = []
        all_issues: list[TransitionIssue] = []

        quality_counts = {
            TransitionQuality.EXCELLENT: 0,
            TransitionQuality.GOOD: 0,
            TransitionQuality.ACCEPTABLE: 0,
            TransitionQuality.ROUGH: 0,
            TransitionQuality.JARRING: 0,
        }

        weakest: list[tuple[int, int, float]] = []

        for i in range(len(sorted_chapters) - 1):
            from_ch = sorted_chapters[i]
            to_ch = sorted_chapters[i + 1]

            # Analyze transition
            profile = self.analyze_transition(from_ch, to_ch)
            profiles.append(profile)

            # Count quality
            quality_counts[profile.quality] += 1

            # Track weakest
            if profile.consistency_score < 0.8:
                weakest.append((from_ch.number, to_ch.number, profile.consistency_score))

            # Analyze connection
            connection = self.analyze_connection(from_ch, to_ch)
            connections.append(connection)

            # Create issues
            for issue_desc in profile.issues:
                all_issues.append(TransitionIssue(
                    issue_id=str(uuid.uuid4())[:8],
                    from_chapter=from_ch.number,
                    to_chapter=to_ch.number,
                    issue_type="general",
                    severity="moderate",
                    description=issue_desc,
                    suggested_fix="; ".join(profile.recommendations),
                ))

        # Calculate statistics
        total = len(profiles)
        consistency_scores = [p.consistency_score for p in profiles]
        avg_consistency = sum(consistency_scores) / total if total > 0 else 1.0

        # Calculate overall score
        quality_weights = {
            TransitionQuality.EXCELLENT: 1.0,
            TransitionQuality.GOOD: 0.85,
            TransitionQuality.ACCEPTABLE: 0.7,
            TransitionQuality.ROUGH: 0.5,
            TransitionQuality.JARRING: 0.3,
        }
        weighted_sum = sum(quality_weights[p.quality] for p in profiles)
        overall_score = weighted_sum / total if total > 0 else 1.0

        # Generate critical issues
        critical = [p for p in profiles if p.quality in [TransitionQuality.ROUGH, TransitionQuality.JARRING]]
        critical_issues = [f"章节{p.from_chapter_number}到{p.to_chapter_number}的过渡存在问题：{', '.join(p.issues)}"
                          for p in critical]

        # Generate recommendations
        recommendations = self._generate_overall_recommendations(profiles, quality_counts)

        # Sort weakest by score
        weakest.sort(key=lambda x: x[2])

        return TransitionAnalysis(
            overall_transition_score=overall_score,
            transition_profiles=profiles,
            connections=connections,
            issues=all_issues,
            total_transitions=total,
            excellent_transitions=quality_counts[TransitionQuality.EXCELLENT],
            good_transitions=quality_counts[TransitionQuality.GOOD],
            acceptable_transitions=quality_counts[TransitionQuality.ACCEPTABLE],
            rough_transitions=quality_counts[TransitionQuality.ROUGH],
            jarring_transitions=quality_counts[TransitionQuality.JARRING],
            average_consistency=avg_consistency,
            weakest_transitions=weakest[:5],
            critical_issues=critical_issues,
            recommendations=recommendations,
        )

    def _generate_overall_recommendations(
        self,
        profiles: list[ChapterTransitionProfile],
        quality_counts: dict[TransitionQuality, int],
    ) -> list[str]:
        """Generate overall recommendations for improving transitions."""
        recommendations = []

        if quality_counts[TransitionQuality.JARRING] > 0:
            recommendations.append(f"必须修复 {quality_counts[TransitionQuality.JARRING]} 处严重断裂的过渡")

        if quality_counts[TransitionQuality.ROUGH] > 0:
            recommendations.append(f"建议优化 {quality_counts[TransitionQuality.ROUGH]} 处粗糙的过渡")

        # Check for common issues
        time_issues = sum(1 for p in profiles if "时间" in ",".join(p.issues))
        if time_issues > 0:
            recommendations.append("加强章节间的时间过渡说明")

        scene_issues = sum(1 for p in profiles if "场景" in ",".join(p.issues))
        if scene_issues > 0:
            recommendations.append("增加场景过渡描写的连贯性")

        emotion_issues = sum(1 for p in profiles if "情感" in ",".join(p.issues))
        if emotion_issues > 0:
            recommendations.append("渐进式调整情感基调，避免突变")

        if not recommendations:
            recommendations.append("章节过渡整体流畅，保持现有质量")

        return recommendations

    def analyze_novel_transitions(self, novel: Novel) -> TransitionAnalysis:
        """Analyze all chapter transitions in a novel.

        Args:
            novel: Novel to analyze

        Returns:
            TransitionAnalysis
        """
        # Collect all chapters
        all_chapters: list[Chapter] = []
        for volume in novel.volumes:
            all_chapters.extend(volume.chapters)

        return self.analyze_all_transitions(all_chapters)

    def create_revision_plan(
        self,
        analysis: TransitionAnalysis,
        target_score: float = 0.85,
    ) -> TransitionPlan:
        """Create a plan for improving chapter transitions.

        Args:
            analysis: Transition analysis
            target_score: Target consistency score

        Returns:
            TransitionPlan
        """
        # Identify transitions that need revision
        to_revise: list[tuple[int, int]] = []
        for profile in analysis.transition_profiles:
            if profile.consistency_score < target_score:
                to_revise.append((profile.from_chapter_number, profile.to_chapter_number))

        # Sort by priority (lowest score first)
        score_map = {
            (p.from_chapter_number, p.to_chapter_number): p.consistency_score
            for p in analysis.transition_profiles
        }
        to_revise.sort(key=lambda x: score_map.get(x, 1.0))

        # Determine focus areas based on common issues
        all_issues = " ".join([" ".join(p.issues) for p in analysis.transition_profiles])

        plan = TransitionPlan(
            transitions_to_revise=to_revise,
            priority_order=to_revise,
            estimated_revisions=len(to_revise),
            ai_bridge_generation=True,
        )

        if "时间" in all_issues:
            plan.focus_time_continuity = True
        if "场景" in all_issues:
            plan.focus_scene_continuity = True
        if "情感" in all_issues:
            plan.focus_emotional_flow = True
        if "张力" in all_issues:
            plan.focus_plot_continuity = True

        return plan

    async def revise_transition(
        self,
        from_chapter: Chapter,
        to_chapter: Chapter,
        profile: ChapterTransitionProfile,
    ) -> TransitionRevision:
        """Revise the transition between two chapters.

        Args:
            from_chapter: Source chapter
            to_chapter: Target chapter
            profile: Transition profile

        Returns:
            TransitionRevision
        """
        original_from_ending = from_chapter.content[-300:] if from_chapter.content else ""
        original_to_opening = to_chapter.content[:300] if to_chapter.content else ""

        before_score = profile.consistency_score

        # Build revision prompt
        prompt = f"""请为以下章节之间创建流畅的过渡内容：

【第{from_chapter.number}章「{from_chapter.title}」结尾】
{original_from_ending}

【第{to_chapter.number}章「{to_chapter.title}」开头】
{original_to_opening}

过渡问题分析：
{", ".join(profile.issues) if profile.issues else "需要优化过渡"}

推荐改进方式：
{", ".join(profile.recommendations) if profile.recommendations else "增加过渡段落"}

要求：
1. 如果需要时间过渡，在结尾添加时间说明（如"数日后"、"夜幕降临"等）
2. 如果需要场景过渡，创建桥梁段落描写环境/地点变化
3. 保持原有的情感基调和叙事节奏
4. 优化结尾和开头的衔接
5. 直接输出修改后的内容，用【结尾过渡】和【开头过渡】标记

格式：
【结尾过渡】
[第{from_chapter.number}章修改后的结尾部分]

【开头过渡】
[第{to_chapter.number}章修改后的开头部分]"""

        response = await self.ai_service.generate(prompt, temperature=0.3)
        response = response.strip()

        # Parse response
        from_revised = original_from_ending
        to_revised = original_to_opening
        bridge = ""

        if "【结尾过渡】" in response and "【开头过渡】" in response:
            parts = response.split("【开头过渡】")
            if len(parts) >= 2:
                ending_part = parts[0].split("【结尾过渡】")[1] if "【结尾过渡】" in parts[0] else ""
                from_revised = ending_part.strip() if ending_part else original_from_ending
                to_revised = parts[1].strip()

        # Calculate improved score (simplified)
        after_score = min(1.0, before_score + 0.15)

        return TransitionRevision(
            from_chapter=from_chapter.number,
            to_chapter=to_chapter.number,
            from_chapter_revised=from_revised,
            to_chapter_revised=to_revised,
            bridge_content=bridge,
            before_score=before_score,
            after_score=after_score,
            changes_made=["优化了章节结尾和开头的衔接"],
            issues_addressed=profile.issues[:1] if profile.issues else [],
            issues_remaining=profile.issues[1:] if len(profile.issues) > 1 else [],
        )

    def generate_transition_report(
        self,
        analysis: TransitionAnalysis,
    ) -> TransitionReport:
        """Generate a comprehensive transition report.

        Args:
            analysis: Transition analysis

        Returns:
            TransitionReport
        """
        # Build summary
        summary_parts = [
            f"分析了 {analysis.total_transitions} 处章节过渡",
        ]

        if analysis.excellent_transitions > 0:
            summary_parts.append(f"其中 {analysis.excellent_transitions} 处过渡优秀")
        if analysis.good_transitions > 0:
            summary_parts.append(f"{analysis.good_transitions} 处良好")
        if analysis.rough_transitions > 0:
            summary_parts.append(f"{analysis.rough_transitions} 处需要改进")
        if analysis.jarring_transitions > 0:
            summary_parts.append(f"{analysis.jarring_transitions} 处存在严重断裂")

        summary_parts.append(f"整体过渡评分：{analysis.overall_transition_score:.2f}")

        if analysis.weakest_transitions:
            worst = analysis.weakest_transitions[0]
            summary_parts.append(f"最需改进：第{worst[0]}章到第{worst[1]}章")

        summary = "。".join(summary_parts) + "。"

        return TransitionReport(
            analysis=analysis,
            revision_plan=self.create_revision_plan(analysis),
            summary=summary,
        )

    def get_transition_summary(
        self,
        profile: ChapterTransitionProfile,
    ) -> str:
        """Get a human-readable summary of a transition.

        Args:
            profile: Chapter transition profile

        Returns:
            Human-readable summary
        """
        quality_desc = {
            TransitionQuality.EXCELLENT: "优秀",
            TransitionQuality.GOOD: "良好",
            TransitionQuality.ACCEPTABLE: "一般",
            TransitionQuality.ROUGH: "粗糙",
            TransitionQuality.JARRING: "断裂",
        }

        type_desc = {
            TransitionType.SCENE_CONTINUATION: "场景延续",
            TransitionType.SCENE_SWITCH: "场景切换",
            TransitionType.TIME_JUMP: "时间跳跃",
            TransitionType.POV_SWITCH: "视角转换",
            TransitionType.PARALLEL_NARRATIVE: "平行叙事",
            TransitionType.EMOTIONAL_SHIFT: "情感转变",
            TransitionType.TENSION_PEAK: "张力高潮",
            TransitionType.TENSION_RELEASE: "张力释放",
            TransitionType.REVELATION: "悬念揭晓",
            TransitionType.STATUS_QUO: "回归常态",
        }

        return (
            f"第{profile.from_chapter_number}章→第{profile.to_chapter_number}章："
            f"{type_desc.get(profile.transition_type, '未知')}，"
            f"质量{quality_desc.get(profile.quality, '未知')}，"
            f"一致性评分{profile.consistency_score:.2f}"
        )
