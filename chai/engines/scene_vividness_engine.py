"""Scene vividness engine for validating scene description quality."""

import re
from typing import Optional

from chai.models.scene_vividness import (
    SceneVividnessType,
    SceneVividnessSeverity,
    SceneVividnessIssue,
    SceneVividnessProfile,
    SceneVividnessAnalysis,
    SceneVividnessRevision,
    SceneVividnessReport,
    SceneVividnessTemplate,
    ImageryClarity,
    SensoryEngagement,
    ShowDontTellLevel,
    VisualDetailCheck,
    SensoryDetailCheck,
    ShowDontTellCheck,
    LanguageQualityCheck,
)
from chai.models import Chapter, Scene


class SceneVividnessEngine:
    """Engine for validating scene description vividness and visual imagery."""

    # Filter words that weaken imagery
    FILTER_WORDS = {
        '看到', '看见', '观察到', '注视着', '瞥见', '看见',
        '听到', '听见', '聆听到', '注意', '注意到',
        '感到', '感觉', '感受到', '体会到', '发觉', '发现',
        '认为', '觉得', '知道', '理解', '明白', '意识到',
    }

    # Weak adjectives/qualifiers
    WEAK_ADJECTIVES = {
        '很', '非常', '十分', '相当', '颇', '有点',
        '有些', '一点', '一点点的', '略微', '稍微',
        '稍稍', '略', '较', '蛮', '怪', '满', '挺', '好',
    }

    # Cliche descriptions
    CLICHE_PATTERNS = {
        '漆黑一片': '漆黑一片',
        '金碧辉煌': '金碧辉煌',
        '鸟语花香': '鸟语花香',
        '风和日丽': '风和日丽',
        '晴空万里': '晴空万里',
        '电闪雷鸣': '电闪雷鸣',
        '倾盆大雨': '倾盆大雨',
        '鹅毛大雪': '鹅毛大雪',
        '眉清目秀': '眉清目秀',
        '亭亭玉立': '亭亭玉立',
        '仪表堂堂': '仪表堂堂',
        '苍白的脸上': '苍白的脸上',
        '血红的': '血红的',
        '漆黑的眼睛': '漆黑的眼睛',
    }

    # Color words
    COLOR_WORDS = {
        '红', '黄', '蓝', '绿', '白', '黑', '紫', '橙', '粉', '灰',
        '金色', '银色', '青色', '棕色', '褐色', '紫色', '深色', '浅色',
        '暗红', '淡蓝', '米色', '象牙', '绯红', '朱红', '翠绿', '碧绿',
        '湛蓝', '天蓝', '灰白', '漆黑', '雪白', '粉红', '金黄', '土黄',
    }

    # Visual verbs (strong action verbs)
    VISUAL_VERBS = {
        '闪烁', '闪耀', '照射', '洒落', '笼罩', '覆盖', '穿透',
        '蔓延', '延伸', '蜿蜒', '流淌', '流动', '漂浮', '悬挂',
        '矗立', '耸立', '伫立', '排列', '散落', '堆积', '环绕',
        '交织', '缠绕', '盘旋', '翱翔', '飞舞', '飘落', '滴落',
    }

    # Telling phrases (direct statements of emotion/state)
    TELLING_PHRASES = {
        '很紧张': '很紧张',
        '很害怕': '很害怕',
        '很恐惧': '很恐惧',
        '很悲伤': '很悲伤',
        '很难过': '很难过',
        '很生气': '很生气',
        '很愤怒': '很愤怒',
        '很高兴': '很高兴',
        '很快乐': '很快乐',
        '很兴奋': '很兴奋',
        '很惊讶': '很惊讶',
        '很震惊': '很震惊',
        '很困惑': '很困惑',
        '很迷茫': '很迷茫',
        '很茫然': '很茫然',
        '气氛紧张': '气氛紧张',
        '气氛压抑': '气氛压抑',
        '气氛诡异': '气氛诡异',
        '气氛恐怖': '气氛恐怖',
        '感到紧张': '感到紧张',
        '感到害怕': '感到害怕',
        '感到悲伤': '感到悲伤',
        '感到孤独': '感到孤独',
        '让人觉得': '让人觉得',
        '显得很': '显得很',
        '看起来很': '看起来很',
        '看起来像是': '看起来像是',
    }

    def __init__(self, template: SceneVividnessTemplate = SceneVividnessTemplate.STANDARD):
        """Initialize scene vividness engine."""
        self.template = template

    def analyze_scene_vividness(
        self,
        scene_description: str,
        scene_id: str = "unknown",
    ) -> SceneVividnessAnalysis:
        """Analyze a scene description for vividness.

        Args:
            scene_description: The scene description text
            scene_id: Scene identifier

        Returns:
            SceneVividnessAnalysis with detailed findings
        """
        word_count = self._count_chinese_words(scene_description)

        # Perform checks
        visual_check = self._check_visual_details(scene_description)
        sensory_check = self._check_sensory_details(scene_description)
        show_dont_tell = self._check_show_dont_tell(scene_description)
        language_quality = self._check_language_quality(scene_description)

        # Identify issues
        issues = self._identify_issues(
            scene_description, visual_check, sensory_check,
            show_dont_tell, language_quality
        )

        # Identify strengths
        strengths = self._identify_strengths(
            scene_description, visual_check, sensory_check,
            show_dont_tell, language_quality
        )

        # Calculate scores
        vividness_score = self._calculate_vividness_score(
            visual_check, sensory_check, show_dont_tell, language_quality
        )
        imagery_clarity = self._determine_imagery_clarity(visual_check, word_count)
        sensory_engagement = self._determine_sensory_engagement(sensory_check)
        show_dont_tell_level = self._determine_show_dont_tell_level(show_dont_tell)

        # Create profile
        profile = SceneVividnessProfile(
            scene_id=scene_id,
            word_count=word_count,
            vividness_score=vividness_score,
            imagery_clarity=imagery_clarity,
            sensory_engagement=sensory_engagement,
            show_dont_tell_level=show_dont_tell_level,
            visual_details=visual_check,
            sensory_details=sensory_check,
            show_dont_tell=show_dont_tell,
            language_quality=language_quality,
            issues=issues,
            strengths=strengths,
        )

        # Count issues by severity
        minor_count = sum(1 for i in issues if i.severity == SceneVividnessSeverity.MINOR)
        moderate_count = sum(1 for i in issues if i.severity == SceneVividnessSeverity.MODERATE)
        severe_count = sum(1 for i in issues if i.severity == SceneVividnessSeverity.SEVERE)

        # Build issue breakdown
        issue_breakdown = {}
        for issue in issues:
            issue_type = issue.issue_type.value
            issue_breakdown[issue_type] = issue_breakdown.get(issue_type, 0) + 1

        # Calculate component scores
        visual_imagery_score = self._calculate_visual_imagery_score(visual_check, language_quality)
        sensory_balance_score = self._calculate_sensory_balance_score(sensory_check)
        show_dont_tell_score = show_dont_tell.showing_ratio
        language_score = self._calculate_language_score(language_quality)

        return SceneVividnessAnalysis(
            scene_id=scene_id,
            profile=profile,
            overall_vividness=vividness_score,
            visual_imagery_score=visual_imagery_score,
            sensory_balance_score=sensory_balance_score,
            show_dont_tell_score=show_dont_tell_score,
            language_quality_score=language_score,
            total_issues=len(issues),
            minor_issues=minor_count,
            moderate_issues=moderate_count,
            severe_issues=severe_count,
            issue_breakdown=issue_breakdown,
        )

    def analyze_chapter_vividness(
        self,
        chapter: Chapter,
    ) -> SceneVividnessReport:
        """Analyze all scenes in a chapter for vividness.

        Args:
            chapter: Chapter object with scenes

        Returns:
            SceneVividnessReport with chapter analysis
        """
        scene_profiles = []
        total_vividness = 0.0

        for scene in chapter.scenes:
            if scene.scene_type.value in ['action', 'dialogue']:
                # Skip pure dialogue scenes
                continue

            scene_text = self._extract_scene_text(scene)
            if not scene_text:
                continue

            analysis = self.analyze_scene_vividness(scene_text, scene.scene_id)
            scene_profiles.append(analysis.profile)
            total_vividness += analysis.overall_vividness

        scene_count = len(scene_profiles)
        avg_vividness = total_vividness / scene_count if scene_count > 0 else 0.0

        # Calculate distribution
        distribution = {
            'vivid': 0,      # > 0.7
            'adequate': 0,   # 0.4-0.7
            'dull': 0,       # < 0.4
        }
        for profile in scene_profiles:
            if profile.vividness_score > 0.7:
                distribution['vivid'] += 1
            elif profile.vividness_score < 0.4:
                distribution['dull'] += 1
            else:
                distribution['adequate'] += 1

        # Find most common issues
        all_issues = []
        for profile in scene_profiles:
            all_issues.extend(profile.issues)

        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        most_common = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Generate recommendations
        recommendations = self._generate_chapter_recommendations(
            scene_profiles, most_common
        )

        return SceneVividnessReport(
            chapter_id=chapter.chapter_id,
            scene_profiles=scene_profiles,
            average_vividness=avg_vividness,
            vividness_distribution=distribution,
            total_issues=len(all_issues),
            most_common_issues=most_common,
            recommendations=recommendations,
            scene_count=scene_count,
            vivid_scene_count=distribution['vivid'],
            dull_scene_count=distribution['dull'],
        )

    def _count_chinese_words(self, text: str) -> int:
        """Count Chinese words (characters + English words)."""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words

    def _check_visual_details(self, text: str) -> VisualDetailCheck:
        """Check visual detail completeness."""
        # Count color words
        color_count = 0
        for color in self.COLOR_WORDS:
            color_count += text.count(color)

        # Count visual verbs
        visual_verb_count = 0
        for verb in self.VISUAL_VERBS:
            visual_verb_count += text.count(verb)

        # Check for specific visual elements
        has_color = color_count > 0
        has_texture = any(word in text for word in ['粗糙', '光滑', '柔软', '坚硬', '粗糙', '细腻', '质感'])
        has_size = any(word in text for word in ['巨大', '渺小', '高耸', '宽阔', '狭窄', '微小', '庞大', '细小'])
        has_light = any(word in text for word in ['光', '亮', '暗', '阴影', '光线', '阳光', '月光', '灯光'])
        has_spatial = any(word in text for word in ['左', '右', '前', '后', '上', '下', '中间', '周围', '之间'])

        return VisualDetailCheck(
            has_color_details=has_color,
            has_texture_details=has_texture,
            has_size_scale=has_size,
            has_light_shadow=has_light,
            has_spatial_arrangement=has_spatial,
            has_focal_point=has_spatial,  # Simplified check
            color_word_count=color_count,
            visual_verb_count=visual_verb_count,
        )

    def _check_sensory_details(self, text: str) -> SensoryDetailCheck:
        """Check sensory engagement."""
        # Visual
        visual_words = ['看', '眼', '视觉', '颜色', '光', '亮', '暗']
        visual_count = sum(text.count(word) for word in visual_words)

        # Auditory
        sound_words = ['听', '声音', '响', '静', '声', '音', '噪音', '喧哗', '寂静']
        auditory_count = sum(text.count(word) for word in sound_words)

        # Tactile
        tactile_words = ['摸', '触', '感觉', '温度', '热', '冷', '粗糙', '光滑', '柔软']
        tactile_count = sum(text.count(word) for word in tactile_words)

        # Olfactory
        smell_words = ['闻', '气味', '香', '臭', '芬芳', '腥', '酸味', '香味']
        olfactory_count = sum(text.count(word) for word in smell_words)

        # Gustatory
        taste_words = ['味', '尝', '酸', '甜', '苦', '辣', '咸', '涩']
        gustatory_count = sum(text.count(word) for word in taste_words)

        # Calculate sense diversity score (0-1)
        senses_used = sum([
            visual_count > 0,
            auditory_count > 0,
            tactile_count > 0,
            olfactory_count > 0,
            gustatory_count > 0,
        ])
        sense_diversity_score = senses_used / 5.0

        return SensoryDetailCheck(
            visual_count=visual_count,
            auditory_count=auditory_count,
            tactile_count=tactile_count,
            olfactory_count=olfactory_count,
            gustatory_count=gustatory_count,
            sense_diversity_score=sense_diversity_score,
        )

    def _check_show_dont_tell(self, text: str) -> ShowDontTellCheck:
        """Check show don't tell patterns."""
        telling_phrases = []
        showing_count = 0

        for phrase in self.TELLING_PHRASES:
            if phrase in text:
                telling_phrases.append(phrase)

        # Estimate showing count based on sensory details
        showing_count = len(re.findall(r'[的一]些?[\u4e00-\u9fff]', text))

        telling_count = len(telling_phrases)

        # Calculate ratio
        total = showing_count + telling_count
        showing_ratio = showing_count / total if total > 0 else 0.5

        return ShowDontTellCheck(
            telling_phrases=telling_phrases,
            showing_count=showing_count,
            telling_count=telling_count,
            showing_ratio=showing_ratio,
        )

    def _check_language_quality(self, text: str) -> LanguageQualityCheck:
        """Check language quality issues."""
        filter_count = 0
        for word in self.FILTER_WORDS:
            filter_count += text.count(word)

        weak_adj_count = 0
        for word in self.WEAK_ADJECTIVES:
            weak_adj_count += text.count(word)

        cliche_count = 0
        for cliche in self.CLICHE_PATTERNS:
            cliche_count += text.count(cliche)

        # Count passive voice (simplified)
        passive_patterns = [
            r'被[\u4e00-\u9fff]', r'遭到[\u4e00-\u9fff]', r'受到[\u4e00-\u9fff]',
        ]
        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text))

        # Concrete word ratio (simplified heuristic)
        concrete_indicators = ['的', '了', '是', '在', '有']
        total_words = len(re.findall(r'[\u4e00-\u9fff]+', text))
        if total_words > 0:
            concrete_ratio = min(1.0, len([w for w in concrete_indicators if text.count(w)]) / 5.0)
        else:
            concrete_ratio = 0.5

        return LanguageQualityCheck(
            filter_word_count=filter_count,
            weak_adjective_count=weak_adj_count,
            cliche_count=cliche_count,
            passive_voice_count=passive_count,
            concrete_word_ratio=concrete_ratio,
        )

    def _identify_issues(
        self,
        text: str,
        visual: VisualDetailCheck,
        sensory: SensoryDetailCheck,
        show_dont_tell: ShowDontTellCheck,
        language: LanguageQualityCheck,
    ) -> list[SceneVividnessIssue]:
        """Identify specific vividness issues."""
        issues = []

        # Visual detail issues
        if not visual.has_color_details:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.ABSENT_VISUAL_DETAILS,
                severity=SceneVividnessSeverity.MODERATE,
                location="throughout",
                description="No color details found in description",
                suggestion="Add specific colors to make the scene more vivid",
            ))

        if not visual.has_light_shadow:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.ABSENT_VISUAL_DETAILS,
                severity=SceneVividnessSeverity.MODERATE,
                location="throughout",
                description="No light/shadow descriptions found",
                suggestion="Include light sources and shadow patterns for atmosphere",
            ))

        if not visual.has_spatial_arrangement:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.UNCLEAR_SPATIAL_LAYOUT,
                severity=SceneVividnessSeverity.MINOR,
                location="throughout",
                description="Spatial layout is unclear",
                suggestion="Use directional words (left, right, above) to clarify arrangement",
            ))

        # Sensory issues
        if sensory.sense_diversity_score < 0.2:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.ABSENT_SENSORY_DETAILS,
                severity=SceneVividnessSeverity.MODERATE,
                location="throughout",
                description="Very limited sensory engagement",
                suggestion="Add details for at least 2-3 senses",
            ))
        elif sensory.sense_diversity_score < 0.4:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.SINGLE_SENSE_OVERUSE,
                severity=SceneVividnessSeverity.MINOR,
                location="throughout",
                description="Description relies heavily on one sense",
                suggestion="Include more varied sensory details",
            ))

        # Show don't tell issues
        if show_dont_tell.telling_count > 0:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.TELLING_INSTEAD_SHOWING,
                severity=SceneVividnessSeverity.MODERATE,
                location=", ".join(show_dont_tell.telling_phrases[:3]),
                description=f"Found {show_dont_tell.telling_count} telling phrases",
                suggestion="Replace direct emotional statements with sensory evidence",
            ))

        # Language quality issues
        if language.filter_word_count > 3:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.FILTER_WORDS,
                severity=SceneVividnessSeverity.MINOR,
                location="throughout",
                description=f"Found {language.filter_word_count} filter words",
                suggestion="Remove 'saw/heard/felt' filter words when possible",
            ))

        if language.weak_adjective_count > 5:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.WEAK_ADJECTIVES,
                severity=SceneVividnessSeverity.MINOR,
                location="throughout",
                description=f"Found {language.weak_adjective_count} weak qualifiers",
                suggestion="Replace 'very', 'quite' with specific descriptors",
            ))

        if language.cliche_count > 0:
            issues.append(SceneVividnessIssue(
                issue_type=SceneVividnessType.CLICHE_DESCRIPTIONS,
                severity=SceneVividnessSeverity.MINOR,
                location="throughout",
                description=f"Found {language.cliche_count} cliche phrases",
                suggestion="Replace cliches with fresh, specific descriptions",
            ))

        return issues

    def _identify_strengths(
        self,
        text: str,
        visual: VisualDetailCheck,
        sensory: SensoryDetailCheck,
        show_dont_tell: ShowDontTellCheck,
        language: LanguageQualityCheck,
    ) -> list[str]:
        """Identify vividness strengths."""
        strengths = []

        if visual.has_color_details and visual.color_word_count >= 3:
            strengths.append("Rich color palette creates visual depth")

        if visual.has_light_shadow:
            strengths.append("Light and shadow contrast adds drama")

        if sensory.sense_diversity_score >= 0.6:
            strengths.append("Full sensory engagement immerses reader")

        if show_dont_tell.showing_ratio > 0.7:
            strengths.append("Excellent show don't tell balance")

        if language.filter_word_count == 0:
            strengths.append("Direct, unfiltered prose style")

        if language.cliche_count == 0:
            strengths.append("Original, fresh descriptions")

        if visual.has_spatial_arrangement:
            strengths.append("Clear spatial orientation")

        return strengths

    def _calculate_vividness_score(
        self,
        visual: VisualDetailCheck,
        sensory: SensoryDetailCheck,
        show_dont_tell: ShowDontTellCheck,
        language: LanguageQualityCheck,
    ) -> float:
        """Calculate overall vividness score 0-1."""
        scores = []

        # Visual details (30%)
        visual_score = 0.0
        if visual.has_color_details:
            visual_score += 0.25
        if visual.has_texture_details:
            visual_score += 0.2
        if visual.has_light_shadow:
            visual_score += 0.25
        if visual.has_spatial_arrangement:
            visual_score += 0.2
        if visual.visual_verb_count >= 3:
            visual_score += 0.1
        scores.append(min(1.0, visual_score))

        # Sensory diversity (25%)
        scores.append(sensory.sense_diversity_score)

        # Show don't tell (25%)
        scores.append(show_dont_tell.showing_ratio)

        # Language quality (20%)
        lang_score = 1.0
        if language.filter_word_count > 0:
            lang_score -= min(0.3, language.filter_word_count * 0.05)
        if language.weak_adjective_count > 0:
            lang_score -= min(0.3, language.weak_adjective_count * 0.03)
        if language.cliche_count > 0:
            lang_score -= min(0.2, language.cliche_count * 0.05)
        scores.append(max(0.0, lang_score))

        # Weighted average
        weights = [0.30, 0.25, 0.25, 0.20]
        return sum(s * w for s, w in zip(scores, weights))

    def _calculate_visual_imagery_score(
        self,
        visual: VisualDetailCheck,
        language: LanguageQualityCheck,
    ) -> float:
        """Calculate visual imagery score."""
        score = 0.0
        if visual.has_color_details:
            score += 0.25
        if visual.has_light_shadow:
            score += 0.25
        if visual.has_spatial_arrangement:
            score += 0.2
        if visual.visual_verb_count >= 2:
            score += 0.15
        if language.filter_word_count < 3:
            score += 0.15
        return min(1.0, score)

    def _calculate_sensory_balance_score(
        self,
        sensory: SensoryDetailCheck,
    ) -> float:
        """Calculate sensory balance score."""
        # Start with diversity
        score = sensory.sense_diversity_score * 0.6

        # Bonus for rich counts
        total_sensory = (
            sensory.visual_count +
            sensory.auditory_count +
            sensory.tactile_count +
            sensory.olfactory_count
        )
        if total_sensory >= 10:
            score += 0.2
        elif total_sensory >= 5:
            score += 0.1

        # Balance (no single sense dominating)
        max_sense = max(
            sensory.visual_count,
            sensory.auditory_count,
            sensory.tactile_count,
            sensory.olfactory_count,
        )
        if total_sensory > 0 and max_sense / total_sensory < 0.7:
            score += 0.2

        return min(1.0, score)

    def _calculate_language_score(
        self,
        language: LanguageQualityCheck,
    ) -> float:
        """Calculate language quality score."""
        score = 0.5  # Base

        # Filter words penalty
        score -= min(0.2, language.filter_word_count * 0.04)

        # Weak adjectives penalty
        score -= min(0.15, language.weak_adjective_count * 0.02)

        # Cliches penalty
        score -= min(0.1, language.cliche_count * 0.03)

        # Concrete ratio bonus
        score += language.concrete_word_ratio * 0.2

        return max(0.0, min(1.0, score))

    def _determine_imagery_clarity(
        self,
        visual: VisualDetailCheck,
        word_count: int,
    ) -> ImageryClarity:
        """Determine imagery clarity level."""
        score = 0
        if visual.has_color_details:
            score += 1
        if visual.has_light_shadow:
            score += 1
        if visual.has_spatial_arrangement:
            score += 1
        if visual.visual_verb_count >= 2:
            score += 1

        if score >= 3 and word_count >= 100:
            return ImageryClarity.VIVID
        elif score >= 2 and word_count >= 50:
            return ImageryClarity.CLEAR
        elif score >= 1:
            return ImageryClarity.ADEQUATE
        elif word_count > 0:
            return ImageryClarity.FUZZY
        else:
            return ImageryClarity.UNCLEAR

    def _determine_sensory_engagement(
        self,
        sensory: SensoryDetailCheck,
    ) -> SensoryEngagement:
        """Determine sensory engagement level."""
        if sensory.sense_diversity_score >= 0.6:
            return SensoryEngagement.RICH
        elif sensory.sense_diversity_score >= 0.3:
            return SensoryEngagement.MODERATE
        elif sensory.sense_diversity_score >= 0.1:
            return SensoryEngagement.MINIMAL
        else:
            return SensoryEngagement.NONE

    def _determine_show_dont_tell_level(
        self,
        show_dont_tell: ShowDontTellCheck,
    ) -> ShowDontTellLevel:
        """Determine show don't tell level."""
        ratio = show_dont_tell.showing_ratio
        if ratio >= 0.85:
            return ShowDontTellLevel.EXCELLENT
        elif ratio >= 0.65:
            return ShowDontTellLevel.MOSTLY_SHOWING
        elif ratio >= 0.45:
            return ShowDontTellLevel.PARTIAL_SHOWING
        else:
            return ShowDontTellLevel.MOSTLY_TELLING

    def _extract_scene_text(self, scene: Scene) -> str:
        """Extract text content from scene."""
        if hasattr(scene, 'content') and scene.content:
            return scene.content
        return ""

    def _generate_chapter_recommendations(
        self,
        scene_profiles: list[SceneVividnessProfile],
        most_common_issues: list[tuple[str, int]],
    ) -> list[str]:
        """Generate chapter-level recommendations."""
        recommendations = []

        if not scene_profiles:
            return ["No scenes to analyze"]

        # Check overall vividness
        avg_vividness = sum(p.vividness_score for p in scene_profiles) / len(scene_profiles)
        if avg_vividness < 0.5:
            recommendations.append("Overall scene vividness needs improvement")

        # Check for dull scenes
        dull_count = sum(1 for p in scene_profiles if p.vividness_score < 0.4)
        if dull_count > 0:
            recommendations.append(f"{dull_count} scene(s) have low vividness - prioritize revision")

        # Address common issues
        for issue_type, count in most_common_issues[:3]:
            if issue_type == 'absent_visual_details':
                recommendations.append("Add more visual details (colors, light/shadow) across scenes")
            elif issue_type == 'absent_sensory_details':
                recommendations.append("Expand sensory engagement beyond just visual")
            elif issue_type == 'telling_instead_showing':
                recommendations.append("Replace direct emotional statements with sensory evidence")

        return recommendations

    def create_revision_plan(
        self,
        analysis: SceneVividnessAnalysis,
    ) -> SceneVividnessRevision:
        """Create revision plan based on analysis.

        Args:
            analysis: The vividness analysis results

        Returns:
            SceneVividnessRevision with revision suggestions
        """
        revision_notes = []
        priority_fixes = []
        suggested_additions = []
        suggested_cuts = []

        profile = analysis.profile

        # Prioritize severe and moderate issues
        for issue in profile.issues:
            if issue.severity == SceneVividnessSeverity.SEVERE:
                priority_fixes.append(f"[SEVERE] {issue.suggestion}")
                revision_notes.append(f"Fix: {issue.description} at {issue.location}")
            elif issue.severity == SceneVividnessSeverity.MODERATE:
                revision_notes.append(f"Revise: {issue.description}")

        # Suggest additions based on what's missing
        if not profile.visual_details.has_color_details:
            suggested_additions.append("Add specific color descriptions")

        if not profile.visual_details.has_light_shadow:
            suggested_additions.append("Include light source and shadow patterns")

        if not profile.visual_details.has_spatial_arrangement:
            suggested_additions.append("Add directional/spatial relationship words")

        if profile.sensory_details.sense_diversity_score < 0.4:
            suggested_additions.append("Add sensory details from 1-2 additional senses")

        # Suggest cuts based on issues
        if profile.language_quality.filter_word_count > 3:
            suggested_cuts.append("Reduce filter words (saw, heard, felt)")

        if profile.language_quality.cliche_count > 0:
            suggested_cuts.append("Replace cliche descriptions with fresh ones")

        return SceneVividnessRevision(
            original_scene_id=analysis.scene_id,
            revision_notes=revision_notes,
            priority_fixes=priority_fixes,
            suggested_additions=suggested_additions,
            suggested_cuts=suggested_cuts,
        )

    def generate_report(
        self,
        analyses: list[SceneVividnessAnalysis],
    ) -> SceneVividnessReport:
        """Generate comprehensive report from multiple analyses.

        Args:
            analyses: List of scene vividness analyses

        Returns:
            SceneVividnessReport with aggregate results
        """
        if not analyses:
            return SceneVividnessReport()

        scene_profiles = [a.profile for a in analyses]
        total_vividness = sum(a.overall_vividness for a in analyses)
        avg_vividness = total_vividness / len(analyses)

        # Calculate distribution
        distribution = {'vivid': 0, 'adequate': 0, 'dull': 0}
        for profile in scene_profiles:
            if profile.vividness_score > 0.7:
                distribution['vivid'] += 1
            elif profile.vividness_score < 0.4:
                distribution['dull'] += 1
            else:
                distribution['adequate'] += 1

        # Collect all issues
        all_issues = []
        for profile in scene_profiles:
            all_issues.extend(profile.issues)

        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        most_common = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Generate recommendations
        recommendations = []
        if avg_vividness < 0.5:
            recommendations.append("Overall vividness needs improvement")
        if distribution['dull'] > 0:
            recommendations.append(f"{distribution['dull']} scene(s) are dull and need revision")

        return SceneVividnessReport(
            scene_profiles=scene_profiles,
            average_vividness=avg_vividness,
            vividness_distribution=distribution,
            total_issues=len(all_issues),
            most_common_issues=most_common,
            recommendations=recommendations,
            scene_count=len(scene_profiles),
            vivid_scene_count=distribution['vivid'],
            dull_scene_count=distribution['dull'],
        )

    def get_summary(self, analysis: SceneVividnessAnalysis) -> str:
        """Get human-readable summary of analysis.

        Args:
            analysis: The vividness analysis

        Returns:
            Human-readable summary string
        """
        profile = analysis.profile

        lines = [
            f"=== Scene Vividness Analysis: {analysis.scene_id} ===",
            f"Vividness Score: {analysis.overall_vividness:.2f}/1.0",
            f"Imagery Clarity: {profile.imagery_clarity.value}",
            f"Sensory Engagement: {profile.sensory_engagement.value}",
            f"Show Don't Tell: {profile.show_dont_tell_level.value}",
            f"",
            f"Issues Found: {analysis.total_issues} ({analysis.severe_issues} severe, {analysis.moderate_issues} moderate, {analysis.minor_issues} minor)",
        ]

        if profile.strengths:
            lines.append("")
            lines.append("Strengths:")
            for strength in profile.strengths[:3]:
                lines.append(f"  + {strength}")

        if profile.issues:
            lines.append("")
            lines.append("Priority Issues:")
            for issue in profile.issues[:3]:
                lines.append(f"  - [{issue.severity.value}] {issue.description}")

        return "\n".join(lines)
