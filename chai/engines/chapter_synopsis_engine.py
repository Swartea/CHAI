"""Chapter synopsis engine for detailed chapter planning and plot point arrangement."""

from datetime import datetime
from typing import Optional
import uuid

from chai.models.chapter_synopsis import (
    SynopsisPlotPoint,
    SynopsisPlotPointType,
    SynopsisPlotPointStatus,
    PlotPointImportance,
    ChapterSynopsis,
    ChapterSynopsisSection,
    PlotPointArrangement,
    ChapterSynopsisAnalysis,
)
from chai.models.story_outline import StoryOutline, ChapterOutline, TensionLevel
from chai.models.main_story_structure import MainStoryStructure, StoryBeat
from chai.models.character_growth_arc import CharacterGrowthArcSystem
from chai.services import AIService


# Standard chapter structure template
CHAPTER_STRUCTURE_TEMPLATE = {
    "opening": {
        "name": "开场",
        "purpose": "建立场景，吸引读者",
        "typical_length": "10-15%",
    },
    "development": {
        "name": "发展",
        "purpose": "推进情节，展现人物",
        "typical_length": "40-50%",
    },
    "climax": {
        "name": "高潮",
        "purpose": "冲突爆发，情感冲击",
        "typical_length": "20-25%",
    },
    "resolution": {
        "name": "收尾",
        "purpose": "问题解决，情感余韵",
        "typical_length": "15-20%",
    },
}

# Plot point distribution guidelines
PLOT_POINT_DISTRIBUTION = {
    "turning_point": {"min_per_story": 3, "ideal_positions": [0.15, 0.5, 0.85]},
    "climax": {"min_per_story": 1, "ideal_position": 0.9},
    "key_event": {"min_per_chapter": 1, "max_per_chapter": 3},
    "complication": {"min_per_act": 2},
    "revelation": {"min_per_story": 5},
}


class ChapterSynopsisEngine:
    """Engine for generating detailed chapter synopses and arranging plot points."""

    def __init__(self, ai_service: AIService):
        """Initialize chapter synopsis engine with AI service."""
        self.ai_service = ai_service

    async def generate_synopsis(
        self,
        chapter_number: int,
        genre: str,
        theme: str,
        story_outline: Optional[StoryOutline] = None,
        main_structure: Optional[MainStoryStructure] = None,
        plot_points: Optional[list[SynopsisPlotPoint]] = None,
        characters: Optional[list[dict]] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
    ) -> ChapterSynopsis:
        """Generate a detailed chapter synopsis.

        Args:
            chapter_number: Chapter number
            genre: Novel genre
            theme: Central theme
            story_outline: Optional story outline for context
            main_structure: Optional main story structure for beat context
            plot_points: Optional existing plot points for this chapter
            characters: Optional character details
            growth_arcs: Optional character growth arc system

        Returns:
            ChapterSynopsis object
        """
        synopsis_id = f"synopsis_{uuid.uuid4().hex[:8]}"

        # Get AI-assisted synopsis data
        ai_synopsis_data = await self._generate_synopsis_with_ai(
            chapter_number=chapter_number,
            genre=genre,
            theme=theme,
            story_outline=story_outline,
            main_structure=main_structure,
            characters=characters or [],
        )

        # Build sections
        sections = self._build_sections(
            synopsis_id=synopsis_id,
            ai_data=ai_synopsis_data,
            chapter_number=chapter_number,
        )

        # Get plot point IDs for this chapter
        point_ids = [
            p.id for p in (plot_points or [])
            if p.chapter == chapter_number
        ]

        synopsis = ChapterSynopsis(
            id=synopsis_id,
            chapter_number=chapter_number,
            title=ai_synopsis_data.get("title", f"第{chapter_number}章"),
            summary=ai_synopsis_data.get("summary", ""),
            sections=sections,
            detailed_synopsis=ai_synopsis_data.get("detailed_synopsis", ""),
            plot_point_ids=point_ids,
            pov_character=ai_synopsis_data.get("pov_character"),
            characters_present=ai_synopsis_data.get("characters_present", []),
            new_characters=ai_synopsis_data.get("new_characters", []),
            primary_location=ai_synopsis_data.get("primary_location", ""),
            time_setting=ai_synopsis_data.get("time_setting", ""),
            plot_threads_advanced=ai_synopsis_data.get("plot_threads_advanced", []),
            character_development=ai_synopsis_data.get("character_development", []),
            foreshadowing_planted=ai_synopsis_data.get("foreshadowing_planted", []),
            foreshadowing_payoffs=ai_synopsis_data.get("foreshadowing_payoffs", []),
            themes_explored=ai_synopsis_data.get("themes_explored", []),
            chapter_emotional_arc=ai_synopsis_data.get("emotional_arc", ""),
            pacing_notes=ai_synopsis_data.get("pacing_notes", ""),
            status=SynopsisPlotPointStatus.COMPLETE,
        )

        return synopsis

    async def _generate_synopsis_with_ai(
        self,
        chapter_number: int,
        genre: str,
        theme: str,
        story_outline: Optional[StoryOutline],
        main_structure: Optional[MainStoryStructure],
        characters: list[dict],
    ) -> dict:
        """Generate synopsis data using AI."""
        # Get context from story outline
        chapter_info = ""
        if story_outline and chapter_number <= len(story_outline.chapters):
            ch = story_outline.chapters[chapter_number - 1]
            chapter_info = f"章节概要：{ch.summary}\n"

        # Get beat context from main structure
        beat_info = ""
        if main_structure:
            beats_in_chapter = [
                b for b in main_structure.beats
                if b.start_chapter <= chapter_number <= b.end_chapter
            ]
            if beats_in_chapter:
                beat_info = "本章相关情节点：\n" + "\n".join(
                    f"- {b.name}: {b.purpose}" for b in beats_in_chapter
                )

        char_names = [c.get("name", f"角色{i}") for i, c in enumerate(characters[:5])]

        prompt = f"""为{genre}类型小说的第{chapter_number}章生成详细章节概要。

主题：{theme}
主要角色：{', '.join(char_names)}

{chapter_info}
{beat_info}

请以JSON格式生成章节概要：
{{
  "title": "章节标题",
  "summary": "章节一句话总结（20字以内）",
  "detailed_synopsis": "详细章节概要（300-500字），包括起承转合",
  "pov_character": "POV视角角色名",
  "characters_present": ["本章出场角色列表"],
  "new_characters": ["本章新出场角色列表（首次出现）"],
  "primary_location": "主要场景地点",
  "time_setting": "时间设定（如：第一天早晨）",
  "plot_threads_advanced": ["本章推进的线索ID列表"],
  "character_development": ["本章角色成长时刻描述"],
  "foreshadowing_planted": ["本章埋下的伏笔ID列表"],
  "foreshadowing_payoffs": ["本章回收的伏笔ID列表"],
  "themes_explored": ["本章探索的主题"],
  "emotional_arc": "本章情感弧线描述（如：希望→绝望→决心）",
  "pacing_notes": "节奏提示（如：前期缓慢铺垫，后期急促紧张）",
  "sections": {{
    "opening": "开场部分概要",
    "development": "发展部分概要",
    "climax": "高潮部分概要",
    "resolution": "收尾部分概要"
  }}
}}"""
        result = await self.ai_service.generate(prompt)
        return self.ai_service._parse_json(result)

    def _build_sections(
        self,
        synopsis_id: str,
        ai_data: dict,
        chapter_number: int,
    ) -> list[ChapterSynopsisSection]:
        """Build chapter sections from AI data."""
        sections = []
        section_templates = ["opening", "development", "climax", "resolution"]
        ai_sections = ai_data.get("sections", {})

        for i, section_key in enumerate(section_templates):
            section_text = ai_sections.get(section_key, f"第{section_key}部分的概要")
            sections.append(ChapterSynopsisSection(
                id=f"{synopsis_id}_sec_{i + 1}",
                name=CHAPTER_STRUCTURE_TEMPLATE[section_key]["name"],
                order=i + 1,
                synopsis_text=section_text,
                key_events=self._extract_key_events(section_text),
                mood="",
                tension_level=self._infer_tension_level(section_key, chapter_number),
            ))

        return sections

    def _extract_key_events(self, text: str) -> list[str]:
        """Extract key events from synopsis text."""
        # Simple extraction - in real use would be more sophisticated
        events = []
        sentences = text.split("。")
        for s in sentences[:3]:
            s = s.strip()
            if len(s) > 5:
                events.append(s)
        return events

    def _infer_tension_level(self, section_key: str, chapter_number: int) -> str:
        """Infer tension level from section type."""
        tension_map = {
            "opening": "low",
            "development": "moderate",
            "climax": "high",
            "resolution": "moderate",
        }
        return tension_map.get(section_key, "moderate")

    async def generate_all_synopses(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        story_outline: Optional[StoryOutline] = None,
        main_structure: Optional[MainStoryStructure] = None,
        plot_points: Optional[list[SynopsisPlotPoint]] = None,
        characters: Optional[list[dict]] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
    ) -> list[ChapterSynopsis]:
        """Generate synopses for all chapters.

        Args:
            genre: Novel genre
            theme: Central theme
            target_chapters: Target number of chapters
            story_outline: Optional story outline
            main_structure: Optional main story structure
            plot_points: Optional plot points
            characters: Optional character details
            growth_arcs: Optional character growth arcs

        Returns:
            List of ChapterSynopsis objects
        """
        synopses = []

        for ch_num in range(1, target_chapters + 1):
            synopsis = await self.generate_synopsis(
                chapter_number=ch_num,
                genre=genre,
                theme=theme,
                story_outline=story_outline,
                main_structure=main_structure,
                plot_points=plot_points,
                characters=characters,
                growth_arcs=growth_arcs,
            )
            synopses.append(synopsis)

        return synopses

    async def arrange_plot_points(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        story_outline: Optional[StoryOutline] = None,
        main_structure: Optional[MainStoryStructure] = None,
        characters: Optional[list[dict]] = None,
    ) -> PlotPointArrangement:
        """Arrange plot points across chapters.

        Args:
            genre: Novel genre
            theme: Central theme
            target_chapters: Target number of chapters
            story_outline: Optional story outline for context
            main_structure: Optional main story structure
            characters: Optional character details

        Returns:
            PlotPointArrangement object
        """
        arrangement_id = f"arrangement_{uuid.uuid4().hex[:8]}"

        # Generate plot points with AI
        ai_points_data = await self._generate_plot_points_with_ai(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            story_outline=story_outline,
            main_structure=main_structure,
            characters=characters or [],
        )

        # Create plot points from AI data
        plot_points = self._create_plot_points(
            arrangement_id=arrangement_id,
            ai_data=ai_points_data,
            target_chapters=target_chapters,
            story_outline=story_outline,
            main_structure=main_structure,
        )

        # Build chapter to points mapping
        chapter_to_points = {}
        for point in plot_points:
            ch_key = f"chapter_{point.chapter}"
            if ch_key not in chapter_to_points:
                chapter_to_points[ch_key] = []
            chapter_to_points[ch_key].append(point.id)

        # Build thread to points mapping
        thread_to_points = {}
        for point in plot_points:
            for thread_id in point.plot_thread_ids:
                if thread_id not in thread_to_points:
                    thread_to_points[thread_id] = []
                thread_to_points[thread_id].append(point.id)

        arrangement = PlotPointArrangement(
            id=arrangement_id,
            story_arc_id=main_structure.id if main_structure else None,
            plot_points=plot_points,
            chapter_to_points=chapter_to_points,
            thread_to_points=thread_to_points,
            total_chapters=target_chapters,
            plot_points_per_chapter_avg=len(plot_points) / target_chapters,
            turning_point_coverage=self._calculate_turning_point_coverage(plot_points, target_chapters),
            subplot_balance=self._calculate_subplot_balance(plot_points, thread_to_points),
        )

        return arrangement

    async def _generate_plot_points_with_ai(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        story_outline: Optional[StoryOutline],
        main_structure: Optional[MainStoryStructure],
        characters: list[dict],
    ) -> dict:
        """Generate plot points using AI."""
        # Get structure context
        structure_context = ""
        if main_structure:
            structure_context = f"结构类型：{main_structure.structure_type.value}\n"
            structure_context += "情节点：\n"
            for beat in main_structure.beats[:10]:
                structure_context += f"- {beat.name}（第{beat.start_chapter}-{beat.end_chapter}章）\n"

        char_names = [c.get("name", f"角色{i}") for i, c in enumerate(characters[:5])]

        prompt = f"""为{genre}类型小说设计详细的情节点安排。

主题：{theme}
目标章节数：{target_chapters}
主要角色：{', '.join(char_names)}

{structure_context}

请以JSON格式生成情节点安排：
{{
  "plot_points": [
    {{
      "name": "情节点名称",
      "type": "turning_point/key_event/climax/complication/revelation/decision_point等",
      "chapter": 章节号,
      "scene_hint": "场景提示（如scene_2）",
      "description": "情节点详细描述",
      "significance": "重要性说明",
      "importance": "essential/important/notable/minor",
      "character_ids": ["涉及的的角色ID列表"],
      "plot_thread_ids": ["推进的线索ID列表"],
      "emotional_impact": "情感冲击描述",
      "tension_level": "low/moderate/high/climax",
      "consequences": ["直接后果列表"],
      "setups": ["铺垫的内容列表"]
    }}
  ],
  "turning_points": [
    {{"chapter": 章节号, "name": "转折点名称", "description": "描述"}}
  ],
  "major_revelations": [
    {{"chapter": 章节号, "description": "揭示内容"}}
  ]
}}"""
        result = await self.ai_service.generate(prompt)
        return self.ai_service._parse_json(result)

    def _create_plot_points(
        self,
        arrangement_id: str,
        ai_data: dict,
        target_chapters: int,
        story_outline: Optional[StoryOutline],
        main_structure: Optional[MainStoryStructure],
    ) -> list[SynopsisPlotPoint]:
        """Create plot points from AI data."""
        plot_points = []
        point_id_counter = 0

        # Map story beats to plot point types
        beat_type_map = {
            "inciting_incident": SynopsisPlotPointType.INCITING_INCIDENT,
            "midpoint": SynopsisPlotPointType.TURNING_POINT,
            "crisis": SynopsisPlotPointType.CRISIS,
            "climax": SynopsisPlotPointType.CLIMAX,
            "complication": SynopsisPlotPointType.COMPLICATION,
        }

        for point_data in ai_data.get("plot_points", []):
            chapter = point_data.get("chapter", 1)

            # Link to story beat if available
            story_beat_id = None
            if main_structure:
                matching_beats = [
                    b for b in main_structure.beats
                    if b.start_chapter <= chapter <= b.end_chapter
                ]
                if matching_beats:
                    story_beat_id = matching_beats[0].id

            point = SynopsisPlotPoint(
                id=f"pp_{arrangement_id}_{point_id_counter}",
                name=point_data.get("name", f"情节点{point_id_counter + 1}"),
                plot_point_type=SynopsisPlotPointType(point_data.get("type", "key_event")),
                description=point_data.get("description", ""),
                significance=point_data.get("significance", ""),
                chapter=chapter,
                scene_hint=point_data.get("scene_hint"),
                importance=PlotPointImportance(
                    point_data.get("importance", "important")
                ),
                status=SynopsisPlotPointStatus.PLANNED,
                story_beat_id=story_beat_id,
                act_number=self._infer_act(chapter, target_chapters),
                character_ids=point_data.get("character_ids", []),
                protagonist_involved=True,  # Simplified
                plot_thread_ids=point_data.get("plot_thread_ids", []),
                main_conflict_advancement=point_data.get("type") in [
                    "turning_point", "climax", "key_event"
                ],
                emotional_impact=point_data.get("emotional_impact", ""),
                tension_level=point_data.get("tension_level", "moderate"),
                consequences=point_data.get("consequences", []),
                setups=point_data.get("setups", []),
            )
            plot_points.append(point)
            point_id_counter += 1

        # Add essential turning points if missing
        turning_points = [p for p in plot_points if p.importance == PlotPointImportance.ESSENTIAL]
        if len(turning_points) < 3:
            essential_positions = [0.15, 0.5, 0.85]
            for i, pos in enumerate(essential_positions):
                ch = max(1, min(target_chapters, int(target_chapters * pos)))
                if not any(p.chapter == ch and p.importance == PlotPointImportance.ESSENTIAL for p in plot_points):
                    plot_points.append(SynopsisPlotPoint(
                        id=f"pp_{arrangement_id}_{point_id_counter}",
                        name=f"关键转折点{i + 1}",
                        plot_point_type=SynopsisPlotPointType.TURNING_POINT,
                        description=f"第{ch}章的关键转折",
                        significance="故事的重要转折点",
                        chapter=ch,
                        importance=PlotPointImportance.ESSENTIAL,
                        status=SynopsisPlotPointStatus.PENDING,
                        tension_level="high",
                    ))
                    point_id_counter += 1

        return plot_points

    def _infer_act(self, chapter: int, target_chapters: int) -> int:
        """Infer act number from chapter."""
        act_size = target_chapters // 3
        if act_size == 0:
            act_size = 8
        return min(3, (chapter - 1) // act_size + 1)

    def _calculate_turning_point_coverage(
        self,
        plot_points: list[SynopsisPlotPoint],
        target_chapters: int,
    ) -> float:
        """Calculate coverage of major turning points."""
        essential_points = [
            p for p in plot_points
            if p.importance == PlotPointImportance.ESSENTIAL
        ]

        if len(essential_points) >= 3:
            # Check if they're well distributed
            chapters = sorted([p.chapter for p in essential_points])
            if len(chapters) >= 3:
                third = target_chapters * 0.15
                mid = target_chapters * 0.5
                late = target_chapters * 0.85
                has_early = any(abs(c - third) < 3 for c in chapters)
                has_mid = any(abs(c - mid) < 3 for c in chapters)
                has_late = any(abs(c - late) < 3 for c in chapters)
                if has_early and has_mid and has_late:
                    return 1.0
        return len(essential_points) / 3.0

    def _calculate_subplot_balance(
        self,
        plot_points: list[SynopsisPlotPoint],
        thread_to_points: dict[str, list[str]],
    ) -> float:
        """Calculate balance of subplot advancement."""
        if not thread_to_points:
            return 1.0

        counts = [len(points) for points in thread_to_points.values()]
        if not counts:
            return 1.0

        avg = sum(counts) / len(counts)
        if avg == 0:
            return 1.0

        variance = sum((c - avg) ** 2 for c in counts) / len(counts)
        # Normalize: 0 variance = 1.0, high variance = lower
        return max(0.0, 1.0 - (variance / (avg ** 2 + 1)))

    def link_to_story_beats(
        self,
        arrangement: PlotPointArrangement,
        main_structure: MainStoryStructure,
    ) -> PlotPointArrangement:
        """Link plot points to story beats from main structure.

        Args:
            arrangement: Plot point arrangement
            main_structure: Main story structure to link to

        Returns:
            Updated arrangement with linked plot points
        """
        for point in arrangement.plot_points:
            # Find matching beat
            matching_beats = [
                b for b in main_structure.beats
                if b.start_chapter <= point.chapter <= b.end_chapter
            ]

            if matching_beats:
                beat = matching_beats[0]
                point.story_beat_id = beat.id
                point.act_number = beat.act_number

                # Update tension if needed
                if beat.tension_level:
                    point.tension_level = beat.tension_level

        return arrangement

    async def analyze_synopsis(
        self,
        synopses: list[ChapterSynopsis],
        arrangement: Optional[PlotPointArrangement] = None,
        story_outline: Optional[StoryOutline] = None,
    ) -> ChapterSynopsisAnalysis:
        """Analyze chapter synopsis quality.

        Args:
            synopses: List of chapter synopses
            arrangement: Optional plot point arrangement
            story_outline: Optional story outline

        Returns:
            ChapterSynopsisAnalysis object
        """
        analysis = ChapterSynopsisAnalysis(synopsis_id="synopsis_analysis")

        if not synopses:
            return analysis

        # Chapter coverage
        analysis.chapter_coverage = len(synopses) / 24.0  # Assuming 24 target

        # Plot point coverage
        if arrangement:
            chapters_with_points = len(arrangement.chapter_to_points)
            analysis.plot_point_coverage = chapters_with_points / arrangement.total_chapters

        # Pacing analysis
        analysis.pacing_score = self._analyze_pacing(synopses)

        # Tension distribution
        analysis.tension_distribution = self._analyze_tension_distribution(synopses)

        # Thread coverage
        if arrangement:
            analysis.thread_coverage = {
                thread_id: len(points)
                for thread_id, points in arrangement.thread_to_points.items()
            }

        # Character screen time
        analysis.character_screen_time = self._analyze_character_screen_time(synopses)

        # Protagonist focus
        protagonist_chapters = sum(
            1 for s in synopses
            if s.pov_character and "主角" in s.pov_character
        )
        analysis.protagonist_focus_ratio = protagonist_chapters / max(len(synopses), 1)

        # Foreshadowing balance
        analysis.foreshadowing_balance = self._analyze_foreshadowing(synopses)

        # Calculate quality scores
        analysis.coherence_score = self._calculate_coherence(synopses, arrangement)
        analysis.completeness_score = self._calculate_completeness(synopses, arrangement)

        # Identify issues
        analysis.identified_issues = self._identify_issues(synopses, arrangement)

        # Recommendations
        analysis.recommendations = self._generate_recommendations(
            synopses, arrangement, analysis
        )

        return analysis

    def _analyze_pacing(self, synopses: list[ChapterSynopsis]) -> float:
        """Analyze pacing quality."""
        if not synopses:
            return 0.0

        score = 1.0

        # Check for climax chapters
        climax_chapters = [s for s in synopses if s.is_climax_chapter]
        if len(climax_chapters) < 1:
            score -= 0.2

        # Check for prologue/epilogue
        has_prologue = any(s.is_prologue for s in synopses)
        has_epilogue = any(s.is_epilogue for s in synopses)
        if not (has_prologue and has_epilogue):
            score -= 0.1

        # Check synopsis length variation
        lengths = [len(s.detailed_synopsis) for s in synopses]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            variation = sum(abs(l - avg_len) for l in lengths) / len(lengths)
            if variation > avg_len * 0.5:
                score -= 0.2

        return max(0.0, min(1.0, score))

    def _analyze_tension_distribution(
        self,
        synopses: list[ChapterSynopsis],
    ) -> dict:
        """Analyze tension distribution."""
        tension_counts = {"low": 0, "moderate": 0, "high": 0, "climax": 0}

        for synopsis in synopses:
            for section in synopsis.sections:
                level = section.tension_level
                if level in tension_counts:
                    tension_counts[level] += 1

        return tension_counts

    def _analyze_character_screen_time(
        self,
        synopses: list[ChapterSynopsis],
    ) -> dict:
        """Analyze character screen time distribution."""
        char_counts = {}

        for synopsis in synopses:
            for char in synopsis.characters_present:
                char_counts[char] = char_counts.get(char, 0) + 1

        return char_counts

    def _analyze_foreshadowing(
        self,
        synopses: list[ChapterSynopsis],
    ) -> dict:
        """Analyze foreshadowing balance."""
        total_planted = sum(
            len(s.foreshadowing_planted) for s in synopses
        )
        total_payoffs = sum(
            len(s.foreshadowing_payoffs) for s in synopses
        )

        return {
            "planted": total_planted,
            "paid_off": total_payoffs,
            "ratio": total_payoffs / total_planted if total_planted > 0 else 0,
        }

    def _calculate_coherence(
        self,
        synopses: list[ChapterSynopsis],
        arrangement: Optional[PlotPointArrangement],
    ) -> float:
        """Calculate coherence score."""
        score = 1.0

        # Penalize for missing chapters
        expected = 24
        if len(synopses) < expected:
            score -= 0.1 * (expected - len(synopses)) / expected

        # Penalize for unresolved threads
        if arrangement:
            # Check if all plot points are linked
            unlinked = [
                p for p in arrangement.plot_points
                if not p.plot_thread_ids
            ]
            if unlinked:
                score -= 0.1 * len(unlinked) / len(arrangement.plot_points)

        return max(0.0, min(1.0, score))

    def _calculate_completeness(
        self,
        synopses: list[ChapterSynopsis],
        arrangement: Optional[PlotPointArrangement],
    ) -> float:
        """Calculate completeness score."""
        score = 0.0
        max_score = 5.0

        # Has synopses for most chapters
        if len(synopses) >= 20:
            score += 1.5
        elif len(synopses) >= 12:
            score += 1.0
        elif len(synopses) >= 6:
            score += 0.5

        # Has detailed synopsis text
        with_details = sum(1 for s in synopses if s.detailed_synopsis)
        if with_details >= len(synopses) * 0.8:
            score += 1.5

        # Has plot point arrangement
        if arrangement and len(arrangement.plot_points) >= 10:
            score += 1.0

        # Has character development notes
        with_dev = sum(1 for s in synopses if s.character_development)
        if with_dev >= len(synopses) * 0.5:
            score += 0.5

        # Has foreshadowing
        has_fore = sum(1 for s in synopses if s.foreshadowing_planted)
        if has_fore >= len(synopses) * 0.3:
            score += 0.5

        return score / max_score

    def _identify_issues(
        self,
        synopses: list[ChapterSynopsis],
        arrangement: Optional[PlotPointArrangement],
    ) -> list[str]:
        """Identify issues in synopses."""
        issues = []

        # Check for climax placement
        if arrangement:
            climax_points = [
                p for p in arrangement.plot_points
                if p.plot_point_type == SynopsisPlotPointType.CLIMAX
            ]
            if climax_points:
                last_chapter = max(p.chapter for p in arrangement.plot_points)
                for cp in climax_points:
                    if cp.chapter < last_chapter * 0.7:
                        issues.append("高潮可能过早出现")
                        break

        # Check for protagonist presence
        protagonist_chapters = [
            s for s in synopses
            if s.pov_character and "主角" in s.pov_character
        ]
        if len(protagonist_chapters) < len(synopses) * 0.3:
            issues.append("主角POV章节偏少，可能影响读者代入感")

        # Check for tension variation
        tension_variation = set()
        for s in synopses:
            for section in s.sections:
                tension_variation.add(section.tension_level)
        if len(tension_variation) < 3:
            issues.append("章节张力变化不足，节奏可能单调")

        return issues

    def _generate_recommendations(
        self,
        synopses: list[ChapterSynopsis],
        arrangement: Optional[PlotPointArrangement],
        analysis: ChapterSynopsisAnalysis,
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if analysis.completeness_score < 0.7:
            recommendations.append("建议为更多章节生成详细概要")

        if analysis.pacing_score < 0.8:
            recommendations.append("建议优化章节节奏，确保高潮部分有足够篇幅")

        if arrangement:
            # Check for subplot balance
            if analysis.thread_coverage:
                max_thread = max(analysis.thread_coverage.values())
                min_thread = min(analysis.thread_coverage.values())
                if max_thread > min_thread * 3:
                    recommendations.append("建议平衡各条线索的戏份，避免某条线索过重或过轻")

        if analysis.identified_issues:
            recommendations.append("建议检查并修正已发现的问题")

        return recommendations

    def get_synopsis_summary(self, synopses: list[ChapterSynopsis]) -> str:
        """Get a human-readable summary of chapter synopses.

        Args:
            synopses: List of chapter synopses

        Returns:
            Summary string
        """
        if not synopses:
            return "暂无章节概要"

        lines = [
            f"=== 章节概要概览 ===",
            f"总章节数：{len(synopses)}",
            f"",
        ]

        # Group by type
        prologues = [s for s in synopses if s.is_prologue]
        epilogues = [s for s in synopses if s.is_epilogue]
        climaxes = [s for s in synopses if s.is_climax_chapter]

        if prologues:
            lines.append(f"序章：第{prologues[0].chapter_number}章")
        if climaxes:
            lines.append(f"高潮章节：{', '.join(str(c.chapter_number) for c in climaxes)}")
        if epilogues:
            lines.append(f"尾声：第{epilogues[0].chapter_number}章")

        lines.extend(["", "=== 章节摘要 ==="])

        for synopsis in synopses[:6]:
            lines.append(
                f"第{synopsis.chapter_number}章 {synopsis.title}："
                f"{synopsis.summary[:40]}..."
            )

        if len(synopses) > 6:
            lines.append(f"... 共{len(synopses)}章")

        return "\n".join(lines)

    def export_synopsis(
        self,
        synopsis: ChapterSynopsis,
    ) -> dict:
        """Export chapter synopsis as a dictionary.

        Args:
            synopsis: ChapterSynopsis to export

        Returns:
            Dictionary representation
        """
        return {
            "id": synopsis.id,
            "chapter_number": synopsis.chapter_number,
            "title": synopsis.title,
            "summary": synopsis.summary,
            "detailed_synopsis": synopsis.detailed_synopsis,
            "pov_character": synopsis.pov_character,
            "characters_present": synopsis.characters_present,
            "new_characters": synopsis.new_characters,
            "primary_location": synopsis.primary_location,
            "time_setting": synopsis.time_setting,
            "plot_point_ids": synopsis.plot_point_ids,
            "plot_threads_advanced": synopsis.plot_threads_advanced,
            "character_development": synopsis.character_development,
            "foreshadowing_planted": synopsis.foreshadowing_planted,
            "foreshadowing_payoffs": synopsis.foreshadowing_payoffs,
            "themes_explored": synopsis.themes_explored,
            "emotional_arc": synopsis.chapter_emotional_arc,
            "pacing_notes": synopsis.pacing_notes,
            "word_count_target": synopsis.word_count_target,
            "status": synopsis.status.value,
            "is_prologue": synopsis.is_prologue,
            "is_epilogue": synopsis.is_epilogue,
            "is_climax_chapter": synopsis.is_climax_chapter,
        }

    def export_arrangement(
        self,
        arrangement: PlotPointArrangement,
    ) -> dict:
        """Export plot point arrangement as a dictionary.

        Args:
            arrangement: PlotPointArrangement to export

        Returns:
            Dictionary representation
        """
        return {
            "id": arrangement.id,
            "story_arc_id": arrangement.story_arc_id,
            "total_chapters": arrangement.total_chapters,
            "plot_points_per_chapter_avg": arrangement.plot_points_per_chapter_avg,
            "turning_point_coverage": arrangement.turning_point_coverage,
            "subplot_balance": arrangement.subplot_balance,
            "plot_points": [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": p.plot_point_type.value,
                    "chapter": p.chapter,
                    "description": p.description,
                    "importance": p.importance.value,
                    "tension_level": p.tension_level,
                }
                for p in arrangement.plot_points
            ],
            "chapter_to_points": arrangement.chapter_to_points,
        }