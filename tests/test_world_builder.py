"""Tests for WorldBuilder engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import WorldSetting, MagicSystem, SocialStructure
from chai.engines import WorldBuilder, WorldSystem
from chai.services import AIService


class TestWorldBuilder:
    """Tests for WorldBuilder."""

    def test_uses_magic_system_fantasy(self):
        """Test that fantasy genres use magic systems."""
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        assert builder._uses_magic_system("玄幻") is True
        assert builder._uses_magic_system("奇幻") is True
        assert builder._uses_magic_system("仙侠") is True
        assert builder._uses_magic_system("科幻") is True
        assert builder._uses_magic_system("都市异能") is True
        assert builder._uses_magic_system("fantasy") is True
        assert builder._uses_magic_system("sci-fi") is True

    def test_uses_magic_system_no_magic(self):
        """Test that non-fantasy genres don't use magic systems."""
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        assert builder._uses_magic_system("都市") is False
        assert builder._uses_magic_system("言情") is False
        assert builder._uses_magic_system("悬疑") is False
        assert builder._uses_magic_system("urban") is False
        assert builder._uses_magic_system("romance") is False

    @pytest.mark.asyncio
    async def test_build_world_without_magic(self):
        """Test building a world without magic system for non-fantasy genre."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试都市世界",
            "genre": "都市",
            "geography": {},
            "politics": {},
            "culture": {},
            "history": {},
        })
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [{"name": "亚洲"}],
            "countries": [{"name": "中国"}],
            "cities": [],
            "landmarks": [],
        })
        mock_ai.generate_politics = AsyncMock(return_value={
            "governments": [{"name": "政府"}],
            "factions": [],
        })
        mock_ai.generate_culture = AsyncMock(return_value={
            "religions": [],
            "traditions": [],
        })
        mock_ai.generate_history = AsyncMock(return_value={
            "eras": [],
            "major_events": [],
        })
        mock_ai.generate_social_structure = AsyncMock(return_value=SocialStructure(
            classes=[],
            factions=[],
            power_distribution={},
        ))

        builder = WorldBuilder(mock_ai)

        # Should not raise - even without real API
        world = await builder.build_world("都市", "现代都市生活")

        assert world.name == "测试都市世界"
        assert world.genre == "都市"
        assert world.magic_system is None
        assert world.geography is not None
        assert world.politics is not None
        assert world.culture is not None
        assert world.history is not None

    @pytest.mark.asyncio
    async def test_build_world_with_magic(self):
        """Test building a world with magic system for fantasy genre."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试玄幻世界",
            "genre": "玄幻",
            "geography": {},
            "politics": {},
            "culture": {},
            "history": {},
        })
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [{"name": "大陆"}],
            "countries": [],
            "cities": [],
            "landmarks": [],
        })
        mock_ai.generate_politics = AsyncMock(return_value={
            "governments": [],
            "factions": [],
        })
        mock_ai.generate_culture = AsyncMock(return_value={
            "religions": [],
            "traditions": [],
        })
        mock_ai.generate_history = AsyncMock(return_value={
            "eras": [],
            "major_events": [],
        })
        mock_ai.generate_magic_system = AsyncMock(return_value=MagicSystem(
            name="元素魔法",
            system_type="magic",
            rules=["元素共鸣"],
            limitations=["体力消耗"],
            levels=["初级", "中级", "高级"],
        ))
        mock_ai.generate_social_structure = AsyncMock(return_value=SocialStructure(
            classes=[],
            factions=[],
            power_distribution={},
        ))

        builder = WorldBuilder(mock_ai)

        world = await builder.build_world("玄幻", "修仙之旅")

        assert world.name == "测试玄幻世界"
        assert world.genre == "玄幻"
        assert world.magic_system is not None
        assert world.magic_system.name == "元素魔法"
        assert world.magic_system.system_type == "magic"


class TestWorldBuilderExpansion:
    """Tests for WorldBuilder expansion methods."""

    @pytest.mark.asyncio
    async def test_expand_geography(self):
        """Test expanding world geography."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [{"name": "扩展大陆"}],
            "countries": [],
            "cities": [],
            "landmarks": [],
        })

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(name="测试", genre="玄幻", geography={})

        expanded = await builder.expand_world(world, "geography")

        assert expanded.geography is not None
        mock_ai.generate_geography.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_politics(self):
        """Test expanding world politics."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_politics = AsyncMock(return_value={
            "governments": [{"name": "扩展政府"}],
            "factions": [],
        })

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(name="测试", genre="玄幻", politics={})

        expanded = await builder.expand_world(world, "politics")

        assert expanded.politics is not None
        mock_ai.generate_politics.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_culture(self):
        """Test expanding world culture."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_culture = AsyncMock(return_value={
            "religions": [{"name": "扩展宗教"}],
            "traditions": [],
        })

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(name="测试", genre="玄幻", culture={})

        expanded = await builder.expand_world(world, "culture")

        assert expanded.culture is not None
        mock_ai.generate_culture.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_history(self):
        """Test expanding world history."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_history = AsyncMock(return_value={
            "eras": [{"name": "扩展时代"}],
            "major_events": [],
        })

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(name="测试", genre="玄幻", history={})

        expanded = await builder.expand_world(world, "history")

        assert expanded.history is not None
        mock_ai.generate_history.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_magic_system_creates_new(self):
        """Test expanding magic system creates new if none exists."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_magic_system = AsyncMock(return_value=MagicSystem(
            name="新魔法",
            system_type="magic",
            rules=[],
            limitations=[],
            levels=[],
        ))

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={},
            politics={},
            culture={},
            magic_system=None,
        )

        expanded = await builder.expand_world(world, "magic")

        assert expanded.magic_system is not None
        assert expanded.magic_system.name == "新魔法"
        mock_ai.generate_magic_system.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_magic_system_updates_existing(self):
        """Test expanding magic system updates existing."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.expand_magic_system = AsyncMock(return_value={
            "name": "扩展魔法",
            "system_type": "magic",
            "rules": ["新规则"],
            "limitations": [],
            "levels": [],
        })

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={},
            politics={},
            culture={},
            magic_system=MagicSystem(
                name="原魔法",
                system_type="magic",
                rules=["原规则"],
                limitations=[],
                levels=[],
            ),
        )

        expanded = await builder.expand_world(world, "magic")

        assert expanded.magic_system is not None
        assert expanded.magic_system.name == "扩展魔法"
        mock_ai.expand_magic_system.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_social(self):
        """Test expanding social structure."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_social_structure = AsyncMock(return_value=SocialStructure(
            classes=[{"name": "贵族"}],
            factions=[],
            power_distribution={},
        ))

        builder = WorldBuilder(mock_ai)
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            social_structure=None,
        )

        expanded = await builder.expand_world(world, "social")

        assert expanded.social_structure is not None
        mock_ai.generate_social_structure.assert_called_once()


class TestAIServiceWorldMethods:
    """Tests for AI service world generation methods."""

    @pytest.mark.asyncio
    async def test_generate_geography(self):
        """Test geography generation method exists and returns dict."""
        from chai.services import AIService
        import os

        # Create a real AIService with a mock client
        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                # Mock the client response
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"continents": [], "countries": [], "cities": [], "landmarks": []}')]
                ))

                result = await ai_service.generate_geography("玄幻", "修仙")

                assert isinstance(result, dict)
                assert "continents" in result
                assert "countries" in result
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.asyncio
    async def test_generate_politics(self):
        """Test politics generation method exists and returns dict."""
        from chai.services import AIService
        import os

        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"governments": [], "factions": [], "alliances": [], "conflicts": []}')]
                ))

                result = await ai_service.generate_politics("玄幻", "修仙")

                assert isinstance(result, dict)
                assert "governments" in result
                assert "factions" in result
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.asyncio
    async def test_generate_culture(self):
        """Test culture generation method exists and returns dict."""
        from chai.services import AIService
        import os

        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"religions": [], "traditions": [], "languages": []}')]
                ))

                result = await ai_service.generate_culture("玄幻", "修仙")

                assert isinstance(result, dict)
                assert "religions" in result
                assert "traditions" in result
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.asyncio
    async def test_generate_history(self):
        """Test history generation method exists and returns dict."""
        from chai.services import AIService
        import os

        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"eras": [], "major_events": [], "historical_figures": []}')]
                ))

                result = await ai_service.generate_history("玄幻", "修仙")

                assert isinstance(result, dict)
                assert "eras" in result
                assert "major_events" in result
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.asyncio
    async def test_generate_magic_system(self):
        """Test magic system generation returns MagicSystem object."""
        from chai.services import AIService
        import os

        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"name": "元素魔法", "system_type": "magic", "rules": ["规则1"], "limitations": ["限制1"], "levels": ["初级"]}')]
                ))

                result = await ai_service.generate_magic_system("玄幻", "修仙")

                assert isinstance(result, MagicSystem)
                assert result.name == "元素魔法"
                assert result.system_type == "magic"
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.asyncio
    async def test_generate_social_structure(self):
        """Test social structure generation returns SocialStructure object."""
        from chai.services import AIService
        import os

        with patch("anthropic.Anthropic"):
            original_key = os.environ.get("ANTHROPIC_API_KEY")
            os.environ["ANTHROPIC_API_KEY"] = "test-key"
            try:
                ai_service = AIService()
                ai_service.client = MagicMock()
                ai_service.client.messages.create = MagicMock(return_value=MagicMock(
                    content=[MagicMock(text='{"classes": [{"name": "贵族"}], "factions": [], "power_distribution": {}}')]
                ))

                result = await ai_service.generate_social_structure("玄幻", "修仙")

                assert isinstance(result, SocialStructure)
                assert len(result.classes) == 1
                assert result.classes[0]["name"] == "贵族"
            finally:
                if original_key:
                    os.environ["ANTHROPIC_API_KEY"] = original_key
                else:
                    os.environ.pop("ANTHROPIC_API_KEY", None)


class TestWorldSystem:
    """Tests for WorldSystem class."""

    def test_world_system_init(self):
        """Test WorldSystem initialization."""
        world = WorldSetting(
            name="测试世界",
            genre="玄幻",
            geography={"countries": [{"name": "王国A"}]},
            politics={"governments": [{"name": "王国A政府"}]},
            culture={"religions": [{"name": "圣光教"}]},
            history={"eras": [{"name": "第一纪元"}]},
        )
        system = WorldSystem(world)

        assert system.world == world
        assert system._relationships == {}

    def test_analyze_relationships(self):
        """Test relationship analysis."""
        world = WorldSetting(
            name="测试世界",
            genre="玄幻",
            geography={
                "countries": [{"name": "王国A"}, {"name": "王国B"}],
                "landmarks": [{"name": "圣山"}],
                "cities": [{"name": "首都"}],
            },
            politics={
                "governments": [{"name": "王国A政府"}],
                "factions": [{"name": "武士团"}],
                "conflicts": [{"name": "边境战争"}],
            },
            culture={
                "religions": [{"name": "圣光教"}],
                "traditions": [{"name": "成年礼"}],
            },
            history={
                "eras": [{"name": "第一纪元"}],
                "major_events": [{"name": "建国"}],
            },
        )
        system = WorldSystem(world)
        relationships = system.analyze_relationships()

        assert "geography_politics" in relationships
        assert "politics_culture" in relationships
        assert "culture_history" in relationships
        assert "history_geography" in relationships
        assert "cross_influences" in relationships

        # Verify geo-politics analysis
        geo_pol = relationships["geography_politics"]
        assert geo_pol["country_count"] == 2
        assert geo_pol["government_count"] == 1
        assert geo_pol["territorial_claims"] == 1

    def test_analyze_geo_politics(self):
        """Test geography-politics relationship analysis."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={"countries": [{"name": "A"}], "landmarks": []},
            politics={"governments": [{"name": "Gov1"}], "factions": [], "conflicts": []},
            culture={},
            history={},
        )
        system = WorldSystem(world)
        result = system._analyze_geo_politics()

        assert result["country_count"] == 1
        assert result["government_count"] == 1
        assert "Geography shapes political" in result["influence"]

    def test_analyze_politics_culture(self):
        """Test politics-culture relationship analysis."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={},
            politics={"factions": [{"name": "F1"}], "governments": []},
            culture={"religions": [{"name": "R1"}], "traditions": []},
            history={},
        )
        system = WorldSystem(world)
        result = system._analyze_politics_culture()

        assert result["faction_count"] == 1
        assert result["religion_count"] == 1
        assert "Political power" in result["influence"]

    def test_get_cross_influences(self):
        """Test cross-influences retrieval."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={},
            politics={},
            culture={},
            history={},
        )
        system = WorldSystem(world)
        influences = system._get_cross_influences()

        assert "geography → politics" in influences
        assert "politics → culture" in influences
        assert "culture → history" in influences
        assert "history → geography" in influences

    def test_get_consistency_report_empty_world(self):
        """Test consistency report for minimal world."""
        world = WorldSetting(name="测试", genre="玄幻")
        system = WorldSystem(world)
        report = system.get_consistency_report()

        assert "issues" in report
        assert "recommendations" in report
        assert "status" in report

    def test_get_consistency_report_with_mismatches(self):
        """Test consistency report detects mismatches."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={"countries": [{"name": "A"}, {"name": "B"}, {"name": "C"}]},
            politics={"governments": [{"name": "Gov1"}]},
            culture={"religions": []},
            history={"eras": [], "major_events": [{"name": "E1"}, {"name": "E2"}]},
        )
        system = WorldSystem(world)
        report = system.get_consistency_report()

        # Should have issues about country/government mismatch
        assert len(report["issues"]) > 0
        assert any("Mismatch" in issue for issue in report["issues"])

    def test_get_consistency_report_good_world(self):
        """Test consistency report for well-structured world."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={
                "countries": [{"name": "A"}],
                "landmarks": [{"name": "L1"}, {"name": "L2"}, {"name": "L3"}],
                "cities": [{"name": "C1"}, {"name": "C2"}, {"name": "C3"}],
            },
            politics={"governments": [{"name": "Gov1"}], "factions": []},
            culture={"religions": [{"name": "R1"}], "traditions": []},
            history={"eras": [{"name": "E1"}], "major_events": [{"name": "E1"}, {"name": "E2"}, {"name": "E3"}]},
        )
        system = WorldSystem(world)
        report = system.get_consistency_report()

        assert report["status"] == "consistent"
        assert len(report["issues"]) == 0


class TestWorldBuilderCore:
    """Tests for WorldBuilder core world building methods."""

    @pytest.mark.asyncio
    async def test_build_core_world(self):
        """Test building core world without magic/social."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试核心世界",
            "genre": "都市",
        })
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [{"name": "亚洲"}],
            "countries": [{"name": "中国"}],
            "cities": [],
            "landmarks": [],
        })
        mock_ai.generate_politics = AsyncMock(return_value={
            "governments": [{"name": "政府"}],
            "factions": [],
        })
        mock_ai.generate_culture = AsyncMock(return_value={
            "religions": [],
            "traditions": [],
        })
        mock_ai.generate_history = AsyncMock(return_value={
            "eras": [],
            "major_events": [],
        })

        builder = WorldBuilder(mock_ai)
        world = await builder.build_core_world("都市", "现代都市")

        assert world.name == "测试核心世界"
        assert world.genre == "都市"
        assert world.magic_system is None
        assert world.social_structure is None
        assert world.geography is not None
        assert world.politics is not None
        assert world.culture is not None
        assert world.history is not None

    @pytest.mark.asyncio
    async def test_build_core_world_references_components(self):
        """Test that core world builds components with cross-references."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={"name": "测试", "genre": "都市"})
        mock_ai.generate_geography = AsyncMock(return_value={"countries": []})
        mock_ai.generate_politics = AsyncMock(return_value={"governments": []})
        mock_ai.generate_culture = AsyncMock(return_value={"religions": []})
        mock_ai.generate_history = AsyncMock(return_value={"eras": []})

        builder = WorldBuilder(mock_ai)
        await builder.build_core_world("都市", "现代")

        # Verify politics gets geography context
        mock_ai.generate_politics.assert_called_once()
        call_kwargs = mock_ai.generate_politics.call_args[1]
        assert "geography" in call_kwargs

        # Verify culture gets geography and politics context
        mock_ai.generate_culture.assert_called_once()
        call_kwargs = mock_ai.generate_culture.call_args[1]
        assert "geography" in call_kwargs
        assert "politics" in call_kwargs

        # Verify history gets all context
        mock_ai.generate_history.assert_called_once()
        call_kwargs = mock_ai.generate_history.call_args[1]
        assert "geography" in call_kwargs
        assert "politics" in call_kwargs
        assert "culture" in call_kwargs


class TestWorldBuilderSystem:
    """Tests for WorldBuilder system methods."""

    def test_build_world_system(self):
        """Test building world system."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={"countries": []},
            politics={"governments": []},
            culture={"religions": []},
            history={"eras": []},
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        system = builder.build_world_system(world)

        assert isinstance(system, WorldSystem)
        assert system.world == world
        assert len(system._relationships) > 0

    @pytest.mark.asyncio
    async def test_build_complete_world_system(self):
        """Test building complete world and system."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={"name": "完整世界", "genre": "玄幻"})
        mock_ai.generate_geography = AsyncMock(return_value={"continents": []})
        mock_ai.generate_politics = AsyncMock(return_value={"governments": []})
        mock_ai.generate_culture = AsyncMock(return_value={"religions": []})
        mock_ai.generate_history = AsyncMock(return_value={"eras": []})
        mock_ai.generate_magic_system = AsyncMock(return_value=MagicSystem(
            name="Test", system_type="magic", rules=[], limitations=[], levels=[]
        ))
        mock_ai.generate_social_structure = AsyncMock(return_value=SocialStructure(
            classes=[], factions=[], power_distribution={}
        ))

        builder = WorldBuilder(mock_ai)
        world, system = await builder.build_complete_world_system("玄幻", "奇幻")

        assert isinstance(world, WorldSetting)
        assert isinstance(system, WorldSystem)
        assert system.world == world


class TestWorldBuilderValidation:
    """Tests for WorldBuilder validation methods."""

    def test_validate_world_consistency(self):
        """Test world consistency validation."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={
                "countries": [{"name": "A"}, {"name": "B"}],
                "landmarks": [{"name": "L1"}],
                "cities": [{"name": "C1"}],
            },
            politics={"governments": [{"name": "Gov1"}], "factions": []},
            culture={"religions": [], "traditions": []},
            history={"eras": [], "major_events": []},
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        report = builder.validate_world_consistency(world)

        assert "issues" in report
        assert "recommendations" in report
        assert "status" in report

    def test_validate_good_world(self):
        """Test validation of well-structured world."""
        world = WorldSetting(
            name="测试",
            genre="玄幻",
            geography={
                "countries": [{"name": "A"}],
                "landmarks": [{"name": "L1"}, {"name": "L2"}, {"name": "L3"}],
                "cities": [{"name": "C1"}, {"name": "C2"}, {"name": "C3"}],
            },
            politics={"governments": [{"name": "Gov1"}], "factions": []},
            culture={"religions": [{"name": "R1"}], "traditions": []},
            history={"eras": [{"name": "E1"}], "major_events": [{"name": "E1"}, {"name": "E2"}, {"name": "E3"}]},
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        report = builder.validate_world_consistency(world)

        assert report["status"] == "consistent"


class TestWorldBuilderSummary:
    """Tests for WorldBuilder summary and export methods."""

    def test_get_world_summary(self):
        """Test getting world summary."""
        world = WorldSetting(
            name="测试世界",
            genre="玄幻",
            geography={
                "continents": [{"name": "大陆A"}],
                "countries": [{"name": "王国A"}, {"name": "王国B"}],
                "cities": [{"name": "首都"}],
                "landmarks": [{"name": "圣山"}],
            },
            politics={
                "governments": [{"name": "王国A政府"}],
                "factions": [{"name": "武士团"}],
                "conflicts": [],
            },
            culture={
                "religions": [{"name": "圣光教"}],
                "traditions": [{"name": "成年礼"}],
                "languages": [{"name": "通用语"}],
            },
            history={
                "eras": [{"name": "第一纪元"}],
                "major_events": [{"name": "建国"}],
                "historical_figures": [{"name": "始祖"}],
            },
            magic_system=MagicSystem(
                name="元素魔法",
                system_type="magic",
                rules=["规则1"],
                limitations=["限制1"],
                levels=["初级"],
            ),
            social_structure=SocialStructure(
                classes=[{"name": "贵族"}],
                factions=[{"name": "议会"}],
                power_distribution={},
            ),
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        summary = builder.get_world_summary(world)

        assert "测试世界" in summary
        assert "玄幻" in summary
        assert "大陆A" in summary
        assert "王国A" in summary
        assert "圣光教" in summary
        assert "第一纪元" in summary
        assert "元素魔法" in summary

    def test_get_world_summary_empty_world(self):
        """Test getting summary for empty world."""
        world = WorldSetting(name="空世界", genre="玄幻")
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        summary = builder.get_world_summary(world)

        assert "空世界" in summary
        assert "(未设定)" in summary

    def test_export_world_system(self):
        """Test exporting world system."""
        world = WorldSetting(
            name="导出世界",
            genre="玄幻",
            geography={"countries": []},
            politics={"governments": []},
            culture={"religions": []},
            history={"eras": []},
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        export = builder.export_world_system(world)

        assert "world" in export
        assert "summary" in export
        assert "relationships" in export
        assert "consistency" in export
        assert export["world"]["name"] == "导出世界"

    def test_export_world_system_without_relationships(self):
        """Test exporting world without relationships."""
        world = WorldSetting(
            name="导出世界",
            genre="玄幻",
            geography={},
            politics={},
            culture={},
            history={},
        )
        mock_ai = MagicMock(spec=AIService)
        builder = WorldBuilder(mock_ai)

        export = builder.export_world_system(world, include_relationships=False)

        assert "world" in export
        assert "summary" in export
        assert "relationships" not in export
        assert "consistency" not in export
