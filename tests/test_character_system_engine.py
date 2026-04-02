"""Tests for CharacterSystemEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models import (
    Character,
    CharacterSystem,
    CharacterArchetype,
    CharacterSkill,
    CharacterGroup,
    CharacterConflict,
    CharacterGrowthStage,
    CharacterRelationship,
    CharacterRole,
)
from chai.engines import CharacterSystemEngine
from chai.services import AIService


class TestCharacterModel:
    """Tests for enhanced Character model."""

    def test_character_basic_fields(self):
        """Test Character with basic fields."""
        char = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
        )
        assert char.id == "char_001"
        assert char.name == "张三"
        assert char.role == CharacterRole.PROTAGONIST
        assert char.status == "active"

    def test_character_extended_fields(self):
        """Test Character with extended fields."""
        char = Character(
            id="char_002",
            name="李四",
            role=CharacterRole.ANTAGONIST,
            age="30岁",
            age_numeric=30,
            appearance={
                "face": "冷峻",
                "body": "高大",
                "dressing": "黑色长袍",
                "overall": "威严",
            },
            distinguishing_features=["眉间疤痕", "银色瞳孔"],
            presence="令人窒息的气场",
            personality={
                "traits": ["冷静", "理性"],
                "mbti": "INTJ",
            },
            personality_description="城府极深，从不显露真实情感",
            values=["力量", "秩序"],
            fears=["失去控制", "被背叛"],
            desires=["统治世界", "永恒生命"],
            strengths=["战略头脑", "超强的意志力"],
            weaknesses=["过度自信", "孤独"],
            habits=["摩擦戒指", "观察手指"],
            backstory="曾是帝国最年轻的将军",
            origin="北境王国",
            family_background="贵族世家",
            education="帝国最高学院",
            previous_occupations=["将军", "间谍首领"],
            formative_experiences=["战争的洗礼", "亲人的背叛"],
            motivation="复仇与权力",
            goal="建立一个绝对秩序的帝国",
            internal_conflict="对权力的渴望与对人性最后的怀疑",
            skills=[
                CharacterSkill(
                    name="剑术",
                    description="帝国最强的剑士",
                    category="combat",
                    proficiency_level="master",
                    source="多年战场历练",
                )
            ],
            combat_abilities=["剑术", "骑术"],
            social_abilities=["威慑", "谈判"],
            intellectual_abilities=["战略", "谋略"],
            resources=["暗影军团", "秘密情报网"],
            equipment=["长剑", "黑色斗篷"],
            groups=[
                CharacterGroup(
                    group_id="group_001",
                    name="暗影议会",
                    group_type="secret_society",
                    role="首领",
                    position="议长",
                    joined_at="十年前",
                )
            ],
            relationships=[
                CharacterRelationship(
                    character_id="char_001",
                    character_name="张三",
                    relationship_type="nemesis",
                    description="宿命之敌",
                    dynamics="亦敌亦友，相互制衡",
                    history="曾是同门师兄弟",
                    current_status="对立",
                )
            ],
            archetype="影子",
            growth_arc="从追求绝对力量到理解人性",
            growth_stages=[
                CharacterGrowthStage(
                    stage_name="觉醒",
                    description="发现内心深处的人性",
                    trigger_event="与主角的对决",
                    lessons_learned=["力量不是一切"],
                    new_abilities_or_insights=["理解弱点的价值"],
                    emotional_state="困惑",
                )
            ],
            starting_state="冷酷无情",
            ending_state="为人性留有一席之地",
            psychological_profile={
                "attachment_style": "回避型",
                "defense_mechanisms": ["理性化", "隔离"],
            },
            attachment_style="难以建立信任",
            defense_mechanisms=["理智化", "压抑"],
            emotional_wounds=["弟弟的死", "爱人的背叛"],
            resilience_factors=["坚强的意志", "对理想的执念"],
            speech_pattern="低沉而带有威压",
            speech_characteristics=["常用命令式", "很少用疑问句"],
            catchphrases=["这是命令", "弱者没有生存的权利"],
            communication_style="直接、简洁、有威压感",
            narrative_function="对比主角的镜像角色",
            thematic_significance="探讨力量的真正意义",
            character_arc_summary="从追求绝对力量到理解人性的复杂",
            conflicts=[
                CharacterConflict(
                    conflict_type="internal",
                    description="对权力的渴望与人性的矛盾",
                    parties_involved=["自己"],
                    stakes="失去灵魂还是获得世界",
                    current_status="active",
                )
            ],
            first_appearance="第一章",
            status="active",
        )

        assert char.age == "30岁"
        assert char.age_numeric == 30
        assert len(char.distinguishing_features) == 2
        assert char.presence == "令人窒息的气场"
        assert len(char.values) == 2
        assert len(char.fears) == 2
        assert len(char.desires) == 2
        assert len(char.strengths) == 2
        assert len(char.weaknesses) == 2
        assert len(char.skills) == 1
        assert char.skills[0].name == "剑术"
        assert len(char.groups) == 1
        assert char.groups[0].name == "暗影议会"
        assert len(char.relationships) == 1
        assert char.relationships[0].relationship_type == "nemesis"
        assert char.archetype == "影子"
        assert len(char.growth_stages) == 1
        assert len(char.conflicts) == 1
        assert len(char.catchphrases) == 2


class TestCharacterArchetype:
    """Tests for CharacterArchetype model."""

    def test_archetype_basic(self):
        """Test basic archetype creation."""
        archetype = CharacterArchetype(
            name="英雄",
            description="故事的核心人物",
            typical_traits=["勇敢", "正直"],
            typical_motivations=["保护所爱之人"],
            typical_weaknesses=["过度责任感"],
            growth_potential="从自我中心到无私奉献",
            examples_in_literature=["哈利波特", "指环王"],
        )
        assert archetype.name == "英雄"
        assert len(archetype.typical_traits) == 2
        assert len(archetype.examples_in_literature) == 2


class TestCharacterSkill:
    """Tests for CharacterSkill model."""

    def test_skill_basic(self):
        """Test basic skill creation."""
        skill = CharacterSkill(
            name="剑术",
            description="精通各种剑技",
            category="combat",
            proficiency_level="master",
            source="十年苦练",
            conditions=["需要武器"],
            limitations=["对远程敌人无效"],
            synergy_with_other_skills=["骑术", "战术"],
        )
        assert skill.name == "剑术"
        assert skill.category == "combat"
        assert skill.proficiency_level == "master"
        assert len(skill.limitations) == 1


class TestCharacterGroup:
    """Tests for CharacterGroup model."""

    def test_group_basic(self):
        """Test basic group creation."""
        group = CharacterGroup(
            group_id="grp_001",
            name="江湖门派",
            group_type="martial_sect",
            role="掌门",
            position="最高",
            joined_at="二十年前",
            tenure="掌门20年",
            contributions=["创派立派", "培养人才"],
            group_reputation="武林至尊",
            group_conflicts=["门派之争"],
        )
        assert group.name == "江湖门派"
        assert group.group_type == "martial_sect"
        assert group.role == "掌门"


class TestCharacterConflict:
    """Tests for CharacterConflict model."""

    def test_conflict_basic(self):
        """Test basic conflict creation."""
        conflict = CharacterConflict(
            conflict_type="internal",
            description="内心的善恶之争",
            parties_involved=["自己"],
            cause="童年的创伤",
            stakes="灵魂的归属",
            current_status="active",
            potential_resolution="接受人性的复杂",
            impact_on_character="影响决策",
        )
        assert conflict.conflict_type == "internal"
        assert len(conflict.parties_involved) == 1


class TestCharacterGrowthStage:
    """Tests for CharacterGrowthStage model."""

    def test_growth_stage_basic(self):
        """Test basic growth stage creation."""
        stage = CharacterGrowthStage(
            stage_name="觉醒",
            description="认识到自己的使命",
            trigger_event="师父的牺牲",
            lessons_learned=["责任比生命更重要"],
            new_abilities_or_insights=["觉醒特殊能力"],
            emotional_state="悲痛但坚定",
            chapter_or_arc_reference="第15章",
        )
        assert stage.stage_name == "觉醒"
        assert len(stage.lessons_learned) == 1


class TestCharacterSystem:
    """Tests for CharacterSystem model."""

    def test_character_system_basic(self):
        """Test basic character system creation."""
        system = CharacterSystem(
            name="玄幻小说角色体系",
            genre="玄幻",
            theme="修仙",
            archetypes=[
                CharacterArchetype(
                    name="英雄",
                    description="主角",
                    typical_traits=["勇敢"],
                    typical_motivations=["成长"],
                    typical_weaknesses=["经验不足"],
                    growth_potential="成为强者",
                    examples_in_literature=["凡人修仙传"],
                )
            ],
            relationship_templates=[
                {
                    "type": "师徒",
                    "description": "传承关系",
                    "typical_dynamics": "严格教导与叛逆成长",
                    "common_conflicts": "理念不合",
                    "development_potential": "亦师亦友",
                }
            ],
            generation_guidelines="注重角色的成长性和内心冲突",
            role_distribution={
                "protagonist": 1,
                "antagonist": 1,
                "supporting": 5,
            },
            group_templates=[
                {
                    "name": "修仙门派",
                    "type": "sect",
                    "typical_structure": "掌门-长老-弟子",
                    "roles_within_group": ["掌门", "长老", "核心弟子", "普通弟子"],
                    "internal_conflicts":["资源争夺", "理念分歧"],
                }
            ],
        )
        assert system.name == "玄幻小说角色体系"
        assert system.genre == "玄幻"
        assert len(system.archetypes) == 1
        assert len(system.relationship_templates) == 1
        assert len(system.role_distribution) == 3


class TestCharacterSystemEngine:
    """Tests for CharacterSystemEngine methods."""

    def test_analyze_character_consistency_empty(self):
        """Test analysis with no characters."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)
        result = engine.analyze_character_consistency([])

        assert len(result["issues"]) > 0
        assert result["status"] == "needs_review"
        assert result["completeness_score"] == 0.0

    def test_analyze_character_consistency_with_protagonist(self):
        """Test analysis with valid characters."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char1 = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            backstory="平凡少年",
            motivation="成为强者",
            goal="拯救世界",
        )
        char2 = Character(
            id="char_002",
            name="李四",
            role=CharacterRole.ANTAGONIST,
            backstory="失去一切",
            motivation="复仇",
            goal="毁灭世界",
        )

        result = engine.analyze_character_consistency([char1, char2])

        assert result["total_characters"] == 2
        assert result["protagonist_count"] == 1
        assert result["antagonist_count"] == 1
        assert result["status"] == "consistent"

    def test_analyze_character_consistency_missing_antagonist(self):
        """Test analysis with missing antagonist."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char1 = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            backstory="平凡少年",
            motivation="成为强者",
            goal="拯救世界",
        )

        result = engine.analyze_character_consistency([char1])

        assert result["antagonist_count"] == 0
        assert len(result["warnings"]) > 0

    def test_validate_character_development_protagonist(self):
        """Test validation of protagonist development."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            growth_arc="从软弱到坚强",
            starting_state="胆小怕事",
            ending_state="顶天立地",
            growth_stages=[
                CharacterGrowthStage(
                    stage_name="觉醒",
                    description="第一次成长",
                    trigger_event="师父的教导",
                    lessons_learned=["勇敢"],
                    new_abilities_or_insights=["剑气"],
                    emotional_state="坚定",
                ),
                CharacterGrowthStage(
                    stage_name="突破",
                    description="第二次成长",
                    trigger_event="生死之战",
                    lessons_learned=["责任"],
                    new_abilities_or_insights=["剑意"],
                    emotional_state="平静",
                ),
            ],
        )

        result = engine.validate_character_development(char)

        assert result["valid"] is True
        assert result["has_growth_arc"] is True
        assert result["growth_stage_count"] == 2

    def test_validate_character_development_missing_arc(self):
        """Test validation with missing growth arc."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
        )

        result = engine.validate_character_development(char)

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_character_development_minor_character(self):
        """Test validation of minor character (should pass without full arc)."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char = Character(
            id="char_001",
            name="店主",
            role=CharacterRole.MINOR,
        )

        result = engine.validate_character_development(char)

        assert result["valid"] is True

    def test_get_character_summary(self):
        """Test getting character summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        char = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            age="20岁",
            personality_description="热血正义",
            values=["正义", "友情"],
            fears=["失去朋友"],
            desires=["变强", "保护所爱之人"],
            strengths=["剑术天赋"],
            weaknesses=["冲动"],
            backstory="出身于没落世家",
            motivation="恢复家族荣光",
            goal="成为剑圣",
            catchphrases=["我的剑，为守护而出鞘"],
            speech_pattern="豪爽直接",
        )

        summary = engine.get_character_summary(char)

        assert "张三" in summary
        assert "protagonist" in summary
        assert "20岁" in summary
        assert "热血正义" in summary
        assert "正义" in summary
        assert "我的剑" in summary

    def test_get_character_system_summary(self):
        """Test getting character system summary."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        system = CharacterSystem(
            name="武侠角色体系",
            genre="武侠",
            theme="江湖",
            archetypes=[
                CharacterArchetype(
                    name="大侠",
                    description="正派主角",
                    typical_traits=["正义", "勇敢"],
                    typical_motivations=["行侠仗义"],
                    typical_weaknesses=["过于仁慈"],
                    growth_potential="成为一代宗师",
                    examples_in_literature=["神雕侠侣"],
                )
            ],
            role_distribution={
                "protagonist": 1,
                "antagonist": 2,
            },
            group_templates=[
                {
                    "name": "武林门派",
                    "type": "sect",
                    "typical_structure": "掌门-长老-弟子",
                    "roles_within_group": ["掌门", "弟子"],
                    "internal_conflicts": ["门户之见"],
                }
            ],
        )

        summary = engine.get_character_system_summary(system)

        assert "武侠角色体系" in summary
        assert "武侠" in summary
        assert "大侠" in summary
        assert "武林门派" in summary

    def test_export_character_system(self):
        """Test exporting character system."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterSystemEngine(mock_ai)

        system = CharacterSystem(
            name="测试体系",
            genre="测试",
            theme="测试主题",
        )

        char = Character(
            id="char_001",
            name="测试角色",
            role=CharacterRole.PROTAGONIST,
            backstory="测试背景",
            motivation="测试动机",
            goal="测试目标",
        )

        export = engine.export_character_system(
            character_system=system,
            characters=[char],
            include_analysis=True,
        )

        assert "character_system" in export
        assert "characters" in export
        assert "summary" in export
        assert "analysis" in export

    @pytest.mark.asyncio
    async def test_generate_character_relationship(self):
        """Test generating relationship between characters."""
        mock_ai = MagicMock(spec=AIService)
        mock_ai.generate = AsyncMock(return_value='{"character_id": "char_002", "character_name": "李四", "relationship_type": "rival", "description": "竞争对手", "dynamics": "相互竞争", "history": "同门师兄弟", "current_status": "对立", "key_events": ["比武大会"]}')
        engine = CharacterSystemEngine(mock_ai)

        char1 = Character(
            id="char_001",
            name="张三",
            role=CharacterRole.PROTAGONIST,
        )
        char2 = Character(
            id="char_002",
            name="李四",
            role=CharacterRole.SUPPORTING,
        )

        relationship = await engine.generate_character_relationship(char1, char2, "rival")

        assert relationship.character_id == "char_002"
        assert relationship.character_name == "李四"
        assert relationship.relationship_type == "rival"
        assert relationship.dynamics == "相互竞争"


class TestCharacterRelationshipTypes:
    """Tests for CharacterRelationship model."""

    def test_relationship_types(self):
        """Test various relationship types."""
        rel = CharacterRelationship(
            character_id="char_002",
            character_name="李四",
            relationship_type="mentor",
            description="师徒关系",
            dynamics="严厉教导",
            history="在山中相遇",
            current_status="持续中",
            key_events=["拜师", "传功"],
        )
        assert rel.relationship_type == "mentor"
        assert len(rel.key_events) == 2


class TestCharacterRole:
    """Tests for CharacterRole enum."""

    def test_all_roles_defined(self):
        """Test that all expected roles exist."""
        assert CharacterRole.PROTAGONIST.value == "protagonist"
        assert CharacterRole.ANTAGONIST.value == "antagonist"
        assert CharacterRole.SUPPORTING.value == "supporting"
        assert CharacterRole.MINOR.value == "minor"
        assert CharacterRole.MENTOR.value == "mentor"
        assert CharacterRole.LOVE_INTEREST.value == "love_interest"
        assert CharacterRole.SIDEKICK.value == "sidekick"
        assert CharacterRole.DEuteragonist.value == "deuteragonist"