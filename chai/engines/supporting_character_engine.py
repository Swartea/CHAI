"""Supporting character engine for generating and managing supporting characters."""

from typing import Optional, Any
from chai.models.supporting_character import (
    SupportingCharacter,
    SupportingCharacterProfile,
    SupportingCharacterSystem,
    SupportingArchetype,
    SupportingRoleType,
    SupportingCharacterAppearance,
    SupportingCharacterPersonality,
    SupportingCharacterBackground,
    SupportingCharacterMotivation,
    SupportingCharacterRelationship,
    SupportingCharacterArc,
    SupportingCharacterSkill,
    SupportingCharacterConflict,
)
from chai.models import Character, CharacterRole, MainCharacter
from chai.services import AIService


class SupportingCharacterEngine:
    """Engine for generating and managing supporting characters.

    Supporting characters are secondary characters who support the protagonist.
    They include mentors, sidekicks, best friends, love interests, allies, etc.
    Each has their own arc, motivations, and relationship with the protagonist.
    """

    def __init__(self, ai_service: AIService):
        """Initialize supporting character engine with AI service."""
        self.ai_service = ai_service

    async def generate_supporting_character(
        self,
        role_type: SupportingRoleType,
        genre: str,
        theme: str,
        protagonist: Optional[MainCharacter] = None,
        existing_characters: Optional[list[Character]] = None,
        world_context: Optional[dict] = None,
    ) -> SupportingCharacter:
        """Generate a supporting character.

        Args:
            role_type: Type of supporting role (mentor, sidekick, ally, etc.)
            genre: Novel genre
            theme: Central theme
            protagonist: Optional protagonist character for relationship
            existing_characters: Optional list of existing characters
            world_context: Optional world context

        Returns:
            SupportingCharacter object
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        protagonist_info = ""
        if protagonist:
            protagonist_info = f"""主角信息：
姓名：{protagonist.name}
性格：{protagonist.personality_description[:100] if protagonist.personality_description else '未设定'}
动机：{protagonist.motivation or '未设定'}
目标：{protagonist.goal or '未设定'}
"""

        existing_chars_info = ""
        if existing_characters:
            chars_info = []
            for c in existing_characters[:3]:
                chars_info.append(f"- {c.name}（{c.role.value}）")
            existing_chars_info = "已有角色：\n" + "\n".join(chars_info) + "\n"

        role_descriptions = {
            SupportingRoleType.MENTOR: "导师型 - 指导和教导主角的角色，通常具有丰富经验和智慧",
            SupportingRoleType.SIDEKICK: "助手型 - 忠诚的伙伴，与主角并肩作战",
            SupportingRoleType.BEST_FRIEND: "挚友型 - 主角最亲密的朋友，了解主角的一切",
            SupportingRoleType.LOVE_INTEREST: "爱人型 - 主角的浪漫对象",
            SupportingRoleType.MENTEE: "学徒型 - 主角的学生或追随者",
            SupportingRoleType.ALLY: "同盟型 - 在特定目标上与主角合作",
            SupportingRoleType.CONTACT: "线人型 - 为主角提供信息",
            SupportingRoleType.EXPERT: "专家型 - 在某个领域提供专业知识和技能",
            SupportingRoleType.COMIC_RELIEF: "喜剧型 - 提供幽默和轻松时刻",
            SupportingRoleType.WISDOM_KEEPER: "智者型 - 拥有古老智慧和知识",
            SupportingRoleType.FOIL: "对照型 - 与主角形成对比，凸显主角特质",
            SupportingRoleType.FALLEN_ALLY: "堕落同盟 - 曾经是盟友，后来成为敌人",
            SupportingRoleType.RETIRED_HERO: "隐退英雄 - 曾经的英雄，现在隐退",
            SupportingRoleType.INFORMANT: "情报员 - 收集和提供情报",
        }

        prompt = f"""生成一个{role_descriptions.get(role_type, role_type.value)}角色。

类型：{genre}
主题：{theme}
{context}
{protagonist_info}
{existing_chars_info}

请生成一个完整的配角角色，以JSON格式输出：

{{
  "id": "唯一标识符",
  "name": "角色姓名",
  "supporting_role_type": "{role_type.value}",
  "description": "角色简要描述",

  "age": "年龄描述",
  "age_numeric": 年龄数值,
  "appearance": {{
    "face": "面部特征（如：温和的面容，眉宇间透着智慧）",
    "eyes": "眼睛描写（如：深邃的棕色眼眸）",
    "hair": "发型发色（如：花白的头发）",
    "body": "体型（如：中等身材，微微发福）",
    "skin": "肤色（如：古铜色）",
    "dressing": "着装风格（如：朴素的灰色长袍）",
    "accessories": ["标志性配饰"],
    "overall": "整体形象（如：第一眼给人睿智可靠的感觉）"
  }},
  "distinguishing_features": ["显著特征1", "显著特征2"],
  "presence": "气质/气场描述",

  "personality": {{
    "core_traits": ["核心性格特点1", "核心性格特点2"],
    "personality_description": "详细性格描述（100字以上）",
    "mbti": "MBTI类型",
    "values": ["核心价值1", "价值2"],
    "fears": ["恐惧1", "恐惧2"],
    "desires": ["欲望1", "欲望2"],
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "habits": ["习惯1", "习惯2"],
    "emotional_pattern": "典型情绪反应模式"
  }},

  "background": {{
    "origin": "出身来历",
    "family_background": "家庭背景",
    "education": "教育背景",
    "previous_occupations": ["之前职业1", "职业2"],
    "key_experiences": ["关键经历1", "经历2"],
    "formative_events": ["塑造事件1", "事件2"],
    "socioeconomic_status": "社会经济地位"
  }},
  "backstory": "背景故事详细描述（100字以上）",

  "motivation": {{
    "surface_motivation": "表面动机",
    "deep_motivation": "深层动机",
    "motivation_type": "动机类型",
    "motivation_source": "动机来源",
    "motivation_for_allying": "为何支持主角",
    "personal_goals": ["个人目标1", "目标2"],
    "conflicts_with_protagonist": ["与主角潜在冲突1", "冲突2"]
  }},

  "relationship_to_protagonist": {{
    "protagonist_id": "主角ID",
    "protagonist_name": "主角姓名",
    "relationship_type": "关系类型（如：师徒、挚友、同盟等）",
    "relationship_dynamics": "关系互动模式",
    "relationship_history": "关系历史",
    "current_status": "现状",
    "key_events": ["关键事件1", "事件2"],
    "support_functions": ["如何支持主角1", "支持方式2"],
    "future_potential": "关系发展潜力"
  }},

  "skills": [
    {{
      "name": "技能名称",
      "description": "技能描述",
      "category": "技能类别",
      "proficiency_level": "精通程度",
      "source": "习得来源",
      "usefulness_to_protagonist": "对主角的帮助"
    }}
  ],
  "combat_abilities": ["战斗能力1", "能力2"],
  "social_abilities": ["社交能力1", "能力2"],
  "intellectual_abilities": ["智力能力1", "能力2"],

  "equipment": ["装备1", "装备2"],
  "resources": ["资源1", "资源2"],

  "character_arc": {{
    "archetype": "角色原型",
    "growth_arc": "成长弧线描述",
    "starting_state": "初始状态",
    "ending_state": "结局状态",
    "transformation": "转变描述",
    "lessons_learned": ["学到的教训1", "教训2"],
    "impact_on_story": "对故事的影响"
  }},

  "psychological_profile": {{
    "attachment_style": "依恋风格",
    "defense_mechanisms": ["防御机制1"]
  }},
  "attachment_style": "依恋风格",
  "defense_mechanisms": ["防御机制1", "机制2"],
  "emotional_wounds": ["情感创伤1"],

  "speech_pattern": "说话风格描述",
  "catchphrases": ["口头禅1", "口头禅2"],
  "communication_style": "沟通风格",

  "narrative_function": "在叙事中的功能",
  "thematic_significance": "主题意义",
  "screen_time_estimate": "预计戏份（high/medium/low）",

  "conflicts": [
    {{
      "conflict_type": "冲突类型",
      "description": "冲突描述",
      "parties_involved": ["相关方"],
      "cause": "起因",
      "stakes": "赌注",
      "resolution": "可能的解决方式"
    }}
  ],

  "first_appearance": "首次出场时机",
  "status": "角色状态"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return self._parse_supporting_character(data, role_type)

    def _parse_supporting_character(
        self,
        data: dict,
        role_type: SupportingRoleType,
    ) -> SupportingCharacter:
        """Parse JSON data into SupportingCharacter object."""
        appearance_data = data.get("appearance", {})
        appearance = SupportingCharacterAppearance(
            face=appearance_data.get("face", ""),
            eyes=appearance_data.get("eyes", ""),
            hair=appearance_data.get("hair", ""),
            body=appearance_data.get("body", ""),
            skin=appearance_data.get("skin", ""),
            dressing=appearance_data.get("dressing", ""),
            accessories=appearance_data.get("accessories", []),
            overall=appearance_data.get("overall", ""),
        )

        personality_data = data.get("personality", {})
        personality = SupportingCharacterPersonality(
            core_traits=personality_data.get("core_traits", []),
            personality_description=personality_data.get("personality_description", ""),
            mbti=personality_data.get("mbti", ""),
            values=personality_data.get("values", []),
            fears=personality_data.get("fears", []),
            desires=personality_data.get("desires", []),
            strengths=personality_data.get("strengths", []),
            weaknesses=personality_data.get("weaknesses", []),
            habits=personality_data.get("habits", []),
            emotional_pattern=personality_data.get("emotional_pattern", ""),
        )

        background_data = data.get("background", {})
        background = SupportingCharacterBackground(
            origin=background_data.get("origin", ""),
            family_background=background_data.get("family_background", ""),
            education=background_data.get("education", ""),
            previous_occupations=background_data.get("previous_occupations", []),
            key_experiences=background_data.get("key_experiences", []),
            formative_events=background_data.get("formative_events", []),
            socioeconomic_status=background_data.get("socioeconomic_status", ""),
        )

        motivation_data = data.get("motivation", {})
        motivation = SupportingCharacterMotivation(
            surface_motivation=motivation_data.get("surface_motivation", ""),
            deep_motivation=motivation_data.get("deep_motivation", ""),
            motivation_type=motivation_data.get("motivation_type", ""),
            motivation_source=motivation_data.get("motivation_source", ""),
            motivation_for_allying=motivation_data.get("motivation_for_allying", ""),
            personal_goals=motivation_data.get("personal_goals", []),
            conflicts_with_protagonist=motivation_data.get("conflicts_with_protagonist", []),
        )

        relationship_data = data.get("relationship_to_protagonist", {})
        relationship = SupportingCharacterRelationship(
            protagonist_id=relationship_data.get("protagonist_id", ""),
            protagonist_name=relationship_data.get("protagonist_name", ""),
            relationship_type=relationship_data.get("relationship_type", ""),
            relationship_dynamics=relationship_data.get("relationship_dynamics", ""),
            relationship_history=relationship_data.get("relationship_history", ""),
            current_status=relationship_data.get("current_status", ""),
            key_events=relationship_data.get("key_events", []),
            support_functions=relationship_data.get("support_functions", []),
            future_potential=relationship_data.get("future_potential", ""),
        )

        arc_data = data.get("character_arc", {})
        arc = SupportingCharacterArc(
            archetype=arc_data.get("archetype", ""),
            growth_arc=arc_data.get("growth_arc", ""),
            starting_state=arc_data.get("starting_state", ""),
            ending_state=arc_data.get("ending_state", ""),
            transformation=arc_data.get("transformation", ""),
            lessons_learned=arc_data.get("lessons_learned", []),
            impact_on_story=arc_data.get("impact_on_story", ""),
        )

        skills = []
        for item in data.get("skills", []):
            if isinstance(item, dict):
                skills.append(SupportingCharacterSkill(
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    category=item.get("category", ""),
                    proficiency_level=item.get("proficiency_level", ""),
                    source=item.get("source", ""),
                    usefulness_to_protagonist=item.get("usefulness_to_protagonist", ""),
                ))

        conflicts = []
        for item in data.get("conflicts", []):
            if isinstance(item, dict):
                conflicts.append(SupportingCharacterConflict(
                    conflict_type=item.get("conflict_type", ""),
                    description=item.get("description", ""),
                    parties_involved=item.get("parties_involved", []),
                    cause=item.get("cause", ""),
                    stakes=item.get("stakes", ""),
                    resolution=item.get("resolution", ""),
                ))

        return SupportingCharacter(
            id=data.get("id", f"supporting_{hash(data.get('name', 'unknown'))}"),
            name=data.get("name", "未知配角"),
            supporting_role_type=role_type,
            description=data.get("description", ""),
            age=data.get("age", ""),
            age_numeric=data.get("age_numeric"),
            appearance=appearance,
            distinguishing_features=data.get("distinguishing_features", []),
            presence=data.get("presence", ""),
            personality=personality,
            background=background,
            backstory=data.get("backstory", ""),
            motivation=motivation,
            relationship_to_protagonist=relationship,
            skills=skills,
            combat_abilities=data.get("combat_abilities", []),
            social_abilities=data.get("social_abilities", []),
            intellectual_abilities=data.get("intellectual_abilities", []),
            equipment=data.get("equipment", []),
            resources=data.get("resources", []),
            character_arc=arc,
            psychological_profile=data.get("psychological_profile", {}),
            attachment_style=data.get("attachment_style", ""),
            defense_mechanisms=data.get("defense_mechanisms", []),
            emotional_wounds=data.get("emotional_wounds", []),
            speech_pattern=data.get("speech_pattern", ""),
            catchphrases=data.get("catchphrases", []),
            communication_style=data.get("communication_style", ""),
            narrative_function=data.get("narrative_function", ""),
            thematic_significance=data.get("thematic_significance", ""),
            screen_time_estimate=data.get("screen_time_estimate", ""),
            conflicts=conflicts,
            first_appearance=data.get("first_appearance", ""),
            death=data.get("death"),
            status=data.get("status", "active"),
        )

    async def generate_supporting_cast(
        self,
        genre: str,
        theme: str,
        protagonist: Optional[MainCharacter] = None,
        count: int = 3,
        world_context: Optional[dict] = None,
    ) -> list[SupportingCharacter]:
        """Generate a complete supporting cast for the protagonist.

        Args:
            genre: Novel genre
            theme: Central theme
            protagonist: Optional protagonist
            count: Number of supporting characters to generate
            world_context: Optional world context

        Returns:
            List of SupportingCharacter objects
        """
        role_types = [
            SupportingRoleType.MENTOR,
            SupportingRoleType.SIDEKICK,
            SupportingRoleType.ALLY,
            SupportingRoleType.EXPERT,
            SupportingRoleType.CONTACT,
            SupportingRoleType.BEST_FRIEND,
            SupportingRoleType.LOVE_INTEREST,
            SupportingRoleType.WISDOM_KEEPER,
            SupportingRoleType.COMIC_RELIEF,
            SupportingRoleType.FOIL,
            SupportingRoleType.MENTEE,
            SupportingRoleType.FALLEN_ALLY,
            SupportingRoleType.RETIRED_HERO,
            SupportingRoleType.INFORMANT,
        ]

        protagonist_info = ""
        if protagonist:
            protagonist_info = f"""主角信息：
姓名：{protagonist.name}
性格：{protagonist.personality_description[:100] if protagonist.personality_description else '未设定'}
需要支持类型："""
            needed_types = []
            if "mentor" not in protagonist.backstory.lower():
                needed_types.append("导师型（Mentor）")
            if not protagonist.relationships:
                needed_types.append("挚友型（Best Friend）")
            if not any(s for s in protagonist.skills if s.category == "combat"):
                needed_types.append("战斗型助手（Sidekick）")
            protagonist_info += "、".join(needed_types) if needed_types else "全面支持"

        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        prompt = f"""为{genre}类型小说生成{count}个配角角色。

类型：{genre}
主题：{theme}
{context}
{protagonist_info}

请生成{count}个不同类型的配角角色，以JSON数组格式输出：

[
  {{
    "id": "角色ID",
    "name": "角色姓名",
    "supporting_role_type": "mentor/sidekick/ally/expert/contact/best_friend/love_interest/wisdom_keeper/comic_relief/foil/mentee/fallen_ally/retired_hero/informant",
    "description": "角色简要描述",
    "age": "年龄描述",
    "age_numeric": 年龄数值,
    "appearance": {{"face": "面部", "eyes": "眼睛", "hair": "发型", "body": "体型", "dressing": "着装", "overall": "整体"}},
    "distinguishing_features": ["显著特征"],
    "presence": "气质",
    "personality": {{"core_traits": ["性格特点"], "personality_description": "描述", "mbti": "MBTI", "values": ["价值观"], "fears": ["恐惧"], "desires": ["欲望"], "strengths": ["优点"], "weaknesses": ["缺点"], "habits": ["习惯"]}},
    "background": {{"origin": "出身", "family_background": "家庭", "education": "教育", "previous_occupations": ["职业"], "key_experiences": ["经历"], "formative_events": ["事件"]}},
    "backstory": "背景故事",
    "motivation": {{"surface_motivation": "表面动机", "deep_motivation": "深层动机", "motivation_type": "类型", "motivation_for_allying": "为何支持主角", "personal_goals": ["目标"], "conflicts_with_protagonist": ["冲突"]}},
    "relationship_to_protagonist": {{"relationship_type": "关系类型", "relationship_dynamics": "互动模式", "relationship_history": "历史", "current_status": "现状", "support_functions": ["支持方式"]}},
    "skills": [{{"name": "技能", "description": "描述", "category": "类别", "proficiency_level": "程度", "source": "来源", "usefulness_to_protagonist": "对主角帮助"}}],
    "combat_abilities": ["战斗能力"],
    "social_abilities": ["社交能力"],
    "intellectual_abilities": ["智力能力"],
    "equipment": ["装备"],
    "resources": ["资源"],
    "character_arc": {{"archetype": "原型", "growth_arc": "成长弧线", "starting_state": "初始", "ending_state": "结局", "transformation": "转变", "lessons_learned": ["教训"], "impact_on_story": "影响"}},
    "speech_pattern": "说话风格",
    "catchphrases": ["口头禅"],
    "communication_style": "沟通风格",
    "narrative_function": "叙事功能",
    "thematic_significance": "主题意义",
    "screen_time_estimate": "戏份（high/medium/low）",
    "conflicts": [{{"conflict_type": "类型", "description": "描述", "parties_involved": ["相关方"], "stakes": "赌注", "resolution": "解决"}}],
    "first_appearance": "首次出场",
    "status": "active"
  }}
]

请确保生成{count}个不同角色的JSON数组。"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json_array(result)

        characters = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                try:
                    role_str = item.get("supporting_role_type", "ally")
                    try:
                        role_type = SupportingRoleType(role_str)
                    except ValueError:
                        role_type = SupportingRoleType.ALLY
                    characters.append(self._parse_supporting_character(item, role_type))
                except Exception:
                    continue

        return characters

    def create_profile(
        self,
        supporting_character: SupportingCharacter,
    ) -> SupportingCharacterProfile:
        """Create a complete profile from supporting character.

        Args:
            supporting_character: Source character

        Returns:
            SupportingCharacterProfile
        """
        return SupportingCharacterProfile(
            basic_info={
                "id": supporting_character.id,
                "name": supporting_character.name,
                "role_type": supporting_character.supporting_role_type.value,
                "age": supporting_character.age,
                "status": supporting_character.status,
            },
            appearance=supporting_character.appearance,
            personality=supporting_character.personality,
            background=supporting_character.background,
            motivation=supporting_character.motivation,
            relationship_to_protagonist=supporting_character.relationship_to_protagonist,
            skills=supporting_character.skills,
            character_arc=supporting_character.character_arc,
            speech_pattern=supporting_character.speech_pattern,
            catchphrases=supporting_character.catchphrases,
            narrative_function=supporting_character.narrative_function,
            thematic_significance=supporting_character.thematic_significance,
        )

    def to_character(
        self,
        supporting_character: SupportingCharacter,
    ) -> Character:
        """Convert SupportingCharacter to base Character model.

        Args:
            supporting_character: Source supporting character

        Returns:
            Character object
        """
        return Character(
            id=supporting_character.id,
            name=supporting_character.name,
            role=CharacterRole.SUPPORTING,
            age=supporting_character.age,
            age_numeric=supporting_character.age_numeric,
            appearance=supporting_character.appearance.model_dump(),
            distinguishing_features=supporting_character.distinguishing_features,
            presence=supporting_character.presence,
            personality=supporting_character.personality.model_dump(),
            personality_description=supporting_character.personality.personality_description,
            values=supporting_character.personality.values,
            fears=supporting_character.personality.fears,
            desires=supporting_character.personality.desires,
            strengths=supporting_character.personality.strengths,
            weaknesses=supporting_character.personality.weaknesses,
            habits=supporting_character.personality.habits,
            backstory=supporting_character.backstory,
            origin=supporting_character.background.origin,
            family_background=supporting_character.background.family_background,
            education=supporting_character.background.education,
            previous_occupations=supporting_character.background.previous_occupations,
            formative_experiences=supporting_character.background.formative_events,
            motivation=supporting_character.motivation.surface_motivation,
            goal="; ".join(supporting_character.motivation.personal_goals),
            internal_conflict="; ".join(supporting_character.motivation.conflicts_with_protagonist),
            skills=[
                Character(
                    id=f"{supporting_character.id}_skill",
                    name=s.name,
                    role=CharacterRole.SUPPORTING,
                ).skills.append(s) or s
                for s in supporting_character.skills
            ] if supporting_character.skills else [],
            combat_abilities=supporting_character.combat_abilities,
            social_abilities=supporting_character.social_abilities,
            intellectual_abilities=supporting_character.intellectual_abilities,
            equipment=supporting_character.equipment,
            resources=supporting_character.resources,
            speech_pattern=supporting_character.speech_pattern,
            catchphrases=supporting_character.catchphrases,
            communication_style=supporting_character.communication_style,
            narrative_function=supporting_character.narrative_function,
            thematic_significance=supporting_character.thematic_significance,
            first_appearance=supporting_character.first_appearance,
            status=supporting_character.status,
        )

    def get_supporting_character_summary(
        self,
        supporting_character: SupportingCharacter,
    ) -> str:
        """Get human-readable summary of supporting character.

        Args:
            supporting_character: Character to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {supporting_character.name} ===",
            f"角色类型: {supporting_character.supporting_role_type.value}",
            f"年龄: {supporting_character.age or '未设定'}",
            "",
        ]

        if supporting_character.description:
            lines.append(f"【描述】{supporting_character.description}")

        if supporting_character.presence:
            lines.append(f"【气质】{supporting_character.presence}")

        app = supporting_character.appearance
        if app.overall:
            lines.extend(["", "【外貌】"])
            if app.face:
                lines.append(f"  面部: {app.face}")
            if app.eyes:
                lines.append(f"  眼睛: {app.eyes}")
            if app.hair:
                lines.append(f"  发型: {app.hair}")
            if app.dressing:
                lines.append(f"  着装: {app.dressing}")
            lines.append(f"  整体: {app.overall}")

        pers = supporting_character.personality
        if pers.personality_description:
            lines.extend(["", "【性格】"])
            lines.append(f"  {pers.personality_description}")
            if pers.core_traits:
                lines.append(f"  核心特点: {', '.join(pers.core_traits)}")
            if pers.mbti:
                lines.append(f"  MBTI: {pers.mbti}")

        bg = supporting_character.background
        if supporting_character.backstory:
            lines.extend(["", "【背景】"])
            lines.append(f"  {supporting_character.backstory[:150]}...")
            if bg.origin:
                lines.append(f"  出身: {bg.origin}")

        mot = supporting_character.motivation
        if mot.motivation_for_allying:
            lines.extend(["", "【支持主角的原因】"])
            lines.append(f"  {mot.motivation_for_allying}")

        rel = supporting_character.relationship_to_protagonist
        if rel.relationship_type:
            lines.extend(["", "【与主角的关系】"])
            lines.append(f"  类型: {rel.relationship_type}")
            if rel.relationship_dynamics:
                lines.append(f"  互动模式: {rel.relationship_dynamics}")
            if rel.support_functions:
                lines.append(f"  支持方式: {', '.join(rel.support_functions)}")

        arc = supporting_character.character_arc
        if arc.growth_arc:
            lines.extend(["", "【成长弧线】"])
            lines.append(f"  {arc.growth_arc}")
            if arc.starting_state and arc.ending_state:
                lines.append(f"  变化: {arc.starting_state} → {arc.ending_state}")

        if supporting_character.skills:
            lines.extend(["", f"【技能】({len(supporting_character.skills)})"])
            for skill in supporting_character.skills[:3]:
                lines.append(f"  • {skill.name}: {skill.description[:30] if skill.description else '无描述'}...")

        if supporting_character.catchphrases:
            lines.extend(["", "【口头禅】"])
            lines.append(f"  {', '.join(supporting_character.catchphrases)}")

        if supporting_character.narrative_function:
            lines.extend(["", "【叙事功能】"])
            lines.append(f"  {supporting_character.narrative_function}")

        lines.extend(["", f"状态: {supporting_character.status}"])
        if supporting_character.screen_time_estimate:
            lines.append(f"预计戏份: {supporting_character.screen_time_estimate}")

        return "\n".join(lines)

    def export_supporting_character(
        self,
        supporting_character: SupportingCharacter,
        include_profile: bool = True,
    ) -> dict[str, Any]:
        """Export supporting character as complete document.

        Args:
            supporting_character: Character to export
            include_profile: Whether to include profile

        Returns:
            Complete export dict
        """
        export_data = {
            "supporting_character": supporting_character.model_dump(),
            "summary": self.get_supporting_character_summary(supporting_character),
        }

        if include_profile:
            export_data["profile"] = self.create_profile(supporting_character).model_dump()

        return export_data

    def validate_supporting_character(
        self,
        supporting_character: SupportingCharacter,
    ) -> dict[str, Any]:
        """Validate supporting character completeness.

        Args:
            supporting_character: Character to validate

        Returns:
            Validation results
        """
        issues = []
        warnings = []
        suggestions = []

        if not supporting_character.name:
            issues.append("角色缺少姓名")

        if not supporting_character.backstory:
            warnings.append("角色缺少背景故事")

        if not supporting_character.motivation.motivation_for_allying:
            warnings.append("缺少支持主角的动机设定")

        if not supporting_character.relationship_to_protagonist.relationship_type:
            warnings.append("缺少与主角的关系类型设定")

        if not supporting_character.character_arc.growth_arc:
            suggestions.append("可以添加成长弧线来丰富角色发展")

        if not supporting_character.skills:
            suggestions.append("可以添加技能来展示角色的独特能力")

        if not supporting_character.catchphrases:
            suggestions.append("可以添加口头禅来增加角色记忆点")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "character_name": supporting_character.name,
            "role_type": supporting_character.supporting_role_type.value,
        }