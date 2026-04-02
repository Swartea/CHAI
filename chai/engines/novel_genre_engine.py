"""Novel genre engine for supporting multiple novel types."""

import re
from typing import Optional
from chai.models.novel import Novel
from chai.models.novel_genre import (
    NovelGenreType,
    WorldSettingType,
    MagicTechnologyLevel,
    PlotStructureType,
    RomanceType,
    ConflictType,
    TargetAudience,
    GenreWorldConfig,
    GenreCharacterTemplate,
    GenrePlotConfig,
    GenreStyleConfig,
    GenreToneConfig,
    NovelGenreProfile,
    GenreAnalysisResult,
    GenreTemplate,
    GenreRecommendation,
)


# Genre templates for each novel type
GENRE_TEMPLATES: dict[str, GenreTemplate] = {
    "xianhua": GenreTemplate(
        template_name="xianhua",
        template_description="仙侠小说：修仙世界观，主角从凡人修炼成仙",
        genre=NovelGenreType.XIANHUA,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.XIANHUA,
            world_setting_type=WorldSettingType.HIGH_FANTASY,
            magic_tech_level=MagicTechnologyLevel.HIGH,
            geography_importance=0.6,
            politics_importance=0.4,
            culture_importance=0.7,
            history_importance=0.8,
            magic_system_importance=1.0,
            social_structure_importance=0.6,
            requires_cultivation_system=True,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.XIANHUA,
            common_archetypes=["主角", "师傅", "师兄/师姐", "反派", "红颜知己"],
            allows_gray_characters=True,
            requires_strong_protagonist=True,
            allows_weak_to_strong=True,
            common_relationship_patterns=["师徒", "同门", "道友", "敌人"],
            romance_importance=RomanceType.SUBPLOT_ROMANCE,
            min_key_characters=8,
            max_key_characters=25,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.XIANHUA,
            recommended_structure=PlotStructureType.THREE_ACT,
            allows_multiple_plots=True,
            plot_complexity="complex",
            typical_pacing="moderate",
            chapter_hook_style="cliffhanger",
            common_plot_tropes=["修炼突破", "秘境探险", "门派纷争", "神兵利器", "逆天改命"],
            required_themes=["成长", "坚持", "机缘", "天道"],
            taboo_themes=[],
            primary_conflict_type=ConflictType.EXTERNAL,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.XIANHUA,
            typical_narrative_voice="third_limited",
            allows_multiple_pov=True,
            typical_tones=["epic", "dramatic", "mysterious"],
            tone_flexibility=0.4,
            typical_description_density="rich",
            typical_dialogue_ratio=0.25,
            internal_thought_typical=0.15,
            common_style_elements=["古风", "诗意", "宏大"],
            genre_specific_vocabulary=["灵气", "金丹", "元婴", "渡劫", "功法", "法宝"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.XIANHUA,
            primary_tone="epic",
            secondary_tones=["dramatic", "mysterious", "romantic"],
            emotional_intensity="high",
            allows_humor=True,
            allows_tragedy=True,
            typical_severity="serious",
        ),
        target_audience=TargetAudience.NEW_ADULT,
    ),
    "yuanman": GenreTemplate(
        template_name="yuanman",
        template_description="玄幻小说：异世界冒险，充满魔法与奇幻元素",
        genre=NovelGenreType.YUANMAN,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.YUANMAN,
            world_setting_type=WorldSettingType.HIGH_FANTASY,
            magic_tech_level=MagicTechnologyLevel.HIGH,
            geography_importance=0.8,
            politics_importance=0.5,
            culture_importance=0.6,
            history_importance=0.7,
            magic_system_importance=1.0,
            social_structure_importance=0.5,
            requires_cultivation_system=False,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.YUANMAN,
            common_archetypes=["穿越者", "勇者", "魔王", "公主", "导师"],
            allows_gray_characters=True,
            requires_strong_protagonist=True,
            allows_weak_to_strong=True,
            common_relationship_patterns=["冒险搭档", "主仆", "师徒", "宿敌"],
            romance_importance=RomanceType.SUBPLOT_ROMANCE,
            min_key_characters=6,
            max_key_characters=20,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.YUANMAN,
            recommended_structure=PlotStructureType.HEROS_JOURNEY,
            allows_multiple_plots=True,
            plot_complexity="complex",
            typical_pacing="moderate",
            chapter_hook_style="cliffhanger",
            common_plot_tropes=["异世界召唤", "升级系统", "公会任务", "魔王战役"],
            required_themes=["成长", "友情", "正义"],
            taboo_themes=[],
            primary_conflict_type=ConflictType.EXTERNAL,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.YUANMAN,
            typical_narrative_voice="third_limited",
            allows_multiple_pov=True,
            typical_tones=["epic", "dramatic", "light"],
            tone_flexibility=0.5,
            typical_description_density="rich",
            typical_dialogue_ratio=0.3,
            internal_thought_typical=0.1,
            common_style_elements=["冒险感", "热血", "奇幻"],
            genre_specific_vocabulary=["魔法", "斗气", "魔兽", "勇者", "魔王"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.YUANMAN,
            primary_tone="epic",
            secondary_tones=["dramatic", "light"],
            emotional_intensity="high",
            allows_humor=True,
            allows_tragedy=True,
            typical_severity="moderate",
        ),
        target_audience=TargetAudience.NEW_ADULT,
    ),
    "dushi": GenreTemplate(
        template_name="dushi",
        template_description="都市小说：现代城市背景，贴近现实生活",
        genre=NovelGenreType.DUSHI,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.DUSHI,
            world_setting_type=WorldSettingType.URBAN_MODERN,
            magic_tech_level=MagicTechnologyLevel.MEDIUM,
            geography_importance=0.4,
            politics_importance=0.6,
            culture_importance=0.7,
            history_importance=0.3,
            magic_system_importance=0.2,
            social_structure_importance=0.9,
            requires_modern_technology=True,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.DUSHI,
            common_archetypes=["普通人", "商界精英", "职场新人", "富二代", "女神"],
            allows_gray_characters=True,
            requires_strong_protagonist=True,
            allows_weak_to_strong=True,
            common_relationship_patterns=["职场关系", "青梅竹马", "商战对手", "闺蜜"],
            romance_importance=RomanceType.PRIMARY_ROMANCE,
            min_key_characters=5,
            max_key_characters=15,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.DUSHI,
            recommended_structure=PlotStructureType.THREE_ACT,
            allows_multiple_plots=True,
            plot_complexity="moderate",
            typical_pacing="moderate",
            chapter_hook_style="reveal",
            common_plot_tropes=["逆袭", "创业", "豪门恩怨", "职场风云"],
            required_themes=["奋斗", "爱情", "现实"],
            taboo_themes=[],
            primary_conflict_type=ConflictType.SOCIAL,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.DUSHI,
            typical_narrative_voice="third_limited",
            allows_multiple_pov=True,
            typical_tones=["dramatic", "romantic", "light"],
            tone_flexibility=0.6,
            typical_description_density="moderate",
            typical_dialogue_ratio=0.4,
            internal_thought_typical=0.15,
            common_style_elements=["现代感", "都市气息", "写实"],
            genre_specific_vocabulary=["总裁", "豪门", "职场", "创业"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.DUSHI,
            primary_tone="dramatic",
            secondary_tones=["romantic", "light"],
            emotional_intensity="moderate",
            allows_humor=True,
            allows_tragedy=True,
            typical_severity="moderate",
        ),
        target_audience=TargetAudience.NEW_ADULT,
    ),
    "yanqing": GenreTemplate(
        template_name="yanqing",
        template_description="言情小说：以爱情为主线，情感描写细腻",
        genre=NovelGenreType.YANQING,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.YANQING,
            world_setting_type=WorldSettingType.REALISTIC,
            magic_tech_level=MagicTechnologyLevel.NONE,
            geography_importance=0.3,
            politics_importance=0.2,
            culture_importance=0.5,
            history_importance=0.2,
            magic_system_importance=0.0,
            social_structure_importance=0.6,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.YANQING,
            common_archetypes=["女主角", "男主角", "闺蜜", "情敌", "家人"],
            allows_gray_characters=False,
            requires_strong_protagonist=False,
            allows_weak_to_strong=False,
            common_relationship_patterns=["恋人", "闺蜜", "家人", "情敌"],
            romance_importance=RomanceType.PRIMARY_ROMANCE,
            min_key_characters=4,
            max_key_characters=10,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.YANQING,
            recommended_structure=PlotStructureType.ROMANCE_STRUCTURE,
            allows_multiple_plots=False,
            plot_complexity="simple",
            typical_pacing="slow",
            chapter_hook_style="reveal",
            common_plot_tropes=["命中注定", "先婚后爱", "暗恋成真", "破镜重圆"],
            required_themes=["爱情", "成长", "信任"],
            taboo_themes=["婚外情"],
            primary_conflict_type=ConflictType.RELATIONSHIP,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.YANQING,
            typical_narrative_voice="third_limited",
            allows_multiple_pov=True,
            typical_tones=["romantic", "lyrical", "intimate"],
            tone_flexibility=0.3,
            typical_description_density="moderate",
            typical_dialogue_ratio=0.45,
            internal_thought_typical=0.2,
            common_style_elements=["细腻", "温柔", "情感丰富"],
            genre_specific_vocabulary=["心动", "喜欢", "爱意", "吻", "拥抱"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.YANQING,
            primary_tone="romantic",
            secondary_tones=["lyrical", "intimate"],
            emotional_intensity="high",
            allows_humor=True,
            allows_tragedy=False,
            typical_severity="light",
        ),
        target_audience=TargetAudience.YOUNG_ADULT,
    ),
    "xuanyi": GenreTemplate(
        template_name="xuanyi",
        template_description="悬疑小说：充满谜团和反转，紧张刺激",
        genre=NovelGenreType.XUANYI,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.XUANYI,
            world_setting_type=WorldSettingType.REALISTIC,
            magic_tech_level=MagicTechnologyLevel.NONE,
            geography_importance=0.4,
            politics_importance=0.3,
            culture_importance=0.4,
            history_importance=0.3,
            magic_system_importance=0.0,
            social_structure_importance=0.5,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.XUANYI,
            common_archetypes=["侦探", "嫌疑人", "受害者", "证人", "幕后黑手"],
            allows_gray_characters=True,
            requires_strong_protagonist=True,
            allows_weak_to_strong=False,
            common_relationship_patterns=["侦探搭档", "委托人", "对手"],
            romance_importance=RomanceType.NONE,
            min_key_characters=5,
            max_key_characters=15,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.XUANYI,
            recommended_structure=PlotStructureType.MYSTERY_STRUCTURE,
            allows_multiple_plots=False,
            plot_complexity="complex",
            typical_pacing="slow",
            chapter_hook_style="cliffhanger",
            common_plot_tropes=["密室杀人", "不在场证明", "心理博弈", "真相揭露"],
            required_themes=["真相", "正义", "信任"],
            taboo_themes=[],
            primary_conflict_type=ConflictType.EXTERNAL,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.XUANYI,
            typical_narrative_voice="third_limited",
            allows_multiple_pov=True,
            typical_tones=["mysterious", "suspenseful", "dark"],
            tone_flexibility=0.3,
            typical_description_density="moderate",
            typical_dialogue_ratio=0.35,
            internal_thought_typical=0.15,
            common_style_elements=["紧张感", "压抑", "层层迷雾"],
            genre_specific_vocabulary=["嫌疑", "证据", "推理", "真相", "谜团"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.XUANYI,
            primary_tone="mysterious",
            secondary_tones=["suspenseful", "dark"],
            emotional_intensity="moderate",
            allows_humor=False,
            allows_tragedy=True,
            typical_severity="serious",
        ),
        target_audience=TargetAudience.ADULT,
    ),
    "kehuan": GenreTemplate(
        template_name="kehuan",
        template_description="科幻小说：基于科学与技术，展望未来",
        genre=NovelGenreType.KEHAN,
        world_config=GenreWorldConfig(
            genre=NovelGenreType.KEHAN,
            world_setting_type=WorldSettingType.SCI_FI_WORLD,
            magic_tech_level=MagicTechnologyLevel.ULTRA,
            geography_importance=0.5,
            politics_importance=0.6,
            culture_importance=0.5,
            history_importance=0.4,
            magic_system_importance=0.0,
            social_structure_importance=0.7,
        ),
        character_template=GenreCharacterTemplate(
            genre=NovelGenreType.KEHAN,
            common_archetypes=["科学家", "宇航员", "AI", "指挥官", "异星生命"],
            allows_gray_characters=True,
            requires_strong_protagonist=True,
            allows_weak_to_strong=False,
            common_relationship_patterns=["队友", "指挥官", "人工智能", "外星文明"],
            romance_importance=RomanceType.SUBPLOT_ROMANCE,
            min_key_characters=4,
            max_key_characters=15,
        ),
        plot_config=GenrePlotConfig(
            genre=NovelGenreType.KEHAN,
            recommended_structure=PlotStructureType.THREE_ACT,
            allows_multiple_plots=True,
            plot_complexity="complex",
            typical_pacing="moderate",
            chapter_hook_style="reveal",
            common_plot_tropes=["星际探索", "时间旅行", "人工智能", "文明碰撞"],
            required_themes=["探索", "生存", "人性"],
            taboo_themes=[],
            primary_conflict_type=ConflictType.EXTERNAL,
        ),
        style_config=GenreStyleConfig(
            genre=NovelGenreType.KEHAN,
            typical_narrative_voice="third_omniscient",
            allows_multiple_pov=True,
            typical_tones=["epic", "dramatic", "mysterious"],
            tone_flexibility=0.5,
            typical_description_density="high",
            typical_dialogue_ratio=0.3,
            internal_thought_typical=0.1,
            common_style_elements=["科技感", "未来感", "宏大"],
            genre_specific_vocabulary=["飞船", "星系", "人工智能", "量子", "星际"],
        ),
        tone_config=GenreToneConfig(
            genre=NovelGenreType.KEHAN,
            primary_tone="epic",
            secondary_tones=["dramatic", "mysterious"],
            emotional_intensity="moderate",
            allows_humor=True,
            allows_tragedy=True,
            typical_severity="serious",
        ),
        target_audience=TargetAudience.ADULT,
    ),
}


class NovelGenreEngine:
    """Engine for handling novel genre-specific configurations."""

    def __init__(self):
        """Initialize the novel genre engine."""
        self._templates = dict(GENRE_TEMPLATES)

    def get_template(self, genre_name: str) -> Optional[GenreTemplate]:
        """Get a genre template by name.

        Args:
            genre_name: Genre name (e.g., "xianhua", "dushi")

        Returns:
            GenreTemplate if found, None otherwise
        """
        return self._templates.get(genre_name.lower())

    def get_all_templates(self) -> dict[str, GenreTemplate]:
        """Get all available genre templates."""
        return self._templates.copy()

    def create_genre_profile(self, genre: NovelGenreType) -> NovelGenreProfile:
        """Create a genre profile for a specific genre.

        Args:
            genre: Novel genre type

        Returns:
            NovelGenreProfile with full genre configuration
        """
        template = self._templates.get(genre.value)
        if template:
            return template.to_genre_profile()

        # Create default profile if no template exists
        return self._create_default_profile(genre)

    def _create_default_profile(self, genre: NovelGenreType) -> NovelGenreProfile:
        """Create a default genre profile."""
        return NovelGenreProfile(
            genre=genre,
            world_config=GenreWorldConfig(
                genre=genre,
                world_setting_type=WorldSettingType.REALISTIC,
                magic_tech_level=MagicTechnologyLevel.MEDIUM,
            ),
            character_template=GenreCharacterTemplate(
                genre=genre,
                common_archetypes=[],
                romance_importance=RomanceType.NONE,
            ),
            plot_config=GenrePlotConfig(
                genre=genre,
                recommended_structure=PlotStructureType.THREE_ACT,
                plot_complexity="moderate",
                typical_pacing="moderate",
                chapter_hook_style="cliffhanger",
            ),
            style_config=GenreStyleConfig(
                genre=genre,
                typical_narrative_voice="third_limited",
                typical_tones=["dramatic"],
                typical_description_density="moderate",
                typical_dialogue_ratio=0.3,
            ),
            tone_config=GenreToneConfig(
                genre=genre,
                primary_tone="dramatic",
                emotional_intensity="moderate",
                allows_humor=True,
                allows_tragedy=True,
                typical_severity="moderate",
            ),
        )

    def detect_genre_from_content(
        self,
        content: str,
    ) -> GenreAnalysisResult:
        """Detect the genre of a novel based on its content.

        Args:
            content: Novel content to analyze

        Returns:
            GenreAnalysisResult with detected genre and confidence
        """
        # Genre-specific keyword sets
        genre_keywords = {
            NovelGenreType.XIANHUA: [
                "修仙", "灵气", "金丹", "元婴", "渡劫", "飞升", "宗门", "功法",
                "师兄", "师姐", "师妹", "妖修", "魔族", "仙界", "凡界", "天劫"
            ],
            NovelGenreType.YUANMAN: [
                "异世界", "魔法", "斗气", "勇者", "魔王", "公会", "技能",
                "升级", "副本", "魔兽", "精灵", "矮人", "龙族", "剑与魔法"
            ],
            NovelGenreType.DUSHI: [
                "城市", "公司", "创业", "职场", "总裁", "老板", "同事",
                "商业", "谈判", "合同", "赚钱", "买房", "都市", "现代"
            ],
            NovelGenreType.YANQING: [
                "心动", "喜欢", "爱", "接吻", "拥抱", "告白", "约会",
                "恋人", "男友", "女友", "约会", "浪漫", "甜蜜", "眼泪"
            ],
            NovelGenreType.XUANYI: [
                "死亡", "谋杀", "嫌疑", "证据", "推理", "侦探", "真相",
                "秘密", "阴谋", "谜团", "线索", "调查", "追查", "凶手"
            ],
            NovelGenreType.KEHAN: [
                "飞船", "星际", "宇宙", "星球", "科技", "人工智能", "机器人",
                "太空", "星系", "能量", "量子", "维度", "外星", "探索"
            ],
        }

        # Count keyword matches
        genre_scores: dict[str, float] = {}
        for genre, keywords in genre_keywords.items():
            score = sum(content.count(kw) for kw in keywords)
            genre_scores[genre.value] = score

        # Normalize and find best match
        total = sum(genre_scores.values())
        if total > 0:
            normalized_scores = {k: v / total for k, v in genre_scores.items()}
        else:
            normalized_scores = {k: 0.0 for k in genre_scores.keys()}

        # Find highest scoring genre
        best_genre = max(normalized_scores, key=normalized_scores.get)
        best_score = normalized_scores.get(best_genre, 0.0)

        # Convert to enum
        detected = NovelGenreType(best_genre) if best_score > 0 else NovelGenreType.DUSHI

        # Generate recommendations
        recommendations = []
        if best_score < 0.3:
            recommendations.append("Consider adding more genre-specific keywords for better classification")
        if best_score > 0.5:
            recommendations.append(f"Strong {detected.value} genre markers detected")

        return GenreAnalysisResult(
            detected_genre=detected,
            confidence=best_score,
            genre_evidence=normalized_scores,
            recommendations=recommendations,
        )

    def detect_genre_from_title(
        self,
        title: str,
    ) -> list[tuple[NovelGenreType, float]]:
        """Detect possible genres from novel title.

        Args:
            title: Novel title

        Returns:
            List of (genre, confidence) tuples sorted by confidence
        """
        # Title patterns for each genre
        title_patterns = {
            NovelGenreType.XIANHUA: [
                r"仙[侠道]", r"修[仙炼]", r"飞升", r"金丹", r"元婴", r"凡人流",
                r"综仙侠", r"仙府", r"宗门",
            ],
            NovelGenreType.YUANMAN: [
                r"玄幻", r"异世", r"魔法", r"勇者", r"魔王", r"召唤", r"系统流",
                r"综武", r"无限流",
            ],
            NovelGenreType.DUSHI: [
                r"都市", r"职场", r"创业", r"商战", r"总裁", r"豪门", r"逆袭",
            ],
            NovelGenreType.YANQING: [
                r"言情", r"甜文", r"宠文", r"婚恋", r"恋爱", r"love",
            ],
            NovelGenreType.XUANYI: [
                r"悬疑", r"推理", r"侦探", r"罪案", r"惊悚", r"心理",
            ],
            NovelGenreType.KEHAN: [
                r"星际", r"科幻", r"太空", r"未来", r"科技", r"赛博",
            ],
        }

        results: list[tuple[NovelGenreType, float]] = []
        for genre, patterns in title_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, title, re.IGNORECASE):
                    score += 1.0
            if score > 0:
                results.append((genre, min(1.0, score / len(patterns))))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def recommend_genre_for_plot(
        self,
        plot_keywords: list[str],
    ) -> list[GenreRecommendation]:
        """Recommend genres based on plot keywords.

        Args:
            plot_keywords: Keywords describing the plot

        Returns:
            List of genre recommendations sorted by priority
        """
        plot_to_genre = {
            "修仙": NovelGenreType.XIANHUA,
            "异世界": NovelGenreType.YUANMAN,
            "都市": NovelGenreType.DUSHI,
            "爱情": NovelGenreType.YANQING,
            "悬疑": NovelGenreType.XUANYI,
            "推理": NovelGenreType.XUANYI,
            "科幻": NovelGenreType.KEHAN,
            "未来": NovelGenreType.KEHAN,
            "冒险": NovelGenreType.YUANMAN,
            "战斗": NovelGenreType.YUANMAN,
            "商战": NovelGenreType.DUSHI,
            "职场": NovelGenreType.DUSHI,
        }

        genre_counts: dict[NovelGenreType, int] = {}
        for keyword in plot_keywords:
            if keyword in plot_to_genre:
                genre = plot_to_genre[keyword]
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        recommendations = []
        for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
            template = self._templates.get(genre.value)
            recommendations.append(GenreRecommendation(
                genre=genre,
                priority=min(100, count * 20),
                reason=f"Matches {count} plot keyword(s)",
                expected_appeal=f"{template.template_description if template else 'Unknown genre'}",
            ))

        return recommendations

    def apply_genre_to_novel(
        self,
        novel: Novel,
        genre: NovelGenreType,
    ) -> Novel:
        """Apply genre settings to a novel object.

        Args:
            novel: Novel to modify
            genre: Genre to apply

        Returns:
            Modified novel with genre settings
        """
        profile = self.create_genre_profile(genre)

        # Update novel genre field
        novel.genre = genre.value

        return novel

    def get_genre_summary(
        self,
        genre: NovelGenreType,
    ) -> str:
        """Get a human-readable summary of a genre.

        Args:
            genre: Genre to summarize

        Returns:
            Summary string
        """
        template = self._templates.get(genre.value)
        if not template:
            return f"Genre: {genre.value}"

        parts = [
            f"【{template.template_description}】",
            "",
            f"世界观类型: {template.world_config.world_setting_type.value}",
            f"魔法/科技水平: {template.world_config.magic_tech_level.value}",
            "",
            f"推荐结构: {template.plot_config.recommended_structure.value}",
            f"典型节奏: {template.plot_config.typical_pacing}",
            f"章节钩子: {template.plot_config.chapter_hook_style}",
            "",
            f"叙事风格: {template.style_config.typical_narrative_voice}",
            f"基调: {', '.join(template.style_config.typical_tones)}",
            f"对话比例: {template.style_config.typical_dialogue_ratio:.0%}",
            "",
            f"目标读者: {template.target_audience.value}",
        ]

        return "\n".join(parts)

    def get_all_genres(self) -> list[NovelGenreType]:
        """Get all available genre types."""
        return list(NovelGenreType)

    def get_genres_by_category(self) -> dict[str, list[NovelGenreType]]:
        """Get genres organized by category."""
        return {
            "Chinese Web Novels": [
                NovelGenreType.XIANHUA,
                NovelGenreType.YUANMAN,
                NovelGenreType.DUSHI,
                NovelGenreType.YANQING,
                NovelGenreType.XUANYI,
                NovelGenreType.KEHAN,
                NovelGenreType.LISHI,
                NovelGenreType.JUNSHI,
                NovelGenreType.YOUXI,
                NovelGenreType.JINGJI,
                NovelGenreType.QINGXIAOSHUO,
                NovelGenreType.TONGREN,
                NovelGenreType.DANMEI,
                NovelGenreType.BAIHE,
                NovelGenreType.NVZUN,
                NovelGenreType.ZHICHANG,
            ],
            "Western Genres": [
                NovelGenreType.FANTASY,
                NovelGenreType.SCI_FI,
                NovelGenreType.URBAN_FANTASY,
                NovelGenreType.ROMANCE,
                NovelGenreType.MYSTERY,
                NovelGenreType.THRILLER,
                NovelGenreType.HORROR,
                NovelGenreType.LITERARY,
                NovelGenreType.ACTION,
                NovelGenreType.HISTORICAL_FICTION,
            ],
        }
