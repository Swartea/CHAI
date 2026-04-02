"""Style consistency engine for maintaining narrative voice and tone throughout the novel."""

import re
from typing import Optional
from chai.models import Novel, Chapter
from chai.models.style_consistency import (
    StyleConsistencyType,
    NarrativeTone,
    NarrativeVoice,
    PacingLevel,
    DescriptiveDensity,
    SentenceComplexity,
    VocabularyLevel,
    StyleConsistencyIssue,
    StyleConsistencyStatus,
    StyleConsistencyCheck,
    StyleProfile,
    StyleConsistencyAnalysis,
    StyleConsistencyPlan,
    StyleConsistencyRevision,
    StyleConsistencyTemplate,
    StyleConsistencyDraft,
    CharacterVoiceProfile,
)
from chai.services import AIService


# Pre-built style consistency templates
STYLE_TEMPLATES = {
    "epic_fantasy": StyleConsistencyTemplate(
        template_name="epic_fantasy",
        template_description="Epic fantasy style with grand, heroic tone and rich descriptions",
        tones=[NarrativeTone.EPIC, NarrativeTone.DRAMATIC],
        narrative_voice=NarrativeVoice.THIRD_OMNISCIENT,
        pacing=PacingLevel.MODERATE,
        descriptive_density=DescriptiveDensity.HIGH,
        dialogue_ratio=0.25,
        sentence_structure=SentenceComplexity.MIXED,
        vocabulary_level=VocabularyLevel.SOPHISTICATED,
        strict_tone_matching=False,
        strict_voice_matching=True,
        allow_pacing_variation=True,
        character_voice_preservation=True,
    ),
    "urban_fantasy": StyleConsistencyTemplate(
        template_name="urban_fantasy",
        template_description="Modern urban fantasy with balance of action and dialogue",
        tones=[NarrativeTone.DRAMATIC, NarrativeTone.MYSTERIOUS, NarrativeTone.LIGHT],
        narrative_voice=NarrativeVoice.THIRD_LIMITED,
        pacing=PacingLevel.MODERATE,
        descriptive_density=DescriptiveDensity.MEDIUM,
        dialogue_ratio=0.4,
        sentence_structure=SentenceComplexity.MIXED,
        vocabulary_level=VocabularyLevel.MODERATE,
        strict_tone_matching=False,
        strict_voice_matching=True,
        allow_pacing_variation=True,
        character_voice_preservation=True,
    ),
    "romance": StyleConsistencyTemplate(
        template_name="romance",
        template_description="Romantic style with intimate tone and emotional depth",
        tones=[NarrativeTone.ROMANTIC, NarrativeTone.INTIMATE, NarrativeTone.LYRICAL],
        narrative_voice=NarrativeVoice.THIRD_LIMITED,
        pacing=PacingLevel.SLOW,
        descriptive_density=DescriptiveDensity.MEDIUM,
        dialogue_ratio=0.45,
        sentence_structure=SentenceComplexity.MIXED,
        vocabulary_level=VocabularyLevel.MODERATE,
        strict_tone_matching=False,
        strict_voice_matching=True,
        allow_pacing_variation=True,
        character_voice_preservation=True,
    ),
    "mystery": StyleConsistencyTemplate(
        template_name="mystery",
        template_description="Mystery/suspense style with tense pacing and mysterious tone",
        tones=[NarrativeTone.MYSTERIOUS, NarrativeTone.SUSPENSEFUL, NarrativeTone.DARK],
        narrative_voice=NarrativeVoice.THIRD_LIMITED,
        pacing=PacingLevel.MODERATE,
        descriptive_density=DescriptiveDensity.MEDIUM,
        dialogue_ratio=0.35,
        sentence_structure=SentenceComplexity.COMPLEX,
        vocabulary_level=VocabularyLevel.SOPHISTICATED,
        strict_tone_matching=True,
        strict_voice_matching=True,
        allow_pacing_variation=False,
        character_voice_preservation=True,
    ),
    "scifi": StyleConsistencyTemplate(
        template_name="scifi",
        template_description="Science fiction style with technical precision and grand scope",
        tones=[NarrativeTone.EPIC, NarrativeTone.DRAMATIC, NarrativeTone.DARK],
        narrative_voice=NarrativeVoice.THIRD_OMNISCIENT,
        pacing=PacingLevel.MODERATE,
        descriptive_density=DescriptiveDensity.HIGH,
        dialogue_ratio=0.3,
        sentence_structure=SentenceComplexity.COMPLEX,
        vocabulary_level=VocabularyLevel.SCHOLARLY,
        strict_tone_matching=False,
        strict_voice_matching=True,
        allow_pacing_variation=True,
        character_voice_preservation=True,
    ),
    "literary": StyleConsistencyTemplate(
        template_name="literary",
        template_description="Literary fiction with lyrical prose and deep introspection",
        tones=[NarrativeTone.LYRICAL, NarrativeTone.INTIMATE, NarrativeTone.NOSTALGIC],
        narrative_voice=NarrativeVoice.THIRD_LIMITED,
        pacing=PacingLevel.SLOW,
        descriptive_density=DescriptiveDensity.HIGH,
        dialogue_ratio=0.25,
        sentence_structure=SentenceComplexity.COMPLEX,
        vocabulary_level=VocabularyLevel.SOPHISTICATED,
        strict_tone_matching=True,
        strict_voice_matching=True,
        allow_pacing_variation=False,
        character_voice_preservation=True,
    ),
    "action_adventure": StyleConsistencyTemplate(
        template_name="action_adventure",
        template_description="Fast-paced action adventure with dynamic pacing",
        tones=[NarrativeTone.DRAMATIC, NarrativeTone.EPIC, NarrativeTone.LIGHT],
        narrative_voice=NarrativeVoice.THIRD_OMNISCIENT,
        pacing=PacingLevel.FAST,
        descriptive_density=DescriptiveDensity.LOW,
        dialogue_ratio=0.35,
        sentence_structure=SentenceComplexity.SIMPLE,
        vocabulary_level=VocabularyLevel.MODERATE,
        strict_tone_matching=False,
        strict_voice_matching=True,
        allow_pacing_variation=True,
        character_voice_preservation=True,
    ),
    "horror": StyleConsistencyTemplate(
        template_name="horror",
        template_description="Horror style with dark tone and building suspense",
        tones=[NarrativeTone.DARK, NarrativeTone.MYSTERIOUS, NarrativeTone.SUSPENSEFUL],
        narrative_voice=NarrativeVoice.THIRD_LIMITED,
        pacing=PacingLevel.MODERATE,
        descriptive_density=DescriptiveDensity.HIGH,
        dialogue_ratio=0.25,
        sentence_structure=SentenceComplexity.MIXED,
        vocabulary_level=VocabularyLevel.SOPHISTICATED,
        strict_tone_matching=True,
        strict_voice_matching=True,
        allow_pacing_variation=False,
        character_voice_preservation=True,
    ),
}


class StyleEngine:
    """Engine for maintaining style consistency across the novel."""

    def __init__(self, ai_service: AIService):
        """Initialize style engine with AI service."""
        self.ai_service = ai_service
        self._style_profile: Optional[StyleProfile] = None
        self._templates = dict(STYLE_TEMPLATES)

    def analyze_novel_style(self, novel: Novel) -> StyleProfile:
        """Analyze the style profile of a novel based on its chapters.

        Returns:
            StyleProfile with detected style characteristics
        """
        all_dialogue_chars = 0
        all_content_chars = 0
        tones_detected: dict[str, int] = {}

        # Tone keywords mapping
        tone_keywords = {
            "epic": ["史诗", "壮阔", "宏大", "伟大", "传奇"],
            "dramatic": ["紧张", "危机", "戏剧性", "关键", "决定"],
            "lyrical": ["优美", "诗意", "柔和", "温柔", "婉约"],
            "intimate": ["亲密", "内心", "感受", "心灵", "私密"],
            "mysterious": ["神秘", "谜", "未知", "诡异", "悬疑"],
            "romantic": ["爱", "情", "心", "吻", "恋"],
            "dark": ["黑暗", "绝望", "死亡", "恐惧", "阴沉"],
            "light": ["轻松", "愉快", "阳光", "欢笑", "希望"],
            "gritty": ["粗糙", "真实", "冷酷", "无情", "血腥"],
            "whimsical": ["奇妙", "梦幻", "童话", "魔法", "奇异"],
            "suspenseful": ["紧张", "悬念", "心跳", "屏息", "危机"],
            "nostalgic": ["回忆", "过去", "怀念", "往事", "当年"],
        }

        for volume in novel.volumes:
            for chapter in volume.chapters:
                content = chapter.content
                if not content:
                    continue
                all_content_chars += len(content)

                # Count dialogue
                dialogues = re.findall(r'"[^"]*"', content)
                all_dialogue_chars += sum(len(d) for d in dialogues)

                # Detect tones from content
                for tone, keywords in tone_keywords.items():
                    for keyword in keywords:
                        if keyword in content:
                            tones_detected[tone] = tones_detected.get(tone, 0) + 1

        dialogue_ratio = all_dialogue_chars / all_content_chars if all_content_chars > 0 else 0.3

        # Determine pacing from word counts
        total_chapters = sum(len(v.chapters) for v in novel.volumes)
        avg_chapter_words = 0
        if total_chapters > 0:
            total_words = sum(
                c.word_count for v in novel.volumes for c in v.chapters
            )
            avg_chapter_words = total_words / total_chapters

        if avg_chapter_words > 3500:
            pacing = PacingLevel.SLOW
        elif avg_chapter_words > 2500:
            pacing = PacingLevel.MODERATE
        else:
            pacing = PacingLevel.FAST

        # Determine descriptive density
        adj_pattern = r'的|地|得'
        descriptive_markers = 0
        for v in novel.volumes:
            for c in v.chapters:
                descriptive_markers += len(re.findall(adj_pattern, c.content))

        descriptive_ratio = descriptive_markers / all_content_chars if all_content_chars > 0 else 0
        if descriptive_ratio > 0.1:
            density = DescriptiveDensity.HIGH
        elif descriptive_ratio > 0.05:
            density = DescriptiveDensity.MEDIUM
        else:
            density = DescriptiveDensity.LOW

        # Most common tones
        narrative_tones = []
        for tone, count in tones_detected.items():
            if count >= 2:  # Only include if appears multiple times
                try:
                    narrative_tones.append(NarrativeTone(tone))
                except ValueError:
                    pass

        if not narrative_tones:
            narrative_tones = [NarrativeTone.DRAMATIC]

        # Count tone frequencies
        tone_counts: dict[str, int] = {}
        for tone_str, count in tones_detected.items():
            tone_counts[tone_str] = count
        dominant_tone_str = max(tone_counts, key=tone_counts.get) if tone_counts else "dramatic"
        try:
            dominant_tone = NarrativeTone(dominant_tone_str)
        except ValueError:
            dominant_tone = NarrativeTone.DRAMATIC

        self._style_profile = StyleProfile(
            tones=narrative_tones,
            dominant_tone=dominant_tone,
            narrative_voice=NarrativeVoice.THIRD_OMNISCIENT,
            pacing=pacing,
            descriptive_density=density,
            dialogue_ratio=dialogue_ratio,
            sentence_structure=SentenceComplexity.MIXED,
            vocabulary_level=VocabularyLevel.MODERATE,
        )

        return self._style_profile

    def get_style_profile(self) -> Optional[StyleProfile]:
        """Get the current style profile."""
        return self._style_profile

    def set_style_profile(self, profile: StyleProfile) -> None:
        """Set the style profile."""
        self._style_profile = profile

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
        density_map = {
            DescriptiveDensity.HIGH: 0.05,
            DescriptiveDensity.MEDIUM: 0.03,
            DescriptiveDensity.LOW: 0.01,
        }
        expected_min = density_map.get(style_profile.descriptive_density, 0.03)

        if descriptive_ratio < expected_min:
            issues.append(
                f"Chapter {chapter.number}: Descriptive density ({descriptive_ratio:.2%}) "
                f"lower than expected ({style_profile.descriptive_density.value})"
            )

        return issues

    def check_tone_consistency(
        self,
        chapter: Chapter,
        style_profile: StyleProfile,
    ) -> StyleConsistencyCheck:
        """Check tone consistency within a chapter.

        Returns:
            StyleConsistencyCheck with tone consistency results
        """
        content = chapter.content
        issues = []
        recommendations = []

        # Tone keywords
        tone_keywords = {
            NarrativeTone.EPIC: ["史诗", "壮阔", "宏大", "伟大", "传奇"],
            NarrativeTone.DRAMATIC: ["紧张", "危机", "戏剧性", "关键", "决定"],
            NarrativeTone.LYRICAL: ["优美", "诗意", "柔和", "温柔", "婉约"],
            NarrativeTone.INTIMATE: ["亲密", "内心", "感受", "心灵", "私密"],
            NarrativeTone.MYSTERIOUS: ["神秘", "谜", "未知", "诡异", "悬疑"],
            NarrativeTone.ROMANTIC: ["爱", "情", "心", "吻", "恋"],
            NarrativeTone.DARK: ["黑暗", "绝望", "死亡", "恐惧", "阴沉"],
            NarrativeTone.LIGHT: ["轻松", "愉快", "阳光", "欢笑", "希望"],
            NarrativeTone.GRITTY: ["粗糙", "真实", "冷酷", "无情", "血腥"],
            NarrativeTone.WHIMSICAL: ["奇妙", "梦幻", "童话", "魔法", "奇异"],
            NarrativeTone.SUSPENSEFUL: ["紧张", "悬念", "心跳", "屏息", "危机"],
            NarrativeTone.NOSTALGIC: ["回忆", "过去", "怀念", "往事", "当年"],
        }

        # Count tone occurrences
        tone_counts: dict[str, int] = {}
        for tone, keywords in tone_keywords.items():
            count = sum(content.count(kw) for kw in keywords)
            if count > 0:
                tone_counts[tone.value] = count

        # Check for unexpected tones
        expected_tones = {t.value for t in style_profile.tones}
        found_tones = set(tone_counts.keys())

        unexpected_tones = found_tones - expected_tones
        if unexpected_tones and len(found_tones) > 2:
            issues.append(f"Unexpected tone shifts detected: {', '.join(unexpected_tones)}")
            recommendations.append("Stay consistent with the established narrative tone")

        # Calculate tone consistency score
        if tone_counts:
            dominant_tone = max(tone_counts, key=tone_counts.get)
            if dominant_tone in expected_tones:
                score = 0.9
            else:
                score = 0.5
        else:
            score = 0.7  # Neutral content

        status = StyleConsistencyStatus.CONSISTENT
        if score < 0.5:
            status = StyleConsistencyStatus.INCONSISTENT
        elif score < 0.7:
            status = StyleConsistencyStatus.MAJOR_ISSUES
        elif score < 0.9:
            status = StyleConsistencyStatus.MINOR_ISSUES

        return StyleConsistencyCheck(
            check_type=StyleConsistencyType.TONE,
            status=status,
            score=score,
            issues=issues,
            chapter_number=chapter.number,
            recommendations=recommendations,
        )

    def check_pacing_consistency(
        self,
        chapter: Chapter,
        style_profile: StyleProfile,
    ) -> StyleConsistencyCheck:
        """Check pacing consistency within a chapter.

        Returns:
            StyleConsistencyCheck with pacing consistency results
        """
        content = chapter.content
        issues = []
        recommendations = []

        # Analyze paragraph lengths as pacing indicator
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            return StyleConsistencyCheck(
                check_type=StyleConsistencyType.PACING,
                status=StyleConsistencyStatus.CONSISTENT,
                score=1.0,
                issues=[],
                chapter_number=chapter.number,
                recommendations=[],
            )

        paragraph_lengths = [len(p) for p in paragraphs]
        avg_length = sum(paragraph_lengths) / len(paragraph_lengths)

        # Check for sudden length changes (pacing issues)
        short_paragraphs = sum(1 for l in paragraph_lengths if l < 50)
        long_paragraphs = sum(1 for l in paragraph_lengths if l > 300)
        pacing_variation_ratio = long_paragraphs / len(paragraph_lengths) if paragraphs else 0

        expected_pacing_map = {
            PacingLevel.FAST: 0.4,  # More short paragraphs
            PacingLevel.MODERATE: 0.2,
            PacingLevel.SLOW: 0.1,  # Fewer short paragraphs
        }
        expected_variation = expected_pacing_map.get(style_profile.pacing, 0.2)

        if abs(pacing_variation_ratio - expected_variation) > 0.3:
            issues.append(
                f"Pacing inconsistency: {pacing_variation_ratio:.0%} long paragraphs, "
                f"expected ~{expected_variation:.0%} for {style_profile.pacing.value} pacing"
            )
            recommendations.append(
                f"Adjust paragraph lengths to match {style_profile.pacing.value} pacing"
            )

        score = 1.0 - abs(pacing_variation_ratio - expected_variation)
        score = max(0.0, min(1.0, score))

        status = StyleConsistencyStatus.CONSISTENT
        if score < 0.5:
            status = StyleConsistencyStatus.INCONSISTENT
        elif score < 0.7:
            status = StyleConsistencyStatus.MAJOR_ISSUES
        elif score < 0.9:
            status = StyleConsistencyStatus.MINOR_ISSUES

        return StyleConsistencyCheck(
            check_type=StyleConsistencyType.PACING,
            status=status,
            score=score,
            issues=issues,
            chapter_number=chapter.number,
            recommendations=recommendations,
        )

    def check_dialogue_ratio_consistency(
        self,
        chapter: Chapter,
        style_profile: StyleProfile,
    ) -> StyleConsistencyCheck:
        """Check dialogue ratio consistency within a chapter.

        Returns:
            StyleConsistencyCheck with dialogue ratio consistency results
        """
        content = chapter.content
        issues = []
        recommendations = []

        # Count dialogue
        dialogues = re.findall(r'"[^"]*"', content)
        dialogue_chars = sum(len(d) for d in dialogues)
        total_chars = len(content)

        if total_chars == 0:
            return StyleConsistencyCheck(
                check_type=StyleConsistencyType.DIALOGUE_RATIO,
                status=StyleConsistencyStatus.CONSISTENT,
                score=1.0,
                issues=[],
                chapter_number=chapter.number,
                recommendations=[],
            )

        dialogue_ratio = dialogue_chars / total_chars
        expected_ratio = style_profile.dialogue_ratio

        # Allow 15% variance
        variance = abs(dialogue_ratio - expected_ratio) / expected_ratio if expected_ratio > 0 else 1.0

        if variance > 0.5:
            if dialogue_ratio > expected_ratio:
                issues.append(
                    f"Too much dialogue in chapter {chapter.number}: "
                    f"{dialogue_ratio:.0%} vs expected ~{expected_ratio:.0%}"
                )
                recommendations.append("Reduce dialogue or add more narration")
            else:
                issues.append(
                    f"Too little dialogue in chapter {chapter.number}: "
                    f"{dialogue_ratio:.0%} vs expected ~{expected_ratio:.0%}"
                )
                recommendations.append("Add more dialogue to balance with narration")

        score = max(0.0, 1.0 - variance)

        status = StyleConsistencyStatus.CONSISTENT
        if score < 0.5:
            status = StyleConsistencyStatus.INCONSISTENT
        elif score < 0.7:
            status = StyleConsistencyStatus.MAJOR_ISSUES
        elif score < 0.9:
            status = StyleConsistencyStatus.MINOR_ISSUES

        return StyleConsistencyCheck(
            check_type=StyleConsistencyType.DIALOGUE_RATIO,
            status=status,
            score=score,
            issues=issues,
            chapter_number=chapter.number,
            recommendations=recommendations,
        )

    def analyze_consistency(
        self,
        novel: Novel,
        style_profile: Optional[StyleProfile] = None,
    ) -> StyleConsistencyAnalysis:
        """Perform comprehensive style consistency analysis.

        Args:
            novel: Novel to analyze
            style_profile: Optional style profile to compare against

        Returns:
            StyleConsistencyAnalysis with all consistency checks
        """
        if style_profile is None:
            style_profile = self._style_profile or self.analyze_novel_style(novel)

        all_issues: list[str] = []
        all_recommendations: list[str] = []
        chapter_issues: dict[int, list[str]] = {}

        # Collect all checks
        tone_checks: list[StyleConsistencyCheck] = []
        pacing_checks: list[StyleConsistencyCheck] = []
        dialogue_checks: list[StyleConsistencyCheck] = []

        for volume in novel.volumes:
            for chapter in volume.chapters:
                if not chapter.content:
                    continue

                # Tone check
                tone_check = self.check_tone_consistency(chapter, style_profile)
                tone_checks.append(tone_check)

                # Pacing check
                pacing_check = self.check_pacing_consistency(chapter, style_profile)
                pacing_checks.append(pacing_check)

                # Dialogue ratio check
                dialogue_check = self.check_dialogue_ratio_consistency(chapter, style_profile)
                dialogue_checks.append(dialogue_check)

                # Collect issues
                chapter_issues[chapter.number] = (
                    tone_check.issues + pacing_check.issues + dialogue_check.issues
                )

        # Calculate overall scores
        all_checks = tone_checks + pacing_checks + dialogue_checks
        if all_checks:
            overall_score = sum(c.score for c in all_checks) / len(all_checks)
        else:
            overall_score = 1.0

        # Determine overall status
        if overall_score >= 0.9:
            overall_status = StyleConsistencyStatus.CONSISTENT
        elif overall_score >= 0.7:
            overall_status = StyleConsistencyStatus.MINOR_ISSUES
        elif overall_score >= 0.5:
            overall_status = StyleConsistencyStatus.MAJOR_ISSUES
        else:
            overall_status = StyleConsistencyStatus.INCONSISTENT

        # Aggregate all issues
        for checks in [tone_checks, pacing_checks, dialogue_checks]:
            for check in checks:
                all_issues.extend(check.issues)
                all_recommendations.extend(check.recommendations)

        return StyleConsistencyAnalysis(
            overall_status=overall_status,
            overall_score=overall_score,
            tone_check=tone_checks[0] if tone_checks else None,
            pacing_check=pacing_checks[0] if pacing_checks else None,
            dialogue_ratio_check=dialogue_checks[0] if dialogue_checks else None,
            all_issues=all_issues,
            all_recommendations=all_recommendations,
            chapter_issues=chapter_issues,
        )

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
            f"基调：{', '.join(t.value for t in style_profile.tones)}",
            f"主导基调：{style_profile.dominant_tone.value}",
            f"叙事声音：{style_profile.narrative_voice.value}",
            f"叙事节奏：{style_profile.pacing.value}",
            f"对话比例：{style_profile.dialogue_ratio:.0%}",
            f"描写密度：{style_profile.descriptive_density.value}",
            f"句式结构：{style_profile.sentence_structure.value}",
            f"词汇层次：{style_profile.vocabulary_level.value}",
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

    def get_template(self, template_name: str) -> Optional[StyleConsistencyTemplate]:
        """Get a style template by name."""
        return self._templates.get(template_name)

    def get_all_templates(self) -> dict[str, StyleConsistencyTemplate]:
        """Get all available style templates."""
        return self._templates.copy()

    def apply_template(self, template_name: str) -> Optional[StyleProfile]:
        """Apply a style template and return the resulting profile."""
        template = self._templates.get(template_name)
        if template is None:
            return None
        self._style_profile = template.to_style_profile()
        return self._style_profile

    def create_character_voice_profile(
        self,
        character,
        sample_dialogue: list[str],
    ) -> CharacterVoiceProfile:
        """Create a voice profile for a character based on sample dialogue.

        Args:
            character: Character object
            sample_dialogue: List of dialogue lines for this character

        Returns:
            CharacterVoiceProfile with voice characteristics
        """
        if not sample_dialogue:
            return CharacterVoiceProfile(
                character_id=character.id if hasattr(character, 'id') else "unknown",
                character_name=character.name if hasattr(character, 'name') else "Unknown",
            )

        combined = " ".join(sample_dialogue)

        # Analyze sentence complexity
        sentence_ends = re.findall(r'[。！？.!?]', combined)
        avg_sentence_length = len(combined) / max(1, len(sentence_ends))

        if avg_sentence_length < 20:
            sentence_structure = SentenceComplexity.SIMPLE
        elif avg_sentence_length < 40:
            sentence_structure = SentenceComplexity.MIXED
        else:
            sentence_structure = SentenceComplexity.COMPLEX

        # Analyze vocabulary sophistication (simple heuristic)
        sophisticated_words = ["然而", "因此", "虽然", "但是", "于是", "倘若", "既已", "何必"]
        simple_count = sum(combined.count(w) for w in sophisticated_words)

        if simple_count > 5:
            vocab_level = VocabularyLevel.SOPHISTICATED
        elif simple_count > 2:
            vocab_level = VocabularyLevel.MODERATE
        else:
            vocab_level = VocabularyLevel.SIMPLE

        return CharacterVoiceProfile(
            character_id=character.id if hasattr(character, 'id') else "unknown",
            character_name=character.name if hasattr(character, 'name') else "Unknown",
            speech_pattern=character.speech_pattern if hasattr(character, 'speech_pattern') else "",
            vocabulary_level=vocab_level,
            sentence_structure=sentence_structure,
            formality_level="neutral",
            use_of_honorifics=True,
            catchphrases=character.catchphrase if hasattr(character, 'catchphrase') and character.catchphrase else [],
            filler_words=[],
            verbal_tics=[],
            emotional_restraint="moderate",
            directness="moderate",
            consistency_score=0.9,
            issues=[],
        )

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

基调：{', '.join(t.value for t in style_profile.tones)}
主导基调：{style_profile.dominant_tone.value}
叙事声音：{style_profile.narrative_voice.value}
叙事节奏：{style_profile.pacing.value}
对话比例：{style_profile.dialogue_ratio:.0%}
描写密度：{style_profile.descriptive_density.value}
句式结构：{style_profile.sentence_structure.value}
词汇层次：{style_profile.vocabulary_level.value}

原文：
{chapter.content}

要求：
1. 保持原文情节和结构不变
2. 调整文风以符合上述要求
3. 确保与全书的语调一致
4. 优化表达但保持原意
5. 保持角色语言风格一致

直接输出润色后的内容，不要添加任何说明。"""

        polished = await self.ai_service.generate(prompt, temperature=0.3)
        return polished.strip()

    async def revise_for_consistency(
        self,
        chapter: Chapter,
        style_profile: Optional[StyleProfile] = None,
    ) -> StyleConsistencyRevision:
        """Revise chapter for style consistency.

        Args:
            chapter: Chapter to revise
            style_profile: Optional style profile to use

        Returns:
            StyleConsistencyRevision with original, revised content and issues
        """
        if style_profile is None:
            style_profile = self._style_profile or StyleProfile(
                tones=[NarrativeTone.DRAMATIC],
                dominant_tone=NarrativeTone.DRAMATIC,
            )

        original = chapter.content

        # Analyze current issues
        issues_before = []
        issues_before.extend(self.check_tone_consistency(chapter, style_profile).issues)
        issues_before.extend(self.check_pacing_consistency(chapter, style_profile).issues)
        issues_before.extend(self.check_dialogue_ratio_consistency(chapter, style_profile).issues)

        # Polish for consistency
        revised = await self.polish_for_consistency(chapter, style_profile)

        # Create a temporary chapter with revised content for analysis
        temp_chapter = Chapter(
            id=chapter.id,
            number=chapter.number,
            title=chapter.title,
            content=revised,
            word_count=len(revised),
            status=chapter.status,
        )

        # Check remaining issues
        issues_after = []
        issues_after.extend(self.check_tone_consistency(temp_chapter, style_profile).issues)
        issues_after.extend(self.check_pacing_consistency(temp_chapter, style_profile).issues)
        issues_after.extend(self.check_dialogue_ratio_consistency(temp_chapter, style_profile).issues)

        return StyleConsistencyRevision(
            original_content=original,
            revised_content=revised,
            changes_made=["Applied style consistency polishing"],
            issues_fixed=[i for i in issues_before if i not in issues_after],
            issues_remaining=issues_after,
        )

    def export_draft(
        self,
        content: str,
        style_profile: Optional[StyleProfile] = None,
        template_name: Optional[str] = None,
    ) -> StyleConsistencyDraft:
        """Export content as a style consistency draft.

        Args:
            content: Draft content
            style_profile: Style profile applied
            template_name: Template used if any

        Returns:
            StyleConsistencyDraft
        """
        if style_profile is None:
            style_profile = self._style_profile or StyleProfile(
                tones=[NarrativeTone.DRAMATIC],
                dominant_tone=NarrativeTone.DRAMATIC,
            )

        applied = [template_name] if template_name else []

        return StyleConsistencyDraft(
            content=content,
            target_profile=style_profile,
            applied_templates=applied,
            consistency_score=0.85,  # Estimated
            notes="",
        )
