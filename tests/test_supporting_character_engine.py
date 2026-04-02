"""Tests for SupportingCharacterEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.supporting_character import (
    SupportingCharacter,
    SupportingCharacterProfile,
    SupportingCharacterSystem,
    SupportingArchetype,
    SupportingRoleType,
    SupportingCharacterAppearance,
    SupportingCharacterPersonality,
    SupportingCharacterBackground,
    SupportingCharacterMotivation,
    SupportingCharacterRelationship,
    SupportingCharacterArc,
    SupportingCharacterSkill,
    SupportingCharacterConflict,
)
from chai.models import Character, CharacterRole
from chai.engines.supporting_character_engine import SupportingCharacterEngine
from chai.services import AIService


class TestSupportingCharacterModel:
    """Tests for SupportingCharacter model."""

    def test_supporting_character_basic_fields(self):
        """Test SupportingCharacter with basic fields."""
        char = SupportingCharacter(
            id="supporting_001",
            name="导师张",
            supporting_role_type=SupportingRoleType.MENTOR,
        )
        assert char.id == "supporting_001"
        assert char.name == "导师张"
        assert char.supporting_role_type == SupportingRoleType.MENTOR
        assert char.status == "active"

    def test_supporting_character_with_appearance(self):
        """Test SupportingCharacter with detailed appearance."""
        char = SupportingCharacter(
            id="supporting_002",
            name="智者李",
            supporting_role_type=SupportingRoleType.WISDOM_KEEPER,
            age="60岁",
            age_numeric=60,
            appearance=SupportingCharacterAppearance(
                face="慈祥的面容",
                eyes="深邃的智慧眼眸",
                hair="花白的长发",
                body="消瘦但矍铄",
                skin="布满皱纹",
                dressing="素色长袍",
                accessories=["玉佩"],
                overall="一看就是饱学之士",
            ),
            distinguishing_features=["左手残疾"],
            presence="温和而威严",
        )
        assert char.age == "60岁"
        assert char.age_numeric == 60
        assert char.appearance.face == "慈祥的面容"
        assert char.appearance.eyes == "深邃的智慧眼眸"
        assert char.presence == "温和而威严"

    def test_supporting_character_with_personality(self):
        """Test SupportingCharacter with detailed personality."""
        char = SupportingCharacter(
            id="supporting_003",
            name="战友王",
            supporting_role_type=SupportingRoleType.SIDEKICK,
            personality=SupportingCharacterPersonality(
                core_traits=["忠诚", "勇敢", "幽默"],
                personality_description="性格开朗，是主角最好的朋友",
                mbti="ESFP",
                values=["友情", "义气"],
                fears=["失去主角这个朋友"],
                desires=["证明自己的价值"],
                strengths=["战斗技巧", "人际交往"],
                weaknesses=["冲动", "容易相信人"],
                habits=["紧张时吹口哨"],
                emotional_pattern="面对危险时反而更加兴奋",
            ),
        )
        assert char.personality.mbti == "ESFP"
        assert "忠诚" in char.personality.core_traits
        assert char.personality.fears == ["失去主角这个朋友"]

    def test_supporting_character_with_background(self):
        """Test SupportingCharacter with detailed background."""
        char = SupportingCharacter(
            id="supporting_004",
            name="盟友赵",
            supporting_role_type=SupportingRoleType.ALLY,
            background=SupportingCharacterBackground(
                origin="边境小镇",
                family_background="商人家庭",
                education="私塾教育",
                previous_occupations=["商人", "情报贩子"],
                key_experiences=["战争流离失所"],
                formative_events=["被主角所救"],
                socioeconomic_status="中等收入",
            ),
            backstory="战乱中与主角相遇，一见如故",
        )
        assert char.background.origin == "边境小镇"
        assert char.background.socioeconomic_status == "中等收入"
        assert "商人" in char.background.previous_occupations

    def test_supporting_character_with_motivation(self):
        """Test SupportingCharacter with motivation."""
        char = SupportingCharacter(
            id="supporting_005",
            name="爱人孙",
            supporting_role_type=SupportingRoleType.LOVE_INTEREST,
            motivation=SupportingCharacterMotivation(
                surface_motivation="帮助主角成功",
                deep_motivation="与主角在一起",
                motivation_type="love",
                motivation_source="被主角的品质吸引",
                motivation_for_allying="共同的目标和理想",
                personal_goals=["建立家庭", "平静生活"],
                conflicts_with_protagonist=["对未来的分歧"],
            ),
        )
        assert char.motivation.motivation_for_allying == "共同的目标和理想"
        assert "建立家庭" in char.motivation.personal_goals

    def test_supporting_character_with_relationship(self):
        """Test SupportingCharacter with protagonist relationship."""
        char = SupportingCharacter(
            id="supporting_006",
            name="学徒周",
            supporting_role_type=SupportingRoleType.MENTEE,
            relationship_to_protagonist=SupportingCharacterRelationship(
                protagonist_id="prot_001",
                protagonist_name="主角吴",
                relationship_type="师徒",
                relationship_dynamics="徒弟崇拜师父，师父视如己出",
                relationship_history="战场上救下濒死的主角",
                current_status="亦师亦友",
                key_events=["救命之恩", "传授武艺"],
                support_functions=["协助战斗", "照顾生活"],
                future_potential="可能超越师父",
            ),
        )
        assert char.relationship_to_protagonist.relationship_type == "师徒"
        assert char.relationship_to_protagonist.protagonist_name == "主角吴"

    def test_supporting_character_with_arc(self):
        """Test SupportingCharacter with character arc."""
        char = SupportingCharacter(
            id="supporting_007",
            name="喜剧人郑",
            supporting_role_type=SupportingRoleType.COMIC_RELIEF,
            character_arc=SupportingCharacterArc(
                archetype="小丑",
                growth_arc="从只为搞笑到理解人生真谛",
                starting_state="用搞笑掩饰内心痛苦",
                ending_state="学会正视情感",
                transformation="不再逃避内心",
                lessons_learned=["幽默不能解决一切"],
                impact_on_story="缓解紧张气氛，也带来反思",
            ),
        )
        assert char.character_arc.growth_arc == "从只为搞笑到理解人生真谛"
        assert char.character_arc.archetype == "小丑"


class TestSupportingCharacterProfile:
    """Tests for SupportingCharacterProfile model."""

    def test_profile_creation(self):
        """Test creating a profile from supporting character."""
        char = SupportingCharacter(
            id="support_001",
            name="测试配角",
            supporting_role_type=SupportingRoleType.ALLY,
            appearance=SupportingCharacterAppearance(
                face="普通",
                eyes="明亮",
                hair="黑色",
                body="中等",
                skin="健康",
                dressing="朴素",
                accessories=[],
                overall="平凡",
            ),
            personality=SupportingCharacterPersonality(
                core_traits=["友善"],
                personality_description="性格友善",
                mbti="ENFP",
                values=["善良"],
                fears=[],
                desires=[],
                strengths=[],
                weaknesses=[],
                habits=[],
            ),
        )
        engine = SupportingCharacterEngine(MagicMock())
        profile = engine.create_profile(char)

        assert profile.basic_info["name"] == "测试配角"
        assert profile.appearance.face == "普通"


class TestSupportingCharacterEngine:
    """Tests for SupportingCharacterEngine methods."""

    def test_to_character_conversion(self):
        """Test converting SupportingCharacter to base Character."""
        mock_ai = MagicMock(spec=AIService)
        engine = SupportingCharacterEngine(mock_ai)

        supporting = SupportingCharacter(
            id="support_001",
            name="测试配角",
            supporting_role_type=SupportingRoleType.MENTOR,
            age="50岁",
            age_numeric=50,
            presence="威严",
            personality_description="严格的导师",
            backstory="曾是名将",
            speech_pattern="简洁有力",
            narrative_function="指导主角成长",
        )

        char = engine.to_character(supporting)

        assert char.id == "support_001"
        assert char.name == "测试配角"
        assert char.role == CharacterRole.SUPPORTING
        assert char.age == "50岁"

    def test_get_supporting_character_summary(self):
        """Test getting supporting character summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = SupportingCharacterEngine(mock_ai)

        supporting = SupportingCharacter(
            id="support_001",
            name="导师张",
            supporting_role_type=SupportingRoleType.MENTOR,
            age="60岁",
            description="主角的导师",
            presence="温和而威严",
            appearance=SupportingCharacterAppearance(
                face="饱经沧桑",
                eyes="锐利",
                hair="花白",
                body="消瘦",
                skin="皱纹",
                dressing="素袍",
                accessories=["玉佩"],
                overall="不凡",
            ),
            personality=SupportingCharacterPersonality(
                core_traits=["智慧", "冷静"],
                personality_description="睿智而冷静的战略家",
                mbti="INTJ",
            ),
            backstory="曾是帝国将军",
            motivation=SupportingCharacterMotivation(
                motivation_for_allying="看到主角的潜力",
            ),
            relationship_to_protagonist=SupportingCharacterRelationship(
                relationship_type="师徒",
                relationship_dynamics="教导与学习",
                support_functions=["传授武艺", "指引方向"],
            ),
            character_arc=SupportingCharacterArc(
                growth_arc="见证徒弟的成长",
                starting_state="严厉",
                ending_state="欣慰",
            ),
            catchphrases=["记住这个教训"],
            narrative_function="推动主角成长",
            status="active",
        )

        summary = engine.get_supporting_character_summary(supporting)

        assert "导师张" in summary
        assert "mentor" in summary
        assert "60岁" in summary
        assert "师徒" in summary
        assert "记住这个教训" in summary

    def test_validate_supporting_character_missing_info(self):
        """Test validation with incomplete supporting character."""
        mock_ai = MagicMock(spec=AIService)
        engine = SupportingCharacterEngine(mock_ai)

        supporting = SupportingCharacter(
            id="support_001",
            name="测试",
            supporting_role_type=SupportingRoleType.ALLY,
        )

        result = engine.validate_supporting_character(supporting)

        # Minimal supporting character with only name and type has no critical issues (only warnings)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert "背景故事" in str(result["warnings"])

    def test_validate_supporting_character_complete(self):
        """Test validation with complete supporting character."""
        mock_ai = MagicMock(spec=AIService)
        engine = SupportingCharacterEngine(mock_ai)

        supporting = SupportingCharacter(
            id="support_001",
            name="完整配角",
            supporting_role_type=SupportingRoleType.ALLY,
            backstory="完整背景故事",
            motivation=SupportingCharacterMotivation(
                motivation_for_allying="共同理想",
            ),
            relationship_to_protagonist=SupportingCharacterRelationship(
                relationship_type="盟友",
            ),
            character_arc=SupportingCharacterArc(
                growth_arc="成长弧线",
            ),
            catchphrases=["加油"],
        )

        result = engine.validate_supporting_character(supporting)

        assert result["valid"] is True

    def test_export_supporting_character(self):
        """Test exporting supporting character."""
        mock_ai = MagicMock(spec=AIService)
        engine = SupportingCharacterEngine(mock_ai)

        supporting = SupportingCharacter(
            id="support_001",
            name="导出测试",
            supporting_role_type=SupportingRoleType.SIDEKICK,
            backstory="测试背景",
        )

        export = engine.export_supporting_character(supporting, include_profile=True)

        assert "supporting_character" in export
        assert "profile" in export
        assert "summary" in export
        assert export["supporting_character"]["name"] == "导出测试"


class TestSupportingRoleType:
    """Tests for SupportingRoleType enum."""

    def test_all_role_types_exist(self):
        """Test all role types are defined."""
        assert SupportingRoleType.MENTOR.value == "mentor"
        assert SupportingRoleType.SIDEKICK.value == "sidekick"
        assert SupportingRoleType.BEST_FRIEND.value == "best_friend"
        assert SupportingRoleType.LOVE_INTEREST.value == "love_interest"
        assert SupportingRoleType.MENTEE.value == "mentee"
        assert SupportingRoleType.ALLY.value == "ally"
        assert SupportingRoleType.CONTACT.value == "contact"
        assert SupportingRoleType.EXPERT.value == "expert"
        assert SupportingRoleType.COMIC_RELIEF.value == "comic_relief"
        assert SupportingRoleType.WISDOM_KEEPER.value == "wisdom_keeper"
        assert SupportingRoleType.FOIL.value == "foil"
        assert SupportingRoleType.FALLEN_ALLY.value == "fallen_ally"
        assert SupportingRoleType.RETIRED_HERO.value == "retired_hero"
        assert SupportingRoleType.INFORMANT.value == "informant"


class TestSupportingCharacterSkill:
    """Tests for SupportingCharacterSkill model."""

    def test_skill_fields(self):
        """Test skill model fields."""
        skill = SupportingCharacterSkill(
            name="剑术",
            description="精湛的剑法",
            category="combat",
            proficiency_level="master",
            source="多年苦练",
            usefulness_to_protagonist="保护主角",
        )
        assert skill.name == "剑术"
        assert skill.category == "combat"
        assert skill.proficiency_level == "master"
        assert skill.usefulness_to_protagonist == "保护主角"


class TestSupportingCharacterConflict:
    """Tests for SupportingCharacterConflict model."""

    def test_conflict_fields(self):
        """Test conflict model fields."""
        conflict = SupportingCharacterConflict(
            conflict_type="external",
            description="与反派的冲突",
            parties_involved=["配角", "反派"],
            cause="立场不同",
            stakes="生死",
            resolution="和解",
        )
        assert conflict.conflict_type == "external"
        assert conflict.stakes == "生死"
