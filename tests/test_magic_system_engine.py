"""Tests for MagicSystemEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import MagicSystem, PowerTechnique, PowerConflict
from chai.engines import MagicSystemEngine
from chai.services import AIService


class TestMagicSystemModel:
    """Tests for enhanced MagicSystem model."""

    def test_magic_system_basic_fields(self):
        """Test MagicSystem with basic fields."""
        ms = MagicSystem(
            name="元素魔法",
            system_type="magic",
            rules=["元素共鸣"],
            limitations=["体力消耗"],
            levels=["初级", "中级", "高级"],
        )
        assert ms.name == "元素魔法"
        assert ms.system_type == "magic"
        assert len(ms.rules) == 1
        assert len(ms.limitations) == 1
        assert len(ms.levels) == 3

    def test_magic_system_extended_fields(self):
        """Test MagicSystem with extended fields."""
        ms = MagicSystem(
            name="元素魔法",
            system_type="magic",
            rules=["规则1", "规则2"],
            limitations=["限制1"],
            levels=["初级", "高级"],
            source_of_power="元素之力",
            power_origin_story="太古时代，元素结晶降世",
            schools_or_types=[
                {
                    "name": "火系",
                    "description": "操控火焰",
                    "typical_users": ["火系法师"],
                    "strengths": ["高攻击"],
                    "weaknesses": ["怕水"],
                }
            ],
            training_methods=[
                {
                    "name": "冥想",
                    "description": "通过冥想感受元素",
                    "requirements": ["灵根"],
                    "duration": "1年",
                    "effects": ["感知元素"],
                }
            ],
            artifacts=[
                {
                    "name": "火神杖",
                    "description": "蕴含火神之力",
                    "power_level": "传说",
                    "requirements": "火系法师",
                }
            ],
            organizations=[
                {
                    "name": "元素公会",
                    "type": "公会",
                    "leader": "会长",
                    "goals": ["保护元素平衡"],
                }
            ],
            weaknesses=["水系克星", "过度使用会反噬"],
            world_influence="影响了整个大陆的格局",
            social_acceptance="被大众接受",
            history=[
                {"era": "神话时代", "event": "元素降世", "impact": "开启了魔法纪元"}
            ],
            forbidden_techniques=[
                {
                    "name": "元素湮灭",
                    "description": "毁灭性禁术",
                    "original_purpose": "战争武器",
                    "consequences": "使用者会死亡",
                }
            ],
            associated_phenomena=["施法时有元素光芒"],
        )
        assert ms.source_of_power == "元素之力"
        assert ms.power_origin_story == "太古时代，元素结晶降世"
        assert len(ms.schools_or_types) == 1
        assert ms.schools_or_types[0]["name"] == "火系"
        assert len(ms.training_methods) == 1
        assert ms.training_methods[0]["name"] == "冥想"
        assert len(ms.artifacts) == 1
        assert ms.artifacts[0]["name"] == "火神杖"
        assert len(ms.organizations) == 1
        assert ms.organizations[0]["name"] == "元素公会"
        assert len(ms.weaknesses) == 2
        assert ms.world_influence == "影响了整个大陆的格局"
        assert len(ms.history) == 1
        assert ms.history[0]["era"] == "神话时代"
        assert len(ms.forbidden_techniques) == 1
        assert ms.forbidden_techniques[0]["name"] == "元素湮灭"
        assert len(ms.associated_phenomena) == 1


class TestPowerTechniqueModel:
    """Tests for PowerTechnique model."""

    def test_power_technique_basic(self):
        """Test PowerTechnique basic fields."""
        pt = PowerTechnique(
            name="火球术",
            description="召唤火球攻击敌人",
            school="火系",
            type="attack",
            power_level=5,
            mastery_level="intermediate",
            primary_effect="造成火属性伤害",
        )
        assert pt.name == "火球术"
        assert pt.type == "attack"
        assert pt.power_level == 5

    def test_power_technique_full(self):
        """Test PowerTechnique with all fields."""
        pt = PowerTechnique(
            name="冰封千里",
            description="大范围冰系攻击",
            school="冰系",
            type="attack",
            power_level=8,
            mastery_level="master",
            energy_cost="大量魔力",
            cooldown="1小时",
            conditions=["必须在冰系领域内"],
            primary_effect="冻结范围内一切",
            secondary_effects=["减速", "减防"],
            side_effects=["施法者也会感到寒冷"],
            countermeasures=["火系抵抗", "空间传送"],
            manifestation="周围温度骤降，出现冰晶",
        )
        assert pt.energy_cost == "大量魔力"
        assert pt.cooldown == "1小时"
        assert len(pt.conditions) == 1
        assert len(pt.side_effects) == 1
        assert len(pt.countermeasures) == 2


class TestPowerConflictModel:
    """Tests for PowerConflict model."""

    def test_power_conflict_basic(self):
        """Test PowerConflict basic fields."""
        pc = PowerConflict(
            name="元素战争",
            description="各元素系之间的争斗",
            parties_involved=["火系公会", "水系公会"],
            cause="争夺元素圣地",
            current_status="active",
            stakes="谁能控制元素圣地",
        )
        assert pc.name == "元素战争"
        assert len(pc.parties_involved) == 2
        assert pc.current_status == "active"

    def test_power_conflict_full(self):
        """Test PowerConflict with all fields."""
        pc = PowerConflict(
            name="王位争夺",
            description="围绕魔王的继承权",
            parties_involved=["暗影教", "圣光骑士团", "中立势力"],
            cause="魔王突然失踪",
            current_status="brewing",
            key_battles=[
                {"name": "第一次王位之战", "description": "大规模冲突", "result": "无胜者"}
            ],
            stakes="谁能成为新一代魔王",
            potential_resolution=["通过决斗决定", "和平谈判"],
        )
        assert len(pc.key_battles) == 1
        assert pc.stakes == "谁能成为新一代魔王"
        assert len(pc.potential_resolution) == 2


class TestMagicSystemEngine:
    """Tests for MagicSystemEngine."""

    def test_engine_init(self):
        """Test MagicSystemEngine initialization."""
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)
        assert engine.ai_service == mock_ai

    def test_analyze_system_consistency_complete(self):
        """Test analysis of complete magic system."""
        ms = MagicSystem(
            name="完整魔法",
            system_type="magic",
            rules=["规则1", "规则2", "规则3", "规则4", "规则5"],
            limitations=["限制1", "限制2", "限制3"],
            levels=["初级", "中级", "高级", "大师"],
            source_of_power="魔力源泉",
            schools_or_types=[
                {
                    "name": "学院派",
                    "description": "系统学习",
                    "strengths": ["扎实"],
                    "weaknesses": ["速度慢"],
                }
            ],
            training_methods=[{"name": "冥想", "description": "基础"}],
            artifacts=[{"name": "法杖", "description": "增幅"}],
            organizations=[{"name": "法师协会", "type": "协会"}],
            weaknesses=["弱点1"],
            world_influence="影响深远",
            history=[{"era": "古代", "event": "起源", "impact": "改变"}],
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.analyze_system_consistency(ms)

        assert "issues" in result
        assert "warnings" in result
        assert "suggestions" in result
        assert "status" in result
        assert "completeness_score" in result
        assert result["status"] == "consistent"

    def test_analyze_system_consistency_empty(self):
        """Test analysis of empty magic system."""
        ms = MagicSystem(
            name="空系统",
            system_type="magic",
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.analyze_system_consistency(ms)

        assert len(result["issues"]) > 0
        assert result["status"] == "needs_review"
        assert result["completeness_score"] < 0.5

    def test_analyze_system_consistency_missing_limitations(self):
        """Test analysis catches missing limitations."""
        ms = MagicSystem(
            name="不平衡系统",
            system_type="magic",
            rules=["规则1", "规则2", "规则3", "规则4", "规则5", "规则6"],
            limitations=[],  # No limitations - problematic!
            levels=["初级", "中级"],
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.analyze_system_consistency(ms)

        # Should have warning about missing limitations
        assert len(result["warnings"]) > 0
        assert any("限制" in w or "limitation" in w.lower() for w in result["warnings"])

    def test_validate_power_levels_valid(self):
        """Test power level validation for valid system."""
        ms = MagicSystem(
            name="测试",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级：入门", "中级：进阶", "高级：精英", "大师：巅峰"],
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.validate_power_levels(ms)

        assert result["valid"] is True
        assert result["level_count"] == 4

    def test_validate_power_levels_empty(self):
        """Test power level validation for empty levels."""
        ms = MagicSystem(
            name="测试",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=[],
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.validate_power_levels(ms)

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_power_levels_few_levels(self):
        """Test power level validation catches too few levels."""
        ms = MagicSystem(
            name="测试",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级"],  # Only one level
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        result = engine.validate_power_levels(ms)

        assert result["valid"] is False
        assert any("过少" in issue or "few" in issue.lower() for issue in result["issues"])

    def test_get_system_summary(self):
        """Test getting system summary."""
        ms = MagicSystem(
            name="元素魔法系统",
            system_type="magic",
            source_of_power="元素之力",
            rules=["规则1", "规则2"],
            limitations=["限制1"],
            levels=["初级", "高级"],
            schools_or_types=[
                {
                    "name": "火系",
                    "description": "操控火焰",
                    "strengths": ["高伤害"],
                    "weaknesses": [],
                }
            ],
            training_methods=[{"name": "冥想", "description": "基础修炼"}],
            organizations=[{"name": "元素公会", "type": "公会"}],
            artifacts=[{"name": "火神杖", "description": "神器"}],
            forbidden_techniques=[{"name": "禁术", "consequences": "死亡"}],
            weaknesses=["水克火"],
            world_influence="改变世界格局",
            social_acceptance="被社会接受",
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        summary = engine.get_system_summary(ms)

        assert "元素魔法系统" in summary
        assert "magic" in summary
        assert "元素之力" in summary
        assert "规则1" in summary
        assert "火系" in summary
        assert "元素公会" in summary

    def test_get_system_summary_minimal(self):
        """Test getting summary for minimal system."""
        ms = MagicSystem(
            name="最小系统",
            system_type="magic",
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        summary = engine.get_system_summary(ms)

        assert "最小系统" in summary
        assert "magic" in summary

    def test_export_power_system(self):
        """Test exporting power system."""
        ms = MagicSystem(
            name="导出系统",
            system_type="magic",
            rules=["规则1"],
            limitations=["限制1"],
            levels=["初级"],
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        export = engine.export_power_system(ms)

        assert "magic_system" in export
        assert "summary" in export
        assert "analysis" in export
        assert export["magic_system"]["name"] == "导出系统"

    def test_export_power_system_without_analysis(self):
        """Test exporting without analysis."""
        ms = MagicSystem(
            name="导出系统",
            system_type="magic",
        )
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        export = engine.export_power_system(ms, include_analysis=False)

        assert "magic_system" in export
        assert "summary" in export
        assert "analysis" not in export

    def test_calculate_completeness(self):
        """Test completeness score calculation."""
        mock_ai = MagicMock(spec=AIService)
        engine = MagicSystemEngine(mock_ai)

        # Empty system
        ms_empty = MagicSystem(name="空", system_type="magic")
        score = engine._calculate_completeness(ms_empty)
        assert score < 0.3

        # Complete system
        ms_complete = MagicSystem(
            name="完整",
            system_type="magic",
            source_of_power="源",
            rules=["r1", "r2", "r3", "r4", "r5"],
            limitations=["l1", "l2", "l3", "l4"],
            levels=["l1", "l2", "l3", "l4"],
            schools_or_types=[{"name": "s1"}, {"name": "s2"}, {"name": "s3"}],
            training_methods=[{"name": "t1"}],
            artifacts=[{"name": "a1"}],
            organizations=[{"name": "o1"}],
            weaknesses=["w1"],
            world_influence="inf",
            history=[{"era": "e1"}],
        )
        score = engine._calculate_completeness(ms_complete)
        assert score > 0.7


class TestMagicSystemEngineAsync:
    """Tests for async MagicSystemEngine methods."""

    @pytest.mark.asyncio
    async def test_build_power_system(self):
        """Test building a complete power system."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="""
        {
            "name": "测试系统",
            "system_type": "magic",
            "source_of_power": "测试之力",
            "power_origin_story": "起源故事",
            "rules": ["规则1", "规则2"],
            "limitations": ["限制1"],
            "levels": ["初级", "高级"],
            "schools_or_types": [],
            "training_methods": [],
            "typical_training_duration": "10年",
            "artifacts": [],
            "consumables": [],
            "organizations": [],
            "power_interactions": [],
            "weaknesses": [],
            "world_influence": "影响",
            "social_acceptance": "接受",
            "history": [],
            "forbidden_techniques": [],
            "associated_phenomena": []
        }
        """)
        mock_ai._parse_json = MagicMock(return_value={
            "name": "测试系统",
            "system_type": "magic",
            "source_of_power": "测试之力",
            "power_origin_story": "起源故事",
            "rules": ["规则1", "规则2"],
            "limitations": ["限制1"],
            "levels": ["初级", "高级"],
            "schools_or_types": [],
            "training_methods": [],
            "typical_training_duration": "10年",
            "artifacts": [],
            "consumables": [],
            "organizations": [],
            "power_interactions": [],
            "weaknesses": [],
            "world_influence": "影响",
            "social_acceptance": "接受",
            "history": [],
            "forbidden_techniques": [],
            "associated_phenomena": [],
        })

        engine = MagicSystemEngine(mock_ai)
        result = await engine.build_power_system("玄幻", "修仙", "magic")

        assert result.name == "测试系统"
        assert result.system_type == "magic"
        assert result.source_of_power == "测试之力"

    @pytest.mark.asyncio
    async def test_generate_technique(self):
        """Test generating a single technique."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="""
        {
            "name": "火球术",
            "description": "召唤火球攻击",
            "school": "火系",
            "type": "attack",
            "power_level": 5,
            "mastery_level": "intermediate",
            "energy_cost": "中等",
            "cooldown": "5秒",
            "conditions": ["需要火系天赋"],
            "primary_effect": "造成火焰伤害",
            "secondary_effects": ["点燃"],
            "side_effects": [],
            "countermeasures": ["水系防御"],
            "manifestation": "火球发射"
        }
        """)
        mock_ai._parse_json = MagicMock(return_value={
            "name": "火球术",
            "description": "召唤火球攻击",
            "school": "火系",
            "type": "attack",
            "power_level": 5,
            "mastery_level": "intermediate",
            "energy_cost": "中等",
            "cooldown": "5秒",
            "conditions": ["需要火系天赋"],
            "primary_effect": "造成火焰伤害",
            "secondary_effects": ["点燃"],
            "side_effects": [],
            "countermeasures": ["水系防御"],
            "manifestation": "火球发射",
        })

        ms = MagicSystem(
            name="元素魔法",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级", "高级"],
        )
        engine = MagicSystemEngine(mock_ai)
        result = await engine.generate_technique(ms, "attack", 5, "火系")

        assert result.name == "火球术"
        assert result.type == "attack"
        assert result.power_level == 5
        assert result.school == "火系"

    @pytest.mark.asyncio
    async def test_generate_techniques_batch(self):
        """Test batch technique generation."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="""
        [
            {"name": "技能1", "type": "attack", "power_level": 3, "mastery_level": "beginner"},
            {"name": "技能2", "type": "defense", "power_level": 4, "mastery_level": "intermediate"}
        ]
        """)
        mock_ai._parse_json_array = MagicMock(return_value=[
            {"name": "技能1", "type": "attack", "power_level": 3, "mastery_level": "beginner", "school": "", "description": "", "energy_cost": "", "cooldown": "", "conditions": [], "primary_effect": "", "secondary_effects": [], "side_effects": [], "countermeasures": [], "manifestation": ""},
            {"name": "技能2", "type": "defense", "power_level": 4, "mastery_level": "intermediate", "school": "", "description": "", "energy_cost": "", "cooldown": "", "conditions": [], "primary_effect": "", "secondary_effects": [], "side_effects": [], "countermeasures": [], "manifestation": ""},
        ])

        ms = MagicSystem(
            name="测试",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级", "高级"],
            schools_or_types=[{"name": "水系", "description": ""}],
        )
        engine = MagicSystemEngine(mock_ai)
        result = await engine.generate_techniques_batch(ms, 2)

        assert len(result) == 2
        assert result[0].name == "技能1"
        assert result[1].name == "技能2"

    @pytest.mark.asyncio
    async def test_create_system_conflict(self):
        """Test creating a system-based conflict."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value="""
        {
            "name": "派系战争",
            "description": "围绕魔法的争斗",
            "parties_involved": ["火系公会", "水系公会"],
            "cause": "争夺魔法圣地",
            "current_status": "active",
            "key_battles": [{"name": "圣地之战", "description": "决定性战役", "result": "火系胜"}],
            "stakes": "谁控制圣地",
            "potential_resolution": ["通过决斗", "和平谈判"]
        }
        """)
        mock_ai._parse_json = MagicMock(return_value={
            "name": "派系战争",
            "description": "围绕魔法的争斗",
            "parties_involved": ["火系公会", "水系公会"],
            "cause": "争夺魔法圣地",
            "current_status": "active",
            "key_battles": [{"name": "圣地之战", "description": "决定性战役", "result": "火系胜"}],
            "stakes": "谁控制圣地",
            "potential_resolution": ["通过决斗", "和平谈判"],
        })

        ms = MagicSystem(
            name="元素魔法",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级"],
        )
        engine = MagicSystemEngine(mock_ai)
        result = await engine.create_system_conflict(ms)

        assert result.name == "派系战争"
        assert len(result.parties_involved) == 2
        assert result.current_status == "active"


class TestPowerSystemBuilder:
    """Tests for PowerSystemBuilder helper."""

    def test_power_system_builder_init(self):
        """Test PowerSystemBuilder initialization."""
        from chai.engines.world_builder import PowerSystemBuilder

        mock_ai = MagicMock(spec=AIService)
        builder = PowerSystemBuilder(mock_ai)

        assert builder._engine.ai_service == mock_ai

    def test_power_system_builder_analyze(self):
        """Test PowerSystemBuilder analyze method."""
        from chai.engines.world_builder import PowerSystemBuilder

        mock_ai = MagicMock(spec=AIService)
        builder = PowerSystemBuilder(mock_ai)

        ms = MagicSystem(
            name="测试",
            system_type="magic",
            rules=["规则"],
            limitations=["限制"],
            levels=["初级"],
        )
        result = builder.analyze(ms)

        assert "issues" in result
        assert "completeness_score" in result

    def test_power_system_builder_summarize(self):
        """Test PowerSystemBuilder summarize method."""
        from chai.engines.world_builder import PowerSystemBuilder

        mock_ai = MagicMock(spec=AIService)
        builder = PowerSystemBuilder(mock_ai)

        ms = MagicSystem(
            name="测试魔法",
            system_type="magic",
            source_of_power="魔力",
        )
        result = builder.summarize(ms)

        assert "测试魔法" in result
        assert "魔力" in result
