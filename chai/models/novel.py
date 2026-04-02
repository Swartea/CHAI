"""Novel, volume, chapter, and scene models."""

from enum import Enum
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from chai.models.world import WorldSetting
    from chai.models.character import Character
    from chai.models.plot import PlotOutline


class SceneType(str, Enum):
    """Scene type classification."""
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    ACTION = "action"
    DESCRIPTION = "description"
    REFLECTION = "reflection"


class Novel(BaseModel):
    """Complete novel model."""

    id: str = Field(description="Unique novel identifier")
    title: str = Field(description="Novel title")
    genre: str = Field(description="Genre")
    target_word_count: int = Field(
        default=80000,
        description="Target word count for entire novel"
    )

    # Components
    world_setting: Optional["WorldSetting"] = Field(default=None, repr=False)
    characters: list["Character"] = Field(default_factory=list, repr=False)
    plot_outline: Optional["PlotOutline"] = Field(default=None, repr=False)

    # Structure
    volumes: list["Volume"] = Field(default_factory=list, description="Volumes/Parts")
    has_prologue: bool = Field(default=False, description="Has prologue")
    has_epilogue: bool = Field(default=False, description="Has epilogue")

    # Metadata
    target_chapter_word_count: tuple[int, int] = Field(
        default=(2000, 4000),
        description="Target word count per chapter (min, max)"
    )


class Volume(BaseModel):
    """Volume/Part within a novel."""

    id: str = Field(description="Volume ID")
    title: str = Field(description="Volume title")
    number: int = Field(description="Volume number")
    description: str = Field(default="", description="Volume description")

    chapters: list["Chapter"] = Field(default_factory=list, description="Chapters in this volume")


class Chapter(BaseModel):
    """Chapter model."""

    id: str = Field(description="Chapter ID")
    number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")

    is_prologue: bool = Field(default=False, description="Is this a prologue")
    is_epilogue: bool = Field(default=False, description="Is this an epilogue")

    summary: str = Field(default="", description="Chapter summary")
    content: str = Field(default="", description="Chapter content")

    word_count: int = Field(default=0, description="Actual word count")
    target_word_count: int = Field(default=3000, description="Target word count")

    scenes: list["Scene"] = Field(default_factory=list, description="Scenes")

    plot_point_ids: list[str] = Field(
        default_factory=list,
        description="Plot point IDs covered"
    )

    characters_involved: list[str] = Field(
        default_factory=list,
        description="Character IDs appearing"
    )

    status: str = Field(
        default="pending",
        description="Status: pending, writing, editing, complete"
    )


class Scene(BaseModel):
    """Scene within a chapter."""

    id: str = Field(description="Scene ID")
    number: int = Field(description="Scene number in chapter")

    scene_type: SceneType = Field(default=SceneType.NARRATIVE)

    location: str = Field(default="", description="Scene location")
    time_period: str = Field(default="", description="Time period")

    characters: list[str] = Field(default_factory=list, description="Character IDs")
    content: str = Field(default="", description="Scene content")

    mood: str = Field(default="", description="Scene mood/atmosphere")
    purpose: str = Field(default="", description="Scene purpose in story")
