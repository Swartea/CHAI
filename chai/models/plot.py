"""Plot models for story structure."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PlotPointType(str, Enum):
    """Types of plot points."""
    EXPOSITION = "exposition"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    MIDPOINT = "midpoint"
    CRISIS = "crisis"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


class PlotStructure(str, Enum):
    """Story structure types."""
    THREE_ACT = "three_act"
    HEROS_JOURNEY = "heros_journey"
    SEVEN_POINT = "seven_point"
    SAVE_THE_CAT = "save_the_cat"


class PlotPoint(BaseModel):
    """Individual plot point in the story."""

    id: str = Field(description="Unique plot point ID")
    point_type: PlotPointType = Field(description="Type of plot point")

    title: str = Field(description="Plot point title")
    description: str = Field(description="What happens at this point")

    chapter_range: tuple[int, int] = Field(
        description="Chapter range for this plot point (start, end)"
    )

    characters_involved: list[str] = Field(
        default_factory=list,
        description="Character IDs involved"
    )

    themes: list[str] = Field(
        default_factory=list,
        description="Themes explored at this point"
    )

    foreshadowing: list[str] = Field(
        default_factory=list,
        description="Foreshadowing elements planted"
    )


class PlotArc(BaseModel):
    """A plot arc within the story."""

    id: str = Field(description="Unique arc ID")
    name: str = Field(description="Arc name")

    arc_type: str = Field(
        description="Type: main, subplot, character, romantic, etc."
    )

    plot_points: list[PlotPoint] = Field(
        default_factory=list,
        description="Sequence of plot points"
    )

    protagonist: Optional[str] = Field(
        default=None,
        description="Main character focused in this arc"
    )


class PlotOutline(BaseModel):
    """Complete plot outline for the novel."""

    structure_type: PlotStructure = Field(
        description="Story structure used"
    )

    genre: str = Field(description="Novel genre")

    theme: list[str] = Field(
        default_factory=list,
        description="Central themes"
    )

    plot_arcs: list[PlotArc] = Field(
        default_factory=list,
        description="All plot arcs"
    )

    subplots: list[str] = Field(
        default_factory=list,
        description="Subplot descriptions"
    )

    foreshadowing_plan: dict = Field(
        default_factory=dict,
        description="Planted foreshadowing and payoffs"
    )
