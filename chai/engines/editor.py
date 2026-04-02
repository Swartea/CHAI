"""Editing and proofreading engine."""

import re
from typing import Optional
from chai.models import Chapter, Novel, Scene, SceneType
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

    def check_dialogue_tags(self, chapter: Chapter) -> list[str]:
        """Check dialogue tag consistency in a chapter."""
        issues = []

        # Common dialogue tag patterns
        dialogue_pattern = r'"[^"]*"'
        tag_pattern = r'[，。；：' ']?([\u4e00-\u9fa5]{1,3})[，。；：' ']?$'

        dialogues = re.findall(dialogue_pattern, chapter.content)
        for i, dialogue in enumerate(dialogues):
            # Check if dialogue ends with proper punctuation
            if not re.search(r'[""]\s*[，。！？、；：' ']', dialogue):
                issues.append(
                    f"Dialogue {i+1} may have inconsistent ending punctuation"
                )

        return issues

    def check_punctuation(self, chapter: Chapter) -> list[str]:
        """Check punctuation consistency in a chapter."""
        issues = []

        content = chapter.content

        # Check for mixing of Chinese and English punctuation
        if re.search(r'[,，]', content) and re.search(r'[,]', content):
            if not (content.count(',') == content.count('，')):
                issues.append(
                    f"Chapter {chapter.number}: Mixed use of Chinese and English commas detected"
                )

        # Check dialogue quote consistency - count ASCII double quotes
        # For Chinese-style quotes, we check balanced usage
        quote_pairs = re.findall(r'"[^"]*"', content)
        # Extract content outside dialogue quotes to check for stray quotes
        content_without_dialogue = re.sub(r'"[^"]*"', '', content)
        stray_quotes = content_without_dialogue.count('"')
        if stray_quotes > 0:
            issues.append(
                f"Chapter {chapter.number}: Found {stray_quotes} unmatched dialogue quotes"
            )

        return issues

    def analyze_pacing(self, chapter: Chapter) -> dict:
        """Analyze the pacing of a chapter (scene vs narration ratio).

        Returns:
            dict with pacing analysis including scene counts, dialogue ratio, etc.
        """
        content = chapter.content

        # Count dialogue portions
        dialogues = re.findall(r'"[^"]*"', content)
        dialogue_chars = sum(len(d) for d in dialogues)
        dialogue_ratio = dialogue_chars / len(content) if content else 0

        # Count paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        # Estimate scene changes (double newlines followed by location indicator)
        scene_indicators = ['。', '！', '？']
        scene_estimate = sum(1 for p in paragraphs if len(p) > 0 and p[-1] in scene_indicators)

        return {
            "chapter_number": chapter.number,
            "word_count": chapter.word_count,
            "paragraph_count": paragraph_count,
            "dialogue_ratio": round(dialogue_ratio, 2),
            "estimated_scenes": scene_estimate,
            "narration_ratio": round(1 - dialogue_ratio, 2),
        }

    def check_foreshadowing(self, novel: Novel) -> list[str]:
        """Check if foreshadowing elements are properly planted and resolved."""
        issues = []

        # Collect all foreshadowing from plot outline
        foreshadowing_plan = novel.plot_outline.foreshadowing_plan if novel.plot_outline else {}

        # Check if chapters in relevant ranges mention foreshadowing themes
        for volume in novel.volumes:
            for chapter in volume.chapters:
                if chapter.plot_point_ids:
                    for pp_id in chapter.plot_point_ids:
                        # Find corresponding plot point
                        if novel.plot_outline:
                            for arc in novel.plot_outline.plot_arcs:
                                for point in arc.plot_points:
                                    if point.id == pp_id and point.foreshadowing:
                                        # Check if chapter content references the foreshadowing
                                        for shadow in point.foreshadowing:
                                            if shadow not in chapter.content:
                                                issues.append(
                                                    f"Chapter {chapter.number}: "
                                                    f"Foreshadowing '{shadow}' may need to be planted"
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

    def generate_full_report(self, novel: Novel) -> str:
        """Generate a comprehensive editorial report for the novel."""
        all_issues = []

        # Collect all consistency issues
        all_issues.extend(self.check_consistency(novel))

        # Collect dialogue tag issues
        for volume in novel.volumes:
            for chapter in volume.chapters:
                all_issues.extend(self.check_dialogue_tags(chapter))
                all_issues.extend(self.check_punctuation(chapter))

        # Collect foreshadowing issues
        all_issues.extend(self.check_foreshadowing(novel))

        # Generate pacing analysis
        pacing_data = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                pacing_data.append(self.analyze_pacing(chapter))

        report_lines = ["=" * 50, "CHAI Editorial Report", "=" * 50]

        if all_issues:
            report_lines.append("\nIssues Found:")
            for issue in all_issues:
                report_lines.append(f"  - {issue}")
        else:
            report_lines.append("\nNo issues found.")

        report_lines.append("\nPacing Analysis:")
        report_lines.append("-" * 40)
        for data in pacing_data:
            report_lines.append(
                f"  Chapter {data['chapter_number']}: "
                f"{data['word_count']} words, "
                f"dialogue ratio: {data['dialogue_ratio']:.0%}, "
                f"~{data['estimated_scenes']} scenes"
            )

        return "\n".join(report_lines)
