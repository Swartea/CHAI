"""Unit tests for chapter content engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from chai.engines.chapter_content_engine import (
    ChapterContentEngine,
    CHAPTER_TEMPLATES,
)
from chai.models.chapter_content import (
    ChapterContentType,
    ChapterContentStatus,
    ChapterContentPlan,
    ChapterSectionContent,
    ChapterContentDraft,
    ChapterContentRevision,
    ChapterContentAnalysis,
    ChapterContentTemplate,
    NarrativePoint,
    DialogueStyle,
)
from chai.models.chapter_synopsis import (
    ChapterSynopsis,
    SynopsisPlotPointStatus,
)


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    service = MagicMock()
    service.generate = AsyncMock(return_value="这是一个测试章节内容。主角来到城镇，遇到了新的挑战。突然，事情发生了转折。主角做出了重要的决定。经过一番波折，故事暂时告一段落，但仍有悬念留存。")
    return service


@pytest.fixture
def engine(mock_ai_service):
    """Create a chapter content engine with mock service."""
    return ChapterContentEngine(mock_ai_service)


class TestChapterContentModels:
    """Test chapter content models."""

    def test_chapter_content_plan_creation(self):
        """Test creating a chapter content plan."""
        plan = ChapterContentPlan(
            id="plan_1",
            chapter_synopsis_id="syn_1",
            chapter_number=1,
            title="第1章",
            target_word_count=3000,
        )
        assert plan.id == "plan_1"
        assert plan.chapter_number == 1
        assert plan.target_word_count == 3000
        assert plan.status == ChapterContentStatus.PENDING

    def test_chapter_content_plan_defaults(self):
        """Test plan default values."""
        plan = ChapterContentPlan(
            id="plan_2",
            chapter_synopsis_id="syn_2",
            chapter_number=2,
            title="第2章",
        )
        assert plan.chapter_type == ChapterContentType.NORMAL
        assert plan.min_word_count == 2000
        assert plan.max_word_count == 4000
        assert plan.dialogue_style == DialogueStyle.MIXED

    def test_chapter_section_content_creation(self):
        """Test creating section content."""
        section = ChapterSectionContent(
            id="sec_1",
            narrative_point=NarrativePoint.OPENING,
            order=1,
            content="开场内容",
            word_count=500,
        )
        assert section.narrative_point == NarrativePoint.OPENING
        assert section.content == "开场内容"
        assert section.word_count == 500

    def test_chapter_content_draft_creation(self):
        """Test creating a content draft."""
        draft = ChapterContentDraft(
            id="draft_1",
            plan_id="plan_1",
            chapter_number=1,
            title="第1章",
            content="章节正文内容",
            word_count=3000,
        )
        assert draft.id == "draft_1"
        assert draft.word_count == 3000
        assert draft.status == ChapterContentStatus.PENDING

    def test_chapter_content_revision_creation(self):
        """Test creating a revision."""
        revision = ChapterContentRevision(
            id="rev_1",
            draft_id="draft_1",
            revision_type="minor",
            issues=["对话不够自然"],
            changes_needed=["修改对话部分"],
        )
        assert revision.revision_type == "minor"
        assert len(revision.issues) == 1
        assert revision.priority == 1

    def test_chapter_content_analysis_defaults(self):
        """Test analysis default values."""
        analysis = ChapterContentAnalysis(draft_id="draft_1")
        assert analysis.structure_score == 0.0
        assert analysis.pacing_score == 0.0
        assert analysis.overall_quality_score == 0.0


class TestChapterContentEngine:
    """Test ChapterContentEngine."""

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine is not None
        assert hasattr(engine, 'ai_service')

    def test_get_template_normal(self, engine):
        """Test getting normal chapter template."""
        template = engine.get_template(ChapterContentType.NORMAL)
        assert template.id == "normal_template"
        assert ChapterContentType.NORMAL in template.chapter_types

    def test_get_template_prologue(self, engine):
        """Test getting prologue template."""
        template = engine.get_template(ChapterContentType.PROLOGUE)
        assert template.id == "prologue_template"

    def test_get_template_climax(self, engine):
        """Test getting climax chapter template."""
        template = engine.get_template(ChapterContentType.CLIMAX)
        assert template.id == "climax_template"
        assert template.dialogue_ratio == 0.35

    def test_get_template_unknown(self, engine):
        """Test getting template for unknown type returns normal."""
        template = engine.get_template(ChapterContentType.TRANSITION)
        assert template.id == "transition_template"

    def test_determine_chapter_type_prologue(self, engine):
        """Test determining prologue chapter type."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="序章",
            summary="序章概要",
            is_prologue=True,
        )
        result = engine._determine_chapter_type(synopsis)
        assert result == ChapterContentType.PROLOGUE

    def test_determine_chapter_type_epilogue(self, engine):
        """Test determining epilogue chapter type."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=24,
            title="尾声",
            summary="尾声概要",
            is_epilogue=True,
        )
        result = engine._determine_chapter_type(synopsis)
        assert result == ChapterContentType.EPILOGUE

    def test_determine_chapter_type_climax(self, engine):
        """Test determining climax chapter type."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=20,
            title="第20章",
            summary="高潮章节概要",
            is_climax_chapter=True,
        )
        result = engine._determine_chapter_type(synopsis)
        assert result == ChapterContentType.CLIMAX

    def test_determine_chapter_type_bridge(self, engine):
        """Test determining bridge chapter type."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=10,
            title="过渡章",
            summary="过渡章节概要",
            is_bridge=True,
        )
        result = engine._determine_chapter_type(synopsis)
        assert result == ChapterContentType.BRIDGE

    def test_determine_chapter_type_normal(self, engine):
        """Test determining normal chapter type."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=5,
            title="第5章",
            summary="普通章节概要",
        )
        result = engine._determine_chapter_type(synopsis)
        assert result == ChapterContentType.NORMAL

    def test_count_chinese_words(self, engine):
        """Test Chinese word counting."""
        text = "这是一个测试句子。"
        count = engine._count_chinese_words(text)
        assert count == 8

    def test_count_chinese_words_empty(self, engine):
        """Test counting empty text."""
        count = engine._count_chinese_words("")
        assert count == 0

    def test_count_chinese_words_mixed(self, engine):
        """Test counting mixed Chinese and English."""
        text = "Hello世界"
        count = engine._count_chinese_words(text)
        # Hello(5) + 世界(2) = 7
        assert count == 7

    def test_export_draft(self, engine):
        """Test exporting draft as dict."""
        draft = ChapterContentDraft(
            id="draft_1",
            plan_id="plan_1",
            chapter_number=1,
            title="第1章",
            content="测试内容",
            word_count=100,
        )
        exported = engine.export_draft(draft)
        assert exported["id"] == "draft_1"
        assert exported["chapter_number"] == 1
        assert exported["word_count"] == 100
        assert exported["meets_target"] is False


class TestChapterTemplates:
    """Test chapter content templates."""

    def test_normal_template_structure(self):
        """Test normal template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.NORMAL]
        assert len(template.section_structure) == 4
        assert template.dialogue_ratio == 0.3
        assert template.has_hook_ending is True

    def test_prologue_template_structure(self):
        """Test prologue template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.PROLOGUE]
        assert len(template.section_structure) == 4
        assert template.dialogue_ratio == 0.2
        assert template.has_hook_ending is True

    def test_climax_template_structure(self):
        """Test climax template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.CLIMAX]
        assert len(template.section_structure) == 4
        assert template.dialogue_ratio == 0.35
        assert NarrativePoint.CLIMAX in [s["narrative_point"] for s in template.section_structure]

    def test_epilogue_template_structure(self):
        """Test epilogue template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.EPILOGUE]
        assert len(template.section_structure) == 3
        assert template.has_hook_ending is False

    def test_bridge_template_structure(self):
        """Test bridge template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.BRIDGE]
        assert len(template.section_structure) == 3
        assert template.has_hook_ending is True

    def test_transition_template_structure(self):
        """Test transition template has correct structure."""
        template = CHAPTER_TEMPLATES[ChapterContentType.TRANSITION]
        assert len(template.section_structure) == 2
        assert template.has_scene_breaks is False


@pytest.mark.asyncio
class TestChapterContentEngineAsync:
    """Test async methods of ChapterContentEngine."""

    async def test_generate_content_basic(self, engine):
        """Test basic content generation."""
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

        draft = await engine.generate_content(synopsis)

        assert draft is not None
        assert draft.chapter_number == 1
        assert draft.title == "第1章"
        assert len(draft.content) > 0
        assert draft.word_count > 0

    async def test_generate_content_with_prologue(self, engine):
        """Test prologue content generation."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=0,
            title="序章",
            summary="序章概要",
            is_prologue=True,
        )

        draft = await engine.generate_content(synopsis)

        assert draft is not None
        assert len(draft.content) > 0

    async def test_generate_content_with_climax(self, engine):
        """Test climax chapter content generation."""
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=20,
            title="第20章",
            summary="高潮章节",
            is_climax_chapter=True,
        )

        draft = await engine.generate_content(synopsis)

        assert draft is not None
        assert draft.word_count >= 3000

    async def test_analyze_content(self, engine):
        """Test content analysis."""
        draft = ChapterContentDraft(
            id="draft_1",
            plan_id="plan_1",
            chapter_number=1,
            title="第1章",
            content="这是一个测试章节内容。主角来到城镇，遇到了新的挑战。突然，事情发生了转折。主角做出了重要的决定。经过一番波折，故事暂时告一段落。",
            word_count=60,
        )

        plan = ChapterContentPlan(
            id="plan_1",
            chapter_synopsis_id="syn_1",
            chapter_number=1,
            title="第1章",
            target_word_count=3000,
            is_climax_chapter=False,
            foreshadowing_to_plant=[],
            foreshadowing_to_payoff=[],
        )

        analysis = await engine.analyze_content(draft, plan)

        assert analysis is not None
        assert analysis.word_count_ratio > 0

    async def test_revoke_content(self, engine):
        """Test content revision."""
        draft = ChapterContentDraft(
            id="draft_1",
            plan_id="plan_1",
            chapter_number=1,
            title="第1章",
            content="原始内容",
            word_count=100,
        )

        revision = ChapterContentRevision(
            id="rev_1",
            draft_id="draft_1",
            revision_type="minor",
            issues=["内容太短"],
            changes_needed=["扩展内容"],
        )

        revised = await engine.revise_content(draft, revision)

        assert revised is not None
        assert revised.status == ChapterContentStatus.REVISED