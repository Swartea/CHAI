"""Tests for AntagonistEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.antagonist import (
    Antagonist,
    AntagonistProfile,
    AntagonistSystem,
    AntagonistType,
    AntagonistAppearance,
    AntagonistPersonality,
    AntagonistBackground,
    AntagonistMotivation,
    AntagonistRelationship,
    AntagonistPower,
    AntagonistOrganization,
    AntagonistArc,
    AntagonistConflict,
    AntagonistTactics,
)
from chai.models import Character, CharacterRole
from chai.engines.antagonist_engine import AntagonistEngine
from chai.services import AIService


class TestAntagonistModel:
    """Tests for Antagonist model."""

    def test_antagonist_basic_fields(self):
        """Test Antagonist with basic fields."""
        char = Antagonist(
            id="antagonist_001",
            name="黑魔王",
            antagonist_type=AntagonistType.BIG_BAD,
        )
        assert char.id == "antagonist_001"
        assert char.name == "黑魔王"
        assert char.antagonist_type == AntagonistType.BIG_BAD
        assert char.status == "active"

    def test_antagonist_with_appearance(self):
        """Test Antagonist with detailed appearance."""
        char = Antagonist(
            id="antagonist_002",
            name="暗影刺客",
            antagonist_type=AntagonistType.VILLAIN,
            age="35岁",
            age_numeric=35,
            appearance=AntagonistAppearance(
                face="冷酷的面具脸",
                eyes="血红双眸",
                hair="漆黑长发",
                body="修长精干",
                skin="苍白如骨",
                dressing="黑色夜行衣",
                accessories=["致命毒针"],
                overall="让人不寒而栗的存在",
            ),
            distinguishing_features=["左眼伤疤"],
            presence="压迫感十足",
            first_impression="不可信任的危险人物",
        )
        assert char.age == "35岁"
        assert char.appearance.eyes == "血红双眸"
        assert char.presence == "压迫感十足"

    def test_antagonist_with_personality(self):
        """Test Antagonist with detailed personality."""
        char = Antagonist(
            id="antagonist_003",
            name="疯狂科学家",
            antagonist_type=AntagonistType.MANIPULATOR,
            personality=AntagonistPersonality(
                core_traits=["冷酷", "计算精密", "自恋"],
                personality_description="极端理性，为达目的不择手段",
                mbti="INTJ",
                moral_alignment="绝对邪恶",
                values=["完美", "控制"],
                fears=["失败", "失控"],
                desires=["终极权力", "完美实验"],
                strengths=["超高智商", "资源丰富"],
                weaknesses=["过度自信", "低估情感"],
                habits=["把玩实验仪器"],
                emotional_pattern="情绪波动时更加危险",
            ),
        )
        assert char.personality.mbti == "INTJ"
        assert "冷酷" in char.personality.core_traits
        assert char.personality.moral_alignment == "绝对邪恶"

    def test_antagonist_with_background(self):
        """Test Antagonist with detailed background."""
        char = Antagonist(
            id="antagonist_004",
            name="堕落贵族",
            antagonist_type=AntagonistType.CORRUPTED,
            background=AntagonistBackground(
                origin="皇室血脉",
                family_background="没落贵族",
                education="皇家学院全优",
                previous_occupations=["宫廷医师", "首席顾问"],
                key_experiences=["被陷害失去一切"],
                downfall_moments=["家人的背叛"],
                socioeconomic_status="曾经的顶层贵族",
            ),
            backstory="曾是被寄予厚望的天才，因阴谋而堕入黑暗",
            origin_story="被最信任的人陷害后觉醒黑暗力量",
        )
        assert char.background.origin == "皇室血脉"
        assert "被陷害失去一切" in char.background.key_experiences

    def test_antagonist_with_motivation(self):
        """Test Antagonist with motivation."""
        char = Antagonist(
            id="antagonist_005",
            name="复仇者",
            antagonist_type=AntagonistType.REVENGE_SEEKER,
            motivation=AntagonistMotivation(
                surface_motivation="毁灭帝国",
                deep_motivation="复仇的渴望吞噬了一切",
                motivation_type="revenge",
                motivation_origin="全家被灭门",
                justification="这是他们应得的",
                twisted_logic="以正义之名行毁灭之实",
                personal_goals=["找到幕后黑手"],
                what_they_lost="家人、名誉、一切",
            ),
        )
        assert char.motivation.surface_motivation == "毁灭帝国"
        assert char.motivation.justification == "这是他们应得的"
        assert char.motivation.what_they_lost == "家人、名誉、一切"

    def test_antagonist_with_relationship(self):
        """Test Antagonist with protagonist relationship."""
        char = Antagonist(
            id="antagonist_006",
            name="黑暗双胞胎",
            antagonist_type=AntagonistType.SHADOW,
            relationship_to_protagonist=AntagonistRelationship(
                protagonist_id="prot_001",
                protagonist_name="光明骑士",
                relationship_type="镜像对立",
                relationship_dynamics="同样的出身，不同的选择",
                history="曾经是挚友，因理念不合分道扬镳",
                current_status="不共戴天",
                key_conflicts=["拯救还是毁灭", "方法之争"],
                mirrors_protagonist=True,
                symmetry_points=["同样的力量", "相反的信念"],
            ),
        )
        assert char.relationship_to_protagonist.mirrors_protagonist is True
        assert "拯救还是毁灭" in char.relationship_to_protagonist.key_conflicts

    def test_antagonist_with_power(self):
        """Test Antagonist with power/abilities."""
        char = Antagonist(
            id="antagonist_007",
            name="黑暗领主",
            antagonist_type=AntagonistType.TYRANT,
            power=AntagonistPower(
                power_source="古老黑暗魔法",
                power_type="暗影系魔法",
                combat_abilities=["暗影剑术", "黑暗领域"],
                social_abilities=["政治操控", "舆论控制"],
                intellectual_abilities=["战略大师", "千年智慧"],
                special_abilities=["召唤亡灵军团", "心灵控制"],
                weaknesses=["光明魔法", "真挚情感"],
                power_limitations="满月时力量减弱",
            ),
        )
        assert char.power.power_source == "古老黑暗魔法"
        assert "暗影剑术" in char.power.combat_abilities
        assert "光明魔法" in char.power.weaknesses

    def test_antagonist_with_organization(self):
        """Test Antagonist with organization."""
        char = Antagonist(
            id="antagonist_008",
            name="教廷首领",
            antagonist_type=AntagonistType.IDEOLOGICAL,
            organization=AntagonistOrganization(
                organization_name="黑暗教廷",
                organization_type="宗教组织",
                size="数万人",
                structure="严格的等级制度",
                key_members=["三大主教", "审判长"],
                resources=["圣地财富", "信徒忠诚"],
                territories=["黑暗圣地", "多个王国"],
                power_base="信仰控制",
            ),
        )
        assert char.organization.organization_name == "黑暗教廷"
        assert char.organization.size == "数万人"

    def test_antagonist_with_tactics(self):
        """Test Antagonist with tactics."""
        char = Antagonist(
            id="antagonist_009",
            name="阴谋家",
            antagonist_type=AntagonistType.MANIPULATOR,
            tactics=AntagonistTactics(
                preferred_methods=["暗中操控", "借刀杀人"],
                manipulation_tactics=["信息控制", "利益诱惑"],
                combat_style="避免正面交锋",
                social_strategy="分化瓦解",
                deception_patterns=["真假难辨的情报"],
                response_to_defeat="立即撤退保存实力",
            ),
        )
        assert "暗中操控" in char.tactics.preferred_methods
        assert char.tactics.combat_style == "避免正面交锋"

    def test_antagonist_with_arc(self):
        """Test Antagonist with character arc."""
        char = Antagonist(
            id="antagonist_010",
            name="悲剧反派",
            antagonist_type=AntagonistType.TRAGIC_ANTAGONIST,
            character_arc=AntagonistArc(
                archetype="悲剧英雄",
                arc_type="堕落弧线",
                starting_state="理想主义的改革者",
                ending_state="被权力腐蚀的暴君",
                corruption_arc="从追求正义到不择手段",
                redemption_potential="可能被主角救赎",
                transformation="失去初心",
                impact_on_protagonist="成为主角的反面教材",
            ),
        )
        assert char.character_arc.arc_type == "堕落弧线"
        assert char.character_arc.redemption_potential == "可能被主角救赎"

    def test_antagonist_with_conflict(self):
        """Test Antagonist with conflicts."""
        char = Antagonist(
            id="antagonist_011",
            name="战争领主",
            antagonist_type=AntagonistType.VILLAIN,
            conflicts=[
                AntagonistConflict(
                    conflict_type="external",
                    description="与主角阵营的全面战争",
                    against_protagonist=["争夺霸权", "意识形态对立"],
                    internal_conflict="对权力的渴望vs对友谊的怀念",
                    external_conflicts=["其他势力的威胁"],
                    stakes="整个世界的归属",
                    potential_resolution="一方彻底失败",
                )
            ],
        )
        assert len(char.conflicts) == 1
        assert char.conflicts[0].stakes == "整个世界的归属"


class TestAntagonistProfile:
    """Tests for AntagonistProfile model."""

    def test_profile_creation(self):
        """Test creating a profile from antagonist."""
        char = Antagonist(
            id="ant_001",
            name="测试反派",
            antagonist_type=AntagonistType.VILLAIN,
            appearance=AntagonistAppearance(
                face="冷酷",
                eyes="锐利",
                hair="黑色",
                body="高大",
                skin="苍白",
                dressing="黑袍",
                accessories=[],
                overall="可怕",
            ),
            personality=AntagonistPersonality(
                core_traits=["邪恶"],
                personality_description="极度危险",
                mbti="INTJ",
            ),
        )
        engine = AntagonistEngine(MagicMock())
        profile = engine.create_profile(char)

        assert profile.basic_info["name"] == "测试反派"


class TestAntagonistEngine:
    """Tests for AntagonistEngine methods."""

    def test_to_character_conversion(self):
        """Test converting Antagonist to base Character."""
        mock_ai = MagicMock(spec=AIService)
        engine = AntagonistEngine(mock_ai)

        antagonist = Antagonist(
            id="ant_001",
            name="测试反派",
            antagonist_type=AntagonistType.BIG_BAD,
            age="40岁",
            age_numeric=40,
            presence="压迫感",
            personality_description="极度危险",
            backstory="黑暗的过去",
            motivation=AntagonistMotivation(
                surface_motivation="统治世界",
                deep_motivation="证明自己",
            ),
            speech_pattern="威严冷酷",
            narrative_function="主要威胁",
            threat_level="catastrophic",
        )

        char = engine.to_character(antagonist)

        assert char.id == "ant_001"
        assert char.name == "测试反派"
        assert char.role == CharacterRole.ANTAGONIST
        assert char.age == "40岁"

    def test_get_antagonist_summary(self):
        """Test getting antagonist summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = AntagonistEngine(mock_ai)

        antagonist = Antagonist(
            id="ant_001",
            name="黑暗帝王",
            antagonist_type=AntagonistType.BIG_BAD,
            age="未知",
            threat_level="catastrophic",
            description="统治整个大陆的暴君",
            presence="令人窒息的压迫感",
            first_impression="不可战胜的存在",
            appearance=AntagonistAppearance(
                face="冷峻",
                eyes="血红",
                hair="苍白",
                body="魁梧",
                skin="灰白",
                dressing="漆黑铠甲",
                accessories=["皇冠"],
                overall="恐怖的化身",
            ),
            personality=AntagonistPersonality(
                core_traits=["冷酷", "权欲"],
                personality_description="极端冷酷的统治者",
                moral_alignment="绝对邪恶",
            ),
            backstory="千年前统一大陆的皇帝",
            motivation=AntagonistMotivation(
                surface_motivation="永恒的统治",
                deep_motivation="对死亡的恐惧",
                justification="只有我能拯救这个世界",
            ),
            relationship_to_protagonist=AntagonistRelationship(
                relationship_type="天敌",
                key_conflicts=["生存之战"],
                mirrors_protagonist=True,
            ),
            power=AntagonistPower(
                power_source="千年修为",
                power_type="暗黑力量",
                combat_abilities=["无敌剑法"],
                weaknesses=["勇气"],
            ),
            vulnerability="对主角家人的执念",
            catchphrases=["跪下或者死亡"],
            narrative_function="终极考验",
            status="active",
        )

        summary = engine.get_antagonist_summary(antagonist)

        assert "黑暗帝王" in summary
        assert "big_bad" in summary
        assert "catastrophic" in summary
        assert "跪下或者死亡" in summary

    def test_validate_antagonist_missing_info(self):
        """Test validation with incomplete antagonist."""
        mock_ai = MagicMock(spec=AIService)
        engine = AntagonistEngine(mock_ai)

        antagonist = Antagonist(
            id="ant_001",
            name="测试",
            antagonist_type=AntagonistType.VILLAIN,
        )

        result = engine.validate_antagonist(antagonist)

        # Minimal antagonist with only name and type has no critical issues (only warnings)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    def test_validate_antagonist_complete(self):
        """Test validation with complete antagonist."""
        mock_ai = MagicMock(spec=AIService)
        engine = AntagonistEngine(mock_ai)

        antagonist = Antagonist(
            id="ant_001",
            name="完整反派",
            antagonist_type=AntagonistType.VILLAIN,
            backstory="完整背景",
            motivation=AntagonistMotivation(
                surface_motivation="统治世界",
                deep_motivation="证明自己",
            ),
            relationship_to_protagonist=AntagonistRelationship(
                relationship_type="敌对",
            ),
            power=AntagonistPower(
                power_source="黑暗力量",
                power_type="暗黑",
                weaknesses=["光明"],
            ),
            threat_level="high",
            vulnerability="家人",
            defeat_conditions=["主角觉醒"],
        )

        result = engine.validate_antagonist(antagonist)

        assert result["valid"] is True

    def test_export_antagonist(self):
        """Test exporting antagonist."""
        mock_ai = MagicMock(spec=AIService)
        engine = AntagonistEngine(mock_ai)

        antagonist = Antagonist(
            id="ant_001",
            name="导出测试",
            antagonist_type=AntagonistType.VILLAIN,
            backstory="测试背景",
        )

        export = engine.export_antagonist(antagonist, include_profile=True)

        assert "antagonist" in export
        assert "profile" in export
        assert "summary" in export
        assert export["antagonist"]["name"] == "导出测试"


class TestAntagonistType:
    """Tests for AntagonistType enum."""

    def test_all_antagonist_types_exist(self):
        """Test all antagonist types are defined."""
        assert AntagonistType.VILLAIN.value == "villain"
        assert AntagonistType.DARK_HERO.value == "dark_hero"
        assert AntagonistType.TEMPORARY_ANTAGONIST.value == "temporary_antagonist"
        assert AntagonistType.ETERNAL_RIVAL.value == "eternal_rival"
        assert AntagonistType.TYRANT.value == "tyrant"
        assert AntagonistType.MANIPULATOR.value == "manipulator"
        assert AntagonistType.REVENGE_SEEKER.value == "revenge_seeker"
        assert AntagonistType.CORRUPTED.value == "corrupted"
        assert AntagonistType.IDEOLOGICAL.value == "ideological"
        assert AntagonistType.TRAGIC_ANTAGONIST.value == "tragic_antagonist"
        assert AntagonistType.MINION.value == "minion"
        assert AntagonistType.BIG_BAD.value == "big_bad"
        assert AntagonistType.TEMPTER.value == "tempter"
        assert AntagonistType.SHADOW.value == "shadow"
        assert AntagonistType.NEMESIS.value == "nemesis"


class TestAntagonistPower:
    """Tests for AntagonistPower model."""

    def test_power_fields(self):
        """Test power model fields."""
        power = AntagonistPower(
            power_source="龙族血脉",
            power_type="火焰魔法",
            combat_abilities=["龙息", "利爪"],
            social_abilities=["威压"],
            intellectual_abilities=["千年智慧"],
            special_abilities=["变身巨龙"],
            weaknesses=["冷水"],
            power_limitations="愤怒时失控",
        )
        assert power.power_source == "龙族血脉"
        assert "龙息" in power.combat_abilities
        assert power.power_limitations == "愤怒时失控"


class TestAntagonistTactics:
    """Tests for AntagonistTactics model."""

    def test_tactics_fields(self):
        """Test tactics model fields."""
        tactics = AntagonistTactics(
            preferred_methods=["暗杀", "阴谋"],
            manipulation_tactics=["谎言", "欺骗"],
            combat_style="一击脱离",
            social_strategy="分而治之",
            deception_patterns=["双重身份"],
            response_to_defeat="战略转移",
        )
        assert tactics.combat_style == "一击脱离"
        assert tactics.response_to_defeat == "战略转移"


class TestAntagonistConflict:
    """Tests for AntagonistConflict model."""

    def test_conflict_fields(self):
        """Test conflict model fields."""
        conflict = AntagonistConflict(
            conflict_type="external",
            description="毁灭王国",
            against_protagonist=["争夺王位"],
            internal_conflict="对权力的渴望vs对亲人的爱",
            external_conflicts=["其他王国入侵"],
            stakes="整个大陆的命运",
            potential_resolution="通过一场决战解决",
        )
        assert conflict.conflict_type == "external"
        assert conflict.stakes == "整个大陆的命运"


class TestAntagonistSystem:
    """Tests for AntagonistSystem model."""

    def test_antagonist_system_fields(self):
        """Test antagonist system model fields."""
        system = AntagonistSystem(
            name="黑暗帝国反派体系",
            protagonist_id="prot_001",
            primary_antagonist=Antagonist(
                id="ant_001",
                name="黑暗帝王",
                antagonist_type=AntagonistType.BIG_BAD,
            ),
            secondary_antagonists=[
                Antagonist(
                    id="ant_002",
                    name="黑暗将军",
                    antagonist_type=AntagonistType.VILLAIN,
                ),
            ],
            minion_types=["骷髅兵", "暗黑法师"],
            organization_templates=[{"name": "黑暗军团", "type": "军事"}],
            conflict_potential="从局部冲突到全面战争",
        )
        assert system.name == "黑暗帝国反派体系"
        assert system.primary_antagonist.name == "黑暗帝王"
        assert len(system.secondary_antagonists) == 1
