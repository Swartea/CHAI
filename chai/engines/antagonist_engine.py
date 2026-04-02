"""Antagonist engine for generating and managing villain characters."""

from typing import Optional, Any
from chai.models.antagonist import (
    Antagonist,
    AntagonistProfile,
    AntagonistSystem,
    AntagonistType,
    AntagonistAppearance,
    AntagonistPersonality,
    AntagonistBackground,
    AntagonistMotivation,
    AntagonistRelationship,
    AntagonistPower,
    AntagonistOrganization,
    AntagonistArc,
    AntagonistConflict,
    AntagonistTactics,
)
from chai.models import Character, CharacterRole, MainCharacter
from chai.services import AIService


class AntagonistEngine:
    """Engine for generating and managing antagonist characters.

    Antagonists are characters who oppose the protagonist.
    They can range from pure evil villains to sympathetic adversaries.
    Each has their own motivations, methods, and relationship with the protagonist.
    """

    def __init__(self, ai_service: AIService):
        """Initialize antagonist engine with AI service."""
        self.ai_service = ai_service

    async def generate_antagonist(
        self,
        antagonist_type: AntagonistType,
        genre: str,
        theme: str,
        protagonist: Optional[MainCharacter] = None,
        existing_characters: Optional[list[Character]] = None,
        world_context: Optional[dict] = None,
    ) -> Antagonist:
        """Generate an antagonist character.

        Args:
            antagonist_type: Type of antagonist
            genre: Novel genre
            theme: Central theme
            protagonist: Optional protagonist for relationship
            existing_characters: Optional list of existing characters
            world_context: Optional world context

        Returns:
            Antagonist object
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
优势：{', '.join(protagonist.strengths[:3]) if protagonist.strengths else '未设定'}
弱点：{', '.join(protagonist.weaknesses[:3]) if protagonist.weaknesses else '未设定'}
"""

        existing_chars_info = ""
        if existing_characters:
            chars_info = []
            for c in existing_characters[:3]:
                chars_info.append(f"- {c.name}（{c.role.value}）")
            existing_chars_info = "已有角色：\n" + "\n".join(chars_info) + "\n"

        type_descriptions = {
            AntagonistType.VILLAIN: "恶棍型 - 纯粹的邪恶，为了作恶而作恶",
            AntagonistType.DARK_HERO: "黑暗英雄型 - 道义上灰色地带的角色",
            AntagonistType.TEMPORARY_ANTAGONIST: "临时反派 - 曾经是盟友，后来成为敌人",
            AntagonistType.ETERNAL_RIVAL: "终身对手 - 持续不断的竞争对手",
            AntagonistType.TYRANT: "暴君型 - 残暴的统治者",
            AntagonistType.MANIPULATOR: "操控者型 - 通过操纵他人来达成目的",
            AntagonistType.REVENGE_SEEKER: "复仇者型 - 被复仇所驱动",
            AntagonistType.CORRUPTED: "堕落型 - 曾是好人，后来变坏",
            AntagonistType.IDEOLOGICAL: "意识形态型 - 有着对立的信念体系",
            AntagonistType.TRAGIC_ANTAGONIST: "悲剧反派 - 令人同情的反派",
            AntagonistType.MINION: "爪牙型 - 真正敌人的手下",
            AntagonistType.BIG_BAD: "大反派 - 主要的终极敌人",
            AntagonistType.TEMPTER: "诱惑者型 - 试图诱惑主角走错路",
            AntagonistType.SHADOW: "影子型 - 主角的黑暗面映射",
            AntagonistType.NEMESIS: "死敌型 - 主角的终极对手",
        }

        prompt = f"""生成一个{type_descriptions.get(antagonist_type, antagonist_type.value)}反派角色。

类型：{genre}
主题：{theme}
{context}
{protagonist_info}
{existing_chars_info}

请生成一个完整的反派角色，以JSON格式输出：

{{
  "id": "唯一标识符",
  "name": "角色姓名",
  "antagonist_type": "{antagonist_type.value}",
  "description": "角色简要描述",

  "age": "年龄描述",
  "age_numeric": 年龄数值,
  "appearance": {{
    "face": "面部特征（如：棱角分明的脸庞，带着冷酷）",
    "eyes": "眼睛描写（如：冰冷的灰色眼眸）",
    "hair": "发型发色（如：漆黑的长发）",
    "body": "体型（如：高大威猛）",
    "skin": "肤色（如：苍白如纸）",
    "dressing": "着装风格（如：华丽的黑色长袍）",
    "accessories": ["标志性配饰"],
    "overall": "整体形象（如：让人不寒而栗的存在感）"
  }},
  "distinguishing_features": ["显著特征1", "显著特征2"],
  "presence": "气场描述（如：压迫感十足的威严）",
  "first_impression": "第一眼印象",

  "personality": {{
    "core_traits": ["核心性格特点1", "特点2"],
    "personality_description": "详细性格描述（100字以上）",
    "mbti": "MBTI类型",
    "moral_alignment": "道德立场描述",
    "values": ["扭曲的价值观1", "价值观2"],
    "fears": ["恐惧1", "恐惧2"],
    "desires": ["欲望1", "欲望2"],
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["弱点1", "弱点2"],
    "habits": ["习惯1", "习惯2"],
    "emotional_pattern": "典型情绪反应模式"
  }},

  "background": {{
    "origin": "出身来历",
    "family_background": "家庭背景",
    "education": "教育背景",
    "previous_occupations": ["之前职业1", "职业2"],
    "key_experiences": ["关键经历1", "经历2"],
    "downfall_moments": ["堕落时刻1", "时刻2"],
    "socioeconomic_status": "社会经济地位"
  }},
  "backstory": "背景故事详细描述（100字以上）",
  "origin_story": "成为反派的起源故事",

  "motivation": {{
    "surface_motivation": "表面动机/目标",
    "deep_motivation": "深层心理动机",
    "motivation_type": "动机类型",
    "motivation_origin": "动机的起源",
    "justification": "如何为自己的行为辩护",
    "twisted_logic": "扭曲的逻辑",
    "personal_goals": ["个人目标1", "目标2"],
    "what_they_lost": "他们失去的东西"
  }},

  "relationship_to_protagonist": {{
    "protagonist_id": "主角ID",
    "protagonist_name": "主角姓名",
    "relationship_type": "对立/敌对类型",
    "relationship_dynamics": "对立互动模式",
    "history": "对立历史",
    "current_status": "现状",
    "key_conflicts": ["关键冲突点1", "冲突2"],
    "mirrors_protagonist": 是否镜像主角,
    "symmetry_points": ["与主角的相似点1", "相似点2"]
  }},

  "power": {{
    "power_source": "力量来源",
    "power_type": "力量类型",
    "combat_abilities": ["战斗能力1", "能力2"],
    "social_abilities": ["社交/政治能力"],
    "intellectual_abilities": ["智力能力"],
    "special_abilities": ["特殊能力1", "能力2"],
    "weaknesses": ["可以被利用的弱点"],
    "power_limitations": "力量的局限性"
  }},

  "organization": {{
    "organization_name": "组织名称",
    "organization_type": "组织类型",
    "size": "规模",
    "structure": "组织结构",
    "key_members": ["关键成员1", "成员2"],
    "resources": ["资源1", "资源2"],
    "territories": ["控制的领土"],
    "power_base": "势力基础"
  }},

  "tactics": {{
    "preferred_methods": ["常用手段1", "手段2"],
    "manipulation_tactics": ["操控手段1", "手段2"],
    "combat_style": "战斗风格",
    "social_strategy": "社交/政治策略",
    "deception_patterns": ["欺骗模式1"],
    "response_to_defeat": "失败时的反应"
  }},

  "character_arc": {{
    "archetype": "反派原型",
    "arc_type": "弧线类型",
    "starting_state": "初始状态",
    "ending_state": "结局状态",
    "corruption_arc": "堕落弧线",
    "redemption_potential": "救赎可能性",
    "transformation": "转变描述",
    "impact_on_protagonist": "对主角的影响"
  }},

  "psychological_profile": {{
    "attachment_style": "依恋风格",
    "defense_mechanisms": ["防御机制1"]
  }},
  "attachment_style": "依恋风格",
  "defense_mechanisms": ["防御机制1", "机制2"],
  "emotional_wounds": ["情感创伤1"],
  "vulnerability": "关键弱点/软肋",

  "speech_pattern": "说话风格描述",
  "catchphrases": ["标志性台词1", "台词2"],
  "communication_style": "沟通风格",

  "narrative_function": "在叙事中的功能",
  "thematic_significance": "主题意义",
  "threat_level": "威胁等级（low/medium/high/catastrophic）",

  "conflicts": [
    {{
      "conflict_type": "冲突类型",
      "description": "冲突描述",
      "against_protagonist": ["与主角的冲突点"],
      "internal_conflict": "内心挣扎",
      "external_conflicts": ["其他外部冲突"],
      "stakes": "赌注",
      "potential_resolution": "可能的解决方式"
    }}
  ],

  "first_appearance": "首次出场时机",
  "death": "死亡信息（如有）",
  "status": "角色状态",
  "defeat_conditions": ["被击败的条件1", "条件2"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return self._parse_antagonist(data, antagonist_type)

    def _parse_antagonist(
        self,
        data: dict,
        antagonist_type: AntagonistType,
    ) -> Antagonist:
        """Parse JSON data into Antagonist object."""
        appearance_data = data.get("appearance", {})
        appearance = AntagonistAppearance(
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
        personality = AntagonistPersonality(
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
        background = AntagonistBackground(
            origin=background_data.get("origin", ""),
            family_background=background_data.get("family_background", ""),
            education=background_data.get("education", ""),
            previous_occupations=background_data.get("previous_occupations", []),
            key_experiences=background_data.get("key_experiences", []),
            downfall_moments=background_data.get("downfall_moments", []),
            socioeconomic_status=background_data.get("socioeconomic_status", ""),
        )

        motivation_data = data.get("motivation", {})
        motivation = AntagonistMotivation(
            surface_motivation=motivation_data.get("surface_motivation", ""),
            deep_motivation=motivation_data.get("deep_motivation", ""),
            motivation_type=motivation_data.get("motivation_type", ""),
            motivation_origin=motivation_data.get("motivation_origin", ""),
            justification=motivation_data.get("justification", ""),
            twisted_logic=motivation_data.get("twisted_logic", ""),
            personal_goals=motivation_data.get("personal_goals", []),
            what_they_lost=motivation_data.get("what_they_lost", ""),
        )

        relationship_data = data.get("relationship_to_protagonist", {})
        relationship = AntagonistRelationship(
            protagonist_id=relationship_data.get("protagonist_id", ""),
            protagonist_name=relationship_data.get("protagonist_name", ""),
            relationship_type=relationship_data.get("relationship_type", ""),
            relationship_dynamics=relationship_data.get("relationship_dynamics", ""),
            history=relationship_data.get("history", ""),
            current_status=relationship_data.get("current_status", ""),
            key_conflicts=relationship_data.get("key_conflicts", []),
            mirrors_protagonist=relationship_data.get("mirrors_protagonist", False),
            symmetry_points=relationship_data.get("symmetry_points", []),
        )

        power_data = data.get("power", {})
        power = AntagonistPower(
            power_source=power_data.get("power_source", ""),
            power_type=power_data.get("power_type", ""),
            combat_abilities=power_data.get("combat_abilities", []),
            social_abilities=power_data.get("social_abilities", []),
            intellectual_abilities=power_data.get("intellectual_abilities", []),
            special_abilities=power_data.get("special_abilities", []),
            weaknesses=power_data.get("weaknesses", []),
            power_limitations=power_data.get("power_limitations", ""),
        )

        organization_data = data.get("organization", {})
        organization = AntagonistOrganization(
            organization_name=organization_data.get("organization_name", ""),
            organization_type=organization_data.get("organization_type", ""),
            size=organization_data.get("size", ""),
            structure=organization_data.get("structure", ""),
            key_members=organization_data.get("key_members", []),
            resources=organization_data.get("resources", []),
            territories=organization_data.get("territories", []),
            power_base=organization_data.get("power_base", ""),
        )

        tactics_data = data.get("tactics", {})
        tactics = AntagonistTactics(
            preferred_methods=tactics_data.get("preferred_methods", []),
            manipulation_tactics=tactics_data.get("manipulation_tactics", []),
            combat_style=tactics_data.get("combat_style", ""),
            social_strategy=tactics_data.get("social_strategy", ""),
            deception_patterns=tactics_data.get("deception_patterns", []),
            response_to_defeat=tactics_data.get("response_to_defeat", ""),
        )

        arc_data = data.get("character_arc", {})
        arc = AntagonistArc(
            archetype=arc_data.get("archetype", ""),
            arc_type=arc_data.get("arc_type", ""),
            starting_state=arc_data.get("starting_state", ""),
            ending_state=arc_data.get("ending_state", ""),
            corruption_arc=arc_data.get("corruption_arc", ""),
            redemption_potential=arc_data.get("redemption_potential", ""),
            transformation=arc_data.get("transformation", ""),
            impact_on_protagonist=arc_data.get("impact_on_protagonist", ""),
        )

        conflicts = []
        for item in data.get("conflicts", []):
            if isinstance(item, dict):
                conflicts.append(AntagonistConflict(
                    conflict_type=item.get("conflict_type", ""),
                    description=item.get("description", ""),
                    against_protagonist=item.get("against_protagonist", []),
                    internal_conflict=item.get("internal_conflict", ""),
                    external_conflicts=item.get("external_conflicts", []),
                    stakes=item.get("stakes", ""),
                    potential_resolution=item.get("potential_resolution", ""),
                ))

        return Antagonist(
            id=data.get("id", f"antagonist_{hash(data.get('name', 'unknown'))}"),
            name=data.get("name", "未知反派"),
            antagonist_type=antagonist_type,
            description=data.get("description", ""),
            age=data.get("age", ""),
            age_numeric=data.get("age_numeric"),
            appearance=appearance,
            distinguishing_features=data.get("distinguishing_features", []),
            presence=data.get("presence", ""),
            first_impression=data.get("first_impression", ""),
            personality=personality,
            background=background,
            backstory=data.get("backstory", ""),
            origin_story=data.get("origin_story", ""),
            motivation=motivation,
            relationship_to_protagonist=relationship,
            power=power,
            organization=organization,
            tactics=tactics,
            character_arc=arc,
            psychological_profile=data.get("psychological_profile", {}),
            attachment_style=data.get("attachment_style", ""),
            defense_mechanisms=data.get("defense_mechanisms", []),
            emotional_wounds=data.get("emotional_wounds", []),
            vulnerability=data.get("vulnerability", ""),
            speech_pattern=data.get("speech_pattern", ""),
            catchphrases=data.get("catchphrases", []),
            communication_style=data.get("communication_style", ""),
            narrative_function=data.get("narrative_function", ""),
            thematic_significance=data.get("thematic_significance", ""),
            threat_level=data.get("threat_level", ""),
            conflicts=conflicts,
            first_appearance=data.get("first_appearance", ""),
            death=data.get("death"),
            status=data.get("status", "active"),
            defeat_conditions=data.get("defeat_conditions", []),
        )

    async def generate_antagonist_system(
        self,
        genre: str,
        theme: str,
        protagonist: Optional[MainCharacter] = None,
        world_context: Optional[dict] = None,
    ) -> AntagonistSystem:
        """Generate a complete antagonist system with primary and secondary antagonists.

        Args:
            genre: Novel genre
            theme: Central theme
            protagonist: Optional protagonist
            world_context: Optional world context

        Returns:
            AntagonistSystem with all antagonists
        """
        protagonist_info = ""
        if protagonist:
            protagonist_info = f"""主角信息：
姓名：{protagonist.name}
性格：{protagonist.personality_description[:100] if protagonist.personality_description else '未设定'}
优势：{', '.join(protagonist.strengths[:3]) if protagonist.strengths else '未设定'}
弱点：{', '.join(protagonist.weaknesses[:3]) if protagonist.weaknesses else '未设定'}
目标：{protagonist.goal or '未设定'}
"""

        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        prompt = f"""为{genre}类型小说设计完整的反派体系。

类型：{genre}
主题：{theme}
{context}
{protagonist_info}

请设计一个包含主要反派和次要反派的反派体系：

1. 主要反派（Big Bad）：故事的主要威胁
2. 次要反派：各种类型的对手和威胁

请生成反派体系，以JSON格式输出：

{{
  "name": "反派体系名称",
  "protagonist_id": "主角ID",
  "primary_antagonist": {{
    "id": "唯一标识符",
    "name": "角色姓名",
    "antagonist_type": "big_bad/shadow/nemesis/tempter",
    "description": "简要描述",
    "age": "年龄描述",
    "age_numeric": 年龄数值,
    "appearance": {{"face": "面部", "eyes": "眼睛", "hair": "发型", "body": "体型", "dressing": "着装", "overall": "整体"}},
    "distinguishing_features": ["显著特征"],
    "presence": "气场",
    "first_impression": "第一印象",
    "personality": {{"core_traits": ["性格"], "personality_description": "描述", "mbti": "MBTI", "moral_alignment": "道德", "values": ["价值观"], "fears": ["恐惧"], "desires": ["欲望"], "strengths": ["优势"], "weaknesses": ["弱点"]}},
    "background": {{"origin": "出身", "family_background": "家庭", "education": "教育", "previous_occupations": ["职业"], "key_experiences": ["经历"], "downfall_moments": ["堕落"]}},
    "backstory": "背景故事",
    "origin_story": "成为反派的故事",
    "motivation": {{"surface_motivation": "表面动机", "deep_motivation": "深层动机", "motivation_type": "类型", "motivation_origin": "起源", "justification": "自我辩护", "twisted_logic": "扭曲逻辑", "personal_goals": ["目标"], "what_they_lost": "失去的"}},
    "relationship_to_protagonist": {{"relationship_type": "对立类型", "relationship_dynamics": "互动模式", "history": "历史", "current_status": "现状", "key_conflicts": ["冲突"], "mirrors_protagonist": false, "symmetry_points": ["相似点"]}},
    "power": {{"power_source": "力量来源", "power_type": "力量类型", "combat_abilities": ["战斗"], "social_abilities": ["社交"], "intellectual_abilities": ["智力"], "special_abilities": ["特殊"], "weaknesses": ["弱点"], "power_limitations": "限制"}},
    "organization": {{"organization_name": "组织", "organization_type": "类型", "size": "规模", "structure": "结构", "key_members": ["成员"], "resources": ["资源"], "territories": ["领土"], "power_base": "基础"}},
    "tactics": {{"preferred_methods": ["方法"], "manipulation_tactics": ["操控"], "combat_style": "战斗", "social_strategy": "策略", "deception_patterns": ["欺骗"], "response_to_defeat": "失败反应"}},
    "character_arc": {{"archetype": "原型", "arc_type": "弧线", "starting_state": "初始", "ending_state": "结局", "corruption_arc": "堕落", "redemption_potential": "救赎可能", "transformation": "转变", "impact_on_protagonist": "对主角影响"}},
    "vulnerability": "弱点",
    "speech_pattern": "说话风格",
    "catchphrases": ["台词"],
    "narrative_function": "叙事功能",
    "thematic_significance": "主题意义",
    "threat_level": "威胁等级",
    "first_appearance": "首次出场",
    "status": "状态",
    "defeat_conditions": ["击败条件"]
  }},
  "secondary_antagonists": [
    {{
      "id": "ID",
      "name": "姓名",
      "antagonist_type": "villain/revenge_seeker/manipulator/temporary_antagonist/ideological/corrupted/tragic_antagonist/minion/tyrant/dark_hero/eternal_rival",
      "description": "描述",
      "age": "年龄",
      "personality": {{"core_traits": ["特点"], "personality_description": "描述", "mbti": "MBTI", "fears": ["恐惧"], "desires": ["欲望"], "strengths": ["优势"], "weaknesses": ["弱点"]}},
      "background": {{"origin": "出身", "key_experiences": ["经历"]}},
      "backstory": "背景",
      "motivation": {{"surface_motivation": "动机", "deep_motivation": "深层动机", "justification": "辩护"}},
      "relationship_to_protagonist": {{"relationship_type": "关系", "key_conflicts": ["冲突"]}},
      "power": {{"power_source": "力量", "combat_abilities": ["战斗"], "special_abilities": ["特殊"]}},
      "tactics": {{"preferred_methods": ["方法"]}},
      "character_arc": {{"archetype": "原型", "arc_type": "弧线", "impact_on_protagonist": "影响"}},
      "vulnerability": "弱点",
      "threat_level": "威胁",
      "status": "状态"
    }}
  ],
  "minion_types": ["爪牙类型1", "类型2"],
  "organization_templates": [{{"name": "组织模板", "type": "类型", "typical_structure": "结构"}}],
  "conflict_potential": "冲突升级潜力"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        primary = None
        if data.get("primary_antagonist"):
            primary_data = data["primary_antagonist"]
            primary_type_str = primary_data.get("antagonist_type", "big_bad")
            try:
                primary_type = AntagonistType(primary_type_str)
            except ValueError:
                primary_type = AntagonistType.BIG_BAD
            primary = self._parse_antagonist(primary_data, primary_type)

        secondary = []
        for item in data.get("secondary_antagonists", []):
            if isinstance(item, dict):
                try:
                    type_str = item.get("antagonist_type", "villain")
                    try:
                        ant_type = AntagonistType(type_str)
                    except ValueError:
                        ant_type = AntagonistType.VILLAIN
                    secondary.append(self._parse_antagonist(item, ant_type))
                except Exception:
                    continue

        return AntagonistSystem(
            name=data.get("name", "反派体系"),
            protagonist_id=data.get("protagonist_id", ""),
            primary_antagonist=primary,
            secondary_antagonists=secondary,
            minion_types=data.get("minion_types", []),
            organization_templates=data.get("organization_templates", []),
            conflict_potential=data.get("conflict_potential", ""),
        )

    def create_profile(self, antagonist: Antagonist) -> AntagonistProfile:
        """Create a complete profile from antagonist.

        Args:
            antagonist: Source antagonist

        Returns:
            AntagonistProfile
        """
        return AntagonistProfile(
            basic_info={
                "id": antagonist.id,
                "name": antagonist.name,
                "antagonist_type": antagonist.antagonist_type.value,
                "age": antagonist.age,
                "threat_level": antagonist.threat_level,
                "status": antagonist.status,
            },
            appearance=antagonist.appearance,
            personality=antagonist.personality,
            background=antagonist.background,
            motivation=antagonist.motivation,
            relationship_to_protagonist=antagonist.relationship_to_protagonist,
            power=antagonist.power,
            organization=antagonist.organization,
            tactics=antagonist.tactics,
            character_arc=antagonist.character_arc,
            speech_pattern=antagonist.speech_pattern,
            catchphrases=antagonist.catchphrases,
            narrative_function=antagonist.narrative_function,
            thematic_significance=antagonist.thematic_significance,
            threat_level=antagonist.threat_level,
        )

    def to_character(self, antagonist: Antagonist) -> Character:
        """Convert Antagonist to base Character model.

        Args:
            antagonist: Source antagonist

        Returns:
            Character object
        """
        return Character(
            id=antagonist.id,
            name=antagonist.name,
            role=CharacterRole.ANTAGONIST,
            age=antagonist.age,
            age_numeric=antagonist.age_numeric,
            appearance=antagonist.appearance.model_dump(),
            distinguishing_features=antagonist.distinguishing_features,
            presence=antagonist.presence,
            personality=antagonist.personality.model_dump(),
            personality_description=antagonist.personality.personality_description,
            values=antagonist.personality.values,
            fears=antagonist.personality.fears,
            desires=antagonist.personality.desires,
            strengths=antagonist.personality.strengths,
            weaknesses=antagonist.personality.weaknesses,
            habits=antagonist.personality.habits,
            backstory=antagonist.backstory,
            origin=antagonist.background.origin,
            family_background=antagonist.background.family_background,
            education=antagonist.background.education,
            previous_occupations=antagonist.background.previous_occupations,
            formative_experiences=antagonist.background.key_experiences,
            motivation=antagonist.motivation.surface_motivation,
            goal="; ".join(antagonist.motivation.personal_goals),
            internal_conflict=antagonist.motivation.justification,
            combat_abilities=antagonist.power.combat_abilities,
            social_abilities=antagonist.power.social_abilities,
            intellectual_abilities=antagonist.power.intellectual_abilities,
            speech_pattern=antagonist.speech_pattern,
            catchphrases=antagonist.catchphrases,
            communication_style=antagonist.communication_style,
            narrative_function=antagonist.narrative_function,
            thematic_significance=antagonist.thematic_significance,
            first_appearance=antagonist.first_appearance,
            death=antagonist.death,
            status=antagonist.status,
        )

    def get_antagonist_summary(self, antagonist: Antagonist) -> str:
        """Get human-readable summary of antagonist.

        Args:
            antagonist: Character to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {antagonist.name} ===",
            f"反派类型: {antagonist.antagonist_type.value}",
            f"年龄: {antagonist.age or '未设定'}",
            f"威胁等级: {antagonist.threat_level or '未设定'}",
            "",
        ]

        if antagonist.description:
            lines.append(f"【描述】{antagonist.description}")

        if antagonist.presence:
            lines.append(f"【气场】{antagonist.presence}")

        if antagonist.first_impression:
            lines.append(f"【第一印象】{antagonist.first_impression}")

        app = antagonist.appearance
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

        pers = antagonist.personality
        if pers.personality_description:
            lines.extend(["", "【性格】"])
            lines.append(f"  {pers.personality_description}")
            if pers.core_traits:
                lines.append(f"  核心特点: {', '.join(pers.core_traits)}")
            if pers.mbti:
                lines.append(f"  MBTI: {pers.mbti}")
            if pers.moral_alignment:
                lines.append(f"  道德立场: {pers.moral_alignment}")

        bg = antagonist.background
        if antagonist.backstory:
            lines.extend(["", "【背景】"])
            lines.append(f"  {antagonist.backstory[:150]}...")
            if bg.origin:
                lines.append(f"  出身: {bg.origin}")

        mot = antagonist.motivation
        lines.extend(["", "【动机】"])
        if mot.surface_motivation:
            lines.append(f"  表面动机: {mot.surface_motivation}")
        if mot.deep_motivation:
            lines.append(f"  深层动机: {mot.deep_motivation}")
        if mot.justification:
            lines.append(f"  自我辩护: {mot.justification}")
        if mot.what_they_lost:
            lines.append(f"  失去的: {mot.what_they_lost}")

        rel = antagonist.relationship_to_protagonist
        if rel.relationship_type:
            lines.extend(["", "【与主角的对立】"])
            lines.append(f"  类型: {rel.relationship_type}")
            if rel.relationship_dynamics:
                lines.append(f"  互动: {rel.relationship_dynamics}")
            if rel.key_conflicts:
                lines.append(f"  冲突点: {', '.join(rel.key_conflicts[:2])}")
            if rel.mirrors_protagonist:
                lines.append(f"  镜像主角: 是")

        pwr = antagonist.power
        if pwr.power_source:
            lines.extend(["", "【力量】"])
            lines.append(f"  来源: {pwr.power_source}")
            lines.append(f"  类型: {pwr.power_type}")
            if pwr.combat_abilities:
                lines.append(f"  战斗: {', '.join(pwr.combat_abilities[:2])}")
            if pwr.special_abilities:
                lines.append(f"  特殊: {', '.join(pwr.special_abilities[:2])}")
            if pwr.weaknesses:
                lines.append(f"  弱点: {', '.join(pwr.weaknesses[:2])}")

        org = antagonist.organization
        if org.organization_name:
            lines.extend(["", "【组织】"])
            lines.append(f"  {org.organization_name}")
            lines.append(f"  类型: {org.organization_type}")
            if org.size:
                lines.append(f"  规模: {org.size}")

        if antagonist.vulnerability:
            lines.extend(["", "【弱点】"])
            lines.append(f"  {antagonist.vulnerability}")

        arc = antagonist.character_arc
        if arc.arc_type or arc.archetype:
            lines.extend(["", "【角色弧线】"])
            if arc.archetype:
                lines.append(f"  原型: {arc.archetype}")
            if arc.arc_type:
                lines.append(f"  类型: {arc.arc_type}")
            if arc.corruption_arc:
                lines.append(f"  堕落: {arc.corruption_arc[:80]}...")
            if arc.redemption_potential:
                lines.append(f"  救赎可能: {arc.redemption_potential}")

        if antagonist.catchphrases:
            lines.extend(["", "【标志性台词】"])
            lines.append(f"  {', '.join(antagonist.catchphrases[:2])}")

        if antagonist.narrative_function:
            lines.extend(["", "【叙事功能】"])
            lines.append(f"  {antagonist.narrative_function}")

        lines.extend(["", f"状态: {antagonist.status}"])
        if antagonist.first_appearance:
            lines.append(f"首次出场: {antagonist.first_appearance}")
        if antagonist.defeat_conditions:
            lines.append(f"击败条件: {', '.join(antagonist.defeat_conditions[:2])}")

        return "\n".join(lines)

    def export_antagonist(
        self,
        antagonist: Antagonist,
        include_profile: bool = True,
    ) -> dict[str, Any]:
        """Export antagonist as complete document.

        Args:
            antagonist: Character to export
            include_profile: Whether to include profile

        Returns:
            Complete export dict
        """
        export_data = {
            "antagonist": antagonist.model_dump(),
            "summary": self.get_antagonist_summary(antagonist),
        }

        if include_profile:
            export_data["profile"] = self.create_profile(antagonist).model_dump()

        return export_data

    def validate_antagonist(self, antagonist: Antagonist) -> dict[str, Any]:
        """Validate antagonist completeness.

        Args:
            antagonist: Character to validate

        Returns:
            Validation results
        """
        issues = []
        warnings = []
        suggestions = []

        if not antagonist.name:
            issues.append("角色缺少姓名")

        if not antagonist.backstory:
            warnings.append("角色缺少背景故事")

        if not antagonist.motivation.surface_motivation:
            warnings.append("缺少动机/目标设定")

        if not antagonist.motivation.deep_motivation:
            warnings.append("缺少深层心理动机设定")

        if not antagonist.relationship_to_protagonist.relationship_type:
            warnings.append("缺少与主角的对立关系设定")

        if not antagonist.power.power_source:
            warnings.append("缺少力量来源设定")

        if not antagonist.power.weaknesses:
            warnings.append("缺少弱点设定 - 每个强大反派都应该有可利用的弱点")

        if not antagonist.threat_level:
            suggestions.append("可以添加威胁等级来明确危险程度")

        if not antagonist.defeat_conditions:
            suggestions.append("可以添加击败条件来明确如何解决这个威胁")

        if not antagonist.vulnerability:
            suggestions.append("可以添加关键弱点/软肋来增加戏剧性")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "character_name": antagonist.name,
            "antagonist_type": antagonist.antagonist_type.value,
            "threat_level": antagonist.threat_level,
        }