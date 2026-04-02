"""
CHAI - AI 小说自动化写作系统

An AI-powered novel writing engine that autonomously plans, generates,
and proofreading complete long-form novel creations.
"""

__version__ = "0.1.0"
__author__ = "CHAI Team"

from chai.models.novel import Novel, Chapter, Scene
from chai.models.character import Character, CharacterRelationship
from chai.models.world import WorldSetting, MagicSystem, SocialStructure
from chai.models.plot import PlotOutline, PlotArc, PlotPoint

__all__ = [
    "Novel",
    "Chapter",
    "Scene",
    "Character",
    "CharacterRelationship",
    "WorldSetting",
    "MagicSystem",
    "SocialStructure",
    "PlotOutline",
    "PlotArc",
    "PlotPoint",
]
