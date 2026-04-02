"""Tests for MainCharacterEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.main_character import (
    MainCharacter,
    MainCharacterProfile,
    AppearanceDetail,
    PersonalityDimension,
    BackgroundDetail,
    MotivationDetail,
    MotivationType,
)
from chai.models import Character, CharacterRole
from chai.engines.main_character_engine import MainCharacterEngine
from chai.services import AIService


class TestMainCharacterModel:
    """Tests for MainCharacter model."""

    def test_main_character_basic_fields(self):
        """Test MainCharacter with basic fields."""
        char = MainCharacter(
            id="protagonist_001",
            name="张三",
        )
        assert char.id == "protagonist_001"
        assert char.name == "张三"
        assert char.status == "active"

    def test_main_character_with_appearance(self):
        """Test MainCharacter with detailed appearance."""
        char = MainCharacter(
            id="protagonist_002",
            name="李四",
            age="25岁",
            age_numeric=25,
            appearance_detail=AppearanceDetail(
                face="棱角分明的脸庞",
                eyes="深邃的黑色眼眸",
                hair="乌黑的短发",
                body="高大挺拔",
                skin="古铜色肌肤",
                dressing="简约黑色风衣",
                accessories=["银色项链"],
                overall="给人可靠稳重的感觉",
            ),
            distinguishing_features=["眉间疤痕"],
            presence="沉稳内敛",
            first_impression="神秘而可信",
        )
        assert char.age == "25岁"
        assert char.age_numeric == 25
        assert char.appearance_detail.face == "棱角分明的脸庞"
        assert char.appearance_detail.eyes == "深邃的黑色眼眸"
        assert "眉间疤痕" in char.distinguishing_features
        assert char.presence == "沉稳内敛"

    def test_main_character_with_personality(self):
        """Test MainCharacter with detailed personality."""
        char = MainCharacter(
            id="protagonist_003",
            name="王五",
            personality_dimension=PersonalityDimension(
                openness=7,
                conscientiousness=8,
                extraversion=5,
                agreeableness=6,
                neuroticism=4,
            ),
            personality_description="理性而冷静，善于分析问题",
            mbti="INTJ",
            values=["正义", "自由"],
            fears=["失去控制", "被背叛"],
            desires=["追求真相", "保护所爱之人"],
            strengths=["战略头脑", "超强意志力"],
            weaknesses=["过于固执", "不擅表达"],
            habits=["紧张时摸下巴"],
            emotional_pattern="愤怒时沉默，悲伤时独处",
        )
        assert char.personality_dimension.openness == 7
        assert char.mbti == "INTJ"
        assert "正义" in char.values
        assert len(char.fears) == 2
        assert char.emotional_pattern == "愤怒时沉默，悲伤时独处"

    def test_main_character_with_background(self):
        """Test MainCharacter with detailed background."""
        char = MainCharacter(
            id="protagonist_004",
            name="赵六",
            background_detail=BackgroundDetail(
                birth_place="北方小镇",
                birth_era="战乱年代",
                childhood="在山村中度过平静的童年",
                adolescence="被选中进入学院学习",
                early_adulthood="加入军队开始了军旅生涯",
                family_members=[
                    {"relation": "父亲", "name": "赵大", "description": "普通农夫"},
                ],
                socioeconomic_status="中下阶层出身",
                education_background="帝国学院毕业",
                career_path=["士兵", "军官"],
                key_events=["战争", "父亲的死"],
                turning_points=["被贵族收养"],
            ),
            backstory="出身平凡但志向远大",
            origin="北方边境",
            family_background="普通农户家庭",
            formative_experiences=["战争的洗礼", "父亲的牺牲"],
        )
        assert char.background_detail.birth_place == "北方小镇"
        assert char.background_detail.socioeconomic_status == "中下阶层出身"
        assert len(char.background_detail.family_members) == 1
        assert "战争" in char.background_detail.key_events

    def test_main_character_with_motivation(self):
        """Test MainCharacter with detailed motivation."""
        char = MainCharacter(
            id="protagonist_005",
            name="孙七",
            motivation_detail=MotivationDetail(
                surface_motivation="找到失踪的父亲",
                deep_motivation="证明自己的价值",
                motivation_type="discovery",
                motivation_source="父亲的教导",
                motivation_conflict="想要复仇但相信宽恕",
                driving_force="对真相的渴求",
                obstacles=["强大的敌人", "自身的软弱"],
                internal_conflict="追求力量与守护善良的矛盾",
                fear_core="失去自我",
                desire_core="被认可",
            ),
            motivation="找到父亲并证明自己",
            goal="成为最强的剑士",
            internal_conflict="复仇与宽恕之间的挣扎",
        )
        assert char.motivation_detail.surface_motivation == "找到失踪的父亲"
        assert char.motivation_detail.deep_motivation == "证明自己的价值"
        assert char.motivation_detail.motivation_type == "discovery"
        assert char.motivation == "找到父亲并证明自己"

    def test_main_character_with_arc(self):
        """Test MainCharacter with character arc."""
        char = MainCharacter(
            id="protagonist_006",
            name="周八",
            archetype="英雄",
            growth_arc="从自我怀疑到坚定信念",
            starting_state="胆小怕事，不敢面对挑战",
            ending_state="勇敢坚定，成为领袖",
            speech_pattern="沉稳有力，掷地有声",
            catchphrases=["我的剑，为守护而出鞘"],
            communication_style="直接明了",
            narrative_function="带领团队克服困难",
            thematic_significance="成长与救赎",
            character_arc_summary="从平凡到伟大的蜕变",
        )
        assert char.archetype == "英雄"
        assert char.growth_arc == "从自我怀疑到坚定信念"
        assert "我的剑，为守护而出鞘" in char.catchphrases


class TestMainCharacterProfile:
    """Tests for MainCharacterProfile model."""

    def test_profile_creation(self):
        """Test creating a profile from main character."""
        char = MainCharacter(
            id="prot_001",
            name="测试主角",
            appearance_detail=AppearanceDetail(
                face="英俊",
                eyes="明亮",
                hair="黑色",
                body="匀称",
                skin="白皙",
                dressing="整洁",
                accessories=[],
                overall="清爽",
            ),
            personality_dimension=PersonalityDimension(
                openness=6,
                conscientiousness=7,
                extraversion=5,
                agreeableness=6,
                neuroticism=4,
            ),
        )
        engine = MainCharacterEngine(MagicMock())
        profile = engine.create_profile(char)

        assert profile.basic_info["name"] == "测试主角"
        assert profile.appearance.face == "英俊"
        assert profile.personality.openness == 6


class TestMainCharacterEngine:
    """Tests for MainCharacterEngine methods."""

    def test_to_character_conversion(self):
        """Test converting MainCharacter to base Character."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="测试主角",
            age="25岁",
            age_numeric=25,
            presence="沉稳",
            personality_description="理性冷静",
            values=["正义"],
            fears=["失去"],
            desires=["成长"],
            strengths=["智慧"],
            weaknesses=["固执"],
            backstory="平凡出身",
            origin="南方",
            family_background="普通家庭",
            formative_experiences=["战争"],
            motivation="变得更强",
            goal="保护所爱之人",
            internal_conflict="内心的挣扎",
            archetype="英雄",
            growth_arc="成长弧线",
            starting_state="弱小",
            ending_state="强大",
            speech_pattern="沉稳",
            catchphrases=["口头禅"],
            communication_style="直接",
            narrative_function="主角",
            thematic_significance="成长",
            character_arc_summary="成长的故事",
            first_appearance="第一章",
            status="active",
        )

        char = engine.to_character(main_char)

        assert char.id == "prot_001"
        assert char.name == "测试主角"
        assert char.role == CharacterRole.PROTAGONIST
        assert char.age == "25岁"
        assert char.personality_description == "理性冷静"
        assert char.motivation == "变得更强"

    def test_get_main_character_summary(self):
        """Test getting main character summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="张三",
            age="30岁",
            mbti="INTJ",
            appearance_detail=AppearanceDetail(
                face="棱角分明",
                eyes="深邃",
                hair="短发",
                body="高大",
                skin="古铜",
                dressing="风衣",
                accessories=[],
                overall="威严",
            ),
            presence="沉稳内敛",
            distinguishing_features=["疤痕"],
            personality_dimension=PersonalityDimension(
                openness=7,
                conscientiousness=8,
                extraversion=5,
                agreeableness=6,
                neuroticism=4,
            ),
            personality_description="理性而冷静的战略家",
            values=["力量", "秩序"],
            fears=["失去控制"],
            desires=["真相"],
            strengths=["智慧"],
            weaknesses=["固执"],
            habits=["摸下巴"],
            emotional_pattern="愤怒时沉默",
            backstory="曾是将军，经历战火洗礼",
            background_detail=BackgroundDetail(
                birth_place="北方",
                birth_era="战乱",
                childhood="平静",
                adolescence="动荡",
                early_adulthood="军旅",
                family_members=[],
                socioeconomic_status="中上",
                education_background="军校",
                career_path=["士兵", "将军"],
                key_events=["战争"],
                turning_points=["父亲的死"],
            ),
            motivation="追求力量",
            goal="建立秩序",
            motivation_detail=MotivationDetail(
                surface_motivation="权力",
                deep_motivation="证明价值",
                motivation_type="power",
                motivation_source="童年阴影",
                motivation_conflict="力量vs人性",
                driving_force="恐惧",
                obstacles=["敌人"],
                internal_conflict="内心挣扎",
                fear_core="失去控制",
                desire_core="被认可",
            ),
            archetype="英雄",
            growth_arc="从追求力量到理解人性",
            starting_state="冷酷",
            ending_state="温情",
            speech_pattern="低沉有力",
            catchphrases=["力量即正义"],
            narrative_function="主角",
            thematic_significance="力量的代价",
        )

        summary = engine.get_main_character_summary(main_char)

        assert "张三" in summary
        assert "30岁" in summary
        assert "INTJ" in summary
        assert "棱角分明" in summary
        assert "理性而冷静的战略家" in summary
        assert "追求力量" in summary
        assert "力量即正义" in summary

    def test_validate_main_character_completeness_missing_appearance(self):
        """Test validation with incomplete appearance."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="测试",
            # Missing detailed appearance
        )

        result = engine.validate_main_character_completeness(main_char)

        assert result["valid"] is False
        assert len(result["issues"]) > 0
        assert "completeness_scores" in result
        assert "appearance" in result["completeness_scores"]
        assert result["completeness_scores"]["appearance"] < 0.5

    def test_validate_main_character_completeness_missing_personality(self):
        """Test validation with incomplete personality."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="测试",
            personality_description="",  # Missing
            mbti="",  # Missing
            values=[],  # Missing
            fears=[],  # Missing
            desires=[],  # Missing
        )

        result = engine.validate_main_character_completeness(main_char)

        assert result["valid"] is False
        assert "completeness_scores" in result
        assert result["completeness_scores"]["personality"] < 0.5

    def test_validate_main_character_completeness_missing_motivation(self):
        """Test validation with incomplete motivation."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="测试",
            motivation="",  # Missing
            goal="",  # Missing
        )

        result = engine.validate_main_character_completeness(main_char)

        assert result["valid"] is False
        assert "completeness_scores" in result
        assert result["completeness_scores"]["motivation"] < 0.5

    def test_validate_main_character_completeness_complete(self):
        """Test validation with complete character."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="完整主角",
            age="25岁",
            age_numeric=25,
            appearance_detail=AppearanceDetail(
                face="英俊",
                eyes="明亮",
                hair="黑色",
                body="匀称",
                skin="白皙",
                dressing="整洁",
                accessories=["项链"],
                overall="清爽",
            ),
            distinguishing_features=["疤痕"],
            presence="沉稳",
            personality_dimension=PersonalityDimension(
                openness=7,
                conscientiousness=8,
                extraversion=5,
                agreeableness=6,
                neuroticism=4,
            ),
            personality_description="理性冷静的战略家",
            mbti="INTJ",
            values=["正义", "自由"],
            fears=["失去", "背叛"],
            desires=["真相", "力量"],
            strengths=["智慧"],
            weaknesses=["固执"],
            habits=["思考"],
            background_detail=BackgroundDetail(
                birth_place="南方",
                birth_era="和平",
                childhood="幸福",
                adolescence="成长",
                early_adulthood="独立",
                family_members=[{"relation": "父", "name": "测试", "description": "温和"}],
                socioeconomic_status="中产",
                education_background="大学",
                career_path=["学习"],
                key_events=["毕业"],
                turning_points=["工作"],
            ),
            backstory="完整背景故事",
            motivation="完整动机",
            goal="完整目标",
            motivation_detail=MotivationDetail(
                surface_motivation="表层",
                deep_motivation="深层",
                motivation_type="growth",
                motivation_source="经历",
                motivation_conflict="矛盾",
                driving_force="动力",
                obstacles=["障碍"],
                internal_conflict="冲突",
                fear_core="恐惧",
                desire_core="欲望",
            ),
            growth_arc="成长弧线",
            starting_state="初始",
            ending_state="结局",
        )

        result = engine.validate_main_character_completeness(main_char)

        assert result["overall_completeness"] >= 0.7

    def test_export_main_character(self):
        """Test exporting main character."""
        mock_ai = MagicMock(spec=AIService)
        engine = MainCharacterEngine(mock_ai)

        main_char = MainCharacter(
            id="prot_001",
            name="导出测试",
            age="25岁",
            presence="沉稳",
            personality_description="理性",
            motivation="变得更强",
            goal="保护他人",
        )

        export = engine.export_main_character(main_char, include_analysis=True)

        assert "main_character" in export
        assert "profile" in export
        assert "summary" in export
        assert "analysis" in export
        assert export["main_character"]["name"] == "导出测试"


class TestAppearanceDetail:
    """Tests for AppearanceDetail model."""

    def test_appearance_detail_full(self):
        """Test full appearance detail."""
        app = AppearanceDetail(
            face="英俊的脸庞",
            eyes="深邃的蓝眸",
            hair="金色的长发",
            body="修长的身材",
            skin="白皙的肌肤",
            dressing="华丽的礼服",
            accessories=["戒指", "项链"],
            overall="如同画中走出的人物",
        )
        assert app.face == "英俊的脸庞"
        assert app.eyes == "深邃的蓝眸"
        assert len(app.accessories) == 2


class TestPersonalityDimension:
    """Tests for PersonalityDimension model."""

    def test_personality_dimension(self):
        """Test personality dimension."""
        pd = PersonalityDimension(
            openness=8,
            conscientiousness=7,
            extraversion=6,
            agreeableness=5,
            neuroticism=4,
        )
        assert pd.openness == 8
        assert pd.conscientiousness == 7
        assert pd.extraversion == 6


class TestBackgroundDetail:
    """Tests for BackgroundDetail model."""

    def test_background_detail_full(self):
        """Test full background detail."""
        bg = BackgroundDetail(
            birth_place="东方的岛屿",
            birth_era="魔法纪元",
            childhood="在海边小镇度过",
            adolescence="进入魔法学院",
            early_adulthood="成为冒险者",
            family_members=[
                {"relation": "父亲", "name": "海神", "description": "强大的魔法师"},
            ],
            socioeconomic_status="贵族出身",
            education_background="皇家魔法学院",
            career_path=["学徒", "魔法师", "冒险者"],
            key_events=["海啸", "学院比赛"],
            turning_points=["获得神器"],
        )
        assert bg.birth_place == "东方的岛屿"
        assert len(bg.career_path) == 3


class TestMotivationDetail:
    """Tests for MotivationDetail model."""

    def test_motivation_detail_full(self):
        """Test full motivation detail."""
        mot = MotivationDetail(
            surface_motivation="复仇",
            deep_motivation="证明自己的价值",
            motivation_type="revenge",
            motivation_source="父亲的死",
            motivation_conflict="复仇vs放下",
            driving_force="愤怒与悲伤",
            obstacles=["强大的敌人", "内心的善良"],
            internal_conflict="复仇是否会带来更多痛苦",
            fear_core="再次失去所爱之人",
            desire_core="让父亲安息",
        )
        assert mot.surface_motivation == "复仇"
        assert mot.deep_motivation == "证明自己的价值"
        assert mot.motivation_type == "revenge"
