"""Sequential writing engine for auto-writing chapters in order.

This engine orchestrates the fourth step in the CHAI workflow: taking a complete
outline and writing chapters sequentially in order, with checkpoint management
and progress tracking.
"""

import uuid
import time
from datetime import datetime
from typing import Optional

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
)
from chai.models.chapter_synopsis import (
    ChapterSynopsis,
    ChapterSynopsisSection,
    SynopsisPlotPointStatus,
)
from chai.models.chapter_body import (
    ChapterBody,
    ChapterBodyStatus,
)
from chai.models.incremental_writing import (
    IncrementalWritingProject,
    WritingPhase,
    CheckpointType,
)
from chai.models.subplot_foreshadowing import SubplotForeshadowingDesign
from chai.models.climax_ending import ClimaxEndingSystem
from chai.models.character import Character
from chai.models.world import WorldSetting
from chai.services import AIService
from chai.engines.chapter_body_engine import ChapterBodyEngine
from chai.engines.incremental_writing_engine import IncrementalWritingEngine


class SequentialWritingEngine:
    """Engine for sequential chapter-by-chapter writing.

    This engine orchestrates writing chapters in sequential order by:
    1. Converting outline plans to chapter synopses
    2. Generating chapter content using ChapterBodyEngine
    3. Tracking progress with IncrementalWritingEngine
    4. Creating checkpoints for resume capability
    5. Supporting various writing order modes
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize sequential writing engine.

        Args:
            ai_service: Optional AI service for enhanced content generation
        """
        self.ai_service = ai_service
        self.chapter_body_engine = ChapterBodyEngine(ai_service) if ai_service else None
        self.incremental_engine = IncrementalWritingEngine(ai_service)

    async def write_sequentially(
        self,
        request: SequentialWritingRequest,
    ) -> SequentialWritingResult:
        """Write chapters sequentially based on outline.

        Args:
            request: Sequential writing request with outline and config

        Returns:
            SequentialWritingResult with writing progress and results
        """
        start_time = time.time()
        writing_id = f"writing_{uuid.uuid4().hex[:8]}"

        # Parse outline components
        components = self._parse_outline_components(request.outline_components)
        if not components or not components.chapters:
            return SequentialWritingResult(
                success=False,
                writing_id=writing_id,
                project_id=request.project_id,
                status=SequentialWritingStatus.FAILED,
                progress=SequentialWritingProgress(),
                error_message="No chapters found in outline",
            )

        # Validate outline if configured
        if request.config.validate_outline:
            validation = self._validate_outline_components(components)
            if not validation["is_valid"]:
                return SequentialWritingResult(
                    success=False,
                    writing_id=writing_id,
                    project_id=request.project_id,
                    status=SequentialWritingStatus.FAILED,
                    progress=SequentialWritingProgress(),
                    error_message=f"Outline validation failed: {validation['errors']}",
                )

        # Create incremental writing project for tracking
        project = self.incremental_engine.create_project(
            novel_id=request.project_id,
            title=request.project_title,
            genre=request.genre,
        )
        session = self.incremental_engine.start_session(
            project, phase=WritingPhase.WRITING_CHAPTER
        )

        # Determine chapter order
        chapter_order = self._determine_chapter_order(
            components, request.config, project.completed_chapters
        )

        # Initialize progress tracking
        progress = self._initialize_progress(components, chapter_order, request.config)

        # Parse context objects
        world_setting = self._parse_world_setting(request.world_setting)
        characters = self._parse_characters(request.characters)
        subplot_design = self._parse_subplot_design(request.subplot_design)
        climax_ending = self._parse_climax_ending(request.climax_ending_system)

        # Start writing
        result = SequentialWritingResult(
            success=True,
            writing_id=writing_id,
            project_id=request.project_id,
            status=SequentialWritingStatus.IN_PROGRESS,
            progress=progress,
        )

        previous_body: Optional[ChapterBody] = None
        failed_chapters = []

        for i, chapter_plan in enumerate(chapter_order):
            # Check if we should stop
            if request.config.end_chapter and chapter_plan.chapter_number > request.config.end_chapter:
                break

            # Update progress - current chapter
            progress.in_progress_chapter = chapter_plan.chapter_number

            # Find chapter progress entry
            ch_progress = next(
                (p for p in progress.chapter_progress if p.chapter_number == chapter_plan.chapter_number),
                None
            )
            if ch_progress:
                ch_progress.state = ChapterWritingState.IN_PROGRESS
                ch_progress.started_at = datetime.now().isoformat()

            try:
                # Convert outline plan to synopsis
                synopsis = self._outline_plan_to_synopsis(chapter_plan, components)

                # Generate chapter body
                if self.chapter_body_engine:
                    body = await self.chapter_body_engine.generate_chapter_body(
                        synopsis=synopsis,
                        world_setting=world_setting,
                        characters=characters,
                        subplot_design=subplot_design,
                        climax_ending_system=climax_ending,
                        previous_chapter_body=previous_body,
                    )
                else:
                    # Fallback: create minimal body without AI
                    body = self._create_minimal_body(chapter_plan, synopsis)

                # Update progress
                if ch_progress:
                    ch_progress.state = ChapterWritingState.COMPLETE
                    ch_progress.word_count = body.word_count
                    ch_progress.completed_at = datetime.now().isoformat()

                progress.completed_chapters += 1
                progress.total_word_count += body.word_count

                # Save chapter progress
                self.incremental_engine.save_chapter_progress(
                    project=project,
                    chapter_number=chapter_plan.chapter_number,
                    title=chapter_plan.chapter_title,
                    content=body.content,
                    word_count=body.word_count,
                    target_word_count=chapter_plan.word_count_target,
                    coherence_score=body.coherence_score,
                    pacing_score=body.pacing_score,
                )

                # Create checkpoint if configured
                if request.config.auto_checkpoint and (i + 1) % request.config.checkpoint_interval == 0:
                    checkpoint = self.incremental_engine.create_checkpoint(
                        project=project,
                        session_id=session.id,
                        checkpoint_type=CheckpointType.AUTO,
                        chapter_number=chapter_plan.chapter_number + 1,
                        content=body.content,
                        word_count=body.word_count,
                        continuation_hint=f"第{chapter_plan.chapter_number}章已完成，继续第{chapter_plan.chapter_number + 1}章",
                    )
                    result.last_checkpoint_id = checkpoint.id

                previous_body = body
                result.last_chapter_completed = chapter_plan.chapter_number

            except Exception as e:
                error_msg = str(e)
                if ch_progress:
                    ch_progress.state = ChapterWritingState.FAILED
                    ch_progress.error_message = error_msg
                    ch_progress.retry_count += 1

                failed_chapters.append({
                    "chapter_number": chapter_plan.chapter_number,
                    "title": chapter_plan.chapter_title,
                    "error": error_msg,
                })

                result.success = False

                # Continue with next chapter unless it's critical
                if chapter_plan.chapter_number == 1:
                    result.error_message = f"Failed at first chapter: {error_msg}"
                    break

        # Finalize progress
        progress.in_progress_chapter = None
        if progress.total_chapters > 0:
            progress.progress_percentage = (progress.completed_chapters / progress.total_chapters) * 100
        if progress.completed_chapters > 0:
            progress.average_word_count = progress.total_word_count // progress.completed_chapters

        # Determine final status
        if result.success and progress.completed_chapters == progress.total_chapters:
            result.status = SequentialWritingStatus.COMPLETE
        elif progress.completed_chapters > 0:
            result.status = SequentialWritingStatus.PAUSED
        else:
            result.status = SequentialWritingStatus.FAILED

        result.writing_time_seconds = time.time() - start_time

        # Mark session complete
        if result.success:
            self.incremental_engine.end_session(
                project, session.id, status=(
                    self.incremental_engine._get_session(project, session.id).status.__class__.COMPLETED
                    if self.incremental_engine._get_session(project, session.id) else None
                )
            )

        return result

    def _determine_chapter_order(
        self,
        components: CompleteOutlineComponents,
        config: SequentialWritingConfig,
        completed_chapters: list[int],
    ) -> list[ChapterOutlinePlan]:
        """Determine the order to write chapters based on config.

        Args:
            components: Complete outline components
            config: Writing configuration
            completed_chapters: List of already completed chapter numbers

        Returns:
            Ordered list of chapter plans to write
        """
        chapters = sorted(components.chapters, key=lambda c: c.chapter_number)

        # Filter by range
        if config.start_chapter > 1:
            chapters = [c for c in chapters if c.chapter_number >= config.start_chapter]
        if config.end_chapter:
            chapters = [c for c in chapters if c.chapter_number <= config.end_chapter]

        # Skip completed if configured
        if config.skip_completed and completed_chapters:
            chapters = [c for c in chapters if c.chapter_number not in completed_chapters]

        if config.order_mode == WritingOrderMode.VOLUME_FIRST:
            # Sort by volume first, then chapter number
            chapters = sorted(chapters, key=lambda c: (c.volume_index, c.chapter_number))
        elif config.order_mode == WritingOrderMode.SEQUENTIAL:
            # Sequential order (default)
            chapters = sorted(chapters, key=lambda c: c.chapter_number)
        # CUSTOM mode uses provided order

        return chapters

    def _initialize_progress(
        self,
        components: CompleteOutlineComponents,
        chapter_order: list[ChapterOutlinePlan],
        config: SequentialWritingConfig,
    ) -> SequentialWritingProgress:
        """Initialize progress tracking.

        Args:
            components: Complete outline components
            chapter_order: Ordered chapters to write
            config: Writing configuration

        Returns:
            Initialized SequentialWritingProgress
        """
        total = len(components.chapters)
        chapter_progress = []

        for ch in components.chapters:
            state = ChapterWritingState.PENDING
            if config.skip_completed:
                # Will be updated based on actual completed chapters
                pass

            chapter_progress.append(SequentialChapterProgress(
                chapter_number=ch.chapter_number,
                chapter_title=ch.chapter_title,
                state=state,
                target_word_count=ch.word_count_target,
            ))

        return SequentialWritingProgress(
            total_chapters=total,
            completed_chapters=0,
            total_word_count=0,
            chapter_progress=chapter_progress,
        )

    def _outline_plan_to_synopsis(
        self,
        plan: ChapterOutlinePlan,
        components: CompleteOutlineComponents,
    ) -> ChapterSynopsis:
        """Convert a chapter outline plan to a chapter synopsis.

        Args:
            plan: Chapter outline plan
            components: Complete outline components for context

        Returns:
            ChapterSynopsis for content generation
        """
        # Get active foreshadowing for this chapter
        active_foreshadowing = []
        for f in components.foreshadowing:
            if f.chapter_planted == plan.chapter_number:
                active_foreshadowing.append(f.element)
            elif f.chapter_payoff == plan.chapter_number:
                active_foreshadowing.append(f"伏笔回收：{f.element}")

        # Get subplot info
        active_subplots = []
        for s in components.subplots:
            if plan.chapter_number in s.chapters_involved:
                active_subplots.append(s.description)

        # Check if climax chapter
        is_climax = any(
            c.chapter_location == plan.chapter_number
            for c in components.climax
        )

        # Create synopsis sections based on scenes
        sections = []
        for i, scene_desc in enumerate(plan.scenes if plan.scenes else ["场景内容"]):
            sections.append(ChapterSynopsisSection(
                id=f"sec_{uuid.uuid4().hex[:8]}",
                name=f"第{i + 1}幕",
                order=i + 1,
                synopsis_text=scene_desc,
            ))

        # If no scenes, create a single section from synopsis
        if not sections:
            sections.append(ChapterSynopsisSection(
                id=f"sec_{uuid.uuid4().hex[:8]}",
                name="主要内容",
                order=1,
                synopsis_text=plan.synopsis,
            ))

        synopsis = ChapterSynopsis(
            id=f"syn_{uuid.uuid4().hex[:8]}",
            chapter_number=plan.chapter_number,
            title=plan.chapter_title,
            summary=plan.synopsis[:200] if plan.synopsis else f"第{plan.chapter_number}章内容",
            sections=sections,
            detailed_synopsis=plan.synopsis,
            word_count_target=plan.word_count_target,
            status=SynopsisPlotPointStatus.PENDING,
            is_climax_chapter=is_climax,
            plot_threads_advanced=plan.plot_threads,
            foreshadowing_planted=plan.foreshadowing,
        )

        return synopsis

    def _create_minimal_body(
        self,
        plan: ChapterOutlinePlan,
        synopsis: ChapterSynopsis,
    ) -> ChapterBody:
        """Create a minimal chapter body without AI generation.

        Args:
            plan: Chapter outline plan
            synopsis: Chapter synopsis

        Returns:
            Minimal ChapterBody
        """
        return ChapterBody(
            id=f"body_{uuid.uuid4().hex[:8]}",
            chapter_number=plan.chapter_number,
            title=plan.chapter_title,
            chapter_type="normal",
            content=f"第{plan.chapter_number}章内容待生成。\n\n本章概要：{synopsis.detailed_synopsis}",
            sections=[],
            word_count=len(synopsis.detailed_synopsis),
            meets_target=False,
            coherence_score=0.5,
            pacing_score=0.5,
            character_voice_score=0.5,
            has_plot_advancement=True,
            has_character_development=False,
            foreshadowing_properly_planted=False,
            status=ChapterBodyStatus.COMPLETE,
            synopsis_id=synopsis.id,
        )

    def _parse_outline_components(self, data: dict) -> Optional[CompleteOutlineComponents]:
        """Parse outline components from dict.

        Args:
            data: Outline components dict

        Returns:
            CompleteOutlineComponents or None
        """
        try:
            return CompleteOutlineComponents(**data)
        except Exception:
            return None

    def _parse_world_setting(self, data: Optional[dict]) -> Optional[WorldSetting]:
        """Parse world setting from dict.

        Args:
            data: World setting dict

        Returns:
            WorldSetting or None
        """
        if not data:
            return None
        try:
            return WorldSetting(**data)
        except Exception:
            return None

    def _parse_characters(self, data: list[dict]) -> list[Character]:
        """Parse characters from dicts.

        Args:
            data: Character dicts

        Returns:
            List of Character
        """
        characters = []
        for char_data in data:
            try:
                characters.append(Character(**char_data))
            except Exception:
                pass
        return characters

    def _parse_subplot_design(self, data: Optional[dict]) -> Optional[SubplotForeshadowingDesign]:
        """Parse subplot design from dict.

        Args:
            data: Subplot design dict

        Returns:
            SubplotForeshadowingDesign or None
        """
        if not data:
            return None
        try:
            return SubplotForeshadowingDesign(**data)
        except Exception:
            return None

    def _parse_climax_ending(self, data: Optional[dict]) -> Optional[ClimaxEndingSystem]:
        """Parse climax/ending system from dict.

        Args:
            data: Climax/ending system dict

        Returns:
            ClimaxEndingSystem or None
        """
        if not data:
            return None
        try:
            return ClimaxEndingSystem(**data)
        except Exception:
            return None

    def _validate_outline_components(
        self,
        components: CompleteOutlineComponents,
    ) -> dict:
        """Validate outline components.

        Args:
            components: Components to validate

        Returns:
            Validation result dict
        """
        errors = []
        warnings = []

        if not components.chapters:
            errors.append("No chapters defined in outline")
        else:
            # Check for duplicate chapter numbers
            chapter_nums = [c.chapter_number for c in components.chapters]
            duplicates = set([n for n in chapter_nums if chapter_nums.count(n) > 1])
            if duplicates:
                errors.append(f"Duplicate chapter numbers: {duplicates}")

            # Check for missing chapter numbers
            min_ch = min(chapter_nums) if chapter_nums else 1
            max_ch = max(chapter_nums) if chapter_nums else 1
            expected = set(range(min_ch, max_ch + 1))
            missing = expected - set(chapter_nums)
            if missing and len(missing) <= 5:
                warnings.append(f"Missing chapter numbers: {sorted(missing)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def get_summary(
        self,
        result: SequentialWritingResult,
        project_title: str,
    ) -> SequentialWritingSummary:
        """Get a summary of the writing result.

        Args:
            result: Sequential writing result
            project_title: Project title

        Returns:
            SequentialWritingSummary
        """
        next_chapter = None
        next_title = None

        for p in result.progress.chapter_progress:
            if p.state == ChapterWritingState.PENDING:
                next_chapter = p.chapter_number
                next_title = p.chapter_title
                break

        # Estimate remaining time (rough: 2 minutes per chapter)
        remaining = result.progress.total_chapters - result.progress.completed_chapters
        estimated_minutes = remaining * 2 if remaining > 0 else None

        return SequentialWritingSummary(
            writing_id=result.writing_id,
            project_title=project_title,
            genre="",  # Would need to be passed in
            status=result.status,
            total_chapters=result.progress.total_chapters,
            completed_chapters=result.progress.completed_chapters,
            total_word_count=result.progress.total_word_count,
            progress_percentage=result.progress.progress_percentage,
            next_chapter_to_write=next_chapter,
            next_chapter_title=next_title,
            estimated_remaining_time_minutes=estimated_minutes,
        )

    def get_next_chapter(
        self,
        components: CompleteOutlineComponents,
        completed_chapters: list[int],
    ) -> Optional[ChapterOutlinePlan]:
        """Get the next chapter to write.

        Args:
            components: Complete outline components
            completed_chapters: List of completed chapter numbers

        Returns:
            Next ChapterOutlinePlan or None
        """
        completed_set = set(completed_chapters)
        sorted_chapters = sorted(components.chapters, key=lambda c: c.chapter_number)

        for ch in sorted_chapters:
            if ch.chapter_number not in completed_set:
                return ch

        return None

    def export_writing_package(
        self,
        result: SequentialWritingResult,
        project_id: str,
    ) -> dict:
        """Export writing result as a package.

        Args:
            result: Sequential writing result
            project_id: Project ID

        Returns:
            Dictionary representation
        """
        return {
            "project_id": project_id,
            "writing_id": result.writing_id,
            "status": result.status.value,
            "progress": {
                "total_chapters": result.progress.total_chapters,
                "completed_chapters": result.progress.completed_chapters,
                "total_word_count": result.progress.total_word_count,
                "progress_percentage": result.progress.progress_percentage,
            },
            "last_chapter_completed": result.last_chapter_completed,
            "last_checkpoint_id": result.last_checkpoint_id,
            "exported_at": datetime.now().isoformat(),
        }
