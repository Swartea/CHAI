"""Scene description engine for generating environment, atmosphere, and visual details."""

from typing import Optional
from chai.models import Novel, WorldSetting
from chai.models.scene_description import (
    SceneDescriptionPlan, SceneDescriptionDraft, SceneDescriptionRevision,
    SceneDescriptionAnalysis, SceneDescriptionTemplate,
    EnvironmentType, AtmosphereType, LightingCondition, TimeOfDay,
    EnvironmentDetail, LightingDetail, WeatherDetail, VisualDetail,
    SensoryDetail, AtmosphereDetail, SpatialLayout, WeatherCondition
)
from chai.services import AIService


class SceneDescriptionEngine:
    """Engine for generating rich scene descriptions."""

    # Pre-built templates for common scene types
    TEMPLATES: dict[str, SceneDescriptionTemplate] = {
        "dark_forest": SceneDescriptionTemplate(
            name="黑暗森林",
            environment_type=EnvironmentType.NATURAL,
            atmosphere_type=AtmosphereType.OMINOUS,
            lighting_condition=LightingCondition.DARK,
            visual_detail_types=["color", "texture", "shadow", "space"],
            sensory_detail_types=["sound", "touch", "smell"],
            description_length="medium",
            typical_focus=["树木", "阴影", "神秘声音", "危险气息"]
        ),
        "grand_hall": SceneDescriptionTemplate(
            name="宏伟大厅",
            environment_type=EnvironmentType.INDOOR,
            atmosphere_type=AtmosphereType.EPIC,
            lighting_condition=LightingCondition.DRAMATIC,
            visual_detail_types=["size", "light", "shadow", "detail"],
            sensory_detail_types=["sound", "touch", "smell"],
            description_length="long",
            typical_focus=["高耸的穹顶", "光影效果", "回声", "石材质感"]
        ),
        "peaceful_meadow": SceneDescriptionTemplate(
            name="宁静草原",
            environment_type=EnvironmentType.NATURAL,
            atmosphere_type=AtmosphereType.PEACEFUL,
            lighting_condition=LightingCondition.SOFT,
            visual_detail_types=["color", "texture", "movement", "space"],
            sensory_detail_types=["sound", "smell", "touch"],
            description_length="medium",
            typical_focus=["草地颜色", "微风", "花香", "开阔视野"]
        ),
        "mysterious_castle": SceneDescriptionTemplate(
            name="神秘城堡",
            environment_type=EnvironmentType.INDOOR,
            atmosphere_type=AtmosphereType.MYSTERIOUS,
            lighting_condition=LightingCondition.DIM,
            visual_detail_types=["shadow", "texture", "space", "detail"],
            sensory_detail_types=["sound", "touch", "smell"],
            description_length="long",
            typical_focus=["阴暗角落", "回廊", "尘埃", "古老气息"]
        ),
        "busy_market": SceneDescriptionTemplate(
            name="热闹市集",
            environment_type=EnvironmentType.URBAN,
            atmosphere_type=AtmosphereType.JOYFUL,
            lighting_condition=LightingCondition.BRIGHT,
            visual_detail_types=["color", "movement", "detail"],
            sensory_detail_types=["sound", "smell", "taste"],
            description_length="medium",
            typical_focus=["人流", "商品", "叫卖声", "各种气味"]
        ),
        "stormy_sea": SceneDescriptionTemplate(
            name="风暴海面",
            environment_type=EnvironmentType.OUTDOOR,
            atmosphere_type=AtmosphereType.TENSE,
            lighting_condition=LightingCondition.DRAMATIC,
            visual_detail_types=["movement", "color", "light", "shadow"],
            sensory_detail_types=["sound", "touch", "smell"],
            description_length="long",
            typical_focus=["浪涛", "闪电", "狂风", "雨幕"]
        ),
        "romantic_garden": SceneDescriptionTemplate(
            name="浪漫花园",
            environment_type=EnvironmentType.NATURAL,
            atmosphere_type=AtmosphereType.ROMANTIC,
            lighting_condition=LightingCondition.SUNSET,
            visual_detail_types=["color", "texture", "light", "detail"],
            sensory_detail_types=["smell", "sound", "touch"],
            description_length="medium",
            typical_focus=["花朵", "光线", "香气", "隐私感"]
        ),
        "tense_negotiation": SceneDescriptionTemplate(
            name="紧张谈判",
            environment_type=EnvironmentType.INDOOR,
            atmosphere_type=AtmosphereType.TENSE,
            lighting_condition=LightingCondition.ARTIFICIAL,
            visual_detail_types=["detail", "movement", "space"],
            sensory_detail_types=["sound", "touch"],
            description_length="short",
            typical_focus=["表情", "手势", "沉默", "张力"]
        ),
        "battlefield": SceneDescriptionTemplate(
            name="战场",
            environment_type=EnvironmentType.OUTDOOR,
            atmosphere_type=AtmosphereType.GRIM,
            lighting_condition=LightingCondition.DRAMATIC,
            visual_detail_types=["movement", "color", "shadow"],
            sensory_detail_types=["sound", "smell", "touch"],
            description_length="long",
            typical_focus=["混乱", "硝烟", "血迹", "喊杀声"]
        ),
        "cozy_tavern": SceneDescriptionTemplate(
            name="温馨酒馆",
            environment_type=EnvironmentType.INDOOR,
            atmosphere_type=AtmosphereType.COMIC,
            lighting_condition=LightingCondition.SOFT,
            visual_detail_types=["color", "texture", "detail"],
            sensory_detail_types=["sound", "smell", "taste"],
            description_length="medium",
            typical_focus=["暖光", "木质装潢", "酒香", "喧闹"]
        ),
    }

    def __init__(self, ai_service: AIService):
        """Initialize scene description engine."""
        self.ai_service = ai_service

    async def generate_description(
        self,
        scene_id: str,
        scene_location: str,
        time_setting: TimeOfDay,
        environment_type: EnvironmentType,
        atmosphere_type: AtmosphereType,
        lighting_condition: LightingCondition = LightingCondition.DIM,
        world_setting: Optional[WorldSetting] = None,
        previous_scene_description: Optional[str] = None,
        narrative_perspective: str = "third_person",
        description_length: str = "medium",
        custom_focus: Optional[list[str]] = None,
        weather_condition: Optional[WeatherCondition] = None,
    ) -> SceneDescriptionDraft:
        """Generate a complete scene description.

        Args:
            scene_id: Unique scene identifier
            scene_location: Location name/description
            time_setting: Time of day
            environment_type: Type of environment
            atmosphere_type: Desired atmosphere/mood
            lighting_condition: Lighting conditions
            world_setting: Optional world setting for contextual details
            previous_scene_description: Previous scene description for continuity
            narrative_perspective: third_person or character_centric
            description_length: brief, short, medium, long
            custom_focus: Custom focus areas for the description
            weather_condition: Optional weather conditions

        Returns:
            SceneDescriptionDraft with all generated components
        """
        # Build the plan
        plan = self._build_plan(
            scene_id=scene_id,
            scene_location=scene_location,
            time_setting=time_setting,
            environment_type=environment_type,
            atmosphere_type=atmosphere_type,
            lighting_condition=lighting_condition,
            weather_condition=weather_condition,
            narrative_perspective=narrative_perspective,
            description_length=description_length,
            custom_focus=custom_focus,
        )

        # Generate each component
        env_desc = await self._generate_environment_description(plan, world_setting)
        atmos_desc = await self._generate_atmosphere_description(plan)
        visual_desc = await self._generate_visual_details(plan)
        sensory_desc = await self._generate_sensory_details(plan)

        # Combine into flowing description
        combined = await self._combine_descriptions(
            env_desc=env_desc,
            atmos_desc=atmos_desc,
            visual_desc=visual_desc,
            sensory_desc=sensory_desc,
            plan=plan,
            world_setting=world_setting,
            previous_scene=previous_scene_description,
        )

        draft = SceneDescriptionDraft(
            plan=plan,
            environment_description=env_desc,
            atmosphere_description=atmos_desc,
            visual_details_description=visual_desc,
            sensory_description=sensory_desc,
            combined_description=combined,
            word_count=len(combined),
            status="draft"
        )

        return draft

    def _build_plan(
        self,
        scene_id: str,
        scene_location: str,
        time_setting: TimeOfDay,
        environment_type: EnvironmentType,
        atmosphere_type: AtmosphereType,
        lighting_condition: LightingCondition,
        weather_condition: Optional[WeatherCondition],
        narrative_perspective: str,
        description_length: str,
        custom_focus: Optional[list[str]],
    ) -> SceneDescriptionPlan:
        """Build a scene description plan."""
        # Create environment detail
        env_detail = EnvironmentDetail(
            environment_type=environment_type,
            location_name=scene_location,
        )

        # Create lighting detail
        light_detail = LightingDetail(
            condition=lighting_condition,
            light_source=self._get_light_source(time_setting, lighting_condition),
        )

        # Create weather detail if applicable
        weather_detail = None
        if weather_condition:
            weather_detail = WeatherDetail(condition=weather_condition)

        # Create visual detail
        visual_detail = VisualDetail(
            detail_types=["COLOR", "TEXTURE", "SPACE", "DETAIL"],
            color_palette=self._get_color_palette(atmosphere_type),
        )

        # Create sensory detail
        sensory_detail = SensoryDetail(
            detail_types=["SOUND", "SMELL", "TOUCH"],
        )

        # Create atmosphere detail
        atmos_detail = AtmosphereDetail(
            atmosphere_type=atmosphere_type,
            atmosphere_intensity="medium",
            emotional_tone=self._get_emotional_tones(atmosphere_type),
            pacing_quality="moderate",
            tension_level="low",
        )

        return SceneDescriptionPlan(
            scene_id=scene_id,
            scene_location=scene_location,
            time_setting=time_setting,
            environment=env_detail,
            lighting=light_detail,
            weather=weather_detail,
            visual=visual_detail,
            sensory=sensory_detail,
            atmosphere=atmos_detail,
            description_length=description_length,
            description_focus=custom_focus or [],
            narrative_perspective=narrative_perspective,
        )

    def _get_light_source(
        self, time: TimeOfDay, condition: LightingCondition
    ) -> str:
        """Get appropriate light source description."""
        sources = {
            TimeOfDay.DAWN: "柔和的晨光",
            TimeOfDay.MORNING: "明亮的日光",
            TimeOfDay.NOON: "强烈的正午阳光",
            TimeOfDay.AFTERNOON: "温暖的午后光线",
            TimeOfDay.EVENING: "橘红色的夕阳",
            TimeOfDay.NIGHT: "月光或星光",
            TimeOfDay.MIDNIGHT: "微弱的月光",
        }
        if condition == LightingCondition.ARTIFICIAL:
            return "人工光源"
        return sources.get(time, "自然光")

    def _get_color_palette(self, atmosphere: AtmosphereType) -> list[str]:
        """Get appropriate color palette for atmosphere."""
        palettes = {
            AtmosphereType.TENSE: ["灰", "暗红", "黑色"],
            AtmosphereType.PEACEFUL: ["蓝", "绿", "淡黄"],
            AtmosphereType.MYSTERIOUS: ["深紫", "黑色", "银色"],
            AtmosphereType.OMINOUS: ["黑色", "暗红", "灰色"],
            AtmosphereType.JOYFUL: ["金色", "橙色", "明黄"],
            AtmosphereType.SAD: ["灰色", "蓝色", "暗色"],
            AtmosphereType.ROMANTIC: ["粉红", "金色", "玫瑰色"],
            AtmosphereType.DANGEROUS: ["红色", "黑色", "暗色"],
            AtmosphereType.EPIC: ["金色", "白色", "蓝色"],
            AtmosphereType.LYRICAL: ["紫色", "淡蓝", "银色"],
            AtmosphereType.GRIM: ["黑色", "灰色", "暗红"],
            AtmosphereType.HOPEFUL: ["金色", "白色", "亮色"],
            AtmosphereType.NOSTALGIC: ["泛黄", "棕色", "暖色"],
            AtmosphereType.EERIE: ["绿色", "灰白", "银色"],
            AtmosphereType.COMIC: ["明亮", "鲜艳", "暖色"],
            AtmosphereType.DRAMATIC: ["红色", "黑色", "金色"],
        }
        return palettes.get(atmosphere, ["自然色"])

    def _get_emotional_tones(self, atmosphere: AtmosphereType) -> list[str]:
        """Get emotional tones for atmosphere."""
        tones = {
            AtmosphereType.TENSE: ["紧张", "不安", "压迫感"],
            AtmosphereType.PEACEFUL: ["宁静", "放松", "平和"],
            AtmosphereType.MYSTERIOUS: ["神秘", "好奇", "未知"],
            AtmosphereType.OMINOUS: ["不祥", "恐惧", "威胁"],
            AtmosphereType.JOYFUL: ["快乐", "欢快", "喜悦"],
            AtmosphereType.SAD: ["悲伤", "忧郁", "沉重"],
            AtmosphereType.ROMANTIC: ["浪漫", "温馨", "甜蜜"],
            AtmosphereType.DANGEROUS: ["危险", "紧张", "恐惧"],
            AtmosphereType.EPIC: ["壮观", "震撼", "宏伟"],
            AtmosphereType.LYRICAL: ["优美", "诗意", "柔和"],
            AtmosphereType.GRIM: ["残酷", "黑暗", "绝望"],
            AtmosphereType.HOPEFUL: ["希望", "期待", "光明"],
            AtmosphereType.NOSTALGIC: ["怀念", "惆怅", "温馨"],
            AtmosphereType.EERIE: ["诡异", "不安", "毛骨悚然"],
            AtmosphereType.COMIC: ["轻松", "幽默", "愉快"],
            AtmosphereType.DRAMATIC: ["激烈", "动情", "戏剧性"],
        }
        return tones.get(atmosphere, ["中性"])

    async def _generate_environment_description(
        self,
        plan: SceneDescriptionPlan,
        world_setting: Optional[WorldSetting],
    ) -> str:
        """Generate environment/setting description."""
        prompt = f"""描述场景：{plan.scene_location}
环境类型：{plan.environment.value}
空间布局：{plan.environment.spatial_layout.value}

时间：{plan.time_setting.value}
光照：{plan.lighting.condition.value}
{plan.lighting.light_source}

{world_setting.name if world_setting else '未知世界观'}

要求：
1. 描写要有画面感，细节丰富
2. 突出环境特点和氛围
3. 字数：{plan.description_length}（brief=50-100字, short=100-200字, medium=200-400字, long=400-600字）
4. 直接输出描写文字，不要解释"""

        result = await self.ai_service.generate(prompt, temperature=0.7)
        return result.strip()

    async def _generate_atmosphere_description(
        self,
        plan: SceneDescriptionPlan,
    ) -> str:
        """Generate atmosphere/mood description."""
        prompt = f"""为以下场景营造氛围：

氛围类型：{plan.atmosphere.atmosphere_type.value}
氛围强度：{plan.atmosphere.atmosphere_intensity}
情感基调：{', '.join(plan.atmosphere.emotional_tone)}
紧张程度：{plan.atmosphere.tension_level}
叙事节奏感：{plan.atmosphere.pacing_quality}

场景位置：{plan.scene_location}

要求：
1. 通过环境细节暗示氛围
2. 不要直接说"气氛很紧张"等，要通过描写传达
3. 字数：{plan.description_length}
4. 直接输出描写文字，不要解释"""

        result = await self.ai_service.generate(prompt, temperature=0.7)
        return result.strip()

    async def _generate_visual_details(
        self,
        plan: SceneDescriptionPlan,
    ) -> str:
        """Generate visual detail description."""
        visual_types_str = ", ".join([v.value for v in plan.visual.detail_types])
        colors_str = ", ".join(plan.visual.color_palette)

        prompt = f"""描写场景中的视觉细节：

重点视觉元素：{visual_types_str}
色彩基调：{colors_str}
焦点：{plan.visual.focal_point or '整体场景'}
对比元素：{', '.join(plan.visual.visual_contrasts) if plan.visual.visual_contrasts else '明暗对比'}

场景：{plan.scene_location}
时间：{plan.time_setting.value}

要求：
1. 注重色彩、光影、质感的描写
2. 选择性描写，避免堆砌
3. 字数：{plan.description_length}
4. 直接输出描写文字，不要解释"""

        result = await self.ai_service.generate(prompt, temperature=0.7)
        return result.strip()

    async def _generate_sensory_details(
        self,
        plan: SceneDescriptionPlan,
    ) -> str:
        """Generate sensory detail description."""
        sensory_types_str = ", ".join([s.value for s in plan.sensory.detail_types])

        prompt = f"""描写场景中的感官细节（除视觉外）：

感官类型：{sensory_types_str}
声音：{', '.join(plan.sensory.sound_descriptions) if plan.sensory.sound_descriptions else '环境音'}
气味：{', '.join(plan.sensory.smell_descriptions) if plan.sensory.smell_descriptions else '无特别气味'}
触觉：{', '.join(plan.sensory.touch_descriptions) if plan.sensory.touch_descriptions else '温度感觉'}
温度感：{plan.sensory.temperature_sensation or '适中'}

场景：{plan.scene_location}
氛围：{plan.atmosphere.atmosphere_type.value}

要求：
1. 选择2-3种感官重点描写，不要全部都用
2. 感官描写要与场景和氛围协调
3. 字数：{plan.description_length}
4. 直接输出描写文字，不要解释"""

        result = await self.ai_service.generate(prompt, temperature=0.7)
        return result.strip()

    async def _combine_descriptions(
        self,
        env_desc: str,
        atmos_desc: str,
        visual_desc: str,
        sensory_desc: str,
        plan: SceneDescriptionPlan,
        world_setting: Optional[WorldSetting],
        previous_scene: Optional[str],
    ) -> str:
        """Combine all description components into a flowing scene description."""
        continuity_hint = ""
        if previous_scene:
            continuity_hint = f"\n前一场景结尾：{previous_scene[-100:]}..."

        prompt = f"""将以下场景描写片段整合成一段流畅的描写：

环境描写：
{env_desc}

氛围描写：
{atmos_desc}

视觉细节：
{visual_desc}

感官细节：
{sensory_desc}

{continuity_hint}

场景：{plan.scene_location}
世界观：{world_setting.name if world_setting else '未知'}
叙事视角：{plan.narrative_perspective}
字数要求：{plan.description_length}

要求：
1. 整合为一个自然的段落，避免割裂感
2. 不要使用"首先是...然后是…"这类过渡
3. 让各部分描写有机融合
4. 直接输出整合后的描写文字，不要解释"""

        result = await self.ai_service.generate(prompt, temperature=0.7)
        return result.strip()

    async def revise_description(
        self,
        draft: SceneDescriptionDraft,
        revision_notes: list[str],
    ) -> SceneDescriptionRevision:
        """Revise a scene description based on notes."""
        prompt = f"""请根据以下意见修改场景描写：

原文：
{draft.combined_description}

修改意见：
{chr(10).join(f"- {note}" for note in revision_notes)}

要求：
1. 按照意见进行修改
2. 保持原文的整体感觉
3. 不要大幅删减或添加内容
4. 直接输出修改后的文字，不要解释"""

        revised = await self.ai_service.generate(prompt, temperature=0.5)

        return SceneDescriptionRevision(
            original_draft=draft,
            revision_notes=revision_notes,
            revised_description=revised.strip(),
        )

    def analyze_description(
        self,
        draft: SceneDescriptionDraft,
    ) -> SceneDescriptionAnalysis:
        """Analyze a scene description for quality."""
        issues = []
        suggestions = []

        # Check length
        word_count = draft.word_count
        length = draft.plan.description_length
        expected_ranges = {
            "brief": (50, 100),
            "short": (100, 200),
            "medium": (200, 400),
            "long": (400, 600),
        }
        if length in expected_ranges:
            min_w, max_w = expected_ranges[length]
            if word_count < min_w:
                issues.append(f"描写过短（{word_count}字），少于{min_w}字")
                suggestions.append("增加更多环境细节和感官描写")
            elif word_count > max_w:
                issues.append(f"描写过长（{word_count}字），多于{max_w}字")
                suggestions.append("精简描写，突出重点")

        # Check atmosphere consistency
        atmos_types = [a.value for a in AtmosphereType]
        atmos_str = draft.atmosphere_description.lower()
        atmos_consistency = 0.5
        if any(word in atmos_str for word in draft.plan.atmosphere.atmosphere_type.value):
            atmos_consistency = 0.8

        # Check visual immersion
        visual_words = len(draft.visual_details_description)
        visual_immersion = min(1.0, visual_words / 100)

        # Check sensory balance
        sensory_words = len(draft.sensory_description)
        sensory_balance = min(1.0, sensory_words / 80)

        # Check descriptive density
        if word_count < 100:
            descriptive_density = "too_sparse"
        elif word_count < 200:
            descriptive_density = "sparse"
        elif word_count < 400:
            descriptive_density = "medium"
        elif word_count < 600:
            descriptive_density = "rich"
        else:
            descriptive_density = "too_rich"

        return SceneDescriptionAnalysis(
            scene_id=draft.plan.scene_id,
            atmosphere_consistency=atmos_consistency,
            visual_immersion=visual_immersion,
            sensory_balance=sensory_balance,
            descriptive_density=descriptive_density,
            issues=issues,
            suggestions=suggestions,
        )

    def get_template(self, template_name: str) -> Optional[SceneDescriptionTemplate]:
        """Get a scene description template by name."""
        return self.TEMPLATES.get(template_name)

    def get_all_templates(self) -> dict[str, SceneDescriptionTemplate]:
        """Get all available scene description templates."""
        return self.TEMPLATES.copy()

    async def generate_from_template(
        self,
        template_name: str,
        scene_id: str,
        scene_location: str,
        world_setting: Optional[WorldSetting] = None,
        **kwargs,
    ) -> SceneDescriptionDraft:
        """Generate scene description from a template.

        Args:
            template_name: Name of template to use
            scene_id: Scene identifier
            scene_location: Location description
            world_setting: Optional world setting
            **kwargs: Override template values (time_setting, atmosphere_type, etc.)

        Returns:
            Generated scene description draft
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Apply kwargs overrides
        time_setting = kwargs.get("time_setting", TimeOfDay.AFTERNOON)
        atmosphere_type = kwargs.get("atmosphere_type", template.atmosphere_type)
        environment_type = kwargs.get("environment_type", template.environment_type)
        lighting = kwargs.get("lighting_condition", template.lighting_condition)
        description_length = kwargs.get("description_length", template.description_length)

        return await self.generate_description(
            scene_id=scene_id,
            scene_location=scene_location,
            time_setting=time_setting,
            environment_type=environment_type,
            atmosphere_type=atmosphere_type,
            lighting_condition=lighting,
            world_setting=world_setting,
            description_length=description_length,
            custom_focus=template.typical_focus,
        )

    def export_draft(self, draft: SceneDescriptionDraft) -> dict:
        """Export draft to dictionary format."""
        return {
            "scene_id": draft.plan.scene_id,
            "scene_location": draft.plan.scene_location,
            "time": draft.plan.time_setting.value,
            "environment_type": draft.plan.environment.environment_type.value,
            "atmosphere_type": draft.plan.atmosphere.atmosphere_type.value,
            "lighting": draft.plan.lighting.condition.value,
            "combined_description": draft.combined_description,
            "word_count": draft.word_count,
            "status": draft.status,
        }
