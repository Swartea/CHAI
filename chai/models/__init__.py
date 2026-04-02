"""Data models for CHAI novel writing system."""

from chai.models.world import (
    WorldSetting,
    MagicSystem,
    SocialStructure,
    PowerTechnique,
    PowerConflict,
    SocialClass,
    Faction,
    FactionRelationship,
    Guild,
    CriminalOrganization,
    ReligiousInstitution,
    SecretSociety,
    SocialConflict,
)
from chai.models.character import (
    Character,
    CharacterRelationship,
    CharacterRole,
    CharacterRelationshipType,
    CharacterArchetype,
    CharacterSkill,
    CharacterGroup,
    CharacterConflict,
    CharacterGrowthStage,
    CharacterSystem,
)
from chai.models.main_character import (
    MainCharacter,
    MainCharacterProfile,
    AppearanceDetail,
    PersonalityDimension,
    BackgroundDetail,
    MotivationDetail,
    MotivationType,
)
from chai.models.plot import PlotOutline, PlotArc, PlotPoint, PlotPointType, PlotStructure
from chai.models.novel import Novel, Volume, Chapter, Scene, SceneType
from chai.models.deconstruct import (
    CharacterTemplate,
    CharacterTemplateType,
    PlotPattern,
    PlotPatternType,
    WorldTemplate,
    WorldTemplateType,
    DeconstructSource,
    DeconstructionResult,
    BookDeconstructTemplate,
)

# Rebuild models to resolve forward references after all imports
Novel.model_rebuild()
Volume.model_rebuild()
Chapter.model_rebuild()
Scene.model_rebuild()

__all__ = [
    "WorldSetting",
    "MagicSystem",
    "SocialStructure",
    "PowerTechnique",
    "PowerConflict",
    "SocialClass",
    "Faction",
    "FactionRelationship",
    "Guild",
    "CriminalOrganization",
    "ReligiousInstitution",
    "SecretSociety",
    "SocialConflict",
    "Character",
    "CharacterRelationship",
    "CharacterRole",
    "CharacterRelationshipType",
    "CharacterArchetype",
    "CharacterSkill",
    "CharacterGroup",
    "CharacterConflict",
    "CharacterGrowthStage",
    "CharacterSystem",
    "MainCharacter",
    "MainCharacterProfile",
    "AppearanceDetail",
    "PersonalityDimension",
    "BackgroundDetail",
    "MotivationDetail",
    "MotivationType",
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
    # Deconstruct models
    "CharacterTemplate",
    "CharacterTemplateType",
    "PlotPattern",
    "PlotPatternType",
    "WorldTemplate",
    "WorldTemplateType",
    "DeconstructSource",
    "DeconstructionResult",
    "BookDeconstructTemplate",
]
