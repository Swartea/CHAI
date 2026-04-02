"""World building engine for comprehensive world generation."""

from typing import Optional, Any
from chai.models import (
    WorldSetting,
    MagicSystem,
    SocialStructure,
)
from chai.services import AIService


class PowerSystemBuilder:
    """Builder for magic/tech/superpower systems using MagicSystemEngine."""

    def __init__(self, ai_service: AIService):
        """Initialize with AI service."""
        from chai.engines.magic_system_engine import MagicSystemEngine
        self._engine = MagicSystemEngine(ai_service)

    async def build(
        self,
        genre: str,
        theme: str,
        system_type: str = "mixed",
        world_context: Optional[dict] = None,
    ) -> MagicSystem:
        """Build a complete power system.

        Args:
            genre: Novel genre
            theme: Central theme
            system_type: Type of system (magic, technology, superpower, mixed)
            world_context: Optional world context

        Returns:
            Complete MagicSystem
        """
        return await self._engine.build_power_system(
            genre=genre,
            theme=theme,
            system_type=system_type,
            world_context=world_context,
        )

    def analyze(self, magic_system: MagicSystem) -> dict[str, Any]:
        """Analyze system consistency.

        Args:
            magic_system: System to analyze

        Returns:
            Analysis results
        """
        return self._engine.analyze_system_consistency(magic_system)

    def summarize(self, magic_system: MagicSystem) -> str:
        """Get system summary.

        Args:
            magic_system: System to summarize

        Returns:
            Formatted summary string
        """
        return self._engine.get_system_summary(magic_system)


class SocialSystemBuilder:
    """Builder for social structures and factions using SocialSystemEngine."""

    def __init__(self, ai_service: AIService):
        """Initialize with AI service."""
        from chai.engines.social_system_engine import SocialSystemEngine
        self._engine = SocialSystemEngine(ai_service)

    async def build(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        politics: Optional[dict] = None,
        culture: Optional[dict] = None,
        magic_system: Optional[Any] = None,
    ) -> "SocialStructure":
        """Build a complete social system.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data for context
            politics: Politics data for context
            culture: Culture data for context
            magic_system: Magic/tech system for context

        Returns:
            Complete SocialStructure
        """
        return await self._engine.build_social_system(
            genre=genre,
            theme=theme,
            geography=geography,
            politics=politics,
            culture=culture,
            magic_system=magic_system,
        )

    def analyze(self, social_structure: "SocialStructure") -> dict[str, Any]:
        """Analyze social structure consistency.

        Args:
            social_structure: Social structure to analyze

        Returns:
            Analysis results
        """
        return self._engine.analyze_social_consistency(social_structure)

    def summarize(self, social_structure: "SocialStructure") -> str:
        """Get social structure summary.

        Args:
            social_structure: Social structure to summarize

        Returns:
            Formatted summary string
        """
        return self._engine.get_social_summary(social_structure)


class WorldSystem:
    """Represents a complete world system with interconnected components.

    Tracks relationships and dependencies between geography, politics,
    culture, and history elements.
    """

    def __init__(self, world_setting: WorldSetting):
        """Initialize world system."""
        self.world = world_setting
        self._relationships: dict[str, list[str]] = {}
        self._influences: dict[str, dict[str, str]] = {}

    def analyze_relationships(self) -> dict[str, Any]:
        """Analyze relationships between world components.

        Returns:
            Dict describing how geography, politics, culture, history interconnect
        """
        relationships = {
            "geography_politics": self._analyze_geo_politics(),
            "politics_culture": self._analyze_politics_culture(),
            "culture_history": self._analyze_culture_history(),
            "history_geography": self._analyze_history_geography(),
            "cross_influences": self._get_cross_influences(),
        }
        self._relationships = relationships
        return relationships

    def _analyze_geo_politics(self) -> dict[str, Any]:
        """Analyze geography's influence on politics."""
        geo = self.world.geography
        politics = self.world.politics

        countries = geo.get("countries", [])
        governments = politics.get("governments", [])
        conflicts = politics.get("conflicts", [])

        return {
            "territorial_claims": len(conflicts),
            "government_count": len(governments),
            "country_count": len(countries),
            "influence": "Geography shapes political boundaries and territorial disputes",
        }

    def _analyze_politics_culture(self) -> dict[str, Any]:
        """Analyze politics' influence on culture."""
        politics = self.world.politics
        culture = self.world.culture

        factions = politics.get("factions", [])
        religions = culture.get("religions", [])
        traditions = culture.get("traditions", [])

        return {
            "faction_count": len(factions),
            "religion_count": len(religions),
            "tradition_count": len(traditions),
            "influence": "Political power structures shape cultural development and religious institutions",
        }

    def _analyze_culture_history(self) -> dict[str, Any]:
        """Analyze culture's influence on history."""
        culture = self.world.culture
        history = self.world.history

        traditions = culture.get("traditions", [])
        religions = culture.get("religions", [])
        eras = history.get("eras", [])
        events = history.get("major_events", [])

        return {
            "tradition_count": len(traditions),
            "religion_count": len(religions),
            "era_count": len(eras),
            "event_count": len(events),
            "influence": "Cultural traditions shape historical narratives and collective memory",
        }

    def _analyze_history_geography(self) -> dict[str, Any]:
        """Analyze history's influence on geography."""
        history = self.world.history
        geo = self.world.geography

        events = history.get("major_events", [])
        landmarks = geo.get("landmarks", [])
        cities = geo.get("cities", [])

        return {
            "event_count": len(events),
            "landmark_count": len(landmarks),
            "city_count": len(cities),
            "influence": "Historical events shape landmarks, cities, and territorial changes",
        }

    def _get_cross_influences(self) -> dict[str, str]:
        """Get all cross-influences between world components."""
        return {
            "geography → politics": "Terrain determines strategic positions, natural resources affect economic power",
            "politics → culture": "Laws, factions, and governance shape religions, customs, and arts",
            "culture → history": "Traditions and beliefs influence how events are recorded and remembered",
            "history → geography": "Wars and migrations change borders and create new landmarks",
            "geography → culture": "Climate and terrain influence lifestyle, cuisine, and traditions",
            "politics → history": "Decisions of leaders create turning points that shape future eras",
        }

    def get_consistency_report(self) -> dict[str, Any]:
        """Generate a consistency report for the world system.

        Returns:
            Dict with consistency issues and recommendations
        """
        issues = []
        recommendations = []

        # Check geography-political alignment
        geo_countries = len(self.world.geography.get("countries", []))
        pol_govs = len(self.world.politics.get("governments", []))
        if geo_countries > 0 and pol_govs > 0 and geo_countries != pol_govs:
            issues.append(f"Mismatch: {geo_countries} countries but {pol_govs} governments")
            recommendations.append("Ensure each major country has a corresponding government structure")

        # Check cultural-religious alignment
        cultures = self.world.culture.get("religions", [])
        if len(cultures) == 0:
            recommendations.append("Consider adding religious/cultural institutions for depth")

        # Check history-era alignment
        events = self.world.history.get("major_events", [])
        eras = self.world.history.get("eras", [])
        if len(events) > 0 and len(eras) == 0:
            recommendations.append("Consider organizing history into distinct eras")
        if len(events) > 0 and len(events) < 3:
            recommendations.append("Consider adding more major historical events for depth")

        # Check geography landmarks
        landmarks = self.world.geography.get("landmarks", [])
        if len(landmarks) < 3:
            recommendations.append("Consider adding more notable landmarks for world texture")

        # Check cities
        cities = self.world.geography.get("cities", [])
        if len(cities) < 3:
            recommendations.append("Consider adding more cities for narrative settings")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "status": "consistent" if len(issues) == 0 else "needs_review",
        }


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
            # Use PowerSystemBuilder for comprehensive magic system generation
            power_builder = PowerSystemBuilder(self.ai_service)
            world_context = {
                "geography": geography,
                "politics": politics,
                "culture": culture,
            }
            system_type = self._infer_power_system_type(genre)
            magic_system = await power_builder.build(
                genre=genre,
                theme=theme,
                system_type=system_type,
                world_context=world_context,
            )

        # Use SocialSystemBuilder for comprehensive social structure generation
        social_builder = SocialSystemBuilder(self.ai_service)
        social_structure = await social_builder.build(
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
                # Build new magic system using PowerSystemBuilder
                power_builder = PowerSystemBuilder(self.ai_service)
                world_context = {
                    "geography": world_setting.geography,
                    "politics": world_setting.politics,
                    "culture": world_setting.culture,
                }
                world_setting.magic_system = await power_builder.build(
                    genre=world_setting.genre,
                    theme="",
                    system_type=self._infer_power_system_type(world_setting.genre),
                    world_context=world_context,
                )
            else:
                # Expand existing magic system using MagicSystemEngine
                from chai.engines.magic_system_engine import MagicSystemEngine
                engine = MagicSystemEngine(self.ai_service)
                world_context = {
                    "geography": world_setting.geography,
                    "politics": world_setting.politics,
                    "culture": world_setting.culture,
                }
                world_setting.magic_system = await engine.expand_magic_system(
                    magic_system=world_setting.magic_system,
                    expansion_type="schools",
                    world_context=world_context,
                )

        elif expansion_type == "social":
            if world_setting.social_structure is None:
                # Build new social structure using SocialSystemBuilder
                social_builder = SocialSystemBuilder(self.ai_service)
                world_setting.social_structure = await social_builder.build(
                    genre=world_setting.genre,
                    theme="",
                    geography=world_setting.geography,
                    politics=world_setting.politics,
                    culture=world_setting.culture,
                    magic_system=world_setting.magic_system,
                )
            else:
                # Expand existing social structure using SocialSystemEngine
                from chai.engines.social_system_engine import SocialSystemEngine
                engine = SocialSystemEngine(self.ai_service)
                world_setting.social_structure = await engine.expand_social_system(
                    social_structure=world_setting.social_structure,
                    expansion_type="factions",
                    genre=world_setting.genre,
                    theme="",
                )

        return world_setting

    def _uses_magic_system(self, genre: str) -> bool:
        """Check if genre typically uses magic/tech/superpower systems."""
        magic_genres = {
            "玄幻", "奇幻", "仙侠", "科幻", "都市异能",
            "fantasy", "sci-fi", "xianxia", "urban fantasy",
        }
        return genre.lower() in {g.lower() for g in magic_genres}

    def _infer_power_system_type(self, genre: str) -> str:
        """Infer the type of power system based on genre.

        Args:
            genre: Novel genre

        Returns:
            Power system type (magic, technology, superpower, mixed)
        """
        genre_lower = genre.lower()
        if genre_lower in {"科幻", "sci-fi"}:
            return "technology"
        elif genre_lower in {"都市异能", "urban fantasy", "都市", "modern"}:
            return "superpower"
        elif genre_lower in {"玄幻", "奇幻", "仙侠", "fantasy", "xianxia"}:
            return "magic"
        else:
            return "mixed"

    async def build_power_system(
        self,
        genre: str,
        theme: str,
        system_type: Optional[str] = None,
    ) -> MagicSystem:
        """Build a standalone power system.

        Args:
            genre: Novel genre
            theme: Central theme
            system_type: Optional specific system type

        Returns:
            Complete MagicSystem
        """
        power_builder = PowerSystemBuilder(self.ai_service)
        inferred_type = system_type or self._infer_power_system_type(genre)
        return await power_builder.build(
            genre=genre,
            theme=theme,
            system_type=inferred_type,
        )

    async def build_core_world(
        self,
        genre: str,
        theme: str,
        customizations: Optional[dict] = None,
    ) -> WorldSetting:
        """Build a complete world with only the 4 core elements.

        Builds geography, politics, culture, and history without magic
        or social systems - ideal for realistic/modern fiction.

        Args:
            genre: Novel genre
            theme: Central theme
            customizations: Optional customizations for world generation

        Returns:
            WorldSetting with core components (geography, politics, culture, history)
        """
        customizations = customizations or {}

        # Generate base world setting
        world_data = await self.ai_service.generate_world_setting(genre, theme)

        # Generate core components ensuring they reference each other
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

        world = WorldSetting(
            name=world_data.get("name", f"{theme}世界"),
            genre=genre,
            geography=geography,
            politics=politics,
            culture=culture,
            history=history,
            magic_system=None,
            social_structure=None,
        )

        return world

    def build_world_system(
        self,
        world_setting: WorldSetting,
    ) -> WorldSystem:
        """Build a complete world system from a world setting.

        Creates a WorldSystem that tracks relationships and dependencies
        between all world components.

        Args:
            world_setting: Existing world setting

        Returns:
            WorldSystem with analyzed relationships
        """
        system = WorldSystem(world_setting)
        system.analyze_relationships()
        return system

    async def build_complete_world_system(
        self,
        genre: str,
        theme: str,
        customizations: Optional[dict] = None,
    ) -> tuple[WorldSetting, WorldSystem]:
        """Build a complete world and its system representation.

        Creates a fully integrated world with all components and
        a WorldSystem that tracks their relationships.

        Args:
            genre: Novel genre
            theme: Central theme
            customizations: Optional customizations

        Returns:
            Tuple of (WorldSetting, WorldSystem)
        """
        world = await self.build_world(genre, theme, customizations)
        system = self.build_world_system(world)
        return world, system

    def validate_world_consistency(
        self,
        world_setting: WorldSetting,
    ) -> dict[str, Any]:
        """Validate consistency of a world setting.

        Checks for logical inconsistencies between world components
        and provides recommendations.

        Args:
            world_setting: World setting to validate

        Returns:
            Dict with validation results and recommendations
        """
        system = WorldSystem(world_setting)
        return system.get_consistency_report()

    def get_world_summary(
        self,
        world_setting: WorldSetting,
    ) -> str:
        """Get a human-readable summary of the world.

        Args:
            world_setting: World setting to summarize

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {world_setting.name} ===",
            f"类型: {world_setting.genre}",
            "",
            "【地理环境】",
        ]

        geo = world_setting.geography
        if geo:
            continents = geo.get("continents", [])
            countries = geo.get("countries", [])
            cities = geo.get("cities", [])
            landmarks = geo.get("landmarks", [])

            if continents:
                lines.append(f"  大陆: {', '.join(c.get('name', '') for c in continents[:3])}")
            if countries:
                lines.append(f"  国家: {len(countries)}个")
            if cities:
                lines.append(f"  城市: {len(cities)}座")
            if landmarks:
                lines.append(f"  地标: {len(landmarks)}处")
        else:
            lines.append("  (未设定)")

        lines.extend(["", "【政治结构】"])
        politics = world_setting.politics
        if politics:
            governments = politics.get("governments", [])
            factions = politics.get("factions", [])
            conflicts = politics.get("conflicts", [])

            if governments:
                lines.append(f"  政府: {', '.join(g.get('name', '') for g in governments[:3])}")
            if factions:
                lines.append(f"  势力: {len(factions)}个")
            if conflicts:
                lines.append(f"  冲突: {len(conflicts)}起")
        else:
            lines.append("  (未设定)")

        lines.extend(["", "【文化元素】"])
        culture = world_setting.culture
        if culture:
            religions = culture.get("religions", [])
            traditions = culture.get("traditions", [])
            languages = culture.get("languages", [])

            if religions:
                lines.append(f"  宗教: {', '.join(r.get('name', '') for r in religions[:3])}")
            if traditions:
                lines.append(f"  传统: {len(traditions)}项")
            if languages:
                lines.append(f"  语言: {len(languages)}种")
        else:
            lines.append("  (未设定)")

        lines.extend(["", "【历史背景】"])
        history = world_setting.history
        if history:
            eras = history.get("eras", [])
            events = history.get("major_events", [])
            figures = history.get("historical_figures", [])

            if eras:
                lines.append(f"  时代: {', '.join(e.get('name', '') for e in eras[:3])}")
            if events:
                lines.append(f"  事件: {len(events)}起")
            if figures:
                lines.append(f"  人物: {len(figures)}位")
        else:
            lines.append("  (未设定)")

        if world_setting.magic_system:
            ms = world_setting.magic_system
            lines.extend(["", f"【魔法系统: {ms.name}】"])
            lines.append(f"  类型: {ms.system_type}")
            lines.append(f"  规则: {len(ms.rules)}条")
            lines.append(f"  限制: {len(ms.limitations)}条")

        if world_setting.social_structure:
            ss = world_setting.social_structure
            lines.extend(["", "【社会结构】"])
            lines.append(f"  阶层: {len(ss.classes)}个")
            lines.append(f"  势力: {len(ss.factions)}个")

        return "\n".join(lines)

    def export_world_system(
        self,
        world_setting: WorldSetting,
        include_relationships: bool = True,
    ) -> dict[str, Any]:
        """Export world as a complete system document.

        Args:
            world_setting: World setting to export
            include_relationships: Whether to include relationship analysis

        Returns:
            Dict containing complete world system data
        """
        export_data = {
            "world": world_setting.model_dump(),
            "summary": self.get_world_summary(world_setting),
        }

        if include_relationships:
            system = WorldSystem(world_setting)
            export_data["relationships"] = system.analyze_relationships()
            export_data["consistency"] = system.get_consistency_report()

        return export_data
