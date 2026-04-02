"""World building engine for comprehensive world generation."""

from typing import Optional
from chai.models import (
    WorldSetting,
    MagicSystem,
    SocialStructure,
)
from chai.services import AIService


class WorldBuilder:
    """Engine for building comprehensive world settings.

    Coordinates generation of geography, politics, culture, history,
    magic/tech systems, and social structures.
    """

    def __init__(self, ai_service: AIService):
        """Initialize world builder with AI service."""
        self.ai_service = ai_service

    async def build_world(
        self,
        genre: str,
        theme: str,
        customizations: Optional[dict] = None,
    ) -> WorldSetting:
        """Build a complete world setting.

        Args:
            genre: Novel genre
            theme: Central theme
            customizations: Optional customizations for world generation

        Returns:
            Complete WorldSetting with all components
        """
        customizations = customizations or {}

        # Generate base world setting
        world_data = await self.ai_service.generate_world_setting(genre, theme)

        # Generate detailed components in parallel
        geography = await self.ai_service.generate_geography(
            genre=genre,
            theme=theme,
            base_geography=world_data.get("geography", {}),
        )

        politics = await self.ai_service.generate_politics(
            genre=genre,
            theme=theme,
            geography=geography,
        )

        culture = await self.ai_service.generate_culture(
            genre=genre,
            theme=theme,
            geography=geography,
            politics=politics,
        )

        history = await self.ai_service.generate_history(
            genre=genre,
            theme=theme,
            geography=geography,
            politics=politics,
            culture=culture,
        )

        magic_system = None
        if self._uses_magic_system(genre):
            magic_system = await self.ai_service.generate_magic_system(
                genre=genre,
                theme=theme,
                world_context={
                    "geography": geography,
                    "politics": politics,
                    "culture": culture,
                },
            )

        social_structure = await self.ai_service.generate_social_structure(
            genre=genre,
            theme=theme,
            geography=geography,
            politics=politics,
            culture=culture,
            magic_system=magic_system,
        )

        world = WorldSetting(
            name=world_data.get("name", f"{theme}世界"),
            genre=genre,
            geography=geography,
            politics=politics,
            culture=culture,
            history=history,
            magic_system=magic_system,
            social_structure=social_structure,
        )

        return world

    async def expand_world(
        self,
        world_setting: WorldSetting,
        expansion_type: str,
    ) -> WorldSetting:
        """Expand an existing world setting.

        Args:
            world_setting: Existing world setting
            expansion_type: Type of expansion (geography, politics, culture, history, magic, social)

        Returns:
            Updated WorldSetting
        """
        if expansion_type == "geography":
            new_geography = await self.ai_service.generate_geography(
                genre=world_setting.genre,
                theme="",
                base_geography=world_setting.geography,
                expand=True,
            )
            world_setting.geography = new_geography

        elif expansion_type == "politics":
            new_politics = await self.ai_service.generate_politics(
                genre=world_setting.genre,
                theme="",
                geography=world_setting.geography,
                expand=True,
            )
            world_setting.politics = new_politics

        elif expansion_type == "culture":
            new_culture = await self.ai_service.generate_culture(
                genre=world_setting.genre,
                theme="",
                geography=world_setting.geography,
                politics=world_setting.politics,
                expand=True,
            )
            world_setting.culture = new_culture

        elif expansion_type == "history":
            new_history = await self.ai_service.generate_history(
                genre=world_setting.genre,
                theme="",
                geography=world_setting.geography,
                politics=world_setting.politics,
                culture=world_setting.culture,
                expand=True,
            )
            world_setting.history = new_history

        elif expansion_type == "magic":
            if world_setting.magic_system is None:
                world_setting.magic_system = await self.ai_service.generate_magic_system(
                    genre=world_setting.genre,
                    theme="",
                    world_context={
                        "geography": world_setting.geography,
                        "politics": world_setting.politics,
                        "culture": world_setting.culture,
                    },
                )
            else:
                # Expand existing magic system
                expanded = await self.ai_service.expand_magic_system(
                    existing_magic=world_setting.magic_system.model_dump(),
                    world_context={
                        "geography": world_setting.geography,
                        "politics": world_setting.politics,
                        "culture": world_setting.culture,
                    },
                )
                world_setting.magic_system = MagicSystem(**expanded)

        elif expansion_type == "social":
            new_social = await self.ai_service.generate_social_structure(
                genre=world_setting.genre,
                theme="",
                geography=world_setting.geography,
                politics=world_setting.politics,
                culture=world_setting.culture,
                magic_system=world_setting.magic_system,
                expand=True,
            )
            world_setting.social_structure = new_social

        return world_setting

    def _uses_magic_system(self, genre: str) -> bool:
        """Check if genre typically uses magic/tech/superpower systems."""
        magic_genres = {
            "玄幻", "奇幻", "仙侠", "科幻", "都市异能",
            "fantasy", "sci-fi", "xianxia", "urban fantasy",
        }
        return genre.lower() in {g.lower() for g in magic_genres}
