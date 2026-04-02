"""Character growth arc engine for planning and managing character development."""

from typing import Optional, Any
from chai.models.character_growth_arc import (
    GrowthArcType,
    ArcStageType,
    GrowthMetricType,
    GrowthTrigger,
    GrowthObstacle,
    GrowthLesson,
    GrowthStage,
    GrowthArcProfile,
    CharacterGrowthArcSystem,
    GrowthArcAnalysis,
)
from chai.models import Character, MainCharacter, SupportingCharacter, Antagonist
from chai.services import AIService


class CharacterGrowthArcEngine:
    """Engine for generating and managing character growth arcs.

    Character growth arc planning is crucial for creating satisfying character
    development that feels authentic and drives the story forward.
    """

    def __init__(self, ai_service: AIService):
        """Initialize character growth arc engine with AI service."""
        self.ai_service = ai_service

    async def generate_growth_arc(
        self,
        character: Character,
        arc_type: GrowthArcType,
        genre: str,
        theme: str,
        total_chapters: int = 50,
        world_context: Optional[dict] = None,
    ) -> GrowthArcProfile:
        """Generate a comprehensive growth arc for a character.

        Args:
            character: The character to create an arc for
            arc_type: Type of growth arc (positive, negative, circular, etc.)
            genre: Novel genre
            theme: Central theme of the story
            total_chapters: Total chapters in the story
            world_context: Optional world context

        Returns:
            GrowthArcProfile with detailed arc stages
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        arc_type_descriptions = {
            GrowthArcType.POSITIVE: "正面成长弧 - 角色克服弱点、实现成长、达到目标",
            GrowthArcType.NEGATIVE: "负面堕落弧 - 角色因贪婪/恐惧等原因堕落或失败",
            GrowthArcType.FLAT: "平面弧 - 角色信念被考验但最终坚守",
            GrowthArcType.CIRCULAR: "圆形弧 - 角色经历起伏回到原点但有新的理解",
            GrowthArcType.FALL_AND_RISE: "跌落复兴弧 - 角色失败后重新站起",
            GrowthArcType.RISE_AND_FALL: "上升坠落弧 - 角色成功后因傲慢失败",
            GrowthArcType.TRANSFORMATION: "蜕变弧 - 角色完全转变为新的人",
            GrowthArcType.BOND: "羁绊弧 - 角色弧线聚焦于人际关系的建立/破裂",
            GrowthArcType.EDUCATION: "教育弧 - 角色通过学习获得成长",
        }

        prompt = f"""为{character.name}这个角色生成详细的成长弧线规划。

角色信息：
- 姓名：{character.name}
- 角色类型：{character.role}
- 性格描述：{character.personality_description[:200] if character.personality_description else '未设定'}
- 背景：{character.backstory[:200] if character.backstory else '未设定'}
- 动机：{character.motivation or '未设定'}
- 目标：{character.goal or '未设定'}
- 恐惧：{', '.join(character.fears) if character.fears else '未设定'}
- 欲望：{', '.join(character.desires) if character.desires else '未设定'}
- 弱点：{', '.join(character.weaknesses) if character.weaknesses else '未设定'}
- 优势：{', '.join(character.strengths) if character.strengths else '未设定'}
- 初始信念：{character.psychological_profile.get('core_belief', '未设定') if character.psychological_profile else '未设定'}

成长弧类型：{arc_type_descriptions.get(arc_type, '正面成长弧')}

类型：{genre}
主题：{theme}
总章节数：{total_chapters}章
{context}

请生成完整的角色成长弧规划，以JSON格式输出：

{{
  "character_id": "{character.id}",
  "character_name": "{character.name}",
  "arc_type": "{arc_type.value if hasattr(arc_type, 'value') else arc_type}",
  "arc_name": "弧线名称（如：从恐惧到勇气）",
  "arc_summary": "一句话弧线总结",
  "theme": "弧线主题",

  "starting_state": "起始状态描述（角色在故事开始时的状态）",
  "ending_state": "结束状态描述（角色在故事结束时的状态）",
  "starting_strengths": ["起始优势1", "优势2"],
  "starting_weaknesses": ["起始弱点1", "弱点2"],
  "ending_strengths": ["结束优势1", "优势2"],
  "ending_weaknesses": ["结束弱点1", "弱点2"],

  "core_wound": "核心创伤（驱动弧线的情感创伤）",
  "core_desire": "核心欲望（角色最深层的渴望）",
  "core_fear": "核心恐惧（角色最深的恐惧）",

  "initial_belief": "初始信念（角色开始时相信的谎言或错误观念）",
  "truth_learned": "学到的真理（弧线结束时学到的真相）",
  "belief_transformation": "信念转变过程",

  "stages": [
    {{
      "stage_type": "status_quo",
      "stage_name": "阶段名称",
      "description": "阶段描述",
      "chapter_range": "1-5",
      "trigger_event": "触发事件",
      "emotional_state": "情感状态",
      "mental_state": "心理状态",
      "lessons_learned": [
        {{
          "lesson_type": "lesson类型",
          "description": "学到的教训",
          "application": "如何应用",
          "integration_level": "融入程度"
        }}
      ],
      "new_abilities_or_insights": ["新能力/洞察1", "洞察2"],
      "perspective_shift": "视角转变",
      "behavioral_changes": ["行为变化1", "变化2"],
      "key_relationships_at_stage": ["关键关系1"],
      "relationship_developments": {{"关系名": "关系发展"}},
      "conflicts_faced": ["冲突1", "冲突2"],
      "internal_struggles": ["内心挣扎1", "挣扎2"],
      "growth_metrics": {{"skill": 0.1, "wisdom": 0.05}}
    }}
  ],
  "total_chapters": {total_chapters},

  "arc_triggers": [
    {{
      "trigger_type": "触发类型",
      "description": "触发描述",
      "source": "internal/external/relationship",
      "timing": "early/mid/late",
      "intensity": "low/medium/high/extreme",
      "impact": "影响描述"
    }}
  ],

  "obstacles": [
    {{
      "obstacle_type": "obstacle类型",
      "description": "障碍描述",
      "resistance": "如何抵抗成长",
      "overcome": false,
      "overcoming_method": "克服方法（如已克服）",
      "growth_from_overcoming": "从克服中学到（如已克服）"
    }}
  ],

  "key_moments": ["关键场景1", "关键场景2"],
  "turning_points": ["转折点1", "转折点2"],
  "key_relationship_arcs": {{"关系名": "关系如何发展"}},

  "primary_growth_metric": "growth_metric类型",
  "secondary_growth_metrics": ["secondary_metric1"],
  "growth_trajectory": [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0],

  "thematic_connections": ["主题连接1", "主题连接2"],
  "symbol_or_motif": "代表符号或意象"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)
        return self._build_growth_arc_profile(data)

    async def generate_character_arc_system(
        self,
        characters: list[Character],
        genre: str,
        theme: str,
        story_id: str = "",
        story_title: str = "",
        total_chapters: int = 50,
    ) -> CharacterGrowthArcSystem:
        """Generate growth arcs for all characters in a story.

        Args:
            characters: List of all characters
            genre: Novel genre
            theme: Central theme
            story_id: Story identifier
            story_title: Story title
            total_chapters: Total chapters

        Returns:
            CharacterGrowthArcSystem with all character arcs
        """
        arc_system = CharacterGrowthArcSystem(
            story_id=story_id,
            story_title=story_title,
            character_arcs=[],
            arc_interdependencies={},
            thematic_throughlines=[],
        )

        protagonist = None
        for char in characters:
            if char.role.value == "protagonist" if hasattr(char.role, 'value') else char.role == "protagonist":
                protagonist = char
                break

        protagonist_arc_type = GrowthArcType.POSITIVE
        if protagonist and protagonist.internal_conflict:
            if "贪婪" in protagonist.internal_conflict or "权力" in protagonist.motivation:
                protagonist_arc_type = GrowthArcType.RISE_AND_FALL
            elif "恐惧" in protagonist.internal_conflict:
                protagonist_arc_type = GrowthArcType.POSITIVE

        arc_type_map = {
            "protagonist": protagonist_arc_type,
            "antagonist": GrowthArcType.NEGATIVE,
            "supporting": GrowthArcType.CIRCULAR,
            "minor": GrowthArcType.FLAT,
            "mentor": GrowthArcType.EDUCATION,
            "love_interest": GrowthArcType.BOND,
            "sidekick": GrowthArcType.POSITIVE,
            "deuteragonist": GrowthArcType.FALL_AND_RISE,
        }

        for char in characters:
            role_key = char.role.value if hasattr(char.role, 'value') else char.role
            arc_type = arc_type_map.get(role_key, GrowthArcType.CIRCULAR)

            arc = await self.generate_growth_arc(
                character=char,
                arc_type=arc_type,
                genre=genre,
                theme=theme,
                total_chapters=total_chapters,
            )
            arc_system.character_arcs.append(arc)

            if role_key == "protagonist":
                arc_system.protagonist_arc_id = arc.character_id

        arc_type_counts: dict[str, int] = {}
        for arc in arc_system.character_arcs:
            arc_type_str = arc.arc_type.value if hasattr(arc.arc_type, 'value') else str(arc.arc_type)
            arc_type_counts[arc_type_str] = arc_type_counts.get(arc_type_str, 0) + 1
        arc_system.arc_type_distribution = arc_type_counts

        return arc_system

    async def analyze_arc_coherence(
        self,
        arc: GrowthArcProfile,
        all_arcs: Optional[list[GrowthArcProfile]] = None,
    ) -> GrowthArcAnalysis:
        """Analyze the coherence and quality of a character growth arc.

        Args:
            arc: The growth arc to analyze
            all_arcs: Other arcs in the story for context

        Returns:
            GrowthArcAnalysis with coherence assessment
        """
        arcs_context = ""
        if all_arcs:
            other_arcs = [f"- {a.character_name}: {a.arc_summary}" for a in all_arcs if a.character_id != arc.character_id]
            if other_arcs:
                arcs_context = "\n其他角色弧线：\n" + "\n".join(other_arcs[:5])

        prompt = f"""分析以下角色成长弧的质量和内在一致性：

角色：{arc.character_name}
弧线类型：{arc.arc_type.value if hasattr(arc.arc_type, 'value') else arc.arc_type}
弧线总结：{arc.arc_summary}
起始状态：{arc.starting_state}
结束状态：{arc.ending_state}
核心创伤：{arc.core_wound}
核心欲望：{arc.core_desire}
核心恐惧：{arc.core_fear}
初始信念：{arc.initial_belief}
学到的真理：{arc.truth_learned}

阶段数量：{len(arc.stages)}
关键转折点：{', '.join(arc.turning_points) if arc.turning_points else '未设定'}
{arcs_context}

请评估这个成长弧的以下方面（0.0-1.0评分）：
1. arc_coherence: 弧线内在一致性（各阶段是否逻辑连贯）
2. emotional_authenticity: 情感真实性（成长是否令人信服）
3. thematic_integration: 主题融合度（是否与故事主题紧密结合）
4. relationship_impact: 关系影响度（对角色关系的影响）
5. stakes_clarity: 赌注清晰度（成长的重要性是否清晰）

并分析：
- potential_issues: 潜在问题
- strengths: 优势
- recommendations: 改进建议

以JSON格式输出：
{{
  "character_id": "{arc.character_id}",
  "arc_coherence": 0.0-1.0评分,
  "growth_pacing": "too_fast/balanced/too_slow",
  "emotional_authenticity": 0.0-1.0评分,
  "thematic_integration": 0.0-1.0评分,
  "relationship_impact": 0.0-1.0评分,
  "stakes_clarity": 0.0-1.0评分,
  "potential_issues": ["问题1", "问题2"],
  "strengths": ["优势1", "优势2"],
  "recommendations": ["建议1", "建议2"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)
        return GrowthArcAnalysis(**data)

    async def expand_arc_stage(
        self,
        arc: GrowthArcProfile,
        stage_index: int,
    ) -> GrowthStage:
        """Expand a single arc stage with more detail.

        Args:
            arc: The growth arc containing the stage
            stage_index: Index of the stage to expand

        Returns:
            Expanded GrowthStage
        """
        if stage_index < 0 or stage_index >= len(arc.stages):
            raise ValueError(f"Invalid stage index: {stage_index}")

        stage = arc.stages[stage_index]

        prompt = f"""为角色{arc.character_name}的成长弧线中的以下阶段生成更详细的描述：

阶段名称：{stage.stage_name}
阶段类型：{stage.stage_type.value if hasattr(stage.stage_type, 'value') else stage.stage_type}
基础描述：{stage.description}
章节范围：{stage.chapter_range}
当前情感状态：{stage.emotional_state}

角色弧线信息：
- 弧线类型：{arc.arc_type.value if hasattr(arc.arc_type, 'value') else arc.arc_type}
- 核心创伤：{arc.core_wound}
- 核心欲望：{arc.core_desire}
- 初始信念：{arc.initial_belief}
- 学到的真理：{arc.truth_learned}

请扩展这个阶段，添加更多细节：
1. 更详细的场景描写
2. 角色的具体内心活动
3. 与其他角色的具体互动
4. 身体和情绪反应
5. 环境细节

以JSON格式输出扩展后的阶段信息：
{{
  "stage_type": "{stage.stage_type.value if hasattr(stage.stage_type, 'value') else stage.stage_type}",
  "stage_name": "阶段名称（可更新）",
  "description": "详细阶段描述（300字以上）",
  "chapter_range": "章节范围",
  "trigger_event": "详细触发事件",
  "emotional_state": "详细情感状态",
  "mental_state": "详细心理状态",
  "lessons_learned": [
    {{
      "lesson_type": "lesson类型",
      "description": "详细教训描述",
      "application": "应用方式",
      "integration_level": "融入程度"
    }}
  ],
  "new_abilities_or_insights": ["详细能力/洞察1", "洞察2"],
  "perspective_shift": "详细视角转变",
  "behavioral_changes": ["详细行为变化1", "变化2"],
  "key_relationships_at_stage": ["关键关系1"],
  "relationship_developments": {{"关系名": "详细关系发展"}},
  "conflicts_faced": ["详细冲突1", "冲突2"],
  "internal_struggles": ["详细内心挣扎1", "挣扎2"],
  "growth_metrics": {{"skill": 0.1, "wisdom": 0.05}}
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        lessons = []
        for l in data.get("lessons_learned", []):
            lessons.append(GrowthLesson(**l))

        return GrowthStage(
            stage_type=ArcStageType(data.get("stage_type", stage.stage_type.value if hasattr(stage.stage_type, 'value') else stage.stage_type)),
            stage_name=data.get("stage_name", stage.stage_name),
            description=data.get("description", stage.description),
            chapter_range=data.get("chapter_range", stage.chapter_range),
            trigger_event=data.get("trigger_event", stage.trigger_event),
            emotional_state=data.get("emotional_state", stage.emotional_state),
            mental_state=data.get("mental_state", stage.mental_state),
            lessons_learned=lessons,
            new_abilities_or_insights=data.get("new_abilities_or_insights", stage.new_abilities_or_insights),
            perspective_shift=data.get("perspective_shift", stage.perspective_shift),
            behavioral_changes=data.get("behavioral_changes", stage.behavioral_changes),
            key_relationships_at_stage=data.get("key_relationships_at_stage", stage.key_relationships_at_stage),
            relationship_developments=data.get("relationship_developments", stage.relationship_developments),
            conflicts_faced=data.get("conflicts_faced", stage.conflicts_faced),
            internal_struggles=data.get("internal_struggles", stage.internal_struggles),
            growth_metrics=data.get("growth_metrics", stage.growth_metrics),
        )

    async def create_arc_from_protagonist(
        self,
        protagonist: MainCharacter,
        genre: str,
        theme: str,
        total_chapters: int = 50,
    ) -> GrowthArcProfile:
        """Create a growth arc specifically designed for a protagonist.

        Args:
            protagonist: The main character
            genre: Novel genre
            theme: Central theme
            total_chapters: Total chapters

        Returns:
            GrowthArcProfile for the protagonist
        """
        character = Character(
            id=protagonist.id,
            name=protagonist.name,
            role=Character.Role.PROTAGONIST,
            personality_description=protagonist.personality_description or "",
            backstory=protagonist.background_detail.personality_description[:200] if protagonist.background_detail else "",
            motivation=protagonist.motivation_detail.surface_motivation if protagonist.motivation_detail else "",
            goal=protagonist.motivation_detail.deep_motivation if protagonist.motivation_detail else "",
            fears=protagonist.personality_dimension.fears if protagonist.personality_dimension else [],
            desires=[protagonist.motivation_detail.desire_core] if protagonist.motivation_detail else [],
            weaknesses=[],
            strengths=[],
            psychological_profile={},
        )

        arc_type = self._infer_arc_type_from_motivation(protagonist)

        return await self.generate_growth_arc(
            character=character,
            arc_type=arc_type,
            genre=genre,
            theme=theme,
            total_chapters=total_chapters,
        )

    async def create_arc_from_supporting_character(
        self,
        supporting_char: SupportingCharacter,
        genre: str,
        theme: str,
        total_chapters: int = 50,
    ) -> GrowthArcProfile:
        """Create a growth arc for a supporting character.

        Args:
            supporting_char: The supporting character
            genre: Novel genre
            theme: Central theme
            total_chapters: Total chapters

        Returns:
            GrowthArcProfile for the supporting character
        """
        role_type = supporting_char.role_type.value if hasattr(supporting_char.role_type, 'value') else supporting_char.role_type

        role_arc_map = {
            "mentor": GrowthArcType.EDUCATION,
            "sidekick": GrowthArcType.POSITIVE,
            "best_friend": GrowthArcType.BOND,
            "love_interest": GrowthArcType.BOND,
            "ally": GrowthArcType.POSITIVE,
            "contact": GrowthArcType.FLAT,
            "expert": GrowthArcType.EDUCATION,
            "comic_relief": GrowthArcType.CIRCULAR,
            "wisdom_keeper": GrowthArcType.EDUCATION,
            "foil": GrowthArcType.TRANSFORMATION,
            "fallen_ally": GrowthArcType.NEGATIVE,
            "retired_hero": GrowthArcType.FALL_AND_RISE,
            "mentee": GrowthArcType.POSITIVE,
            "informant": GrowthArcType.FLAT,
        }

        arc_type = role_arc_map.get(role_type, GrowthArcType.CIRCULAR)

        character = Character(
            id=supporting_char.id,
            name=supporting_char.name,
            role=Character.Role.SUPPORTING,
            personality_description=supporting_char.personality.personality_description[:200] if supporting_char.personality else "",
            backstory=supporting_char.background.backstory[:200] if supporting_char.background else "",
            motivation=supporting_char.motivation.motivation[:200] if supporting_char.motivation else "",
            fears=supporting_char.personality.fears[:3] if supporting_char.personality else [],
            desires=supporting_char.motivation.desires[:3] if supporting_char.motivation else [],
            internal_conflict=supporting_char.conflicts[0].description[:200] if supporting_char.conflicts else "",
        )

        return await self.generate_growth_arc(
            character=character,
            arc_type=arc_type,
            genre=genre,
            theme=theme,
            total_chapters=total_chapters,
        )

    async def create_arc_from_antagonist(
        self,
        antagonist: Antagonist,
        genre: str,
        theme: str,
        total_chapters: int = 50,
    ) -> GrowthArcProfile:
        """Create a growth arc for an antagonist.

        Args:
            antagonist: The antagonist character
            genre: Novel genre
            theme: Central theme
            total_chapters: Total chapters

        Returns:
            GrowthArcProfile for the antagonist
        """
        ant_type = antagonist.antagonist_type.value if hasattr(antagonist.antagonist_type, 'value') else antagonist.antagonist_type

        ant_arc_map = {
            "villain": GrowthArcType.NEGATIVE,
            "dark_hero": GrowthArcType.FALL_AND_RISE,
            "temporary_antagonist": GrowthArcType.CIRCULAR,
            "eternal_rival": GrowthArcType.FLAT,
            "tyrant": GrowthArcType.NEGATIVE,
            "manipulator": GrowthArcType.NEGATIVE,
            "revenge_seeker": GrowthArcType.RISE_AND_FALL,
            "corrupted": GrowthArcType.NEGATIVE,
            "ideological": GrowthArcType.TRANSFORMATION,
            "tragic_antagonist": GrowthArcType.FALL_AND_RISE,
            "minion": GrowthArcType.POSITIVE,
            "big_bad": GrowthArcType.NEGATIVE,
            "tempter": GrowthArcType.CIRCULAR,
            "shadow": GrowthArcType.TRANSFORMATION,
            "nemesis": GrowthArcType.FLAT,
        }

        arc_type = ant_arc_map.get(ant_type, GrowthArcType.NEGATIVE)

        character = Character(
            id=antagonist.id,
            name=antagonist.name,
            role=Character.Role.ANTAGONIST,
            personality_description=antagonist.personality.personality_description[:200] if antagonist.personality else "",
            backstory=antagonist.background.backstory[:200] if antagonist.background else "",
            motivation=antagonist.motivation.motivation[:200] if antagonist.motivation else "",
            fears=antagonist.personality.fears[:3] if antagonist.personality else [],
            desires=antagonist.motivation.desires[:3] if antagonist.motivation else [],
            internal_conflict=antagonist.conflicts[0].description[:200] if antagonist.conflicts else "",
        )

        return await self.generate_growth_arc(
            character=character,
            arc_type=arc_type,
            genre=genre,
            theme=theme,
            total_chapters=total_chapters,
        )

    def get_arc_summary(self, arc: GrowthArcProfile) -> str:
        """Get a human-readable summary of a character growth arc.

        Args:
            arc: The growth arc

        Returns:
            Summary string
        """
        arc_type_str = arc.arc_type.value if hasattr(arc.arc_type, 'value') else str(arc.arc_type)

        summary = f"""角色成长弧线概要：{arc.character_name}
=========================================

弧线名称：{arc.arc_name}
弧线类型：{arc_type_str}
弧线总结：{arc.arc_summary}

【起始状态】
{arc.starting_state}

【结束状态】
{arc.ending_state}

【核心要素】
- 核心创伤：{arc.core_wound}
- 核心欲望：{arc.core_desire}
- 核心恐惧：{arc.core_fear}

【信念转变】
初始信念（谎言）：{arc.initial_belief}
学到的真理：{arc.truth_learned}

【成长阶段】({len(arc.stages)}个阶段)
"""

        for i, stage in enumerate(arc.stages, 1):
            stage_type_str = stage.stage_type.value if hasattr(stage.stage_type, 'value') else stage.stage_type
            summary += f"\n  {i}. {stage.stage_name} ({stage_type_str})"
            summary += f"\n     章节：{stage.chapter_range}"
            summary += f"\n     情感状态：{stage.emotional_state}"
            if stage.lessons_learned:
                summary += f"\n     学到的教训：{len(stage.lessons_learned)}个"
            if stage.new_abilities_or_insights:
                summary += f"\n     新能力/洞察：{', '.join(stage.new_abilities_or_insights[:2])}"

        if arc.key_moments:
            summary += f"\n\n【关键场景】"
            for moment in arc.key_moments[:3]:
                summary += f"\n  - {moment}"

        return summary

    def _infer_arc_type_from_motivation(self, protagonist: MainCharacter) -> GrowthArcType:
        """Infer the appropriate arc type from protagonist motivation."""
        if not protagonist.motivation_detail:
            return GrowthArcType.POSITIVE

        motivation = protagonist.motivation_detail.surface_motivation.lower()
        deep_motivation = protagonist.motivation_detail.deep_motivation.lower() if protagonist.motivation_detail.deep_motivation else ""

        if "救赎" in motivation or "赎罪" in motivation:
            return GrowthArcType.FALL_AND_RISE
        elif "复仇" in motivation or "报复" in motivation:
            return GrowthArcType.RISE_AND_FALL
        elif "证明" in motivation or "认可" in motivation:
            return GrowthArcType.POSITIVE
        elif "失去" in motivation or "死亡" in motivation:
            return GrowthArcType.TRANSFORMATION
        elif "逃避" in motivation or "恐惧" in deep_motivation:
            return GrowthArcType.POSITIVE

        return GrowthArcType.POSITIVE

    def _build_growth_arc_profile(self, data: dict) -> GrowthArcProfile:
        """Build a GrowthArcProfile from parsed JSON data."""
        stages = []
        for s in data.get("stages", []):
            lessons = []
            for l in s.get("lessons_learned", []):
                lessons.append(GrowthLesson(**l))

            stages.append(GrowthStage(
                stage_type=ArcStageType(s.get("stage_type", "status_quo")),
                stage_name=s.get("stage_name", ""),
                description=s.get("description", ""),
                chapter_range=s.get("chapter_range", ""),
                trigger_event=s.get("trigger_event", ""),
                emotional_state=s.get("emotional_state", ""),
                mental_state=s.get("mental_state", ""),
                lessons_learned=lessons,
                new_abilities_or_insights=s.get("new_abilities_or_insights", []),
                perspective_shift=s.get("perspective_shift", ""),
                behavioral_changes=s.get("behavioral_changes", []),
                key_relationships_at_stage=s.get("key_relationships_at_stage", []),
                relationship_developments=s.get("relationship_developments", {}),
                conflicts_faced=s.get("conflicts_faced", []),
                internal_struggles=s.get("internal_struggles", []),
                growth_metrics=s.get("growth_metrics", {}),
            ))

        triggers = []
        for t in data.get("arc_triggers", []):
            triggers.append(GrowthTrigger(**t))

        obstacles = []
        for o in data.get("obstacles", []):
            obstacles.append(GrowthObstacle(**o))

        arc_type_val = data.get("arc_type", "positive")
        if hasattr(arc_type_val, 'value'):
            arc_type_val = arc_type_val.value
        if isinstance(arc_type_val, str):
            arc_type_val = GrowthArcType(arc_type_val)

        primary_metric_val = data.get("primary_growth_metric", "wisdom")
        if hasattr(primary_metric_val, 'value'):
            primary_metric_val = primary_metric_val.value
        if isinstance(primary_metric_val, str):
            try:
                primary_metric_val = GrowthMetricType(primary_metric_val)
            except ValueError:
                primary_metric_val = GrowthMetricType.WISDOM

        secondary_metrics = []
        for m in data.get("secondary_growth_metrics", []):
            if hasattr(m, 'value'):
                m = m.value
            try:
                secondary_metrics.append(GrowthMetricType(m))
            except ValueError:
                pass

        return GrowthArcProfile(
            character_id=data.get("character_id", ""),
            character_name=data.get("character_name", ""),
            arc_type=arc_type_val,
            arc_name=data.get("arc_name", ""),
            arc_summary=data.get("arc_summary", ""),
            theme=data.get("theme", ""),
            starting_state=data.get("starting_state", ""),
            ending_state=data.get("ending_state", ""),
            starting_strengths=data.get("starting_strengths", []),
            starting_weaknesses=data.get("starting_weaknesses", []),
            ending_strengths=data.get("ending_strengths", []),
            ending_weaknesses=data.get("ending_weaknesses", []),
            core_wound=data.get("core_wound", ""),
            core_desire=data.get("core_desire", ""),
            core_fear=data.get("core_fear", ""),
            stages=stages,
            total_chapters=data.get("total_chapters", 50),
            arc_triggers=triggers,
            obstacles=obstacles,
            key_moments=data.get("key_moments", []),
            turning_points=data.get("turning_points", []),
            key_relationship_arcs=data.get("key_relationship_arcs", {}),
            primary_growth_metric=primary_metric_val,
            secondary_growth_metrics=secondary_metrics,
            growth_trajectory=data.get("growth_trajectory", []),
            initial_belief=data.get("initial_belief", ""),
            truth_learned=data.get("truth_learned", ""),
            belief_transformation=data.get("belief_transformation", ""),
            thematic_connections=data.get("thematic_connections", []),
            symbol_or_motif=data.get("symbol_or_motif", ""),
        )

    def export_arc_system(self, arc_system: CharacterGrowthArcSystem) -> dict:
        """Export arc system to a dictionary.

        Args:
            arc_system: The arc system to export

        Returns:
            Dictionary representation
        """
        arcs = []
        for arc in arc_system.character_arcs:
            arc_dict = {
                "character_id": arc.character_id,
                "character_name": arc.character_name,
                "arc_type": arc.arc_type.value if hasattr(arc.arc_type, 'value') else arc.arc_type,
                "arc_name": arc.arc_name,
                "arc_summary": arc.arc_summary,
                "theme": arc.theme,
                "stages": [
                    {
                        "stage_type": s.stage_type.value if hasattr(s.stage_type, 'value') else s.stage_type,
                        "stage_name": s.stage_name,
                        "description": s.description,
                        "chapter_range": s.chapter_range,
                        "emotional_state": s.emotional_state,
                    }
                    for s in arc.stages
                ],
            }
            arcs.append(arc_dict)

        return {
            "story_id": arc_system.story_id,
            "story_title": arc_system.story_title,
            "character_arcs": arcs,
            "arc_type_distribution": arc_system.arc_type_distribution,
            "protagonist_arc_id": arc_system.protagonist_arc_id,
        }
