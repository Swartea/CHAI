"""Complete outline engine for generating or importing full novel outlines.

This engine handles the second step in the CHAI workflow: generating or importing
a complete outline after project initialization.
"""

import uuid
from datetime import datetime
from typing import Optional

from chai.models.complete_outline import (
    CompleteOutlineMode,
    CompleteOutlineStatus,
    OutlineComponentStatus,
    CompleteOutlineGenerationConfig,
    CompleteOutlineRequest,
    CompleteOutlineResult,
    CompleteOutlineSummary,
    CompleteOutlineComponents,
    VolumeOutlinePlan,
    ChapterOutlinePlan,
    SubplotOutlinePlan,
    ForeshadowingOutlinePlan,
    ClimaxOutlinePlan,
    EndingOutlinePlan,
    OutlineValidationIssue,
    OutlineValidationResult,
    NextChapterToWrite,
)
from chai.models.story_outline import (
    StoryOutline,
    StoryOutlineType,
    OutlineStatus,
    VolumeOutline,
    ChapterOutline,
)
from chai.models.outline_import import ImportFormat
from chai.engines.story_outline_engine import StoryOutlineEngine
from chai.engines.outline_import_engine import OutlineImportEngine
from chai.engines.main_story_structure_engine import MainStoryStructureEngine
from chai.engines.chapter_synopsis_engine import ChapterSynopsisEngine
from chai.engines.subplot_foreshadowing_engine import SubplotForeshadowingEngine
from chai.engines.climax_ending_engine import ClimaxEndingEngine
from chai.services import AIService


class CompleteOutlineEngine:
    """Engine for generating or importing complete novel outlines.

    This engine orchestrates the outline creation process by:
    1. Generating a complete outline from project information (using other engines)
    2. Importing an existing outline from various formats
    3. Validating the complete outline
    4. Providing continuation context for the writing phase
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize complete outline engine.

        Args:
            ai_service: Optional AI service for enhanced outline generation
        """
        self.ai_service = ai_service
        self.story_outline_engine = StoryOutlineEngine(ai_service) if ai_service else None
        self.outline_import_engine = OutlineImportEngine(ai_service)
        # Only instantiate AI-dependent engines when ai_service is available
        self.main_structure_engine = MainStoryStructureEngine(ai_service) if ai_service else None
        self.chapter_synopsis_engine = ChapterSynopsisEngine(ai_service) if ai_service else None
        self.subplot_engine = SubplotForeshadowingEngine(ai_service) if ai_service else None
        self.climax_engine = ClimaxEndingEngine(ai_service) if ai_service else None

    async def create_complete_outline(
        self,
        request: CompleteOutlineRequest,
    ) -> CompleteOutlineResult:
        """Create a complete outline based on the request.

        This method handles both generation and import modes:
        - GENERATE: Creates a new outline from project info
        - IMPORT: Imports an existing outline from content
        - HYBRID: Imports base outline and generates missing parts

        Args:
            request: Complete outline request with project info and config

        Returns:
            CompleteOutlineResult with generated/imported outline
        """
        outline_id = f"complete_outline_{uuid.uuid4().hex[:8]}"

        try:
            if request.config.mode == CompleteOutlineMode.IMPORT:
                return await self._import_outline(request, outline_id)
            elif request.config.mode == CompleteOutlineMode.HYBRID:
                return await self._hybrid_outline(request, outline_id)
            else:
                return await self._generate_outline(request, outline_id)

        except Exception as e:
            return CompleteOutlineResult(
                outline_id=outline_id,
                project_id=request.project_id,
                status=CompleteOutlineStatus.FAILED,
                components=CompleteOutlineComponents(),
                error_message=str(e),
            )

    async def _generate_outline(
        self,
        request: CompleteOutlineRequest,
        outline_id: str,
    ) -> CompleteOutlineResult:
        """Generate a complete outline from project information."""
        result = CompleteOutlineResult(
            outline_id=outline_id,
            project_id=request.project_id,
            status=CompleteOutlineStatus.IN_PROGRESS,
            components=CompleteOutlineComponents(),
        )

        try:
            # Generate story outline using StoryOutlineEngine
            if self.story_outline_engine and request.main_characters:
                outline_type = StoryOutlineType(request.config.outline_structure)
                story_outline = await self.story_outline_engine.generate_outline(
                    genre=request.project_type,
                    theme=request.theme,
                    main_characters=request.main_characters,
                    supporting_characters=request.supporting_characters,
                    antagonists=request.antagonists,
                    outline_type=outline_type,
                    target_chapters=request.config.target_chapters,
                    target_word_count=request.config.target_word_count,
                    world_setting=request.world_setting,
                )
                result.story_outline_id = story_outline.id
            else:
                # Create minimal outline without AI
                story_outline = self._create_minimal_outline(request, outline_id)

            # Generate volume plans
            volumes = self._extract_volume_plans(story_outline)

            # Generate chapter plans
            chapters = self._extract_chapter_plans(story_outline)

            # Generate subplot plans if configured
            subplots = []
            if request.config.include_subplots:
                subplots = self._extract_subplot_plans(story_outline)

            # Generate foreshadowing plans if configured
            foreshadowing = []
            if request.config.include_foreshadowing:
                foreshadowing = self._extract_foreshadowing_plans(story_outline)

            # Generate climax plans if configured
            climax = []
            if request.config.include_climax:
                climax = self._extract_climax_plans(story_outline)

            # Generate ending plan if configured
            ending = None
            if request.config.include_ending:
                ending = self._extract_ending_plan(story_outline)

            result.components = CompleteOutlineComponents(
                volumes=volumes,
                chapters=chapters,
                subplots=subplots,
                foreshadowing=foreshadowing,
                climax=climax,
                ending=ending,
            )
            result.status = CompleteOutlineStatus.COMPLETE
            result.generation_stats = {
                "volumes_generated": len(volumes),
                "chapters_generated": len(chapters),
                "subplots_generated": len(subplots),
                "foreshadowing_generated": len(foreshadowing),
                "climax_generated": len(climax),
                "has_ending": ending is not None,
            }

            return result

        except Exception as e:
            result.status = CompleteOutlineStatus.FAILED
            result.error_message = f"Outline generation failed: {str(e)}"
            return result

    async def _import_outline(
        self,
        request: CompleteOutlineRequest,
        outline_id: str,
    ) -> CompleteOutlineResult:
        """Import a complete outline from content."""
        result = CompleteOutlineResult(
            outline_id=outline_id,
            project_id=request.project_id,
            status=CompleteOutlineStatus.IN_PROGRESS,
            components=CompleteOutlineComponents(),
        )

        if not request.import_content:
            result.status = CompleteOutlineStatus.FAILED
            result.error_message = "Import content is required for IMPORT mode"
            return result

        # Determine import format
        import_format_str = request.import_format or "json"
        try:
            import_format = ImportFormat(import_format_str)
        except ValueError:
            import_format = ImportFormat.JSON

        # Import using OutlineImportEngine
        import_result = await self.outline_import_engine.import_outline(
            content=request.import_content,
            import_format=import_format,
        )

        if not import_result.success:
            result.status = CompleteOutlineStatus.FAILED
            result.error_message = f"Import failed: {import_result.validation_errors}"
            return result

        # Convert to story outline
        if import_result.raw_data:
            story_outline = self.outline_import_engine.convert_to_story_outline(import_result)
            result.story_outline_id = story_outline.id

        # Extract plans from imported outline
        volumes = []
        chapters = []
        subplots = []
        foreshadowing = []
        climax = []
        ending = None

        if import_result.raw_data:
            raw = import_result.raw_data

            # Extract volumes
            for vol_data in raw.volumes_data:
                volumes.append(VolumeOutlinePlan(
                    volume_index=vol_data.get("number", len(volumes) + 1),
                    volume_title=vol_data.get("title", f"第{len(volumes) + 1}卷"),
                    chapter_count=vol_data.get("chapter_end", 0) - vol_data.get("chapter_start", 0) + 1 if vol_data.get("chapter_start") and vol_data.get("chapter_end") else 0,
                    chapter_start=vol_data.get("chapter_start", 0),
                    chapter_end=vol_data.get("chapter_end", 0),
                    volume_summary=vol_data.get("description", ""),
                    status=OutlineComponentStatus.IMPORTED,
                ))

            # Extract chapters
            for ch_data in raw.chapters_data:
                chapters.append(ChapterOutlinePlan(
                    chapter_number=ch_data.get("number", len(chapters) + 1),
                    chapter_title=ch_data.get("title", f"第{len(chapters) + 1}章"),
                    volume_index=1,  # Default to first volume
                    synopsis=ch_data.get("summary", ""),
                    word_count_target=ch_data.get("target_word_count", 3000),
                    scenes=ch_data.get("scene_summaries", []),
                    plot_threads=ch_data.get("plot_threads_advanced", []),
                    foreshadowing=ch_data.get("foreshadowing_planted", []),
                    status=OutlineComponentStatus.IMPORTED,
                ))

            # Extract subplots
            for thread_data in raw.plot_threads_data:
                subplots.append(SubplotOutlinePlan(
                    subplot_id=f"imported_{len(subplots)}",
                    subplot_type=thread_data.get("thread_type", "subplot"),
                    description=thread_data.get("description", ""),
                    chapters_involved=thread_data.get("chapters_active", []),
                    status=OutlineComponentStatus.IMPORTED,
                ))

            # Extract foreshadowing
            for fore_data in raw.foreshadowing_data:
                foreshadowing.append(ForeshadowingOutlinePlan(
                    foreshadowing_id=f"imported_{len(foreshadowing)}",
                    element=fore_data.get("element", ""),
                    chapter_planted=fore_data.get("chapter_planted", 1),
                    chapter_payoff=fore_data.get("chapter_payoff"),
                    status=OutlineComponentStatus.IMPORTED,
                ))

        result.components = CompleteOutlineComponents(
            volumes=volumes,
            chapters=chapters,
            subplots=subplots,
            foreshadowing=foreshadowing,
            climax=climax,
            ending=ending,
        )
        result.status = CompleteOutlineStatus.COMPLETE
        result.generation_stats = {
            "volumes_imported": len(volumes),
            "chapters_imported": len(chapters),
            "subplots_imported": len(subplots),
            "foreshadowing_imported": len(foreshadowing),
            "import_validation": import_result.validation_status.value,
        }

        return result

    async def _hybrid_outline(
        self,
        request: CompleteOutlineRequest,
        outline_id: str,
    ) -> CompleteOutlineResult:
        """Create a hybrid outline: import base and generate missing parts."""
        result = CompleteOutlineResult(
            outline_id=outline_id,
            project_id=request.project_id,
            status=CompleteOutlineStatus.IN_PROGRESS,
            components=CompleteOutlineComponents(),
        )

        # First import the base outline
        if request.import_content:
            import_result = await self._import_outline(request, outline_id)
            if import_result.status == CompleteOutlineStatus.FAILED:
                return import_result
            result.components = import_result.components
            result.story_outline_id = import_result.story_outline_id
        else:
            # Generate base if no import
            gen_result = await self._generate_outline(request, outline_id)
            result.components = gen_result.components
            result.story_outline_id = gen_result.story_outline_id

        # Then fill in missing parts
        components = result.components

        # Generate missing subplots if needed
        if request.config.include_subplots and len(components.subplots) == 0:
            subplots = await self._generate_subplots(request, components)
            components.subplots.extend(subplots)

        # Generate missing foreshadowing if needed
        if request.config.include_foreshadowing and len(components.foreshadowing) == 0:
            foreshadowing = await self._generate_foreshadowing(components)
            components.foreshadowing.extend(foreshadowing)

        # Generate climax if needed
        if request.config.include_climax and len(components.climax) == 0:
            climax = await self._generate_climax(request, components)
            components.climax = climax

        # Generate ending if needed
        if request.config.include_ending and components.ending is None:
            components.ending = await self._generate_ending(request, components)

        result.status = CompleteOutlineStatus.COMPLETE
        result.generation_stats = {
            "volumes_total": len(components.volumes),
            "chapters_total": len(components.chapters),
            "subplots_generated": len(components.subplots),
            "foreshadowing_generated": len(components.foreshadowing),
            "climax_generated": len(components.climax),
            "has_ending": components.ending is not None,
        }

        return result

    def _create_minimal_outline(
        self,
        request: CompleteOutlineRequest,
        outline_id: str,
    ) -> StoryOutline:
        """Create a minimal outline without AI assistance."""
        chapters_per_volume = request.config.target_chapters // max(1, request.config.target_volumes)

        volumes = []
        chapters = []

        for vol_idx in range(request.config.target_volumes):
            vol_num = vol_idx + 1
            ch_start = vol_idx * chapters_per_volume + 1
            ch_end = min((vol_idx + 1) * chapters_per_volume, request.config.target_chapters)

            volumes.append(VolumeOutline(
                id=f"{outline_id}_vol_{vol_num}",
                number=vol_num,
                title=f"第{vol_num}卷",
                chapter_start=ch_start,
                chapter_end=ch_end,
                description=f"第{vol_num}卷概要",
                theme=f"第{vol_num}卷主题",
                central_conflict="待补充",
                status=OutlineStatus.PENDING,
            ))

            for ch_num in range(ch_start, ch_end + 1):
                chapters.append(ChapterOutline(
                    id=f"{outline_id}_ch_{ch_num}",
                    number=ch_num,
                    title=f"第{ch_num}章",
                    summary="待补充",
                    tension_level="moderate",
                    status=OutlineStatus.PENDING,
                    target_word_count=request.config.target_word_count // request.config.target_chapters,
                ))

        return StoryOutline(
            id=outline_id,
            title=request.project_title,
            genre=request.project_type,
            theme=request.theme,
            outline_type=StoryOutlineType.THREE_ACT,
            target_word_count=request.config.target_word_count,
            target_chapter_count=request.config.target_chapters,
            volumes=volumes,
            chapters=chapters,
            plot_threads=[],
            foreshadowing_elements=[],
            status=OutlineStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _extract_volume_plans(self, outline: StoryOutline) -> list[VolumeOutlinePlan]:
        """Extract volume plans from story outline."""
        return [
            VolumeOutlinePlan(
                volume_index=v.number,
                volume_title=v.title,
                chapter_count=v.chapter_end - v.chapter_start + 1,
                chapter_start=v.chapter_start,
                chapter_end=v.chapter_end,
                volume_summary=v.description,
                status=OutlineComponentStatus.GENERATED,
            )
            for v in outline.volumes
        ]

    def _extract_chapter_plans(self, outline: StoryOutline) -> list[ChapterOutlinePlan]:
        """Extract chapter plans from story outline."""
        plans = []
        for ch in outline.chapters:
            # Find which volume this chapter belongs to
            volume_idx = 1
            for v in outline.volumes:
                if v.chapter_start <= ch.number <= v.chapter_end:
                    volume_idx = v.number
                    break

            plans.append(ChapterOutlinePlan(
                chapter_number=ch.number,
                chapter_title=ch.title,
                volume_index=volume_idx,
                synopsis=ch.summary,
                word_count_target=ch.target_word_count,
                scenes=ch.scene_summaries if hasattr(ch, 'scene_summaries') else [],
                plot_threads=ch.plot_threads_advanced if hasattr(ch, 'plot_threads_advanced') else [],
                foreshadowing=ch.foreshadowing_planted if hasattr(ch, 'foreshadowing_planted') else [],
                status=OutlineComponentStatus.GENERATED,
            ))
        return plans

    def _extract_subplot_plans(self, outline: StoryOutline) -> list[SubplotOutlinePlan]:
        """Extract subplot plans from story outline."""
        return [
            SubplotOutlinePlan(
                subplot_id=t.id,
                subplot_type=t.thread_type.value,
                description=t.description,
                chapters_involved=t.chapters_active,
                status=OutlineComponentStatus.GENERATED,
            )
            for t in outline.plot_threads
            if t.thread_type.value in ("subplot", "romantic", "mystery")
        ]

    def _extract_foreshadowing_plans(self, outline: StoryOutline) -> list[ForeshadowingOutlinePlan]:
        """Extract foreshadowing plans from story outline."""
        return [
            ForeshadowingOutlinePlan(
                foreshadowing_id=f.id,
                element=f.element,
                chapter_planted=f.chapter_planted,
                chapter_payoff=f.chapter_payoff,
                status=OutlineComponentStatus.GENERATED,
            )
            for f in outline.foreshadowing_elements
        ]

    def _extract_climax_plans(self, outline: StoryOutline) -> list[ClimaxOutlinePlan]:
        """Extract climax plans from story outline."""
        climax_chapters = [
            ch for ch in outline.chapters
            if ch.tension_level.value == "climax"
        ]
        return [
            ClimaxOutlinePlan(
                climax_id=f"climax_{ch.number}",
                climax_type="main_climax",
                chapter_location=ch.number,
                description=ch.summary,
                status=OutlineComponentStatus.GENERATED,
            )
            for ch in climax_chapters
        ]

    def _extract_ending_plan(self, outline: StoryOutline) -> Optional[EndingOutlinePlan]:
        """Extract ending plan from story outline."""
        # Find epilogue or last chapter
        epilogue = None
        for ch in outline.chapters:
            if hasattr(ch, 'is_epilogue') and ch.is_epilogue:
                epilogue = ch
                break

        last_ch = outline.chapters[-1] if outline.chapters else None
        target = epilogue or last_ch

        if target:
            return EndingOutlinePlan(
                ending_id=f"ending_{target.number}",
                ending_type="standard",
                chapter_location=target.number,
                description=target.summary if hasattr(target, 'summary') else "结尾",
                status=OutlineComponentStatus.GENERATED,
            )
        return None

    async def _generate_subplots(
        self,
        request: CompleteOutlineRequest,
        components: CompleteOutlineComponents,
    ) -> list[SubplotOutlinePlan]:
        """Generate subplot plans."""
        subplots = []

        # Add romantic subplot if multiple main characters
        if len(request.main_characters) >= 2:
            subplots.append(SubplotOutlinePlan(
                subplot_id=f"subplot_romantic_{len(subplots)}",
                subplot_type="romantic",
                description="角色感情线发展",
                chapters_involved=list(range(3, components.chapters[-1].chapter_number if components.chapters else 24)),
                status=OutlineComponentStatus.PENDING,
            ))

        # Add general subplots based on chapters
        if len(components.chapters) >= 10:
            mid = len(components.chapters) // 2
            subplots.append(SubplotOutlinePlan(
                subplot_id=f"subplot_mystery_{len(subplots)}",
                subplot_type="mystery",
                description="隐藏真相揭露",
                chapters_involved=list(range(5, components.chapters[-1].chapter_number if components.chapters else 24)),
                status=OutlineComponentStatus.PENDING,
            ))

        return subplots

    async def _generate_foreshadowing(
        self,
        components: CompleteOutlineComponents,
    ) -> list[ForeshadowingOutlinePlan]:
        """Generate foreshadowing plans."""
        if not components.chapters:
            return []

        total_chapters = components.chapters[-1].chapter_number
        foreshadowing = []

        # Plant foreshadowing in early chapters
        early_chapters = min(5, total_chapters)
        for i in range(early_chapters):
            foreshadowing.append(ForeshadowingOutlinePlan(
                foreshadowing_id=f"fore_early_{i}",
                element=f"早期伏笔元素{i + 1}",
                chapter_planted=i + 1,
                chapter_payoff=total_chapters - 3 + i if total_chapters > 5 else None,
                status=OutlineComponentStatus.PENDING,
            ))

        return foreshadowing

    async def _generate_climax(
        self,
        request: CompleteOutlineRequest,
        components: CompleteOutlineComponents,
    ) -> list[ClimaxOutlinePlan]:
        """Generate climax plans."""
        if not components.chapters:
            return []

        total_chapters = components.chapters[-1].chapter_number

        # Main climax around 80% through the story
        climax_chapter = int(total_chapters * 0.8)
        climax_chapter = max(climax_chapter, total_chapters - 4)

        return [
            ClimaxOutlinePlan(
                climax_id="climax_main",
                climax_type="final_climax",
                chapter_location=climax_chapter,
                description="核心高潮场景",
                status=OutlineComponentStatus.PENDING,
            )
        ]

    async def _generate_ending(
        self,
        request: CompleteOutlineRequest,
        components: CompleteOutlineComponents,
    ) -> EndingOutlinePlan:
        """Generate ending plan."""
        if not components.chapters:
            last_ch = 24
        else:
            last_ch = components.chapters[-1].chapter_number

        return EndingOutlinePlan(
            ending_id="ending_standard",
            ending_type="clean_resolution",
            chapter_location=last_ch,
            description="故事圆满收尾",
            status=OutlineComponentStatus.PENDING,
        )

    def validate_outline(
        self,
        components: CompleteOutlineComponents,
    ) -> OutlineValidationResult:
        """Validate a complete outline.

        Args:
            components: Outline components to validate

        Returns:
            OutlineValidationResult with validation findings
        """
        issues = []

        # Check volumes
        if len(components.volumes) == 0:
            issues.append(OutlineValidationIssue(
                issue_type="missing_volumes",
                severity="warning",
                location="volumes",
                description="No volumes defined",
                suggestion="Consider organizing chapters into volumes",
            ))

        # Check chapters
        if len(components.chapters) == 0:
            issues.append(OutlineValidationIssue(
                issue_type="missing_chapters",
                severity="error",
                location="chapters",
                description="No chapters defined",
                suggestion="Generate or import chapter outlines",
            ))

        # Check chapter continuity
        if components.chapters:
            chapter_numbers = sorted([c.chapter_number for c in components.chapters])
            expected = list(range(min(chapter_numbers), max(chapter_numbers) + 1))
            missing = set(expected) - set(chapter_numbers)
            if missing:
                issues.append(OutlineValidationIssue(
                    issue_type="missing_chapters",
                    severity="error",
                    location="chapters",
                    description=f"Missing chapter numbers: {sorted(missing)}",
                    suggestion="Fill in missing chapter outlines",
                ))

            # Check for duplicate chapter numbers
            duplicates = set([n for n in chapter_numbers if chapter_numbers.count(n) > 1])
            if duplicates:
                issues.append(OutlineValidationIssue(
                    issue_type="duplicate_chapters",
                    severity="error",
                    location="chapters",
                    description=f"Duplicate chapter numbers: {duplicates}",
                    suggestion="Ensure each chapter has a unique number",
                ))

        # Check subplot coverage
        if components.subplots and components.chapters:
            subplot_chapters = set()
            for s in components.subplots:
                subplot_chapters.update(s.chapters_involved)

            uncovered = set(range(1, components.chapters[-1].chapter_number + 1)) - subplot_chapters
            if len(uncovered) > len(components.chapters) * 0.5:
                issues.append(OutlineValidationIssue(
                    issue_type="subplot_gaps",
                    severity="warning",
                    location="subplots",
                    description="Many chapters are not covered by any subplot",
                    suggestion="Consider adding more subplots for better story coverage",
                ))

        # Check foreshadowing payoff
        unpaired = [f for f in components.foreshadowing if f.chapter_payoff is None]
        if unpaired:
            issues.append(OutlineValidationIssue(
                issue_type="unpaired_foreshadowing",
                severity="warning",
                location="foreshadowing",
                description=f"{len(unpaired)} foreshadowing elements have no payoff chapter",
                suggestion="Ensure all foreshadowing elements are resolved",
            ))

        # Check climax position
        if components.climax:
            last_ch = components.chapters[-1].chapter_number if components.chapters else 24
            for c in components.climax:
                if c.chapter_location < last_ch * 0.6:
                    issues.append(OutlineValidationIssue(
                        issue_type="climax_early",
                        severity="warning",
                        location="climax",
                        description=f"Climax at chapter {c.chapter_location} may be too early (last chapter is {last_ch})",
                        suggestion="Consider moving climax closer to the end",
                    ))

        # Calculate result
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        return OutlineValidationResult(
            is_valid=len(errors) == 0,
            issues=issues,
            warnings=len(warnings),
            errors=len(errors),
        )

    def get_next_chapter(
        self,
        components: CompleteOutlineComponents,
        written_chapters: Optional[list[int]] = None,
    ) -> Optional[NextChapterToWrite]:
        """Get the next chapter to write based on outline and progress.

        Args:
            components: Complete outline components
            written_chapters: List of chapter numbers that have been written

        Returns:
            NextChapterToWrite with details, or None if all chapters written
        """
        if not components.chapters:
            return None

        written = set(written_chapters or [])

        # Find first unwritten chapter
        for ch in sorted(components.chapters, key=lambda c: c.chapter_number):
            if ch.chapter_number not in written:
                # Find previous chapter summary
                prev_summary = ""
                if ch.chapter_number > 1:
                    prev = next((c for c in components.chapters if c.chapter_number == ch.chapter_number - 1), None)
                    if prev:
                        prev_summary = prev.synopsis

                # Get active foreshadowing
                active_fore = [
                    f.element for f in components.foreshadowing
                    if f.chapter_planted < ch.chapter_number and f.chapter_payoff and f.chapter_payoff >= ch.chapter_number
                ]

                # Get plot continuity
                continuity = []
                for s in components.subplots:
                    if ch.chapter_number in s.chapters_involved:
                        continuity.append(s.description)

                return NextChapterToWrite(
                    chapter_number=ch.chapter_number,
                    chapter_title=ch.chapter_title,
                    synopsis=ch.synopsis,
                    word_count_target=ch.word_count_target,
                    previous_chapter_summary=prev_summary,
                    plot_continuity=continuity,
                    foreshadowing_active=active_fore,
                )

        return None

    def get_summary(
        self,
        components: CompleteOutlineComponents,
        project_title: str,
    ) -> CompleteOutlineSummary:
        """Get a summary of the complete outline.

        Args:
            components: Complete outline components
            project_title: Title of the project

        Returns:
            CompleteOutlineSummary for display
        """
        return CompleteOutlineSummary(
            outline_id=components.volumes[0].volume_title if components.volumes else "unknown",
            project_title=project_title,
            status=CompleteOutlineStatus.COMPLETE,
            volume_count=len(components.volumes),
            chapter_count=len(components.chapters),
            subplot_count=len(components.subplots),
            foreshadowing_count=len(components.foreshadowing),
            climax_count=len(components.climax),
            has_ending=components.ending is not None,
            word_count_target=sum(c.word_count_target for c in components.chapters),
            created_at=datetime.now().isoformat(),
        )

    def export_outline_package(
        self,
        components: CompleteOutlineComponents,
        project_id: str,
    ) -> dict:
        """Export outline as a package for storage or transfer.

        Args:
            components: Complete outline components
            project_id: Associated project ID

        Returns:
            Dictionary representation of the complete outline
        """
        return {
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "volumes": [
                {
                    "volume_index": v.volume_index,
                    "title": v.volume_title,
                    "chapter_start": v.chapter_start,
                    "chapter_end": v.chapter_end,
                    "summary": v.volume_summary,
                }
                for v in components.volumes
            ],
            "chapters": [
                {
                    "chapter_number": c.chapter_number,
                    "title": c.chapter_title,
                    "volume_index": c.volume_index,
                    "synopsis": c.synopsis,
                    "word_count_target": c.word_count_target,
                    "scenes": c.scenes,
                    "plot_threads": c.plot_threads,
                    "foreshadowing": c.foreshadowing,
                }
                for c in components.chapters
            ],
            "subplots": [
                {
                    "subplot_id": s.subplot_id,
                    "type": s.subplot_type,
                    "description": s.description,
                    "chapters": s.chapters_involved,
                }
                for s in components.subplots
            ],
            "foreshadowing": [
                {
                    "foreshadowing_id": f.foreshadowing_id,
                    "element": f.element,
                    "chapter_planted": f.chapter_planted,
                    "chapter_payoff": f.chapter_payoff,
                }
                for f in components.foreshadowing
            ],
            "climax": [
                {
                    "climax_id": c.climax_id,
                    "type": c.climax_type,
                    "chapter": c.chapter_location,
                    "description": c.description,
                }
                for c in components.climax
            ],
            "ending": {
                "ending_id": components.ending.ending_id if components.ending else None,
                "type": components.ending.ending_type if components.ending else None,
                "chapter": components.ending.chapter_location if components.ending else None,
                "description": components.ending.description if components.ending else None,
            } if components.ending else None,
        }