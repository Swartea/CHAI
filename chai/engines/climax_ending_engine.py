"""Climax and ending engine for powerful story conclusions."""

from datetime import datetime
from typing import Optional
import uuid

from chai.models.climax_ending import (
    ClimaxType,
    ClimaxIntensity,
    ClimaxStatus,
    ClimaxElement,
    ClimaxStructure,
    ClimaxDesign,
    EndingType,
    EndingStatus,
    EndingElement,
    EndingStructure,
    EndingDesign,
    ClimaxEndingConnection,
    ClimaxEndingSystem,
    ClimaxAnalysis,
    EndingAnalysis,
    ClimaxEndingAnalysis,
)
from chai.models.main_story_structure import MainStoryStructure, StoryBeat, StoryBeatType
from chai.models.story_outline import StoryOutline, PlotThread
from chai.models.character_growth_arc import CharacterGrowthArcSystem, GrowthArcProfile
from chai.models.subplot_foreshadowing import SubplotForeshadowingDesign
from chai.services import AIService


# Climax templates by type
CLIMAX_TEMPLATES = {
    ClimaxType.FINAL_CLIMAX: {
        "name": "终极对决",
        "typical_elements": ["buildup", "confrontation", "peak", "resolution"],
        "tension_curve": [0.7, 0.85, 1.0, 0.6],
    },
    ClimaxType.EMOTIONAL_CLIMAX: {
        "name": "情感高潮",
        "typical_elements": ["revelation", "emotional_release", "catharsis", "resolution"],
        "tension_curve": [0.6, 0.8, 1.0, 0.4],
    },
    ClimaxType.COMBAT_CLIMAX: {
        "name": "战斗高潮",
        "typical_elements": ["strategy", "battle", "turning_point", "victory_defeat"],
        "tension_curve": [0.75, 0.9, 1.0, 0.5],
    },
    ClimaxType.SACRIFICE_CLIMAX: {
        "name": "牺牲高潮",
        "typical_elements": ["decision", "sacrifice", "aftermath", "legacy"],
        "tension_curve": [0.7, 0.85, 1.0, 0.35],
    },
    ClimaxType.REVELATION_CLIMAX: {
        "name": "揭示高潮",
        "typical_elements": ["tension_build", "revelation", "repercussions", "new_status"],
        "tension_curve": [0.65, 0.85, 1.0, 0.55],
    },
    ClimaxType.DECISION_CLIMAX: {
        "name": "抉择高潮",
        "typical_elements": ["dilemma", "internal_conflict", "choice", "consequences"],
        "tension_curve": [0.7, 0.9, 1.0, 0.45],
    },
    ClimaxType.TRANSFORMATION_CLIMAX: {
        "name": "蜕变高潮",
        "typical_elements": ["crisis", "transformation", "new_identity", "acceptance"],
        "tension_curve": [0.7, 0.85, 1.0, 0.5],
    },
    ClimaxType.SUB_CLIMAX: {
        "name": "次级高潮",
        "typical_elements": ["conflict", "peak", "resolution"],
        "tension_curve": [0.5, 0.75, 0.85, 0.4],
    },
}


# Ending templates by type
ENDING_TEMPLATES = {
    EndingType.CLEAN_RESOLUTION: {
        "name": "完美结局",
        "description": "所有冲突得到解决",
        "typical_elements": ["victory", "celebration", "new_beginning"],
    },
    EndingType.BITTERSWEET: {
        "name": "苦乐参半",
        "description": "有些遗憾但整体积极",
        "typical_elements": ["triumph", "loss", "hope"],
    },
    EndingType.TRAGIC: {
        "name": "悲剧结局",
        "description": "主角失败或死亡",
        "typical_elements": ["defeat", "sacrifice", "death", "legacy"],
    },
    EndingType.OPEN_ENDED: {
        "name": "开放结局",
        "description": "留下想象空间",
        "typical_elements": ["conclusion", "question", "possibility"],
    },
    EndingType.CIRCULAR: {
        "name": "环形结局",
        "description": "首尾呼应",
        "typical_elements": ["return", "reflection", "completion"],
    },
    EndingType.TWIST_ENDING: {
        "name": "反转结局",
        "description": "意想不到的转折",
        "typical_elements": ["apparent_resolution", "twist", "recontextualization"],
    },
    EndingType.TRIUMPHANT: {
        "name": "胜利结局",
        "description": "英雄获得最终胜利",
        "typical_elements": ["final_battle", "victory", "reward", "new_order"],
    },
    EndingType.PYRRHIC_VICTORY: {
        "name": "皮洛士式胜利",
        "description": "代价惨重的胜利",
        "typical_elements": ["victory", "heavy_cost", "ambiguous_future"],
    },
    EndingType.REDEMPTIVE: {
        "name": "救赎结局",
        "description": "通过牺牲获得救赎",
        "typical_elements": ["sacrifice", "forgiveness", "peace", "legacy"],
    },
    EndingType.CLEANSED: {
        "name": "净化结局",
        "description": "邪恶被彻底消灭",
        "typical_elements": ["final_defeat", "purification", "restoration", "renewal"],
    },
}


class ClimaxEndingEngine:
    """Engine for designing climaxes and endings."""

    def __init__(self, ai_service: AIService):
        """Initialize climax and ending engine with AI service."""
        self.ai_service = ai_service

    async def generate_climax_design(
        self,
        story_id: str,
        genre: str,
        theme: str,
        climax_type: ClimaxType,
        main_structure: Optional[MainStoryStructure] = None,
        story_outline: Optional[StoryOutline] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
        target_chapters: int = 24,
    ) -> ClimaxDesign:
        """Generate a climax design.

        Args:
            story_id: Story identifier
            genre: Story genre
            theme: Central theme
            climax_type: Type of climax
            main_structure: Optional main story structure
            story_outline: Optional story outline
            growth_arcs: Optional character growth arcs
            subplot_design: Optional subplot design
            target_chapters: Target number of chapters

        Returns:
            ClimaxDesign object
        """
        design_id = f"climax_{uuid.uuid4().hex[:8]}"

        # Get climax structure from template or AI
        template = CLIMAX_TEMPLATES.get(climax_type, CLIMAX_TEMPLATES[ClimaxType.FINAL_CLIMAX])

        # Determine climax chapter (typically late in story)
        climax_chapter = self._calculate_climax_chapter(target_chapters, climax_type)

        # Generate climax structure
        climax_structure = await self._generate_climax_structure(
            climax_id=design_id,
            climax_type=climax_type,
            template=template,
            climax_chapter=climax_chapter,
            genre=genre,
            theme=theme,
            main_structure=main_structure,
            growth_arcs=growth_arcs,
            subplot_design=subplot_design,
        )

        # Generate sub-climaxes if needed
        sub_climaxes = await self._generate_sub_climaxes(
            story_id=story_id,
            main_climax=climax_structure,
            climax_chapter=climax_chapter,
            target_chapters=target_chapters,
            genre=genre,
            theme=theme,
        )

        design = ClimaxDesign(
            id=design_id,
            story_id=story_id,
            main_climax=climax_structure,
            sub_climaxes=sub_climaxes,
            climax_chapter=climax_chapter,
            climax_duration_chapters=self._calculate_climax_duration(climax_type),
            story_beat_ids=self._extract_story_beat_ids(main_structure),
            character_arc_ids=self._extract_arc_ids(growth_arcs),
            plot_thread_ids=self._extract_thread_ids(story_outline),
            status=ClimaxStatus.DEVELOPED,
        )

        return design

    async def _generate_climax_structure(
        self,
        climax_id: str,
        climax_type: ClimaxType,
        template: dict,
        climax_chapter: int,
        genre: str,
        theme: str,
        main_structure: Optional[MainStoryStructure],
        growth_arcs: Optional[CharacterGrowthArcSystem],
        subplot_design: Optional[SubplotForeshadowingDesign],
    ) -> ClimaxStructure:
        """Generate climax structure."""
        # Build elements
        elements = []
        element_types = template.get("typical_elements", ["buildup", "peak", "resolution"])

        for i, element_type in enumerate(element_types):
            element_id = f"{climax_id}_elem_{i}"
            element = ClimaxElement(
                id=element_id,
                name=self._get_element_name(element_type),
                description=f"{element_type} description",
                element_type=element_type,
                chapter=climax_chapter,
                sequence_order=i,
                tension_level=ClimaxIntensity.HIGH if i == len(element_types) - 1 else ClimaxIntensity.MODERATE,
            )
            elements.append(element)

        # Peak moment is typically the last element or the middle one
        peak_index = len(elements) - 1 if elements else 0
        peak_moment = elements[peak_index].name if elements else "Peak moment"

        structure = ClimaxStructure(
            id=climax_id,
            climax_type=climax_type,
            name=template.get("name", "高潮"),
            buildup_chapters=list(range(max(1, climax_chapter - 3), climax_chapter)),
            trigger_event="主要冲突的终极对决",
            elements=elements,
            peak_moment=peak_moment,
            peak_chapter=climax_chapter,
            immediate_resolution="冲突暂时平息",
            consequences=["主要冲突升级", "角色命运改变"],
            world_changes=["世界状态改变"],
            emotional_impact="强烈的情感冲击",
            catharsis_level=0.8,
        )

        return structure

    async def _generate_sub_climaxes(
        self,
        story_id: str,
        main_climax: ClimaxStructure,
        climax_chapter: int,
        target_chapters: int,
        genre: str,
        theme: str,
    ) -> list[ClimaxStructure]:
        """Generate sub-climaxes for major plot threads."""
        sub_climaxes = []

        # Typically 1-2 sub-climaxes for complex stories
        num_sub = min(2, max(0, (target_chapters // 10) - 1))

        for i in range(num_sub):
            sub_id = f"{story_id}_subclimax_{i}"
            sub_chapter = climax_chapter - (i + 1) * 3

            if sub_chapter > 0:
                sub_structure = ClimaxStructure(
                    id=sub_id,
                    climax_type=ClimaxType.SUB_CLIMAX,
                    name=f"次级高潮 {i + 1}",
                    buildup_chapters=[sub_chapter - 1],
                    trigger_event=f"支线冲突{i + 1}爆发",
                    elements=[],
                    peak_moment=f"支线高潮{i + 1}",
                    peak_chapter=sub_chapter,
                    immediate_resolution="支线冲突解决",
                    consequences=[f"支线{i + 1}结局"],
                    emotional_impact="中等情感冲击",
                    catharsis_level=0.5,
                )
                sub_climaxes.append(sub_structure)

        return sub_climaxes

    def _calculate_climax_chapter(self, target_chapters: int, climax_type: ClimaxType) -> int:
        """Calculate appropriate chapter for climax."""
        # Final climax typically around 85-90% through the story
        if climax_type == ClimaxType.FINAL_CLIMAX:
            return int(target_chapters * 0.88)
        elif climax_type == ClimaxType.SUB_CLIMAX:
            return int(target_chapters * 0.7)
        else:
            return int(target_chapters * 0.85)

    def _calculate_climax_duration(self, climax_type: ClimaxType) -> int:
        """Calculate how many chapters the climax spans."""
        durations = {
            ClimaxType.FINAL_CLIMAX: 2,
            ClimaxType.COMBAT_CLIMAX: 2,
            ClimaxType.EMOTIONAL_CLIMAX: 1,
            ClimaxType.SUB_CLIMAX: 1,
        }
        return durations.get(climax_type, 1)

    def _get_element_name(self, element_type: str) -> str:
        """Get localized element name."""
        names = {
            "buildup": "张力积累",
            "confrontation": "正面对决",
            "peak": "巅峰时刻",
            "resolution": "结果揭晓",
            "revelation": "真相揭露",
            "emotional_release": "情感宣泄",
            "catharsis": "情感释放",
            "battle": "激战",
            "turning_point": "转折点",
            "victory_defeat": "胜负揭晓",
            "decision": "艰难抉择",
            "sacrifice": "牺牲时刻",
            "aftermath": "余波",
            "legacy": "遗产传承",
            "tension_build": "紧张升级",
            "repercussions": "连锁反应",
            "new_status": "新格局",
            "internal_conflict": "内心挣扎",
            "choice": "最终选择",
            "consequences": "后果展现",
            "crisis": "危机时刻",
            "transformation": "蜕变",
            "new_identity": "新身份",
            "acceptance": "接受",
            "conflict": "冲突爆发",
        }
        return names.get(element_type, element_type)

    def _extract_story_beat_ids(self, main_structure: Optional[MainStoryStructure]) -> list[str]:
        """Extract story beat IDs from structure."""
        if not main_structure:
            return []
        return [beat.id for beat in main_structure.beats]

    def _extract_arc_ids(self, growth_arcs: Optional[CharacterGrowthArcSystem]) -> list[str]:
        """Extract character arc IDs from system."""
        if not growth_arcs:
            return []
        return [arc.id for arc in growth_arcs.arcs]

    def _extract_thread_ids(self, story_outline: Optional[StoryOutline]) -> list[str]:
        """Extract plot thread IDs from outline."""
        if not story_outline:
            return []
        return [thread.id for thread in story_outline.plot_threads]

    async def generate_ending_design(
        self,
        story_id: str,
        genre: str,
        theme: str,
        ending_type: EndingType,
        climax_design: Optional[ClimaxDesign] = None,
        main_structure: Optional[MainStoryStructure] = None,
        story_outline: Optional[StoryOutline] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
        target_chapters: int = 24,
    ) -> EndingDesign:
        """Generate an ending design.

        Args:
            story_id: Story identifier
            genre: Story genre
            theme: Central theme
            ending_type: Type of ending
            climax_design: Optional associated climax design
            main_structure: Optional main story structure
            story_outline: Optional story outline
            growth_arcs: Optional character growth arcs
            target_chapters: Target number of chapters

        Returns:
            EndingDesign object
        """
        design_id = f"ending_{uuid.uuid4().hex[:8]}"

        # Get ending template
        template = ENDING_TEMPLATES.get(ending_type, ENDING_TEMPLATES[EndingType.CLEAN_RESOLUTION])

        # Determine ending chapter
        climax_chapter = climax_design.climax_chapter if climax_design else int(target_chapters * 0.88)
        ending_chapter = climax_chapter + climax_design.climax_duration_chapters if climax_design else target_chapters - 2

        # Generate ending structure
        ending_structure = await self._generate_ending_structure(
            ending_id=design_id,
            ending_type=ending_type,
            template=template,
            ending_chapter=ending_chapter,
            genre=genre,
            theme=theme,
            story_outline=story_outline,
            growth_arcs=growth_arcs,
        )

        design = EndingDesign(
            id=design_id,
            story_id=story_id,
            ending=ending_structure,
            ending_chapter=ending_chapter,
            epilogue_chapters=1 if ending_type in [EndingType.OPEN_ENDED, EndingType.CIRCULAR] else 0,
            climax_id=climax_design.id if climax_design else "",
            character_arc_ids=self._extract_arc_ids(growth_arcs),
            theme_resolution=f"主题'{theme}'在结局得到升华",
            thematic_statement=f"通过故事传达关于{theme}的深刻思考",
            main_question_answered="故事的核心问题在结局得到回答",
            closure_level=self._calculate_closure_level(ending_type),
            status=EndingStatus.DEVELOPED,
        )

        return design

    async def _generate_ending_structure(
        self,
        ending_id: str,
        ending_type: EndingType,
        template: dict,
        ending_chapter: int,
        genre: str,
        theme: str,
        story_outline: Optional[StoryOutline],
        growth_arcs: Optional[CharacterGrowthArcSystem],
    ) -> EndingStructure:
        """Generate ending structure."""
        # Build elements
        elements = []
        element_types = template.get("typical_elements", ["conclusion"])

        for i, element_type in enumerate(element_types):
            element_id = f"{ending_id}_elem_{i}"
            element = EndingElement(
                id=element_id,
                name=self._get_ending_element_name(element_type),
                description=f"{element_type} description",
                element_type=element_type,
                chapter=ending_chapter,
                sequence_order=i,
                purpose=f"传达{element_type}效果",
                emotional_effect=self._get_emotional_effect(element_type),
            )
            elements.append(element)

        # Resolve threads
        resolved_threads = []
        unresolved_threads = []

        if story_outline:
            for thread in story_outline.plot_threads:
                if thread.status.value in ["resolved", "complete"]:
                    resolved_threads.append(thread.id)
                else:
                    unresolved_threads.append(thread.id)

        # Determine final elements
        final_image = self._get_final_image(ending_type)
        final_line = self._get_final_line(ending_type)

        structure = EndingStructure(
            id=ending_id,
            ending_type=ending_type,
            name=template.get("name", "结局"),
            resolved_threads=resolved_threads,
            unresolved_threads=unresolved_threads if ending_type == EndingType.OPEN_ENDED else [],
            elements=elements,
            final_image=final_image,
            final_line=final_line,
            closing_symbol="首尾呼应的象征",
            emotional_tone=template.get("description", ""),
            reader_emotional_journey=["期待", "紧张", "满足", "回味"],
            character_fates={},
            world_state="世界恢复到新的平衡状态",
        )

        return structure

    def _get_ending_element_name(self, element_type: str) -> str:
        """Get localized ending element name."""
        names = {
            "victory": "胜利宣告",
            "celebration": "庆典",
            "new_beginning": "新的开始",
            "triumph": "凯旋",
            "loss": "失落",
            "hope": "希望",
            "defeat": "失败",
            "sacrifice": "牺牲",
            "death": "逝去",
            "legacy": "传承",
            "conclusion": "尾声",
            "question": "疑问",
            "possibility": "可能性",
            "return": "回归",
            "reflection": "反思",
            "completion": "完结",
            "apparent_resolution": "表面解决",
            "twist": "反转",
            "recontextualization": "重新诠释",
            "final_battle": "最终之战",
            "reward": "奖赏",
            "new_order": "新秩序",
            "heavy_cost": "沉重代价",
            "ambiguous_future": "不确定的未来",
            "forgiveness": "宽恕",
            "peace": "宁静",
            "final_defeat": "彻底击败",
            "purification": "净化",
            "restoration": "恢复",
            "renewal": "新生",
        }
        return names.get(element_type, element_type)

    def _get_emotional_effect(self, element_type: str) -> str:
        """Get emotional effect description."""
        effects = {
            "victory": "喜悦与满足",
            "celebration": "欢乐与释然",
            "new_beginning": "希望与期待",
            "triumph": "自豪与满足",
            "loss": "悲伤与感慨",
            "hope": "温暖与期待",
            "defeat": "沉重与惋惜",
            "sacrifice": "悲壮与敬仰",
            "death": "哀伤与沉思",
            "legacy": "感慨与敬意",
            "conclusion": "完整与满足",
            "question": "好奇与思索",
            "possibility": "期待与想象",
            "return": "圆满与回归",
            "reflection": "沉思与回味",
            "completion": "圆满与释然",
            "twist": "震惊与重新思考",
            "recontextualization": "恍然大悟",
            "new_order": "安心与期待",
        }
        return effects.get(element_type, "情感共鸣")

    def _get_final_image(self, ending_type: EndingType) -> str:
        """Get appropriate final image for ending type."""
        images = {
            EndingType.CLEAN_RESOLUTION: "朝阳下的新世界",
            EndingType.BITTERSWEET: "夕阳中的孤独身影",
            EndingType.TRAGIC: "消散的余晖",
            EndingType.OPEN_ENDED: "道路延伸向远方",
            EndingType.CIRCULAR: "回到原点",
            EndingType.TWIST_ENDING: "镜子中的另一面",
            EndingType.TRIUMPHANT: "站在巅峰俯瞰世界",
            EndingType.PYRRHIC_VICTORY: "废墟上的幸存者",
            EndingType.REDEMPTIVE: "升向光明的灵魂",
            EndingType.CLEANSED: "净化后的清明世界",
        }
        return images.get(ending_type, "结局画面")

    def _get_final_line(self, ending_type: EndingType) -> str:
        """Get appropriate final line for ending type."""
        lines = {
            EndingType.CLEAN_RESOLUTION: "故事至此结束，但生活仍在继续。",
            EndingType.BITTERSWEET: "有些遗憾，但这就是人生。",
            EndingType.TRAGIC: "一切都结束了。",
            EndingType.OPEN_ENDED: "故事未完待续……",
            EndingType.CIRCULAR: "一切从这里开始，也在这里结束。",
            EndingType.TWIST_ENDING: "原来如此……",
            EndingType.TRIUMPHANT: "我们赢了！",
            EndingType.PYRRHIC_VICTORY: "值得吗？这个问题没有答案。",
            EndingType.REDEMPTIVE: "愿一切归于安宁。",
            EndingType.CLEANSED: "黑暗已逝，光明永存。",
        }
        return lines.get(ending_type, "")

    def _calculate_closure_level(self, ending_type: EndingType) -> float:
        """Calculate closure level based on ending type."""
        closure_levels = {
            EndingType.CLEAN_RESOLUTION: 1.0,
            EndingType.BITTERSWEET: 0.8,
            EndingType.TRAGIC: 0.85,
            EndingType.OPEN_ENDED: 0.4,
            EndingType.CIRCULAR: 0.9,
            EndingType.TWIST_ENDING: 0.7,
            EndingType.TRIUMPHANT: 0.95,
            EndingType.PYRRHIC_VICTORY: 0.6,
            EndingType.REDEMPTIVE: 0.9,
            EndingType.CLEANSED: 0.95,
        }
        return closure_levels.get(ending_type, 0.8)

    async def generate_complete_design(
        self,
        story_id: str,
        genre: str,
        theme: str,
        climax_type: ClimaxType,
        ending_type: EndingType,
        main_structure: Optional[MainStoryStructure] = None,
        story_outline: Optional[StoryOutline] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
        target_chapters: int = 24,
    ) -> ClimaxEndingSystem:
        """Generate a complete climax and ending system.

        Args:
            story_id: Story identifier
            genre: Story genre
            theme: Central theme
            climax_type: Type of climax
            ending_type: Type of ending
            main_structure: Optional main story structure
            story_outline: Optional story outline
            growth_arcs: Optional character growth arcs
            subplot_design: Optional subplot design
            target_chapters: Target number of chapters

        Returns:
            ClimaxEndingSystem object
        """
        system_id = f"climax_ending_{uuid.uuid4().hex[:8]}"

        # Generate climax design
        climax_design = await self.generate_climax_design(
            story_id=story_id,
            genre=genre,
            theme=theme,
            climax_type=climax_type,
            main_structure=main_structure,
            story_outline=story_outline,
            growth_arcs=growth_arcs,
            subplot_design=subplot_design,
            target_chapters=target_chapters,
        )

        # Generate ending design
        ending_design = await self.generate_ending_design(
            story_id=story_id,
            genre=genre,
            theme=theme,
            ending_type=ending_type,
            climax_design=climax_design,
            main_structure=main_structure,
            story_outline=story_outline,
            growth_arcs=growth_arcs,
            target_chapters=target_chapters,
        )

        # Create connection
        connection = ClimaxEndingConnection(
            id=f"{system_id}_conn",
            climax_id=climax_design.id,
            ending_id=ending_design.id,
            transition_chapters=climax_design.climax_duration_chapters,
            transition_nature="从高潮到结局的平稳过渡",
            emotional_flow="从激昂到平静的情感流动",
            plot_continuity="情节连贯，逻辑自洽",
            climax_weight=0.6,
        )

        system = ClimaxEndingSystem(
            id=system_id,
            story_id=story_id,
            climax_design=climax_design,
            ending_design=ending_design,
            connection=connection,
            main_structure_id=main_structure.id if main_structure else None,
            story_outline_id=story_outline.id if story_outline else None,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        return system

    async def analyze_climax(
        self,
        climax_design: ClimaxDesign,
    ) -> ClimaxAnalysis:
        """Analyze climax design quality.

        Args:
            climax_design: Climax design to analyze

        Returns:
            ClimaxAnalysis object
        """
        issues = []
        recommendations = []

        # Check structural integrity
        elements = climax_design.main_climax.elements
        structural_integrity = 0.5 if len(elements) < 2 else 0.8 if len(elements) < 4 else 0.95

        # Check element balance
        element_balance = 0.7 if elements else 0.0

        # Check emotional impact
        emotional_peak = climax_design.main_climax.catharsis_level

        # Check tension curve
        tension_curve_quality = 0.75

        # Check plot thread resolution
        plot_resolution = min(1.0, len(climax_design.plot_thread_ids) / 5) if climax_design.plot_thread_ids else 0.5

        # Check character arc resolution
        arc_resolution = min(1.0, len(climax_design.character_arc_ids) / 3) if climax_design.character_arc_ids else 0.5

        # Identify issues
        if structural_integrity < 0.7:
            issues.append("高潮结构完整性不足")

        if emotional_peak < 0.6:
            issues.append("情感冲击强度不足")

        if len(elements) < 3:
            issues.append("高潮元素数量偏少")

        # Generate recommendations
        if structural_integrity < 0.7:
            recommendations.append("增加高潮元素数量以提升结构性")

        if emotional_peak < 0.6:
            recommendations.append("加强情感冲击设计")

        if plot_resolution < 0.7:
            recommendations.append("确保更多情节线在高潮得到解决")

        analysis = ClimaxAnalysis(
            design_id=climax_design.id,
            structural_integrity=structural_integrity,
            element_balance=element_balance,
            emotional_peak_effectiveness=emotional_peak,
            tension_curve_quality=tension_curve_quality,
            plot_thread_resolution=plot_resolution,
            character_arc_resolution=arc_resolution,
            identified_issues=issues,
            recommendations=recommendations,
        )

        return analysis

    async def analyze_ending(
        self,
        ending_design: EndingDesign,
    ) -> EndingAnalysis:
        """Analyze ending design quality.

        Args:
            ending_design: Ending design to analyze

        Returns:
            EndingAnalysis object
        """
        issues = []
        recommendations = []

        # Check closure quality
        closure_quality = ending_design.closure_level

        # Check thread resolution
        resolved = len(ending_design.ending.resolved_threads)
        unresolved = len(ending_design.ending.unresolved_threads)
        thread_resolution = resolved / (resolved + unresolved + 1)

        # Check emotional satisfaction
        emotional_satisfaction = 0.7 + (closure_quality * 0.3)

        # Check thematic resolution
        thematic_resolution = 0.8 if ending_design.theme_resolution else 0.5

        # Check character fate satisfaction
        fate_count = len(ending_design.ending.character_fates)
        fate_satisfaction = min(1.0, fate_count / 5)

        # Identify issues
        if closure_quality < 0.6:
            issues.append("结局闭合度不足")

        if unresolved > resolved and ending_design.ending.unresolved_threads:
            issues.append("未解之情节线过多")

        if fate_count < 3:
            issues.append("角色命运交代不足")

        # Generate recommendations
        if closure_quality < 0.6:
            recommendations.append("增加结局的闭合感")

        if fate_count < 3:
            recommendations.append("补充更多角色的最终命运")

        analysis = EndingAnalysis(
            design_id=ending_design.id,
            closure_quality=closure_quality,
            thread_resolution_quality=thread_resolution,
            emotional_satisfaction=emotional_satisfaction,
            thematic_resolution_quality=thematic_resolution,
            character_fate_satisfaction=fate_satisfaction,
            identified_issues=issues,
            recommendations=recommendations,
        )

        return analysis

    async def analyze_climax_ending_system(
        self,
        system: ClimaxEndingSystem,
    ) -> ClimaxEndingAnalysis:
        """Analyze complete climax and ending system.

        Args:
            system: Climax ending system to analyze

        Returns:
            ClimaxEndingAnalysis object
        """
        # Analyze components
        climax_analysis = await self.analyze_climax(system.climax_design)
        ending_analysis = await self.analyze_ending(system.ending_design)

        # Analyze connection
        transition_quality = 0.7 if system.connection.transition_chapters <= 3 else 0.6
        emotional_flow_quality = 0.75
        narrative_coherence = (climax_analysis.structural_integrity + ending_analysis.closure_quality) / 2

        # Overall quality
        overall = (
            climax_analysis.emotional_peak_effectiveness * 0.35 +
            ending_analysis.emotional_satisfaction * 0.25 +
            transition_quality * 0.2 +
            narrative_coherence * 0.2
        )

        # Combine issues
        all_issues = climax_analysis.identified_issues + ending_analysis.identified_issues
        all_recommendations = climax_analysis.recommendations + ending_analysis.recommendations

        # Add connection-specific issues
        if system.connection.transition_chapters > 3:
            all_issues.append("高潮到结局的过渡过长")

        if system.connection.climax_weight < 0.4 or system.connection.climax_weight > 0.8:
            all_recommendations.append("调整高潮与结局的比重平衡")

        analysis = ClimaxEndingAnalysis(
            system_id=system.id,
            climax_analysis=climax_analysis,
            ending_analysis=ending_analysis,
            transition_quality=transition_quality,
            emotional_flow_quality=emotional_flow_quality,
            narrative_coherence=narrative_coherence,
            overall_quality_score=overall,
            identified_issues=all_issues,
            recommendations=all_recommendations,
        )

        return analysis

    def get_system_summary(self, system: ClimaxEndingSystem) -> str:
        """Get human-readable summary of climax and ending system.

        Args:
            system: Climax ending system

        Returns:
            Summary string
        """
        climax = system.climax_design
        ending = system.ending_design

        summary = f"""高潮与结局设计
================

高潮设计:
- 类型: {climax.main_climax.name}
- 位置: 第{climax.climax_chapter}章
- 时长: {climax.climax_duration_chapters}章
- 峰值时刻: {climax.main_climax.peak_moment}
- 情感冲击: {climax.main_climax.emotional_impact}
- 次级高潮: {len(climax.sub_climaxes)}个

结局设计:
- 类型: {ending.ending.name}
- 位置: 第{ending.ending_chapter}章
- 闭合度: {int(ending.closure_level * 100)}%
- 主题呈现: {ending.thematic_statement}
- 最终画面: {ending.ending.final_image}

连接设计:
- 过渡时长: {system.connection.transition_chapters}章
- 情感流动: {system.connection.emotional_flow}

质量评分:
- 情感冲击: {int(system.emotional_impact_score * 100)}%
- 主题连贯: {int(system.thematic_coherence_score * 100)}%
- 满意度: {int(system.satisfaction_score * 100)}%
"""
        return summary

    def export_system(self, system: ClimaxEndingSystem) -> dict:
        """Export climax and ending system to dictionary.

        Args:
            system: Climax ending system

        Returns:
            Dictionary representation
        """
        return {
            "id": system.id,
            "story_id": system.story_id,
            "climax": {
                "id": system.climax_design.id,
                "type": system.climax_design.main_climax.climax_type.value,
                "name": system.climax_design.main_climax.name,
                "chapter": system.climax_design.climax_chapter,
                "peak_moment": system.climax_design.main_climax.peak_moment,
                "emotional_impact": system.climax_design.main_climax.emotional_impact,
                "sub_climaxes": [
                    {"type": sc.climax_type.value, "chapter": sc.peak_chapter}
                    for sc in system.climax_design.sub_climaxes
                ],
            },
            "ending": {
                "id": system.ending_design.id,
                "type": system.ending_design.ending.ending_type.value,
                "name": system.ending_design.ending.name,
                "chapter": system.ending_design.ending_chapter,
                "final_image": system.ending_design.ending.final_image,
                "final_line": system.ending_design.ending.final_line,
                "closure_level": system.ending_design.closure_level,
            },
            "connection": {
                "transition_chapters": system.connection.transition_chapters,
                "emotional_flow": system.connection.emotional_flow,
            },
            "quality": {
                "emotional_impact": system.emotional_impact_score,
                "thematic_coherence": system.thematic_coherence_score,
                "satisfaction": system.satisfaction_score,
            },
        }
