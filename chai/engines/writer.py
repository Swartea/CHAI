"""Chapter writing engine."""

from typing import Optional
from chai.models import Novel, Chapter, Volume
from chai.services import AIService


class ChapterWriter:
    """Engine for generating chapter content."""

    def __init__(self, ai_service: AIService):
        """Initialize chapter writer with AI service."""
        self.ai_service = ai_service

    async def write_chapter(
        self,
        novel: Novel,
        chapter_number: int,
        chapter_outline: dict,
        previous_chapter: Optional[Chapter] = None,
    ) -> Chapter:
        """Write a single chapter."""
        chapter_summary = previous_chapter.summary if previous_chapter else None

        content = await self.ai_service.generate_chapter(
            chapter_outline=chapter_outline,
            world_setting=novel.world_setting.model_dump() if novel.world_setting else {},
            characters=[c.model_dump() for c in novel.characters],
            previous_chapter_summary=chapter_summary,
        )

        chapter = Chapter(
            id=f"ch_{chapter_number}",
            number=chapter_number,
            title=chapter_outline.get("title", f"第{chapter_number}章"),
            summary=chapter_outline.get("summary", ""),
            content=content,
            word_count=len(content),
            target_word_count=novel.target_chapter_word_count[1]
                if novel.target_chapter_word_count else 3000,
            status="complete",
        )

        return chapter

    async def write_volume(
        self,
        novel: Novel,
        volume: Volume,
        start_chapter: int,
    ) -> Volume:
        """Write all chapters in a volume."""
        previous_chapter = None

        for i, chapter_outline in enumerate(volume.chapters):
            chapter = await self.write_chapter(
                novel=novel,
                chapter_number=start_chapter + i,
                chapter_outline=chapter_outline.model_dump()
                    if hasattr(chapter_outline, 'model_dump') else chapter_outline,
                previous_chapter=previous_chapter,
            )
            volume.chapters[i] = chapter
            previous_chapter = chapter

        return volume

    async def write_novel(self, novel: Novel) -> Novel:
        """Write entire novel chapter by chapter."""
        previous_chapter = None
        all_chapters = []

        for volume in novel.volumes:
            for i, chapter_outline in enumerate(volume.chapters):
                chapter = await self.write_chapter(
                    novel=novel,
                    chapter_number=len(all_chapters) + 1,
                    chapter_outline=chapter_outline.model_dump()
                        if hasattr(chapter_outline, 'model_dump') else chapter_outline,
                    previous_chapter=previous_chapter,
                )
                all_chapters.append(chapter)
                previous_chapter = chapter

        total_words = sum(c.word_count for c in all_chapters)
        print(f"Written {len(all_chapters)} chapters, {total_words} total words")

        return novel
