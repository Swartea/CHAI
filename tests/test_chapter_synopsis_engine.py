"""Unit tests for chapter synopsis engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from chai.engines.chapter_synopsis_engine import (
    ChapterSynopsisEngine,
    CHAPTER_STRUCTURE_TEMPLATE,
    PLOT_POINT_DISTRIBUTION,
)
from chai.models.chapter_synopsis import (
    SynopsisPlotPoint,
    SynopsisPlotPointType,
    SynopsisPlotPointStatus,
    PlotPointImportance,
    ChapterSynopsis,
    ChapterSynopsisSection,
    PlotPointArrangement,
    ChapterSynopsisAnalysis,
)


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    service = MagicMock()
    service.generate = AsyncMock(return_value='{"title": "第1章", "summary": "测试章节", "detailed_synopsis": "详细测试内容", "pov_character": "主角", "characters_present": ["主角", "配角"], "new_characters": [], "primary_location": "城镇", "time_setting": "第一天", "plot_threads_advanced": [], "character_development": [], "foreshadowing_planted": [], "foreshadowing_payoffs": [], "themes_explored": [], "emotional_arc": "平静", "pacing_notes": "平稳", "sections": {"opening": "开场", "development": "发展", "climax": "高潮", "resolution": "收尾"}}')
    service._parse_json = MagicMock(return_value={"title": "第1章", "summary": "测试章节", "detailed_synopsis": "详细测试内容", "pov_character": "主角", "characters_present": ["主角", "配角"], "new_characters": [], "primary_location": "城镇", "time_setting": "第一天", "plot_threads_advanced": [], "character_development": [], "foreshadowing_planted": [], "foreshadowing_payoffs": [], "themes_explored": [], "emotional_arc": "平静", "pacing_notes": "平稳", "sections": {"opening": "开场", "development": "发展", "climax": "高潮", "resolution": "收尾"}})
    return service


@pytest.fixture
def engine(mock_ai_service):
    """Create a chapter synopsis engine with mock service."""
    return ChapterSynopsisEngine(mock_ai_service)


class TestSynopsisPlotPointModel:
    """Test SynopsisPlotPoint model."""

    def test_plot_point_creation(self):
        """Test creating a plot point."""
        point = SynopsisPlotPoint(
            id="pp_1",
            name="关键转折",
            plot_point_type=SynopsisPlotPointType.TURNING_POINT,
            description="故事发生重大转折",
            chapter=8,
            importance=PlotPointImportance.ESSENTIAL,
        )
        assert point.id == "pp_1"
        assert point.name == "关键转折"
        assert point.plot_point_type == SynopsisPlotPointType.TURNING_POINT
        assert point.chapter == 8
        assert point.importance == PlotPointImportance.ESSENTIAL

    def test_plot_point_defaults(self):
        """Test plot point default values."""
        point = SynopsisPlotPoint(
            id="pp_2",
            name="测试点",
            plot_point_type=SynopsisPlotPointType.KEY_EVENT,
            description="测试描述",
            chapter=5,
        )
        assert point.status == SynopsisPlotPointStatus.PENDING
        assert point.tension_level == "moderate"
        assert point.character_ids == []


class TestChapterSynopsisModel:
    """Test ChapterSynopsis model."""

    def test_chapter_synopsis_creation(self):
        """Test creating a chapter synopsis."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="第1章",
            summary="测试章节概要",
            pov_character="主角",
        )
        assert synopsis.id == "syn_1"
        assert synopsis.chapter_number == 1
        assert synopsis.title == "第1章"
        assert synopsis.summary == "测试章节概要"
        assert synopsis.pov_character == "主角"

    def test_chapter_synopsis_with_sections(self):
        """Test synopsis with sections."""
        sections = [
            ChapterSynopsisSection(
                id="sec_1",
                name="开场",
                order=1,
                synopsis_text="开场描述",
            ),
            ChapterSynopsisSection(
                id="sec_2",
                name="发展",
                order=2,
                synopsis_text="发展描述",
            ),
        ]
        synopsis = ChapterSynopsis(
            id="syn_2",
            chapter_number=2,
            title="第2章",
            summary="第二章概要",
            sections=sections,
        )
        assert len(synopsis.sections) == 2
        assert synopsis.sections[0].name == "开场"
        assert synopsis.sections[1].name == "发展"


class TestPlotPointArrangement:
    """Test PlotPointArrangement model."""

    def test_arrangement_creation(self):
        """Test creating a plot point arrangement."""
        points = [
            SynopsisPlotPoint(
                id="pp_1",
                name="转折1",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="转折",
                chapter=4,
                importance=PlotPointImportance.ESSENTIAL,
            ),
            SynopsisPlotPoint(
                id="pp_2",
                name="转折2",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="转折",
                chapter=12,
                importance=PlotPointImportance.ESSENTIAL,
            ),
        ]
        arrangement = PlotPointArrangement(
            id="arr_1",
            plot_points=points,
            total_chapters=24,
        )
        assert arrangement.id == "arr_1"
        assert len(arrangement.plot_points) == 2
        assert arrangement.total_chapters == 24

    def test_chapter_to_points_mapping(self):
        """Test chapter to points mapping."""
        points = [
            SynopsisPlotPoint(
                id="pp_1",
                name="事件1",
                plot_point_type=SynopsisPlotPointType.KEY_EVENT,
                description="事件",
                chapter=3,
            ),
            SynopsisPlotPoint(
                id="pp_2",
                name="事件2",
                plot_point_type=SynopsisPlotPointType.KEY_EVENT,
                description="事件",
                chapter=3,
            ),
        ]
        arrangement = PlotPointArrangement(
            id="arr_2",
            plot_points=points,
            chapter_to_points={"chapter_3": ["pp_1", "pp_2"]},
        )
        assert "chapter_3" in arrangement.chapter_to_points
        assert len(arrangement.chapter_to_points["chapter_3"]) == 2


class TestChapterSynopsisEngine:
    """Test ChapterSynopsisEngine."""

    @pytest.mark.asyncio
    async def test_generate_synopsis(self, engine):
        """Test generating a single chapter synopsis."""
        synopsis = await engine.generate_synopsis(
            chapter_number=1,
            genre="奇幻",
            theme="成长",
        )
        assert synopsis.chapter_number == 1
        assert synopsis.title == "第1章"
        assert len(synopsis.sections) == 4  # opening, development, climax, resolution

    @pytest.mark.asyncio
    async def test_generate_all_synopses(self, engine):
        """Test generating synopses for all chapters."""
        synopses = await engine.generate_all_synopses(
            genre="奇幻",
            theme="成长",
            target_chapters=3,
        )
        assert len(synopses) == 3
        assert synopses[0].chapter_number == 1
        assert synopses[1].chapter_number == 2
        assert synopses[2].chapter_number == 3

    @pytest.mark.asyncio
    async def test_arrange_plot_points(self, engine):
        """Test arranging plot points across chapters."""
        arrangement = await engine.arrange_plot_points(
            genre="奇幻",
            theme="成长",
            target_chapters=24,
        )
        assert arrangement.total_chapters == 24
        assert len(arrangement.plot_points) > 0

    def test_calculate_turning_point_coverage(self, engine):
        """Test turning point coverage calculation."""
        points = [
            SynopsisPlotPoint(
                id="pp_1",
                name="转折1",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="",
                chapter=4,
                importance=PlotPointImportance.ESSENTIAL,
            ),
            SynopsisPlotPoint(
                id="pp_2",
                name="转折2",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="",
                chapter=12,
                importance=PlotPointImportance.ESSENTIAL,
            ),
            SynopsisPlotPoint(
                id="pp_3",
                name="转折3",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="",
                chapter=20,
                importance=PlotPointImportance.ESSENTIAL,
            ),
        ]
        coverage = engine._calculate_turning_point_coverage(points, 24)
        assert coverage == 1.0  # Well distributed

    def test_calculate_turning_point_coverage_poor(self, engine):
        """Test turning point coverage with poor distribution."""
        points = [
            SynopsisPlotPoint(
                id="pp_1",
                name="转折1",
                plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                description="",
                chapter=2,
                importance=PlotPointImportance.ESSENTIAL,
            ),
        ]
        coverage = engine._calculate_turning_point_coverage(points, 24)
        assert coverage < 1.0

    def test_calculate_subplot_balance(self, engine):
        """Test subplot balance calculation."""
        points = [
            SynopsisPlotPoint(
                id="pp_1",
                name="主线1",
                plot_point_type=SynopsisPlotPointType.KEY_EVENT,
                description="",
                chapter=5,
                plot_thread_ids=["thread_main"],
            ),
            SynopsisPlotPoint(
                id="pp_2",
                name="感情线1",
                plot_point_type=SynopsisPlotPointType.KEY_EVENT,
                description="",
                chapter=6,
                plot_thread_ids=["thread_romantic"],
            ),
        ]
        thread_to_points = {
            "thread_main": ["pp_1"],
            "thread_romantic": ["pp_2"],
        }
        balance = engine._calculate_subplot_balance(points, thread_to_points)
        assert balance == 1.0  # Equal distribution

    def test_infer_act(self, engine):
        """Test act inference from chapter number."""
        assert engine._infer_act(1, 24) == 1
        assert engine._infer_act(8, 24) == 1
        assert engine._infer_act(9, 24) == 2
        assert engine._infer_act(16, 24) == 2
        assert engine._infer_act(17, 24) == 3
        assert engine._infer_act(24, 24) == 3

    @pytest.mark.asyncio
    async def test_analyze_synopsis(self, engine):
        """Test synopsis analysis."""
        synopses = [
            ChapterSynopsis(
                id="syn_1",
                chapter_number=1,
                title="第1章",
                summary="测试",
                detailed_synopsis="详细测试内容" * 20,
                pov_character="主角",
                characters_present=["主角", "配角"],
                character_development=["角色成长1"],
                foreshadowing_planted=["f1"],
            ),
            ChapterSynopsis(
                id="syn_2",
                chapter_number=2,
                title="第2章",
                summary="测试2",
                detailed_synopsis="详细测试内容" * 20,
                pov_character="主角",
                characters_present=["主角"],
                foreshadowing_payoffs=["f1"],
            ),
        ]
        arrangement = PlotPointArrangement(
            id="arr_1",
            plot_points=[
                SynopsisPlotPoint(
                    id="pp_1",
                    name="事件1",
                    plot_point_type=SynopsisPlotPointType.KEY_EVENT,
                    description="",
                    chapter=1,
                    plot_thread_ids=["thread_main"],
                ),
            ],
            total_chapters=24,
            chapter_to_points={"chapter_1": ["pp_1"]},
            thread_to_points={"thread_main": ["pp_1"]},
        )

        analysis = await engine.analyze_synopsis(synopses, arrangement)
        assert analysis.chapter_coverage == 2 / 24
        assert analysis.plot_point_coverage == 1 / 24
        assert analysis.coherence_score > 0
        assert analysis.completeness_score > 0

    def test_get_synopsis_summary(self, engine):
        """Test getting synopsis summary."""
        synopses = [
            ChapterSynopsis(
                id="syn_1",
                chapter_number=1,
                title="序章",
                summary="开场介绍",
                is_prologue=True,
            ),
            ChapterSynopsis(
                id="syn_2",
                chapter_number=2,
                title="新的开始",
                summary="主角踏上旅程",
            ),
            ChapterSynopsis(
                id="syn_3",
                chapter_number=24,
                title="尾声",
                summary="故事结束",
                is_epilogue=True,
            ),
        ]
        summary = engine.get_synopsis_summary(synopses)
        assert "总章节数" in summary
        assert "序章" in summary
        assert "尾声" in summary

    def test_export_synopsis(self, engine):
        """Test exporting synopsis to dict."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="第1章",
            summary="测试概要",
            pov_character="主角",
            characters_present=["主角", "配角"],
            status=SynopsisPlotPointStatus.COMPLETE,
        )
        exported = engine.export_synopsis(synopsis)
        assert exported["id"] == "syn_1"
        assert exported["chapter_number"] == 1
        assert exported["title"] == "第1章"
        assert exported["pov_character"] == "主角"

    def test_export_arrangement(self, engine):
        """Test exporting arrangement to dict."""
        arrangement = PlotPointArrangement(
            id="arr_1",
            plot_points=[
                SynopsisPlotPoint(
                    id="pp_1",
                    name="转折",
                    plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                    description="重大转折",
                    chapter=8,
                    importance=PlotPointImportance.ESSENTIAL,
                    tension_level="high",
                ),
            ],
            total_chapters=24,
            chapter_to_points={"chapter_8": ["pp_1"]},
        )
        exported = engine.export_arrangement(arrangement)
        assert exported["id"] == "arr_1"
        assert exported["total_chapters"] == 24
        assert len(exported["plot_points"]) == 1


class TestChapterSynopsisEngineInternal:
    """Test internal methods of ChapterSynopsisEngine."""

    def test_extract_key_events(self, engine):
        """Test extracting key events from text."""
        text = "主角来到城镇。这是他第一次离开家乡。城镇很热闹。"
        events = engine._extract_key_events(text)
        assert len(events) <= 3

    def test_infer_tension_level(self, engine):
        """Test tension level inference."""
        assert engine._infer_tension_level("opening", 1) == "low"
        assert engine._infer_tension_level("development", 1) == "moderate"
        assert engine._infer_tension_level("climax", 1) == "high"
        assert engine._infer_tension_level("resolution", 1) == "moderate"

    def test_build_sections(self, engine):
        """Test building chapter sections."""
        ai_data = {
            "sections": {
                "opening": "开场描述",
                "development": "发展描述",
                "climax": "高潮描述",
                "resolution": "收尾描述",
            }
        }
        sections = engine._build_sections(
            synopsis_id="syn_test",
            ai_data=ai_data,
            chapter_number=1,
        )
        assert len(sections) == 4
        assert sections[0].name == "开场"
        assert sections[1].name == "发展"
        assert sections[2].name == "高潮"
        assert sections[3].name == "收尾"


class TestChapterSynopsisAnalysis:
    """Test ChapterSynopsisAnalysis model."""

    def test_analysis_creation(self):
        """Test creating a synopsis analysis."""
        analysis = ChapterSynopsisAnalysis(
            synopsis_id="analysis_1",
            chapter_coverage=0.8,
            pacing_score=0.85,
            coherence_score=0.9,
        )
        assert analysis.synopsis_id == "analysis_1"
        assert analysis.chapter_coverage == 0.8
        assert analysis.pacing_score == 0.85

    def test_analysis_with_issues(self):
        """Test analysis with identified issues."""
        analysis = ChapterSynopsisAnalysis(
            synopsis_id="analysis_2",
            identified_issues=["高潮出现过早", "配角戏份不足"],
            recommendations=["调整高潮位置", "增加配角出场"],
        )
        assert len(analysis.identified_issues) == 2
        assert len(analysis.recommendations) == 2


class TestSynopsisPlotPointTypes:
    """Test plot point type enum."""

    def test_all_plot_point_types(self):
        """Test all plot point types are accessible."""
        assert SynopsisPlotPointType.TURNING_POINT.value == "turning_point"
        assert SynopsisPlotPointType.CLIMAX.value == "climax"
        assert SynopsisPlotPointType.KEY_EVENT.value == "key_event"
        assert SynopsisPlotPointType.COMPLICATION.value == "complication"
        assert SynopsisPlotPointType.REVELATION.value == "revelation"
        assert SynopsisPlotPointType.DECISION_POINT.value == "decision_point"

    def test_plot_point_importance(self):
        """Test plot point importance levels."""
        assert PlotPointImportance.ESSENTIAL.value == "essential"
        assert PlotPointImportance.IMPORTANT.value == "important"
        assert PlotPointImportance.NOTABLE.value == "notable"
        assert PlotPointImportance.MINOR.value == "minor"


class TestChapterSynopsisSection:
    """Test ChapterSynopsisSection model."""

    def test_section_creation(self):
        """Test creating a section."""
        section = ChapterSynopsisSection(
            id="sec_1",
            name="开场",
            order=1,
            synopsis_text="开场内容",
            key_events=["事件1", "事件2"],
            tension_level="low",
        )
        assert section.id == "sec_1"
        assert section.name == "开场"
        assert section.order == 1
        assert len(section.key_events) == 2
        assert section.tension_level == "low"