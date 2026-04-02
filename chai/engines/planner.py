"""Story planning engine."""

from typing import Optional
from chai.models import (
    Novel,
    WorldSetting,
    Character,
    PlotOutline,
    PlotArc,
    PlotPoint,
    PlotPointType,
    PlotStructure,
)
from chai.services import AIService


# Plot structure templates for different story structures
HEROS_JOURNEY_POINTS = [
    (PlotPointType.EXPOSITION, "普通世界", "介绍主角及其日常生活"),
    (PlotPointType.INCITING_INCIDENT, "冒险召唤", "收到改变命运的召唤"),
    (PlotPointType.RISING_ACTION, "拒绝召唤", "主角犹豫或拒绝"),
    (PlotPointType.MIDPOINT, "遇到导师", "获得指引或学习技能"),
    (PlotPointType.RISING_ACTION, "跨越门槛", "正式踏上冒险旅程"),
    (PlotPointType.RISING_ACTION, "考验与盟友", "面对挑战，结识伙伴或敌人"),
    (PlotPointType.CRISIS, "最深处的洞穴", "面临最大考验"),
    (PlotPointType.CLIMAX, "考验", "决定性对决或挑战"),
    (PlotPointType.FALLING_ACTION, "回报", "获得奖励或完成目标"),
    (PlotPointType.RESOLUTION, "回归之路", "带着改变回归"),
]

SEVEN_POINT_POINTS = [
    (PlotPointType.EXPOSITION, "钩子", "吸引读者的开场"),
    (PlotPointType.INCITING_INCIDENT, "第一转折点", "打破平衡的事件"),
    (PlotPointType.RISING_ACTION, "假装胜利", "主角看似成功"),
    (PlotPointType.MIDPOINT, "第二转折点", "揭示真正挑战"),
    (PlotPointType.RISING_ACTION, "所有失去", "最低谷时刻"),
    (PlotPointType.CRISIS, "黑色时刻", "看似无望"),
    (PlotPointType.CLIMAX, "第三转折点", "最终对决"),
    (PlotPointType.RESOLUTION, "结局", "解决与收尾"),
]

SAVE_THE_CAT_POINTS = [
    (PlotPointType.EXPOSITION, "开场画面", "建立调性，展现主题"),
    (PlotPointType.INCITING_INCIDENT, "主题呈现", "提出故事主题"),
    (PlotPointType.RISING_ACTION, "Set-up", "建立世界与角色"),
    (PlotPointType.RISING_ACTION, "催化剂", "改变一切的事件"),
    (PlotPointType.MIDPOINT, "争执", "主角抵抗改变"),
    (PlotPointType.RISING_ACTION, "B故事", "引入次要情节线"),
    (PlotPointType.CRISIS, "游戏", "中间段，角色尝试新道路"),
    (PlotPointType.CLIMAX, "所有失去", "最黑暗时刻"),
    (PlotPointType.FALLING_ACTION, "黑色事件", "跌至谷底"),
    (PlotPointType.RESOLUTION, "结局画面", "问题解决，新常态"),
]


class StoryPlanner:
    """Engine for planning and structuring novels."""

    def __init__(self, ai_service: AIService):
        """Initialize story planner with AI service."""
        self.ai_service = ai_service

    async def create_world(
        self,
        genre: str,
        theme: str,
        customizations: Optional[dict] = None,
    ) -> WorldSetting:
        """Create world setting for a new novel."""
        world_data = await self.ai_service.generate_world_setting(genre, theme)

        world = WorldSetting(
            name=world_data.get("name", f"{theme}世界"),
            genre=genre,
            geography=world_data.get("geography", {}),
            politics=world_data.get("politics", {}),
            culture=world_data.get("culture", {}),
            history=world_data.get("history", {}),
        )

        return world

    async def create_characters(
        self,
        world_setting: WorldSetting,
        genre: str,
        protagonist_count: int = 1,
        supporting_count: int = 3,
        antagonist_count: int = 1,
    ) -> list[Character]:
        """Create characters for the novel."""
        char_data = await self.ai_service.generate_characters(
            world_setting=world_setting.model_dump(),
            genre=genre,
            count=protagonist_count + supporting_count + antagonist_count,
        )

        characters = []
        for i, c in enumerate(char_data[:protagonist_count]):
            characters.append(Character(
                id=f"char_{i}",
                name=c.get("name", f"主角{i}"),
                role="protagonist",
                backstory=c.get("backstory", ""),
                motivation=c.get("motivation", ""),
                goal=c.get("goal", ""),
            ))

        for i, c in enumerate(char_data[protagonist_count:protagonist_count + supporting_count]):
            characters.append(Character(
                id=f"char_{protagonist_count + i}",
                name=c.get("name", f"配角{i}"),
                role="supporting",
                backstory=c.get("backstory", ""),
                motivation=c.get("motivation", ""),
                goal=c.get("goal", ""),
            ))

        for i, c in enumerate(char_data[protagonist_count + supporting_count:]):
            characters.append(Character(
                id=f"char_{protagonist_count + supporting_count + i}",
                name=c.get("name", f"反派{i}"),
                role="antagonist",
                backstory=c.get("backstory", ""),
                motivation=c.get("motivation", ""),
                goal=c.get("goal", ""),
            ))

        return characters

    async def create_plot_outline(
        self,
        world_setting: WorldSetting,
        characters: list[Character],
        genre: str,
        theme: str,
        structure: PlotStructure = PlotStructure.THREE_ACT,
    ) -> PlotOutline:
        """Create complete plot outline with specified structure.

        Args:
            world_setting: World setting for the novel
            characters: List of characters
            genre: Novel genre
            theme: Central theme
            structure: Plot structure type (THREE_ACT, HEROS_JOURNEY, SEVEN_POINT, SAVE_THE_CAT)
        """
        plot_data = await self.ai_service.generate_plot_outline(
            world_setting=world_setting.model_dump(),
            characters=[c.model_dump() for c in characters],
            genre=genre,
        )

        # Get plot structure template
        if structure == PlotStructure.HEROS_JOURNEY:
            structure_template = HEROS_JOURNEY_POINTS
        elif structure == PlotStructure.SEVEN_POINT:
            structure_template = SEVEN_POINT_POINTS
        elif structure == PlotStructure.SAVE_THE_CAT:
            structure_template = SAVE_THE_CAT_POINTS
        else:
            structure_template = self._get_three_act_points(plot_data)

        plot_points = []
        for i, (point_type, title, desc) in enumerate(structure_template):
            ai_points = plot_data.get("plot_arcs", [{}])[0].get("plot_points", [])
            ai_point = ai_points[i] if i < len(ai_points) else {}

            chapter_start = i * 3 + 1
            chapter_end = (i + 1) * 3

            plot_points.append(PlotPoint(
                id=f"pp_{i}",
                point_type=point_type,
                title=ai_point.get("title", title),
                description=ai_point.get("description", desc),
                chapter_range=(chapter_start, chapter_end),
                characters_involved=[c.id for c in characters[:3]],
                themes=[theme],
                foreshadowing=ai_point.get("foreshadowing", []),
            ))

        arc = PlotArc(
            id="main_arc",
            name="主线剧情",
            arc_type="main",
            plot_points=plot_points,
            protagonist=characters[0].id if characters else None,
        )

        # Extract subplots from AI response
        subplots = plot_data.get("subplots", [])
        foreshadowing_plan = plot_data.get("foreshadowing_plan", {})

        return PlotOutline(
            structure_type=structure,
            genre=genre,
            theme=[theme],
            plot_arcs=[arc],
            subplots=subplots,
            foreshadowing_plan=foreshadowing_plan,
        )

    def _get_three_act_points(self, plot_data: dict) -> list:
        """Get Three-Act structure plot points."""
        return [
            (PlotPointType.EXPOSITION, "建置", "介绍世界、角色和 situation"),
            (PlotPointType.INCITING_INCIDENT, "催化事件", "打破平衡的事件"),
            (PlotPointType.RISING_ACTION, "上升", "冲突加剧， tension 增加"),
            (PlotPointType.MIDPOINT, "中点", "重大发现或转折"),
            (PlotPointType.RISING_ACTION, "逼近", "冲突达到顶点"),
            (PlotPointType.CRISIS, "危机", "主角面临最大挑战"),
            (PlotPointType.CLIMAX, "高潮", "决定性对决"),
            (PlotPointType.FALLING_ACTION, "下降", "问题解决"),
            (PlotPointType.RESOLUTION, "结局", "恢复正常或新常态"),
        ]

    async def create_subplot_arc(
        self,
        main_plot: PlotOutline,
        characters: list[Character],
        subplot_index: int,
        arc_type: str = "subplot",
    ) -> PlotArc:
        """Create a subplot arc for the novel.

        Args:
            main_plot: Main plot outline
            characters: List of characters for this subplot
            subplot_index: Index of subplot
            arc_type: Type of subplot (subplot, romantic, character)
        """
        subplot_char = characters[subplot_index % len(characters)] if characters else None

        subplot_points = [
            PlotPoint(
                id=f"sub_{subplot_index}_0",
                point_type=PlotPointType.EXPOSITION,
                title="子情节引入",
                description=f"展开{arc_type}线",
                chapter_range=(2, 5),
                characters_involved=[subplot_char.id] if subplot_char else [],
            ),
            PlotPoint(
                id=f"sub_{subplot_index}_1",
                point_type=PlotPointType.RISING_ACTION,
                title="子情节发展",
                description=f"{arc_type}线展开",
                chapter_range=(6, 12),
                characters_involved=[subplot_char.id] if subplot_char else [],
            ),
            PlotPoint(
                id=f"sub_{subplot_index}_2",
                point_type=PlotPointType.MIDPOINT,
                title="子情节转折",
                description=f"{arc_type}线转折",
                chapter_range=(13, 16),
                characters_involved=[subplot_char.id] if subplot_char else [],
            ),
            PlotPoint(
                id=f"sub_{subplot_index}_3",
                point_type=PlotPointType.CLIMAX,
                title="子情节高潮",
                description=f"{arc_type}线高潮",
                chapter_range=(17, 20),
                characters_involved=[subplot_char.id] if subplot_char else [],
            ),
            PlotPoint(
                id=f"sub_{subplot_index}_4",
                point_type=PlotPointType.RESOLUTION,
                title="子情节收束",
                description=f"{arc_type}线结束",
                chapter_range=(21, 24),
                characters_involved=[subplot_char.id] if subplot_char else [],
            ),
        ]

        return PlotArc(
            id=f"subplot_arc_{subplot_index}",
            name=f"{arc_type}线 {subplot_index + 1}",
            arc_type=arc_type,
            plot_points=subplot_points,
            protagonist=subplot_char.id if subplot_char else None,
        )

    async def plan_novel(
        self,
        genre: str,
        theme: str,
        protagonist_count: int = 1,
        supporting_count: int = 3,
        antagonist_count: int = 1,
        structure: PlotStructure = PlotStructure.THREE_ACT,
    ) -> Novel:
        """Create a complete novel plan including world, characters, and plot.

        Args:
            genre: Novel genre
            theme: Central theme
            protagonist_count: Number of protagonists
            supporting_count: Number of supporting characters
            antagonist_count: Number of antagonists
            structure: Plot structure to use
        """
        world = await self.create_world(genre, theme)
        characters = await self.create_characters(
            world, genre,
            protagonist_count=protagonist_count,
            supporting_count=supporting_count,
            antagonist_count=antagonist_count,
        )
        plot_outline = await self.create_plot_outline(
            world, characters, genre, theme, structure=structure
        )

        novel = Novel(
            id="novel_1",
            title=f"{theme}：{world.name}",
            genre=genre,
            world_setting=world,
            characters=characters,
            plot_outline=plot_outline,
        )

        return novel
