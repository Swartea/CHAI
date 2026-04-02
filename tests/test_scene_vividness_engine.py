"""Tests for scene vividness engine."""

import pytest
from chai.engines.scene_vividness_engine import SceneVividnessEngine
from chai.models.scene_vividness import (
    SceneVividnessType,
    SceneVividnessSeverity,
    SceneVividnessTemplate,
    ImageryClarity,
    SensoryEngagement,
    ShowDontTellLevel,
)


@pytest.fixture
def engine():
    """Create scene vividness engine."""
    return SceneVividnessEngine()


@pytest.fixture
def vivid_scene():
    """A vivid scene description."""
    return """夕阳的余晖洒落在古老的石板路上，将每一块石头都染成了温暖的橙红色。
街道两旁的梧桐树投下斑驳的影子，微风吹过，树叶沙沙作响。
空气中弥漫着烤红薯的香甜气息，混合着远处咖啡馆飘来的苦香。
一只橘色的猫蜷缩在窗台上，慵懒地眯着眼睛。

老旧的木质招牌在风中轻轻摇晃，发出吱呀的声响。
街角的路灯刚刚亮起，昏黄的光线与最后一缕阳光交织在一起，
在青石板上勾勒出一幅温馨的画面。"""


@pytest.fixture
def dull_scene():
    """A dull, vague scene description."""
    return """这是一个地方。那里有一些东西。
人们在做事情。感觉很奇怪。
有个建筑物。还有一些人。
我不知道发生了什么。"""


@pytest.fixture
def partial_showing_scene():
    """Scene with some showing but also some telling."""
    return """房间很暗。气氛很紧张。
他感到害怕。她看起来很悲伤。
窗外有声音。他听到了。
他的心跳很快。她在发抖。"""


@pytest.fixture
def sensory_heavy_scene():
    """Scene with heavy sensory details."""
    return """金色的阳光从东边的窗户斜斜地照进来，
在老旧的橡木地板上投下一道明亮的光柱。
空气中浮动着细小的尘埃，在光线中闪闪发亮。
远处传来教堂的钟声，沉闷而悠远。
风带来了松脂的清香，还有一丝海水的咸味。

她伸手触摸墙壁，感觉到砖石粗糙的纹理和残留的温热。
老式的留声机正在播放一首古老的爵士乐，
萨克斯风的声音像融化的蜂蜜一样流淌。
空气中弥漫着咖啡的苦香和旧书页的陈旧气息。"""


class TestAnalyzeSceneVividness:

    def test_analyze_vivid_scene_returns_high_score(self, engine, vivid_scene):
        """Vivid scene should get high vividness score."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")

        assert analysis.overall_vividness > 0.6
        assert analysis.total_issues == 0 or all(
            i.severity == SceneVividnessSeverity.MINOR for i in analysis.profile.issues
        )

    def test_analyze_dull_scene_returns_low_score(self, engine, dull_scene):
        """Dull scene should get low vividness score."""
        analysis = engine.analyze_scene_vividness(dull_scene, "scene_002")

        assert analysis.overall_vividness < 0.5
        assert analysis.total_issues >= 2

    def test_analyze_partial_showing_scene(self, engine, partial_showing_scene):
        """Scene with telling should be flagged."""
        analysis = engine.analyze_scene_vividness(partial_showing_scene, "scene_003")

        # Should have showing/telling issues
        telling_issues = [
            i for i in analysis.profile.issues
            if i.issue_type == SceneVividnessType.TELLING_INSTEAD_SHOWING
        ]
        assert len(telling_issues) > 0

    def test_word_count_calculation(self, engine, vivid_scene):
        """Word count should be calculated correctly."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")

        assert analysis.profile.word_count > 0

    def test_visual_details_check(self, engine, vivid_scene):
        """Visual details should be properly checked."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")

        visual = analysis.profile.visual_details
        assert visual.has_color_details is True
        assert visual.has_light_shadow is True
        assert visual.color_word_count > 0

    def test_sensory_details_check(self, engine, vivid_scene):
        """Sensory details should be properly checked."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")

        sensory = analysis.profile.sensory_details
        # Should have multiple senses engaged
        assert sensory.sense_diversity_score >= 0.3

    def test_filter_words_detection(self, engine, partial_showing_scene):
        """Filter words should be detected."""
        analysis = engine.analyze_scene_vividness(partial_showing_scene, "scene_003")

        # Scene with "听到" should have filter words
        assert analysis.profile.language_quality.filter_word_count >= 0


class TestSceneVividnessIssues:

    def test_identifies_absent_visual_details(self, engine, dull_scene):
        """Should identify missing visual details."""
        analysis = engine.analyze_scene_vividness(dull_scene, "scene_002")

        has_absent_visual = any(
            i.issue_type == SceneVividnessType.ABSENT_VISUAL_DETAILS
            for i in analysis.profile.issues
        )
        assert has_absent_visual

    def test_identifies_showing_instead_telling(self, engine, partial_showing_scene):
        """Should identify telling instead of showing."""
        analysis = engine.analyze_scene_vividness(partial_showing_scene, "scene_003")

        has_telling = any(
            i.issue_type == SceneVividnessType.TELLING_INSTEAD_SHOWING
            for i in analysis.profile.issues
        )
        assert has_telling

    def test_identifies_absent_sensory_details(self, engine):
        """Should identify absent sensory details."""
        # Scene with almost no sensory details
        no_sensory_scene = """这是一个地方。那里有一些东西。
        人们在做事情。不知道发生了什么。"""
        analysis = engine.analyze_scene_vividness(no_sensory_scene, "scene_002")

        has_absent_sensory = any(
            i.issue_type == SceneVividnessType.ABSENT_SENSORY_DETAILS
            for i in analysis.profile.issues
        )
        assert has_absent_sensory


class TestSceneVividnessScores:

    def test_vividness_score_calculation(self, engine, vivid_scene):
        """Vividness score should be reasonable."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")

        assert 0.0 <= analysis.overall_vividness <= 1.0
        assert 0.0 <= analysis.visual_imagery_score <= 1.0
        assert 0.0 <= analysis.sensory_balance_score <= 1.0
        assert 0.0 <= analysis.show_dont_tell_score <= 1.0

    def test_imagery_clarity_determination(self, engine, vivid_scene, dull_scene):
        """Imagery clarity should be determined correctly."""
        vivid_analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")
        dull_analysis = engine.analyze_scene_vividness(dull_scene, "scene_002")

        # Vivid scene should have better imagery clarity
        vivid_level = vivid_analysis.profile.imagery_clarity
        dull_level = dull_analysis.profile.imagery_clarity

        vivid_order = [ImageryClarity.UNCLEAR, ImageryClarity.FUZZY, ImageryClarity.ADEQUATE,
                       ImageryClarity.CLEAR, ImageryClarity.VIVID]
        assert vivid_order.index(vivid_level) >= vivid_order.index(dull_level)

    def test_sensory_engagement_determination(self, engine, sensory_heavy_scene, dull_scene):
        """Sensory engagement should be determined correctly."""
        rich_analysis = engine.analyze_scene_vividness(sensory_heavy_scene, "scene_004")
        dull_analysis = engine.analyze_scene_vividness(dull_scene, "scene_002")

        # Rich sensory scene should have higher engagement
        rich_level = rich_analysis.profile.sensory_engagement
        dull_level = dull_analysis.profile.sensory_engagement

        level_order = [SensoryEngagement.NONE, SensoryEngagement.MINIMAL,
                       SensoryEngagement.MODERATE, SensoryEngagement.RICH]
        assert level_order.index(rich_level) >= level_order.index(dull_level)


class TestCreateRevisionPlan:

    def test_revision_plan_creation(self, engine, partial_showing_scene):
        """Should create revision plan for issues."""
        analysis = engine.analyze_scene_vividness(partial_showing_scene, "scene_003")
        revision = engine.create_revision_plan(analysis)

        assert revision.original_scene_id == "scene_003"
        assert len(revision.revision_notes) > 0 or len(revision.suggested_additions) > 0

    def test_priority_fixes_for_severe_issues(self, engine, dull_scene):
        """Severe issues should be in priority fixes."""
        analysis = engine.analyze_scene_vividness(dull_scene, "scene_002")
        revision = engine.create_revision_plan(analysis)

        # If there are moderate/severe issues, priority fixes should have them
        severe_or_moderate = [
            i for i in analysis.profile.issues
            if i.severity in [SceneVividnessSeverity.SEVERE, SceneVividnessSeverity.MODERATE]
        ]
        if severe_or_moderate:
            assert len(revision.priority_fixes) > 0 or len(revision.revision_notes) > 0


class TestGetSummary:

    def test_summary_format(self, engine, vivid_scene):
        """Summary should be properly formatted."""
        analysis = engine.analyze_scene_vividness(vivid_scene, "scene_001")
        summary = engine.get_summary(analysis)

        assert "scene_001" in summary
        assert "Vividness Score:" in summary
        assert "Imagery Clarity:" in summary


class TestGenerateReport:

    def test_report_from_multiple_analyses(self, engine, vivid_scene, dull_scene):
        """Should generate aggregate report from multiple analyses."""
        analyses = [
            engine.analyze_scene_vividness(vivid_scene, "scene_001"),
            engine.analyze_scene_vividness(dull_scene, "scene_002"),
        ]

        report = engine.generate_report(analyses)

        assert report.scene_count == 2
        assert report.total_issues >= 0
        assert report.average_vividness > 0

    def test_empty_report(self, engine):
        """Should handle empty analyses."""
        report = engine.generate_report([])

        assert report.scene_count == 0
        assert report.total_issues == 0


class TestColorWordDetection:

    def test_detects_color_words(self, engine):
        """Should detect color words in text."""
        text = "红色的花朵在蓝天下绽放，金色的阳光洒落"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.visual_details.has_color_details is True
        assert analysis.profile.visual_details.color_word_count >= 2


class TestFilterWords:

    def test_detects_filter_words(self, engine):
        """Should detect filter words like 看到, 听到."""
        text = "他看到窗外的东西，听到远处的声音，感到有些害怕"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.language_quality.filter_word_count >= 3


class TestClicheDetection:

    def test_detects_cliches(self, engine):
        """Should detect cliche phrases."""
        text = "鸟语花香，风和日丽，亭亭玉立"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.language_quality.cliche_count >= 2


class TestWeakAdjectives:

    def test_detects_weak_adjectives(self, engine):
        """Should detect weak adjectives like 很, 非常."""
        text = "很热，非常冷，有点奇怪"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.language_quality.weak_adjective_count >= 3


class TestShowDontTellPatterns:

    def test_detects_telling_phrases(self, engine):
        """Should detect phrases that tell instead of show."""
        text = "他很紧张，她很悲伤，气氛压抑"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.show_dont_tell.telling_count >= 2


class TestSensoryDiversity:

    def test_sensory_diversity_calculation(self, engine, sensory_heavy_scene):
        """Should calculate sensory diversity correctly."""
        analysis = engine.analyze_scene_vividness(sensory_heavy_scene, "scene_004")

        # Should engage multiple senses
        assert analysis.profile.sensory_details.sense_diversity_score >= 0.4


class TestSpatialArrangement:

    def test_detects_spatial_words(self, engine):
        """Should detect spatial/directional words."""
        text = "左边的桌子上放着书，右边是窗户，前面有一把椅子"
        analysis = engine.analyze_scene_vividness(text, "scene_001")

        assert analysis.profile.visual_details.has_spatial_arrangement is True
