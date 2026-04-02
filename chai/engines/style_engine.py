"""Style consistency engine for maintaining narrative voice and tone."""

import re
from typing import Optional
from dataclasses import dataclass
from chai.models import Novel, Chapter
from chai.services import AIService


@dataclass
class StyleProfile:
    """Style profile for a novel or character."""
    tone: list[str]  # e.g., ["epic", "dramatic", "lyrical"]
    descriptive_density: str  # "high", "medium", "low"
    dialogue_ratio: float  # 0.0 to 1.0
    pacing: str  # "fast", "moderate", "slow"
    sentence_structure: str  # "simple", "mixed", "complex"


class StyleEngine:
    """Engine for maintaining style consistency across the novel."""

    def __init__(self, ai_service: AIService):
        """Initialize style engine with AI service."""
        self.ai_service = ai_service
        self._style_profile: Optional[StyleProfile] = None

    def analyze_novel_style(self, novel: Novel) -> StyleProfile:
        """Analyze the style profile of a novel based on its chapters.

        Returns:
            StyleProfile with detected style characteristics
        """
        all_dialogue_chars = 0
        all_content_chars = 0
        tones_detected = []

        for volume in novel.volumes:
            for chapter in volume.chapters:
                content = chapter.content
                all_content_chars += len(content)

                # Count dialogue
                dialogues = re.findall(r'"[^"]*"', content)
                all_dialogue_chars += sum(len(d) for d in dialogues)

                # Detect tone from content
                if any(word in content for word in ["史诗", "壮阔", "宏大"]):
                    tones_detected.append("epic")
                if any(word in content for word in ["紧张", "危机", "悬疑"]):
                    tones_detected.append("dramatic")
                if any(word in content for word in ["优美", "诗意", "柔和"]):
                    tones_detected.append("lyrical")

        dialogue_ratio = all_dialogue_chars / all_content_chars if all_content_chars > 0 else 0.3

        # Determine pacing from word counts
        avg_chapter_words = sum(
            c.word_count for v in novel.volumes for c in v.chapters
        ) / max(1, sum(len(v.chapters) for v in novel.volumes))

        if avg_chapter_words > 3500:
            pacing = "slow"
        elif avg_chapter_words > 2500:
            pacing = "moderate"
        else:
            pacing = "fast"

        # Most common tone
        if tones_detected:
            tone_counts = {}
            for t in tones_detected:
                tone_counts[t] = tone_counts.get(t, 0) + 1
            dominant_tone = max(tone_counts, key=tone_counts.get)
        else:
            dominant_tone = "neutral"

        self._style_profile = StyleProfile(
            tone=[dominant_tone],
            descriptive_density="medium",
            dialogue_ratio=dialogue_ratio,
            pacing=pacing,
            sentence_structure="mixed",
        )

        return self._style_profile

    def get_style_profile(self) -> Optional[StyleProfile]:
        """Get the current style profile."""
        return self._style_profile

    def check_character_voice_consistency(
        self,
        chapter: Chapter,
        characters: list,
    ) -> list[str]:
        """Check if character dialogue is consistent with their established voice.

        Returns:
            List of consistency issues found
        """
        issues = []

        # Extract dialogue by character (simplified - assumes "name:" prefix)
        for char in characters:
            # Find lines that might be this character's dialogue
            char_pattern = rf'{char.name}[：:][^{{}}]*'
            char_lines = re.findall(char_pattern, chapter.content)

            if char_lines:
                # Check speech pattern consistency
                expected_pattern = char.speech_pattern if hasattr(char, 'speech_pattern') else ""

                # If character has a speech pattern defined, check adherence
                if expected_pattern and len(char_lines) > 2:
                    # Simplified check - look for catchphrases
                    if "catchphrase" in char.__dict__ and char.catchphrase:
                        if not any(char.catchphrase in line for line in char_lines[-3:]):
                            issues.append(
                                f"Character {char.name}: Catchphrase not found in recent dialogue"
                            )

        return issues

    def check_descriptive_consistency(
        self,
        chapter: Chapter,
        style_profile: StyleProfile,
    ) -> list[str]:
        """Check if descriptive density is consistent with the style profile.

        Returns:
            List of consistency issues found
        """
        issues = []

        content = chapter.content
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if not paragraphs:
            return issues

        # Calculate descriptive ratio (adjective density)
        adj_pattern = r'的|地|得'
        total_words = len(content)
        descriptive_markers = len(re.findall(adj_pattern, content))
        descriptive_ratio = descriptive_markers / total_words if total_words > 0 else 0

        # Check against style profile
        if style_profile.descriptive_density == "high" and descriptive_ratio < 0.05:
            issues.append(
                f"Chapter {chapter.number}: Descriptive density lower than expected"
            )
        elif style_profile.descriptive_density == "low" and descriptive_ratio > 0.15:
            issues.append(
                f"Chapter {chapter.number}: Descriptive density higher than expected"
            )

        return issues

    def generate_style_guide(
        self,
        novel: Novel,
        style_profile: StyleProfile,
    ) -> str:
        """Generate a style guide based on the novel's established patterns.

        Returns:
            Style guide as a string
        """
        guide_lines = [
            "=" * 50,
            f"《{novel.title}》文风指南",
            "=" * 50,
            "",
            f"基调：{', '.join(style_profile.tone)}",
            f"叙事节奏：{style_profile.pacing}",
            f"对话比例：{style_profile.dialogue_ratio:.0%}",
            f"描写密度：{style_profile.descriptive_density}",
            "",
            "角色语言风格：",
        ]

        # Add character speech patterns
        for char in novel.characters[:5]:
            if hasattr(char, 'speech_pattern') and char.speech_pattern:
                guide_lines.append(f"  {char.name}：{char.speech_pattern}")

        guide_lines.extend([
            "",
            "写作规范：",
            "- 保持第三人称全知视角",
            "- 场景描写要生动，有画面感",
            "- 对话要符合角色性格",
            "- 情节推进要自然流畅",
        ])

        return "\n".join(guide_lines)

    async def polish_for_consistency(
        self,
        chapter: Chapter,
        style_profile: StyleProfile,
    ) -> str:
        """Polish chapter content to ensure style consistency.

        Args:
            chapter: Chapter to polish
            style_profile: Target style profile

        Returns:
            Polished content
        """
        prompt = f"""请根据以下文风要求润色章节内容：

基调：{', '.join(style_profile.tone)}
叙事节奏：{style_profile.pacing}
对话比例：{style_profile.dialogue_ratio:.0%}
描写密度：{style_profile.descriptive_density}

原文：
{chapter.content}

要求：
1. 保持原文情节和结构不变
2. 调整文风以符合上述要求
3. 确保与全书的语调一致
4. 优化表达但保持原意

直接输出润色后的内容，不要添加任何说明。"""

        polished = await self.ai_service.generate(prompt, temperature=0.3)
        return polished.strip()
