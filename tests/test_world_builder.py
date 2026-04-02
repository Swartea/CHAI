"""Tests for WorldBuilder engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import WorldSetting, MagicSystem, SocialStructure
from chai.engines import WorldBuilder
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
