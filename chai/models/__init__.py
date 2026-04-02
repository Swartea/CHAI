"""Data models for CHAI novel writing system."""

from chai.models.world import WorldSetting, MagicSystem, SocialStructure
from chai.models.character import Character, CharacterRelationship, CharacterRole
from chai.models.plot import PlotOutline, PlotArc, PlotPoint, PlotPointType, PlotStructure
from chai.models.novel import Novel, Volume, Chapter, Scene, SceneType

# Rebuild models to resolve forward references after all imports
Novel.model_rebuild()
Volume.model_rebuild()
Chapter.model_rebuild()
Scene.model_rebuild()

__all__ = [
    "WorldSetting",
    "MagicSystem",
    "SocialStructure",
    "Character",
    "CharacterRelationship",
    "CharacterRole",
    "PlotOutline",
    "PlotArc",
    "PlotPoint",
    "PlotPointType",
    "PlotStructure",
    "Novel",
    "Volume",
    "Chapter",
    "Scene",
    "SceneType",
]
