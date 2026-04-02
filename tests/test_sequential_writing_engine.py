"""Tests for SequentialWritingEngine."""

import pytest
from chai.models.sequential_writing import (
    SequentialWritingStatus,
    WritingOrderMode,
    ChapterWritingState,
    SequentialWritingConfig,
    SequentialChapterProgress,
    SequentialWritingProgress,
    SequentialWritingRequest,
    SequentialWritingResult,
    SequentialWritingSummary,
    CheckpointInfo,
)
from chai.models.complete_outline import (
    CompleteOutlineComponents,
    ChapterOutlinePlan,
    VolumeOutlinePlan,
    OutlineComponentStatus,
    SubplotOutlinePlan,
    ForeshadowingOutlinePlan,
    ClimaxOutlinePlan,
    EndingOutlinePlan,
)
from chai.engines.sequential_writing_engine import SequentialWritingEngine


class TestSequentialWritingModels:
    """Test sequential writing models."""

    def test_sequential_writing_config_defaults(self):
        """Test SequentialWritingConfig default values."""
        config = SequentialWritingConfig()
        assert config.order_mode == WritingOrderMode.SEQUENTIAL
        assert config.start_chapter == 1
        assert config.end_chapter is None
        assert config.auto_checkpoint is True
        assert config.checkpoint_interval == 1
        assert config.skip_completed is True
        assert config.validate_outline is True

    def test_sequential_chapter_progress_defaults(self):
        """Test SequentialChapterProgress default values."""
        progress = SequentialChapterProgress(chapter_number=1)
        assert progress.chapter_number == 1
        assert progress.chapter_title == ""
        assert progress.state == ChapterWritingState.PENDING
        assert progress.word_count == 0
        assert progress.target_word_count == 3000
        assert progress.started_at is None
        assert progress.completed_at is None
        assert progress.error_message is None
        assert progress.retry_count == 0

    def test_sequential_writing_progress_defaults(self):
        """Test SequentialWritingProgress default values."""
        progress = SequentialWritingProgress()
        assert progress.total_chapters == 0
        assert progress.completed_chapters == 0
        assert progress.in_progress_chapter is None
        assert progress.total_word_count == 0
        assert progress.average_word_count == 0
        assert progress.estimated_remaining_words == 0
        assert progress.progress_percentage == 0.0
        assert progress.chapter_progress == []

    def test_checkpoint_info(self):
        """Test CheckpointInfo model."""
        checkpoint = CheckpointInfo(
            checkpoint_id="cp_123",
            chapter_number=5,
            created_at="2024-01-01T00:00:00",
            total_word_count=15000,
            completed_chapters=[1, 2, 3, 4, 5],
        )
        assert checkpoint.checkpoint_id == "cp_123"
        assert checkpoint.chapter_number == 5
        assert len(checkpoint.completed_chapters) == 5


class TestSequentialWritingEngine:
    """Test SequentialWritingEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SequentialWritingEngine(ai_service=None)

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine is not None
        assert self.engine.ai_service is None
        assert self.engine.chapter_body_engine is None
        assert self.engine.incremental_engine is not None

    def test_determine_chapter_order_sequential(self):
        """Test sequential chapter ordering."""
        components = self._create_sample_components()
        config = SequentialWritingConfig(order_mode=WritingOrderMode.SEQUENTIAL)
        completed = []

        order = self.engine._determine_chapter_order(components, config, completed)

        # Should be in chapter number order
        assert [c.chapter_number for c in order] == [1, 2, 3]

    def test_determine_chapter_order_volume_first(self):
        """Test volume-first chapter ordering."""
        components = self._create_sample_components_with_volumes()
        config = SequentialWritingConfig(order_mode=WritingOrderMode.VOLUME_FIRST)
        completed = []

        order = self.engine._determine_chapter_order(components, config, completed)

        # Should be sorted by volume first, then chapter
        assert order[0].volume_index == 1
        assert order[0].chapter_number == 1

    def test_determine_chapter_order_skip_completed(self):
        """Test skipping completed chapters."""
        components = self._create_sample_components()
        config = SequentialWritingConfig(skip_completed=True)
        completed = [1, 2]

        order = self.engine._determine_chapter_order(components, config, completed)

        # Chapter 3 only
        assert len(order) == 1
        assert order[0].chapter_number == 3

    def test_determine_chapter_order_range(self):
        """Test chapter range filtering."""
        components = self._create_sample_components()
        config = SequentialWritingConfig(start_chapter=2, end_chapter=2)
        completed = []

        order = self.engine._determine_chapter_order(components, config, completed)

        assert len(order) == 1
        assert order[0].chapter_number == 2

    def test_validate_outline_components_valid(self):
        """Test outline validation with valid components."""
        components = self._create_sample_components()

        result = self.engine._validate_outline_components(components)

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_outline_components_empty(self):
        """Test outline validation with empty chapters."""
        components = CompleteOutlineComponents(chapters=[])

        result = self.engine._validate_outline_components(components)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_outline_components_duplicates(self):
        """Test outline validation detects duplicate chapters."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(chapter_number=1, chapter_title="Ch1", volume_index=1),
                ChapterOutlinePlan(chapter_number=1, chapter_title="Ch1", volume_index=1),  # Duplicate
            ]
        )

        result = self.engine._validate_outline_components(components)

        assert result["is_valid"] is False

    def test_outline_plan_to_synopsis(self):
        """Test converting outline plan to synopsis."""
        components = self._create_sample_components()
        plan = components.chapters[0]

        synopsis = self.engine._outline_plan_to_synopsis(plan, components)

        assert synopsis.chapter_number == 1
        assert synopsis.title == "第一章"
        assert synopsis.word_count_target == 3000

    def test_create_minimal_body(self):
        """Test creating minimal body without AI."""
        plan = ChapterOutlinePlan(
            chapter_number=1,
            chapter_title="第一章",
            volume_index=1,
            synopsis="测试章节内容",
        )
        from chai.models.chapter_synopsis import ChapterSynopsis
        synopsis = ChapterSynopsis(
            id="syn_1",
            chapter_number=1,
            title="第一章",
            summary="测试",
            detailed_synopsis="这是测试章节的详细内容。",
        )

        body = self.engine._create_minimal_body(plan, synopsis)

        assert body.chapter_number == 1
        assert body.title == "第一章"
        assert body.status.value == "complete"
        assert body.word_count > 0

    def test_parse_outline_components(self):
        """Test parsing outline components from dict."""
        data = {
            "volumes": [
                {
                    "volume_index": 1,
                    "volume_title": "第一卷",
                    "chapter_count": 3,
                    "chapter_start": 1,
                    "chapter_end": 3,
                }
            ],
            "chapters": [
                {
                    "chapter_number": 1,
                    "chapter_title": "第一章",
                    "volume_index": 1,
                }
            ],
            "subplots": [],
            "foreshadowing": [],
            "climax": [],
            "ending": None,
        }

        components = self.engine._parse_outline_components(data)

        assert components is not None
        assert len(components.chapters) == 1
        assert len(components.volumes) == 1

    def test_parse_outline_components_invalid(self):
        """Test parsing invalid outline components."""
        data = {"invalid": "data"}

        components = self.engine._parse_outline_components(data)

        # Returns empty components rather than None when parsing doesn't throw
        assert components is not None
        assert len(components.chapters) == 0

    def test_get_next_chapter(self):
        """Test getting next chapter to write."""
        components = self._create_sample_components()

        next_ch = self.engine.get_next_chapter(components, [])

        assert next_ch is not None
        assert next_ch.chapter_number == 1

    def test_get_next_chapter_all_completed(self):
        """Test getting next chapter when all completed."""
        components = self._create_sample_components()

        next_ch = self.engine.get_next_chapter(components, [1, 2, 3])

        assert next_ch is None

    def test_get_summary(self):
        """Test getting writing summary."""
        from chai.models.chapter_body import ManuscriptStatus

        result = SequentialWritingResult(
            success=True,
            writing_id="writing_123",
            project_id="proj_123",
            status=SequentialWritingStatus.IN_PROGRESS,
            progress=SequentialWritingProgress(
                total_chapters=3,
                completed_chapters=1,
                total_word_count=3000,
                progress_percentage=33.33,
                chapter_progress=[
                    SequentialChapterProgress(chapter_number=1, state=ChapterWritingState.COMPLETE),
                    SequentialChapterProgress(chapter_number=2, state=ChapterWritingState.PENDING),
                    SequentialChapterProgress(chapter_number=3, state=ChapterWritingState.PENDING),
                ],
            ),
        )

        summary = self.engine.get_summary(result, "测试小说")

        assert summary.project_title == "测试小说"
        assert summary.total_chapters == 3
        assert summary.completed_chapters == 1
        assert summary.next_chapter_to_write == 2

    def test_export_writing_package(self):
        """Test exporting writing package."""
        result = SequentialWritingResult(
            success=True,
            writing_id="writing_123",
            project_id="proj_123",
            status=SequentialWritingStatus.COMPLETE,
            progress=SequentialWritingProgress(
                total_chapters=3,
                completed_chapters=3,
                total_word_count=9000,
                progress_percentage=100.0,
            ),
            last_chapter_completed=3,
            last_checkpoint_id="cp_123",
        )

        package = self.engine.export_writing_package(result, "proj_123")

        assert package["project_id"] == "proj_123"
        assert package["writing_id"] == "writing_123"
        assert package["last_chapter_completed"] == 3
        assert "exported_at" in package

    # Helper methods

    def _create_sample_components(self) -> CompleteOutlineComponents:
        """Create sample outline components for testing."""
        return CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=3,
                    chapter_start=1,
                    chapter_end=3,
                )
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=1,
                    chapter_title="第一章",
                    volume_index=1,
                    synopsis="第一章内容",
                    word_count_target=3000,
                ),
                ChapterOutlinePlan(
                    chapter_number=2,
                    chapter_title="第二章",
                    volume_index=1,
                    synopsis="第二章内容",
                    word_count_target=3000,
                ),
                ChapterOutlinePlan(
                    chapter_number=3,
                    chapter_title="第三章",
                    volume_index=1,
                    synopsis="第三章内容",
                    word_count_target=3000,
                ),
            ],
            subplots=[],
            foreshadowing=[],
            climax=[],
            ending=None,
        )

    def _create_sample_components_with_volumes(self) -> CompleteOutlineComponents:
        """Create sample outline components with multiple volumes."""
        return CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=2,
                    chapter_start=1,
                    chapter_end=2,
                ),
                VolumeOutlinePlan(
                    volume_index=2,
                    volume_title="第二卷",
                    chapter_count=2,
                    chapter_start=3,
                    chapter_end=4,
                ),
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=1,
                    chapter_title="第一章",
                    volume_index=1,
                    synopsis="内容1",
                ),
                ChapterOutlinePlan(
                    chapter_number=2,
                    chapter_title="第二章",
                    volume_index=1,
                    synopsis="内容2",
                ),
                ChapterOutlinePlan(
                    chapter_number=3,
                    chapter_title="第三章",
                    volume_index=2,
                    synopsis="内容3",
                ),
                ChapterOutlinePlan(
                    chapter_number=4,
                    chapter_title="第四章",
                    volume_index=2,
                    synopsis="内容4",
                ),
            ],
            subplots=[],
            foreshadowing=[],
            climax=[],
            ending=None,
        )


class TestSequentialWritingRequestValidation:
    """Test SequentialWritingRequest validation."""

    def test_request_requires_project_id(self):
        """Test request requires project_id."""
        request = SequentialWritingRequest(
            project_id="proj_123",
            project_title="测试小说",
            outline_components={},
        )
        assert request.project_id == "proj_123"

    def test_request_with_outline_components(self):
        """Test request with full outline components."""
        components = {
            "chapters": [
                {
                    "chapter_number": 1,
                    "chapter_title": "第一章",
                    "volume_index": 1,
                }
            ]
        }
        request = SequentialWritingRequest(
            project_id="proj_123",
            project_title="测试小说",
            genre="玄幻",
            outline_components=components,
        )
        assert request.outline_components is not None


class TestChapterWritingStateTransitions:
    """Test chapter writing state transitions."""

    def test_state_defaults_to_pending(self):
        """Test state defaults to pending."""
        progress = SequentialChapterProgress(chapter_number=1)
        assert progress.state == ChapterWritingState.PENDING

    def test_state_transitions(self):
        """Test state can be updated."""
        progress = SequentialChapterProgress(chapter_number=1)
        progress.state = ChapterWritingState.IN_PROGRESS
        assert progress.state == ChapterWritingState.IN_PROGRESS

        progress.state = ChapterWritingState.COMPLETE
        assert progress.state == ChapterWritingState.COMPLETE

        progress.state = ChapterWritingState.FAILED
        assert progress.state == ChapterWritingState.FAILED
