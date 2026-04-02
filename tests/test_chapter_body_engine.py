"""Unit tests for chapter body engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from chai.engines.chapter_body_engine import ChapterBodyEngine
from chai.models.chapter_body import (
    ChapterBodyStatus,
    ChapterBodySectionType,
    ChapterBodySection,
    ChapterBody,
    ManuscriptStatus,
    ChapterGenerationProgress,
    ManuscriptBody,
    ManuscriptGenerationRequest,
    ManuscriptGenerationResult,
    ChapterBodyAnalysis,
)
from chai.models.chapter_synopsis import (
    ChapterSynopsis,
    SynopsisPlotPointStatus,
)
from chai.models.chapter_content import (
    ChapterContentDraft,
    ChapterContentStatus,
    ChapterSectionContent,
    NarrativePoint,
)


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    service = MagicMock()
    service.generate = AsyncMock(return_value="这是一个测试章节内容。主角来到城镇，遇到了新的挑战。突然，事情发生了转折。主角做出了重要的决定。经过一番波折，故事暂时告一段落，但仍有悬念留存。")
    return service


@pytest.fixture
def engine(mock_ai_service):
    """Create a chapter body engine with mock service."""
    return ChapterBodyEngine(mock_ai_service)


class TestChapterBodyModels:
    """Test chapter body models."""

    def test_chapter_body_creation(self):
        """Test creating a chapter body."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="测试内容",
            word_count=100,
        )
        assert body.id == "body_1"
        assert body.chapter_number == 1
        assert body.word_count == 100
        assert body.status == ChapterBodyStatus.PENDING

    def test_chapter_body_defaults(self):
        """Test chapter body default values."""
        body = ChapterBody(
            id="body_2",
            chapter_number=2,
            title="第2章",
        )
        assert body.chapter_type == "normal"
        assert body.meets_target is False
        assert body.coherence_score == 0.0
        assert body.has_plot_advancement is False

    def test_chapter_body_section_creation(self):
        """Test creating a chapter body section."""
        section = ChapterBodySection(
            id="sec_1",
            order=1,
            section_type=ChapterBodySectionType.NARRATIVE,
            content="开场内容",
            word_count=500,
        )
        assert section.order == 1
        assert section.section_type == ChapterBodySectionType.NARRATIVE
        assert section.word_count == 500

    def test_manuscript_body_creation(self):
        """Test creating a manuscript body."""
        manuscript = ManuscriptBody(
            id="manuscript_1",
            title="测试小说",
            genre="奇幻",
        )
        assert manuscript.id == "manuscript_1"
        assert manuscript.title == "测试小说"
        assert manuscript.status == ManuscriptStatus.PENDING
        assert manuscript.total_chapters == 0

    def test_manuscript_generation_request(self):
        """Test creating a generation request."""
        request = ManuscriptGenerationRequest(
            chapter_synopses=[{"id": "syn_1", "chapter_number": 1}],
        )
        assert len(request.chapter_synopses) == 1
        assert request.start_chapter == 1
        assert request.parallel_generation is False

    def test_manuscript_generation_result_defaults(self):
        """Test generation result default values."""
        result = ManuscriptGenerationResult(success=True)
        assert result.total_chapters == 0
        assert result.total_word_count == 0
        assert result.average_coherence == 0.0

    def test_chapter_generation_progress(self):
        """Test chapter generation progress."""
        progress = ChapterGenerationProgress(
            chapter_number=1,
            title="第1章",
        )
        assert progress.status == ChapterBodyStatus.PENDING
        assert progress.word_count == 0
        assert progress.retry_count == 0


class TestChapterBodyEngine:
    """Test ChapterBodyEngine."""

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine is not None
        assert hasattr(engine, 'ai_service')
        assert hasattr(engine, 'content_engine')

    def test_get_chapter_type_prologue(self, engine):
        """Test getting chapter type for prologue."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=0,
            title="序章",
            summary="序章概要",
            is_prologue=True,
        )
        result = engine._get_chapter_type(synopsis)
        assert result == "prologue"

    def test_get_chapter_type_epilogue(self, engine):
        """Test getting chapter type for epilogue."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=24,
            title="尾声",
            summary="尾声概要",
            is_epilogue=True,
        )
        result = engine._get_chapter_type(synopsis)
        assert result == "epilogue"

    def test_get_chapter_type_climax(self, engine):
        """Test getting chapter type for climax."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=20,
            title="第20章",
            summary="高潮章节概要",
            is_climax_chapter=True,
        )
        result = engine._get_chapter_type(synopsis)
        assert result == "climax"

    def test_get_chapter_type_bridge(self, engine):
        """Test getting chapter type for bridge."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=10,
            title="过渡章",
            summary="过渡章节概要",
            is_bridge=True,
        )
        result = engine._get_chapter_type(synopsis)
        assert result == "bridge"

    def test_get_chapter_type_normal(self, engine):
        """Test getting chapter type for normal."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=5,
            title="第5章",
            summary="普通章节概要",
        )
        result = engine._get_chapter_type(synopsis)
        assert result == "normal"

    def test_narrative_to_section_type(self, engine):
        """Test converting narrative point to section type."""
        assert engine._narrative_to_section_type("opening") == ChapterBodySectionType.NARRATIVE
        assert engine._narrative_to_section_type("complication") == ChapterBodySectionType.ACTION
        assert engine._narrative_to_section_type("climax") == ChapterBodySectionType.NARRATIVE
        assert engine._narrative_to_section_type("development") == ChapterBodySectionType.NARRATIVE

    def test_draft_to_sections(self, engine):
        """Test converting draft to sections."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="第1章",
            summary="测试",
            plot_point_ids=["pp_1"],
        )
        draft = ChapterContentDraft(
            id="draft_1",
            plan_id="plan_1",
            chapter_number=1,
            title="第1章",
            content="测试内容",
            section_contents=[
                ChapterSectionContent(
                    id="sec_1",
                    narrative_point=NarrativePoint.OPENING,
                    order=1,
                    content="开场",
                    word_count=100,
                ),
                ChapterSectionContent(
                    id="sec_2",
                    narrative_point=NarrativePoint.DEVELOPMENT,
                    order=2,
                    content="发展",
                    word_count=200,
                ),
            ],
            word_count=300,
        )

        sections = engine._draft_to_sections(draft, synopsis)

        assert len(sections) == 2
        assert sections[0].order == 1
        assert sections[0].content == "开场"
        assert sections[1].order == 2
        assert sections[1].content == "发展"

    def test_get_manuscript_summary(self, engine):
        """Test getting manuscript summary."""
        manuscript = ManuscriptBody(
            id="manuscript_1",
            title="测试小说",
            genre="奇幻",
            total_chapters=10,
            completed_chapters=5,
            total_word_count=15000,
            status=ManuscriptStatus.IN_PROGRESS,
            average_coherence=0.85,
            average_pacing=0.80,
        )

        summary = engine.get_manuscript_summary(manuscript)

        assert summary["title"] == "测试小说"
        assert summary["total_chapters"] == 10
        assert summary["completed_chapters"] == 5
        assert summary["progress_percentage"] == 50.0

    def test_export_manuscript(self, engine):
        """Test exporting manuscript."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="测试内容",
            word_count=100,
            status=ChapterBodyStatus.COMPLETE,
        )
        manuscript = ManuscriptBody(
            id="manuscript_1",
            title="测试小说",
            genre="奇幻",
            chapters=[body],
            total_chapters=1,
            completed_chapters=1,
            total_word_count=100,
        )

        exported = engine.export_manuscript(manuscript)

        assert exported["title"] == "测试小说"
        assert len(exported["chapters"]) == 1
        assert exported["chapters"][0]["chapter_number"] == 1


class TestChapterBodyAnalysis:
    """Test chapter body analysis."""

    def test_analyze_chapter_body_basic(self, engine):
        """Test basic chapter body analysis."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="这是一个测试章节。主角来到一个新的地方，突然遇到了意想不到的事情。故事在这里暂时告一段落。",
            word_count=50,
            coherence_score=0.8,
            pacing_score=0.75,
            character_voice_score=0.7,
        )

        analysis = engine.analyze_chapter_body(body)

        assert analysis.chapter_id == "body_1"
        assert analysis.word_count_ratio > 0
        assert analysis.has_clear_opening is True
        assert analysis.overall_quality_score > 0

    def test_analyze_chapter_body_short(self, engine):
        """Test analysis of short chapter."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="短内容",
            word_count=10,
        )

        analysis = engine.analyze_chapter_body(body)

        assert len(analysis.critical_issues) > 0
        assert "字数过少" in analysis.critical_issues[0]

    def test_analyze_chapter_body_with_climax_keywords(self, engine):
        """Test analysis detects climax keywords."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="就在此时，主角突然发现了真相。没想到事情竟然是这样的。刹那间，一切都改变了。",
            word_count=40,
        )

        analysis = engine.analyze_chapter_body(body)

        assert analysis.has_climax is True


@pytest.mark.asyncio
class TestChapterBodyEngineAsync:
    """Test async methods of ChapterBodyEngine."""

    async def test_generate_chapter_body_basic(self, engine):
        """Test basic chapter body generation."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="第1章",
            summary="测试章节概要",
            pov_character="主角",
            characters_present=["主角", "配角"],
            primary_location="城镇",
            time_setting="第一天",
            word_count_target=3000,
        )

        body = await engine.generate_chapter_body(synopsis)

        assert body is not None
        assert body.chapter_number == 1
        assert body.title == "第1章"
        assert len(body.content) > 0
        assert body.word_count > 0
        assert body.status == ChapterBodyStatus.COMPLETE

    async def test_generate_chapter_body_with_previous(self, engine):
        """Test chapter generation with previous chapter."""
        synopsis = ChapterSynopsis(
            id="syn_2",
            chapter_number=2,
            title="第2章",
            summary="第二章概要",
        )

        previous_body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="这是第一章的内容。主角离开了家乡，踏上了新的旅程。",
            word_count=30,
            status=ChapterBodyStatus.COMPLETE,
        )

        body = await engine.generate_chapter_body(
            synopsis,
            previous_chapter_body=previous_body,
        )

        assert body is not None
        assert body.chapter_number == 2

    async def test_generate_manuscript_basic(self, engine):
        """Test basic manuscript generation."""
        request = ManuscriptGenerationRequest(
            chapter_synopses=[
                {
                    "id": "syn_1",
                    "chapter_number": 1,
                    "title": "第1章",
                    "summary": "第一章概要",
                    "pov_character": "主角",
                    "characters_present": ["主角"],
                    "primary_location": "城镇",
                    "time_setting": "第一天",
                    "word_count_target": 3000,
                },
                {
                    "id": "syn_2",
                    "chapter_number": 2,
                    "title": "第2章",
                    "summary": "第二章概要",
                    "pov_character": "主角",
                    "characters_present": ["主角"],
                    "primary_location": "城镇",
                    "time_setting": "第二天",
                    "word_count_target": 3000,
                },
            ],
        )

        result = await engine.generate_manuscript(request)

        assert result is not None
        assert result.total_chapters == 2
        assert result.total_word_count > 0
        assert result.success is True

    async def test_generate_manuscript_with_world_setting(self, engine):
        """Test manuscript generation with world setting."""
        request = ManuscriptGenerationRequest(
            world_setting={
                "name": "测试世界",
                "genre": "奇幻",
            },
            chapter_synopses=[
                {
                    "id": "syn_1",
                    "chapter_number": 1,
                    "title": "第1章",
                    "summary": "第一章概要",
                    "word_count_target": 3000,
                },
            ],
        )

        result = await engine.generate_manuscript(request)

        assert result is not None
        assert result.manuscript is not None
        assert result.manuscript.title == "测试世界"

    async def test_generate_manuscript_chapter_range(self, engine):
        """Test manuscript generation with chapter range."""
        request = ManuscriptGenerationRequest(
            chapter_synopses=[
                {"id": "syn_1", "chapter_number": 1, "title": "第1章", "summary": "概要"},
                {"id": "syn_2", "chapter_number": 2, "title": "第2章", "summary": "概要"},
                {"id": "syn_3", "chapter_number": 3, "title": "第3章", "summary": "概要"},
            ],
            start_chapter=2,
            end_chapter=3,
        )

        result = await engine.generate_manuscript(request)

        assert result is not None
        assert result.total_chapters == 2

    async def test_revise_chapter_body(self, engine):
        """Test revising chapter body."""
        body = ChapterBody(
            id="body_1",
            chapter_number=1,
            title="第1章",
            content="原始内容",
            word_count=10,
            status=ChapterBodyStatus.COMPLETE,
        )

        revision_notes = ["需要扩展内容", "增加更多细节"]

        revised = await engine.revise_chapter_body(body, revision_notes)

        assert revised is not None
        assert revised.status == ChapterBodyStatus.REVISED


class TestManuscriptStatus:
    """Test manuscript status transitions."""

    def test_manuscript_status_pending(self):
        """Test pending manuscript status."""
        manuscript = ManuscriptBody(
            id="man_1",
            title="测试",
            status=ManuscriptStatus.PENDING,
        )
        assert manuscript.status == ManuscriptStatus.PENDING
        assert manuscript.completed_chapters == 0

    def test_manuscript_status_in_progress(self):
        """Test in-progress manuscript status."""
        manuscript = ManuscriptBody(
            id="man_1",
            title="测试",
            status=ManuscriptStatus.IN_PROGRESS,
        )
        assert manuscript.status == ManuscriptStatus.IN_PROGRESS

    def test_manuscript_status_complete(self):
        """Test complete manuscript status."""
        manuscript = ManuscriptBody(
            id="man_1",
            title="测试",
            status=ManuscriptStatus.COMPLETE,
            completed_chapters=10,
            total_chapters=10,
        )
        assert manuscript.status == ManuscriptStatus.COMPLETE

    def test_manuscript_status_chapters_complete(self):
        """Test chapters-complete manuscript status."""
        manuscript = ManuscriptBody(
            id="man_1",
            title="测试",
            status=ManuscriptStatus.CHAPTERS_COMPLETE,
            completed_chapters=10,
            total_chapters=24,
        )
        assert manuscript.status == ManuscriptStatus.CHAPTERS_COMPLETE
        assert manuscript.completed_chapters < manuscript.total_chapters
