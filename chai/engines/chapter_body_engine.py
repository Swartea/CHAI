"""Chapter body generation engine for generating full chapter text from outline.

This engine orchestrates taking the complete story outline and chapter synopses,
then generating full chapter text sequentially using the ChapterContentEngine.
"""

import uuid
import time
from datetime import datetime
from typing import Optional

from chai.models.chapter_body import (
    ChapterBody,
    ChapterBodySection,
    ChapterBodyStatus,
    ChapterBodySectionType,
    ChapterGenerationProgress,
    ManuscriptBody,
    ManuscriptStatus,
    ManuscriptGenerationRequest,
    ManuscriptGenerationResult,
    ChapterBodyAnalysis,
)
from chai.models.chapter_synopsis import ChapterSynopsis
from chai.models.chapter_content import ChapterContentDraft, ChapterContentStatus
from chai.models.subplot_foreshadowing import SubplotForeshadowingDesign
from chai.models.climax_ending import ClimaxEndingSystem
from chai.models.character import Character
from chai.models.world import WorldSetting
from chai.services import AIService
from chai.engines.chapter_content_engine import ChapterContentEngine


class ChapterBodyEngine:
    """Engine for generating full chapter body text from outline.

    This engine orchestrates the chapter-by-chapter generation process,
    taking the complete story outline and chapter synopses and producing
    a full manuscript with all chapters.
    """

    def __init__(self, ai_service: AIService):
        """Initialize chapter body engine with AI service."""
        self.ai_service = ai_service
        self.content_engine = ChapterContentEngine(ai_service)

    async def generate_chapter_body(
        self,
        synopsis: ChapterSynopsis,
        world_setting: Optional[WorldSetting] = None,
        characters: Optional[list[Character]] = None,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
        climax_ending_system: Optional[ClimaxEndingSystem] = None,
        previous_chapter_body: Optional[ChapterBody] = None,
    ) -> ChapterBody:
        """Generate a single chapter body from synopsis.

        Args:
            synopsis: Chapter synopsis to expand
            world_setting: World setting for context
            characters: Character list for voice consistency
            subplot_design: Subplot and foreshadowing design
            climax_ending_system: Climax and ending system
            previous_chapter_body: Previous chapter body for continuity

        Returns:
            ChapterBody with generated content
        """
        body_id = f"body_{uuid.uuid4().hex[:8]}"

        # Get previous chapter summary for continuity
        previous_summary = None
        if previous_chapter_body:
            previous_summary = previous_chapter_body.content[-500:] if previous_chapter_body.content else None

        # Generate content using ChapterContentEngine
        draft = await self.content_engine.generate_content(
            synopsis=synopsis,
            world_setting=world_setting,
            characters=characters,
            subplot_design=subplot_design,
            climax_ending_system=climax_ending_system,
            previous_chapter_summary=previous_summary,
        )

        # Convert draft to chapter body sections
        sections = self._draft_to_sections(draft, synopsis)

        # Build chapter body
        body = ChapterBody(
            id=body_id,
            chapter_number=synopsis.chapter_number,
            title=synopsis.title,
            chapter_type=self._get_chapter_type(synopsis),
            content=draft.content,
            sections=sections,
            word_count=draft.word_count,
            meets_target=draft.meets_target,
            coherence_score=draft.coherence_score,
            pacing_score=draft.pacing_score,
            character_voice_score=draft.character_voice_score,
            has_plot_advancement=draft.has_plot_advancement,
            has_character_development=draft.has_character_development,
            foreshadowing_properly_planted=draft.foreshadowing_properly_planted,
            status=ChapterBodyStatus.COMPLETE,
            synopsis_id=synopsis.id,
        )

        return body

    async def generate_manuscript(
        self,
        request: ManuscriptGenerationRequest,
        story_outline: Optional[dict] = None,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
        climax_ending_system: Optional[ClimaxEndingSystem] = None,
    ) -> ManuscriptGenerationResult:
        """Generate full manuscript chapter by chapter.

        Args:
            request: Generation request with chapter synopses
            story_outline: Story outline data
            subplot_design: Subplot and foreshadowing design
            climax_ending_system: Climax and ending system

        Returns:
            ManuscriptGenerationResult with generated manuscript
        """
        start_time = time.time()
        manuscript_id = f"manuscript_{uuid.uuid4().hex[:8]}"

        # Parse world setting
        world_setting = None
        if request.world_setting:
            try:
                world_setting = WorldSetting(**request.world_setting)
            except Exception:
                pass

        # Parse characters
        characters = []
        for char_data in request.characters:
            try:
                characters.append(Character(**char_data))
            except Exception:
                pass

        # Parse chapter synopses
        synopses = []
        for syn_data in request.chapter_synopses:
            try:
                synopses.append(ChapterSynopsis(**syn_data))
            except Exception:
                pass

        # Sort by chapter number
        synopses.sort(key=lambda s: s.chapter_number)

        # Determine chapter range
        start = request.start_chapter
        end = request.end_chapter or max(s.chapter_number for s in synopses) if synopses else start + 23
        synopses = [s for s in synopses if start <= s.chapter_number <= end]

        # Initialize manuscript
        manuscript = ManuscriptBody(
            id=manuscript_id,
            title=request.world_setting.get("name", "未命名小说") if request.world_setting else "未命名小说",
            genre=request.world_setting.get("genre", "") if request.world_setting else "",
            status=ManuscriptStatus.IN_PROGRESS,
        )

        # Initialize progress tracking
        for syn in synopses:
            manuscript.progress.append(ChapterGenerationProgress(
                chapter_number=syn.chapter_number,
                title=syn.title,
                status=ChapterBodyStatus.PENDING,
            ))

        # Generate chapters sequentially
        previous_body = None
        failed_chapters = []

        for i, syn in enumerate(synopses):
            progress_idx = next(
                (j for j, p in enumerate(manuscript.progress) if p.chapter_number == syn.chapter_number),
                None
            )

            if progress_idx is not None:
                manuscript.progress[progress_idx].status = ChapterBodyStatus.IN_PROGRESS
                manuscript.progress[progress_idx].started_at = datetime.utcnow().isoformat()

            try:
                # Generate chapter body
                body = await self.generate_chapter_body(
                    synopsis=syn,
                    world_setting=world_setting,
                    characters=characters,
                    subplot_design=subplot_design,
                    climax_ending_system=climax_ending_system,
                    previous_chapter_body=previous_body,
                )

                # Add to manuscript
                manuscript.chapters.append(body)

                # Update progress
                if progress_idx is not None:
                    manuscript.progress[progress_idx].status = ChapterBodyStatus.COMPLETE
                    manuscript.progress[progress_idx].word_count = body.word_count
                    manuscript.progress[progress_idx].completed_at = datetime.utcnow().isoformat()

                previous_body = body
                manuscript.completed_chapters += 1
                manuscript.total_word_count += body.word_count

            except Exception as e:
                error_msg = str(e)
                if progress_idx is not None:
                    manuscript.progress[progress_idx].status = ChapterBodyStatus.FAILED
                    manuscript.progress[progress_idx].error_message = error_msg
                    manuscript.progress[progress_idx].retry_count += 1

                failed_chapters.append({
                    "chapter_number": syn.chapter_number,
                    "title": syn.title,
                    "error": error_msg,
                })

        # Calculate statistics
        manuscript.total_chapters = len(synopses)

        if manuscript.chapters:
            manuscript.average_coherence = sum(c.coherence_score for c in manuscript.chapters) / len(manuscript.chapters)
            manuscript.average_pacing = sum(c.pacing_score for c in manuscript.chapters) / len(manuscript.chapters)

            # Calculate foreshadowing coverage
            total_foreshadowing = sum(
                len(c.foreshadowing_properly_planted) for c in manuscript.chapters
            )
            manuscript.foreshadowing_coverage = min(1.0, total_foreshadowing / max(1, len(synopses)))

        # Update status
        if manuscript.completed_chapters == manuscript.total_chapters:
            manuscript.status = ManuscriptStatus.COMPLETE
        elif manuscript.completed_chapters > 0:
            manuscript.status = ManuscriptStatus.CHAPTERS_COMPLETE
        else:
            manuscript.status = ManuscriptStatus.FAILED

        generation_time = time.time() - start_time

        return ManuscriptGenerationResult(
            success=manuscript.status in (ManuscriptStatus.COMPLETE, ManuscriptStatus.CHAPTERS_COMPLETE),
            manuscript=manuscript,
            total_chapters=manuscript.completed_chapters,
            total_word_count=manuscript.total_word_count,
            generation_time_seconds=generation_time,
            failed_chapters=failed_chapters,
            average_coherence=manuscript.average_coherence,
            average_pacing=manuscript.average_pacing,
        )

    def _draft_to_sections(
        self,
        draft: ChapterContentDraft,
        synopsis: ChapterSynopsis,
    ) -> list[ChapterBodySection]:
        """Convert chapter content draft to chapter body sections."""
        sections = []

        for i, sec_content in enumerate(draft.section_contents):
            section = ChapterBodySection(
                id=f"sec_{uuid.uuid4().hex[:8]}",
                order=i + 1,
                section_type=self._narrative_to_section_type(sec_content.narrative_point.value),
                content=sec_content.content,
                word_count=sec_content.word_count,
                purpose=sec_content.purpose,
                key_events=sec_content.key_events,
                characters_involved=sec_content.characters_present,
                location=sec_content.location,
                time_period=sec_content.time_period,
                pov_character=sec_content.pov_character,
                tension_level=sec_content.tension_level,
                mood=sec_content.mood,
                plot_point_ids=synopsis.plot_point_ids,
                subplot_ids=[],
                foreshadowing_planted=[],
                foreshadowing_paid_off=[],
            )
            sections.append(section)

        return sections

    def _narrative_to_section_type(self, narrative_point: str) -> ChapterBodySectionType:
        """Convert narrative point to section type."""
        mapping = {
            "opening": ChapterBodySectionType.NARRATIVE,
            "setup": ChapterBodySectionType.NARRATIVE,
            "development": ChapterBodySectionType.NARRATIVE,
            "complication": ChapterBodySectionType.ACTION,
            "climax": ChapterBodySectionType.NARRATIVE,
            "falling_action": ChapterBodySectionType.NARRATIVE,
            "resolution": ChapterBodySectionType.NARRATIVE,
        }
        return mapping.get(narrative_point, ChapterBodySectionType.NARRATIVE)

    def _get_chapter_type(self, synopsis: ChapterSynopsis) -> str:
        """Get chapter type string from synopsis."""
        if synopsis.is_prologue:
            return "prologue"
        if synopsis.is_epilogue:
            return "epilogue"
        if synopsis.is_climax_chapter:
            return "climax"
        if synopsis.is_bridge:
            return "bridge"
        return "normal"

    async def revise_chapter_body(
        self,
        body: ChapterBody,
        revision_notes: list[str],
        world_setting: Optional[WorldSetting] = None,
        characters: Optional[list[Character]] = None,
    ) -> ChapterBody:
        """Revise a chapter body based on revision notes.

        Args:
            body: Chapter body to revise
            revision_notes: Notes for revision
            world_setting: World setting for context
            characters: Character list

        Returns:
            Revised chapter body
        """
        from chai.models.chapter_content import ChapterContentRevision, ChapterContentStatus

        # Create revision
        revision = ChapterContentRevision(
            id=f"rev_{uuid.uuid4().hex[:8]}",
            draft_id=body.id,
            revision_type="moderate",
            issues=revision_notes,
            changes_needed=revision_notes,
            priority=1,
        )

        # Create draft from body
        draft = ChapterContentDraft(
            id=body.id,
            plan_id=body.synopsis_id or "",
            chapter_number=body.chapter_number,
            title=body.title,
            content=body.content,
            section_contents=[],
            word_count=body.word_count,
            status=ChapterContentStatus.COMPLETE,
        )

        # Revise using content engine
        revised_draft = await self.content_engine.revise_content(
            draft=draft,
            revision=revision,
            world_setting=world_setting,
            characters=characters,
        )

        # Update body
        body.content = revised_draft.content
        body.word_count = revised_draft.word_count
        body.status = ChapterBodyStatus.REVISED

        return body

    def analyze_chapter_body(
        self,
        body: ChapterBody,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
    ) -> ChapterBodyAnalysis:
        """Analyze chapter body quality.

        Args:
            body: Chapter body to analyze
            subplot_design: Subplot design for foreshadowing analysis

        Returns:
            ChapterBodyAnalysis with quality metrics
        """
        analysis = ChapterBodyAnalysis(chapter_id=body.id)

        # Word count ratio (assuming 3000 target)
        target = 3000
        if body.word_count > 0:
            analysis.word_count_ratio = target / body.word_count if body.word_count > target else body.word_count / target

        # Structural analysis
        content = body.content
        analysis.has_clear_opening = len(content) > 0 and content[0] not in ['"', "「", "」"]
        analysis.has_climax = any(keyword in content for keyword in ['突然', '然而', '就在此时', '没想到', '刹那间'])
        analysis.has_satisfying_resolution = '。' in content[-100:] if content else False

        # Calculate structure score
        structure_score = 0.0
        if analysis.has_clear_opening:
            structure_score += 0.3
        if analysis.has_climax:
            structure_score += 0.4
        if analysis.has_satisfying_resolution:
            structure_score += 0.3
        analysis.structure_score = structure_score

        # Pacing
        analysis.pacing_score = body.pacing_score if body.pacing_score > 0 else 0.7

        # Foreshadowing
        if subplot_design:
            planted = body.foreshadowing_properly_planted
            paid_off = body.foreshadowing_properly_planted
            analysis.foreshadowing_planted_count = len(planted)
            analysis.foreshadowing_payoff_count = len(paid_off)
            if planted or paid_off:
                analysis.foreshadowing_balance = len(paid_off) / max(1, len(planted))

        # Overall quality
        scores = [
            analysis.structure_score,
            analysis.pacing_score,
            body.coherence_score,
            body.character_voice_score,
        ]
        analysis.overall_quality_score = sum(scores) / len(scores) if scores else 0.5

        # Identify issues
        if analysis.word_count_ratio < 0.7:
            analysis.critical_issues.append("章节字数过少")
        elif analysis.word_count_ratio > 1.3:
            analysis.critical_issues.append("章节字数过多")

        if not analysis.has_climax:
            analysis.minor_issues.append("缺少明显的高潮点")

        return analysis

    def get_manuscript_summary(self, manuscript: ManuscriptBody) -> dict:
        """Get a human-readable summary of the manuscript.

        Args:
            manuscript: Manuscript to summarize

        Returns:
            Summary dictionary
        """
        return {
            "id": manuscript.id,
            "title": manuscript.title,
            "genre": manuscript.genre,
            "total_chapters": manuscript.total_chapters,
            "completed_chapters": manuscript.completed_chapters,
            "total_word_count": manuscript.total_word_count,
            "status": manuscript.status.value,
            "average_coherence": manuscript.average_coherence,
            "average_pacing": manuscript.average_pacing,
            "foreshadowing_coverage": manuscript.foreshadowing_coverage,
            "progress_percentage": (
                manuscript.completed_chapters / manuscript.total_chapters * 100
                if manuscript.total_chapters > 0 else 0
            ),
        }

    def export_manuscript(self, manuscript: ManuscriptBody) -> dict:
        """Export manuscript as dictionary.

        Args:
            manuscript: Manuscript to export

        Returns:
            Export dictionary
        """
        chapters_export = []
        for body in manuscript.chapters:
            chapters_export.append({
                "chapter_number": body.chapter_number,
                "title": body.title,
                "chapter_type": body.chapter_type,
                "content": body.content,
                "word_count": body.word_count,
                "meets_target": body.meets_target,
                "status": body.status.value,
            })

        return {
            "id": manuscript.id,
            "title": manuscript.title,
            "genre": manuscript.genre,
            "total_chapters": manuscript.total_chapters,
            "completed_chapters": manuscript.completed_chapters,
            "total_word_count": manuscript.total_word_count,
            "status": manuscript.status.value,
            "average_coherence": manuscript.average_coherence,
            "average_pacing": manuscript.average_pacing,
            "chapters": chapters_export,
        }
