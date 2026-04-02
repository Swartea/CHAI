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
    ) -> PlotOutline:
        """Create complete plot outline."""
        plot_data = await self.ai_service.generate_plot_outline(
            world_setting=world_setting.model_dump(),
            characters=[c.model_dump() for c in characters],
            genre=genre,
        )

        plot_points = []
        for i, pp in enumerate(plot_data.get("plot_arcs", [{}])[0].get("plot_points", [])[:8]):
            point_types = [
                PlotPointType.EXPOSITION,
                PlotPointType.INCITING_INCIDENT,
                PlotPointType.RISING_ACTION,
                PlotPointType.MIDPOINT,
                PlotPointType.RISING_ACTION,
                PlotPointType.CRISIS,
                PlotPointType.CLIMAX,
                PlotPointType.FALLING_ACTION,
            ]
            plot_points.append(PlotPoint(
                id=f"pp_{i}",
                point_type=point_types[i % len(point_types)],
                title=pp.get("title", f"情节点{i + 1}"),
                description=pp.get("description", ""),
                chapter_range=(i * 3 + 1, (i + 1) * 3),
            ))

        arc = PlotArc(
            id="main_arc",
            name="主线剧情",
            arc_type="main",
            plot_points=plot_points,
            protagonist=characters[0].id if characters else None,
        )

        return PlotOutline(
            structure_type=PlotStructure.THREE_ACT,
            genre=genre,
            theme=[theme],
            plot_arcs=[arc],
        )

    async def plan_novel(
        self,
        genre: str,
        theme: str,
        protagonist_count: int = 1,
        supporting_count: int = 3,
        antagonist_count: int = 1,
    ) -> Novel:
        """Create a complete novel plan including world, characters, and plot."""
        world = await self.create_world(genre, theme)
        characters = await self.create_characters(
            world, genre,
            protagonist_count=protagonist_count,
            supporting_count=supporting_count,
            antagonist_count=antagonist_count,
        )
        plot_outline = await self.create_plot_outline(
            world, characters, genre, theme
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
