"""Tests for SocialSystemEngine and enhanced SocialStructure model."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import (
    SocialStructure,
    SocialClass,
    Faction,
    FactionRelationship,
    Guild,
    CriminalOrganization,
    ReligiousInstitution,
    SecretSociety,
    SocialConflict,
)
from chai.engines import SocialSystemEngine, SocialSystemBuilder, WorldBuilder
from chai.services import AIService


class TestSocialStructureModel:
    """Tests for enhanced SocialStructure model."""

    def test_social_structure_basic_fields(self):
        """Test SocialStructure with basic fields."""
        ss = SocialStructure(
            classes=[],
            factions=[],
            power_distribution={},
        )
        assert len(ss.classes) == 0
        assert len(ss.factions) == 0
        assert len(ss.power_distribution) == 0

    def test_social_structure_extended_fields(self):
        """Test SocialStructure with all extended fields."""
        ss = SocialStructure(
            classes=[
                {
                    "name": "贵族",
                    "description": "高高在上的统治阶层",
                    "typical_members": ["皇室成员", "大领主"],
                    "lifestyle": "奢华",
                    "rights": ["免税", "司法特权"],
                    "obligations": ["服兵役", "缴纳贡金"],
                    "relationship_with_other_classes": [
                        {"class": "平民", "type": "ruling", "description": "统治关系"}
                    ],
                    "economic_base": "土地所有",
                    "political_influence": 9,
                    "population_percentage": "5%",
                }
            ],
            social_mobility="较低",
            family_structures=["核心家庭", "大家庭"],
            wealth_distribution="极度不均",
            factions=[
                {
                    "name": "皇室家族",
                    "faction_type": "royal",
                    "description": "王权象征",
                    "leader": "国王",
                    "power_level": 10,
                    "territories": ["王都"],
                }
            ],
            guilds=[
                {
                    "name": "商人公会",
                    "profession": "商业",
                    "description": "控制贸易",
                }
            ],
            criminal_organizations=[
                {
                    "name": "黑帮",
                    "description": "地下势力",
                    "illegal_activities": ["走私", "赌博"],
                }
            ],
            religious_institutions=[
                {
                    "name": "圣殿教廷",
                    "deity_or_belief": "光明神",
                    "description": "国教",
                }
            ],
            secret_societies=[
                {
                    "name": "暗影兄弟会",
                    "description": "隐秘组织",
                    "secrecy_level": "极高",
                }
            ],
            faction_relationships=[
                {
                    "faction_a": "皇室家族",
                    "faction_b": "商人公会",
                    "relationship_type": "alliance",
                    "description": "政治同盟",
                    "current_status": "stable",
                }
            ],
            power_distribution={
                "military": "皇室掌控",
                "economic": "贵族与商人共有",
            },
            economic_system={
                "type": "封建制",
                "major_industries": ["农业", "手工业"],
            },
            social_conflicts=[
                {
                    "name": "阶级冲突",
                    "parties_involved": ["贵族", "平民"],
                    "current_status": "brewing",
                }
            ],
            conflict_lines=["贫富差距", "阶级对立"],
            social_norms=["尊敬长辈", "服从权威"],
            taboos=["弑君", "叛国"],
            regional_variations=[
                {
                    "region": "北方",
                    "class_structure": "更严格的等级制度",
                }
            ],
        )
        assert len(ss.classes) == 1
        assert ss.classes[0]["name"] == "贵族"
        assert len(ss.factions) == 1
        assert ss.factions[0]["name"] == "皇室家族"
        assert len(ss.guilds) == 1
        assert ss.guilds[0]["name"] == "商人公会"
        assert len(ss.criminal_organizations) == 1
        assert len(ss.religious_institutions) == 1
        assert len(ss.secret_societies) == 1
        assert len(ss.faction_relationships) == 1
        assert len(ss.social_conflicts) == 1
        assert len(ss.conflict_lines) == 2
        assert len(ss.social_norms) == 2
        assert len(ss.taboos) == 2
        assert len(ss.regional_variations) == 1
        assert ss.social_mobility == "较低"
        assert ss.economic_system["type"] == "封建制"

    def test_social_class_model(self):
        """Test SocialClass model."""
        sc = SocialClass(
            name="贵族",
            description="统治阶层",
            typical_members=["领主"],
            lifestyle="奢华",
            rights=["免税"],
            obligations=["服役"],
            relationship_with_other_classes=[],
            economic_base="土地",
            political_influence=8,
            population_percentage="5%",
        )
        assert sc.name == "贵族"
        assert sc.political_influence == 8

    def test_faction_model(self):
        """Test Faction model."""
        f = Faction(
            name="皇家骑士团",
            faction_type="military",
            description="王室卫队",
            leader="骑士团长",
            leadership_structure="世袭制",
            internal_hierarchy=["团长", "副团长", "骑士"],
            membership="500人",
            recruitment="选拔",
            membership_requirements=["剑术精通"],
            goals=["保卫王室"],
            ideology="忠君爱国",
            values=["荣誉", "忠诚"],
            resources=["武器装备", "军饷"],
            power_level=8,
            military_strength="精锐骑兵",
            economic_power="王室财政支持",
            political_alignment="绝对忠诚王室",
            territories=["王都"],
            headquarters="王城宫殿",
            symbol="双头鹰",
            founding_story="开国时建立",
            founding_date="建国元年",
            historical_events=[],
            allies=["贵族联盟"],
            rivals=["佣兵公会"],
            enemies=["叛军"],
            notable_members=[],
            current_status="巅峰",
            current_goals=["镇压叛乱"],
        )
        assert f.name == "皇家骑士团"
        assert f.faction_type == "military"
        assert f.power_level == 8
        assert len(f.allies) == 1


class TestSocialSystemBuilder:
    """Tests for SocialSystemBuilder."""

    def test_social_system_builder_init(self):
        """Test SocialSystemBuilder initialization."""
        mock_ai = MagicMock(spec=AIService)
        builder = SocialSystemBuilder(mock_ai)
        assert builder._engine is not None

    @pytest.mark.asyncio
    async def test_social_system_builder_build(self):
        """Test building social system via builder."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value='{"classes": [], "factions": [], "guilds": [], "criminal_organizations": [], "religious_institutions": [], "secret_societies": [], "faction_relationships": [], "power_distribution": {}, "economic_system": {}, "social_conflicts": [], "conflict_lines": [], "social_norms": [], "taboos": [], "regional_variations": []}')
        mock_ai._parse_json = MagicMock(return_value={
            "classes": [],
            "factions": [],
            "guilds": [],
            "criminal_organizations": [],
            "religious_institutions": [],
            "secret_societies": [],
            "faction_relationships": [],
            "power_distribution": {},
            "economic_system": {},
            "social_conflicts": [],
            "conflict_lines": [],
            "social_norms": [],
            "taboos": [],
            "regional_variations": [],
        })

        builder = SocialSystemBuilder(mock_ai)
        result = await builder.build(
            genre="玄幻",
            theme="修仙",
        )

        assert isinstance(result, SocialStructure)
        mock_ai.generate.assert_called_once()

    def test_social_system_builder_analyze(self):
        """Test analyzing social structure via builder."""
        mock_ai = MagicMock(spec=AIService)
        builder = SocialSystemBuilder(mock_ai)

        ss = SocialStructure(
            classes=[{"name": "贵族"}],
            factions=[{"name": "皇室"}],
            power_distribution={},
        )
        result = builder.analyze(ss)

        assert "issues" in result
        assert "recommendations" in result
        assert "status" in result
        assert "stats" in result

    def test_social_system_builder_summarize(self):
        """Test summarizing social structure via builder."""
        mock_ai = MagicMock(spec=AIService)
        builder = SocialSystemBuilder(mock_ai)

        ss = SocialStructure(
            classes=[{"name": "贵族", "political_influence": 8}],
            factions=[{"name": "皇室", "faction_type": "royal", "power_level": 10}],
            power_distribution={},
        )
        result = builder.summarize(ss)

        assert isinstance(result, str)
        assert "贵族" in result
        assert "皇室" in result


class TestSocialSystemEngine:
    """Tests for SocialSystemEngine."""

    def test_social_system_engine_init(self):
        """Test SocialSystemEngine initialization."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)
        assert engine.ai_service is not None

    @pytest.mark.asyncio
    async def test_build_social_system(self):
        """Test building a complete social system."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value='{"classes": [{"name": "贵族"}], "factions": [{"name": "皇室"}], "guilds": [], "criminal_organizations": [], "religious_institutions": [], "secret_societies": [], "faction_relationships": [], "power_distribution": {}, "economic_system": {}, "social_conflicts": [], "conflict_lines": [], "social_norms": [], "taboos": [], "regional_variations": []}')
        mock_ai._parse_json = MagicMock(return_value={
            "classes": [{"name": "贵族"}],
            "factions": [{"name": "皇室"}],
            "guilds": [],
            "criminal_organizations": [],
            "religious_institutions": [],
            "secret_societies": [],
            "faction_relationships": [],
            "power_distribution": {},
            "economic_system": {},
            "social_conflicts": [],
            "conflict_lines": [],
            "social_norms": [],
            "taboos": [],
            "regional_variations": [],
        })

        engine = SocialSystemEngine(mock_ai)
        result = await engine.build_social_system(
            genre="玄幻",
            theme="修仙",
        )

        assert isinstance(result, SocialStructure)
        assert len(result.classes) == 1
        assert len(result.factions) == 1
        mock_ai.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_faction(self):
        """Test generating a single faction."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value='{"name": "测试公会", "faction_type": "guild", "description": "测试", "leader": "会长", "power_level": 5}')
        mock_ai._parse_json = MagicMock(return_value={
            "name": "测试公会",
            "faction_type": "guild",
            "description": "测试",
            "leader": "会长",
            "power_level": 5,
        })

        engine = SocialSystemEngine(mock_ai)
        result = await engine.generate_faction(
            faction_type="guild",
            genre="玄幻",
            theme="修仙",
        )

        assert isinstance(result, dict)
        assert result["name"] == "测试公会"
        assert result["faction_type"] == "guild"

    def test_analyze_faction_relationships(self):
        """Test analyzing faction relationships."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        factions = [
            {
                "name": "皇室",
                "allies": ["贵族"],
                "rivals": ["佣兵公会"],
                "enemies": ["叛军"],
            },
            {
                "name": "贵族",
                "allies": ["皇室"],
                "rivals": ["商人公会"],
            },
            {
                "name": "佣兵公会",
                "rivals": ["皇室"],
            },
            {
                "name": "叛军",
                "enemies": ["皇室"],
            },
        ]

        result = engine.analyze_faction_relationships(factions)

        assert isinstance(result, list)
        # Should have deduplicated relationships
        #皇室-贵族 (allies), 皇室-佣兵公会 (rivalry), 皇室-叛军 (hostile), 贵族-商人公会 (rivalry)
        assert len(result) >= 3

    def test_analyze_social_consistency(self):
        """Test social consistency analysis."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        # Test with insufficient factions
        ss = SocialStructure(
            classes=[{"name": "贵族"}],
            factions=[{"name": "皇室"}],
            guilds=[],
            criminal_organizations=[],
            religious_institutions=[],
            secret_societies=[],
            social_conflicts=[],
            power_distribution={},
            economic_system={},
        )

        result = engine.analyze_social_consistency(ss)

        assert "issues" in result
        assert "recommendations" in result
        assert "status" in result
        assert "stats" in result
        assert len(result["issues"]) > 0  # Should have issues about low faction count

    def test_analyze_social_consistency_good(self):
        """Test social consistency analysis with good structure."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        ss = SocialStructure(
            classes=[
                {"name": "贵族"},
                {"name": "平民"},
                {"name": "商人"},
            ],
            factions=[
                {"name": "皇室", "leader": "国王"},
                {"name": "贵族议会"},
                {"name": "商人公会"},
                {"name": "佣兵公会"},
            ],
            guilds=[],
            criminal_organizations=[],
            religious_institutions=[],
            secret_societies=[],
            social_conflicts=[{"name": "阶级矛盾"}],
            power_distribution={"military": "皇室掌控"},
            economic_system={"type": "封建制"},
        )

        result = engine.analyze_social_consistency(ss)

        assert result["status"] == "consistent"
        assert len(result["issues"]) == 0

    def test_get_social_summary(self):
        """Test getting social summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        ss = SocialStructure(
            classes=[
                {"name": "贵族", "political_influence": 9},
                {"name": "平民", "political_influence": 3},
            ],
            factions=[
                {"name": "皇室", "faction_type": "royal", "power_level": 10},
                {"name": "佣兵公会", "faction_type": "mercenary", "power_level": 6},
            ],
            guilds=[{"name": "商人公会"}],
            criminal_organizations=[],
            religious_institutions=[{"name": "圣殿"}],
            secret_societies=[],
            social_conflicts=[{"name": "阶级冲突", "current_status": "brewing"}],
            power_distribution={},
            economic_system={},
        )

        result = engine.get_social_summary(ss)

        assert isinstance(result, str)
        assert "贵族" in result
        assert "皇室" in result
        assert "佣兵公会" in result
        assert "社会阶层" in result
        assert "主要势力" in result

    def test_export_social_system(self):
        """Test exporting social system."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        ss = SocialStructure(
            classes=[{"name": "贵族"}],
            factions=[{"name": "皇室"}],
            power_distribution={},
        )

        result = engine.export_social_system(ss, include_analysis=True)

        assert "social_structure" in result
        assert "summary" in result
        assert "analysis" in result

    def test_export_social_system_without_analysis(self):
        """Test exporting social system without analysis."""
        mock_ai = MagicMock(spec=AIService)
        engine = SocialSystemEngine(mock_ai)

        ss = SocialStructure(
            classes=[{"name": "贵族"}],
            factions=[{"name": "皇室"}],
            power_distribution={},
        )

        result = engine.export_social_system(ss, include_analysis=False)

        assert "social_structure" in result
        assert "summary" in result
        assert "analysis" not in result


class TestWorldBuilderSocialIntegration:
    """Tests for WorldBuilder social structure integration."""

    @pytest.mark.asyncio
    async def test_build_world_with_social_system(self):
        """Test building world uses SocialSystemBuilder."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试世界",
            "genre": "玄幻",
        })
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [{"name": "大陆"}],
            "countries": [{"name": "王国"}],
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
        # Mock generate for SocialSystemEngine
        mock_ai.generate = AsyncMock(return_value='{"classes": [{"name": "贵族"}], "factions": [{"name": "皇室"}], "guilds": [], "criminal_organizations": [], "religious_institutions": [], "secret_societies": [], "faction_relationships": [], "power_distribution": {}, "economic_system": {}, "social_conflicts": [], "conflict_lines": [], "social_norms": [], "taboos": [], "regional_variations": []}')
        mock_ai._parse_json = MagicMock(return_value={
            "classes": [{"name": "贵族"}],
            "factions": [{"name": "皇室"}],
            "guilds": [],
            "criminal_organizations": [],
            "religious_institutions": [],
            "secret_societies": [],
            "faction_relationships": [],
            "power_distribution": {},
            "economic_system": {},
            "social_conflicts": [],
            "conflict_lines": [],
            "social_norms": [],
            "taboos": [],
            "regional_variations": [],
        })

        builder = WorldBuilder(mock_ai)
        world = await builder.build_world("都市", "现代都市")

        assert world.social_structure is not None
        assert isinstance(world.social_structure, SocialStructure)

    @pytest.mark.asyncio
    async def test_expand_world_social(self):
        """Test expanding world with social structure."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate_world_setting = AsyncMock(return_value={
            "name": "测试世界",
            "genre": "玄幻",
        })
        mock_ai.generate_geography = AsyncMock(return_value={
            "continents": [],
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
        mock_ai.generate = AsyncMock(return_value='{"classes": [{"name": "贵族"}], "factions": [{"name": "皇室"}], "guilds": [], "criminal_organizations": [], "religious_institutions": [], "secret_societies": [], "faction_relationships": [], "power_distribution": {}, "economic_system": {}, "social_conflicts": [], "conflict_lines": [], "social_norms": [], "taboos": [], "regional_variations": []}')
        mock_ai._parse_json = MagicMock(return_value={
            "classes": [{"name": "贵族"}],
            "factions": [{"name": "皇室"}],
            "guilds": [],
            "criminal_organizations": [],
            "religious_institutions": [],
            "secret_societies": [],
            "faction_relationships": [],
            "power_distribution": {},
            "economic_system": {},
            "social_conflicts": [],
            "conflict_lines": [],
            "social_norms": [],
            "taboos": [],
            "regional_variations": [],
        })

        builder = WorldBuilder(mock_ai)

        # Build initial world
        world = await builder.build_world("都市", "现代都市")
        assert world.social_structure is not None

        # Expand social structure
        mock_ai.generate = AsyncMock(return_value='[{"name": "新势力", "faction_type": "military", "description": "测试"}]')
        mock_ai._parse_json = MagicMock(return_value=[{"name": "新势力", "faction_type": "military", "description": "测试"}])

        expanded = await builder.expand_world(world, "social")
        assert expanded.social_structure is not None
