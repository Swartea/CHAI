"""Tests for CharacterGrowthArcEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chai.models.character_growth_arc import (
    GrowthArcType,
    ArcStageType,
    GrowthMetricType,
    GrowthTrigger,
    GrowthObstacle,
    GrowthLesson,
    GrowthStage,
    GrowthArcProfile,
    CharacterGrowthArcSystem,
    GrowthArcAnalysis,
)
from chai.models import Character, CharacterRole, CharacterGrowthStage
from chai.engines.character_growth_arc_engine import CharacterGrowthArcEngine
from chai.services import AIService


class TestGrowthArcModels:
    """Tests for character growth arc models."""

    def test_growth_arc_type_enum(self):
        """Test GrowthArcType enum values."""
        assert GrowthArcType.POSITIVE.value == "positive"
        assert GrowthArcType.NEGATIVE.value == "negative"
        assert GrowthArcType.FLAT.value == "flat"
        assert GrowthArcType.CIRCULAR.value == "circular"
        assert GrowthArcType.FALL_AND_RISE.value == "fall_and_rise"
        assert GrowthArcType.RISE_AND_FALL.value == "rise_and_fall"
        assert GrowthArcType.TRANSFORMATION.value == "transformation"
        assert GrowthArcType.BOND.value == "bond"
        assert GrowthArcType.EDUCATION.value == "education"

    def test_arc_stage_type_enum(self):
        """Test ArcStageType enum values."""
        assert ArcStageType.STATUS_QUO.value == "status_quo"
        assert ArcStageType.INCITING_INCIDENT.value == "inciting_incident"
        assert ArcStageType.RISING_ACTION.value == "rising_action"
        assert ArcStageType.COMPLICATION.value == "complication"
        assert ArcStageType.CRISIS.value == "crisis"
        assert ArcStageType.CLIMAX.value == "climax"
        assert ArcStageType.FALLING_ACTION.value == "falling_action"
        assert ArcStageType.RESOLUTION.value == "resolution"

    def test_growth_metric_type_enum(self):
        """Test GrowthMetricType enum values."""
        assert GrowthMetricType.SKILL.value == "skill"
        assert GrowthMetricType.WISDOM.value == "wisdom"
        assert GrowthMetricType.EMOTIONAL.value == "emotional"
        assert GrowthMetricType.MORAL.value == "moral"
        assert GrowthMetricType.RELATIONSHIP.value == "relationship"
        assert GrowthMetricType.SELF_AWARENESS.value == "self_awareness"
        assert GrowthMetricType.POWER.value == "power"
        assert GrowthMetricType.COMPASSION.value == "compassion"
        assert GrowthMetricType.COURAGE.value == "courage"
        assert GrowthMetricType.INDEPENDENCE.value == "independence"

    def test_growth_lesson_model(self):
        """Test GrowthLesson model."""
        lesson = GrowthLesson(
            lesson_type="moral",
            description="学会勇敢面对恐惧",
            application="在关键时刻挺身而出",
            integration_level="complete",
            revisit_required=False,
        )
        assert lesson.lesson_type == "moral"
        assert "勇敢" in lesson.description
        assert lesson.integration_level == "complete"
        assert lesson.revisit_required is False

    def test_growth_trigger_model(self):
        """Test GrowthTrigger model."""
        trigger = GrowthTrigger(
            trigger_type="event",
            description="师父的死激发了主角的成长",
            source="external",
            timing="early",
            intensity="high",
            impact="深刻的情感冲击促使主角反思",
        )
        assert trigger.trigger_type == "event"
        assert "师父" in trigger.description
        assert trigger.source == "external"
        assert trigger.intensity == "high"

    def test_growth_obstacle_model(self):
        """Test GrowthObstacle model."""
        obstacle = GrowthObstacle(
            obstacle_type="internal",
            description="内心的恐惧阻止了成长",
            resistance="每次尝试都被恐惧打断",
            overcome=True,
            overcoming_method="通过冥想和实践逐渐克服",
            growth_from_overcoming="获得了内心的平静",
        )
        assert obstacle.obstacle_type == "internal"
        assert obstacle.overcome is True
        assert "冥想" in obstacle.overcoming_method

    def test_growth_stage_model(self):
        """Test GrowthStage model."""
        lessons = [
            GrowthLesson(
                lesson_type="practical",
                description="学会了战斗技巧",
                application="应用于实战",
                integration_level="partial",
            )
        ]
        stage = GrowthStage(
            stage_type=ArcStageType.RISING_ACTION,
            stage_name="觉醒期",
            description="角色开始意识到自己的潜力",
            chapter_range="3-8",
            trigger_event="导师的启发",
            emotional_state="充满动力",
            mental_state="开始觉醒",
            lessons_learned=lessons,
            new_abilities_or_insights=["战斗技巧", "自我认知"],
            perspective_shift="从被动到主动",
            behavioral_changes=["更加积极主动"],
            key_relationships_at_stage=["导师", "对手"],
            relationship_developments={"导师": "从陌生到信任"},
            conflicts_faced=["内心恐惧", "外部敌人"],
            internal_struggles=["自我怀疑"],
            growth_metrics={"skill": 0.3, "wisdom": 0.2},
        )
        assert stage.stage_type == ArcStageType.RISING_ACTION
        assert stage.stage_name == "觉醒期"
        assert len(stage.lessons_learned) == 1
        assert "战斗技巧" in stage.new_abilities_or_insights
        assert stage.growth_metrics["skill"] == 0.3

    def test_growth_arc_profile_model(self):
        """Test GrowthArcProfile model."""
        stages = [
            GrowthStage(
                stage_type=ArcStageType.STATUS_QUO,
                stage_name="初始状态",
                description="角色处于平静的日常",
                chapter_range="1-2",
                trigger_event="事件触发",
                emotional_state="平静",
                mental_state="稳定",
            )
        ]
        arc = GrowthArcProfile(
            character_id="char_001",
            character_name="张三",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="从懦弱到勇敢",
            arc_summary="一个懦弱的少年成长为勇敢的英雄",
            theme="勇气",
            starting_state="懦弱，害怕冲突",
            ending_state="勇敢，主动面对困难",
            starting_strengths=["善良", "聪明"],
            starting_weaknesses=["懦弱", "优柔寡断"],
            ending_strengths=["勇敢", "果断"],
            ending_weaknesses=["过于冒险"],
            core_wound="童年被欺负的创伤",
            core_desire="变得强大保护所爱之人",
            core_fear="再次被欺负",
            stages=stages,
            total_chapters=50,
            arc_triggers=[],
            obstacles=[],
            key_moments=["第一次战斗胜利"],
            turning_points=["师父的死亡"],
            key_relationship_arcs={"师父": "从师徒到亦师亦友"},
            primary_growth_metric=GrowthMetricType.COURAGE,
            secondary_growth_metrics=[GrowthMetricType.SKILL],
            growth_trajectory=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
            initial_belief="我永远无法变强",
            truth_learned="勇气来自于面对恐惧",
            belief_transformation="从自我否定到自我肯定",
            thematic_connections=["成长", "勇气"],
            symbol_or_motif="破茧成蝶",
        )
        assert arc.character_name == "张三"
        assert arc.arc_type == GrowthArcType.POSITIVE
        assert arc.arc_name == "从懦弱到勇敢"
        assert len(arc.stages) == 1
        assert arc.primary_growth_metric == GrowthMetricType.COURAGE
        assert arc.growth_trajectory[-1] == 1.0
        assert arc.initial_belief == "我永远无法变强"

    def test_character_growth_arc_system_model(self):
        """Test CharacterGrowthArcSystem model."""
        arc1 = GrowthArcProfile(
            character_id="protagonist_001",
            character_name="主角",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="主角弧线",
            arc_summary="主角成长弧线",
            theme="成长",
            starting_state="弱",
            ending_state="强",
            core_wound="创伤",
            core_desire="变强",
            core_fear="失败",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.SKILL,
            growth_trajectory=[0.0, 1.0],
            initial_belief="我不行",
            truth_learned="我可以",
            belief_transformation="从不自信到自信",
        )
        system = CharacterGrowthArcSystem(
            story_id="story_001",
            story_title="测试小说",
            character_arcs=[arc1],
            arc_interdependencies={"protagonist_001": []},
            thematic_throughlines=["成长", "勇气"],
            arc_type_distribution={"positive": 1},
            protagonist_arc_id="protagonist_001",
            parallel_arcs=[],
            intersecting_arcs=[],
        )
        assert system.story_title == "测试小说"
        assert len(system.character_arcs) == 1
        assert system.protagonist_arc_id == "protagonist_001"
        assert system.arc_type_distribution["positive"] == 1

    def test_growth_arc_analysis_model(self):
        """Test GrowthArcAnalysis model."""
        analysis = GrowthArcAnalysis(
            character_id="char_001",
            arc_coherence=0.85,
            growth_pacing="balanced",
            emotional_authenticity=0.9,
            thematic_integration=0.8,
            relationship_impact=0.75,
            stakes_clarity=0.85,
            potential_issues=["部分阶段过渡较快"],
            strengths=["情感真实", "主题突出"],
            recommendations=["可以在中段增加更多挣扎"],
        )
        assert analysis.arc_coherence == 0.85
        assert analysis.growth_pacing == "balanced"
        assert len(analysis.strengths) == 2
        assert len(analysis.recommendations) == 1


class TestCharacterGrowthArcEngine:
    """Tests for CharacterGrowthArcEngine."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)
        assert engine.ai_service is mock_ai

    def test_get_arc_summary_positive_arc(self):
        """Test getting arc summary for positive arc."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        stages = [
            GrowthStage(
                stage_type=ArcStageType.STATUS_QUO,
                stage_name="初始状态",
                description="角色懦弱",
                chapter_range="1-2",
                trigger_event="事件发生",
                emotional_state="平静",
                mental_state="稳定",
                lessons_learned=[],
                new_abilities_or_insights=["勇气"],
                behavioral_changes=["开始主动"],
            ),
            GrowthStage(
                stage_type=ArcStageType.CLIMAX,
                stage_name="高潮",
                description="角色展现勇气",
                chapter_range="40-45",
                trigger_event="危机来临",
                emotional_state="激动",
                mental_state="坚定",
                lessons_learned=[],
                new_abilities_or_insights=["真正的勇气"],
            ),
        ]
        arc = GrowthArcProfile(
            character_id="char_001",
            character_name="张三",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="从懦弱到勇敢",
            arc_summary="懦弱少年成长为英雄",
            theme="勇气",
            starting_state="懦弱",
            ending_state="勇敢",
            core_wound="童年阴影",
            core_desire="保护他人",
            core_fear="失去",
            stages=stages,
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.COURAGE,
            growth_trajectory=[0.0, 1.0],
            initial_belief="我不行",
            truth_learned="我可以",
            belief_transformation="转变",
        )

        summary = engine.get_arc_summary(arc)

        assert "张三" in summary
        assert "从懦弱到勇敢" in summary
        assert "positive" in summary
        assert "初始状态" in summary
        assert "高潮" in summary
        assert "勇气" in summary

    def test_get_arc_summary_with_key_moments(self):
        """Test arc summary with key moments."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        arc = GrowthArcProfile(
            character_id="char_001",
            character_name="李四",
            arc_type=GrowthArcType.TRANSFORMATION,
            arc_name="蜕变",
            arc_summary="角色完全蜕变",
            theme="重生",
            starting_state="迷茫",
            ending_state="清醒",
            core_wound="失去一切",
            core_desire="找到自我",
            core_fear="空虚",
            stages=[],
            total_chapters=40,
            key_moments=["失去一切", "重建自我", "最终救赎"],
            turning_points=["师父的话"],
            primary_growth_metric=GrowthMetricType.SELF_AWARENESS,
            growth_trajectory=[0.0, 0.5, 1.0],
            initial_belief="人生无意义",
            truth_learned="意义在于创造",
            belief_transformation="从悲观到积极",
        )

        summary = engine.get_arc_summary(arc)

        assert "李四" in summary
        assert "失去一切" in summary
        assert "重建自我" in summary
        assert "最终救赎" in summary

    def test_infer_arc_type_from_redemption_motivation(self):
        """Test inferring arc type for redemption motivation."""
        from chai.models.main_character import MainCharacter, MotivationDetail

        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        protagonist = MainCharacter(
            id="prot_001",
            name="救赎者",
            motivation="寻求救赎",
            motivation_detail=MotivationDetail(
                surface_motivation="赎罪",
                deep_motivation="洗清过去的罪恶",
                motivation_type="redemption",
            ),
        )

        arc_type = engine._infer_arc_type_from_motivation(protagonist)
        assert arc_type == GrowthArcType.FALL_AND_RISE

    def test_infer_arc_type_from_revenge_motivation(self):
        """Test inferring arc type for revenge motivation."""
        from chai.models.main_character import MainCharacter, MotivationDetail

        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        protagonist = MainCharacter(
            id="prot_002",
            name="复仇者",
            motivation="复仇",
            motivation_detail=MotivationDetail(
                surface_motivation="复仇",
                deep_motivation="复仇后空虚",
                motivation_type="revenge",
            ),
        )

        arc_type = engine._infer_arc_type_from_motivation(protagonist)
        assert arc_type == GrowthArcType.RISE_AND_FALL

    def test_infer_arc_type_from_fear_motivation(self):
        """Test inferring arc type for fear-based motivation."""
        from chai.models.main_character import MainCharacter, MotivationDetail

        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        protagonist = MainCharacter(
            id="prot_003",
            name="逃避者",
            motivation="逃避过去",
            motivation_detail=MotivationDetail(
                surface_motivation="逃避",
                deep_motivation="面对恐惧",
                motivation_type="fear",
            ),
        )

        arc_type = engine._infer_arc_type_from_motivation(protagonist)
        assert arc_type == GrowthArcType.POSITIVE

    def test_infer_arc_type_default(self):
        """Test default arc type inference."""
        from chai.models.main_character import MainCharacter

        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        protagonist = MainCharacter(
            id="prot_004",
            name="普通人",
        )

        arc_type = engine._infer_arc_type_from_motivation(protagonist)
        assert arc_type == GrowthArcType.POSITIVE

    def test_build_growth_arc_profile_basic(self):
        """Test building growth arc profile from data."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        data = {
            "character_id": "char_001",
            "character_name": "张三",
            "arc_type": "positive",
            "arc_name": "成长弧",
            "arc_summary": "成长的故事",
            "theme": "成长",
            "starting_state": "弱",
            "ending_state": "强",
            "starting_strengths": ["善良"],
            "starting_weaknesses": ["懦弱"],
            "ending_strengths": ["勇敢"],
            "ending_weaknesses": [],
            "core_wound": "创伤",
            "core_desire": "变强",
            "core_fear": "失败",
            "stages": [
                {
                    "stage_type": "status_quo",
                    "stage_name": "初始",
                    "description": "开始状态",
                    "chapter_range": "1-2",
                    "trigger_event": "事件",
                    "emotional_state": "平静",
                    "mental_state": "稳定",
                    "lessons_learned": [],
                    "new_abilities_or_insights": [],
                    "perspective_shift": "",
                    "behavioral_changes": [],
                    "key_relationships_at_stage": [],
                    "relationship_developments": {},
                    "conflicts_faced": [],
                    "internal_struggles": [],
                    "growth_metrics": {},
                }
            ],
            "total_chapters": 50,
            "arc_triggers": [],
            "obstacles": [],
            "key_moments": [],
            "turning_points": [],
            "key_relationship_arcs": {},
            "primary_growth_metric": "wisdom",
            "secondary_growth_metrics": [],
            "growth_trajectory": [0.0, 1.0],
            "initial_belief": "我不行",
            "truth_learned": "我可以",
            "belief_transformation": "转变",
            "thematic_connections": [],
            "symbol_or_motif": "",
        }

        arc = engine._build_growth_arc_profile(data)

        assert arc.character_name == "张三"
        assert arc.arc_type == GrowthArcType.POSITIVE
        assert arc.arc_name == "成长弧"
        assert len(arc.stages) == 1
        assert arc.primary_growth_metric == GrowthMetricType.WISDOM
        assert arc.growth_trajectory[-1] == 1.0

    def test_build_growth_arc_profile_with_lessons(self):
        """Test building arc profile with lessons learned."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        data = {
            "character_id": "char_002",
            "character_name": "李四",
            "arc_type": "positive",
            "arc_name": "学习弧",
            "arc_summary": "学习的故事",
            "theme": "智慧",
            "starting_state": "无知",
            "ending_state": "睿智",
            "core_wound": "失败",
            "core_desire": "知识",
            "core_fear": "无知",
            "stages": [
                {
                    "stage_type": "rising_action",
                    "stage_name": "学习期",
                    "description": "角色开始学习",
                    "chapter_range": "5-15",
                    "trigger_event": "遇到导师",
                    "emotional_state": "渴望",
                    "mental_state": "专注",
                    "lessons_learned": [
                        {
                            "lesson_type": "practical",
                            "description": "学会了基础知识",
                            "application": "应用于实践",
                            "integration_level": "partial",
                        }
                    ],
                    "new_abilities_or_insights": ["基础技能"],
                    "perspective_shift": "开始理解世界",
                    "behavioral_changes": ["更勤奋"],
                    "key_relationships_at_stage": ["导师"],
                    "relationship_developments": {"导师": "建立信任"},
                    "conflicts_faced": ["学习困难"],
                    "internal_struggles": ["自我怀疑"],
                    "growth_metrics": {"wisdom": 0.3},
                }
            ],
            "total_chapters": 40,
            "arc_triggers": [],
            "obstacles": [],
            "key_moments": ["顿悟时刻"],
            "turning_points": ["突破瓶颈"],
            "key_relationship_arcs": {},
            "primary_growth_metric": "wisdom",
            "secondary_growth_metrics": [],
            "growth_trajectory": [0.0, 0.2, 0.5, 1.0],
            "initial_belief": "我太笨了",
            "truth_learned": "努力可以成功",
            "belief_transformation": "从不自信到自信",
            "thematic_connections": ["努力"],
            "symbol_or_motif": "",
        }

        arc = engine._build_growth_arc_profile(data)

        assert arc.character_name == "李四"
        assert len(arc.stages) == 1
        assert len(arc.stages[0].lessons_learned) == 1
        assert arc.stages[0].lessons_learned[0].lesson_type == "practical"
        assert arc.stages[0].growth_metrics["wisdom"] == 0.3
        assert "顿悟时刻" in arc.key_moments

    def test_export_arc_system(self):
        """Test exporting arc system."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        arc = GrowthArcProfile(
            character_id="prot_001",
            character_name="主角",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="主角弧",
            arc_summary="主角成长",
            theme="成长",
            starting_state="弱",
            ending_state="强",
            core_wound="创伤",
            core_desire="变强",
            core_fear="失败",
            stages=[
                GrowthStage(
                    stage_type=ArcStageType.STATUS_QUO,
                    stage_name="初始",
                    description="开始",
                    chapter_range="1-2",
                    trigger_event="事件",
                    emotional_state="平静",
                )
            ],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.SKILL,
            growth_trajectory=[0.0, 1.0],
            initial_belief="我不行",
            truth_learned="我能行",
            belief_transformation="转变",
        )

        system = CharacterGrowthArcSystem(
            story_id="story_001",
            story_title="测试小说",
            character_arcs=[arc],
            arc_type_distribution={"positive": 1},
            protagonist_arc_id="prot_001",
        )

        exported = engine.export_arc_system(system)

        assert exported["story_id"] == "story_001"
        assert exported["story_title"] == "测试小说"
        assert len(exported["character_arcs"]) == 1
        assert exported["protagonist_arc_id"] == "prot_001"
        assert exported["arc_type_distribution"]["positive"] == 1

    def test_export_arc_system_multiple_arcs(self):
        """Test exporting system with multiple arcs."""
        mock_ai = MagicMock(spec=AIService)
        engine = CharacterGrowthArcEngine(mock_ai)

        arc1 = GrowthArcProfile(
            character_id="prot_001",
            character_name="主角",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="主角弧",
            arc_summary="主角成长",
            theme="成长",
            starting_state="弱",
            ending_state="强",
            core_wound="创伤",
            core_desire="变强",
            core_fear="失败",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.SKILL,
            growth_trajectory=[0.0, 1.0],
            initial_belief="我不行",
            truth_learned="我能行",
            belief_transformation="转变",
        )

        arc2 = GrowthArcProfile(
            character_id="ant_001",
            character_name="反派",
            arc_type=GrowthArcType.NEGATIVE,
            arc_name="反派弧",
            arc_summary="反派堕落",
            theme="堕落",
            starting_state="野心",
            ending_state="毁灭",
            core_wound="被背叛",
            core_desire="权力",
            core_fear="失去权力",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.POWER,
            growth_trajectory=[1.0, 0.0],
            initial_belief="权力至上",
            truth_learned="权力导致毁灭",
            belief_transformation="更加贪婪",
        )

        system = CharacterGrowthArcSystem(
            story_id="story_001",
            story_title="测试小说",
            character_arcs=[arc1, arc2],
            arc_type_distribution={"positive": 1, "negative": 1},
            protagonist_arc_id="prot_001",
        )

        exported = engine.export_arc_system(system)

        assert len(exported["character_arcs"]) == 2
        assert exported["arc_type_distribution"]["positive"] == 1
        assert exported["arc_type_distribution"]["negative"] == 1


class TestGrowthArcConsistency:
    """Tests for growth arc consistency checks."""

    def test_growth_trajectory_monotonic_positive_arc(self):
        """Test that positive arc has increasing trajectory."""
        arc = GrowthArcProfile(
            character_id="char_001",
            character_name="张三",
            arc_type=GrowthArcType.POSITIVE,
            arc_name="成长弧",
            arc_summary="成长",
            theme="成长",
            starting_state="弱",
            ending_state="强",
            core_wound="创伤",
            core_desire="变强",
            core_fear="失败",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.SKILL,
            growth_trajectory=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            initial_belief="我不行",
            truth_learned="我能",
            belief_transformation="转变",
        )
        # Check trajectory is monotonically increasing for positive arc
        for i in range(1, len(arc.growth_trajectory)):
            assert arc.growth_trajectory[i] >= arc.growth_trajectory[i - 1]

    def test_growth_trajectory_negative_arc(self):
        """Test that negative arc has decreasing trajectory."""
        arc = GrowthArcProfile(
            character_id="char_002",
            character_name="反派",
            arc_type=GrowthArcType.NEGATIVE,
            arc_name="堕落弧",
            arc_summary="堕落",
            theme="堕落",
            starting_state="强",
            ending_state="弱",
            core_wound="背叛",
            core_desire="权力",
            core_fear="失去",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.MORAL,
            growth_trajectory=[1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
            initial_belief="权力至上",
            truth_learned="毁灭",
            belief_transformation="更加贪婪",
        )
        # Check trajectory is monotonically decreasing for negative arc
        for i in range(1, len(arc.growth_trajectory)):
            assert arc.growth_trajectory[i] <= arc.growth_trajectory[i - 1]

    def test_flat_arc_trajectory(self):
        """Test that flat arc maintains similar values."""
        arc = GrowthArcProfile(
            character_id="char_003",
            character_name="智者",
            arc_type=GrowthArcType.FLAT,
            arc_name="坚守弧",
            arc_summary="坚守信念",
            theme="信念",
            starting_state="坚定",
            ending_state="坚定",
            core_wound="诱惑",
            core_desire="坚守",
            core_fear="动摇",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.MORAL,
            growth_trajectory=[0.8, 0.8, 0.85, 0.8, 0.85, 0.9],
            initial_belief="正义必胜",
            truth_learned="坚守正义",
            belief_transformation="更加坚定",
        )
        # Check trajectory stays relatively flat with minor variations
        avg = sum(arc.growth_trajectory) / len(arc.growth_trajectory)
        for val in arc.growth_trajectory:
            assert abs(val - avg) < 0.2  # Values should be close to average

    def test_circular_arc_trajectory(self):
        """Test that circular arc returns to starting value."""
        arc = GrowthArcProfile(
            character_id="char_004",
            character_name="流浪者",
            arc_type=GrowthArcType.CIRCULAR,
            arc_name="循环弧",
            arc_summary="经历起伏回到原点",
            theme="探索",
            starting_state="迷茫",
            ending_state="清醒但回到原点",
            core_wound="失去方向",
            core_desire="找到自我",
            core_fear="迷失",
            stages=[],
            total_chapters=50,
            primary_growth_metric=GrowthMetricType.SELF_AWARENESS,
            growth_trajectory=[0.2, 0.5, 0.8, 0.5, 0.3, 0.2],
            initial_belief="外面更好",
            truth_learned="内心平静",
            belief_transformation="从追求外在到内在平静",
        )
        # Check trajectory ends near where it started
        start = arc.growth_trajectory[0]
        end = arc.growth_trajectory[-1]
        assert abs(start - end) < 0.15  # Should end close to starting value
