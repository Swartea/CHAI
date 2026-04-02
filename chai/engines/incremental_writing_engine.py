"""Incremental writing engine for checkpoint and session management.

This engine handles saving writing progress, managing checkpoints, and providing
functionality to resume writing from the last saved position (断点续写).
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

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
    IncrementalWritingRecovery,
    AutoSaveConfig,
    IncrementalWritingSummary,
)
from chai.models.novel import Novel, Chapter
from chai.models.story_outline import StoryOutline, ChapterOutline
from chai.models.chapter_body import ChapterBody, ManuscriptBody
from chai.services import AIService


class IncrementalWritingEngine:
    """Engine for incremental writing with checkpoint and session management.

    This engine supports:
    - Creating and managing writing checkpoints
    - Tracking writing sessions
    - Auto-save functionality
    - Resume context generation
    - Progress recovery
    - Writing progress statistics
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize incremental writing engine.

        Args:
            ai_service: Optional AI service for generating continuation hints
        """
        self.ai_service = ai_service
        self._auto_save_config = AutoSaveConfig()

    def create_project(
        self,
        novel_id: str,
        title: str,
        genre: str = "",
        author: str = "",
        target_total_word_count: int = 80000,
    ) -> IncrementalWritingProject:
        """Create a new incremental writing project.

        Args:
            novel_id: Unique novel identifier
            title: Novel title
            genre: Genre
            author: Author name
            target_total_word_count: Target word count for the novel

        Returns:
            New IncrementalWritingProject
        """
        project = IncrementalWritingProject(
            id=f"proj_{uuid.uuid4().hex[:8]}",
            novel_id=novel_id,
            title=title,
            genre=genre,
            author=author,
            target_total_word_count=target_total_word_count,
        )
        return project

    def start_session(
        self,
        project: IncrementalWritingProject,
        phase: WritingPhase = WritingPhase.WRITING_CHAPTER,
    ) -> WritingSession:
        """Start a new writing session.

        Args:
            project: The incremental writing project
            phase: Current writing phase

        Returns:
            New WritingSession
        """
        session = WritingSession(
            id=f"session_{uuid.uuid4().hex[:8]}",
            novel_id=project.novel_id,
            title=project.title,
            genre=project.genre,
            status=WritingSessionStatus.ACTIVE,
            phase=phase,
            started_at=datetime.now().isoformat(),
            last_active_at=datetime.now().isoformat(),
            auto_save_enabled=self._auto_save_config.enabled,
            auto_save_interval=self._auto_save_config.auto_save_interval,
        )

        project.sessions.append(session)
        project.current_session_id = session.id
        project.total_sessions_count += 1
        project.last_modified_at = datetime.now().isoformat()

        return session

    def end_session(
        self,
        project: IncrementalWritingProject,
        session_id: str,
        status: WritingSessionStatus = WritingSessionStatus.COMPLETED,
    ) -> WritingSession:
        """End a writing session.

        Args:
            project: The incremental writing project
            session_id: Session ID to end
            status: Final status of the session

        Returns:
            Updated WritingSession
        """
        session = self._get_session(project, session_id)
        if session:
            session.status = status
            session.ended_at = datetime.now().isoformat()
            project.last_modified_at = datetime.now().isoformat()
        return session

    def create_checkpoint(
        self,
        project: IncrementalWritingProject,
        session_id: Optional[str] = None,
        checkpoint_type: CheckpointType = CheckpointType.MANUAL,
        chapter_number: int = 1,
        scene_number: Optional[int] = None,
        content: str = "",
        word_count: int = 0,
        target_word_count: int = 3000,
        continuation_hint: str = "",
        last_scene_summary: Optional[str] = None,
        coherence_score: float = 0.0,
        pacing_score: float = 0.0,
        expires_in_hours: Optional[int] = None,
    ) -> Checkpoint:
        """Create a checkpoint at current writing position.

        Args:
            project: The incremental writing project
            session_id: Optional session ID (uses current if not provided)
            checkpoint_type: Type of checkpoint
            chapter_number: Current chapter number
            scene_number: Current scene number
            content: Current chapter content
            word_count: Current word count
            target_word_count: Target word count for chapter
            continuation_hint: Hint for continuing
            last_scene_summary: Summary of last scene
            coherence_score: Quality score
            pacing_score: Pacing score
            expires_in_hours: Hours until checkpoint expires

        Returns:
            New Checkpoint
        """
        # Get session or use current
        if session_id is None:
            session_id = project.current_session_id

        # Create checkpoint
        checkpoint = Checkpoint(
            id=f"cp_{uuid.uuid4().hex[:8]}",
            checkpoint_type=checkpoint_type,
            created_at=datetime.now().isoformat(),
            status=CheckpointStatus.CREATED,
            chapter_number=chapter_number,
            scene_number=scene_number,
            word_count=word_count,
            target_word_count=target_word_count,
            last_content_preview=content[-500:] if content and len(content) > 500 else content,
            continuation_hint=continuation_hint,
            last_scene_summary=last_scene_summary,
            coherence_score=coherence_score,
            pacing_score=pacing_score,
        )

        # Set expiry for auto-save checkpoints
        if checkpoint_type == CheckpointType.AUTO and expires_in_hours:
            checkpoint.expires_at = (
                datetime.now() + timedelta(hours=expires_in_hours)
            ).isoformat()

        # Add to project checkpoints
        project.checkpoints.append(checkpoint)
        project.latest_checkpoint_id = checkpoint.id
        project.last_modified_at = datetime.now().isoformat()

        # Update session if available
        if session_id:
            session = self._get_session(project, session_id)
            if session:
                session.checkpoints.append(checkpoint)
                session.current_chapter = chapter_number
                session.current_scene = scene_number
                session.current_word_count = word_count
                session.total_word_count = project.total_word_count + word_count
                session.last_active_at = datetime.now().isoformat()

                # Update progress
                if word_count > session.current_word_count:
                    session.total_word_count = project.total_word_count + word_count

        return checkpoint

    def save_chapter_progress(
        self,
        project: IncrementalWritingProject,
        chapter_number: int,
        title: str,
        content: str,
        word_count: int,
        target_word_count: int = 3000,
        status: WritingSessionStatus = WritingSessionStatus.ACTIVE,
        scenes_completed: int = 0,
        total_scenes: int = 1,
        coherence_score: float = 0.0,
        pacing_score: float = 0.0,
    ) -> ChapterProgress:
        """Save progress for a specific chapter.

        Args:
            project: The incremental writing project
            chapter_number: Chapter number
            title: Chapter title
            content: Chapter content
            word_count: Current word count
            target_word_count: Target word count
            status: Chapter status
            scenes_completed: Number of scenes completed
            total_scenes: Total scenes in chapter
            coherence_score: Quality score
            pacing_score: Pacing score

        Returns:
            Updated ChapterProgress
        """
        progress_percentage = (
            (word_count / target_word_count * 100) if target_word_count > 0 else 0
        )
        progress_percentage = min(progress_percentage, 100.0)

        # Find existing or create new
        progress = self._get_chapter_progress(project, chapter_number)
        if progress is None:
            progress = ChapterProgress(
                chapter_number=chapter_number,
                title=title,
            )
            project.metadata.setdefault("chapter_progress", {})[str(chapter_number)] = progress

        # Update fields
        progress.title = title
        progress.content = content
        progress.word_count = word_count
        progress.target_word_count = target_word_count
        progress.progress_percentage = progress_percentage
        progress.scenes_completed = scenes_completed
        progress.total_scenes = total_scenes
        progress.coherence_score = coherence_score
        progress.pacing_score = pacing_score
        progress.last_modified_at = datetime.now().isoformat()

        # Update project totals
        if status == WritingSessionStatus.COMPLETED:
            progress.status = status
            progress.completed_at = datetime.now().isoformat()
            if chapter_number not in project.completed_chapters:
                project.completed_chapters.append(chapter_number)
                project.completed_chapters.sort()
            if chapter_number in project.in_progress_chapters:
                project.in_progress_chapters.remove(chapter_number)
        else:
            progress.status = WritingSessionStatus.ACTIVE
            if chapter_number not in project.completed_chapters:
                if chapter_number not in project.in_progress_chapters:
                    project.in_progress_chapters.append(chapter_number)

        # Update total word count
        project.total_word_count = sum(
            p.word_count for p in self._get_all_chapter_progress(project)
        )
        project.last_modified_at = datetime.now().isoformat()

        return progress

    def mark_chapter_complete(
        self,
        project: IncrementalWritingProject,
        chapter_number: int,
        content: str = "",
        word_count: int = 0,
    ) -> Checkpoint:
        """Mark a chapter as complete and create a checkpoint.

        Args:
            project: The incremental writing project
            chapter_number: Chapter number
            content: Final chapter content
            word_count: Final word count

        Returns:
            New Checkpoint
        """
        # Update chapter progress
        progress = self._get_chapter_progress(project, chapter_number)
        if progress:
            progress.status = WritingSessionStatus.COMPLETED
            progress.content = content
            progress.word_count = word_count
            progress.progress_percentage = 100.0
            progress.completed_at = datetime.now().isoformat()
            progress.last_modified_at = datetime.now().isoformat()

        # Update project
        if chapter_number not in project.completed_chapters:
            project.completed_chapters.append(chapter_number)
            project.completed_chapters.sort()
        if chapter_number in project.in_progress_chapters:
            project.in_progress_chapters.remove(chapter_number)

        project.total_word_count = sum(
            p.word_count for p in self._get_all_chapter_progress(project)
        )
        project.last_modified_at = datetime.now().isoformat()

        # Create chapter complete checkpoint
        return self.create_checkpoint(
            project=project,
            checkpoint_type=CheckpointType.CHAPTER_COMPLETE,
            chapter_number=chapter_number + 1,  # Next chapter
            content=content,
            word_count=word_count,
            continuation_hint=f"第{chapter_number}章已完成，开始第{chapter_number + 1}章",
        )

    def get_resume_context(
        self,
        project: IncrementalWritingProject,
        checkpoint_id: Optional[str] = None,
        outline: Optional[StoryOutline] = None,
        characters: Optional[dict] = None,
    ) -> ResumeContext:
        """Get context for resuming writing from checkpoint.

        Args:
            project: The incremental writing project
            checkpoint_id: Optional specific checkpoint ID (uses latest if not provided)
            outline: Optional story outline for additional context
            characters: Optional character states

        Returns:
            ResumeContext for continuing writing
        """
        # Get checkpoint
        if checkpoint_id:
            checkpoint = self._get_checkpoint(project, checkpoint_id)
        else:
            checkpoint = self._get_checkpoint(project, project.latest_checkpoint_id)

        if not checkpoint:
            # No checkpoint, start from beginning
            return ResumeContext(
                novel_title=project.title,
                genre=project.genre,
                last_chapter=0,
                last_word_count=0,
            )

        # Get last chapter content
        last_content_excerpt = checkpoint.last_content_preview

        # Get pending chapters from outline if available
        next_chapter = checkpoint.chapter_number
        next_chapter_title = None
        active_plot_threads = []
        pending_foreshadowing = []

        if outline:
            chapters = sorted(outline.chapters, key=lambda c: c.number)
            next_ch = next((c for c in chapters if c.number == checkpoint.chapter_number), None)
            if next_ch:
                next_chapter_title = next_ch.title

            # Get active plot threads
            active_plot_threads = [
                t.name for t in outline.plot_threads
                if any(c >= checkpoint.chapter_number for c in t.chapters_active)
            ]

            # Get pending foreshadowing
            pending_foreshadowing = [
                f.element for f in outline.foreshadowing_elements
                if f.status.value in ("planted", "partial") and
                (f.chapter_payoff is None or f.chapter_payoff >= checkpoint.chapter_number)
            ]

        # Build resume context
        return ResumeContext(
            novel_title=project.title,
            genre=project.genre,
            last_chapter=checkpoint.chapter_number,
            last_scene=checkpoint.scene_number,
            last_word_count=project.total_word_count,
            last_content_excerpt=last_content_excerpt,
            last_scene_summary=checkpoint.last_scene_summary,
            continuation_hint=checkpoint.continuation_hint,
            active_plot_threads=active_plot_threads,
            pending_foreshadowing=pending_foreshadowing,
            character_states=characters or {},
            world_context="",  # Would come from world_setting
            coherence_score=checkpoint.coherence_score,
            pacing_score=checkpoint.pacing_score,
            checkpoint_created_at=checkpoint.created_at,
        )

    def recover_project(
        self,
        project: IncrementalWritingProject,
        checkpoint_id: Optional[str] = None,
    ) -> IncrementalWritingRecovery:
        """Recover project state from checkpoint.

        Args:
            project: The incremental writing project
            checkpoint_id: Optional specific checkpoint to recover from

        Returns:
            IncrementalWritingRecovery with recovery result
        """
        recovery = IncrementalWritingRecovery(
            success=True,
            recovery_status=RecoveryStatus.SUCCESS,
        )

        # Get checkpoint
        if checkpoint_id:
            checkpoint = self._get_checkpoint(project, checkpoint_id)
        else:
            checkpoint = self._get_checkpoint(project, project.latest_checkpoint_id)

        if not checkpoint:
            recovery.success = False
            recovery.recovery_status = RecoveryStatus.FAILED
            recovery.recovery_errors.append("No checkpoint found to recover from")
            return recovery

        # Populate recovery info
        recovery.checkpoint_id = checkpoint.id
        recovery.checkpoint_created_at = checkpoint.created_at
        recovery.recovered_word_count = project.total_word_count
        recovery.recovered_chapters = len(project.completed_chapters)
        recovery.recovered_sessions = len(project.sessions)

        # Get resume context
        recovery.resume_context = self.get_resume_context(project, checkpoint.id)

        return recovery

    def get_progress_summary(
        self,
        project: IncrementalWritingProject,
        outline: Optional[StoryOutline] = None,
    ) -> IncrementalWritingSummary:
        """Get summary of incremental writing progress.

        Args:
            project: The incremental writing project
            outline: Optional story outline for additional info

        Returns:
            IncrementalWritingSummary
        """
        # Calculate progress
        progress_percentage = (
            (project.total_word_count / project.target_total_word_count * 100)
            if project.target_total_word_count > 0 else 0
        )
        progress_percentage = min(progress_percentage, 100.0)

        # Get next chapter
        next_chapter = None
        next_chapter_title = None
        total_chapters = 0

        if outline:
            total_chapters = len(outline.chapters)
            # Find first incomplete chapter
            for chapter in sorted(outline.chapters, key=lambda c: c.number):
                if chapter.number not in project.completed_chapters:
                    next_chapter = chapter.number
                    next_chapter_title = chapter.title
                    break

        # Calculate pending chapters
        pending_chapters = total_chapters - len(project.completed_chapters) - len(project.in_progress_chapters)

        # Get latest checkpoint time
        latest_checkpoint_at = None
        if project.checkpoints:
            latest = max(project.checkpoints, key=lambda c: c.created_at)
            latest_checkpoint_at = latest.created_at

        # Calculate average quality
        checkpoints_with_scores = [
            c for c in project.checkpoints
            if c.coherence_score > 0 or c.pacing_score > 0
        ]
        avg_coherence = 0.0
        avg_pacing = 0.0
        if checkpoints_with_scores:
            avg_coherence = sum(c.coherence_score for c in checkpoints_with_scores) / len(checkpoints_with_scores)
            avg_pacing = sum(c.pacing_score for c in checkpoints_with_scores) / len(checkpoints_with_scores)

        # Get last auto-save time
        last_auto_save_at = None
        auto_save_enabled = True
        if project.sessions:
            latest_session = max(project.sessions, key=lambda s: s.last_active_at)
            auto_save_enabled = latest_session.auto_save_enabled
            auto_checkpoints = [
                c for c in latest_session.checkpoints
                if c.checkpoint_type == CheckpointType.AUTO
            ]
            if auto_checkpoints:
                last_auto_save_at = max(auto_checkpoints, key=lambda c: c.created_at).created_at

        return IncrementalWritingSummary(
            novel_title=project.title,
            genre=project.genre,
            total_word_count=project.total_word_count,
            target_word_count=project.target_total_word_count,
            progress_percentage=progress_percentage,
            total_chapters=total_chapters,
            completed_chapters=len(project.completed_chapters),
            in_progress_chapters=len(project.in_progress_chapters),
            pending_chapters=max(0, pending_chapters),
            next_chapter_to_write=next_chapter,
            next_chapter_title=next_chapter_title,
            total_sessions=project.total_sessions_count,
            total_writing_time_hours=project.total_writing_time_hours,
            total_checkpoints=len(project.checkpoints),
            latest_checkpoint_at=latest_checkpoint_at,
            auto_save_enabled=auto_save_enabled,
            last_auto_save_at=last_auto_save_at,
            average_coherence=avg_coherence,
            average_pacing=avg_pacing,
        )

    def cleanup_old_checkpoints(
        self,
        project: IncrementalWritingProject,
        keep_recent: int = 10,
        keep_manual: bool = True,
    ) -> int:
        """Clean up old checkpoints to save space.

        Args:
            project: The incremental writing project
            keep_recent: Number of recent checkpoints to keep
            keep_manual: Whether to always keep manual checkpoints

        Returns:
            Number of checkpoints removed
        """
        before_count = len(project.checkpoints)

        # Separate checkpoints by type
        manual_checkpoints = [
            c for c in project.checkpoints
            if c.checkpoint_type == CheckpointType.MANUAL
        ]
        auto_checkpoints = [
            c for c in project.checkpoints
            if c.checkpoint_type != CheckpointType.MANUAL
        ]

        # Sort auto checkpoints by date (newest first)
        auto_checkpoints.sort(key=lambda c: c.created_at, reverse=True)

        # Keep recent auto checkpoints
        keep_auto = auto_checkpoints[:keep_recent]

        # Remove expired checkpoints
        now = datetime.now()
        not_expired = [
            c for c in keep_auto
            if c.expires_at is None or datetime.fromisoformat(c.expires_at) > now
        ]

        # Rebuild checkpoints list
        if keep_manual:
            project.checkpoints = manual_checkpoints + not_expired
        else:
            project.checkpoints = not_expired

        # Sort by creation date
        project.checkpoints.sort(key=lambda c: c.created_at, reverse=True)

        # Update latest checkpoint reference
        if project.checkpoints:
            project.latest_checkpoint_id = project.checkpoints[0].id
        else:
            project.latest_checkpoint_id = None

        project.last_modified_at = datetime.now().isoformat()

        return before_count - len(project.checkpoints)

    def validate_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> bool:
        """Validate a checkpoint for integrity.

        Args:
            checkpoint: Checkpoint to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not checkpoint.id or not checkpoint.created_at:
            return False

        # Check word count is reasonable
        if checkpoint.word_count < 0:
            return False

        # Check chapter number is valid
        if checkpoint.chapter_number < 0:
            return False

        # Update status
        checkpoint.status = CheckpointStatus.VALIDATED
        checkpoint.validated_at = datetime.now().isoformat()

        return True

    def export_resume_package(
        self,
        project: IncrementalWritingProject,
        checkpoint_id: Optional[str] = None,
        outline: Optional[StoryOutline] = None,
    ) -> dict:
        """Export a package for resuming writing elsewhere.

        Args:
            project: The incremental writing project
            checkpoint_id: Optional specific checkpoint
            outline: Optional story outline

        Returns:
            Dictionary with resume package data
        """
        resume_context = self.get_resume_context(project, checkpoint_id, outline)
        summary = self.get_progress_summary(project, outline)

        return {
            "project_id": project.id,
            "novel_id": project.novel_id,
            "title": project.title,
            "genre": project.genre,
            "resume_context": resume_context.model_dump(),
            "summary": summary.model_dump(),
            "exported_at": datetime.now().isoformat(),
        }

    # Helper methods
    def _get_session(self, project: IncrementalWritingProject, session_id: str) -> Optional[WritingSession]:
        """Get session by ID."""
        return next((s for s in project.sessions if s.id == session_id), None)

    def _get_checkpoint(self, project: IncrementalWritingProject, checkpoint_id: Optional[str]) -> Optional[Checkpoint]:
        """Get checkpoint by ID."""
        if not checkpoint_id:
            return None
        return next((c for c in project.checkpoints if c.id == checkpoint_id), None)

    def _get_chapter_progress(self, project: IncrementalWritingProject, chapter_number: int) -> Optional[ChapterProgress]:
        """Get chapter progress by number."""
        progress_dict = project.metadata.get("chapter_progress", {})
        return progress_dict.get(str(chapter_number))

    def _get_all_chapter_progress(self, project: IncrementalWritingProject) -> list[ChapterProgress]:
        """Get all chapter progress entries."""
        return list(project.metadata.get("chapter_progress", {}).values())

    def set_auto_save_config(self, config: AutoSaveConfig) -> None:
        """Set auto-save configuration.

        Args:
            config: AutoSaveConfig with settings
        """
        self._auto_save_config = config
