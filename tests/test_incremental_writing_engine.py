"""Tests for incremental writing engine."""

import pytest

from chai.engines.incremental_writing_engine import IncrementalWritingEngine
from chai.models.incremental_writing import (
    CheckpointType,
    CheckpointStatus,
    WritingSessionStatus,
    WritingPhase,
    RecoveryStatus,
    Checkpoint,
    WritingSession,
    IncrementalWritingProject,
    ChapterProgress,
    ResumeContext,
    AutoSaveConfig,
)


class TestIncrementalWritingEngine:
    """Test cases for IncrementalWritingEngine."""

    @pytest.fixture
    def engine(self):
        """Create an IncrementalWritingEngine instance."""
        return IncrementalWritingEngine()

    @pytest.fixture
    def sample_project(self, engine):
        """Create a sample IncrementalWritingProject."""
        return engine.create_project(
            novel_id="novel_001",
            title="测试小说",
            genre="玄幻",
            author="测试作者",
            target_total_word_count=80000,
        )

    def test_create_project(self, engine):
        """Test creating a new incremental writing project."""
        project = engine.create_project(
            novel_id="novel_test",
            title="测试书",
            genre="都市",
            author="作者A",
            target_total_word_count=60000,
        )

        assert project.id is not None
        assert project.novel_id == "novel_test"
        assert project.title == "测试书"
        assert project.genre == "都市"
        assert project.author == "作者A"
        assert project.target_total_word_count == 60000
        assert project.total_word_count == 0
        assert len(project.sessions) == 0
        assert len(project.checkpoints) == 0

    def test_start_session(self, engine, sample_project):
        """Test starting a new writing session."""
        session = engine.start_session(sample_project)

        assert session.id is not None
        assert session.novel_id == "novel_001"
        assert session.title == "测试小说"
        assert session.status == WritingSessionStatus.ACTIVE
        assert session.phase == WritingPhase.WRITING_CHAPTER
        assert session.started_at is not None
        assert sample_project.current_session_id == session.id
        assert sample_project.total_sessions_count == 1

    def test_end_session(self, engine, sample_project):
        """Test ending a writing session."""
        session = engine.start_session(sample_project)
        ended_session = engine.end_session(
            sample_project,
            session.id,
            WritingSessionStatus.COMPLETED
        )

        assert ended_session.status == WritingSessionStatus.COMPLETED
        assert ended_session.ended_at is not None

    def test_create_checkpoint(self, engine, sample_project):
        """Test creating a checkpoint."""
        engine.start_session(sample_project)
        checkpoint = engine.create_checkpoint(
            project=sample_project,
            checkpoint_type=CheckpointType.MANUAL,
            chapter_number=1,
            scene_number=1,
            content="第一章的内容...",
            word_count=1500,
            target_word_count=3000,
            continuation_hint="继续描写场景",
            coherence_score=0.8,
            pacing_score=0.75,
        )

        assert checkpoint.id is not None
        assert checkpoint.checkpoint_type == CheckpointType.MANUAL
        assert checkpoint.chapter_number == 1
        assert checkpoint.scene_number == 1
        assert checkpoint.word_count == 1500
        assert checkpoint.target_word_count == 3000
        assert checkpoint.last_content_preview == "第一章的内容..."
        assert checkpoint.continuation_hint == "继续描写场景"
        assert checkpoint.status == CheckpointStatus.CREATED
        assert sample_project.latest_checkpoint_id == checkpoint.id
        assert len(sample_project.checkpoints) == 1

    def test_create_auto_checkpoint(self, engine, sample_project):
        """Test creating an auto-save checkpoint."""
        engine.start_session(sample_project)
        checkpoint = engine.create_checkpoint(
            project=sample_project,
            checkpoint_type=CheckpointType.AUTO,
            chapter_number=2,
            content="第二章自动保存...",
            word_count=2000,
            expires_in_hours=24,
        )

        assert checkpoint.checkpoint_type == CheckpointType.AUTO
        assert checkpoint.expires_at is not None

    def test_save_chapter_progress(self, engine, sample_project):
        """Test saving chapter progress."""
        progress = engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章：开始",
            content="这是第一章的完整内容。",
            word_count=3000,
            target_word_count=3000,
            scenes_completed=3,
            total_scenes=5,
            coherence_score=0.85,
            pacing_score=0.8,
        )

        assert progress.chapter_number == 1
        assert progress.title == "第一章：开始"
        assert progress.word_count == 3000
        assert progress.progress_percentage == 100.0
        assert progress.status == WritingSessionStatus.ACTIVE
        assert sample_project.total_word_count == 3000

    def test_save_chapter_progress_in_progress(self, engine, sample_project):
        """Test saving chapter progress for in-progress chapter."""
        progress = engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章：开始",
            content="这是第一章的部分内容...",
            word_count=1500,
            target_word_count=3000,
        )

        assert progress.progress_percentage == 50.0
        assert 1 in sample_project.in_progress_chapters
        assert 1 not in sample_project.completed_chapters

    def test_mark_chapter_complete(self, engine, sample_project):
        """Test marking a chapter as complete."""
        # First save some progress
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章：开始",
            content="这是完整内容...",
            word_count=3000,
        )

        # Mark as complete
        checkpoint = engine.mark_chapter_complete(
            project=sample_project,
            chapter_number=1,
            content="这是完整内容...",
            word_count=3000,
        )

        assert checkpoint.checkpoint_type == CheckpointType.CHAPTER_COMPLETE
        assert checkpoint.chapter_number == 2  # Next chapter
        assert 1 in sample_project.completed_chapters
        assert 1 not in sample_project.in_progress_chapters

    def test_get_resume_context_no_checkpoint(self, engine, sample_project):
        """Test getting resume context when no checkpoint exists."""
        context = engine.get_resume_context(sample_project)

        assert context.novel_title == "测试小说"
        assert context.genre == "玄幻"
        assert context.last_chapter == 0
        assert context.last_word_count == 0

    def test_get_resume_context_with_checkpoint(self, engine, sample_project):
        """Test getting resume context with checkpoint."""
        # Create a checkpoint
        engine.start_session(sample_project)
        engine.create_checkpoint(
            project=sample_project,
            chapter_number=2,
            scene_number=3,
            content="第二章内容" * 50,
            word_count=2500,
            continuation_hint="继续第二章的场景",
            last_scene_summary="主角遇到导师",
        )

        context = engine.get_resume_context(sample_project)

        assert context.last_chapter == 2
        assert context.last_scene == 3
        assert context.continuation_hint == "继续第二章的场景"
        assert context.last_scene_summary == "主角遇到导师"
        assert context.checkpoint_created_at is not None

    def test_recover_project(self, engine, sample_project):
        """Test project recovery from checkpoint."""
        # Set up some data
        engine.start_session(sample_project)
        engine.create_checkpoint(
            project=sample_project,
            chapter_number=1,
            content="第一章内容",
            word_count=3000,
        )
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章",
            content="内容",
            word_count=3000,
        )

        recovery = engine.recover_project(sample_project)

        assert recovery.success is True
        assert recovery.recovery_status == RecoveryStatus.SUCCESS
        assert recovery.checkpoint_id is not None
        assert recovery.resume_context is not None
        assert recovery.recovered_word_count == 3000
        assert recovery.recovered_chapters == 0  # Not marked complete

    def test_recover_project_no_checkpoint(self, engine, sample_project):
        """Test recovery when no checkpoint exists."""
        recovery = engine.recover_project(sample_project)

        assert recovery.success is False
        assert recovery.recovery_status == RecoveryStatus.FAILED
        assert len(recovery.recovery_errors) > 0

    def test_get_progress_summary(self, engine, sample_project):
        """Test getting progress summary."""
        # Add some data
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章",
            content="内容",
            word_count=3000,
        )

        summary = engine.get_progress_summary(sample_project)

        assert summary.novel_title == "测试小说"
        assert summary.genre == "玄幻"
        assert summary.total_word_count == 3000
        assert summary.target_word_count == 80000
        assert 0 < summary.progress_percentage < 100

    def test_cleanup_old_checkpoints(self, engine, sample_project):
        """Test cleaning up old checkpoints."""
        engine.start_session(sample_project)

        # Create many auto checkpoints
        for i in range(15):
            engine.create_checkpoint(
                project=sample_project,
                checkpoint_type=CheckpointType.AUTO,
                chapter_number=1,
                content=f"内容{i}",
                word_count=1000 + i * 100,
            )

        assert len(sample_project.checkpoints) == 15

        # Clean up, keeping only 5
        removed = engine.cleanup_old_checkpoints(
            sample_project,
            keep_recent=5,
            keep_manual=True,
        )

        assert removed == 10
        assert len(sample_project.checkpoints) == 5

    def test_validate_checkpoint(self, engine):
        """Test checkpoint validation."""
        checkpoint = Checkpoint(
            id="cp_test",
            checkpoint_type=CheckpointType.MANUAL,
            chapter_number=1,
            word_count=1500,
        )

        is_valid = engine.validate_checkpoint(checkpoint)

        assert is_valid is True
        assert checkpoint.status == CheckpointStatus.VALIDATED
        assert checkpoint.validated_at is not None

    def test_validate_checkpoint_invalid(self, engine):
        """Test checkpoint validation with invalid data."""
        checkpoint = Checkpoint(
            id="",  # Invalid empty ID
            checkpoint_type=CheckpointType.MANUAL,
            chapter_number=-1,  # Invalid chapter number
            word_count=-100,  # Invalid word count
        )

        is_valid = engine.validate_checkpoint(checkpoint)

        assert is_valid is False

    def test_export_resume_package(self, engine, sample_project):
        """Test exporting resume package."""
        engine.start_session(sample_project)
        engine.create_checkpoint(
            project=sample_project,
            chapter_number=2,
            content="第二章内容",
            word_count=2000,
        )

        package = engine.export_resume_package(sample_project)

        assert package["project_id"] == sample_project.id
        assert package["novel_id"] == "novel_001"
        assert package["title"] == "测试小说"
        assert "resume_context" in package
        assert "summary" in package
        assert "exported_at" in package

    def test_set_auto_save_config(self, engine):
        """Test setting auto-save configuration."""
        config = AutoSaveConfig(
            enabled=True,
            auto_save_interval=15,
            max_checkpoints=100,
        )

        engine.set_auto_save_config(config)

        assert engine._auto_save_config.enabled is True
        assert engine._auto_save_config.auto_save_interval == 15
        assert engine._auto_save_config.max_checkpoints == 100

    def test_multiple_sessions(self, engine, sample_project):
        """Test managing multiple writing sessions."""
        # First session
        session1 = engine.start_session(sample_project)
        engine.create_checkpoint(
            project=sample_project,
            session_id=session1.id,
            chapter_number=1,
            content="第一章",
            word_count=3000,
        )
        engine.end_session(sample_project, session1.id, WritingSessionStatus.COMPLETED)

        # Second session
        session2 = engine.start_session(sample_project)
        engine.create_checkpoint(
            project=sample_project,
            session_id=session2.id,
            chapter_number=2,
            content="第二章",
            word_count=1500,
        )

        assert len(sample_project.sessions) == 2
        assert sample_project.current_session_id == session2.id

    def test_chapter_progress_updates(self, engine, sample_project):
        """Test that chapter progress updates correctly."""
        # Start writing chapter 1
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章",
            content="部分内容",
            word_count=1500,
            target_word_count=3000,
        )

        assert 1 in sample_project.in_progress_chapters

        # Continue chapter 1
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章",
            content="更多内容",
            word_count=2500,
            target_word_count=3000,
        )

        # Complete chapter 1
        engine.save_chapter_progress(
            project=sample_project,
            chapter_number=1,
            title="第一章",
            content="完整内容",
            word_count=3000,
            target_word_count=3000,
            status=WritingSessionStatus.COMPLETED,
        )

        assert 1 in sample_project.completed_chapters
        assert 1 not in sample_project.in_progress_chapters


class TestIncrementalWritingModels:
    """Test cases for incremental writing models."""

    def test_checkpoint_model(self):
        """Test Checkpoint model creation."""
        checkpoint = Checkpoint(
            checkpoint_type=CheckpointType.MANUAL,
            chapter_number=1,
            word_count=1500,
        )

        assert checkpoint.id is not None
        assert checkpoint.checkpoint_type == CheckpointType.MANUAL
        assert checkpoint.chapter_number == 1
        assert checkpoint.status == CheckpointStatus.CREATED

    def test_writing_session_model(self):
        """Test WritingSession model creation."""
        session = WritingSession(
            novel_id="novel_001",
            title="测试小说",
        )

        assert session.id is not None
        assert session.status == WritingSessionStatus.ACTIVE
        assert len(session.checkpoints) == 0

    def test_resume_context_model(self):
        """Test ResumeContext model creation."""
        context = ResumeContext(
            novel_title="测试",
            genre="玄幻",
            last_chapter=5,
            last_word_count=15000,
            active_plot_threads=["主线", "感情线"],
        )

        assert context.novel_title == "测试"
        assert context.last_chapter == 5
        assert len(context.active_plot_threads) == 2

    def test_auto_save_config_model(self):
        """Test AutoSaveConfig model creation."""
        config = AutoSaveConfig(
            enabled=True,
            auto_save_interval=5,
            max_checkpoints=20,
        )

        assert config.enabled is True
        assert config.auto_save_interval == 5
        assert config.max_checkpoints == 20
