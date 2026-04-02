"""Main character engine for protagonist-focused generation and management."""

from typing import Optional, Any
from chai.models.main_character import (
    MainCharacter,
    MainCharacterProfile,
    AppearanceDetail,
    PersonalityDimension,
    BackgroundDetail,
    MotivationDetail,
    MotivationType,
)
from chai.models import Character, CharacterRole, WorldSetting
from chai.services import AIService


class MainCharacterEngine:
    """Engine for generating and managing main characters (protagonists).

    Focuses specifically on the 4 core aspects:
    - 外貌 (Appearance): Detailed physical description
    - 性格 (Personality): Deep psychological profiling
    - 背景 (Background): Comprehensive backstory
    - 动机 (Motivation): Driving forces and internal conflicts
    """

    def __init__(self, ai_service: AIService):
        """Initialize main character engine with AI service."""
        self.ai_service = ai_service

    async def generate_main_character(
        self,
        genre: str,
        theme: str,
        world_context: Optional[dict] = None,
        plot_requirements: Optional[dict] = None,
    ) -> MainCharacter:
        """Generate a detailed main character with deep focus on 4 core aspects.

        Args:
            genre: Novel genre (fantasy, sci-fi, romance, etc.)
            theme: Central theme of the story
            world_context: Optional world context (geography, politics, culture)
            plot_requirements: Optional plot requirements affecting character design

        Returns:
            MainCharacter object with detailed settings
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        plot_req = ""
        if plot_requirements:
            plot_req = f"剧情需求：{plot_requirements}\n"

        prompt = f"""生成一个详细的主角角色设定，重点关注四个核心方面：外貌、性格、背景、动机。

类型：{genre}
主题：{theme}
{context}
{plot_req}

请生成一个完整的主角角色，以JSON格式输出：

{{
  "id": "唯一标识符",
  "name": "角色姓名",

  "age": "年龄描述（如：25岁、青年、中年等）",
  "age_numeric": 年龄数值,

  "appearance_detail": {{
    "face": "面部特征详细描写（如：棱角分明的脸庞，眉宇间带着英气）",
    "eyes": "眼睛描写（如：深邃的黑色眼眸，偶尔闪过锐利的光芒）",
    "hair": "发型发色（如：一头乌黑的短发，随风飘动）",
    "body": "体型身材（如：高大挺拔，肌肉线条分明）",
    "skin": "肤色肤质（如：古铜色肌肤，略显粗糙）",
    "dressing": "着装风格（如：简约的黑色风衣，搭配银色配饰）",
    "accessories": ["标志性配饰1", "配饰2"],
    "overall": "整体形象概述（如：第一眼就给人可靠稳重的感觉）"
  }},
  "distinguishing_features": ["显著特征1：眉心的疤痕", "特征2：左手的手套"],
  "presence": "气质/气场描述（如：沉稳内敛，不怒自威）",
  "first_impression": "他人对主角的第一印象",

  "personality_dimension": {{
    "openness": 开放度评分1-10,
    "conscientiousness": 尽责性评分1-10,
    "extraversion": 外向性评分1-10,
    "agreeableness": 宜人性评分1-10,
    "neuroticism": 神经质评分1-10
  }},
  "personality_description": "详细性格描述（200字以上）",
  "mbti": "MBTI类型（如：INTJ、ENFP等）",
  "values": ["核心价值1", "价值2"],
  "fears": ["恐惧1：害怕失去亲人", "恐惧2：害怕被背叛"],
  "desires": ["欲望1：渴望被认可", "欲望2：追求真相"],
  "strengths": ["优点1：冷静的判断力", "优点2：超强的适应能力"],
  "weaknesses": ["缺点1：过于固执", "缺点2：不擅表达感情"],
  "habits": ["习惯1：紧张时抚摸手表的边缘", "习惯2：思考时闭眼"],
  "emotional_pattern": "典型情绪反应模式（如：愤怒时沉默，悲伤时独处）",

  "background_detail": {{
    "birth_place": "出生地点",
    "birth_era": "出生时代/年代",
    "childhood": "童年经历详细描述",
    "adolescence": "青少年时期经历",
    "early_adulthood": "成年早期经历",
    "family_members": [
      {{"relation": "父亲", "name": "姓名", "description": "性格和背景"}},
      {{"relation": "母亲", "name": "姓名", "description": "性格和背景"}}
    ],
    "socioeconomic_status": "社会经济地位描述",
    "education_background": "教育背景",
    "career_path": ["职业经历1", "职业经历2"],
    "key_events": ["关键事件1", "关键事件2", "关键事件3"],
    "turning_points": ["人生转折点1", "转折点2"]
  }},
  "backstory": "背景故事概要（150字以上）",
  "origin": "出身来历简述",
  "family_background": "家庭背景描述",
  "formative_experiences": ["塑造经历1：失去亲人", "经历2：意外获得能力"],

  "motivation_detail": {{
    "surface_motivation": "表面动机（如：找到失踪的父亲）",
    "deep_motivation": "深层动机（如：证明自己的价值，不再被忽视）",
    "motivation_type": "动机类型（revenge/protection/power/love/justice/survival/redemption/discovery/belonging/growth）",
    "motivation_source": "动机来源（如：童年阴影、某次事件、某人影响）",
    "motivation_conflict": "动机冲突（如：想要复仇但又相信宽恕）",
    "driving_force": "核心驱动力",
    "obstacles": ["阻碍因素1", "阻碍因素2"],
    "internal_conflict": "内心冲突详细描述",
    "fear_core": "核心恐惧",
    "desire_core": "核心欲望"
  }},
  "motivation": "动机总结（一句话）",
  "goal": "主要目标",
  "internal_conflict": "内心冲突概述",

  "archetype": "角色原型（如：英雄、寻道者、幸存者）",
  "growth_arc": "成长弧线描述",
  "starting_state": "初始状态（性格、处境）",
  "ending_state": "结局状态（成长后的样子）",

  "speech_pattern": "说话风格描述",
  "catchphrases": ["口头禅1", "口头禅2"],
  "communication_style": "沟通风格",

  "narrative_function": "在叙事中的功能",
  "thematic_significance": "主题意义",
  "character_arc_summary": "一句话角色弧线概括",

  "first_appearance": "首次出场场景",
  "status": "角色状态"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        # Parse appearance detail
        appearance_data = data.get("appearance_detail", {})
        appearance_detail = AppearanceDetail(
            face=appearance_data.get("face", ""),
            eyes=appearance_data.get("eyes", ""),
            hair=appearance_data.get("hair", ""),
            body=appearance_data.get("body", ""),
            skin=appearance_data.get("skin", ""),
            dressing=appearance_data.get("dressing", ""),
            accessories=appearance_data.get("accessories", []),
            overall=appearance_data.get("overall", ""),
        )

        # Parse personality dimension
        personality_data = data.get("personality_dimension", {})
        personality_dimension = PersonalityDimension(
            openness=personality_data.get("openness", 5),
            conscientiousness=personality_data.get("conscientiousness", 5),
            extraversion=personality_data.get("extraversion", 5),
            agreeableness=personality_data.get("agreeableness", 5),
            neuroticism=personality_data.get("neuroticism", 5),
        )

        # Parse background detail
        background_data = data.get("background_detail", {})
        family_members = background_data.get("family_members", [])
        background_detail = BackgroundDetail(
            birth_place=background_data.get("birth_place", ""),
            birth_era=background_data.get("birth_era", ""),
            childhood=background_data.get("childhood", ""),
            adolescence=background_data.get("adolescence", ""),
            early_adulthood=background_data.get("early_adulthood", ""),
            family_members=family_members if isinstance(family_members, list) else [],
            socioeconomic_status=background_data.get("socioeconomic_status", ""),
            education_background=background_data.get("education_background", ""),
            career_path=background_data.get("career_path", []),
            key_events=background_data.get("key_events", []),
            turning_points=background_data.get("turning_points", []),
        )

        # Parse motivation detail
        motivation_data = data.get("motivation_detail", {})
        motivation_detail = MotivationDetail(
            surface_motivation=motivation_data.get("surface_motivation", ""),
            deep_motivation=motivation_data.get("deep_motivation", ""),
            motivation_type=motivation_data.get("motivation_type", ""),
            motivation_source=motivation_data.get("motivation_source", ""),
            motivation_conflict=motivation_data.get("motivation_conflict", ""),
            driving_force=motivation_data.get("driving_force", ""),
            obstacles=motivation_data.get("obstacles", []),
            internal_conflict=motivation_data.get("internal_conflict", ""),
            fear_core=motivation_data.get("fear_core", ""),
            desire_core=motivation_data.get("desire_core", ""),
        )

        return MainCharacter(
            id=data.get("id", f"protagonist_{hash(data.get('name', 'unknown'))}"),
            name=data.get("name", "未知主角"),
            age=data.get("age", ""),
            age_numeric=data.get("age_numeric"),
            appearance_detail=appearance_detail,
            distinguishing_features=data.get("distinguishing_features", []),
            presence=data.get("presence", ""),
            first_impression=data.get("first_impression", ""),
            personality_dimension=personality_dimension,
            personality_description=data.get("personality_description", ""),
            mbti=data.get("mbti", ""),
            values=data.get("values", []),
            fears=data.get("fears", []),
            desires=data.get("desires", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            habits=data.get("habits", []),
            emotional_pattern=data.get("emotional_pattern", ""),
            background_detail=background_detail,
            backstory=data.get("backstory", ""),
            origin=data.get("origin", ""),
            family_background=data.get("family_background", ""),
            formative_experiences=data.get("formative_experiences", []),
            motivation_detail=motivation_detail,
            motivation=data.get("motivation", ""),
            goal=data.get("goal", ""),
            internal_conflict=data.get("internal_conflict", ""),
            archetype=data.get("archetype", ""),
            growth_arc=data.get("growth_arc", ""),
            starting_state=data.get("starting_state", ""),
            ending_state=data.get("ending_state", ""),
            speech_pattern=data.get("speech_pattern", ""),
            catchphrases=data.get("catchphrases", []),
            communication_style=data.get("communication_style", ""),
            narrative_function=data.get("narrative_function", ""),
            thematic_significance=data.get("thematic_significance", ""),
            character_arc_summary=data.get("character_arc_summary", ""),
            first_appearance=data.get("first_appearance", ""),
            status=data.get("status", "active"),
        )

    def create_profile(self, main_character: MainCharacter) -> MainCharacterProfile:
        """Create a complete MainCharacterProfile from MainCharacter.

        Args:
            main_character: Source main character

        Returns:
            MainCharacterProfile with organized information
        """
        return MainCharacterProfile(
            basic_info={
                "id": main_character.id,
                "name": main_character.name,
                "age": main_character.age,
                "age_numeric": main_character.age_numeric,
                "origin": main_character.origin,
                "status": main_character.status,
            },
            appearance=main_character.appearance_detail,
            personality=main_character.personality_dimension,
            background=main_character.background_detail,
            motivation=main_character.motivation_detail,
            values=main_character.values,
            fears=main_character.fears,
            desires=main_character.desires,
            strengths=main_character.strengths,
            weaknesses=main_character.weaknesses,
            archetype=main_character.archetype,
            growth_arc=main_character.growth_arc,
            starting_state=main_character.starting_state,
            ending_state=main_character.ending_state,
            speech_pattern=main_character.speech_pattern,
            catchphrases=main_character.catchphrases,
            narrative_function=main_character.narrative_function,
            thematic_significance=main_character.thematic_significance,
        )

    def to_character(self, main_character: MainCharacter) -> Character:
        """Convert MainCharacter to base Character model for story integration.

        Args:
            main_character: Source main character

        Returns:
            Character object compatible with existing story system
        """
        return Character(
            id=main_character.id,
            name=main_character.name,
            role=CharacterRole.PROTAGONIST,
            age=main_character.age,
            age_numeric=main_character.age_numeric,
            appearance=main_character.appearance_detail.model_dump(),
            distinguishing_features=main_character.distinguishing_features,
            presence=main_character.presence,
            personality=main_character.personality_dimension.model_dump(),
            personality_description=main_character.personality_description,
            values=main_character.values,
            fears=main_character.fears,
            desires=main_character.desires,
            strengths=main_character.strengths,
            weaknesses=main_character.weaknesses,
            habits=main_character.habits,
            backstory=main_character.backstory,
            origin=main_character.origin,
            family_background=main_character.family_background,
            formative_experiences=main_character.formative_experiences,
            motivation=main_character.motivation,
            goal=main_character.goal,
            internal_conflict=main_character.internal_conflict,
            archetype=main_character.archetype,
            growth_arc=main_character.growth_arc,
            starting_state=main_character.starting_state,
            ending_state=main_character.ending_state,
            speech_pattern=main_character.speech_pattern,
            catchphrases=main_character.catchphrases,
            communication_style=main_character.communication_style,
            narrative_function=main_character.narrative_function,
            thematic_significance=main_character.thematic_significance,
            character_arc_summary=main_character.character_arc_summary,
            first_appearance=main_character.first_appearance,
            status=main_character.status,
        )

    def get_main_character_summary(self, main_character: MainCharacter) -> str:
        """Get a human-readable summary of the main character.

        Args:
            main_character: Main character to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {main_character.name} ===",
            f"年龄: {main_character.age or '未设定'}",
            f"MBTI: {main_character.mbti or '未设定'}",
            "",
        ]

        # Appearance
        lines.append("【外貌】")
        app = main_character.appearance_detail
        if app.face:
            lines.append(f"  面部: {app.face}")
        if app.eyes:
            lines.append(f"  眼睛: {app.eyes}")
        if app.hair:
            lines.append(f"  发型: {app.hair}")
        if app.body:
            lines.append(f"  体型: {app.body}")
        if app.dressing:
            lines.append(f"  着装: {app.dressing}")
        if app.overall:
            lines.append(f"  整体: {app.overall}")
        if main_character.presence:
            lines.append(f"  气质: {main_character.presence}")
        if main_character.distinguishing_features:
            lines.append(f"  特征: {', '.join(main_character.distinguishing_features)}")
        lines.append("")

        # Personality
        lines.append("【性格】")
        if main_character.personality_description:
            lines.append(f"  {main_character.personality_description}")
        pd = main_character.personality_dimension
        lines.append(f"  性格维度: O{pd.openness} C{pd.conscientiousness} E{pd.extraversion} A{pd.agreeableness} N{pd.neuroticism}")
        if main_character.values:
            lines.append(f"  价值观: {', '.join(main_character.values)}")
        if main_character.fears:
            lines.append(f"  恐惧: {', '.join(main_character.fears)}")
        if main_character.desires:
            lines.append(f"  欲望: {', '.join(main_character.desires)}")
        if main_character.strengths:
            lines.append(f"  优点: {', '.join(main_character.strengths)}")
        if main_character.weaknesses:
            lines.append(f"  缺点: {', '.join(main_character.weaknesses)}")
        if main_character.habits:
            lines.append(f"  习惯: {', '.join(main_character.habits)}")
        if main_character.emotional_pattern:
            lines.append(f"  情绪模式: {main_character.emotional_pattern}")
        lines.append("")

        # Background
        lines.append("【背景】")
        bg = main_character.background_detail
        if bg.birth_place:
            lines.append(f"  出生地: {bg.birth_place}")
        if bg.socioeconomic_status:
            lines.append(f"  社会地位: {bg.socioeconomic_status}")
        if bg.education_background:
            lines.append(f"  教育: {bg.education_background}")
        if main_character.backstory:
            lines.append(f"  背景故事: {main_character.backstory[:150]}...")
        if main_character.family_background:
            lines.append(f"  家庭: {main_character.family_background}")
        if bg.key_events:
            lines.append(f"  关键事件: {', '.join(bg.key_events[:3])}")
        lines.append("")

        # Motivation
        lines.append("【动机】")
        mot = main_character.motivation_detail
        if mot.surface_motivation:
            lines.append(f"  表面动机: {mot.surface_motivation}")
        if mot.deep_motivation:
            lines.append(f"  深层动机: {mot.deep_motivation}")
        if mot.motivation_type:
            lines.append(f"  动机类型: {mot.motivation_type}")
        if main_character.motivation:
            lines.append(f"  动机概述: {main_character.motivation}")
        if main_character.goal:
            lines.append(f"  目标: {main_character.goal}")
        if mot.internal_conflict:
            lines.append(f"  内心冲突: {mot.internal_conflict}")
        if mot.fear_core:
            lines.append(f"  核心恐惧: {mot.fear_core}")
        if mot.desire_core:
            lines.append(f"  核心欲望: {mot.desire_core}")
        lines.append("")

        # Growth
        if main_character.archetype:
            lines.append(f"【原型】{main_character.archetype}")
        if main_character.growth_arc:
            lines.append(f"【成长弧线】{main_character.growth_arc}")
        if main_character.starting_state and main_character.ending_state:
            lines.append(f"【状态变化】{main_character.starting_state} → {main_character.ending_state}")
        lines.append("")

        # Dialogue
        if main_character.speech_pattern:
            lines.append(f"【说话风格】{main_character.speech_pattern}")
        if main_character.catchphrases:
            lines.append(f"【口头禅】{', '.join(main_character.catchphrases)}")
        lines.append("")

        # Story
        if main_character.narrative_function:
            lines.append(f"【叙事功能】{main_character.narrative_function}")
        if main_character.thematic_significance:
            lines.append(f"【主题意义】{main_character.thematic_significance}")
        if main_character.first_appearance:
            lines.append(f"【首次出场】{main_character.first_appearance}")

        return "\n".join(lines)

    def validate_main_character_completeness(
        self,
        main_character: MainCharacter,
    ) -> dict[str, Any]:
        """Validate that main character has complete 4 core aspects.

        Args:
            main_character: Main character to validate

        Returns:
            Dict with validation results
        """
        issues = []
        warnings = []
        suggestions = []
        completeness_scores = {}

        # Check Appearance (外貌)
        app_score = 0
        app_max = 10
        app = main_character.appearance_detail
        if app.face:
            app_score += 2
        if app.eyes:
            app_score += 1
        if app.hair:
            app_score += 1
        if app.body:
            app_score += 1
        if app.dressing:
            app_score += 1
        if app.overall:
            app_score += 2
        if main_character.presence:
            app_score += 1
        if main_character.distinguishing_features:
            app_score += 1
        completeness_scores["appearance"] = round(app_score / app_max, 2)

        if app_score < 5:
            issues.append("外貌设定不够详细，建议增加面部、眼睛、体型等着墨")

        # Check Personality (性格)
        pers_score = 0
        pers_max = 10
        if main_character.personality_description:
            pers_score += 3
        if main_character.mbti:
            pers_score += 1
        if len(main_character.values) >= 2:
            pers_score += 1
        if len(main_character.fears) >= 2:
            pers_score += 1
        if len(main_character.desires) >= 2:
            pers_score += 1
        if len(main_character.strengths) >= 2:
            pers_score += 1
        if len(main_character.weaknesses) >= 2:
            pers_score += 1
        if main_character.habits:
            pers_score += 1
        completeness_scores["personality"] = round(pers_score / pers_max, 2)

        if pers_score < 5:
            issues.append("性格设定不够完整，建议增加MBTI、价值观、优缺点等")

        # Check Background (背景)
        bg_score = 0
        bg_max = 10
        bg = main_character.background_detail
        if main_character.backstory:
            bg_score += 3
        if bg.birth_place:
            bg_score += 1
        if bg.family_members:
            bg_score += 1
        if bg.socioeconomic_status:
            bg_score += 1
        if bg.education_background:
            bg_score += 1
        if len(bg.key_events) >= 2:
            bg_score += 2
        if len(bg.turning_points) >= 1:
            bg_score += 1
        completeness_scores["background"] = round(bg_score / bg_max, 2)

        if bg_score < 5:
            issues.append("背景设定不够完整，建议增加童年经历、家庭背景、关键事件等")

        # Check Motivation (动机)
        mot_score = 0
        mot_max = 10
        mot = main_character.motivation_detail
        if main_character.motivation:
            mot_score += 2
        if main_character.goal:
            mot_score += 2
        if mot.surface_motivation:
            mot_score += 1
        if mot.deep_motivation:
            mot_score += 2
        if mot.motivation_type:
            mot_score += 1
        if mot.internal_conflict or main_character.internal_conflict:
            mot_score += 1
        if mot.fear_core:
            mot_score += 0.5
        if mot.desire_core:
            mot_score += 0.5
        completeness_scores["motivation"] = round(mot_score / mot_max, 2)

        if mot_score < 5:
            issues.append("动机设定不够完整，建议增加深层动机、内心冲突、核心恐惧/欲望等")

        # Check character arc
        if not main_character.growth_arc:
            warnings.append("主角缺少成长弧线设定")
        if not main_character.starting_state:
            warnings.append("主角缺少初始状态描述")
        if not main_character.ending_state:
            warnings.append("主角缺少结局状态描述")

        # Suggestions
        if not main_character.first_impression:
            suggestions.append("可以添加第一印象的描写，增加角色立体感")
        if not main_character.emotional_pattern:
            suggestions.append("可以添加情绪反应模式，使角色更加鲜活")
        if not main_character.catchphrases:
            suggestions.append("可以为主题角色添加口头禅，增加记忆点")

        # Calculate overall score
        overall_score = sum(completeness_scores.values()) / 4

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "completeness_scores": completeness_scores,
            "overall_completeness": round(overall_score, 2),
            "character_name": main_character.name,
            "status": "complete" if len(issues) == 0 and overall_score >= 0.7 else "needs_revision",
        }

    async def expand_appearance(
        self,
        main_character: MainCharacter,
    ) -> AppearanceDetail:
        """Expand and detail the appearance aspect of a character.

        Args:
            main_character: Character to expand appearance for

        Returns:
            Enhanced AppearanceDetail
        """
        prompt = f"""为一个角色生成详细的外貌描写。

角色：{main_character.name}
当前外貌概要：{main_character.appearance_detail.overall}

请生成更详细的外貌描写，以JSON格式输出：

{{
  "face": "面部特征详细描写",
  "eyes": "眼睛详细描写",
  "hair": "发型发色详细描写",
  "body": "体型身材详细描写",
  "skin": "肤色肤质详细描写",
  "dressing": "着装风格详细描写（包括衣服风格、颜色、材质等）",
  "accessories": ["配饰1", "配饰2", "配饰3"],
  "overall": "整体形象总结"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return AppearanceDetail(
            face=data.get("face", ""),
            eyes=data.get("eyes", ""),
            hair=data.get("hair", ""),
            body=data.get("body", ""),
            skin=data.get("skin", ""),
            dressing=data.get("dressing", ""),
            accessories=data.get("accessories", []),
            overall=data.get("overall", ""),
        )

    async def expand_personality(
        self,
        main_character: MainCharacter,
    ) -> PersonalityDimension:
        """Expand and detail the personality aspect of a character.

        Args:
            main_character: Character to expand personality for

        Returns:
            Enhanced PersonalityDimension
        """
        prompt = f"""为一个角色生成详细的性格分析。

角色：{main_character.name}
当前性格描述：{main_character.personality_description}
MBTI：{main_character.mbti}

请生成详细的性格维度分析，以JSON格式输出：

{{
  "openness": 开放度评分1-10,
  "conscientiousness": 尽责性评分1-10,
  "extraversion": 外向性评分1-10,
  "agreeableness": 宜人性评分1-10,
  "neuroticism": 神经质评分1-10
}}

请确保评分能准确反映角色的性格特点。"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return PersonalityDimension(
            openness=max(1, min(10, data.get("openness", 5))),
            conscientiousness=max(1, min(10, data.get("conscientiousness", 5))),
            extraversion=max(1, min(10, data.get("extraversion", 5))),
            agreeableness=max(1, min(10, data.get("agreeableness", 5))),
            neuroticism=max(1, min(10, data.get("neuroticism", 5))),
        )

    async def expand_background(
        self,
        main_character: MainCharacter,
    ) -> BackgroundDetail:
        """Expand and detail the background aspect of a character.

        Args:
            main_character: Character to expand background for

        Returns:
            Enhanced BackgroundDetail
        """
        prompt = f"""为一个角色生成详细的背景故事。

角色：{main_character.name}
当前背景概要：{main_character.backstory}
出身：{main_character.origin}
家庭背景：{main_character.family_background}

请生成详细的背景信息，以JSON格式输出：

{{
  "birth_place": "出生地点",
  "birth_era": "出生时代/年代",
  "childhood": "童年经历详细描述（100字以上）",
  "adolescence": "青少年时期经历（100字以上）",
  "early_adulthood": "成年早期经历（100字以上）",
  "family_members": [
    {{"relation": "关系", "name": "姓名", "description": "性格和背景"}}
  ],
  "socioeconomic_status": "社会经济地位描述",
  "education_background": "教育背景详细描述",
  "career_path": ["职业经历1", "职业经历2"],
  "key_events": ["关键事件1", "关键事件2", "关键事件3"],
  "turning_points": ["人生转折点1", "转折点2"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return BackgroundDetail(
            birth_place=data.get("birth_place", ""),
            birth_era=data.get("birth_era", ""),
            childhood=data.get("childhood", ""),
            adolescence=data.get("adolescence", ""),
            early_adulthood=data.get("early_adulthood", ""),
            family_members=data.get("family_members", []),
            socioeconomic_status=data.get("socioeconomic_status", ""),
            education_background=data.get("education_background", ""),
            career_path=data.get("career_path", []),
            key_events=data.get("key_events", []),
            turning_points=data.get("turning_points", []),
        )

    async def expand_motivation(
        self,
        main_character: MainCharacter,
    ) -> MotivationDetail:
        """Expand and detail the motivation aspect of a character.

        Args:
            main_character: Character to expand motivation for

        Returns:
            Enhanced MotivationDetail
        """
        prompt = f"""为一个角色生成详细的动机分析。

角色：{main_character.name}
当前动机：{main_character.motivation}
主要目标：{main_character.goal}
内心冲突：{main_character.internal_conflict}
核心恐惧：{', '.join(main_character.fears) if main_character.fears else '未设定'}
核心欲望：{', '.join(main_character.desires) if main_character.desires else '未设定'}

请生成详细的动机分析，以JSON格式输出：

{{
  "surface_motivation": "表面动机（外在目标）",
  "deep_motivation": "深层动机（内心真正驱动）",
  "motivation_type": "动机类型（revenge/protection/power/love/justice/survival/redemption/discovery/belonging/growth）",
  "motivation_source": "动机来源（什么事件或经历塑造了这种动机）",
  "motivation_conflict": "动机冲突（不同动机之间的矛盾）",
  "driving_force": "核心驱动力",
  "obstacles": ["阻碍因素1", "阻碍因素2"],
  "internal_conflict": "内心冲突详细描述",
  "fear_core": "核心恐惧（最深层最根本的恐惧）",
  "desire_core": "核心欲望（最深层最根本的欲望）"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return MotivationDetail(
            surface_motivation=data.get("surface_motivation", ""),
            deep_motivation=data.get("deep_motivation", ""),
            motivation_type=data.get("motivation_type", ""),
            motivation_source=data.get("motivation_source", ""),
            motivation_conflict=data.get("motivation_conflict", ""),
            driving_force=data.get("driving_force", ""),
            obstacles=data.get("obstacles", []),
            internal_conflict=data.get("internal_conflict", ""),
            fear_core=data.get("fear_core", ""),
            desire_core=data.get("desire_core", ""),
        )

    def export_main_character(
        self,
        main_character: MainCharacter,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """Export main character as a complete document.

        Args:
            main_character: Main character to export
            include_analysis: Whether to include completeness analysis

        Returns:
            Complete export dict
        """
        export_data = {
            "main_character": main_character.model_dump(),
            "profile": self.create_profile(main_character).model_dump(),
            "summary": self.get_main_character_summary(main_character),
        }

        if include_analysis:
            export_data["analysis"] = self.validate_main_character_completeness(main_character)

        return export_data
