"""Character system engine for comprehensive character system generation and management."""

from typing import Optional, Any
from chai.models import (
    Character,
    CharacterSystem,
    CharacterArchetype,
    CharacterSkill,
    CharacterGroup,
    CharacterConflict,
    CharacterGrowthStage,
    CharacterRelationship,
    WorldSetting,
)
from chai.services import AIService


class CharacterSystemEngine:
    """Engine for building comprehensive character systems.

    Provides methods to generate character systems, individual characters,
    analyze relationships, and manage character development.
    """

    def __init__(self, ai_service: AIService):
        """Initialize character system engine with AI service."""
        self.ai_service = ai_service

    async def build_character_system(
        self,
        genre: str,
        theme: str,
        world_context: Optional[dict] = None,
    ) -> CharacterSystem:
        """Build a complete character system with archetypes and guidelines.

        Args:
            genre: Novel genre
            theme: Central theme
            world_context: Optional world context (geography, politics, culture, etc.)

        Returns:
            Complete CharacterSystem with archetypes and guidelines
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        prompt = f"""为{genre}类型小说生成完整的角色体系设定。

主题：{theme}
{context}

请生成包含以下方面的详细角色体系，以JSON格式输出：

{{
  "name": "角色体系名称",
  "genre": "{genre}",
  "theme": "{theme}",

  "archetypes": [
    {{
      "name": "原型名称（如：英雄、导师、影子、小丑等）",
      "description": "原型描述",
      "typical_traits": ["典型特征1", "典型特征2"],
      "typical_motivations": ["典型动机1", "典型动机2"],
      "typical_weaknesses": ["典型缺点1", "典型缺点2"],
      "growth_potential": "成长潜力描述",
      "examples_in_literature": ["文学作品中著名例子"]
    }}
  ],

  "relationship_templates": [
    {{
      "type": "关系类型",
      "description": "关系描述",
      "typical_dynamics": "典型互动模式",
      "common_conflicts": "常见冲突类型",
      "development_potential": "关系发展潜力"
    }}
  ],

  "generation_guidelines": "角色生成指南和原则",

  "role_distribution": {{
    "protagonist": 1,
    "antagonist": 1,
    "deuteragonist": 1,
    "supporting": "根据故事规模3-10人",
    "minor": "根据故事规模若干"
  }},

  "group_templates": [
    {{
      "name": "团队/组织模板名称",
      "type": "类型（家族、门派、团队等）",
      "typical_structure": "典型结构",
      "roles_within_group": ["典型角色定位"],
      "internal_conflicts": "内部冲突类型"
    }}
  ]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        archetypes = []
        for item in data.get("archetypes", []):
            if isinstance(item, dict):
                archetypes.append(CharacterArchetype(
                    name=item.get("name", "未知"),
                    description=item.get("description", ""),
                    typical_traits=item.get("typical_traits", []),
                    typical_motivations=item.get("typical_motivations", []),
                    typical_weaknesses=item.get("typical_weaknesses", []),
                    growth_potential=item.get("growth_potential", ""),
                    examples_in_literature=item.get("examples_in_literature", []),
                ))

        return CharacterSystem(
            name=data.get("name", "角色体系"),
            genre=data.get("genre", genre),
            theme=data.get("theme", theme),
            archetypes=archetypes,
            relationship_templates=data.get("relationship_templates", []),
            generation_guidelines=data.get("generation_guidelines", ""),
            role_distribution=data.get("role_distribution", {}),
            group_templates=data.get("group_templates", []),
        )

    async def generate_character(
        self,
        role: str,
        genre: str,
        theme: str,
        world_context: Optional[dict] = None,
        existing_characters: Optional[list[Character]] = None,
        character_system: Optional[CharacterSystem] = None,
    ) -> Character:
        """Generate a specific character.

        Args:
            role: Character role (protagonist, antagonist, supporting, etc.)
            genre: Novel genre
            theme: Central theme
            world_context: Optional world context
            existing_characters: Optional list of existing characters for relationship generation
            character_system: Optional character system for archetype guidance

        Returns:
            Character object
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        existing_chars_info = ""
        if existing_characters:
            context_chars = []
            for c in existing_characters[:5]:
                context_chars.append(f"- {c.name}（{c.role.value}）")
            existing_chars_info = "已有角色：\n" + "\n".join(context_chars) + "\n"

        archetype_guidance = ""
        if character_system and character_system.archetypes:
            archetype_names = [a.name for a in character_system.archetypes[:5]]
            archetype_guidance = f"可用角色原型：{', '.join(archetype_names)}\n"

        prompt = f"""生成一个{role}类型的角色。

类型：{genre}
主题：{theme}
{context}
{existing_chars_info}
{archetype_guidance}

请生成一个完整的{role}角色，以JSON格式输出：

{{
  "id": "唯一标识符",
  "name": "角色姓名",
  "role": "{role}",

  "age": "年龄描述",
  "age_numeric": 年龄数值,
  "appearance": {{
    "face": "面部特征",
    "body": "体型特征",
    "dressing": "着装风格",
    "overall": "整体形象"
  }},
  "distinguishing_features": ["显著特征1", "显著特征2"],
  "presence": "气质/气场的描述",

  "personality": {{
    "traits": ["性格特点1", "性格特点2"],
    "mbti": "MBTI类型（如INTJ）"
  }},
  "personality_description": "性格详细描述",
  "values": ["核心价值1", "核心价值2"],
  "fears": ["恐惧1", "恐惧2"],
  "desires": ["欲望1", "欲望2"],
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "habits": ["习惯1", "习惯2"],

  "backstory": "详细背景故事",
  "origin": "出身来历",
  "family_background": "家庭背景",
  "education": "教育背景",
  "previous_occupations": ["之前职业1", "之前职业2"],
  "formative_experiences": ["塑造经历1", "塑造经历2"],
  "motivation": "行动动机",
  "goal": "主要目标",
  "internal_conflict": "内心冲突",

  "skills": [
    {{
      "name": "技能名称",
      "description": "技能描述",
      "category": "技能类别",
      "proficiency_level": "精通程度",
      "source": "习得来源"
    }}
  ],
  "combat_abilities": ["战斗能力1", "战斗能力2"],
  "social_abilities": ["社交能力1", "社交能力2"],
  "intellectual_abilities": ["智力能力1", "智力能力2"],

  "resources": ["资源1", "资源2"],
  "equipment": ["装备1", "装备2"],
  "vehicles": ["载具1"],

  "groups": [
    {{
      "group_id": "group_001",
      "name": "所属组织名称",
      "group_type": "组织类型",
      "role": "在组织中的角色",
      "position": "职位",
      "joined_at": "加入时间"
    }}
  ],

  "relationships": [
    {{
      "character_id": "关联角色ID",
      "character_name": "关联角色姓名",
      "relationship_type": "关系类型",
      "description": "关系描述",
      "dynamics": "互动模式",
      "history": "关系历史",
      "current_status": "现状"
    }}
  ],

  "archetype": "角色原型（如：英雄、影子、智者等）",
  "growth_arc": "成长弧线描述",
  "growth_stages": [
    {{
      "stage_name": "阶段名称",
      "description": "阶段描述",
      "trigger_event": "触发事件",
      "lessons_learned": ["学到的教训"],
      "new_abilities_or_insights": ["新能力/领悟"],
      "emotional_state": "情感状态"
    }}
  ],
  "starting_state": "初始状态",
  "ending_state": "结局状态",
  "character_development_notes": "角色发展备注",

  "psychological_profile": {{
    "attachment_style": "依恋风格",
    "defense_mechanisms": ["心理防御机制"]
  }},
  "attachment_style": "依恋风格描述",
  "defense_mechanisms": ["防御机制1", "防御机制2"],
  "emotional_wounds": ["情感创伤1", "情感创伤2"],
  "resilience_factors": ["韧性因素1", "韧性因素2"],

  "speech_pattern": "说话风格描述",
  "speech_characteristics": ["说话特点1", "说话特点2"],
  "catchphrases": ["口头禅1", "口头禅2"],
  "communication_style": "沟通风格",

  "narrative_function": "在叙事中的功能",
  "thematic_significance": "主题意义",
  "character_arc_summary": "一句话角色弧线概括",

  "conflicts": [
    {{
      "conflict_type": "冲突类型（internal/external）",
      "description": "冲突描述",
      "parties_involved": ["相关方"],
      "stakes": "赌注",
      "current_status": "现状"
    }}
  ],

  "first_appearance": "首次出场时机",
  "status": "角色状态（active/deceased/missing）"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        skills = []
        for item in data.get("skills", []):
            if isinstance(item, dict):
                skills.append(CharacterSkill(
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    category=item.get("category", ""),
                    proficiency_level=item.get("proficiency_level", ""),
                    source=item.get("source", ""),
                ))

        groups = []
        for item in data.get("groups", []):
            if isinstance(item, dict):
                groups.append(CharacterGroup(
                    group_id=item.get("group_id", ""),
                    name=item.get("name", ""),
                    group_type=item.get("group_type", ""),
                    role=item.get("role", ""),
                    position=item.get("position", ""),
                    joined_at=item.get("joined_at", ""),
                ))

        growth_stages = []
        for item in data.get("growth_stages", []):
            if isinstance(item, dict):
                growth_stages.append(CharacterGrowthStage(
                    stage_name=item.get("stage_name", ""),
                    description=item.get("description", ""),
                    trigger_event=item.get("trigger_event", ""),
                    lessons_learned=item.get("lessons_learned", []),
                    new_abilities_or_insights=item.get("new_abilities_or_insights", []),
                    emotional_state=item.get("emotional_state", ""),
                ))

        relationships = []
        for item in data.get("relationships", []):
            if isinstance(item, dict):
                relationships.append(CharacterRelationship(
                    character_id=item.get("character_id", ""),
                    character_name=item.get("character_name", ""),
                    relationship_type=item.get("relationship_type", ""),
                    description=item.get("description", ""),
                    dynamics=item.get("dynamics", ""),
                    history=item.get("history", ""),
                    current_status=item.get("current_status", ""),
                ))

        conflicts = []
        for item in data.get("conflicts", []):
            if isinstance(item, dict):
                conflicts.append(CharacterConflict(
                    conflict_type=item.get("conflict_type", ""),
                    description=item.get("description", ""),
                    parties_involved=item.get("parties_involved", []),
                    stakes=item.get("stakes", ""),
                    current_status=item.get("current_status", ""),
                ))

        appearance = data.get("appearance", {})
        if isinstance(appearance, dict):
            appearance = appearance

        personality = data.get("personality", {})
        if isinstance(personality, dict):
            personality = personality

        return Character(
            id=data.get("id", f"char_{hash(data.get('name', 'unknown'))}"),
            name=data.get("name", "未知角色"),
            role=data.get("role", role),
            age=data.get("age", ""),
            age_numeric=data.get("age_numeric"),
            appearance=appearance if isinstance(appearance, dict) else {},
            distinguishing_features=data.get("distinguishing_features", []),
            presence=data.get("presence", ""),
            personality=personality if isinstance(personality, dict) else {},
            personality_description=data.get("personality_description", ""),
            values=data.get("values", []),
            fears=data.get("fears", []),
            desires=data.get("desires", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            habits=data.get("habits", []),
            backstory=data.get("backstory", ""),
            origin=data.get("origin", ""),
            family_background=data.get("family_background", ""),
            education=data.get("education", ""),
            previous_occupations=data.get("previous_occupations", []),
            formative_experiences=data.get("formative_experiences", []),
            motivation=data.get("motivation", ""),
            goal=data.get("goal", ""),
            internal_conflict=data.get("internal_conflict", ""),
            skills=skills,
            combat_abilities=data.get("combat_abilities", []),
            social_abilities=data.get("social_abilities", []),
            intellectual_abilities=data.get("intellectual_abilities", []),
            resources=data.get("resources", []),
            equipment=data.get("equipment", []),
            vehicles=data.get("vehicles", []),
            groups=groups,
            relationships=relationships,
            archetype=data.get("archetype", ""),
            growth_arc=data.get("growth_arc", ""),
            growth_stages=growth_stages,
            starting_state=data.get("starting_state", ""),
            ending_state=data.get("ending_state", ""),
            character_development_notes=data.get("character_development_notes", ""),
            psychological_profile=data.get("psychological_profile", {}),
            attachment_style=data.get("attachment_style", ""),
            defense_mechanisms=data.get("defense_mechanisms", []),
            emotional_wounds=data.get("emotional_wounds", []),
            resilience_factors=data.get("resilience_factors", []),
            speech_pattern=data.get("speech_pattern", ""),
            speech_characteristics=data.get("speech_characteristics", []),
            catchphrases=data.get("catchphrases", []),
            communication_style=data.get("communication_style", ""),
            narrative_function=data.get("narrative_function", ""),
            thematic_significance=data.get("thematic_significance", ""),
            character_arc_summary=data.get("character_arc_summary", ""),
            conflicts=conflicts,
            first_appearance=data.get("first_appearance", ""),
            death=data.get("death"),
            status=data.get("status", "active"),
        )

    async def generate_characters_batch(
        self,
        genre: str,
        theme: str,
        count: int = 5,
        role_distribution: Optional[dict] = None,
        world_context: Optional[dict] = None,
        character_system: Optional[CharacterSystem] = None,
    ) -> list[Character]:
        """Generate multiple characters at once.

        Args:
            genre: Novel genre
            theme: Central theme
            count: Number of characters to generate
            role_distribution: Optional dict specifying role distribution
            world_context: Optional world context
            character_system: Optional character system for guidance

        Returns:
            List of Character objects
        """
        roles = role_distribution or {
            "protagonist": 1,
            "antagonist": 1,
            "supporting": max(1, count - 3),
        }

        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        archetype_guidance = ""
        if character_system and character_system.archetypes:
            archetype_info = []
            for a in character_system.archetypes:
                archetype_info.append(f"- {a.name}: {a.description[:50]}")
            archetype_guidance = "可用角色原型：\n" + "\n".join(archetype_info[:5]) + "\n"

        prompt = f"""为{genre}类型小说生成{count}个角色。

主题：{theme}
{context}
{archetype_guidance}

角色分配：{roles}

请生成{count}个角色，以JSON数组格式输出：

[
  {{
    "id": "角色ID",
    "name": "角色姓名",
    "role": "角色类型（protagonist/antagonist/supporting/minor）",
    "age": "年龄描述",
    "age_numeric": 年龄,
    "appearance": {{"face": "面部", "body": "体型", "dressing": "着装", "overall": "整体"}},
    "distinguishing_features": ["显著特征"],
    "presence": "气质描述",
    "personality": {{"traits": ["性格特点"], "mbti": "MBTI"}},
    "personality_description": "性格描述",
    "values": ["价值观"],
    "fears": ["恐惧"],
    "desires": ["欲望"],
    "strengths": ["优点"],
    "weaknesses": ["缺点"],
    "habits": ["习惯"],
    "backstory": "背景故事",
    "origin": "出身",
    "family_background": "家庭背景",
    "education": "教育",
    "previous_occupations": ["之前职业"],
    "formative_experiences": ["塑造经历"],
    "motivation": "动机",
    "goal": "目标",
    "internal_conflict": "内心冲突",
    "skills": [{{"name": "技能", "description": "描述", "category": "类别", "proficiency_level": "程度", "source": "来源"}}],
    "combat_abilities": ["战斗能力"],
    "social_abilities": ["社交能力"],
    "intellectual_abilities": ["智力能力"],
    "resources": ["资源"],
    "equipment": ["装备"],
    "groups": [{{"group_id": "id", "name": "组织", "group_type": "类型", "role": "角色", "position": "职位"}}],
    "relationships": [{{"character_id": "id", "character_name": "姓名", "relationship_type": "类型", "description": "描述", "dynamics": "互动"}}],
    "archetype": "原型",
    "growth_arc": "成长弧线",
    "growth_stages": [{{"stage_name": "阶段", "description": "描述", "trigger_event": "触发", "lessons_learned": ["教训"], "new_abilities_or_insights": ["新能力"], "emotional_state": "情感"}}],
    "starting_state": "初始",
    "ending_state": "结局",
    "psychological_profile": {{"attachment_style": "风格", "defense_mechanisms": ["机制"]}},
    "attachment_style": "依恋风格",
    "defense_mechanisms": ["机制"],
    "emotional_wounds": ["创伤"],
    "resilience_factors": ["韧性"],
    "speech_pattern": "说话风格",
    "speech_characteristics": ["特点"],
    "catchphrases": ["口头禅"],
    "communication_style": "沟通风格",
    "narrative_function": "叙事功能",
    "thematic_significance": "主题意义",
    "character_arc_summary": "弧线概括",
    "conflicts": [{{"conflict_type": "类型", "description": "描述", "parties_involved": ["相关方"], "stakes": "赌注", "current_status": "状态"}}],
    "first_appearance": "首次出场",
    "status": "active"
  }}
]

以JSON数组格式输出完整列表。"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json_array(result)

        characters = []
        for item in data:
            if isinstance(item, dict):
                try:
                    skills = []
                    for s in item.get("skills", []):
                        if isinstance(s, dict):
                            skills.append(CharacterSkill(
                                name=s.get("name", ""),
                                description=s.get("description", ""),
                                category=s.get("category", ""),
                                proficiency_level=s.get("proficiency_level", ""),
                                source=s.get("source", ""),
                            ))

                    groups = []
                    for g in item.get("groups", []):
                        if isinstance(g, dict):
                            groups.append(CharacterGroup(
                                group_id=g.get("group_id", ""),
                                name=g.get("name", ""),
                                group_type=g.get("group_type", ""),
                                role=g.get("role", ""),
                                position=g.get("position", ""),
                                joined_at=g.get("joined_at", ""),
                            ))

                    growth_stages = []
                    for gs in item.get("growth_stages", []):
                        if isinstance(gs, dict):
                            growth_stages.append(CharacterGrowthStage(
                                stage_name=gs.get("stage_name", ""),
                                description=gs.get("description", ""),
                                trigger_event=gs.get("trigger_event", ""),
                                lessons_learned=gs.get("lessons_learned", []),
                                new_abilities_or_insights=gs.get("new_abilities_or_insights", []),
                                emotional_state=gs.get("emotional_state", ""),
                            ))

                    relationships = []
                    for r in item.get("relationships", []):
                        if isinstance(r, dict):
                            relationships.append(CharacterRelationship(
                                character_id=r.get("character_id", ""),
                                character_name=r.get("character_name", ""),
                                relationship_type=r.get("relationship_type", ""),
                                description=r.get("description", ""),
                                dynamics=r.get("dynamics", ""),
                                history=r.get("history", ""),
                                current_status=r.get("current_status", ""),
                            ))

                    conflicts = []
                    for c in item.get("conflicts", []):
                        if isinstance(c, dict):
                            conflicts.append(CharacterConflict(
                                conflict_type=c.get("conflict_type", ""),
                                description=c.get("description", ""),
                                parties_involved=c.get("parties_involved", []),
                                stakes=c.get("stakes", ""),
                                current_status=c.get("current_status", ""),
                            ))

                    characters.append(Character(
                        id=item.get("id", f"char_{len(characters)}"),
                        name=item.get("name", "未知"),
                        role=item.get("role", "supporting"),
                        age=item.get("age", ""),
                        age_numeric=item.get("age_numeric"),
                        appearance=item.get("appearance", {}),
                        distinguishing_features=item.get("distinguishing_features", []),
                        presence=item.get("presence", ""),
                        personality=item.get("personality", {}),
                        personality_description=item.get("personality_description", ""),
                        values=item.get("values", []),
                        fears=item.get("fears", []),
                        desires=item.get("desires", []),
                        strengths=item.get("strengths", []),
                        weaknesses=item.get("weaknesses", []),
                        habits=item.get("habits", []),
                        backstory=item.get("backstory", ""),
                        origin=item.get("origin", ""),
                        family_background=item.get("family_background", ""),
                        education=item.get("education", ""),
                        previous_occupations=item.get("previous_occupations", []),
                        formative_experiences=item.get("formative_experiences", []),
                        motivation=item.get("motivation", ""),
                        goal=item.get("goal", ""),
                        internal_conflict=item.get("internal_conflict", ""),
                        skills=skills,
                        combat_abilities=item.get("combat_abilities", []),
                        social_abilities=item.get("social_abilities", []),
                        intellectual_abilities=item.get("intellectual_abilities", []),
                        resources=item.get("resources", []),
                        equipment=item.get("equipment", []),
                        vehicles=item.get("vehicles", []),
                        groups=groups,
                        relationships=relationships,
                        archetype=item.get("archetype", ""),
                        growth_arc=item.get("growth_arc", ""),
                        growth_stages=growth_stages,
                        starting_state=item.get("starting_state", ""),
                        ending_state=item.get("ending_state", ""),
                        character_development_notes=item.get("character_development_notes", ""),
                        psychological_profile=item.get("psychological_profile", {}),
                        attachment_style=item.get("attachment_style", ""),
                        defense_mechanisms=item.get("defense_mechanisms", []),
                        emotional_wounds=item.get("emotional_wounds", []),
                        resilience_factors=item.get("resilience_factors", []),
                        speech_pattern=item.get("speech_pattern", ""),
                        speech_characteristics=item.get("speech_characteristics", []),
                        catchphrases=item.get("catchphrases", []),
                        communication_style=item.get("communication_style", ""),
                        narrative_function=item.get("narrative_function", ""),
                        thematic_significance=item.get("thematic_significance", ""),
                        character_arc_summary=item.get("character_arc_summary", ""),
                        conflicts=conflicts,
                        first_appearance=item.get("first_appearance", ""),
                        death=item.get("death"),
                        status=item.get("status", "active"),
                    ))
                except Exception:
                    continue

        return characters

    async def generate_character_relationship(
        self,
        character_a: Character,
        character_b: Character,
        relationship_type: str = "friend",
    ) -> CharacterRelationship:
        """Generate a relationship between two existing characters.

        Args:
            character_a: First character
            character_b: Second character
            relationship_type: Type of relationship

        Returns:
            CharacterRelationship object
        """
        prompt = f"""为两个角色生成关系设定。

角色A：{character_a.name}
- 类型：{character_a.role.value}
- 性格：{character_a.personality_description[:100] if character_a.personality_description else '未设定'}
- 背景：{character_a.backstory[:100] if character_a.backstory else '未设定'}

角色B：{character_b.name}
- 类型：{character_b.role.value}
- 性格：{character_b.personality_description[:100] if character_b.personality_description else '未设定'}
- 背景：{character_b.backstory[:100] if character_b.backstory else '未设定'}

关系类型：{relationship_type}

请以JSON格式输出关系设定：

{{
  "character_id": "{character_b.id}",
  "character_name": "{character_b.name}",
  "relationship_type": "{relationship_type}",
  "description": "关系描述",
  "dynamics": "互动模式",
  "history": "关系历史",
  "current_status": "现状",
  "key_events": ["关键事件1", "关键事件2"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return CharacterRelationship(
            character_id=data.get("character_id", character_b.id),
            character_name=data.get("character_name", character_b.name),
            relationship_type=data.get("relationship_type", relationship_type),
            description=data.get("description", ""),
            dynamics=data.get("dynamics", ""),
            history=data.get("history", ""),
            current_status=data.get("current_status", ""),
            key_events=data.get("key_events", []),
        )

    def analyze_character_consistency(
        self,
        characters: list[Character],
    ) -> dict[str, Any]:
        """Analyze characters for logical consistency.

        Checks for contradictions, gaps, and balance issues.

        Args:
            characters: List of characters to analyze

        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        suggestions = []

        if not characters:
            issues.append("没有角色可分析")
            return {
                "issues": issues,
                "warnings": warnings,
                "suggestions": suggestions,
                "status": "needs_review",
                "completeness_score": 0.0,
            }

        # Check for protagonist
        protagonists = [c for c in characters if c.role.value == "protagonist"]
        if not protagonists:
            issues.append("缺少主角（protagonist）")
        elif len(protagonists) > 1:
            warnings.append(f"有{len(protagonists)}个主角，可能需要明确主线主角")

        # Check for antagonist
        antagonists = [c for c in characters if c.role.value == "antagonist"]
        if not antagonists:
            warnings.append("缺少反派（antagonist）")

        # Check character names
        names = [c.name for c in characters]
        if len(names) != len(set(names)):
            warnings.append("存在同名角色，需要区分")

        # Check each character for completeness
        for char in characters:
            if not char.name:
                issues.append(f"角色ID {char.id} 缺少姓名")

            if not char.backstory:
                warnings.append(f"角色「{char.name}」缺少背景故事")

            if not char.motivation:
                warnings.append(f"角色「{char.name}」缺少动机设定")

            if not char.goal:
                warnings.append(f"角色「{char.name}」缺少目标设定")

            if char.role.value == "protagonist":
                if not char.growth_arc:
                    warnings.append(f"主角「{char.name}」缺少成长弧线")
                if not char.growth_stages:
                    suggestions.append(f"主角「{char.name}」可以添加详细的成长阶段")

            # Check relationships reference valid characters
            for rel in char.relationships:
                if rel.character_id and rel.character_id not in [c.id for c in characters]:
                    if rel.character_name and rel.character_name not in names:
                        warnings.append(f"角色「{char.name}」的关系「{rel.character_name}」引用了不存在的角色")

            # Check for balanced strengths/weaknesses
            if len(char.strengths) == 0 and len(char.weaknesses) == 0:
                warnings.append(f"角色「{char.name}」缺少优缺点设定")

            # Check for catchphrases/speech patterns for important characters
            if char.role.value in ["protagonist", "antagonist"]:
                if not char.speech_pattern:
                    suggestions.append(f"重要角色「{char.name}」可以添加说话风格设定")

        # Check relationship network
        all_related_ids = set()
        for char in characters:
            for rel in char.relationships:
                if rel.character_id:
                    all_related_ids.add(rel.character_id)

        orphan_chars = [c for c in characters if c.id not in all_related_ids and len(characters) > 1]
        if len(characters) > 2 and len(orphan_chars) > len(characters) // 2:
            suggestions.append("有较多角色没有建立关系网络，建议增加角色间互动")

        return {
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "status": "consistent" if not issues else "needs_review",
            "completeness_score": self._calculate_completeness(characters),
            "protagonist_count": len(protagonists),
            "antagonist_count": len(antagonists),
            "total_characters": len(characters),
        }

    def _calculate_completeness(self, characters: list[Character]) -> float:
        """Calculate how complete the characters are (0.0 - 1.0)."""
        if not characters:
            return 0.0

        total_score = 0.0
        for char in characters:
            score = 0.0
            max_score = 10.0

            if char.name:
                score += 0.5
            if char.age:
                score += 0.3
            if char.appearance:
                score += 0.5
            if char.personality:
                score += 0.5
            if char.personality_description:
                score += 0.3
            if char.backstory:
                score += 1.0
            if char.motivation:
                score += 0.5
            if char.goal:
                score += 0.5
            if char.strengths:
                score += min(0.5, len(char.strengths) * 0.1)
            if char.weaknesses:
                score += min(0.5, len(char.weaknesses) * 0.1)
            if char.skills:
                score += min(0.5, len(char.skills) * 0.1)
            if char.relationships:
                score += min(0.5, len(char.relationships) * 0.1)
            if char.growth_arc:
                score += 1.0
            if char.speech_pattern:
                score += 0.5
            if char.conflicts:
                score += 0.5

            total_score += score / max_score

        return round(total_score / len(characters), 2)

    def validate_character_development(
        self,
        character: Character,
    ) -> dict[str, Any]:
        """Validate character's growth arc for logical progression.

        Args:
            character: Character to validate

        Returns:
            Dict with validation results
        """
        issues = []
        suggestions = []

        if character.role.value not in ["protagonist", "deuteragonist"]:
            return {
                "valid": True,
                "issues": [],
                "suggestions": ["此角色类型不需要详细的成长弧线"],
                "character_name": character.name,
            }

        if not character.growth_arc:
            issues.append("角色缺少成长弧线描述")
        else:
            # Check for starting and ending states
            if not character.starting_state:
                issues.append("缺少初始状态描述")
            if not character.ending_state:
                issues.append("缺少结局状态描述")

            # Check for growth stages
            if not character.growth_stages:
                suggestions.append("可以添加详细的成长阶段来展示角色变化")
            else:
                if len(character.growth_stages) < 2:
                    issues.append("成长阶段过少，建议至少2个阶段展示变化过程")

                # Check for logical progression
                for i, stage in enumerate(character.growth_stages):
                    if not stage.stage_name:
                        warnings.append(f"第{i+1}个成长阶段缺少阶段名称")
                    if not stage.trigger_event:
                        suggestions.append(f"第{i+1}个成长阶段「{stage.stage_name}」缺少触发事件")
                    if not stage.lessons_learned:
                        suggestions.append(f"第{i+1}个成长阶段「{stage.stage_name}」缺少角色学到的教训")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "character_name": character.name,
            "has_growth_arc": bool(character.growth_arc),
            "has_starting_state": bool(character.starting_state),
            "has_ending_state": bool(character.ending_state),
            "growth_stage_count": len(character.growth_stages),
        }

    def get_character_summary(
        self,
        character: Character,
    ) -> str:
        """Get a human-readable summary of a character.

        Args:
            character: Character to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {character.name} ===",
            f"角色类型: {character.role.value}",
            f"年龄: {character.age or '未设定'}",
            "",
        ]

        if character.archetype:
            lines.append(f"【原型】{character.archetype}")

        if character.presence:
            lines.append(f"【气质】{character.presence}")

        if character.personality_description:
            lines.extend(["", "【性格】"])
            lines.append(f"  {character.personality_description}")

        if character.values:
            lines.extend(["", "【价值观】"])
            lines.append(f"  {', '.join(character.values)}")

        if character.fears:
            lines.extend(["", "【恐惧】"])
            lines.append(f"  {', '.join(character.fears)}")

        if character.desires:
            lines.extend(["", "【欲望】"])
            lines.append(f"  {', '.join(character.desires)}")

        if character.strengths:
            lines.extend(["", "【优点】"])
            lines.append(f"  {', '.join(character.strengths)}")

        if character.weaknesses:
            lines.extend(["", "【缺点】"])
            lines.append(f"  {', '.join(character.weaknesses)}")

        if character.backstory:
            lines.extend(["", "【背景】"])
            lines.append(f"  {character.backstory[:200]}...")

        if character.motivation:
            lines.extend(["", "【动机】"])
            lines.append(f"  {character.motivation}")

        if character.goal:
            lines.extend(["", "【目标】"])
            lines.append(f"  {character.goal}")

        if character.skills:
            lines.extend(["", "【技能】"])
            for skill in character.skills[:5]:
                lines.append(f"  • {skill.name}: {skill.description[:50] if skill.description else '无描述'}...")

        if character.relationships:
            lines.extend(["", f"【关系】({len(character.relationships)})"])
            for rel in character.relationships[:3]:
                lines.append(f"  • {rel.character_name or rel.character_id} ({rel.relationship_type})")

        if character.growth_arc:
            lines.extend(["", "【成长弧线】"])
            lines.append(f"  {character.growth_arc}")

        if character.speech_pattern:
            lines.extend(["", "【说话风格】"])
            lines.append(f"  {character.speech_pattern}")

        if character.catchphrases:
            lines.append(f"  口头禅: {', '.join(character.catchphrases[:3])}")

        if character.conflicts:
            lines.extend(["", "【冲突】"])
            for conflict in character.conflicts[:2]:
                lines.append(f"  • {conflict.conflict_type}: {conflict.description[:50]}...")

        lines.extend(["", f"状态: {character.status}"])
        if character.first_appearance:
            lines.append(f"首次出场: {character.first_appearance}")

        return "\n".join(lines)

    def export_character_system(
        self,
        character_system: CharacterSystem,
        characters: Optional[list[Character]] = None,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """Export character system as a complete document.

        Args:
            character_system: Character system to export
            characters: Optional list of characters
            include_analysis: Whether to include consistency analysis

        Returns:
            Complete export dict
        """
        export_data = {
            "character_system": character_system.model_dump(),
            "summary": self.get_character_system_summary(character_system),
        }

        if characters:
            export_data["characters"] = [c.model_dump() for c in characters]
            export_data["character_summaries"] = [self.get_character_summary(c) for c in characters]

        if include_analysis and characters:
            export_data["analysis"] = self.analyze_character_consistency(characters)
            for char in characters:
                export_data[f"character_{char.id}_validation"] = self.validate_character_development(char)

        return export_data

    def get_character_system_summary(
        self,
        character_system: CharacterSystem,
    ) -> str:
        """Get a human-readable summary of the character system.

        Args:
            character_system: Character system to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {character_system.name} ===",
            f"类型: {character_system.genre}",
            f"主题: {character_system.theme}",
            "",
        ]

        if character_system.archetypes:
            lines.extend(["", "【角色原型】"])
            for archetype in character_system.archetypes:
                lines.append(f"  • {archetype.name}: {archetype.description[:50]}...")

        if character_system.relationship_templates:
            lines.extend(["", "【关系模板】"])
            for template in character_system.relationship_templates[:3]:
                if isinstance(template, dict):
                    lines.append(f"  • {template.get('type', '未知')}: {template.get('description', '')[:50]}...")

        if character_system.role_distribution:
            lines.extend(["", "【角色分布】"])
            for role, count in character_system.role_distribution.items():
                lines.append(f"  • {role}: {count}")

        if character_system.group_templates:
            lines.extend(["", "【团队模板】"])
            for group in character_system.group_templates[:3]:
                if isinstance(group, dict):
                    lines.append(f"  • {group.get('name', '未知')}: {group.get('type', '')}")

        if character_system.generation_guidelines:
            lines.extend(["", "【生成指南】"])
            lines.append(f"  {character_system.generation_guidelines[:200]}...")

        return "\n".join(lines)

    async def expand_character_system(
        self,
        character_system: CharacterSystem,
        expansion_type: str,
    ) -> CharacterSystem:
        """Expand an existing character system with new content.

        Args:
            character_system: Existing character system
            expansion_type: What to expand (archetypes, group_templates, relationship_templates)

        Returns:
            Updated CharacterSystem with new content
        """
        if expansion_type == "archetypes":
            existing_names = [a.name for a in character_system.archetypes]
            prompt = f"""请为以下角色系统添加更多角色原型。

现有系统：{character_system.name}
已有原型数量：{len(character_system.archetypes)}

请生成3-5个新的角色原型补充，以JSON数组格式输出：

[
  {{
    "name": "原型名称",
    "description": "原型描述",
    "typical_traits": ["典型特征"],
    "typical_motivations": ["典型动机"],
    "typical_weaknesses": ["典型缺点"],
    "growth_potential": "成长潜力",
    "examples_in_literature": ["文学例子"]
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    character_system.archetypes.append(CharacterArchetype(
                        name=item.get("name", ""),
                        description=item.get("description", ""),
                        typical_traits=item.get("typical_traits", []),
                        typical_motivations=item.get("typical_motivations", []),
                        typical_weaknesses=item.get("typical_weaknesses", []),
                        growth_potential=item.get("growth_potential", ""),
                        examples_in_literature=item.get("examples_in_literature", []),
                    ))

        elif expansion_type == "group_templates":
            existing_names = [g.get("name", "") if isinstance(g, dict) else "" for g in character_system.group_templates]
            prompt = f"""请为以下角色系统添加更多团队/组织模板。

现有系统：{character_system.name}
已有模板数量：{len(character_system.group_templates)}

请生成2-4个新的团队模板补充，以JSON数组格式输出：

[
  {{
    "name": "模板名称",
    "type": "类型",
    "typical_structure": "典型结构",
    "roles_within_group": ["典型角色定位"],
    "internal_conflicts": "内部冲突"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    character_system.group_templates.append(item)

        elif expansion_type == "relationship_templates":
            prompt = f"""请为以下角色系统添加更多关系模板。

现有系统：{character_system.name}
已有模板数量：{len(character_system.relationship_templates)}

请生成3-5个新的关系模板补充，以JSON数组格式输出：

[
  {{
    "type": "关系类型",
    "description": "描述",
    "typical_dynamics": "典型互动",
    "common_conflicts": "常见冲突",
    "development_potential": "发展潜力"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            for item in data:
                if isinstance(item, dict):
                    character_system.relationship_templates.append(item)

        return character_system