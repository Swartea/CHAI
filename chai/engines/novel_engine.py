"""Novel engine - autonomous end-to-end novel writing orchestration."""

import asyncio
from typing import Optional

from chai.models import Novel, Volume, Chapter, WorldSetting, Character, PlotOutline
from chai.services import AIService


class NovelEngine:
    """Autonomous novel writing engine that orchestrates the full pipeline.

    Coordinates StoryPlanner, ChapterWriter, and Editor to produce
    complete novels from theme to polished manuscript.
    """

    def __init__(self, ai_service: AIService):
        """Initialize with AI service."""
        self.ai_service = ai_service

    async def plan(self, genre: str, theme: str) -> Novel:
        """Plan a complete novel (world, characters, plot outline)."""
        from chai.engines import StoryPlanner
        planner = StoryPlanner(self.ai_service)
        return await planner.plan_novel(genre, theme)

    async def write(self, novel: Novel) -> Novel:
        """Write all chapters of the novel."""
        from chai.engines import ChapterWriter
        writer = ChapterWriter(self.ai_service)

        # Ensure novel has volumes with chapter outlines
        if not novel.volumes:
            self._expand_outline_to_volumes(novel)

        return await writer.write_novel(novel)

    async def proofread(self, novel: Novel) -> Novel:
        """Proofread and polish the entire novel."""
        from chai.engines import Editor
        editor = Editor(self.ai_service)
        return await editor.proofread_novel(novel)

    async def run_full_workflow(
        self,
        genre: str,
        theme: str,
        proofread: bool = True,
    ) -> Novel:
        """Run the complete autonomous novel writing workflow.

        Steps:
        1. Plan: Create world, characters, and plot outline
        2. Write: Generate all chapter content
        3. Proofread: Polish all chapters (optional)

        Args:
            genre: Novel genre (fantasy, sci-fi, urban, etc.)
            theme: Central theme or topic
            proofread: Whether to run proofreading pass

        Returns:
            Complete Novel with all volumes, chapters, and content
        """
        print(f"[NovelEngine] Starting full workflow: {genre} - {theme}")

        # Step 1: Plan
        print("[NovelEngine] Phase 1: Planning world, characters, and plot...")
        novel = await self.plan(genre, theme)

        # Step 2: Write
        print("[NovelEngine] Phase 2: Writing all chapters...")
        novel = await self.write(novel)

        # Step 3: Proofread
        if proofread:
            print("[NovelEngine] Phase 3: Proofreading and polishing...")
            novel = await self.proofread(novel)

        total_words = sum(
            ch.word_count
            for vol in novel.volumes
            for ch in vol.chapters
        )
        total_chapters = sum(len(vol.chapters) for vol in novel.volumes)
        print(f"[NovelEngine] Complete: {total_chapters} chapters, {total_words} words")
        return novel

    def _expand_outline_to_volumes(self, novel: Novel) -> None:
        """Expand plot outline into volumes and chapter outlines.

        Converts the PlotOutline (plot points with chapter ranges) into
        actual Volume and Chapter structures with detailed chapter outlines.
        """
        if not novel.plot_outline or not novel.plot_outline.plot_arcs:
            # Create a default single-volume structure
            chapters = [
                Chapter(
                    id=f"ch_{i}",
                    number=i + 1,
                    title=f"第{i + 1}章",
                    summary="",
                    status="pending",
                )
                for i in range(10)
            ]
            volume = Volume(
                id="vol_1",
                title="第一卷",
                number=1,
                description="自动生成章节",
                chapters=chapters,
            )
            novel.volumes = [volume]
            return

        # Group chapters by volume based on plot structure
        main_arc = novel.plot_outline.plot_arcs[0]
        plot_points = main_arc.plot_points

        # Determine number of volumes based on plot points
        # Each plot point typically covers 2-4 chapters
        chapters_per_point = 3
        total_chapters = len(plot_points) * chapters_per_point

        # Create volumes (1 volume per 2-3 plot points typically)
        volumes = []
        chapters_per_volume = chapters_per_point * 2  # 2 plot points per volume

        for v_idx in range(0, len(plot_points), 2):
            volume_chapters = []
            pp_indices = range(v_idx, min(v_idx + 2, len(plot_points)))

            for pp_i in pp_indices:
                pp = plot_points[pp_i]
                start_ch = pp_i * chapters_per_point + 1

                for i in range(chapters_per_point):
                    ch_num = start_ch + i
                    chapter = Chapter(
                        id=f"ch_{ch_num}",
                        number=ch_num,
                        title=f"第{ch_num}章：{pp.title if i == 0 else '续'}",
                        summary=pp.description if i == 0 else "",
                        plot_point_ids=[pp.id],
                        characters_involved=pp.characters_involved,
                        status="pending",
                    )
                    volume_chapters.append(chapter)

            volume = Volume(
                id=f"vol_{v_idx // 2 + 1}",
                title=f"第{v_idx // 2 + 1}卷",
                number=v_idx // 2 + 1,
                description=f"情节：{', '.join(plot_points[pi].title for pi in pp_indices if pi < len(plot_points))}",
                chapters=volume_chapters,
            )
            volumes.append(volume)

        novel.volumes = volumes

    def get_novel_status(self, novel: Novel) -> dict:
        """Get a status summary of the novel."""
        total_chapters = sum(len(vol.chapters) for vol in novel.volumes)
        written_chapters = sum(
            1 for vol in novel.volumes
            for ch in vol.chapters
            if ch.status == "complete" or ch.content
        )
        total_words = sum(
            ch.word_count for vol in novel.volumes for ch in vol.chapters
        )

        return {
            "title": novel.title,
            "genre": novel.genre,
            "total_volumes": len(novel.volumes),
            "total_chapters": total_chapters,
            "written_chapters": written_chapters,
            "total_words": total_words,
            "progress": written_chapters / total_chapters if total_chapters else 0,
        }