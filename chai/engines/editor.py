"""Editing and proofreading engine."""

from chai.models import Chapter, Novel
from chai.services import AIService


class Editor:
    """Engine for editing and proofreading novel content."""

    def __init__(self, ai_service: AIService):
        """Initialize editor with AI service."""
        self.ai_service = ai_service

    async def proofread_chapter(self, chapter: Chapter) -> Chapter:
        """Proofread and polish a chapter."""
        polished_content = await self.ai_service.proofread_chapter(chapter.content)

        chapter.content = polished_content
        chapter.word_count = len(polished_content)
        chapter.status = "edited"

        return chapter

    async def proofread_novel(self, novel: Novel) -> Novel:
        """Proofread entire novel."""
        total_chapters = 0
        for volume in novel.volumes:
            for chapter in volume.chapters:
                await self.proofread_chapter(chapter)
                total_chapters += 1

        print(f"Proofread {total_chapters} chapters")
        return novel

    def check_consistency(self, novel: Novel) -> list[str]:
        """Check for consistency issues in the novel."""
        issues = []

        for volume in novel.volumes:
            for chapter in volume.chapters:
                if chapter.word_count < novel.target_chapter_word_count[0]:
                    issues.append(
                        f"Chapter {chapter.number} is below minimum word count "
                        f"({chapter.word_count} < {novel.target_chapter_word_count[0]})"
                    )
                if chapter.word_count > novel.target_chapter_word_count[1] * 1.2:
                    issues.append(
                        f"Chapter {chapter.number} significantly exceeds maximum word count"
                    )

        return issues

    def generate_consistency_report(self, novel: Novel) -> str:
        """Generate a consistency report for the novel."""
        issues = self.check_consistency(novel)

        if not issues:
            return "Novel passes consistency checks."

        report = ["Consistency Report:", "-" * 40]
        for issue in issues:
            report.append(f"- {issue}")

        return "\n".join(report)
